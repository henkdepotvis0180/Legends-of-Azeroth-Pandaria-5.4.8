# MoP-playerbots: eerste controle en ontwikkelstart

Controle: 17 oktober 2026. Basiscommit: `c24ad821c202d3abff532680060bae488b82a90d`.

Dit is het verslag van de eerste controle. Zie [BUILD-DATABASE-NL.md](BUILD-DATABASE-NL.md)
en `validation/` voor de daaropvolgende installatieprocedure en databasevalidatie.

## Wat deze basis al bevat

- Openbare MoP 5.4.8-core (client build 18414), met een ingebouwde
  `modules/mod_playerbots` en bijbehorende SQL/configuratie.
- De nieuwste basiscommit is van 11 oktober 2026. De core is dus niet uitsluitend
  oude, stilstaande broncode. Recente corewijzigingen bewijzen geen botkwaliteit.
- `strategy/Engine.cpp` kiest acties op basis van triggers, prioriteiten,
  voorwaarden en uitvoerbaarheid. Dit is spel-AI; geen getraind taalmodel.
- Klassecontexten voor de tien oorspronkelijke klassen. De Monk-context is
  uitgecommentarieerd in `Factory/AiFactory.cpp`; Monk valt terug op de generieke
  context. Rolherkenning voor Monk is geen bewijs van werkende Monk-combat-AI.
- Er bestaat al `avoid aoe`-strategielogica. De standaardselectie daarvan is
  afhankelijk van configuratie en een echte speler als master. Werkelijke
  dungeonmechanieken moeten per encounter worden gecontroleerd.

## Eerste wijzigingen

De functie `AiFactory::GetPlayerRoles` bevatte drie concrete classificatiefouten:

| Specialisatie | Voorheen | Na deze wijziging |
| --- | --- | --- |
| Restoration Shaman | DPS, door vergelijking met Druid-specialisatie | Healer |
| Retribution Paladin | Geen rol, door vergelijking met getal 2 | DPS |
| Blood Death Knight | DPS via standaardtak | Tank |

Belangrijk: bij deze controle zijn geen aanroepen van `GetPlayerRoles` buiten
de eigen declaratie en definitie gevonden. Deze reparatie maakt de helper
correct voor verdere integratie; hij verandert op zichzelf geen combatstrategie
en bewijst niet dat groepsvorming nu anders werkt. De bestaande selectie van
combatstrategieën gebruikt ook andere functies.

## Uitgevoerde controles

```
python3 contrib/tests/test_playerbot_roles.py
git diff --check
```

De regressietest compileert de echte functiedefinitie en de echte enums uit de
bronbestanden met C++20. Alleen de twee gebruikte Player-methoden worden vervangen
door een kleine testinterface. Alle 34 speelbare MoP-specialisaties worden op hun
verwachte rol gecontroleerd. De ongewijzigde basis faalt precies op bovenstaande
drie gevallen; de gewijzigde functie slaagt voor alle 34.

Dit is een geïsoleerde classificatietest, geen volledige corebuild of ingame-test.
De test vereist Python 3 en een compiler die GNU/Clang-opties accepteert. Met `CXX`
kan een andere geschikte compiler worden gekozen.

## Buildcontrole en openstaande benodigdheden

De configuratie is geprobeerd met GCC 13.3 en CMake 3.31.6:

```
cmake -S . -B ../mop-build -DPLAYERBOTS=ON -DELUNA=OFF -DTOOLS=ON
```

De configuratie stopt bij ontbrekende Boost-headers en de libraries `filesystem`,
`program_options`, `iostreams`, `regex` en `locale`. Er is dus nog geen volledige
compile uitgevoerd en er zijn geen geteste serverbinaries of speelbare repack.
De MySQL-clientbinary werd evenmin gevonden; verdere dependencies moeten na het
oplossen van Boost opnieuw worden gecontroleerd.

De repository heeft Windows- en Linux-buildworkflows. De Windows-workflow zet
Eluna aan, terwijl de README gebruik met bots afraadt. Gebruik voor de eerste
botbuild expliciet `PLAYERBOTS=ON` en `ELUNA=OFF`. Bestaande workflows zijn in deze
wijziging niet aangepast. In deze fork waren bij controle nog geen Actions-runs.

Voor een speelbare installatie moeten ook beschikbaar en gecontroleerd zijn:

- Een passende volledige world-database. `sql/base` bevat hier `auth.sql` en
  `characters.sql`, maar geen `world.sql`; oude updates zijn geen volledige basis.
- De playerbots-database en de overige module-SQL, met gecontroleerde importvolgorde.
- Clientdata voor build 18414: enUS DBC voor bots en passende maps/vmaps/mmaps.
- MySQL-configuratie en vier databaseverbindingen, inclusief `mop_playerbots`.
- `playerbots.conf` op de door de module gebruikte locatie. De module zoekt die
  momenteel relatief aan de werkdirectory; ontbrekende configuratie stopt de server.

Clientdata, wachtwoorden en databaseback-ups horen niet in de broncode-repository.

## Volgende ontwikkelstap

1. Volledige build reproduceerbaar uitvoeren met bots aan en Eluna uit.
2. Database en clientdata aansluiten; startup en login controleren.
3. Met een kleine testgroep beginnen: Protection Warrior, Holy Priest en twee
   ondersteunde DPS-klassen. De speler vult de vijfde plek; Monk voorlopig overslaan.
4. Ingame controleren: volgen, aanvallen, tankdreiging, healen, doodgaan/herleven,
   loot en instance-overgangen. Resultaten en fouten vastleggen.
5. Pas daarna interruptcoördinatie, gevaarherkenning en specifieke bosses verbeteren.
6. Een eventuele taalmodelkoppeling voor gesprekken/opdrachten apart toevoegen.

Doel is eerst een aantoonbaar werkende groep. Zelflerend raidgedrag en volledige
MoP-dekking zijn nog niet geïmplementeerd of aangetoond.
