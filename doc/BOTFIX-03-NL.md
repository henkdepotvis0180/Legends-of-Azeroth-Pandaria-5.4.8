# Botfix 03: geen zelfstandig grinden met een speler als leider

Datum: 19 oktober 2026.

## Lokale bevinding na botfix 01 en 02

De gebruiker heeft beide patches opnieuw gebouwd en geïnstalleerd; worldserver
en authserver geven hun versie terug. Na starten en toevoegen van een warrior
bevestigt de gebruiker dat de bot gear draagt. De bot valt echter ook vijanden
aan terwijl de speler niets doet. Cast-/healgedrag is nog niet ingame bevestigd.

## Beperkte wijziging

GrindTargetValue mag geen autonoom grinddoel meer kiezen zodra de bot een
echte speler als master heeft. AttackAnythingAction weigert dezelfde toestand
bij zowel isUseful als Execute. De tweede controle voorkomt dat een eerder
gecachet grinddoel alsnog wordt aangevallen na het aansluiten bij een speler.

Het zoeken naar aanvallers en de DPS-/tank-assistpaden zijn niet vervangen.
Deze patch schakelt dus niet alle combat-AI uit. Zelfstandige bots zonder
echte speler als master behouden het bestaande grindpad. Expliciete pull-/RTI-
opdrachten zijn in deze stap niet herwerkt. Ook daadwerkelijke aggro door een
naderend monster is niet hetzelfde als een bot die zelf een grinddoel kiest.

Dit corrigeert een aangetroffen ongewenst pad, maar de precieze trigger van de
geobserveerde aanval is niet met een ingame actietrace vastgelegd. Een lokale
hertest moet bevestigen of er nog een ander pad zelfstandig vijanden kiest.

## Controle

```bash
python3 contrib/tests/test_playerbot_companion_grind.py
python3 contrib/tests/test_playerbot_cast_movement.py
```

Beide slagen. De grindtest extraheert de drie complete gewijzigde
productiemethoden en compileert die met gecontroleerde serverinterfaces.
Getest: spelergeleide bot kiest geen grinddoel en voert geen grindaanval uit;
zelfstandige bot kan dat nog wel; het verkrijgen van een echte master blokkeert
ook een al gekozen aanval; bestaande activiteit-, beweging-, doelwit-, dummy-
en afstandscontroles blijven actief. De 18 cast/bewegingsscenario's slagen ook.
De waarschuwing voor een bestaande ongebruikte grindName-variabele wordt in
de test onderdrukt; de productiemethoden zelf zijn ongewijzigd geëxtraheerd.

Geen nieuwe volledige corebuild of ingame-test van botfix 03 uitgevoerd.
De gebruiker moet de bestaande bouwmap hergebruiken en opnieuw installeren.
Databases en configuratie veranderen niet. Test na herstart met een nieuwe
partybot: idle naast niet-aanvallende monsters; daarna zelf een monster
aanvallen; daarna echte zelfverdediging. Gear, juiste doelwitkeuze en bewegen
naar slagafstand worden apart beoordeeld.

XP, loot, blijvende gearupgrades, volledige tank-/healerwerking en autonoom
raiden blijven openstaande stappen. De eerdere volledige herstelkopie van de
werkende lokale installatie blijft behouden.
