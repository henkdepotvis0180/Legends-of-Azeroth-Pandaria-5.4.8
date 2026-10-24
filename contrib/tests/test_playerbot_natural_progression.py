#!/usr/bin/env python3
"""Exercise complete production progression/selection/randomize methods."""
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile


def definition(text, name):
    match = re.search(r"(?:bool|void) " + re.escape(name) + r"\([^)]*\)(?: const)?\s*\{", text)
    if not match:
        raise RuntimeError(f"Missing {name}")
    end, depth = match.end(), 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[match.start():end]


def main():
    root = Path(__file__).resolve().parents[2]
    source = (root / "modules/mod_playerbots/src/Manager/RandomPlayerbotMgr.cpp").read_text()
    methods = "\n".join(definition(source, "RandomPlayerbotMgr::" + name) for name in [
        "IsAllowedProgressionBot", "ApplyNaturalProgression", "Randomize"])
    program = r'''
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <string>
using uint32 = std::uint32_t;
using uint8 = std::uint8_t;
enum { CLASS_DEATH_KNIGHT = 6, CONFIG_MAX_PLAYER_LEVEL, PLAYER_FLAGS_NO_XP_GAIN };
enum class HighGuid { Player };
struct ObjectGuid {
    uint32 value;
    template<HighGuid> static ObjectGuid Create(uint32 value) { return {value}; }
    uint32 GetCounter() const { return value; }
};
struct CharacterCacheEntry { uint8 Class; };
struct Cache {
    std::map<uint32, CharacterCacheEntry> entries;
    CharacterCacheEntry const* GetCharacterCacheByGuid(ObjectGuid guid) {
        auto it = entries.find(guid.value);
        return it == entries.end() ? nullptr : &it->second;
    }
} cache;
auto* sCharacterCache = &cache;
struct Config {
    bool randomBotNaturalProgression = false;
    uint32 randomBotStartingMinLevel = 4, randomBotStartingMaxLevel = 10;
} config;
auto* sPlayerbotAIConfig = &config;
struct World {
    uint32 cap = 90;
    uint32 getIntConfig(int) { return cap; }
} world;
auto* sWorld = &world;
uint32 nextRoll = 4;
uint32 urand(uint32 low, uint32 high) {
    assert(low <= high && nextRoll >= low && nextRoll <= high);
    return nextRoll;
}
struct AI { void Reset(bool) {} };
struct Player {
    uint32 level = 1, xp = 73, gear = 123, quests = 7, saves = 0;
    uint8 cls = 1;
    bool random = true, xpLocked = true;
    AI ai;
    uint32 GetLevel() { return level; }
    uint8 GetClass() { return cls; }
    void GiveLevel(uint32 value) { level = value; }
    void RemovePlayerFlag(int) { xpLocked = false; }
    void SaveToDB(bool) { ++saves; }
    ObjectGuid GetGUID() { return {1}; }
};
#define GET_PLAYERBOT_AI(bot) (&(bot)->ai)
int factoryCalls = 0;
struct BotFactory {
    Player* bot;
    BotFactory(Player* value, uint32) : bot(value) {}
    void Randomize(bool) { ++factoryCalls; bot->xp = 0; bot->gear = 0; }
};
struct RandomPlayerbotMgr {
    bool IsAllowedProgressionBot(uint32 bot) const;
    void ApplyNaturalProgression(Player* bot);
    void Randomize(Player* bot);
    bool IsRandomBot(Player* bot) { return bot->random; }
    uint32 GetValue(Player*, char const*) { return 1; }
    void Refresh(Player*) {}
    void RandomTeleportForLevel(Player*) {}
    void ScheduleRandomize(uint32, uint32) {}
};
'''
    cases = r'''
int main() {
    RandomPlayerbotMgr mgr;
    Player bot;
    mgr.ApplyNaturalProgression(&bot);
    assert(bot.level == 1 && bot.xpLocked && bot.saves == 0);
    config.randomBotNaturalProgression = true;
    for (uint32 level = 4; level <= 10; ++level) {
        bot = Player{}; nextRoll = level;
        mgr.ApplyNaturalProgression(&bot);
        assert(bot.level == level && bot.xp == 73 && bot.gear == 123 && bot.quests == 7);
        assert(!bot.xpLocked && bot.saves == 1);
        nextRoll = 4;
        mgr.ApplyNaturalProgression(&bot);
        assert(bot.level == level && bot.xp == 73 && bot.saves == 2);
    }
    for (uint32 level : {2u, 3u, 15u, 50u, 90u}) {
        bot = Player{}; bot.level = level;
        mgr.Randomize(&bot);
        assert(bot.level == level && bot.xp == 73 && bot.gear == 123 && bot.quests == 7);
        assert(!bot.xpLocked && factoryCalls == 0);
    }
    bot = Player{}; bot.random = false;
    mgr.ApplyNaturalProgression(&bot);
    assert(bot.level == 1 && bot.xpLocked && bot.saves == 0);
    bot = Player{}; bot.cls = CLASS_DEATH_KNIGHT; bot.level = 55;
    mgr.ApplyNaturalProgression(&bot);
    assert(bot.level == 55 && bot.xpLocked && bot.saves == 0);
    assert(!mgr.IsAllowedProgressionBot(99)); // Missing cache entry: fail closed.
    cache.entries[1] = {1}; cache.entries[2] = {CLASS_DEATH_KNIGHT};
    assert(mgr.IsAllowedProgressionBot(1) && !mgr.IsAllowedProgressionBot(2));
    world.cap = 3; nextRoll = 3; bot = Player{};
    mgr.ApplyNaturalProgression(&bot);
    assert(bot.level == 3); // Respect core cap even below configured start range.
    config.randomBotNaturalProgression = false;
    assert(mgr.IsAllowedProgressionBot(2) && mgr.IsAllowedProgressionBot(99));
    bot = Player{}; mgr.Randomize(&bot);
    assert(factoryCalls == 1); // Legacy mode remains available.
    std::cout << "PASS: start range 4-10, relog, earned levels/XP/gear/quests, XP unlock, DK filter, core cap and legacy mode\n";
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
