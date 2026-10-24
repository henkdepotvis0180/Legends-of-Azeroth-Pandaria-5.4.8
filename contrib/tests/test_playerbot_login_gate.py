#!/usr/bin/env python3
"""Compile the actual login-gate methods against controlled session interfaces."""
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile


def definition(text, name):
    match = re.search(r"bool " + re.escape(name) + r"\(\) const\s*\{", text)
    if not match:
        raise RuntimeError(f"Missing production method {name}")
    end, depth = match.end(), 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[match.start():end]


def main():
    root = Path(__file__).resolve().parents[2]
    source = (root / "modules/mod_playerbots/src/Manager/RandomPlayerbotMgr.cpp").read_text()
    methods = "\n".join(definition(source, name) for name in [
        "RandomPlayerbotMgr::HasRealPlayerOnline", "RandomPlayerbotMgr::ShouldAutoLoginBots"])
    program = r'''
#include <cassert>
#include <iostream>
#include <unordered_map>
struct Player {
    bool inWorld = false;
    bool IsInWorld() const { return inWorld; }
};
struct WorldSession {
    bool bot = false, loggingOut = false;
    Player* player = nullptr;
    bool IsBot() { return bot; }
    bool isLogingOut() const { return loggingOut; }
    Player* GetPlayer() { return player; }
};
struct World {
    std::unordered_map<unsigned, WorldSession*> sessions;
    auto const& GetAllSessions() const { return sessions; }
} world;
auto* sWorld = &world;
struct Config {
    bool enabled = true, randomBotAutologin = true, randomBotLoginOnlyWithPlayers = true;
} config;
auto* sPlayerbotAIConfig = &config;
struct RandomPlayerbotMgr {
    bool HasRealPlayerOnline() const;
    bool ShouldAutoLoginBots() const;
};
'''
    cases = r'''
int main() {
    RandomPlayerbotMgr mgr;
    assert(!mgr.HasRealPlayerOnline() && !mgr.ShouldAutoLoginBots());
    world.sessions[0] = nullptr;
    assert(!mgr.ShouldAutoLoginBots());
    Player botPlayer{true}, humanPlayer{false};
    WorldSession bot{true, false, &botPlayer}, human;
    world.sessions[1] = &bot;
    assert(!mgr.HasRealPlayerOnline() && !mgr.ShouldAutoLoginBots());
    world.sessions[2] = &human;
    assert(!mgr.ShouldAutoLoginBots()); // Character selection.
    human.player = &humanPlayer;
    assert(!mgr.ShouldAutoLoginBots()); // Still entering world.
    humanPlayer.inWorld = true;
    assert(mgr.HasRealPlayerOnline() && mgr.ShouldAutoLoginBots());
    human.loggingOut = true;
    assert(!mgr.ShouldAutoLoginBots());
    human.loggingOut = false;
    config.enabled = false;
    assert(!mgr.ShouldAutoLoginBots());
    config.enabled = true; config.randomBotAutologin = false;
    assert(!mgr.ShouldAutoLoginBots());
    config.randomBotAutologin = true;
    assert(mgr.ShouldAutoLoginBots());
    humanPlayer.inWorld = false;
    assert(!mgr.ShouldAutoLoginBots()); // Last real player left; bots remain.
    config.randomBotLoginOnlyWithPlayers = false;
    assert(mgr.ShouldAutoLoginBots()); // Explicit legacy override.
    config.randomBotAutologin = false;
    assert(!mgr.ShouldAutoLoginBots());
    config.randomBotAutologin = true; config.enabled = false;
    assert(!mgr.ShouldAutoLoginBots());
    std::cout << "PASS: bot-only, character selection, entering/leaving world, logout and config gates\n";
}
'''
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder)
        (path / "test.cpp").write_text(program + methods + cases)
        subprocess.run(shlex.split(os.environ.get("CXX", "c++")) + [
            "-std=c++20", "-Wall", "-Wextra", "-Werror", str(path / "test.cpp"),
            "-o", str(path / "test")], check=True)
        subprocess.run([str(path / "test")], check=True)


if __name__ == "__main__":
    main()
