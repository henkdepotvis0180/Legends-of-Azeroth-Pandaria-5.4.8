# Linux-runtimecontrole en herstelstatus — 18 oktober 2026

De eerdere werksessie heeft de volledige looproutegeneratie en een geslaagde
Linux-start met playerbots bereikt. Bij hervatten na de gebruikslimiet bleek de
tijdelijke werkomgeving opgeruimd. De gegenereerde serverdata, binaries en ruwe
runtime-logs waren nog niet duurzaam opgeslagen. Er is dus momenteel **geen
herstelpakket en geen beschikbare complete repack**. Die bestanden moeten opnieuw
worden opgebouwd. Het GitHub-controlepunt en de herstelde broncode blijven behouden.

## Eerder waargenomen resultaten

Onderstaande resultaten komen uit de tooluitvoer in het gesprek van vóór de
opruiming; ze zijn in deze hervatte omgeving niet opnieuw integraal uitgevoerd.
`validation/runtime-recovered-observations-2026-10-18.json` maakt dat onderscheid
expliciet. De oudere database- en bronwaarschuwingenverslagen stonden al op GitHub.

| Controle | Eerdere uitkomst |
| --- | --- |
| Volledige Release-build met scripts, bots, modules en tools; Eluna uit | Build, installatie en beide versiecontroles exit 0 |
| Native tabellen laden | 174 DBC + 26 DB2 |
| Verse vier databases | 68 imports; twee geregistreerde updates overgeslagen |
| Voorbereide letterlijke SQL-statements | Alle 744 geslaagd |
| Aanvullende camera-extractie | 27 M2-bestanden |
| Volledige mmap-generatie | Exit 0; 219 parameterbestanden en 6.745 tiles |
| Controle van alle gemaakte tiles via native Detour | 6.745 geladen/ontladen, nul fouten |
| Botinitialisatie | Twee accounts en 22 personages; elf klassen |
| Definitieve native start | Wereld gereed na 18,30 seconden |
| Sockets | Auth/world bereikbaar; world gaf 49 begroetingsbytes |
| Duurproef | Beide processen na 60,02 seconden actief |
| Gecontroleerd afsluiten | Beide processen exit 0 |

Automatisch inloggen van bots stond uit. Clientlogin, combat, quests, partijen en
dungeons zijn niet ingame getest. Er is geen taalmodel aangesloten; de bestaande
bots gebruiken geprogrammeerde strategieën.

## Herstelde reparaties

1. De DB2-extractor schreef de eerste taal direct in `dbc/`, terwijl de loader
   ook die taal in `dbc/enUS/` verwacht. `ExtractDB2Files` schrijft nu iedere taal
   naar zijn eigen map en maakt die aan. Eerder leverde echte herextractie 58
   bytegelijke DB2-bestanden op en laadde de server daarna de vereiste 26 tabellen.
2. Bots lazen een tweede, nooit geladen CharSections-store. Lege uiterlijklijsten
   veroorzaakten delen door nul. Core en bots gebruiken nu dezelfde geladen
   `sChrSectionStore`; ontbrekende uiterlijkgegevens worden expliciet geweigerd.
   De test compileert het echte selectiefragment met een fixture die de store uit
   de productie-loader vult. Negen cases slagen; de oude bron reproduceert SIGFPE.
3. `PrepareAddclassCache` stuurde letterlijk `%u` naar MySQL, terwijl PQuery `{}`
   verwacht. SQL-fout 1064 leidde tot abort en vervolgens een fout in de aborthandler.
   De query gebruikt nu de juiste formatter. Daarna slaagde de native start.

De reparaties zijn uit de eerdere werkuitvoer hersteld op controlepunt c9107ed.
In de hervatte omgeving zijn de negen uiterlijkcases en 34 rollen opnieuw getest.
Een nieuwe volledige build en native hercontrole vereisen nieuwe build/data-output.

## Meldingen en beperkingen

De 110 extractor-meldingen betreffen 92 unieke bronnen: 49 transport-WDTs,
19 overige WDTs, vier lege/onleesbare ADT-objectlagen en twintig modellen/WMO's.
Geen van die twintig modellen heeft een vaste gameobject-spawn in de onderzochte
world-database; script- of terreingebruik is daarmee niet uitgesloten. Er zijn
geen bronbestanden nagemaakt of databaseverwijzingen verwijderd om meldingen te
verbergen. Details: `validation/client-source-warnings-2026-10-18.json`.

Een extra native mmap-diagnose registreerde 191 geslaagde tile-loads en 21
waarschuwingen. Vier betroffen een reeds geladen tile (de loader geeft daarvoor
false terug); zeventien betroffen coördinaten zonder geproduceerde navigatietile,
waarvan acht ook zonder bron-.map. De andere negen hadden wel een bron-.map maar
leverden geen navigatietile op. Dit blijft een beperking van dekking. Een complete
generatierun en geldige tiles bewijzen geen goede route op iedere plek.

De world-database meldt bovendien ontbrekende scripts en ongeldige inhoudelijke
verwijzingen. De geslaagde serverstart bewijst geen foutloze gameplay.

## Verdergaan zonder broncodewerk te verliezen

Gebruik de branch van PR #1 en de instructies in `BUILD-DATABASE-NL.md` en
`CLIENTDATA-NL.md`. Het downloadverslag bevat de 56 oorspronkelijke bestandsnamen,
groottes, manifestnaam en downloadbron. Download/extractie, build en mmap-generatie
moeten opnieuw gebeuren; de ruwe clientinvoer is niet meer beschikbaar. Werk op
een blijvende schijf en bewaar de serverdata en binaries voordat de omgeving
wordt afgesloten. Het verslag is geen vervanging voor die bestanden.

Gerichte tests:

```bash
python3 contrib/tests/test_playerbot_roles.py
python3 contrib/tests/test_playerbot_appearance.py
```

De native tilecontrole bouw je tegen dezelfde Detour-library:

```bash
c++ -std=c++20 -O2 -I src/common -I src/common/Collision/Maps \
  -I dep/recastnavigation/Detour/Include contrib/tests/check_mmap_tiles.cpp \
  /absoluut/pad/build/dep/recastnavigation/Detour/libDetour.a -o check_mmap_tiles
./check_mmap_tiles /absoluut/pad/data/mmaps
```
