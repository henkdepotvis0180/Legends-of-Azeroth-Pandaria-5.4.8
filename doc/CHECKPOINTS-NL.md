# Herstelpunten MoP 18414

Werk in afzonderlijke delen. Start een volgend zwaar onderdeel pas nadat het
vorige archief succesvol is bewaard. Een voortgangsbericht of lokaal bestand
alleen telt niet als duurzaam herstelpunt.

## Actuele status na herstelpunt 22

- De Linux-extractietools en aanvullende afhankelijkheden zijn bewaard.
- Zesenveertig MPQ-bronbestanden zijn gecontroleerd en bewaard: 16.206.125.717 bytes.
- Alle gedeelde/enUS-updates, locale-enUS.MPQ, Windows-patches en misc.MPQ zijn
  beschikbaar. Alle zeven basisarchieven die de extractors openen zijn bewaard.
- De nieuwe DBC/DB2-extractie is klaar en afzonderlijk bewaard: 393 DBC + 58 DB2.
  De 200 door de core gebruikte tabellen en acht versiemarkers slagen; 34 lege,
  niet door deze core geladen DBC-bestanden zijn apart vastgelegd.
- Ontbrekende lokale kopieën zijn succesvol uit de bewaarde herstelpunten
  teruggezet. De gebruiker hoeft niets handmatig te downloaden of uit te pakken.
- De cameraset is compleet: alle 27 unieke bestanden voor 34 DBC-rijen zijn
  aanwezig, gecontroleerd en afzonderlijk bewaard.
- De 9.691 nieuwe terreinbestanden voor 187 kaart-ID’s zijn gecontroleerd en bewaard.
- De definitieve vmaps zijn gecontroleerd en bewaard: 216 bomen, 5.150 tiles en
  12.123 hoofdmodellen, plus aanvullende modelbestanden en de gameobject-index.
- Nog nodig: mmaps, core/database-herbouw en een nieuwe
  native startproef. Er is nog geen volledige repack of ingame botvalidatie.

## 01 — Linux-extractietools: bewaard

Bestand: `MoP-18414-checkpoint-01-tools-linux.tar.gz`
Datum: 18 oktober 2026
Grootte: 88379229 bytes
SHA-256: `4cc92d62d7b6c9bb5dac4c84137744b2ba4899ee4bca8bca58afc2315a6f4f1e`

Dit bestand is daadwerkelijk opgeslagen en als download verstrekt in het gesprek.
Het bevat mapextractor, vmap4extractor, vmap4assembler, mmaps_generator,
check_mmap_tiles, CMake 3.28.3 en aanvullende buildbibliotheken/headers.
Platform: Ubuntu 24.04 x86_64 met GCC 13 en normale systeembibliotheken.
Broncodecommit: `0abef97223144fabcfc11b48dd8484aa23f988cd`.

Controle: de vier tooltargets zijn opnieuw gebouwd, hun runtimebibliotheken
laden, launch-/lege-invoerproeven zijn uitgevoerd. Het uiteindelijke archief is
naar een andere map uitgepakt; CMake start daar en alle vijf binaire hashes komen
overeen met checkpoint.json. Er is in dit deel geen clientdata verwerkt.

Herstel: pak het archief uit en voer `source checkpoint-01/restore-env.sh` uit.
Gebruik de tools uit checkpoint-01/bin; de toolbuild hoeft niet opnieuw.
De broncode blijft op GitHub. Dit is nog geen volledige server of repack.

## 02 — enUS- en Windows-bronpatches: bewaard

Bestand: `MoP-18414-checkpoint-02-clientpatches.tar.gz`
Datum: 18 oktober 2026
Archiefgrootte: 198.875.127 bytes
SHA-256: `0abfe396abbcd3e5c90da8ac72cf41d9a713a3b9e718df7832921f59d2b5ca34`

Dit tweede archief is daadwerkelijk opgeslagen en als download verstrekt in het
gesprek. Het bevat twintig MPQ-bestanden, samen 211.882.074 bytes: achttien
enUS-taalupdates, Data/base-Win.MPQ en Updates/wow-0-18414-Win-final.MPQ.
Het oorspronkelijke manifest en batch-report.json zitten in het archief.
Dit is een deel van de bronset, nog geen complete client of serverdata-extractie.

De manifest-MD5 komt overeen met de vastgelegde 18414-referentie. Alle twintig
bestandsgroottes en MPQ-signaturen kloppen. Na archivering zijn alle twintig
MPQ-bestanden uit het archief opnieuw gelezen en tegen hun vastgelegde SHA-256
gecontroleerd. Deze hashes identificeren de ontvangen bytes en zijn geen
onafhankelijk door upstream gepubliceerde digests.

