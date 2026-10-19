#!/usr/bin/env python3
"""Compile actual Engine logging/arming methods with legacy testMode disabled."""
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile


def main():
    root = Path(__file__).resolve().parents[2] / 'modules/mod_playerbots/src/strategy'
    source = (root / 'Engine.cpp').read_text()
    header = (root / 'Engine.h').read_text()
    start = source.index('void Engine::LogAction(')
    end = source.index('\nvoid Engine::ChangeStrategy', start)
    arm = re.search(r'void StartDiagnosticTrace\(\) \{[^}]*\}', header).group()
    program = r'''
#include <cassert>
#include <cstdarg>
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <iostream>
#include <string>
using uint32 = std::uint32_t;
struct Player {};
struct AI { Player* GetBot() { return nullptr; } } ai;
struct Engine {
    AI* botAI = &ai;
    bool testMode = false;
    uint32 diagnosticTicksRemaining = 0;
    std::string diagnosticTrace, lastAction;
    void LogAction(char const* format, ...);
'''
    cases = r'''
};
int main() {
    Engine selected, other;
    selected.LogAction("A:smite - OK");
    assert(selected.diagnosticTrace.empty());
    selected.StartDiagnosticTrace();
    assert(selected.diagnosticTicksRemaining == 20);
    selected.LogAction("TRACE tick minimal=%u queue=%u", 0u, 4u);
    selected.LogAction("A:%s - IMPOSSIBLE", "smite");
    selected.LogAction("Multiplier passive made action smite useless");
    selected.LogAction("No actions executed");
    assert(selected.diagnosticTrace.find("A:smite - IMPOSSIBLE") != std::string::npos);
    other.LogAction("A:smite - OK");
    assert(other.diagnosticTrace.empty());
    auto previous = selected.diagnosticTrace;
    selected.LogAction("PUSH:irrelevant");
    assert(selected.diagnosticTrace == previous);
    for (int i = 0; i < 10000; ++i) selected.LogAction("A:action-%d - OK", i);
    assert(selected.diagnosticTrace.size() <= 6000);
    assert(selected.diagnosticTrace.find("action-9999") != std::string::npos);
    selected.LogAction("A:%010000d", 7);
    assert(selected.diagnosticTrace.size() <= 6000);
    selected.diagnosticTicksRemaining = 0;
    previous = selected.diagnosticTrace;
    selected.LogAction("A:expired - OK");
    assert(selected.diagnosticTrace == previous);
    selected.StartDiagnosticTrace();
    assert(selected.diagnosticTrace.empty() && selected.diagnosticTicksRemaining == 20);
    std::cout << "PASS: opt-in per engine, formatting, event filtering, bounded/oversized output, stopped trace and rearming\n";
}
'''
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder)
        (path / 'test.cpp').write_text(program + arm + '\n' + cases + '\n' + source[start:end])
        subprocess.run(shlex.split(os.environ.get('CXX', 'c++')) + [
            '-std=c++20', '-Wall', '-Wextra', '-Werror', '-Wno-unused-variable',
            str(path / 'test.cpp'), '-o', str(path / 'test')], check=True)
        subprocess.run([str(path / 'test')], cwd=path, check=True)
        assert not (path / 'test.log').exists(), 'Diagnostic capture must not enable legacy file logging'


if __name__ == '__main__':
    main()
