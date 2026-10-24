#!/usr/bin/env python3
"""Exercise actual grind selection/action methods with controlled server interfaces."""
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile


def definition(text, name):
    match = re.search(r"(?:bool|Unit\*) " + re.escape(name) + r"\([^)]*\)\s*\{", text)
    if not match:
        raise RuntimeError(f"Missing production method {name}")
    end, depth = match.end(), 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[match.start():end]


def main():
    root = Path(__file__).resolve().parents[2] / "modules/mod_playerbots/src/strategy"
    values = (root / "value/GrindTargetValue.cpp").read_text()
    actions = (root / "actions/ChooseTargetActions.cpp").read_text()
    methods = "\n".join([
        definition(values, "GrindTargetValue::Calculate"),
        definition(actions, "AttackAnythingAction::isUseful"),
        definition(actions, "AttackAnythingAction::Execute"),
    ])
    program = r'''
#include <cassert>
#include <cstdint>
#include <iostream>
#include <string>
using uint32 = std::uint32_t;
using ObjectGuid = uint32;
struct Event {};
enum { GRIND_ACTIVITY };
enum class NewRpgStatus { GO_GRIND, NEAR_NPC, REST, GO_INNKEEPER, OTHER };
struct Unit {
    std::string name = "Wolf";
    std::string const& GetName() { return name; }
    ObjectGuid GetGUID() { return 42; }
};
struct Group { uint32 GetMembersCount() { return 3; } };
struct Motion { int clears = 0; void Clear() { ++clears; } };
struct Player {
    Group* group = nullptr;
    Motion motion;
    float distance = 10;
    Group* GetGroup() { return group; }
    float GetDistance(Unit*) { return distance; }
    Motion* GetMotionMaster() { return &motion; }
};
struct GuidValue { ObjectGuid value = 0; void Set(ObjectGuid guid) { value = guid; } };
struct Context {
    GuidValue value;
    template<class T> GuidValue* GetValue(char const*) { return &value; }
};
struct RpgInfo { NewRpgStatus status = NewRpgStatus::OTHER; };
struct AI {
    bool realMaster = false, active = true, movable = true;
    Context context;
    RpgInfo rpg;
    bool HasRealPlayerMaster() { return realMaster; }
    bool AllowActivity(int) { return active; }
    RpgInfo const& GetRpgInfo() { return rpg; }
    Context* GetAiObjectContext() { return &context; }
};
#define AI_VALUE(type, name) (botAI->movable)
int attacks = 0;
struct AttackAction { bool Execute(Event) { ++attacks; return true; } };
struct AttackAnythingAction : AttackAction {
    AI* botAI;
    Player* bot;
    Unit* target;
    Context* context;
    Unit* GetTarget() { return target; }
    bool isUseful();
    bool Execute(Event event);
};
struct GrindTargetValue {
    AI* botAI;
    Player* bot;
    Unit* result;
    int calls = 0;
    Unit* FindTargetForGrinding(uint32 count) { ++calls; return count == 0 ? result : nullptr; }
    Unit* Calculate();
};
'''
    cases = r'''
int main() {
    AI ai;
    Player bot;
    Unit target;
    AttackAnythingAction action;
    action.botAI = &ai; action.bot = &bot; action.target = &target; action.context = &ai.context;
    GrindTargetValue value{&ai, &bot, &target};
    ai.realMaster = true;
    assert(value.Calculate() == nullptr && value.calls == 0);
    assert(!action.isUseful());
    assert(!action.Execute(Event{}) && attacks == 0);
    assert(ai.context.value.value == 0 && bot.motion.clears == 0);

    ai.realMaster = false;
    assert(value.Calculate() == &target && value.calls == 1);
    assert(action.isUseful());
    assert(action.Execute(Event{}) && attacks == 1);
    assert(ai.context.value.value == 42 && bot.motion.clears == 1);

    // A queued/cached autonomous action must not pull after acquiring a player master.
    ai.realMaster = true;
    assert(!action.Execute(Event{}) && attacks == 1 && bot.motion.clears == 1);
    ai.realMaster = false;
    ai.active = false;
    assert(!action.isUseful());
    ai.active = true; ai.movable = false;
    assert(!action.isUseful());
    ai.movable = true; action.target = nullptr;
    assert(!action.isUseful());
    action.target = &target; target.name = "Training Dummy";
    assert(!action.isUseful());
    target.name = "Wolf"; ai.rpg.status = NewRpgStatus::REST; bot.distance = 30;
    assert(!action.isUseful());
    std::cout << "PASS: player companion, autonomous bot, cached pull and existing grind guards\n";
}
'''
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder)
        (path / "test.cpp").write_text(program + methods + cases)
        subprocess.run(shlex.split(os.environ.get("CXX", "c++")) +
                       ["-std=c++20", "-Wall", "-Wextra", "-Werror", "-Wno-unused-variable", str(path / "test.cpp"),
                        "-o", str(path / "test")], check=True)
        subprocess.run([str(path / "test")], check=True)


if __name__ == "__main__":
    main()