De hervatbare downloader staat in contrib/recovery/download_client_batch.py.
Zeven lokale HTTP-integratietests slagen: volledige download, hervatten,
Range genegeerd, foutieve Content-Range, hergebruik zonder netwerk, onjuist
bestaand bestand en onveilige padnaam. Hervatten van deze vaste batch:

```bash
python3 contrib/recovery/download_client_batch.py --output /blijvende/schijf/clientpatches
python3 contrib/tests/test_client_batch_download.py
```

Pak bij hervatten eerst dit archief terug. Zo hoeven deze twintig bestanden niet
opnieuw te worden gedownload. De grote basis-MPQs en gedeelde
base-updates ontbreken nog; de volgende kleine stap is locale-enUS.MPQ afzonderlijk bewaren.

## 06 — gedeelde update 16309: bewaard

Dit zesde herstelpunt is daadwerkelijk opgeslagen in twee 7-Zip-volumes en als
download verstrekt in het gesprek. Beide delen zijn nodig; plaats ze samen en
open .001 met 7-Zip. Datum: 18 oktober 2026.

| Bestand | Bytes | SHA-256 |
| --- | --- | --- |
| MoP-18414-checkpoint-06-base16309.7z.001 | 471.859.200 | 0c0b94ae67b89fc6e0ea1c2a05df2404d2a0b8ca13794d26aed2bb52309966e6 |
| MoP-18414-checkpoint-06-base16309.7z.002 | 101.517.249 | dc61321fb1fd66bc8c2f480c7e63e911e11d0a71283aeba9df9de8cc46a2a0ca |

Inhoud: Data/wow-update-base-16309.MPQ, checkpoint.json en README-NL.md.
Het bronbestand is 579.482.392 bytes, overeenkomstig de vaste bronlijst, met
verwachte MPQ-signatuur. SHA-256 van de ontvangen bytes:
`4bb5622251b0aaba6398b4f8749ae4dfefe3384c501f0c3e3a180cb3919b2a57`.

De complete multipart-archieftest slaagde. Het MPQ-bestand is daarna uit het
archief gelezen en de grootte en hash kwamen overeen. De hashes identificeren
ontvangen bytes en zijn geen onafhankelijk upstream-digests. Extractie van
serverdata is in dit deel nog niet uitgevoerd.

Er zijn nu 35 verschillende MPQ-bronbestanden bewaard in checkpoints 02–06,
samen 1.797.268.938 bytes. De vier overige grotere gedeelde updates en benodigde
basis-MPQs ontbreken nog. Volgende stap: wow-update-base-16516.MPQ afzonderlijk
bewaren, wederom met meerdere archiefdelen als dat nodig is.

## 07 — gedeelde update 16516: bewaard

Dit herstelpunt is daadwerkelijk opgeslagen en als download beschikbaar in het
gesprek. Alle 3 7-Zip-volumes horen bij elkaar. De assistent kan ze zelf
terugzetten; downloaden door de gebruiker is alleen nodig voor een eigen kopie.
Datum: 18 oktober 2026.

| Bestand | Bytes | SHA-256 |
| --- | --- | --- |
| MoP-18414-checkpoint-07-base16516.7z.001 | 471859200 | 4f019de5493ca434036a3b87c1e73ffdc260dd20f311d4a67ed729f160e57148 |
| MoP-18414-checkpoint-07-base16516.7z.002 | 471859200 | 20b19f2bf4a8466acff7c730d503d29ee2bf8b3a972df38b4d2b959d953d9e74 |
| MoP-18414-checkpoint-07-base16516.7z.003 | 146186099 | 7806a67cd7a4c29d607a112636208b0e8ba901de0b20fc81ace1f133f51bd518 |

Inhoud: Data/wow-update-base-16516.MPQ, checkpoint.json en README-NL.md.
Het bronbestand is 1126065580 bytes, overeenkomstig de vaste bronlijst,
met verwachte MPQ-signatuur. SHA-256 van de ontvangen bytes:
`fbb6f82db3b0f4eb23085237b2dac62f068d8fcedba567da1c673a0bb987c128`.

De complete archieftest slaagde. Het MPQ-bestand is uit het archief gelezen;
grootte en hash kwamen overeen. De hashes identificeren ontvangen bytes en zijn
geen onafhankelijk upstream-digests. Serverdata-extractie is nog niet uitgevoerd.

Er zijn nu 36 verschillende MPQ-bronbestanden bewaard in checkpoints 02–07,
samen 2923334518 bytes. De overige bronbestanden volgen afzonderlijk;
ieder volgend zwaar deel begint pas nadat het vorige herstelpunt is opgeslagen.

## 08 — gedeelde update 16844: bewaard

Dit herstelpunt is daadwerkelijk opgeslagen en als download beschikbaar in het
gesprek. Alle 1 7-Zip-volumes horen bij elkaar. De assistent kan ze zelf
terugzetten; downloaden door de gebruiker is alleen nodig voor een eigen kopie.
Datum: 18 oktober 2026.

