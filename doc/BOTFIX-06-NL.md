# Botfix 06: gedeeld spellleren en partyhealdoelen

Datum: 19 oktober 2026.

## Aanleiding en afbakening

Gebruiker bevestigt update 5 geïnstalleerd. Een level-4 priest in de party helpt
niet met aanvallen/healen terwijl de groepsleider gewond is en vecht. Buiten de
party vallen bots wel zelfstandig mobs aan. De exacte ingame actietrace is nog
niet vastgelegd. Deze update corrigeert aantoonbare broncodeproblemen; de lokale
hertest moet bevestigen welke daarvan het geobserveerde gedrag veroorzaakten.

## Gedeeld voor alle classes

De botfactory had geen actieve routine die gewone class-spells op het actuele
level aanvult. Alleen level/statverhoging geeft daarvoor geen volledige garantie:
Player::GiveLevel initialiseert skills en specialisatiespells, maar dit is geen
algemene class-spelltrainer. Nieuwe routine BotFactory::LearnClassSpells gebruikt
de al geladen MoP `player_class_spells`-gegevens via ServiceMgr en SpellInfo/DBC.
Geen zelfbedachte vaste unlocklevels of geïmporteerde Wrath-spellnummers.

De routine draait bij botlogin, na de bestaande initialisatie/startlevelwijziging,
en bij een volgende level-up van een bot met een AI. Menselijke spelers worden
niet automatisch getraind. Filters: bestaand spellrecord, SpellLevel > 0 en niet
boven botlevel, onbekende spell, juiste classfamilie/ras, geen talent en geldig
volgens SpellMgr. SpecializationSpells.dbc voorkomt dat exclusieve spells van
andere specs of vóór level 10 worden aangeleerd. De geladen class-spelllijst
bepaalt het aanbod; ontbrekende/verkeerde brondata is hiermee niet gerepareerd.

Bij nieuwe spells worden de AI-waarden ververst. Strategieën worden bij level-up
opnieuw opgebouwd, ook bij een overgang naar een nieuw levelbereik. Geleerde
spells worden bij login opgeslagen; bij level-up blijft de normale core-save
actief. XP, geld, gear, quests en levels worden door de leerfunctie niet gewist.

Dit pad ondersteunt alle elf class-ID's, inclusief Monk. Het is geen bewijs dat
alle classrotaties of tank-/healrollen werken: Monk mist in deze module nog een
eigen AiObjectContext. Ook andere classstrategieën bevatten nog Wrath-erfenis.

## Healselectie en priest

PartyMemberToHeal sloeg iedere GM over en derefereerde groepsleden vóór een
nullcontrole. Nu mogen gewonde GM-groepsleden ook healdoel worden; ontbrekende of
niet ingeladen spelers worden overgeslagen. De gedeelde Check controleert null,
in-world, levend, kaart, charm, afstand en LOS. Dat helpt alle healende classes.
Normale CanCast-/vriendelijkheid-/spelcontroles blijven verantwoordelijk voor
de uiteindelijke cast; dit verandert geen GM- of spelbeveiligingsrechten.

Priest-heal- en shadow-defaults bevatten nu Smite vóór de wandfallback. De
bestaande spellbook-/CanCast-controles bepalen of hij die aanval werkelijk kent
en mag gebruiken. De noncombatstrategie biedt Flash Heal ook bij een medium
gewonde partygenoot aan; voorheen stonden daar alleen Renew en Penance. Er
worden geen hogerelevels-spells geforceerd. Er is geen heal- of damage-effect
rechtstreeks toegepast: bots moeten de normale spellcast uitvoeren.

De bestaande DPS-/tank-assiststrategieën zijn bekeken en aanwezig voor de
ondersteunde classcontexts; geen bewezen fout gevonden die hier veilig een
algemene vervanging rechtvaardigt. De echte combat-/kite-opvolging blijft een
aparte controle. De grens tegen zelfstandig grinden in een spelersparty blijft.

## Wrath-referentie

https://github.com/mod-playerbots/mod-playerbots/blob/d750b4b3a50effdf22bedc8032f0e8e5f7cb8091/src/Bot/Factory/PlayerbotFactory.cpp

De Wrath-factory heeft InitAvailableSpells met trainerdata. MoP heeft andere
interfaces en gegevens. Het principe van levelgebonden spells aanvullen wordt
hier met de bestaande MoP-class-spellservice uitgevoerd. Geen complete factory,
raidstrategieën of Wrath-spelllijsten overgenomen.

## Uitgevoerde controles

- `test_playerbot_class_spellbook.py`: compileert de volledige nieuwe
  productiemethode met gecontroleerde core-interfaces; elf classpaden,
  levelgrenzen, herhaling, family/ras, talentuitsluiting, eigen/vreemde spec,
  pre-spec levels, ontbrekende/ongeldige data en behoud XP/gear slagen.
- `test_playerbot_heal_targets.py`: compileert de twee volledige
  productiemethoden; GM-/normale leider, ontbrekend lid, gezondheid,
  world/map/LOS/range/charm en huisdieren slagen.
- `test_playerbot_priest_defaults.py`: complete defaultactielijsten met bekende
  spellsubsets: Smite zonder wand, wandfallback, geen bekende aanval en behoud
  van de hogere shadow-prioriteit slagen. Geen simulatie van de hele engine.
- Bestaande login-, progressie-, grind-, 18 cast/bewegingsscenario's,
  34 specrollen en equipment-policytest slagen opnieuw.
- Activatiescript gecontroleerd met `bash -n`.

De tests gebruiken gecontroleerde interfaces, geen draaiende MoP-world of echte
DBC/SQL-dataset. Geen volledige corebuild of ingame-verificatie van update 6 in
deze werkomgeving. Die volgen op de gebruikersmachine. Geen claim dat alle
classes, raidrollen of autonoom questen nu compleet zijn. Geen merge naar master.

## Lokale installatie en controle

Na ophalen op een nieuwe lokale branch, met beide servers netjes gestopt:

```bash
bash contrib/apply-local-bot-update.sh
```

Het script test, bouwt met de bestaande buildmap, installeert en bewaart de
configuratieback-up. De tien bots en groeimodus van update 5 blijven actief.
Buildlog: `~/mop/bot-update06-build.log`. Geen database-import of reset nodig.

Start via Start-MoP. Test met de bestaande level-4 priest (geen nieuwe bot nodig):
zelf een passend monster aanvallen, daarna met ontbrekende health blijven staan.
Beoordeel aanvallen en healen apart; normale mana-, range- en LOS-grenzen gelden.
Andere classes kunnen dezelfde spellboekaanvulling bij herlogin gebruiken;
controleren op hun eigen beschikbare aanvallen/heals, geen hogerelevelskills
verwachten. Bevestig vervolgens dat XP/gear/party na netjes herstarten behouden
blijven. Als de priest nog stilstaat, is een ingame spell-/actietrace de volgende
beperkte stap; meer classes tegelijk als volledig gerepareerd labelen is dan niet
onderbouwd.
