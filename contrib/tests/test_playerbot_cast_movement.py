#!/usr/bin/env python3
"""Compile the actual PrepareSpellMovement method against controlled interfaces.

Checks movement decisions, not real spell execution, navigation or gameplay.
"""
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile


def main():
    root = Path(__file__).resolve().parents[2]
    source = (root / "modules/mod_playerbots/src/strategy/actions/GenericSpellActions.cpp").read_text()
    match = re.search(r"bool CastSpellAction::PrepareSpellMovement\([^)]*\)\s*\{", source)
    if not match:
        raise RuntimeError("Production method not found")
    end = match.end()
    depth = 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    method = source[match.start():end]
    program = r'''
#include <cassert>
#include <cstdint>
#include <iostream>
using uint32 = std::uint32_t;
enum { SPELL_AURA_CAST_WHILE_WALKING, CURRENT_GENERIC_SPELL, CURRENT_CHANNELED_SPELL };
struct SpellInfo {
    int time = 1500;
    bool channel = false, repeat = false, positive = false;
    float range = 30;
    int CalcCastTime(uint32) const { return time; }
    bool IsChanneled() const { return channel; }
    bool IsAutoRepeatRangedSpell() const { return repeat; }
    bool IsPositive() const { return positive; }
    float GetMaxRange(bool, void*) const { return range; }
};
struct Unit {
    bool world = true;
    uint32 map = 0;
    float distance = 10;
    bool IsInWorld() const { return world; }
    uint32 GetMapId() const { return map; }
};
struct Pet { bool learned = true; bool HasSpell(uint32) const { return learned; } };
struct Motion { int cleared = 0; void Clear() { ++cleared; } };
struct Player : Unit {
    bool moving = true, learned = true, walkAura = false, los = true;
    bool generic = false, channel = false;
    uint32 level = 1;
    int stopped = 0;
    Pet* pet = nullptr;
    Motion motion;
    Pet* GetPet() { return pet; }
    bool HasSpell(uint32) const { return learned; }
    bool isMoving() const { return moving; }
    uint32 GetLevel() const { return level; }
    bool HasAuraTypeWithAffectMask(int, SpellInfo const*) const { return walkAura; }
    bool IsWithinCombatRange(Unit* target, float range) const { return target->distance <= range; }
    bool IsWithinLOSInMap(Unit*) const { return los; }
    bool GetCurrentSpell(int slot) const { return slot == CURRENT_GENERIC_SPELL ? generic : channel; }
    Motion* GetMotionMaster() { return &motion; }
    void StopMoving() { ++stopped; moving = false; }
};
struct SpellManager {
    SpellInfo info;
    SpellInfo const* GetSpellInfo(uint32 id) { return id == 1 ? &info : nullptr; }
} manager;
auto* sSpellMgr = &manager;
struct CastSpellAction {
    Player* bot;
    bool PrepareSpellMovement(uint32 spellId, Unit* target);
};
'''
    cases = r'''
int main() {
    int checks = 0;
    auto check = [&](auto configure, bool expected, int stops) {
        Player player;
        Unit target;
        manager.info = SpellInfo{};
        configure(player, target, manager.info);
        CastSpellAction action{&player};
        assert(action.PrepareSpellMovement(1, &target) == expected);
        assert(player.stopped == stops);
        assert(player.motion.cleared == stops);
        ++checks;
    };
    check([](auto&, auto&, auto&) {}, true, 1);
    check([](auto& p, auto&, auto&) { p.learned = false; }, false, 0);
    check([](auto& p, auto&, auto&) { p.moving = false; }, true, 0);
    check([](auto&, auto&, auto& s) { s.time = 0; }, true, 0);
    check([](auto& p, auto&, auto&) { p.walkAura = true; }, true, 0);
    check([](auto&, auto& t, auto&) { t.distance = 31; }, false, 0);
    check([](auto&, auto& t, auto&) { t.distance = 30; }, true, 1);
    check([](auto& p, auto&, auto&) { p.los = false; }, false, 0);
    check([](auto&, auto& t, auto&) { t.world = false; }, false, 0);
    check([](auto&, auto& t, auto&) { t.map = 1; }, false, 0);
    check([](auto&, auto& t, auto& s) { t.distance = 35; s.range = 40; s.positive = true; }, true, 1);
    check([](auto& p, auto&, auto&) { p.generic = true; }, false, 0);
    check([](auto& p, auto&, auto&) { p.channel = true; }, false, 0);
    check([](auto&, auto&, auto& s) { s.time = 0; s.channel = true; }, true, 1);
    check([](auto&, auto&, auto& s) { s.time = 0; s.repeat = true; }, true, 1);
    Player player;
    CastSpellAction action{&player};
    assert(!action.PrepareSpellMovement(0, nullptr));
    assert(player.stopped == 0);
    ++checks;
    assert(action.PrepareSpellMovement(1, nullptr));
    assert(player.stopped == 1);
    ++checks;
    player = Player{};
    Pet pet;
    player.pet = &pet;
    player.learned = false;
    assert(action.PrepareSpellMovement(1, nullptr));
    assert(player.stopped == 0 && player.motion.cleared == 0);
    ++checks;
    std::cout << "PASS: " << checks << " production spell-movement scenarios\n";
}
'''
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder)
        (path / "test.cpp").write_text(program + method + cases)
        compiler = shlex.split(os.environ.get("CXX", "c++"))
        subprocess.run(compiler + ["-std=c++20", "-Wall", "-Wextra", "-Werror",
                                  str(path / "test.cpp"), "-o", str(path / "test")], check=True)
        subprocess.run([str(path / "test")], check=True)


if __name__ == "__main__":
    main()