| Bestand | Bytes | SHA-256 |
| --- | --- | --- |
| MoP-18414-checkpoint-08-base16844.7z.001 | 272546309 | 04cd10d07a30dfd12366a59548145a33235365dc1d04308f4be297006f1eb0a2 |

Inhoud: Data/wow-update-base-16844.MPQ, checkpoint.json en README-NL.md.
Het bronbestand is 275245678 bytes, overeenkomstig de vaste bronlijst,
met verwachte MPQ-signatuur. SHA-256 van de ontvangen bytes:
`f84046c548e7836485abc16337bac94738faac3720f6ec8da08cf244af26f3f9`.

De complete archieftest slaagde. Het MPQ-bestand is uit het archief gelezen;
grootte en hash kwamen overeen. De hashes identificeren ontvangen bytes en zijn
geen onafhankelijk upstream-digests. Serverdata-extractie is nog niet uitgevoerd.

Er zijn nu 37 verschillende MPQ-bronbestanden bewaard in checkpoints 02–08,
samen 3198580196 bytes. De overige bronbestanden volgen afzonderlijk;
ieder volgend zwaar deel begint pas nadat het vorige herstelpunt is opgeslagen.

## 09 — gedeelde update 17266: bewaard

Dit herstelpunt is daadwerkelijk opgeslagen en als download beschikbaar in het
gesprek. Alle 2 7-Zip-volumes horen bij elkaar. De assistent kan ze zelf
terugzetten; downloaden door de gebruiker is alleen nodig voor een eigen kopie.
Datum: 18 oktober 2026.

| Bestand | Bytes | SHA-256 |
| --- | --- | --- |
| MoP-18414-checkpoint-09-base17266.7z.001 | 471859200 | ca921db9f4939a129d5385a1d2d5ce3934ea9f12d1b4466004a311245fea797d |
| MoP-18414-checkpoint-09-base17266.7z.002 | 202270210 | 3625558122e95797ace35fb70f07e597848c9616fa372f4b9225bff6e124bd67 |

Inhoud: Data/wow-update-base-17266.MPQ, checkpoint.json en README-NL.md.
Het bronbestand is 681260822 bytes, overeenkomstig de vaste bronlijst,
met verwachte MPQ-signatuur. SHA-256 van de ontvangen bytes:
`08cbedc5e9bf9c85103c79d57902431fbd87dd892395861a2c0e0b9b9cc6f6b8`.

De complete archieftest slaagde. Het MPQ-bestand is uit het archief gelezen;
grootte en hash kwamen overeen. De hashes identificeren ontvangen bytes en zijn
geen onafhankelijk upstream-digests. Serverdata-extractie is nog niet uitgevoerd.

Er zijn nu 38 verschillende MPQ-bronbestanden bewaard in checkpoints 02–09,
samen 3879841018 bytes. De overige bronbestanden volgen afzonderlijk;
ieder volgend zwaar deel begint pas nadat het vorige herstelpunt is opgeslagen.

## 10 — gedeelde update 17325: bewaard

Dit herstelpunt is daadwerkelijk opgeslagen en als download beschikbaar in het
gesprek. Alle 1 7-Zip-volumes horen bij elkaar. De assistent kan ze zelf
terugzetten; downloaden door de gebruiker is alleen nodig voor een eigen kopie.
Datum: 18 oktober 2026.

| Bestand | Bytes | SHA-256 |
| --- | --- | --- |
| MoP-18414-checkpoint-10-base17325.7z.001 | 216594907 | 5567ec31e2aaa29b36aa3c544cdd9131b56b04ec58dd0f66a25ba8a93eb34245 |

Inhoud: Data/wow-update-base-17325.MPQ, checkpoint.json en README-NL.md.
Het bronbestand is 216873161 bytes, overeenkomstig de vaste bronlijst,
met verwachte MPQ-signatuur. SHA-256 van de ontvangen bytes:
`ed302b0683c7ca9870d1e478fa5af7b900f0f4cb310b755b184de3fac09c3273`.

De complete archieftest slaagde. Het MPQ-bestand is uit het archief gelezen;
grootte en hash kwamen overeen. De hashes identificeren ontvangen bytes en zijn
geen onafhankelijk upstream-digests. Serverdata-extractie is nog niet uitgevoerd.

Er zijn nu 39 verschillende MPQ-bronbestanden bewaard in checkpoints 02–10,
samen 4096714179 bytes. De overige bronbestanden volgen afzonderlijk;
ieder volgend zwaar deel begint pas nadat het vorige herstelpunt is opgeslagen.

## 11 — bronbestand misc: bewaard

