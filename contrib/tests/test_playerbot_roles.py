#!/usr/bin/env python3
"""Compile and exercise the actual role classifier without server dependencies.

Extracts the complete GetPlayerRoles definition and production enums unchanged.
Only the Player interface is replaced. This checks classification, not integration,
combat strategies, a complete server build, or Monk combat support.
Run: python3 contrib/tests/test_playerbot_roles.py [--source-root PATH]
Requires a C++20 compiler (CXX, or c++).
"""

import argparse
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile


def definition(source, pattern):
    match = re.search(pattern, source)
    if not match:
        raise ValueError(f"Definition not found: {pattern}")
    start = source.index("{", match.start())
    depth = 1
    end = start + 1
    while depth:
        if source[end] == "{":
            depth += 1
        elif source[end] == "}":
            depth -= 1
        end += 1
    return source[match.start():end]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path,
                        default=Path(__file__).resolve().parents[2])
    root = parser.parse_args().source_root
    shared = (root / "src/server/game/Miscellaneous/SharedDefines.h").read_text()
    roles = (root / "modules/mod_playerbots/src/AI/PlayerbotAI.h").read_text()
    factory = (root / "modules/mod_playerbots/src/Factory/AiFactory.cpp").read_text()

    # Expected gameplay roles for every playable MoP specialization.
    cases = {
        "WARRIOR": {"ARMS": "DPS", "FURY": "DPS", "PROTECTION": "TANK"},
        "PALADIN": {"HOLY": "HEALER", "PROTECTION": "TANK", "RETRIBUTION": "DPS"},
        "HUNTER": {"BEAST_MASTERY": "DPS", "MARKSMANSHIP": "DPS", "SURVIVAL": "DPS"},
        "ROGUE": {"ASSASSINATION": "DPS", "COMBAT": "DPS", "SUBTLETY": "DPS"},
        "PRIEST": {"DISCIPLINE": "HEALER", "HOLY": "HEALER", "SHADOW": "DPS"},
        "DEATH_KNIGHT": {"BLOOD": "TANK", "FROST": "DPS", "UNHOLY": "DPS"},
        "SHAMAN": {"ELEMENTAL": "DPS", "ENHANCEMENT": "DPS", "RESTORATION": "HEALER"},
        "MAGE": {"ARCANE": "DPS", "FIRE": "DPS", "FROST": "DPS"},
        "WARLOCK": {"AFFLICTION": "DPS", "DEMONOLOGY": "DPS", "DESTRUCTION": "DPS"},
        "MONK": {"BREWMASTER": "TANK", "MISTWEAVER": "HEALER", "WINDWALKER": "DPS"},
        "DRUID": {"BALANCE": "DPS", "FERAL": "DPS", "GUARDIAN": "TANK", "RESTORATION": "HEALER"},
    }
    checks = []
    for cls, specs in cases.items():
        for spec, expected in specs.items():
            checks.append(
                f'check(CLASS_{cls}, SPEC_{cls}_{spec}, BOT_ROLE_{expected}, "{cls}/{spec}");')

    program = "\n".join([
        "#include <cstdint>\n#include <iostream>\nusing uint8 = std::uint8_t;",
        definition(shared, r"enum Classes\b") + ";",
        definition(shared, r"enum Specializations\b") + ";",
        definition(roles, r"enum BotRoles\b") + ";",
        "struct Player { Classes cls; Specializations spec; "
        "Classes GetClass() const { return cls; } "
        "Specializations GetSpecialization() const { return spec; } };",
        "struct AiFactory { static BotRoles GetPlayerRoles(Player* player); };",
        definition(factory, r"BotRoles AiFactory::GetPlayerRoles\(Player\* player\)"),
        "int main() { int failures = 0;",
        "auto check = [&](Classes cls, Specializations spec, BotRoles expected, const char* name) {"
        " Player player{cls, spec}; auto actual = AiFactory::GetPlayerRoles(&player);"
        ' if (actual != expected) { std::cerr << name << ": expected " << int(expected)'
        ' << ", got " << int(actual) << "\\n"; ++failures; } };',
        *checks,
        f'if (!failures) std::cout << "PASS: {len(checks)} specialization roles\\n";',
        "return failures ? 1 : 0; }",
    ])
    with tempfile.TemporaryDirectory(prefix="mop-role-test-") as tmp:
        source = Path(tmp) / "roles.cpp"
        executable = Path(tmp) / ("roles.exe" if os.name == "nt" else "roles")
        source.write_text(program)
        compiler = shlex.split(os.environ.get("CXX", "c++"))
        subprocess.run([*compiler, "-std=c++20", "-Wall", "-Wextra", "-Werror",
                        str(source), "-o", str(executable)], check=True)
        subprocess.run([str(executable)], check=True)


if __name__ == "__main__":
    main()
