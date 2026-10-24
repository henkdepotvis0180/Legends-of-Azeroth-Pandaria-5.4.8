#!/usr/bin/env python3
"""Compile the production class-spell learner with controlled core data."""
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile


def definition(source):
    match = re.search(r"uint32 BotFactory::LearnClassSpells\(\)\s*\{", source)
    end, depth = match.end(), 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[match.start():end]


def main():
    root = Path(__file__).resolve().parents[2]
    source = (root / "modules/mod_playerbots/src/Factory/BotFactory.cpp").read_text()
    program = r'''
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <set>
#include <vector>
using uint32 = std::uint32_t;
struct SpellInfo {
    uint32 Id, SpellLevel, SpellFamilyName;
    bool valid = true;
    SpellInfo const* GetFirstRankSpell() const { return this; }
};
struct ChrClassesEntry { uint32 spellfamily; };
struct Classes {
    std::map<uint32, ChrClassesEntry> data;
    ChrClassesEntry const* LookupEntry(uint32 cls) {
        auto it = data.find(cls); return it == data.end() ? nullptr : &it->second;
    }
} sChrClassesStore;
struct SpecializationSpellsEntry { uint32 SpecID, SpellID; };
std::vector<SpecializationSpellsEntry const*> sSpecializationSpellsStore;
struct Player {
    uint32 cls = 1, level = 4, spec = 0, team = 0;
    uint32 xp = 123, gear = 456;
    std::set<uint32> known, wrongRace;
    uint32 GetClass() { return cls; }
    uint32 GetClassMask() { return 1u << (cls-1); }
    uint32 GetRaceMask() { return 1; }
    uint32 GetTeam() { return team; }
    uint32 GetLevel() { return level; }
    uint32 GetTalentSpecialization() { return spec; }
    bool HasSpell(uint32 id) { return known.count(id); }
    bool IsSpellFitByClassAndRace(uint32 id) { return !wrongRace.count(id); }
    void LearnSpell(uint32 id, bool) { known.insert(id); }
};
struct SkillLineAbilityEntry { uint32 Spell, ClassMask, RaceMask; };
struct Abilities {
    std::vector<SkillLineAbilityEntry> data;
    uint32 GetNumRows() { return data.size(); }
    SkillLineAbilityEntry const* LookupEntry(uint32 index) { return &data.at(index); }
} sSkillLineAbilityStore;
// Deliberately no ServiceMgr or SQL class-spell list: an empty table must work.
struct SpellMgr {
    std::map<uint32, SpellInfo> data;
    SpellInfo const* GetSpellInfo(uint32 id) {
        auto it = data.find(id); return it == data.end() ? nullptr : &it->second;
    }
    static bool IsSpellValid(SpellInfo const* info, Player*, bool) { return info->valid; }
} spellMgr;
auto* sSpellMgr = &spellMgr;
struct DBCManager {
    std::set<uint32> talents;
    uint32 GetTalentSpellCost(uint32 id) { return talents.count(id); }
} sDBCManager;
struct BotFactory {
    Player* bot;
    uint32 LearnClassSpells();
};
'''
    cases = r'''
int main() {
    // All 11 MoP class IDs share the same level-aware path; no class spell IDs are hardcoded.
    for (uint32 cls = 1; cls <= 11; ++cls) {
        sChrClassesStore.data[cls] = {cls + 100};
        sSkillLineAbilityStore.data.push_back({cls, 1u << (cls-1), 1});
        spellMgr.data[cls] = {cls, 4, cls + 100};
        Player bot; bot.cls = cls;
        BotFactory factory{&bot};
        assert(factory.LearnClassSpells() == 1 && bot.HasSpell(cls));
        assert(factory.LearnClassSpells() == 0);
        assert(bot.xp == 123 && bot.gear == 456);
        bot.known.clear(); bot.level = 3;
        assert(factory.LearnClassSpells() == 0 && bot.known.empty());
    }
    Player bot; BotFactory factory{&bot};
    sSkillLineAbilityStore.data.clear();
    for (uint32 id = 100; id <= 110; ++id)
        sSkillLineAbilityStore.data.push_back({id, 1, 1});
    sSkillLineAbilityStore.data.push_back({111, 2, 1}); // Another class.
    sSkillLineAbilityStore.data.push_back({112, 1, 2}); // Another race.
    spellMgr.data[111] = {111,4,101};
    spellMgr.data[112] = {112,4,101};
    spellMgr.data[100] = {100,4,101}; // Valid base spell.
    spellMgr.data[101] = {101,5,101}; // Too early.
    spellMgr.data[102] = {102,0,101}; // Server-side spell.
    spellMgr.data[103] = {103,4,999}; // Another class family.
    spellMgr.data[104] = {104,4,101}; bot.wrongRace.insert(104);
    spellMgr.data[105] = {105,4,101}; sDBCManager.talents.insert(105);
    spellMgr.data[106] = {106,4,101,false}; // Invalid spell.
    // 107 deliberately missing.
    spellMgr.data[108] = {108,4,101};
    spellMgr.data[109] = {109,4,101};
    spellMgr.data[110] = {110,4,101}; bot.known.insert(110);
    SpecializationSpellsEntry own{256,108}, other{258,109};
    sSpecializationSpellsStore = {&own,&other};
    bot.spec = 256;
    assert(factory.LearnClassSpells() == 1 && bot.HasSpell(100));
    assert(!bot.HasSpell(108) && !bot.HasSpell(109)); // Pre-spec at level 4.
    bot.level = 10;
    assert(factory.LearnClassSpells() == 2 && bot.HasSpell(101) && bot.HasSpell(108));
    assert(!bot.HasSpell(109) && !bot.HasSpell(105) && !bot.HasSpell(104));
    assert(!bot.HasSpell(111) && !bot.HasSpell(112));
    bot.cls = 99;
    assert(factory.LearnClassSpells() == 0); // Missing class table.
    assert(factory.LearnClassSpells() == 0); // Missing class DBC.
    std::cout << "PASS: no SQL dependency, DBC class/race masks, 11 class paths, level boundaries, duplicate learn, race/family, talents, spec gates, invalid/missing data, retained XP/gear\n";
}
'''
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder)
        (path / "test.cpp").write_text(program + definition(source) + cases)
        subprocess.run(shlex.split(os.environ.get("CXX", "c++")) + [
            "-std=c++20", "-Wall", "-Wextra", "-Werror", str(path / "test.cpp"),
            "-o", str(path / "test")], check=True)
        subprocess.run([str(path / "test")], check=True)


if __name__ == "__main__":
    main()
