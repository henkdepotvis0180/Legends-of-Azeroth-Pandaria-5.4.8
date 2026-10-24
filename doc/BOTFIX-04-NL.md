# Botfix 04: wereldbots na het inloggen van een echte speler

Datum: 19 oktober 2026.

## Gedrag

De automatische random-botplanner begint pas wanneer een echte spelersessie
met een personage in de wereld aanwezig is. Botsessies, het personagekeuzescherm,
nog niet ingeladen personages en uitloggende sessies tellen niet mee. Een echte
GM-speler telt wel mee. Bij een echte login wordt de wachttijd van de planner
ververst; zonder echte speler controleert de planner iedere seconde opnieuw.

De bestaande geleidelijke loginregeling blijft verantwoordelijk voor de bots.
Als de laatste echte speler vertrekt, worden geen nieuwe plannerbatches gestart.
Een al ingezette asynchrone login kan nog afronden. Deze wijziging logt reeds
online wereldbots niet gedwongen uit. De bestaande bot-/groepsregels kunnen
bots nog wel laten uitloggen. Handmatig toegevoegde partybots worden hiermee
niet automatisch permanent aan een spelersaccount gekoppeld.

Nieuwe instelling: `AiPlayerbot.RandomBotLoginOnlyWithPlayers = 1` (ook de
default bij ontbreken). Hiervoor moeten `AiPlayerbot.Enabled` en
`AiPlayerbot.RandomBotAutologin` beide aanstaan. De nieuwe instelling op 0
herstelt de bestaande automatische login zonder aanwezige echte speler.

## Kleine lokale activatie

Stop worldserver netjes met `server shutdown 0` en authserver met Ctrl+C.
Gebruik de bijgewerkte broncode in Ubuntu en bouw opnieuw met de bestaande
bouwmap. De installatie vervangt bestaande `.conf`-bestanden niet.

```bash
python3 contrib/tests/test_playerbot_login_gate.py
MOP_BUILD_JOBS=6 MOP_BUILD_DIR="$HOME/mop/build" MOP_INSTALL_DIR="$HOME/mop/server" \
  bash contrib/build-linux-playerbots.sh -DSCRIPTS=ON
python3 contrib/configure-local-bot-population.py --count 10
```

Het configuratiescript maakt een gedateerde back-up naast `playerbots.conf`.
Het zet Enabled, RandomBotAutologin en RandomBotLoginOnlyWithPlayers op 1,
MinRandomBots en MaxRandomBots op 10 en RandomBotsPerInterval op 5. Andere
instellingen, databases, accounts en bestaande personages blijven behouden.
Het aantal beschikbare botaccounts/personages kan de werkelijke populatie
beperken. De doelpopulatie is geen garantie dat alle bots meteen online zijn.

Start via de bestaande Windows-snelkoppeling. Controleer na een verse start:
zonder ingelogd spelerspersonage begint de automatische populatie niet; na
het ingaan van de wereld volgen de bots geleidelijk. Wereldbots verschijnen
niet noodzakelijk in de buurt van je personage en vormen niet automatisch
een party. Bestaande consoleopdracht `server info` toont het aantal online
spelers; dit totaal omvat ook bots. Controleer voor individuele namen zo nodig
de bestaande database-/serverlogging.

## Uitgevoerde controle en grenzen

`contrib/tests/test_playerbot_login_gate.py` extraheert de twee complete
productiemethoden en compileert die met gecontroleerde sessie-interfaces.
Lege/nullsessies, alleen bots, character selection, world entry, world exit,
uitloggen, een echte speler naast bots en alle configuratiepoorten slagen.
De bestaande companion-grindtest, 18 cast/bewegingsscenario's, 34 specrollen
en equipment-policytest slagen opnieuw.

Geen volledige corebuild of ingame-test van update 4 in deze werkomgeving.
Die controle volgt op de gebruikersmachine. XP, permanente partyherstelregels,
startlevels 1–50, natuurlijk doorlevelen en de uitbreiding naar 250 bots zijn
hiermee nog niet afgerond. De bestaande volledige serverback-up blijft het
herstelpunt van vóór deze botwijzigingen. Geen merge naar master.
