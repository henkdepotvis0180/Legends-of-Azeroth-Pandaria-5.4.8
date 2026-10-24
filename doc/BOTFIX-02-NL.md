# Botfix 02: stoppen voor een gekozen cast

Datum: 19 oktober 2026. Volgt op BOTFIX-01-NL.md. Eén beperkte correctie in
het gedeelde pad voor unit-target-spreuken; geen volledige klasserework.

## Probleem en gedrag

CanCastSpell wees spreuken met casttijd, channels en autorepeat onmiddellijk
af wanneer de bot bewoog. Daardoor kon een CastSpellAction niet geselecteerd
worden om die beweging voor het casten te stoppen. CheckCast behandelt bewegen
al als een voorbereibare toestand, naast bijvoorbeeld draaien en opstaan.

De vroege algemene bewegingsafwijzing is verwijderd. De bestaande controles op
aangeleerde spreuk, cooldown en core-CheckCast blijven behouden. Alleen de
daadwerkelijk gekozen CastSpellAction mag vervolgens de beweging voorbereiden:

- Een ontbrekende of niet aangeleerde spreuk wordt afgewezen, zonder beweging
  te veranderen. Er worden geen hogere-levelvaardigheden aangeleerd of afgedwongen.
- Een petcast stopt de eigenaar niet.
- Een instantcast of een door cast-while-walking toegestane cast onderbreekt de
  beweging niet. De normale corechecks beslissen of casten werkelijk toegestaan is.
- Voor een casttijd/channel/autorepeat stopt een lopende bot pas als het echte
  doelwit in dezelfde map, in wereld, binnen het bereik van de gekozen spreuk
  en binnen zichtlijn is. De bestaande benaderingsacties blijven nodig.
- Lopende generic/channel-casts worden niet door de nieuwe stopactie onderbroken.
- Follow/chase wordt gewist en beweging gestopt voordat de normale castaanroep
  plaatsvindt. De normale casttijd, mana- en cooldownregels blijven van toepassing.

Omdat healacties dit CastSpellAction-pad erven, gebruikt de controle daar het
vriendelijke healdoel en het positieve spreukbereik. Andere overridepaden,
zoals expliciete crowd control, voertuig-, gameobject- en positiecasts, zijn
in deze patch niet herwerkt. Nadering met een afwijkend kort spreukbereik,
minimumbereik, terrein en ontbrekende mmaps vraagt nog afzonderlijke tests.

## Uitgevoerde controles

```bash
python3 contrib/tests/test_playerbot_cast_movement.py
python3 contrib/tests/test_playerbot_roles.py
g++ -std=c++20 -Wall -Wextra -Werror \
  -I modules/mod_playerbots/src/Manager \
  contrib/tests/test_playerbot_equipment_policy.cpp -o /tmp/test-mop-equipment
/tmp/test-mop-equipment
```

Resultaat: 18 cast/bewegingsscenario's slagen. De test extraheert de complete
productiemethode PrepareSpellMovement ongewijzigd, compileert die met C++20 en
vervangt uitsluitend de serverinterfaces door controleerbare testinterfaces.
Getest: niet geleerd, ontbrekende spellinfo, stationary, instant, bewegingsaura,
bereikgrens, buiten bereik, zichtlijn, andere map, uit wereld, vriendelijk
healdoel met ander bereik, bestaande cast/channel, channel/autorepeat, self en pet.
De bestaande 34 specialisatierollen en equipment-policytest blijven slagen.

Dit controleert beslissingen en bewegingsaanroepen, niet de echte core-ABI,
spelluitvoering, navigatie of netwerkgedrag. Deze wijziging is nog niet als
volledige core gebouwd en nog niet op de gebruikers-pc ingame getest.

## Lokale hertest na herbouw

Eerst de servers netjes stoppen en dezelfde buildmap/installatiemap gebruiken.
De gegevens en configuratie blijven behouden. Test in een klein groepje een
mage en een priest, met aangeleerde levelpassende spreuken: na volgen stoppen
voor casten/healen binnen bereik, niet stoppen voor een onbekende spreuk,
en niet onderbreken van de begonnen cast door follow/chase.
De warrior- en startersgearcorrecties van botfix 01 blijven onderdeel van de branch.

## Volgende kleine stappen

1. Benadering en spellselectie per klassestrategie controleren, inclusief
   ontbrekende startspreuken/alternatieven en beschikbare skills per level.
2. Heal-/tankdoelen en mana/aggro ingame toetsen; Monk blijft onvolledig.
3. XP-verdeling en blijvende voortgang onderzoeken: de gebruiker zag geen XP
   bij de eerste bot. Daarna loot, inventaris en normale rolgebonden gearupgrades.
4. Een vaste populatie begint verspreid op levels 1-50, met level 50 als
   startgrens, niet als permanente limiet. Autonoom levelen/raiden is nog geen
   bestaande bewezen functie. Pas na de basis volgen AH, soloschaling en LLM-chat.
