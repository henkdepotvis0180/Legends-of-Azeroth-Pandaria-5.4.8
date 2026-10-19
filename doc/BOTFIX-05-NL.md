# Botfix 05: begin van natuurlijke botprogressie

Datum: 19 oktober 2026.

## Bevestigde lokale uitkomst update 4

De gebruiker meldt tien online wereldbots (negen level 1 en één Death Knight
level 55). Na netjes afsluiten/herstarten keren bots en ook zijn partybot terug.
Dit is een lokale functionele observatie; niet iedere XP-/gearwaarde is vergeleken.

## Vergelijking met de aangeleverde Wrath-module

Referentie: https://github.com/mod-playerbots/mod-playerbots
Bekeken master-commit: d750b4b3a50effdf22bedc8032f0e8e5f7cb8091.

- `src/Bot/RandomPlayerbotMgr.cpp`: onderscheid tussen vaste levels (XP-blokkade)
  en normaal doorlevelen (XP-blokkade verwijderen). Onze verwante code was
  uitgecommentarieerd; de configuratiesleutel alleen had dus geen effect.
- `src/Script/Playerbots.cpp`: bot-XP-multiplier via OnPlayerGiveXP. Voor onze
  eerste stap is geen multiplier nodig: MoP Player::GiveXP verzorgt normale XP,
  tenzij onder meer PLAYER_FLAGS_NO_XP_GAIN actief is. De Wrath-hook is geen
  rechtstreeks vervangbare MoP-interface.
- `src/Ai/Base/Actions/AcceptQuestAction.cpp`: quests via de normale corecontroles
  CanTakeQuest/CanAddQuest en AddQuest. Het bestaan van deze actie bewijst niet
  dat onze MoP-bots zelfstandig de juiste NPC's en questdoelen vinden.

Geen volledige Wrath-module of raid-/classdata geïmporteerd. Deze stap gebruikt
het principe van normale core-XP en past dat toe op de bestaande MoP-interfaces.

## Beperkte optionele groeimodus

Nieuwe instelling: `AiPlayerbot.RandomBotNaturalProgression = 1`.
Default is 0, zodat bestaande andere installaties hun gedrag behouden.

- Alleen automatische wereldbots op level 1 krijgen bij login een beginlevel
  binnen RandomBotStartingMinLevel/MaxLevel (4–10), begrensd door het coremaximum.
- Bots die al level 2 of hoger zijn, houden hun level; ook boven level 10 worden
  ze niet teruggezet. Bestaande XP, inventory en questlog worden niet gewist.
- De XP-blokkade wordt verwijderd en het personage wordt met SaveToDB opgeslagen.
- De twee randomizer-ingangen mogen wereldbots in deze modus niet meer door
  BotFactory::Randomize sturen: dat pad zet XP op nul en verwijdert gear.
- De automatische selectie en herstelselectie slaan Death Knights over. Het
  Death Knight-personage wordt niet verwijderd. Een vrijgevallen plaats kan door
  een andere beschikbare bot worden gevuld. Handmatig toegevoegde/partyherstel-
  bots blijven onder de bestaande partyregels vallen; geen gedwongen verwijdering.

De bestaande startzone-/factieafhandeling wordt behouden. De loginhook past de
modus na de bestaande logininitialisatie toe. GiveLevel gebruikt MoP's normale
levelinitialisatie. Deze stap genereert geen nieuwe gear en voegt geen eigen
questplanner of spelltrainer toe. Voor bots buiten de actieve wereldbotselectie
wordt de groeimodus niet toegepast.

## Lokale installatie

Stop beide servers netjes. Haal deze commit op en gebruik een nieuwe lokale
branch, aangezien de werkbranch voor de draft PR als één commit wordt bewaard.
Daarna is één opdracht voldoende:

```bash
bash contrib/apply-local-bot-update.sh
```

Dit draait beide gerichte tests, hergebruikt de bestaande bouwmap, installeert,
bewaart een back-up van playerbots.conf en activeert tien wereldbots met de
nieuwe groeimodus. Buildlog: `~/mop/bot-update05-build.log`. Bij een buildfout
wordt de configuratie niet aangepast. Start daarna via Start-MoP en log in.

Controleer een bestaande level-1 bot: nu 4–10; na opnieuw inloggen behoudt hij
zijn level. Een al gelevelde bot houdt zijn voortgang. Controleer XP vóór en na
een passende mobkill, en vervolgens opnieuw na netjes afsluiten/herstarten.
XP vereist de normale corevoorwaarden (o.a. levelverschil, rewardafstand en
killcredit). Het weghalen van één blokkade bewijst niet dat elk XP-probleem is
opgelost. Ook daadwerkelijk zelfstandig mobs vinden is een ingamecontrole.

## Uitgevoerde controles en open werk

De nieuwe C++20-regressietest compileert de complete productiemethoden voor
startprogressie, DK-selectie en de periodieke randomizer met gecontroleerde
interfaces. Getest: alle startlevels 4–10, opnieuw toepassen, behoud van
levels 2/3/15/50/90 en XP/gear/quests, XP-unlock, uitsluiten niet-wereldbots en
DK's, ontbrekende cache, lager coremaximum en behoud van de oude modus.
De login-, companion-grind-, 18 cast/bewegingsscenario's, 34 specrollen en
starterequipmenttests slagen opnieuw. Het lokale activatiescript is syntactisch
gecontroleerd; de confighelper is op een tijdelijke configuratie gecontroleerd.

Geen volledige MoP-corebuild, databasehersteltest of ingamecontrole van update 5
in deze werkomgeving. Deze blijven op de gebruikersmachine nodig. Geen claim
van werkend zelfstandig questen, lootupgrades, alle class-spells, tank/heal-AI
of 250 bots. Die onderdelen worden gericht overgezet/getest in volgende stappen.
Geen merge naar master en geen databases gewist of opnieuw geïmporteerd.