Dit herstelpunt is daadwerkelijk opgeslagen en als download beschikbaar in het
gesprek. Alle 2 7-Zip-volumes horen bij elkaar. De assistent kan ze zelf
terugzetten; downloaden door de gebruiker is alleen nodig voor een eigen kopie.
Datum: 18 oktober 2026.

| Bestand | Bytes | SHA-256 |
| --- | --- | --- |
| MoP-18414-checkpoint-11-misc.7z.001 | 471859200 | f1bcd005f830fe7f113624f3fbf207b9e92d3176b2a923524c94288b796c95b7 |
| MoP-18414-checkpoint-11-misc.7z.002 | 311671456 | 1017500c578679be02576db0ae3ab5dc080fb727d8894d168f0a8fc7d62d9167 |

Inhoud: Data/misc.MPQ, checkpoint.json en README-NL.md.
Het bronbestand is 811676948 bytes, overeenkomstig de vaste bronlijst,
met verwachte MPQ-signatuur. SHA-256 van de ontvangen bytes:
`967e086270511ad2e64b8df716e46bd96b99db0a08c30cb8894ff439ac4a0db7`.

De complete archieftest slaagde. Het MPQ-bestand is uit het archief gelezen;
grootte en hash kwamen overeen. De hashes identificeren ontvangen bytes en zijn
geen onafhankelijk upstream-digests. Serverdata-extractie is nog niet uitgevoerd.

Er zijn nu 40 verschillende MPQ-bronbestanden bewaard in checkpoints 02–11,
samen 4908391127 bytes. De overige bronbestanden volgen afzonderlijk;
ieder volgend zwaar deel begint pas nadat het vorige herstelpunt is opgeslagen.

## 12 — nieuwe DBC/DB2-extractie: bewaard

Bestand: `MoP-18414-checkpoint-12-dbc-db2.tar.gz`
Archiefgrootte: 22.840.037 bytes
SHA-256: `75f616407cf89298da974f0561ec93f7b3719bd3ce8e26ce616a18cbafb397a0`
Datum: 18 oktober 2026.

Dit archief is daadwerkelijk opgeslagen en als download beschikbaar in het
gesprek. Inhoud: 393 DBC-bestanden in Data/dbc en 58 DB2-bestanden in Data/dbc/enUS,
plus invoer-, extractie- en validatieverslagen. Uitvoer van de extractor: exit 0.
Alle 451 tabelbestanden zijn volledig uit het archief gelezen en tegen hun
vastgelegde grootte/hash gecontroleerd. Het pakket bevat 160.549.940 tabelbytes.

De 174 actieve DBC- en 26 actieve DB2-loads zijn opnieuw gecontroleerd tegen de
formaten uit de core: aanwezigheid, signature/header, payloadlengte, veldtelling,
minimale recordbreedte en grenzen van stringverwijzingen. De acht 5.4.8-markers
kloppen. De drie bekende extra-recordbreedtes zijn afzonderlijk vastgelegd.
Er zijn daarnaast 34 niet door deze core geladen DBC-bestanden met nul bytes;
ze zijn apart gemeld en niet als geldige vereiste tabellen meegerekend.

De nieuwe validator staat in contrib/tests/check_client_tables.py. Drie proeven
met beschadigde/verkeerd geplaatste vereiste tabellen zijn terecht afgewezen:
afgekapt bestand, stringoffset buiten de stringtabel en DB2 buiten dbc/enUS.
Dit is een bestands-/formaatcontrole, geen nieuwe native serverstart of gameplaytest.

Alle veertig invoer-MPQs (4.908.391.127 bytes) zijn tegen hun bewaarde hashes
gecontroleerd. De vijf ontbrekende lokale archiefdelen van checkpoints 03–06
zijn uit de opgeslagen herstelpunten teruggezet en ook tegen hun eerder
gepubliceerde archiefhashes gecontroleerd. Er zijn geen eerdere bronbestanden
opnieuw van Blizzard gehaald. Het terugzetten is door de assistent uitgevoerd.

Herstel: pak het archief uit en voeg Data/dbc toe aan de latere server-DataDir.
De bron-MPQs en de tabellen hoeven bij een onderbreking niet opnieuw te worden
verwerkt. Cameras, maps, vmaps, mmaps en de nieuwe core-/runtimeproef volgen apart.

## 13 — afzonderlijke camera-extractor: bewaard

Bestand: `MoP-18414-checkpoint-13-camera-tool.tar.gz` (182.582 bytes).
SHA-256: `ad23e77e380c0d8f48341c80795cbc518b698f68f6ecd94b36c87b70147ac6ed`.
De tool is opnieuw gebouwd. De argumentcontrole accepteert nu extractievlaggen
1–7, inclusief camera-only (`-e 4`); 0, 8 en -1 worden geweigerd. Tien CLI-proeven
slagen. De nieuwe binary en herstelinstructies zijn daadwerkelijk opgeslagen.
De tool bevat ook de eerdere DB2-mapreparatie; aanvullende bibliotheken komen
uit herstelpunt 01. De broncodewijziging staat in src/tools/map_extractor/System.cpp.

