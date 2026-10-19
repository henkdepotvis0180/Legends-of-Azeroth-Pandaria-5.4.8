#!/usr/bin/env bash
set -euo pipefail

if pgrep -x worldserver >/dev/null || pgrep -x authserver >/dev/null; then
    echo 'Stop eerst worldserver (server shutdown 0) en authserver (Ctrl+C).'
    exit 1
fi
source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$source_dir"
python3 contrib/tests/test_playerbot_action_trace.py
python3 contrib/tests/test_playerbot_diagnostics.py
python3 contrib/tests/test_playerbot_login_gate.py
python3 contrib/tests/test_playerbot_natural_progression.py
python3 contrib/tests/test_playerbot_class_spellbook.py
python3 contrib/tests/test_playerbot_heal_targets.py
python3 contrib/tests/test_playerbot_priest_defaults.py
python3 contrib/tests/test_playerbot_action_registry.py
mkdir -p "$HOME/mop"
MOP_BUILD_JOBS="${MOP_BUILD_JOBS:-6}" \
MOP_BUILD_DIR="${MOP_BUILD_DIR:-$HOME/mop/build}" \
MOP_INSTALL_DIR="${MOP_INSTALL_DIR:-$HOME/mop/server}" \
    bash contrib/build-linux-playerbots.sh -DSCRIPTS=ON 2>&1 | tee "$HOME/mop/bot-update10-build.log"
python3 contrib/configure-local-bot-population.py \
    --etc "${MOP_INSTALL_DIR:-$HOME/mop/server}/etc" --count 10 --natural-progression
echo 'Update 10 party-priestfix geïnstalleerd. Start via Start-MoP en log in om de bots te activeren.'
