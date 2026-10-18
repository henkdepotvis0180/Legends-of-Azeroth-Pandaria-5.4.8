#!/usr/bin/env python3
"""Import fresh MoP databases; refuse to overwrite existing schemas.

Requires the MySQL CLI and the official world_548_20240722.sql dump.
Connection credentials belong in a private MySQL --defaults-extra-file, not Git.
This tool imports SQL only; it does not start MySQL or a game server.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--world-sql", type=Path, required=True)
    parser.add_argument("--prefix", default="mop")
    parser.add_argument("--mysql", default="mysql")
    parser.add_argument("--defaults-extra-file", type=Path)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3306)
    parser.add_argument("--user", default="root")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,39}", args.prefix):
        parser.error("Prefix must start with a letter and contain only letters, digits or underscores (max 40).")
    world = args.world_sql.resolve(strict=True)
    if world.name != "world_548_20240722.sql":
        parser.error("Expected the official world_548_20240722.sql dump.")
    root = Path(__file__).resolve().parents[1]
    command = [args.mysql]
    if args.defaults_extra_file:
        command.append(f"--defaults-extra-file={args.defaults_extra_file.resolve(strict=True)}")
    else:
        command.append("--no-defaults")
    command += ["--protocol=TCP", f"--host={args.host}", f"--port={args.port}",
                f"--user={args.user}", "--default-character-set=utf8mb4",
                "--max-allowed-packet=256M", "--batch", "--skip-column-names"]
    report = {"status": "in_progress", "imports": [], "skipped_updates": [], "databases": {},
              "world_sha256": sha256(world)}

    def save():
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    def query(sql, database=None):
        result = subprocess.run(command + ([database] if database else []) + ["-e", sql],
                                capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stderr[-3000:])
        return result.stdout.strip()

    def load(path, database, tracked=False):
        print(f"Import {database}: {path.name}", flush=True)
        with path.open("rb") as stream:
            result = subprocess.run(command + [database], stdin=stream,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode:
            raise RuntimeError(f"Import failed: {path.name}\n" + result.stderr.decode(errors="replace")[-3000:])
        if tracked:
            digest = hashlib.sha1(path.read_bytes()).hexdigest()
            query(f"REPLACE INTO updates (name,hash,state) VALUES ('{path.name}','{digest}','RELEASED')", database)
        report["imports"].append({"file": str(path.relative_to(root)) if path.is_relative_to(root) else path.name,
                                  "database": database, "sha256": sha256(path)})
        save()

    databases = {kind: f"{args.prefix}_{kind}" for kind in ("auth", "characters", "world", "playerbots")}
    try:
        report["mysql_version"] = query("SELECT VERSION()")
        existing = set(query("SHOW DATABASES").splitlines())
        collisions = existing.intersection(databases.values())
        if collisions:
            raise RuntimeError("Refusing to overwrite existing databases: " + ", ".join(sorted(collisions)))
        # All four names were checked before creating any schema. Never drop databases.
        for database in databases.values():
            query(f"CREATE DATABASE `{database}` CHARACTER SET utf8mb4")
        load(root / "sql/base/auth.sql", databases["auth"])
        # Fresh installs must not inherit the dump's pre-created administrator.
        query("DELETE FROM account_access; DELETE FROM realmcharacters; "
              "DELETE FROM account;", databases["auth"])
        # The upstream dump points realm 1 at its author's address.
        query("UPDATE realmlist SET address='127.0.0.1', localAddress='127.0.0.1', "
              "gamebuild=18414 WHERE id=1", databases["auth"])
        load(root / "sql/base/characters.sql", databases["characters"])
        # The upstream base contains example characters and their related data.
        # Only a new schema reaches this point; retain update/policy tables.
        keep = {"updates", "updates_include", "reserved_name", "warden_action"}
        runtime_tables = set(query("SHOW TABLES", databases["characters"]).splitlines()) - keep
        cleanup = "; ".join(f"TRUNCATE TABLE `{name.replace('`', '``')}`"
                            for name in sorted(runtime_tables))
        query("SET FOREIGN_KEY_CHECKS=0; " + cleanup + "; SET FOREIGN_KEY_CHECKS=1",
              databases["characters"])
        load(world, databases["world"])
        for folder, kind in (("sql/updates/master/auth", "auth"),
                             ("sql/updates/characters", "characters"),
                             ("sql/updates/world", "world")):
            applied = set(query("SELECT name FROM updates", databases[kind]).splitlines())
            for path in sorted((root / folder).glob("*.sql")):
                if path.name in applied:
                    report["skipped_updates"].append({"file": path.name, "reason": "already recorded in base dump"})
                    continue
                load(path, databases[kind], tracked=True)

        module = root / "modules/mod_playerbots/data/sql"
        base = module / "playerbots/base"
        full = base / "playerbots_database_full.sql"
        bots = databases["playerbots"]
        load(full, bots)
        tables = set(query("SHOW TABLES", bots).splitlines())
        # The combined dump has newer data for 13 tables but omits other caches.
        # Import per-table bases only when their tables are missing.
        for path in sorted(base.glob("*.sql")):
            if path == full:
                continue
            content = path.read_text(encoding="utf-8-sig", errors="replace")
            if re.search(r"^\s*(?:USE\s|CREATE\s+DATABASE\s|DROP\s+DATABASE\s)", content, re.M | re.I):
                raise RuntimeError(f"SQL changes the selected database: {path.name}")
            declared = set(re.findall(r"CREATE TABLE(?: IF NOT EXISTS)? `([^`]+)`", content))
            if declared and not declared.issubset(tables):
                if declared.intersection(tables):
                    raise RuntimeError(f"Mixed existing/missing tables in {path.name}")
                load(path, bots)
                tables.update(declared)
        for name in ("updates", "updates_include"):
            if name not in tables:
                query(f"CREATE TABLE `{bots}`.`{name}` LIKE `{databases['world']}`.`{name}`")
        applied = set(query("SELECT name FROM updates", bots).splitlines())
        for path in sorted((module / "playerbots/updates/db_playerbots").glob("*.sql")):
            if path.name not in applied:
                load(path, bots, tracked=True)
        # Normalize upstream's older module-relative update paths to this layout.
        query("DELETE FROM updates_include", bots)
        for path, state in (("updates", "RELEASED"), ("custom", "RELEASED"), ("archive", "ARCHIVED")):
            query("INSERT INTO updates_include (path,state) VALUES "
                  f"('$/modules/mod_playerbots/data/sql/playerbots/{path}','{state}')", bots)
        for kind in ("characters", "world"):
            for path in sorted((module / kind).glob("*.sql")):
                load(path, databases[kind])
        # Discard old scheduling events referencing the dump author's bots.
        query("TRUNCATE TABLE playerbots_random_bots", bots)
        for kind, database in databases.items():
            report["databases"][kind] = {"name": database, "tables": int(query(
                f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='{database}'"))}
        report["creature_templates"] = int(query("SELECT COUNT(*) FROM creature_template", databases["world"]))
        report["quests"] = int(query("SELECT COUNT(*) FROM quest_template", databases["world"]))
        report["bot_names"] = int(query("SELECT COUNT(*) FROM playerbots_names", databases["characters"]))
        report["accounts"] = int(query("SELECT COUNT(*) FROM account", databases["auth"]))
        report["characters"] = int(query("SELECT COUNT(*) FROM characters", databases["characters"]))
        report["inventory_rows"] = int(query("SELECT COUNT(*) FROM character_inventory", databases["characters"]))
        report["random_bot_events"] = int(query("SELECT COUNT(*) FROM playerbots_random_bots", bots))
        report["realm_address"] = query("SELECT address FROM realmlist WHERE id=1", databases["auth"])
        report["status"] = "passed"
        save()
        print("Database import and SQL validation passed. This is not an ingame test.")
    except Exception as error:
        report["status"] = "failed"
        report["error"] = str(error)
        save()
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
