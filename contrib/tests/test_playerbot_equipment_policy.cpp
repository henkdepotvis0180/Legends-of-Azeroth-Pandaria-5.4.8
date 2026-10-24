#include "EquipmentSelectionPolicy.h"

#include <cassert>
#include <cstdint>
#include <iostream>

int main()
{
    using namespace playerbots;
    assert(MinimumEquipmentLevel(1) == 0);
    assert(MinimumEquipmentLevel(9) == 0);
    assert(MinimumEquipmentLevel(10) == 0);
    assert(MinimumEquipmentLevel(11) == 1);
    assert(MinimumEquipmentLevel(90) == 80);

    for (std::int32_t level = 1; level <= 90; ++level)
    {
        int count = 0;
        bool includesZero = false;
        for (std::int32_t requirement = level;
             requirement >= MinimumEquipmentLevel(level); --requirement)
        {
            assert(requirement >= 0 && requirement <= level);
            includesZero |= requirement == 0;
            ++count;
        }
        assert(count == (level <= 10 ? level + 1 : 11));
        assert(includesZero == (level <= 10));
    }

    assert(AllowStatlessStarterEquipment(1, 0, 0, 0, 0));
    assert(AllowStatlessStarterEquipment(1, 1, 0, 0, 0));
    assert(AllowStatlessStarterEquipment(9, 1, 0, 0, 0));
    assert(!AllowStatlessStarterEquipment(10, 1, 0, 0, 0));
    assert(!AllowStatlessStarterEquipment(90, 1, 0, 0, 0));
    for (std::uint32_t quality = 2; quality <= 7; ++quality)
        assert(!AllowStatlessStarterEquipment(1, quality, 0, 0, 0));
    assert(!AllowStatlessStarterEquipment(1, 1, 1, 0, 0));
    assert(!AllowStatlessStarterEquipment(1, 1, 0, 1, 0));
    assert(!AllowStatlessStarterEquipment(1, 1, 0, 0, 1));
    std::cout << "Equipment policy: levels 1-90 and starter-stat boundaries passed\n";
}
