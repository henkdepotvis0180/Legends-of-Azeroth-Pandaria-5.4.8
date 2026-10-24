#ifndef PLAYERBOT_EQUIPMENT_SELECTION_POLICY_H
#define PLAYERBOT_EQUIPMENT_SELECTION_POLICY_H

#include <cstdint>

namespace playerbots
{
// Include requirement zero for starting equipment; never search above the bot.
constexpr std::int32_t MinimumEquipmentLevel(std::uint32_t level)
{
    return level > 10 ? static_cast<std::int32_t>(level - 10) : 0;
}

// Early white/grey equipment often has armor or weapon damage but no attributes.
// Class, race, armor/weapon proficiency and slot checks still apply separately.
constexpr bool AllowStatlessStarterEquipment(std::uint32_t level, std::uint32_t quality,
    std::uint32_t spellStats, std::uint32_t attackStats, std::uint32_t tankStats)
{
    return level < 10 && quality <= 1 && !spellStats && !attackStats && !tankStats;
}
}

#endif