Er zijn nog geen camerabestanden opgeleverd: de proef met de beperkte DBC-bronset
levert nul camera's op omdat de gemeenschappelijke world/model-bronnen ontbreken.
De volgende bron is world.MPQ (3.365.020.722 bytes), bewaard in acht ruwe delen
van maximaal 450.000.000 bytes. Elk deel wordt afzonderlijk opgeslagen vóór het
volgende begint. Volgnummer 14 blijft onvoltooid totdat alle delen en de volledige
samengevoegde bron gecontroleerd zijn. Dit is geen complete camera-/kaartset.

## 14 — world.MPQ: bewaard en gecontroleerd

Alle acht ruwe delen zijn afzonderlijk opgeslagen, elk vóór het volgende begon.
Bestanden: MoP-18414-checkpoint-14-world.MPQ.part001 tot en met part008.
Delen 1–7 zijn elk 450.000.000 bytes; deel 8 is 215.020.722 bytes.
Samen: 3.365.020.722 bytes. SHA-256 van de samengevoegde bron:
`a88c4557d605ece209cd9d4d334c07db3c1d1db26aa282c4eee64e85dd62bbbe`.
Per-deelgroottes/hashes en herstelinstructies staan in
validation/client-batch14-2026-10-18.json en het bewaarde herstelarchief
MoP-18414-checkpoint-14-world-recovery.tar.gz (5.587 bytes,
SHA-256 e5e7a9f557c5883cc028454325d15c73034fd80527b65d44e4262a778158fa34).
Alle delen zijn opnieuw gelezen bij het samenvoegen; hun hashes en totale
bronlengte kloppen. Er is geen onafhankelijke upstream SHA-256 beschikbaar.

De echte camera-only-extractie levert vier van de 27 unieke modellen voor de
34 CinematicCamera-rijen op. Deze vier slagen voor header-, camera-array-,
timestamp- en splinegrenscontroles. 23 modellen ontbreken nog.
De vier modellen, extractielog en controle zijn ook in het herstelarchief
bewaard. Dit is nadrukkelijk geen complete cameraset of nieuwe native startproef.
Gebruik op Linux een volledig kleinletterig uitvoerpad: de extractor maakt het
hele uitvoerpad kleinletterig. De volgende beperkte bronbatch is model.MPQ;
daarna opnieuw de ontbrekende camera's inventariseren.

## 15 — model.MPQ en 23 camera's: bewaard en gecontroleerd

Drie ruwe delen zijn afzonderlijk opgeslagen vóór het volgende deel begon:
MoP-18414-checkpoint-15-model.MPQ.part001 tot en met part003.
De eerste twee delen zijn elk 450.000.000 bytes; het derde is 277.530.975 bytes.
De samengevoegde bron telt 1.177.530.975 bytes, SHA-256:
`a5ed6a22d9c585cb20629eed8cb0132f28bca4576f04e8ec80d1710b66562e50`.
Alle delen zijn bij het samenvoegen opnieuw gelezen en tegen hun hashes
gecontroleerd. Dit zijn ontvangen hashes, geen onafhankelijke upstream-digests.
Tijdelijke bronkopieën zijn pas na bronverificatie en bevestigde bewaring verwijderd.

De echte camera-only-extractie met world, model en de eerdere bronset levert
23 geldige unieke modellen uit de 27 vereiste modellen voor 34 DBC-rijen.
De extractor meldt 28 extracties; deze teller bevat herhaalde verwijzingen en
is geen telling van unieke vereiste modellen. De controle telt die afzonderlijk.
Alle 23 slagen voor header-, camera-array-, timestamp- en splinegrenscontroles.

Nog ontbrekend: flybybloodelf.m2, flybydraenei.m2, flybysunwell5man.m2 en
flybydeathknight.m2. Verwachte volgende bronnen zijn expansion1.MPQ en
expansion2.MPQ; na iedere bron volgt opnieuw een extractiecontrole.
Er is geen nieuwe native serverstart of ingame camera-/bottest uitgevoerd.

Bewaard herstelarchief met 23 cameras, extractielog, controle en instructies:
MoP-18414-checkpoint-15-model-recovery.tar.gz (22.324 bytes),
SHA-256 `20fa156f82e0a6bdb354071641536f8d901bd5e3270ddf907d349be9b9146d2b`.
De drie grote brondelen zijn afzonderlijk bewaard. Details en per-bestandhashes:
validation/client-batch15-2026-10-18.json.

## 16 — expansion1.MPQ en 26 camera's: bewaard en gecontroleerd

