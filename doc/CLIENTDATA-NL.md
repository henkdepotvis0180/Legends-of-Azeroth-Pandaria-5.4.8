# Clientdata voor build 18414

**Herstelstatus:** de tijdelijke clientdata, gegenereerde serverdata en binaries
zijn na de oorspronkelijke proef door werkruimteonderhoud verwijderd. Er is geen
opgeslagen volledig runtime-herstelpakket. Zie `RUNTIME-CONTROLE-NL.md` voor de historische
eindresultaten en wat opnieuw moet worden opgebouwd.

Op 18 oktober 2026 is de benodigde enUS-clientdata daadwerkelijk gedownload
en met de extractors van deze core verwerkt. De eerdere blokkade door ontbrekende
clientdata is daarmee gedeeltelijk opgelost: DBC, DB2, maps en vmaps zijn
beschikbaar. Volledige mmap-generatie en native start zijn later geslaagd, maar de uitvoer
is niet meer beschikbaar; zie het herstelverslag.

## Downloadbron en controle

De download gebruikt het oorspronkelijke Blizzard-manifest voor de EU-versie
van clientbuild 18414, zoals vastgelegd in
[WoWClientRebuilder](https://github.com/mangostools/WoWClientRebuilder/tree/e41e905208bc2ff20f0007da2240b67c883d725c).
Het StormGarde-archief is niet volledig gedownload; de gecontroleerde eerste
archiefvermeldingen bevatten enGB. Voor onze bots is rechtstreeks enUS gekozen.

Bronmap:

```
http://dist.blizzard.com.edgesuite.net/wow-pod-retail/EU/15890.direct/
```

Manifest: `wow-18414-E68C6C849BBD16D2A8A153AFC865062F.mfil`.
De MD5 van de ontvangen manifestbytes kwam overeen met de vastgelegde waarde
`e68c6c849bbd16d2a8a153afc865062f`.

Er zijn 56 bestanden geselecteerd uit `Data/` en `Updates/`: gedeelde data,
enUS en de Windows-update. Andere talen en OSX zijn uitgesloten. Alle bestanden
zijn gedownload en op hun manifestgrootte gecontroleerd: totaal 23.435.297.608
bytes, ongeveer 23,4 GB / 21,83 GiB. De lijst met bestanden en groottes staat in
`validation/client-data-2026-10-18.json`.

Dit is de clientdata voor extractie. `Wow.exe` is niet uit de patches opgebouwd;
er is hiermee geen zelfstandig speelbare Windows-client verpakt. De individuele
bronbestanden zijn niet tegen onafhankelijke upstream-hashes gecontroleerd.

## Extractie en resultaten

De vier extractietools zijn opnieuw gebouwd uit dezelfde corebron. Alleen hun
CMake-targets zijn gebouwd; dit was geen nieuwe volledige serverbuild.

| Onderdeel | Uitkomst |
| --- | --- |
| DBC-extractie | 393 bestanden, exitcode 0 |
| DB2-extractie | 58 bestanden, in dezelfde geslaagde extractierun |
| Door de core geladen tabellen | 174 DBC + 26 DB2 gecontroleerd |
| Maps | 9.691 bestanden, exitcode 0, alle gecontroleerde headers versie 10 |
| Vmaps | Extractie en assembler beide exitcode 0 |
| Vmap-uitvoer | 216 trees, 5.150 tiles, 12.123 modellen |
| Vmap-headers | Alle gecontroleerde tree/tile/model-bestanden `VMAP_4.3` |
| Mmap-proef | Eén daadwerkelijke tile van 952.668 bytes, mmap-versie 7 |

`maps/0000_43_31.map`, dat de vorige worldserver-start blokkeerde, is nu aanwezig.
Ook `mmaps/0000_43_31.mmtile` is als afzonderlijke generatieproef gemaakt.
Bij de mmap-tool correspondeert de opdracht `--tile 31,43` met deze bestandsnaam.

De tabellencontrole controleerde aanwezigheid, bestandssignatuur, veldtelling,
minimale recordbreedte, payloadlengte en grenzen van stringverwijzingen volgens
de formaten uit de corebron. Drie DBC-bestanden bevatten meer bytes per record
dan het formaat adresseert: `Achievement_Criteria.dbc`, `CriteriaTree.dbc` en
`SpellItemEnchantmentCondition.dbc`. De productie-loader staat dit eveneens toe;
de afwijkingen zijn apart vastgelegd in `validation/client-layouts-2026-10-18.json`.
Dit is geen controle van alle inhoudelijke waarden of een native wereldstart.

De extractor rapporteert interne databuild **18273**. De core vermeldt zelf dat
clientbuild 18414 dezelfde MPQ-buildnamen gebruikt. De download is geselecteerd
met het 18414-manifest; 18273 in de dataheader is hier dus geen zelfstandig bewijs
van een verkeerde clientversie.

## Waarschuwingen en resterende controle

De vmap-extractor meldde 110 keer dat een bronmodel of bronkaart niet kon worden
geopend. De unieke paden zijn bewaard in het validatieverslag. De uiteindelijke
melding van de tool is `Work complete. No errors.`, maar die melding bewijst dus
niet dat er geen ontbrekende bronbestanden zijn. De assembler is wel geslaagd.
De gevolgen voor specifieke locaties en bots moeten tijdens runtime worden getest.

Deze oorspronkelijke extractiecontrole ging vooraf aan de later geslaagde
volledige looproutegeneratie. De volgende beperkingen blijven gelden. De geslaagde
tileproef bewijst dat de tool de gemaakte maps/vmaps voor die tile kan verwerken;
hij bewijst geen volledige pathfinding-dekking. Ook worldserver-start, clientlogin
en groepsgedrag moeten nog opnieuw worden getest.

## Extractie herhalen

Gebruik de tools die uit deze core zijn gebouwd. Onderstaand Linux-voorbeeld
veronderstelt dat ze op `PATH` staan. `client` bevat de gedownloade `Data/`-map;
`data` is een nieuwe uitvoermap. Maak geen uitvoer over een bestaande installatie.

```bash
mkdir -p data/vmaps data/mmaps
mapextractor -i /absoluut/pad/client -o /absoluut/pad/data -b 18414 -e 2
mapextractor -i /absoluut/pad/client -o /absoluut/pad/data -b 18414 -e 1
cd /absoluut/pad/data
vmap4extractor -d /absoluut/pad/client/Data -b 18414
vmap4assembler Buildings vmaps
mmaps_generator 0 --tile 31,43 --threads 6 --silent
```

Voor een volledige mmap-generatie is de opdracht `mmaps_generator --threads 6`.
De latere geslaagde run en het verlies van de tijdelijke uitvoer staan in
`RUNTIME-CONTROLE-NL.md`. De clientdata
en gegenereerde gamebestanden worden niet in deze broncode-repository opgenomen.

Nieuwe bewaarde deelstappen: [CHECKPOINTS-NL.md](CHECKPOINTS-NL.md).
