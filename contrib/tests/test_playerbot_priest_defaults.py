#!/usr/bin/env python3
"""Exercise actual priest default action lists with known-spell subsets."""
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile


def definition(source, name):
    match = re.search(r"NextAction\*\* " + re.escape(name) + r"\(\)\s*\{", source)
    end, depth = match.end(), 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[match.start():end]


def main():
    root = Path(__file__).resolve().parents[2] / "modules/mod_playerbots/src/strategy/Classes/priest"
    methods = "\n".join(definition((root / (name + ".cpp")).read_text(), name + "::getDefaultActions")
                        for name in ["HealPriestStrategy", "ShadowPriestStrategy"])
    methods += "\n" + definition((root / "HolyPriestStrategy.cpp").read_text(), "HolyHealPriestStrategy::getDefaultActions")
    program = r'''
#include <array>
#include <cassert>
#include <iostream>
#include <set>
#include <string>
constexpr float ACTION_DEFAULT = 1;
struct NextAction {
    std::string name;
    float priority;
    NextAction(char const* value, float rank) : name(value), priority(rank) {}
    template<class... T> static NextAction** array(int, T... values) {
        std::array<NextAction*,sizeof...(values)> list{values...};
        auto** result = new NextAction*[list.size()];
        for (unsigned i = 0; i < list.size(); ++i) result[i] = list[i];
        return result;
    }
};
struct HolyHealPriestStrategy { NextAction** getDefaultActions(); };
struct HealPriestStrategy { NextAction** getDefaultActions(); };
struct ShadowPriestStrategy { NextAction** getDefaultActions(); };
std::string select(NextAction** list, std::set<std::string> const& known) {
    std::string selected;
    float rank = -1;
    for (unsigned i = 0; list[i]; ++i) {
        if (known.count(list[i]->name) && list[i]->priority > rank) {
            rank = list[i]->priority; selected = list[i]->name;
        }
        delete list[i];
    }
    delete[] list;
    return selected;
}
'''
    cases = r'''
int main() {
    HolyHealPriestStrategy holy;
    assert(select(holy.getDefaultActions(), {"smite"}) == "smite");
    assert(select(holy.getDefaultActions(), {"shoot"}) == "shoot");
    assert(select(holy.getDefaultActions(), {}) == "");
    HealPriestStrategy heal;
    ShadowPriestStrategy shadow;
    assert(select(heal.getDefaultActions(), {"smite"}) == "smite");
    assert(select(shadow.getDefaultActions(), {"smite"}) == "smite");
    assert(select(heal.getDefaultActions(), {"shoot"}) == "shoot");
    assert(select(shadow.getDefaultActions(), {"shoot"}) == "shoot");
    assert(select(heal.getDefaultActions(), {}) == "");
    assert(select(shadow.getDefaultActions(), {"mind blast","smite"}) == "mind blast");
    std::cout << "PASS: priest known Smite without wand, wand fallback, no known attack, retained shadow priority\n";
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
