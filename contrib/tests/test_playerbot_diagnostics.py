#!/usr/bin/env python3
"""Compile the complete diagnostic handler; exercise it without casting/movement APIs."""
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile


def main():
    root = Path(__file__).resolve().parents[2]
    source = (root / "modules/mod_playerbots/src/cs_playerbots.cpp").read_text()
    match = re.search(r"static bool HandleBotDiagnostic\([^)]*\)\s*\{", source)
    end, depth = match.end(), 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    method = source[match.start():end]
    program = r'''
#include <cassert>
#include <cstdarg>
#include <cstdint>
#include <cstdio>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <type_traits>
#include <vector>
using uint32 = std::uint32_t;
using GuidVector = std::vector<uint32>;
enum BotState { BOT_STATE_COMBAT, BOT_STATE_NON_COMBAT };
enum { POWER_MANA, PLAYERSPELL_REMOVED };
struct ChatHandler {
    std::string output;
    void SendSysMessage(char const* text) { output += text; output += '\n'; }
    void PSendSysMessage(char const* format, ...) __attribute__((format(printf,2,3))) {
        char data[2048]; va_list args; va_start(args,format);
        vsnprintf(data,sizeof(data),format,args); va_end(args); SendSysMessage(data);
    }
};
struct Unit {
    std::string name = "Wolf";
    std::string const& GetName() { return name; }
    float GetHealthPct() { return 30; }
};
struct Group {};
struct PlayerSpell { int state = 1; bool active = true, disabled = false; };
struct Player : Unit {
    Group* group = nullptr;
    std::map<uint32,PlayerSpell*> book;
    uint32 GetLevel() { return 4; }
    bool IsInCombat() { return true; }
    bool isMoving() { return false; }
    int GetPower(int) { return 100; }
    int GetMaxPower(int) { return 100; }
    Group* GetGroup() { return group; }
    Unit* GetVictim() { return nullptr; }
    auto const& GetSpellMap() { return book; }
    float GetDistance(Unit*) { return 10; }
    bool IsWithinLOSInMap(Unit*) { return true; }
} bot, master;
struct SpellInfo {
    char const* SpellName = "Smite";
    uint32 SpellLevel = 1;
    bool IsPassive() const { return false; }
    bool IsPositive() const { return false; }
} spell;
struct SpellMgr { SpellInfo const* GetSpellInfo(uint32 id) { return id ? &spell : nullptr; } } mgr;
auto* sSpellMgr = &mgr;
template<class T> struct Value { T value{}; T Get() { return value; } };
Unit wolf;
struct Context {
    Value<Unit*> target{&wolf}; Value<GuidVector> attackers{{1}}; Value<uint32> id{585};
    template<class T> Value<T>* GetValue(std::string const&, std::string const& = "") {
        if constexpr(std::is_same_v<T,Unit*>) return &target;
        else if constexpr(std::is_same_v<T,GuidVector>) return &attackers;
        else return &id;
    }
};
struct PlayerbotAI {
    bool real = false;
    int probes = 0;
    bool tracing = false;
    void StartDiagnosticTrace() { tracing = true; }
    std::string GetDiagnosticTrace(BotState) const { return tracing ? "A:smite - IMPOSSIBLE\n" : ""; }
    Context context;
    bool IsRealPlayer() { return real; }
    Player* GetMaster() { return &master; }
    Player* GetGroupMaster() { return &master; }
    Context* GetAiObjectContext() { return &context; }
    BotState GetState() { return BOT_STATE_COMBAT; }
    bool HasRealPlayerMaster() { return true; }
    std::vector<std::string> GetStrategies(BotState) { return {"follow","heal"}; }
    bool CanCastSpell(uint32,Unit*) { ++probes; return true; }
} ai;
#define GET_PLAYERBOT_AI(player) (&::ai)
namespace ObjectAccessor {
Player* FindPlayerByName(std::string const& name) { return name == "Clemeria" ? &bot : nullptr; }
}
struct Commands {
'''
    cases = r'''
};
int main() {
    ChatHandler handler;
    assert(!Commands::HandleBotDiagnostic(&handler,nullptr));
    ai.real = true; assert(!Commands::HandleBotDiagnostic(&handler,"Clemeria"));
    ai.real = false;
    assert(!Commands::HandleBotDiagnostic(&handler,"Clemeria invalid"));
    assert(Commands::HandleBotDiagnostic(&handler,"Clemeria trace"));
    assert(ai.tracing && ai.probes == 0);
    PlayerSpell known;
    bot.book[585] = &known; bot.name = "Clemeria";
    master.name = "Sam";
    Group group; bot.group = &group; master.group = &group;
    assert(Commands::HandleBotDiagnostic(&handler,"Clemeria"));
    assert(handler.output.find("BOTDIAG Clemeria level=4") != std::string::npos);
    assert(handler.output.find("sameGroup=1") != std::string::npos);
    assert(handler.output.find("probe smite id=585 target=Wolf canCast=1") != std::string::npos);
    assert(ai.probes == 6);
    assert(handler.output.find("A:smite - IMPOSSIBLE") != std::string::npos);
    ai.context.target.value = nullptr; ai.probes = 0;
    assert(Commands::HandleBotDiagnostic(&handler,"Clemeria") && ai.probes == 0);
    std::cout << "PASS: diagnostic handler, invalid/real player guards, party snapshot, known spells and missing target probes; no cast execution API\n";
}
'''
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder)
        (path / "test.cpp").write_text(program + method + cases)
        subprocess.run(shlex.split(os.environ.get("CXX", "c++")) + [
            "-std=c++20", "-Wall", "-Wextra", "-Werror", str(path / "test.cpp"),
            "-o", str(path / "test")], check=True)
        subprocess.run([str(path / "test")], check=True)


if __name__ == "__main__":
    main()
