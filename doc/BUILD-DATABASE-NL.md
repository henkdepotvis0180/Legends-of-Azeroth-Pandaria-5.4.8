# MoP: build en database-installatie

Dit document beschrijft de Linux-buildcontrole en databasevoorbereiding. Het is
geen Windows-repack en bevat geen WoW-clientdata. Bots gebruiken bestaande
beslisregels; er is geen taalmodel toegevoegd.

## Build reproduceren

Op Ubuntu 24.04 zijn onder meer nodig:

```
sudo apt-get install g++ cmake make libboost-filesystem-dev \
  libboost-program-options-dev libboost-iostreams-dev libboost-regex-dev \
  libboost-locale-dev libmysqlclient-dev libssl-dev libreadline-dev \
  libbz2-dev zlib1g-dev
bash contrib/build-linux-playerbots.sh
```

Het script configureert Release met `PLAYERBOTS=ON`, `ELUNA=OFF`,
`USE_MODULES=ON` en `TOOLS=ON`, bouwt en installeert de core en vraagt de
versies van beide serverprogramma's op. Standaard worden twee compileerprocessen
gebruikt. Met `MOP_BUILD_JOBS`, `MOP_BUILD_DIR`, `MOP_INSTALL_DIR` en `CMAKE`
zijn de instellingen te wijzigen; aanvullende argumenten worden aan CMake gegeven.
De module gebruikt bij `USE_COREPCH=ON` nu daadwerkelijk zijn vooraf
gecompileerde header, net als de rest van de core.

De controleomgeving gebruikt GCC 13.3, CMake 3.31.6, Boost 1.83.0,
OpenSSL 3.0.13 en MySQL-client 8.0.46. De precieze builduitkomst wordt in het
bijbehorende [sessieverslag](validation/BUILD-STARTUP-2026-10-17-NL.md)
vastgelegd. De volledige Linux-build, installatie en beide versiecontroles
slaagden. In de geïsoleerde controleomgeving was expliciet
`-DREADLINE_LIBRARY=/pad/naar/libreadline.so` nodig: de eerder gekozen statische
`libreadline.a` gaf onopgeloste terminalsymbolen bij het linken.
De CMake-code accepteert op Linux
Boost vanaf 1.71; de hogere versies in README/AGENTS zijn geen weerspiegeling
van die daadwerkelijke minimumcontrole.

## De juiste world-basis

Gebruik de officiële upstream-release:

https://github.com/Legends-of-Azeroth/Legends-of-Azeroth-Pandaria-5.4.8/releases/tag/WDB20231230

De releasetag heet `WDB20231230`, maar de database heet
`world_548_20240722.7z`. Na uitpakken is de naam
`world_548_20240722.sql`, precies de naam in `revision.h.in.cmake`.

SHA-256 van het gecontroleerde archief:

```
b14a1ebe7415f3135e771862af94139e7944406a636b9d107d2ab05e15905780
```

SHA-256 van de uitgepakte SQL:

```
aa8a76b1c05a660f1609273812aac7a5610cc6e60d34be50adc4bb879f58b9e7
```

Deze hashes leggen het gebruikte bestand vast; upstream publiceert bij deze
asset zelf geen digest. De oude tekst in de `version`-tabel is geen betrouwbare
maat voor de inhoudsdatum. Het installatiescript registreert de concrete imports
en hashes in een JSON-verslag.

## Nieuwe databases maken

Maak een eigen, privé MySQL-optiebestand met de accountgegevens voor installatie:

```ini
[client]
user=JOUW_INSTALLATIEGEBRUIKER
password=JOUW_WACHTWOORD
```

Bewaar dit bestand buiten Git. Geef de installatiegebruiker de benodigde rechten
voor de nieuwe databases. Gebruik voor de server vervolgens een aparte database-
gebruiker met rechten op alleen de vier bedoelde databases.

```
python3 contrib/setup_mop_databases.py \
  --world-sql /pad/naar/world_548_20240722.sql \
  --defaults-extra-file /prive/mysql-install.cnf \
  --user JOUW_INSTALLATIEGEBRUIKER \
  --prefix mop --report /prive/mop-database-installatie.json
```

Het script maakt `mop_auth`, `mop_characters`, `mop_world` en `mop_playerbots`.
Als een van deze namen al bestaat, stopt het vóór enige databasewijziging. Het
script verwijdert geen databases. Een afgebroken import blijft staan voor
onderzoek; gebruik voor een nieuwe proef andere, lege namen.

De importvolgorde is:

1. Auth- en characters-basis, daarna de officiële world-dump.
2. Nog niet geregistreerde auth-, characters- en world-updates uit de huidige core.
3. De gecombineerde botdump, aangevuld met ontbrekende losse basistabellen.
4. Nog niet geregistreerde botupdates en correctie van module-updatepaden.
5. Botnamen/guildnamen/arenanamen naar characters en module-SQL naar world.

De auth-dump bevat een voorbeeldbeheerder en een extern realm-adres. Bij deze
nieuwe installatie verwijdert het script de meegeleverde account/toegangsrecords
en zet het realm-adres op `127.0.0.1` met clientbuild `18414`. Een eigen
spelersaccount moet later via de server worden aangemaakt.