Vier ruwe delen zijn elk bewaard vóór het volgende begon:
MoP-18414-checkpoint-16-expansion1.MPQ.part001 tot en met part004.
De eerste drie delen zijn elk 450.000.000 bytes; deel vier is 76.915.825 bytes.
Samen: 1.426.915.825 bytes. SHA-256 van de samengevoegde bron:
`6a22f89bfe37f15a5d46ffa4dba2cfbae6f93171b8ff51812ef37c63ec553ef6`.
Alle delen zijn opnieuw gelezen bij het samenvoegen en hun groottes/hashes
kloppen. De hashes identificeren ontvangen bytes; er is geen onafhankelijke
upstream SHA-256 beschikbaar. Een afgebroken overdracht van deel twee is
hervat vanaf de gedeeltelijk ontvangen bytes; eerder bewaarde delen zijn
niet opnieuw vanaf de bron gedownload.

Deze uitvoering begon in een lege tijdelijke omgeving. Alle 42 eerdere
bronbestanden zijn uit de bewaarde herstelpunten teruggezet en tegen hun
gepubliceerde groottes/hashes gecontroleerd, samen 9.450.942.824 bytes.
Ook de camera-extractor, DBC/DB2 en eerdere 23 camera's zijn teruggezet;
hun controle/hashes komen overeen. Geen eerdere bron is opnieuw vanaf Blizzard
gehaald. Details: validation/input-restoration16-2026-10-18.json.

De echte camera-only-extractie met de complete beschikbare invoer geeft nu
26 geldige unieke modellen voor de 34 CinematicCamera-rijen. Nieuw:
flybybloodelf.m2, flybydraenei.m2 en flybysunwell5man.m2. Alle 23 eerdere
camerahashes blijven gelijk. De extractor meldt 31 extracties; de controle
telt de unieke vereiste modellen afzonderlijk. Geen van de 26 is ongeldig.
Header-, camera-array-, volledige timestamp- en splinegrenscontroles slagen.
Alle 26 camerabestanden zijn daarna ook uit het herstelarchief gelezen en
opnieuw tegen hun hashes gecontroleerd.

Nog ontbrekend: cameras/flybydeathknight.m2. De volgende beperkte bron is
Data/expansion2.MPQ. Deze cameraset is nog niet compleet. Er is geen nieuwe
native serverstart, clientlogin of ingame camera-/bottest uitgevoerd.

Bewaard herstelarchief met de 26 camera's, controlescript, relevante
DBC/structuurdefinitie, extractielog, bron-/herstelverslagen en instructies:
MoP-18414-checkpoint-16-expansion1-recovery.tar.gz (36890 bytes).
SHA-256: `198f6ac698e108033c8d6830eb0ad9183106b23b8d14cdac609b04af90ce7537`.
De vier grote bron-delen zijn afzonderlijk bewaard. Per-deel- en cameragegevens:
validation/client-batch16-2026-10-18.json.

## 17 — expansion2.MPQ en volledige cameraset: bewaard en gecontroleerd

Alle zeven brondelen zijn afzonderlijk opgeslagen vóór het volgende begon.
Bestanden: MoP-18414-checkpoint-17-expansion2.MPQ.part001 t/m part007.
Deel 1: 100.000.000 bytes. Delen 2–6: elk 450.000.000 bytes.
Deel 7: 340.192.921 bytes. Voeg de delen in volgorde binair samen.
Samen: 2.690.192.921 bytes. SHA-256 van de samengevoegde bron:
`c3028ca5e01e4a1df63e0fa2660b2231980a0b94dab4a1dd44d610f63f78eee8`.
Alle delen zijn opnieuw gelezen bij het samenvoegen; hun groottes/hashes kloppen.
Dit zijn hashes van ontvangen bytes, geen onafhankelijk upstream-digests.
Na bewaarproblemen is het eerste deel kleiner opgeslagen. De reeds ontvangen
450 MB is volledig hergebruikt; er is niets daarvan opnieuw gedownload.
De 43 eerdere bronbestanden (10.877.858.649 bytes) zijn opnieuw gecontroleerd;
alle maten/hashes kloppen. Geen oude bron hoefde opnieuw gedownload te worden.

De echte camera-only-extractie eindigt met exit 0 en levert de ontbrekende
flybydeathknight.m2 op. Nu zijn alle 27 unieke modellen voor 34 DBC-rijen aanwezig.
Alle 26 eerdere camerabestandshashes zijn ongewijzigd. De extractor meldt
32 extracties; die teller bevat herhaalde verwijzingen en is geen unieke telling.
De controle telt 27 geldig, 0 ontbrekend en 0 ongeldig. MD20/header, camera-array,
volledige timestamp-arrays en splinegrenzen slagen. Alle 27 bestanden zijn ook
uit het bewaarde archief gelezen en opnieuw tegen hun hashes gecontroleerd.

