#!/usr/bin/env python3
"""Exercise production party-heal selection, including GM leaders and absent members."""
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile


def definition(source, name):
    match = re.search(r"(?:Unit\*|bool) " + re.escape(name) + r"\([^)]*\)\s*\{", source)
    end, depth = match.end(), 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[match.start():end]


def main():
    root = Path(__file__).resolve().parents[2]
    source = (root / "modules/mod_playerbots/src/strategy/value/PartyMemberToHealValue.cpp").read_text()
    program = r'''
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
using uint8 = std::uint8_t;
using uint32 = std::uint32_t;
struct Unit {
    bool alive = true, inWorld = true, charmed = false, los = true;
    uint32 map = 0;
    float health = 100, x = 0;
    bool IsAlive() { return alive; }
    bool IsInWorld() { return inWorld; }
    bool IsCharmed() { return charmed; }
    uint32 GetMapId() { return map; }
    float GetHealthPct() { return health; }
    float GetDistance2d(Unit* target) { return std::abs(x-target->x); }
    bool IsWithinLOSInMap(Unit* target) { return target->los; }
};
struct Pet : Unit {};
struct Player;
struct GroupReference {
    Player* player = nullptr;
    GroupReference* following = nullptr;
    Player* GetSource() { return player; }
    GroupReference* next() { return following; }
};
struct Group {
    GroupReference* first = nullptr;
    bool isRaidGroup() { return false; }
    GroupReference* GetFirstMember() { return first; }
};
struct Player : Unit {
    bool gm = false;
    Group* group = nullptr;
    Pet* pet = nullptr;
    Unit* charm = nullptr;
    bool IsGameMaster() { return gm; }
    Group* GetGroup() { return group; }
    Pet* GetPet() { return pet; }
    Unit* GetCharm() { return charm; }
};
struct IsTargetOfHealingSpell {};
bool IsTargetOfSpellCast(Player*, IsTargetOfHealingSpell&) { return false; }
struct MinValueCalculator {
    uint32 minValue;
    void* param = nullptr;
    explicit MinValueCalculator(uint32 value) : minValue(value) {}
    void probe(uint32 value, Unit* unit) { minValue = value; param = unit; }
};
struct Config { uint32 mediumHealth = 70; float healDistance = 40; } config;
auto* sPlayerbotAIConfig = &config;
struct PartyMemberToHeal {
    Player* bot;
    Unit* Calculate();
    bool Check(Unit* player);
};
'''
    cases = r'''
int main() {
    Player bot, leader;
    PartyMemberToHeal value{&bot};
    assert(value.Calculate() == &bot);
    GroupReference missing, member{&leader};
    missing.following = &member;
    Group group{&missing}; bot.group = &group;
    leader.gm = true; leader.health = 30;
    assert(value.Calculate() == &leader); // GM master is a normal heal candidate.
    leader.gm = false;
    assert(value.Calculate() == &leader);
    assert(!value.Check(nullptr));
    leader.inWorld = false; assert(value.Calculate() == nullptr);
    leader.inWorld = true; leader.alive = false; assert(value.Calculate() == nullptr);
    leader.alive = true; leader.map = 1; assert(value.Calculate() == nullptr);
    leader.map = 0; leader.charmed = true; assert(value.Calculate() == nullptr);
    leader.charmed = false; leader.los = false; assert(value.Calculate() == nullptr);
    leader.los = true; leader.x = 100; assert(value.Calculate() == nullptr);
    leader.x = 0; leader.health = 100; assert(value.Calculate() == nullptr);
    Pet pet; pet.health = 20; leader.pet = &pet;
    assert(value.Calculate() == &pet);
    pet.alive = false;
    assert(value.Calculate() == nullptr);
    std::cout << "PASS: GM/normal leader, absent group member, health/world/map/LOS/range/charm guards and pets\n";
}
'''
    methods = "\n".join(definition(source, "PartyMemberToHeal::" + name) for name in ["Calculate", "Check"])
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder)
        (path / "test.cpp").write_text(program + methods + cases)
        subprocess.run(shlex.split(os.environ.get("CXX", "c++")) + [
            "-std=c++20", "-Wall", "-Wextra", "-Werror", str(path / "test.cpp"),
            "-o", str(path / "test")], check=True)
        subprocess.run([str(path / "test")], check=True)


if __name__ == "__main__":
    main()
