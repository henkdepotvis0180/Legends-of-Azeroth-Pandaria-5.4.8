# Update 08: gerichte partydiagnose, nog geen bewezen cast-/volgreparatie

Datum: 19 oktober 2026.

## Nieuwe lokale observatie

De priest cast Smite buiten de party, maar in de party geen damage of heals.
De bot neemt wel afstand. Volgen herstelt pas na verlaten/opnieuw aansluiten.
Voor Smite is spellleren dus niet meer de primaire blokkade. Andere spells en
de precieze uitvoering van update 7 zijn niet afzonderlijk vastgesteld.

## Vergelijking Wrath en MoP

Referentie mod-playerbots/mod-playerbots op
`d750b4b3a50effdf22bedc8032f0e8e5f7cb8091`:

- src/Bot/PlayerbotAI.cpp
- src/Ai/Base/Value/DpsTargetValue.cpp
- src/Ai/Base/Value/PartyMemberToHeal.cpp

De MoP-code heeft veel van dezelfde basis: groep/masterkeuze, DPS-doelen uit
attackers/RTI, afzonderlijke combat/noncombat-engines, partyhealselectie.
MoP herkiest de master vooral als de huidige master ontbreekt of een bot is;
een onjuiste maar nog aanwezige menselijke master wordt daarmee niet vanzelf
gecorrigeerd. Dit is een mogelijk risico, geen bewezen toestand bij Clemeria.

DPS-selectie gebruikt de attackerslijst, niet automatisch ieder geselecteerd
monster van de speler. De priest krijgt in noncombat DPS assist en de priest-nc
heals. In combat bestaan heal- en Smite-acties. Solo voegt de factory extra DPS-
strategieën toe. Daarom bewijst solo Smite niet dat dezelfde strategie in de
party actief is. Zonder runtimegegevens rechtvaardigt deze vergelijking geen
complete vervanging door de Wrath-code. Monk blijft een afzonderlijke lacune.

## Diagnoseopdracht

Nieuwe opdracht in worldserverconsole (zonder punt):

```
botdiag Clemeria
```

Ingame voor accounts met de bestaande NPCBOT-commandobevoegdheid:
`.botdiag Clemeria`. Consoleuitvoer is makkelijker volledig te kopiëren.

De opdracht toont de levende AI: naam/level/state, combat/beweging/mana,
master/groepsleider/sameGroup/mastercombat, huidige en DPS-/healdoelen,
health healdoel, aantal attackers en strategieën van beide engines. Maximaal
30 actieve niet-passieve bekende spells worden getoond. Zes priest-spellnamen
worden via de gewone spell-idlookup en CanCastSpell geprobed, met doel/LOS/afstand.
Er wordt geen CastSpell of verplaatsing uitgevoerd en geen party aangepast.
De waarde-/spellcontroles kunnen normale AI-caches verversen. Dit is een
momentopname, geen actietrace of garantie dat een strategie de cast kiest.
CanCastSpell kan beweging/range als herstelbare situatie accepteren; canCast=1
bewijst dus geen uitgevoerde of geslaagde cast. De probe-lijst is priestrelevant;
de basisstatus kan voor iedere bot worden gelezen.

## Controle en grenzen

`contrib/tests/test_playerbot_diagnostics.py` compileert de complete handler met
gecontroleerde core-interfaces en strenge C++20-waarschuwingen. Getest: ontbrekende
bot/echte speler weigeren, partystatus, spellweergave, probes en ontbrekend doel.
De testinterfaces bieden geen castuitvoerings-/movement-/party-mutatie-API.
Test slaagt. Script syntactisch gecontroleerd met bash -n.
Geen volledige corebuild of ingame-opdracht uitgevoerd in deze werkomgeving.
Dat volgt op de gebruikersmachine. Geen cast- of volgreparatie geclaimd.

## Kleine lokale vervolgstap

Stop beide servers netjes, haal deze commit op en draai:

```bash
bash contrib/apply-local-bot-update.sh
```

Buildlog: ~/mop/bot-update08-build.log. Bestaande bots, voortgang en tien-bot-
configuratie blijven behouden. Start via Start-MoP. Terwijl Clemeria in de party
stilstaat en jij gewond bent/in gevecht: voer botdiag Clemeria uit in de
worldserverconsole en bewaar de uitvoer. Als vergelijking dezelfde opdracht
buiten de party uitvoeren terwijl hij wél Smite cast. Beide momentopnamen
bepalen of master, strategie, doelwit of castmogelijkheid verschilt. Dit vervangt
verdere blinde patches. Geen SQL-import/reset en geen merge naar master.
