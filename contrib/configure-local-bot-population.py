#!/usr/bin/env python3
"""Enable a small player-triggered bot population; preserve local config backups."""
import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import re
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--etc", type=Path, default=Path.home() / "mop/server/etc")
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--natural-progression", action="store_true",
                        help="Start alleen level-1 wereldbots op 4-10; behoud bestaande voortgang.")
    args = parser.parse_args()
    if not 1 <= args.count <= 250:
        parser.error("--count moet tussen 1 en 250 liggen; begin met 10.")
    path = args.etc / "playerbots.conf"
    text = path.read_text()
    settings = {
        "AiPlayerbot.Enabled": 1,
        "AiPlayerbot.RandomBotAutologin": 1,
        "AiPlayerbot.RandomBotLoginOnlyWithPlayers": 1,
        "AiPlayerbot.MinRandomBots": args.count,
        "AiPlayerbot.MaxRandomBots": args.count,
        "AiPlayerbot.RandomBotsPerInterval": 5,
    }
    if args.natural_progression:
        settings.update({
            "AiPlayerbot.RandomBotNaturalProgression": 1,
            "AiPlayerbot.RandomBotStartingMinLevel": 4,
            "AiPlayerbot.RandomBotStartingMaxLevel": 10,
        })
    for key, value in settings.items():
        pattern = rf"(?m)^[ \t]*{re.escape(key)}[ \t]*=.*$"
        line = f"{key} = {value}"
        if re.search(pattern, text):
            text = re.sub(pattern, lambda _: line, text)
        else:
            text += "\n" + line + "\n"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    backup = path.with_name(path.name + ".before-bot-update-" + stamp)
    shutil.copy2(path, backup)
    os.chmod(backup, 0o600)
    temporary = path.with_name(path.name + ".bot-update-" + stamp)
    try:
        with temporary.open("x") as handle:
            os.chmod(temporary, 0o600)
            handle.write(text)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"Back-up: {backup}")
    print(f"Doelpopulatie: {args.count} bots, inloggen na een echte speler in de wereld.")
    print("Start de opnieuw gebouwde server. Het bestaande accountaanbod bepaalt hoeveel bots beschikbaar zijn.")


if __name__ == "__main__":
    main()
