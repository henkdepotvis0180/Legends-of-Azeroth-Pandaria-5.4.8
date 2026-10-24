# Update 10: werkelijke holy-heal fallback en ontbrekende actieregistraties

Datum: 19 oktober 2026.

## Ingame bewijs uit update 9

Clemeria's combat-trace blijft op `combat formation move - UNKNOWN` en
`shoot - UNKNOWN` steken. Smite wordt niet geselecteerd, hoewel Smite 585 in
botdiag bekend/haalbaar is. De actieve strategie is `holy heal`. Master, party,
DPS-doel en attackers komen overeen met Sams gevecht. De noncombat-trace toont
herhaalde follow FAILED, soms OK. Daarmee is nog niet iedere bewegingsfout verklaard.

## Concrete oorzaak en beperkte reparatie

PriestAiObjectContext registreert `holy heal` als HolyHealPriestStrategy. Deze
class is niet HealPriestStrategy of HolyPriestStrategy, maar erft direct van
GenericPriestStrategy. Hij had alleen `shoot` als defaultaanval. De Smite-fix van
update 6 en de bijbehorende test misten precies deze andere class.

HolyHealPriestStrategy biedt nu Smite aan vóór de wandfallback. Bestaande hogere
prioriteit heals blijven staan. Dit leert geen nieuwe spells en forceert geen
cast; normale useful/possible/mana/range/spellcontroles blijven gelden.

De gemeenschappelijke ActionContext had bovendien geen registratie voor `shoot`
en `combat formation move`, terwijl CastShootAction en CombatFormationMoveAction
al bestaan en de strategieën deze namen gebruiken. Beide worden nu naar hun
bestaande implementatie verwezen. Dit geldt voor alle classcontexts die de
algemene actioncontext gebruiken. Geen nieuwe movement- of schietimplementatie.

## Verificatie

- test_playerbot_priest_defaults.py extraheert nu ook de volledige methode
  HolyHealPriestStrategy::getDefaultActions. Smite bekend zonder wand, alleen
  Shoot bekend en geen bekende aanval slagen, plus bestaande priestgevallen.
- test_playerbot_action_registry.py compileert de volledige echte ActionContext
  met gecontroleerde actieinterfaces en controleert dat de namen naar de juiste
  constructors verwijzen. Bestaande follow blijft beschikbaar; onbekende namen
  blijven onbekend. C++20 -Wall -Wextra -Werror: geslaagd.
- bash -n activatiescript geslaagd.

Geen volledige MoP-corebuild of ingameverificatie van update 10 hier uitgevoerd.
De gebruikersmachine doet de build. Dit corrigeert aantoonbare registry/default-
fouten uit de trace, geen claim dat alle partycasts/volgen nu werken.

## Lokale toepassing

Beide servers netjes stoppen, commit ophalen in een nieuwe lokale branch en:

```bash
bash contrib/apply-local-bot-update.sh
```

Buildlog: ~/mop/bot-update10-build.log. Start via Start-MoP; test dezelfde priest
in dezelfde party. Herhaal `botdiag Clemeria trace`, vecht circa vijf seconden en
lees `botdiag Clemeria`. Smite hoort nu in de gekozen acties te kunnen verschijnen;
shoot/formation horen niet meer UNKNOWN te zijn. Het uiteindelijke resultaat
moet in de game worden bevestigd.

Geen database-import/-reset, botverwijdering of merge naar master. Het te ruime
DBC-spellleerfilter, ontbrekende healspells, resterende follow/pathfindingfouten
en MMAP-dekking blijven afzonderlijke openstaande punten. De data van update 9
bewijzen niet dat Smite zelf onmogelijk is of dat iedere follow FAILED fout is
(bijvoorbeeld al op de gewenste plek staan kan ook geen beweging opleveren).