Ook de characters-basis bevat voorbeeldpersonages met inventaris en andere
spelersgegevens. Het script leegt de gegevens van deze nieuwe characters-schema,
met behoud van `updates`, `updates_include`, `reserved_name` en `warden_action`.
Dit gebeurt vóór het importeren van botnamen. De oude planningsgebeurtenissen in
`playerbots_random_bots` worden eveneens geleegd; statische botgegevens blijven
behouden. Het verslag telt accounts, personages, inventaris en botgebeurtenissen
apart, zodat zichtbaar is dat de installatie schoon begint.
De afzonderlijke hercontrole van deze schoonmaak op 18 oktober staat in
`validation/database-cleanup-2026-10-18.json`.

Voer de import niet nogmaals handmatig over een bestaande installatie uit:
meerdere upstream-basisscripts bevatten `DROP TABLE`. Het installatiescript
beschermt daartegen door bestaande schemas te weigeren.

## Configuratie

Gebruik de volledige meegeleverde `.conf.dist`-bestanden als basis. Pas onder
meer de volgende waarden in `worldserver.conf` aan:

```ini
LoginDatabaseInfo = "127.0.0.1;3306;mop;CHANGE_ME;mop_auth"
CharacterDatabaseInfo = "127.0.0.1;3306;mop;CHANGE_ME;mop_characters"
WorldDatabaseInfo = "127.0.0.1;3306;mop;CHANGE_ME;mop_world"
PlayerbotsDatabaseInfo = "127.0.0.1;3306;mop;CHANGE_ME;mop_playerbots"
PlayerbotsDatabase.WorkerThreads = 1
PlayerbotsDatabase.SynchThreads = 1
Logger.playerbots = 3,Console Server
BindIP = "127.0.0.1"
Updates.EnableDatabases = 0
Updates.AutoSetup = 0
```

Stel in `authserver.conf` dezelfde login-databaseverbinding in. De importtool
heeft de updates al toegepast; zet de automatische updater niet zomaar aan.
De upstream-autopopulatie voor een lege botdatabase verwijst nog naar de
world-dump, en is geen vervanging voor bovenstaande importprocedure.

De botmodule zoekt `playerbots.conf` relatief aan de werkdirectory. Kopieer het
volledige sjabloon daarheen en start de server steeds vanuit die directory.
Het sjabloon wordt nu ook bij `cmake --install` meegeleverd.

Voor een eerste kleine test kunnen deze waarden worden gebruikt:

```ini
AiPlayerbot.Enabled = 1
AiPlayerbot.RandomBotAutologin = 0
AiPlayerbot.MinRandomBots = 0
AiPlayerbot.MaxRandomBots = 4
AiPlayerbot.RandomBotAccountCount = 5
AiPlayerbot.AddClassAccountPoolSize = 2
```

Dit beperkt de bedoelde testomvang en schakelt automatisch inloggen van random
bots uit. Het is nog geen ingame-gevalideerd groepsprofiel. Clientdata, waaronder
enUS DBC en passende maps/vmaps/mmaps, zijn nodig voordat botgedrag kan worden
getest. Monk mist in deze basis nog een eigen klassecontext.

## Databasecontrole herhalen

De schone installatieproef op 17 oktober 2026 importeerde 68 SQL-bestanden en
sloeg twee al geregistreerde characters-updates over. Resultaat:

| Database | Tabellen |
| --- | ---: |
| Auth | 45 |
| Characters | 132 |
| World | 237 |
| Playerbots | 31 |

De world-database bevatte 57.517 creature-templates en 18.028 quests; characters
bevatte 100.000 botnamen. Er bleven nul meegeleverde accounts/toegangsrecords over.
De aansluitende proef met de opgeschoonde import had ook nul personages,
inventarisregels en oude botgebeurtenissen. De loginserver bleef tijdens de
startproef draaien en registreerde de realm op localhost. Een tweede import naar
dezelfde schemas werd vóór wijzigingen geweigerd.

Alle 744 gecontroleerde SQL-statements konden worden voorbereid: 96 auth,
565 characters, 73 world en 10 playerbots. De JSON-verslagen staan in
`doc/validation/`. Dit bewijst geen volledige bot- of contentwerking.

```
python3 contrib/tests/check_database_statements.py \
  --defaults-extra-file /prive/mysql-install.cnf \
  --user JOUW_INSTALLATIEGEBRUIKER \
  --prefix mop --report /prive/mop-sql-controle.json
```

Deze controle laat MySQL de letterlijke `PrepareStatement`-SQL uit de core
voorbereiden, zonder die statements uit te voeren. Hij controleert schema en
syntaxis. C++-voorwaarden worden niet geëvalueerd en dynamische botqueries vallen
buiten deze controle. De native worldserver bereikte de realm-, databaseversie-
en permissie-initialisatie, maar meldde daarna ontbrekende maps/vmaps. De
startproef is na 25 seconden afgebroken en geldt niet als geslaagde volledige
worldstart. De individuele databasepoolmeldingen waren door de gebruikte
loginstellingen niet zichtbaar. Ingame-validatie blijft nodig.

Op 18 oktober is de enUS-clientdata daadwerkelijk verkregen en zijn DBC, DB2,
maps en vmaps uitgepakt. Zie [CLIENTDATA-NL.md](CLIENTDATA-NL.md) voor de
gecontroleerde bron, extractieresultaten, waarschuwingen en resterende mmap- en
runtime-controles. De startproef van 17 oktober is daarmee nog niet herhaald.

Actuele herstelstatus en historische native proef: [RUNTIME-CONTROLE-NL.md](RUNTIME-CONTROLE-NL.md).
