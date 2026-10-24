#!/usr/bin/env python3
"""Compile the production appearance selection against the production-loaded store."""
import argparse
from pathlib import Path
import re
import resource
import subprocess
import tempfile


def main():
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--factory-source', type=Path, default=root / 'modules/mod_playerbots/src/Factory/RandomPlayerbotFactory.cpp')
    parser.add_argument('--stores-source', type=Path, default=root / 'src/server/game/DataStores/DBCStores.cpp')
    args = parser.parse_args()
    factory = args.factory_source.read_text(encoding='utf-8-sig')
    stores = args.stores_source.read_text(encoding='utf-8-sig')
    match = re.search(r'LOAD_DBC\([^;]*?,\s*(\w+)\s*,\s*dbcPath,\s*"CharSections\.dbc"', stores)
    if not match:
        raise RuntimeError('Production CharSections loader not found')
    start = factory.index('    std::vector<uint8> skinColors, facialHairTypes;', factory.index('Player* RandomPlayerbotFactory::CreateRandomBot('))
    block = factory[start:factory.index('    WorldPacket p;', start)]
    fixture = r'''
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <utility>
#include <vector>
using uint8 = std::uint8_t;
using uint32 = std::uint32_t;
enum { GENDER_MALE=0, GENDER_FEMALE=1, RACE_NIGHTELF=4, RACE_UNDEAD_PLAYER=5, RACE_TAUREN=6, RACE_DRAENEI=11 };
enum { SECTION_TYPE_SKIN=0, SECTION_TYPE_FACE=1, SECTION_TYPE_FACIAL_HAIR=2, SECTION_TYPE_HAIR=3 };
struct CharSectionsEntry { uint8 RaceID, SexID, BaseSection, VariationIndex, ColorIndex; };
struct Store {
    std::vector<CharSectionsEntry> rows;
    uint32 GetNumRows() const { return rows.size(); }
    CharSectionsEntry const* LookupEntry(uint32 i) const { return i < rows.size() ? &rows[i] : nullptr; }
};
Store sCharSectionsStore, sChrSectionStore;
#define TC_LOG_ERROR(...) ((void)0)
volatile uint32 appearanceSink = 0;
void* selectAppearance(uint8 race, uint8 gender) {
@BLOCK@
    appearanceSink = skinColor + face.first + face.second + hair.first + hair.second + facialHair;
    return reinterpret_cast<void*>(1);
}
int main() {
    int passed = 0;
    auto check = [&](uint8 race, uint8 gender, uint8 sourceRace, uint8 sourceGender, unsigned mask, bool expected) {
        sCharSectionsStore.rows.clear(); sChrSectionStore.rows.clear();
        for (uint8 part = 0; part < 4; ++part)
            if (mask & (1u << part)) @STORE@.rows.push_back({sourceRace, sourceGender, part, 0, 0});
        if ((selectAppearance(race, gender) != nullptr) != expected) std::exit(1);
        ++passed;
    };
    check(1,0,1,0,15,true);
    check(1,0,1,0,0,false);
    check(1,0,1,0,7,false);
    check(1,0,1,0,11,false);
    check(1,1,1,1,11,true);
    check(6,0,6,0,11,true);
    check(4,1,4,1,11,false);
    check(1,0,3,0,15,false);
    check(1,0,1,1,15,false);
    std::cout << "PASS: " << passed << " appearance cases; production loader and bot store agree\n";
}
'''.replace('@BLOCK@', block).replace('@STORE@', match.group(1))
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / 'appearance.cpp'
        binary = Path(directory) / 'appearance'
        source.write_text(fixture)
        subprocess.run(['c++', '-std=c++20', '-O2', str(source), '-o', str(binary)], check=True)
        result = subprocess.run([str(binary)], capture_output=True, text=True,
                                preexec_fn=lambda: resource.setrlimit(resource.RLIMIT_CORE, (0, 0)))
        if result.returncode:
            raise RuntimeError(f'Appearance test failed with exit {result.returncode}: {result.stderr}')
        print(result.stdout, end='')


if __name__ == '__main__':
    main()
