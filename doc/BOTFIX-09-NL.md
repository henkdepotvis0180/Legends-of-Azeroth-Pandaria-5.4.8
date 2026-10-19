# Update 09: begrensde actie-trace via botdiag

Datum: 19 oktober 2026.

## Vastgestelde toestand

Clemeria level 4: master/leader Sam, realMaster=1, sameGroup=1. Tijdens Sams
gevecht: masterCombat=1, attackers=1, huidig/DPS-doel Goblin Assassin,
heal=Sam (96%). Smite 585 is bekend, canCast=1, LOS=1, afstand 5.
Priest zelf combat=0, AI state=0 (combat). Buiten gevecht bleef state=0 ook staan.
Dat is een aanwijzing, geen bewezen oorzaak van cast-/volgstagnatie.
De zes geprobeerde healnamen resolveerden naar id=0. Het spellboek bevat ook
interne/trigger-spellvarianten; de leerfilter van update 7 verdient nog reparatie.
Pmon leverde ondanks logniveau-/togglepogingen geen bruikbare tabel op.

## Nieuwe diagnose

In worldserverconsole (zonder punt):

```
botdiag Clemeria trace
```

Dit bevestigt expliciet dat de trace gestart is. Alleen de engines van deze bot
bewaren de volgende twintig DoNextAction-rondes per engine in geheugen. Geen
pmon, loggerinstelling, testMode of test.log nodig. De gewone scheduler, queues,
actieprioriteiten, spellcasts, party en master worden niet aangepast.

Laat Clemeria in de party terwijl Sam vecht; wacht circa vijf seconden en voer uit:

```
botdiag Clemeria
```

De trace verschijnt rechtstreeks via ChatHandler vóór de bestaande momentopname.
TRACE tick bevat minimal en queuelengte. A:... toont UNKNOWN, USELESS, IMPOSSIBLE,
PREREQ, FAILED of OK; multipliers en No actions executed worden ook bewaard.
CanCast=1 uit de momentopname blijft een mogelijkheidstoets, geen uitgevoerde cast.

Iedere engine heeft een eigen maximum van 6000 bytes. Oude complete regels
worden verwijderd; lange losse regels worden met vsnprintf begrensd. Na twintig
rondes stopt het opnemen en blijft de laatste uitvoer leesbaar tot herstart,
enginevervanging of opnieuw starten van de trace. Niet gebruikte engines
verbruiken hun teller pas wanneer ze draaien. Een nieuwe trace wist de oude.
De capture is standaard uit; andere bots blijven zonder capture. Per bot kan
maximaal ongeveer 18 KB aan trace-inhoud worden bewaard voor drie engines.

## Controle

- test_playerbot_action_trace.py compileert de complete productiemethode
  Engine::LogAction en de echte startfunctie met gecontroleerde interfaces.
  Opt-in/per-engine, opmaak, eventfilter, begrenzing, extreem lange regels,
  gestopte capture en opnieuw starten slagen. Geen test.log gemaakt.
  De bestaande ongebruikte lokale variabele in legacy testMode wordt alleen
  voor deze extractietest als waarschuwing onderdrukt.
- test_playerbot_diagnostics.py compileert de complete commandhandler; ongeldige
  bot/mens weigeren, trace starten zonder castprobes, uitlezen van actieregels,
  bestaande status/spellprobes en ontbrekende doelen slagen.
- bash -n van het lokale activatiescript slaagt.

De teller wordt aan het einde van de gewone DoNextAction-routine verlaagd; die
integratie is in broncode beoordeeld, niet met een volledige world getest.
Geen volledige corebuild of native/ingame-test in deze werkomgeving.
De build en twee consoleopdrachten volgen op de gebruikersmachine.
Geen reparatie van partycasten, volgen of interne spells geclaimd met update 09.
De bestaande voortgang/configback-ups blijven behouden; geen SQL-reset/-import.
Geen merge naar master.

## Lokale toepassing

Beide servers netjes stoppen, commit ophalen op een nieuwe lokale branch en:

```bash
bash contrib/apply-local-bot-update.sh
```

Het script voert de twee trace-/diagnosetests uit, plus de bestaande gerichte
controles, en hergebruikt de bouwmap. Buildlog: ~/mop/bot-update09-build.log.
Start via Start-MoP, voer de twee bovenstaande botdiag-opdrachten uit en bewaar
de uitvoer. Die laat zien op welk actieniveau de volgende reparatie nodig is.