Bewaard archief met de volledige cameraset, controlescript, DBC/structuurdefinitie,
uitvoerlog, bronmetadata en herstelinstructies:
MoP-18414-checkpoint-17-expansion2-cameras.tar.gz (32386 bytes).
SHA-256: `290225ce0fbdafadddc97fc4a4fc7731ccb7d88329ae8646638d13de28d93869`.
Herstel data/cameras uit dit archief in de latere server-DataDir.
De zeven grote bron-delen zijn afzonderlijk bewaard.
Details: validation/client-batch17-2026-10-18.json.

Dit voltooit de camerabestanden, niet de server. Er is nog geen nieuwe native
worldserverstart, clientlogin of ingame camera-/bottest uitgevoerd. De volgende
afzonderlijke fase betreft de resterende kaart-/vmap-bronnen en extractie.

## 18 — expansion3.MPQ: bewaard en gecontroleerd

Drie ruwe delen zijn elk bewaard voordat het volgende begon:
MoP-18414-checkpoint-18-expansion3.MPQ.part001 t/m part003.
De eerste twee tellen elk 450.000.000 bytes, het derde 176.317.751 bytes.
Samen 1.076.317.751 bytes, SHA-256:
`39195ef132ebe8d9b72d28e3e705044ee7f9b4869fca028f2f438613aef146d4`.
Bij het samenvoegen zijn alle delen opnieuw gelezen en hun hashes gecontroleerd.
Dit zijn ontvangen hashes, geen onafhankelijk upstream-digests.
Metadata en per-deelhashes: validation/client-batch18-2026-10-18.json.
De assistent kan de bron uit de bewaarde delen terugzetten. Kaart-/vmap-extractie
volgt na expansion4.MPQ, de laatste ontbrekende bron die deze extractors openen.

## 19 — expansion4.MPQ: bewaard en gecontroleerd

Vier ruwe delen zijn elk bewaard voordat het volgende begon:
MoP-18414-checkpoint-19-expansion4.MPQ.part001 t/m part004.
De eerste drie tellen elk 450.000.000 bytes, het vierde 211.756.396 bytes.
Samen 1.561.756.396 bytes, SHA-256:
`29df529354ebec8ea168f7f19c94f8bef0264a40d7c336c2fceaf0d712cb9d14`.
Alle delen zijn bij het samenvoegen opnieuw gelezen; hun groottes/hashes kloppen.
Dit zijn ontvangen hashes, geen onafhankelijk upstream-digests.
Metadata: validation/client-batch19-2026-10-18.json.
Alle zeven gemeenschappelijke basisarchieven die de extractors openen zijn nu
aanwezig, naast de locale- en gedeelde updates. Dit zijn serverextractiebronnen,
geen complete speelbare client. De kaartdata en vmaps volgen als eigen herstelpunten.

## 20 — kaartdata: volledig geëxtraheerd, gecontroleerd en bewaard

De mapextractor eindigt met exit 0 na 26.99 seconden.
Uitvoer: 9.691 .map-bestanden voor 187 kaart-ID’s, samen 988.873.376 bytes.
Alle bestanden gebruiken kaartformaat 10 en interne data-build 18273.
Iedere header, bloksignatuur, blokgrens en payloadlengte is gecontroleerd:
area, hoogte, flight bounds, vloeistoffen en holes. Geen ongeldige bestanden.
Alle bestanden hebben een SHA-256 in validation.json binnen het archief.
Dit is formaatcontrole van echte uitvoer, geen nieuwe native worldserverstart.

Bewaard in twee ruwe archiefdelen:
- MoP-18414-checkpoint-20-maps.tar.gz.part001 — 450.000.000 bytes.
- MoP-18414-checkpoint-20-maps.tar.gz.part002 — 68.019.588 bytes.
Voeg beide in volgorde samen tot MoP-18414-checkpoint-20-maps.tar.gz.
SHA-256 van het complete archief: `885525df7fb941717185aa2270b19ba984cf555b2b090cfe8a4601db366fcfc0`.
Alle 9.691 kaartbestanden zijn uit dit archief opnieuw gelezen en gehasht,
waarna beide delen succesvol zijn bewaard. Herstel data/maps in de server-DataDir.
Volledig verslag en deelhashes: validation/maps20-2026-10-18.json.
De assistent kan de bestanden terugzetten; handmatig downloaden is niet nodig.

## 21 — ruwe vmap-uitvoer: bewaard en gecontroleerd

De extractor eindigt met exit 0 na 64.85 seconden.
Buildings bevat 12.911 ruwe modellen plus dir_bin en temp_gameobject_models,
samen 12.913 bestanden en 572.104.568 bytes. Alle ruwe assetheaders zijn
VMAP043; beide indexbestanden zijn aanwezig. Alle bestanden zijn gehasht.

