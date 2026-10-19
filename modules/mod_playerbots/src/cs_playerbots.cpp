/*
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program. If not, see <http://www.gnu.org/licenses/>.
 */

#include <sstream>

#include "Chat.h"
#include "ObjectAccessor.h"
#include "Playerbots.h"
#include "SpellInfo.h"
#include "SpellMgr.h"
#include "PlayerbotMgr.h"
#include "PerformanceMonitor.h"
#include "PlayerbotAIConfig.h"
#include "RandomPlayerbotMgr.h"
#include "ScriptMgr.h"

class playerbots_commandscript : public CommandScript
{
public:
    playerbots_commandscript() : CommandScript("playerbots_commandscript") {}

    std::vector<ChatCommand> GetCommands() const override
    {
        static std::vector<ChatCommand> commandTable =
        {
            { "npcbot", &HandlePlayerbotCommand, rbac::RBAC_PERM_COMMAND_NPCBOT, Trinity::ChatCommands::Console::Yes },
            { "botdiag", &HandleBotDiagnostic, rbac::RBAC_PERM_COMMAND_NPCBOT, Trinity::ChatCommands::Console::Yes },
            { "pmon",   &HandlePerfMonCommand,   rbac::RBAC_PERM_COMMAND_PMON,   Trinity::ChatCommands::Console::Yes },
        };
        return commandTable;
    }

    static bool HandlePlayerbotCommand(ChatHandler* handler, char const* args)
    {
        return PlayerbotMgr::HandlePlayerbotMgrCommand(handler, args);
    }

    static bool HandleBotDiagnostic(ChatHandler* handler, char const* args)
    {
        std::istringstream input(args ? args : "");
        std::string name;
        input >> name;
        Player* bot = name.empty() ? nullptr : ObjectAccessor::FindPlayerByName(name);
        PlayerbotAI* ai = bot ? GET_PLAYERBOT_AI(bot) : nullptr;
        if (!bot || !ai || ai->IsRealPlayer())
        {
            handler->SendSysMessage("Gebruik: botdiag NaamVanOnlineBot");
            return false;
        }

        std::string option;
        input >> option;
        if (option == "trace")
        {
            ai->StartDiagnosticTrace();
            handler->SendSysMessage("TRACE gestart voor deze bot: 20 volgende ticks per engine. Vecht 5-10 seconden, voer daarna botdiag Naam uit.");
            return true;
        }
        if (!option.empty())
        {
            handler->SendSysMessage("Gebruik: botdiag Naam [trace]");
            return false;
        }

        for (BotState state : {BOT_STATE_NON_COMBAT, BOT_STATE_COMBAT})
        {
            std::string trace = ai->GetDiagnosticTrace(state);
            handler->PSendSysMessage("TRACE[%u] %s", uint32(state), trace.empty() ? "nog geen trace; gebruik botdiag Naam trace" : "acties:");
            std::istringstream lines(trace);
            std::string line;
            while (std::getline(lines, line))
                handler->SendSysMessage(line.c_str());
        }

        auto label = [](Unit* unit) -> std::string
        {
            return unit ? unit->GetName() : "geen";
        };
        Player* master = ai->GetMaster();
        Player* leader = ai->GetGroupMaster();
        Unit* current = ai->GetAiObjectContext()->GetValue<Unit*>("current target")->Get();
        Unit* dps = ai->GetAiObjectContext()->GetValue<Unit*>("dps target")->Get();
        Unit* heal = ai->GetAiObjectContext()->GetValue<Unit*>("party member to heal")->Get();
        handler->PSendSysMessage("BOTDIAG %s level=%u state=%u combat=%u moving=%u mana=%u/%u",
            bot->GetName().c_str(), uint32(bot->GetLevel()), uint32(ai->GetState()),
            uint32(bot->IsInCombat()), uint32(bot->isMoving()),
            uint32(bot->GetPower(POWER_MANA)), uint32(bot->GetMaxPower(POWER_MANA)));
        handler->PSendSysMessage("master=%s leader=%s realMaster=%u sameGroup=%u masterCombat=%u masterVictim=%s",
            label(master).c_str(), label(leader).c_str(), uint32(ai->HasRealPlayerMaster()),
            uint32(master && bot->GetGroup() && master->GetGroup() == bot->GetGroup()),
            uint32(master && master->IsInCombat()), label(master ? master->GetVictim() : nullptr).c_str());
        handler->PSendSysMessage("current=%s dps=%s heal=%s healHealth=%u attackers=%u",
            label(current).c_str(), label(dps).c_str(), label(heal).c_str(),
            heal ? uint32(heal->GetHealthPct()) : 100u,
            uint32(ai->GetAiObjectContext()->GetValue<GuidVector>("attackers")->Get().size()));
        for (BotState state : {BOT_STATE_NON_COMBAT, BOT_STATE_COMBAT})
        {
            std::ostringstream strategies;
            for (std::string const& strategy : ai->GetStrategies(state))
                strategies << strategy << ",";
            handler->PSendSysMessage("strategies[%u]=%s", uint32(state), strategies.str().c_str());
        }

        uint32 printed = 0;
        for (auto const& entry : bot->GetSpellMap())
        {
            if (entry.second->state == PLAYERSPELL_REMOVED || !entry.second->active || entry.second->disabled)
                continue;
            SpellInfo const* info = sSpellMgr->GetSpellInfo(entry.first);
            if (!info || info->IsPassive())
                continue;
            handler->PSendSysMessage("known id=%u name=%s level=%u", entry.first, info->SpellName, info->SpellLevel);
            if (++printed == 30)
                break;
        }
        handler->PSendSysMessage("active spells shown=%u (max 30)", printed);
        // Same AI lookup and feasibility path as normal casts; never execute a cast.
        for (char const* spell : {"smite", "flash heal", "heal", "lesser heal", "renew", "power word: shield"})
        {
            uint32 id = ai->GetAiObjectContext()->GetValue<uint32>("spell id", spell)->Get();
            SpellInfo const* info = sSpellMgr->GetSpellInfo(id);
            Unit* target = info && info->IsPositive() ? heal : current;
            bool possible = id && target && ai->CanCastSpell(id, target);
            handler->PSendSysMessage("probe %s id=%u target=%s canCast=%u distance=%u los=%u",
                spell, id, label(target).c_str(), uint32(possible),
                target ? uint32(bot->GetDistance(target)) : 0u,
                uint32(target && bot->IsWithinLOSInMap(target)));
        }
        return true;
    }

    static bool HandlePerfMonCommand(ChatHandler* handler, char const* args)
    {
        if (!strcmp(args, "reset"))
        {
            sPerformanceMonitor->Reset();
            return true;
        }

        if (!strcmp(args, "tick"))
        {
            sPerformanceMonitor->PrintStats(true, false);
            return true;
        }

        if (!strcmp(args, "stack"))
        {
            sPerformanceMonitor->PrintStats(false, true);
            return true;
        }

        if (!strcmp(args, "toggle"))
        {
            sPlayerbotAIConfig->perfMonEnabled = !sPlayerbotAIConfig->perfMonEnabled;
            if (sPlayerbotAIConfig->perfMonEnabled)
                TC_LOG_INFO("playerbots", "Performance monitor enabled");
            else
                TC_LOG_INFO("playerbots", "Performance monitor disabled");
            return true;
        }

        sPerformanceMonitor->PrintStats();
        return true;
    }
};

void AddSC_playerbots_commandscript() { new playerbots_commandscript(); }
