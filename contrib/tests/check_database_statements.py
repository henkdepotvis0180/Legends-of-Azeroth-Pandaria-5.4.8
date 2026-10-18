#!/usr/bin/env python3
"""PREPARE (never execute) the core's literal SQL statements against test schemas.

Checks tables, columns and SQL syntax. This is a source-level check of literal
PrepareStatement calls, not a replacement for compiled startup: C++ conditional
branches are not evaluated and dynamic bot queries are outside its coverage.
"""

import argparse
import ast
import json
from pathlib import Path
import re
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mysql", default="mysql")
    parser.add_argument("--port", type=int, default=3306)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--user", default="root")
    parser.add_argument("--defaults-extra-file", type=Path)
    parser.add_argument("--prefix", default="mop")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,39}", args.prefix):
        parser.error("Invalid database prefix")
    root = Path(__file__).resolve().parents[2]
    command = [args.mysql, f"--defaults-extra-file={args.defaults_extra_file.resolve()}"
               if args.defaults_extra_file else "--no-defaults",
               "--protocol=TCP", f"--host={args.host}", f"--port={args.port}",
               f"--user={args.user}", "--batch", "--skip-column-names", "--force"]
    report = {"status": "passed", "checks": []}
    # Preserve string literals while stripping both C++ comment forms.
    comments = re.compile(r'("(?:\\.|[^"\\])*")|(/\*.*?\*/|//[^\n]*)', re.S)
    calls = re.compile(r'PrepareStatement\(\s*(\w+)\s*,\s*((?:"(?:\\.|[^"\\])*"\s*)+),')
    for name, kind in (("Login", "auth"), ("Character", "characters"),
                       ("World", "world"), ("Playerbots", "playerbots")):
        path = root / f"src/server/database/Database/Implementation/{name}Database.cpp"
        content = comments.sub(lambda match: match[1] or "", path.read_text())
        statements = []
        labels = {}
        for index, match in enumerate(calls.finditer(content)):
            sql = "".join(ast.literal_eval(token) for token in re.findall(r'"(?:\\.|[^"\\])*"', match[2]))
            quoted = sql.replace("\\", "\\\\").replace("'", "''")
            # A distinct name prevents a failed PREPARE from reusing an old one.
            labels[len(statements) + 1] = match[1]
            statements += [f"PREPARE probe_{index} FROM '{quoted}';",
                           f"DEALLOCATE PREPARE probe_{index};"]
        if not statements:
            report["checks"].append({"database": kind, "statements": 0,
                                      "note": "No uncommented literal PrepareStatement calls"})
            continue
        result = subprocess.run(command + [f"{args.prefix}_{kind}"],
                                input="\n".join(statements), text=True, capture_output=True)
        errors = result.stderr.strip()
        check = {"database": kind, "statements": len(statements) // 2,
                 "errors": errors, "returncode": result.returncode}
        if result.returncode or re.search(r"\bERROR\s+\d+", errors):
            report["status"] = "failed"
            check["statement_labels_by_line"] = labels
        report["checks"].append(check)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return report["status"] != "passed"


if __name__ == "__main__":
    raise SystemExit(main())
