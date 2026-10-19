# Botfix 01: startersgear en warrior-benadering

Datum: 19 oktober 2026. Dit is de eerste beperkte botcorrectie na de lokale
Windows/WSL-installatie; geen volledige loot- of dungeonmodule.

## Waargenomen op de gebruikers-pc

De Release-core met scripts en playerbots is gebouwd en geïnstalleerd.
De vier databases zijn geïmporteerd. De wereld initialiseert en de gebruiker
kan met een aangepaste 18414-client inloggen, een personage maken en spelen.
Een warrior kan aan de party worden toegevoegd en met het GM-commando worden
opgeroepen. De gebruiker bevestigt volgen buiten gevecht en aanvallen wanneer
een monster dichtbij komt. Op level 1 ontbreekt uitrusting; benaderen tijdens
gevechten werkt nog onvoldoende. Een prestatiemeting toont 611 AI-updates.

De 259 mmap-parameterbestanden en 6590 aanwezige tiles uit een extern pakket
laden met de echte Detour-bibliotheek zonder fouten. Dit bewijst geen volledige
dekking: tijdens spelen zijn ontbrekende/onlaadbare tiles gemeld voor map 571
(31,31), (32,32), (31,32) en map 0 (35,42). Die zijn nog niet hersteld.

Een lokale database/configuratieback-up en een volledige WSL-export zijn door
de gebruiker uitgevoerd, nadat de servers en MySQL netjes waren gestopt.
De export is als tar gelezen en gehasht; een hersteltest is nog niet uitgevoerd.
Windows-startbestanden, de werkende client-executables en WTF zijn meegekopieerd;
de volledige Windows-clientdata valt buiten deze back-up.

## Wijzigingen

- De uitrustingszoeklus neemt de ondergrens mee. Op levels 1-10 bevat die ook
  requirement 0; een signed teller voorkomt unsigned underflow op nul.
- Witte/grijze uitrusting zonder attribute-statbonussen wordt onder level 10
  niet uitsluitend om ontbrekende stats afgewezen. Klasse/race, slot,
  proficiency, armor/weapon-specialisatie en de normale equipcontroles blijven
  van toepassing. Dit levert nog geen garantie op een volledige set voor elke rol.
- De warrior-alternatiefketen Charge -> Heroic Leap eindigt bij `reach melee`
  in plaats van opnieuw een melee-aanval te proberen op afstand. Dit gebruikt
  de bestaande bewegingsactie; het kan ontbrekende mmaps niet repareren.

## Controle en grenzen

De echte EquipmentSelectionPolicy-header is met C++20, -Wall -Wextra -Werror
gecompileerd en uitgevoerd: alle levelgrenzen 1-90, inclusie van nul, eindige
iteratie en statloze starterkwaliteitgrenzen slagen.
De bestaande native test van de rolclassificatie slaagt voor 34 specialisaties.
Dit is geen nieuwe volledige corebuild en geen ingame-validatie van deze patch.
De gedeeltelijke herbouw en hertest moeten op de gebruikers-pc volgen.

```bash
g++ -std=c++20 -Wall -Wextra -Werror \
  -I modules/mod_playerbots/src/Manager \
  contrib/tests/test_playerbot_equipment_policy.cpp \
  -o /tmp/test-mop-equipment
/tmp/test-mop-equipment
python3 contrib/tests/test_playerbot_roles.py
```

## Nog afzonderlijk te implementeren en testen

1. Deze patch lokaal bouwen en level-1-uitrusting plus warrior-benadering testen.
2. Ontbrekende benodigde looproutetiles identificeren en aanvullen.
3. Automatisch looten met lootrechten, geld, inventarisruimte en rolgebonden
   upgrades aansluiten. De aanwezigheid van `loot` in een strategielijst is
   geen bewijs van een geregistreerde, werkende lootimplementatie.
4. Tank-/healer-/DPS-rollen instellen en ingame testen: aggro, taunts,
   genezen, mana, spellrange en beschikbare levelgebonden vaardigheden.
   Een level-1-personage heeft nog niet de volledige dungeon-toolkit.
5. Pas daarna soloschaling, Auction House-bot en lokale taalmodelchat toevoegen.
   Er is nog geen LLM-koppeling. De aangetroffen Emucoach-configuratie is een
   andere implementatie; die is niet overgenomen en bewijst geen functionaliteit.
