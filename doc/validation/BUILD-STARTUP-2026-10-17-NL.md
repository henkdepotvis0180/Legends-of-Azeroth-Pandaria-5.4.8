# Build- en startcontrole: sessieverslag

Uitgevoerd op 17 oktober 2026; vastgelegd bij hervatting op 18 oktober 2026.
Dit verslag reconstrueert de waargenomen uitkomsten uit de vorige werksessie.
De tijdelijke binaries, ruwe logs en testdatabases zijn bij hervatting niet meer
beschikbaar. De JSON-bestanden in deze map zijn de eerder opgeslagen
databaseverslagen; ze zijn niet achteraf aangepast aan de laatste schoonmaakproef.

## Linux-build

De volledige Release-build en installatie via
`contrib/build-linux-playerbots.sh` eindigden met exitcode 0. Gebouwd met GCC
13.3, CMake 3.31.6, Boost 1.83, OpenSSL 3.0.13 en MySQL-client 8.0.46.
`PLAYERBOTS`, `USE_MODULES`, `SCRIPTS`, `TOOLS`, `USE_COREPCH` en `USE_SCRIPTPCH`
stonden aan; `ELUNA` stond uit. De modules gebruikten de PCH-aanpassing uit deze PR.

De core, playerbots-module, alle scripts, authserver, worldserver en
extractietools werden gebouwd. Beide geïnstalleerde servers gaven met
`--version` exitcode 0. `nm` bevestigde registratie van `AddSC_mod_playerbots`;
het geïnstalleerde `playerbots.conf.dist` was aanwezig.

Een eerste linkpoging met de statische readline-bibliotheek mislukte op
terminalsymbolen. De geslaagde poging wees expliciet de gedeelde
`libreadline.so` aan via `READLINE_LIBRARY`. Dit is een configuratievereiste
van de geïsoleerde dependency-map, geen bewezen vereiste op elke Linux-installatie.

De banner meldde `rev. Archive`: de upstream-versiegenerator gebruikt
Mercurial-metadata. Deze tekst is geen betrouwbare identificatie van de Git-commit.

## Databases en starten

De volledige verse import is met MySQL 8.0.46 uitgevoerd. De opgeslagen
database-installatieproef omvat 68 imports, vier schemas en twee overgeslagen,
al geregistreerde characters-updates. Alle 744 gecontroleerde letterlijke
SQL-statements konden worden voorbereid. Een herhaalde installatie naar bestaande
schemas werd vóór wijzigingen geweigerd.

De laatste schoonmaakproef gebruikte `mopclean_*` en behield de aantallen
tabellen en statische inhoud uit het opgeslagen installatieverslag: 45/132/237/31
tabellen, 57.517 creature-templates, 18.028 quests en 100.000 botnamen.
Accounts, personages, inventarisregels en oude botgebeurtenissen waren alle nul;
het realm-adres was `127.0.0.1`. Het ruwe JSON-verslag van deze aanvullende proef
is niet behouden.

Op 18 oktober is de schoonmaak opnieuw afzonderlijk uitgevoerd met de echte
characters-basis en gecombineerde botdump. Het verslag
`database-cleanup-2026-10-18.json` bevestigt 5 → 0 personages, 33 → 0
inventarisregels en 2.001 → 0 botgebeurtenissen. Alle geleegde characters-tabellen
waren leeg; updateadministratie en statische botteksten bleven behouden. Na de
module-import waren opnieuw 100.000 botnamen aanwezig. Dit was geen nieuwe
volledige world-import of native serverstart.

De native authserver bleef gedurende de controle van acht seconden draaien en
registreerde de realm. De native worldserver bereikte realm-ID 1, de world-
databaseversie en permissies. Daarna meldde hij ontbrekende map/vmap-data,
waaronder `maps/0000_43_31.map`. De proef is na 25 seconden beëindigd.
De poolmeldingen waren onderdrukt door de logconfiguratie; het testscript kon ze
daarom niet bevestigen en rapporteerde geen geslaagde volledige worldstart.

## Grenzen van de controle

Dit bevestigt de Linux-compilatie en de genoemde databasecontroles. Een
volledig draaiende worldserver, clientlogin, combat-, dungeon- en raidgedrag zijn
niet aangetoond. Daarvoor ontbreken passende clientdata, waaronder enUS DBC en
maps/vmaps/mmaps. Er is geen Windows-build of repack gevalideerd en geen
taalmodel of zelflerend gedrag toegevoegd.
