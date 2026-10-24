#!/usr/bin/env python3
"""Compile the actual common ActionContext against controlled action interfaces."""
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile


def main():
    root = Path(__file__).resolve().parents[2]
    source = (root / 'modules/mod_playerbots/src/strategy/actions/ActionContext.h').read_text()
    start = source.index('class ActionContext :')
    end = source.rindex('};') + 2
    context = source[start:end]
    names = sorted(set(re.findall(r'new (\w+)\(', context)))
    prelude = r'''
#include <cassert>
#include <iostream>
#include <string>
#include <unordered_map>
struct PlayerbotAI {};
struct Action { virtual ~Action() = default; };
template<class T> class NamedObjectContext {
protected:
    std::unordered_map<std::string,T*(*)(PlayerbotAI*)> creators;
public:
    T* create(std::string const& name, PlayerbotAI* ai) {
        auto it = creators.find(name);
        return it == creators.end() ? nullptr : it->second(ai);
    }
};
'''
    stubs = '\n'.join(f'struct {name} : Action {{ explicit {name}(PlayerbotAI*) {{}} }};' for name in names)
    cases = r'''
int main() {
    ActionContext context;
    PlayerbotAI ai;
    Action* shoot = context.create("shoot", &ai);
    Action* formation = context.create("combat formation move", &ai);
    assert(dynamic_cast<CastShootAction*>(shoot));
    assert(dynamic_cast<CombatFormationMoveAction*>(formation));
    assert(!context.create("unknown", &ai));
    Action* follow = context.create("follow", &ai);
    assert(dynamic_cast<FollowAction*>(follow));
    delete shoot; delete formation; delete follow;
    std::cout << "PASS: actual common registry resolves shoot, combat formation move and existing follow\n";
}
'''
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder)
        (path / 'test.cpp').write_text(prelude + stubs + context + cases)
        subprocess.run(shlex.split(os.environ.get('CXX','c++')) + [
            '-std=c++20','-Wall','-Wextra','-Werror', str(path/'test.cpp'),'-o',str(path/'test')], check=True)
        subprocess.run([str(path/'test')], check=True)


if __name__ == '__main__':
    main()