Er zijn 110 bronmeldingen over 92 unieke ontbrekende/lege bronnen. De
genormaliseerde bronset is identiek aan de eerdere extractie; er zijn geen
nieuwe ontbrekende bronnen. Dit is niet hetzelfde als foutloze spelinhoud.
De volledige meldingenlijst blijft bewaard; impact op gameplay is niet getest.

Archief: MoP-18414-checkpoint-21-vmap-raw.tar.gz (283.189.167 bytes).
SHA-256: `f79216500b89da2e879043d8a4aaf48db2e9f5af673c888b61fb9ad2e8acc209`.
Alle 12.913 bestanden zijn uit het archief opnieuw gelezen/gehasht; het archief
is daadwerkelijk bewaard vóór de assembler start. Dit is nog geen definitieve
vmapset. Herstel Buildings en gebruik vmap4assembler uit checkpoint 01.
Metadata: validation/vmap-raw21-2026-10-18.json.

## 22 — definitieve vmaps: samengesteld, native gecontroleerd en bewaard

De assembler eindigt met exit 0 na 12.1 seconden.
Uitvoer: 216 .vmtree-bestanden, 5.150 .vmtile-bestanden, 12.123 .vmo-modellen,
4.329 aanvullende .m2-modelbestanden en GameObjectModels.dtree.
Samen: 21.819 bestanden en 1.167.534.320 bytes. Alle VMAP_4.3-signaturen
en bestandshashes zijn gecontroleerd. De gameobject-index bevat 4.787 geldige
displayrecords; alle 3.914 unieke modelverwijzingen wijzen naar bestaande .vmo's.

Een nieuwe native controle gebruikt de echte WorldModel::readFile,
ModelSpawn::readFromFile en VMapManager2::loadMap uit de collisionbibliotheek.
Alle 16.452 hoofd-/aanvullende modellen, 216 bomen en 5.150 tiles laden;
2.259.334 tile-modelverwijzingen bestaan. Resultaat: 0 fouten, exit 0.
De model-/groep-BIH-data wordt daarbij daadwerkelijk gelezen.
Een model met correcte signature maar bewust afgekapt vóór de payload wordt
terecht afgewezen. Broncode en binary van deze controle zitten in het archief.
Dit is een native bestandslezercontrole, geen nieuwe worldserverstart.

Bewaard in twee ruwe archiefdelen:
- MoP-18414-checkpoint-22-vmaps.tar.gz.part001 — 450.000.000 bytes.
- MoP-18414-checkpoint-22-vmaps.tar.gz.part002 — 108.849.731 bytes.
Voeg beide in volgorde samen tot MoP-18414-checkpoint-22-vmaps.tar.gz.
SHA-256 van het complete archief: `5b14bf0ef91ec3f99b5a5e3d4f2e080da01ae3bc377f5024afd1f9c82e3ef38d`.
Alle 21.819 databestanden zijn uit het archief opnieuw gelezen en gehasht;
beide delen zijn succesvol bewaard. Herstel data/vmaps in de server-DataDir.
De bekende 110 bronmeldingen / 92 unieke ontbrekende of lege bronnen blijven
ongewijzigd vastgelegd. Er is geen nieuwe gameplay-, clientlogin- of bottest.

Verslag en deelhashes: validation/vmaps22-2026-10-18.json.
De kaartdata en vmaps zijn nu bewaard. Volgende zware stap: mmaps, in beperkte
kaartgroepen met native Detour-controle en bewaring per groep.

## Volgende afzonderlijke delen

1. Clientbrondata in beperkte downloadbatches. Bewaar iedere batch met exacte
   bestandsnamen/groottes en een archiefhash. Gebruik de vastgelegde 18414-lijst
   in validation/client-data-2026-10-18.json. Download geen batches opnieuw als
   een bewaard archief kan worden teruggezet.
2. DBC/DB2 (enUS DB2 in dbc/enUS), cameras, maps en vmaps elk afzonderlijk
   extraheren, controleren en bewaren. Ruwe invoer pas daarna opruimen.
3. Mmaps per kaart of beperkte kaartgroep. Controleer gemaakte tiles met
   check_mmap_tiles en bewaar iedere batch vóór de volgende. Grote continenten
   eventueel in tilebatches met bijbehorende .mmap-parameterbestanden opsplitsen.
4. Core met scripts en bots bouwen en binaries bewaren. Verse vier databases
   installeren en native startproef uitvoeren. Daarna het eindpakket samenstellen.

Bij hervatten is dit document de actuele voortgang. De eerdere succesvolle
runtimeproef staat in RUNTIME-CONTROLE-NL.md; de toenmalige runtimebestanden zijn
verloren gegaan. Checkpoints 01 tot en met 22 hierboven zijn de nieuwe bewaarde delen.


