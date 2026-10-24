# Botfix 07: spellleren onafhankelijk van de onvolledige SQL-tabel

Datum: 19 oktober 2026.

## Vastgestelde lokale oorzaak

Gebruiker draait update 6. Priest Clemeria, level 4, gebruikt geen damage/heals,
maar neemt wel afstand. Volgen herstelt pas na party verlaten/opnieuw aansluiten.
SQL toont geen character_spell-records voor Clemeria. player_class_spells bevat
slechts class 2: 6 records, class 6: 13 records, class 9: 2 records; priest en de
andere classes ontbreken. Dat verklaart waarom update 6 de priest niet aanvult.
Die update vertrouwde ten onrechte op een volledige class-spellijst. De tests
hadden een gevulde nepbron en detecteerden deze ontbrekende afhankelijkheid niet.
Geen opgeslagen spells bewijst op zichzelf niet dat het runtime-spellboek leeg is.

## Reparatie

BotFactory::LearnClassSpells haalt kandidaten nu uit de al geladen MoP
SkillLineAbility.dbc, zoals de bestaande core-commandocode in
src/server/scripts/Commands/cs_learn.cpp voor class-spells. De tabel
player_class_spells en ServiceMgr zijn geen afhankelijkheid meer.

ClassMask en RaceMask worden gecontroleerd indien gezet. De bestaande filters
blijven: juiste SpellFamilyName, passend ras/class via core, bestaand/geldig
spellrecord, positief SpellLevel niet hoger dan botlevel, geen bekend spell,
geen talent, geen exclusieve spell van een andere spec en geen spec-unlock vóór
level 10. De huidige botlogin-/level-uphooks van update 6 blijven actief.
Geen wijziging aan menselijke spellboeken, XP, gear of quests. Geen Wrath-IDs
of databasevulling geïmporteerd en geen botpersonages verwijderd.

## Controle

De bestaande productiemethode-test is aangepast: er bestaat nu helemaal geen
ServiceMgr-/SQL-bron in de testinterfaces. DBC-kandidaten voorzien alle elf
classpaden; gecontroleerd zijn ook class-/rasmaskers, levelgrenzen, geen dubbele
learn, spellfamily, talent-/specfilters, ontbrekende/ongeldige data en behoud
van XP/gear. Test slaagt met C++20, -Wall -Wextra -Werror.
Het activatiescript slaagt met bash -n.

Dit zijn gecontroleerde interfaces, geen volledige corebuild of echte
DBC-dataset/ingame-test. Die controles volgen op de gebruikersmachine. De eerdere
claim dat update 6 spellleren compleet maakte was niet onderbouwd door de lokale
database-inhoud; update 7 herstelt precies die afhankelijkheid. Niet claimen dat
hiermee alle spells/rotaties of het party-volgprobleem zijn gerepareerd.

## Lokale toepassing

Na ophalen van deze commit in een nieuwe lokale branch, beide servers gestopt:

```bash
bash contrib/apply-local-bot-update.sh
```

De bestaande buildmap wordt hergebruikt. Het script voert de gerichte controles
uit, bouwt/installeert en bewaart de configuratieback-up. Dezelfde tien bots en
progressieconfiguratie blijven actief. Buildlog: ~/mop/bot-update07-build.log.
Geen SQL-import of characterreset nodig. Start via Start-MoP en log in.

Controleer daarna opnieuw Clemeria's character_spell-records en test afzonderlijk
Smite/damage en healen op een gewonde partygenoot. Als records verschijnen maar
casts uitblijven, volgt de runtime-spell-/actietrace. Het volgen dat alleen na
partyhergroeperen hervat, blijft een aparte nog niet gerepareerde fout.
Geen merge naar master.
