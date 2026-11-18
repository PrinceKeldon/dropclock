#!/usr/bin/env python3
"""Static multilingual launch-site generator.

Run:  python3 build.py        ->  writes ./dist  (upload that folder to any static host)

Before deploying, edit the CONFIG block below (SITE_URL, affiliate tags).
When Rockstar announces one official unlock time, set UNLOCK_UTC and rebuild.
"""
import json
import os
import shutil
from html import escape
from urllib.parse import quote_plus

# ----------------------------- CONFIG ---------------------------------------
SITE_URL = "https://dropclock.live"     # your domain, no trailing slash
BRAND = "DropClock"                    # neutral brand, no game trademarks
UNLOCK_UTC = None                     # e.g. "2026-11-19T05:00:00Z" once officially confirmed
TARGET_LOCAL = "2026-11-19T00:00:00"  # fallback assumption: local midnight

# One Amazon Associates tracking ID per store. Replace the placeholders.
AFFILIATE_TAGS = {
    "amazon.ae": "YOURTAG-AE",   # needs a UAE/Egypt address, skipped for now
    "amazon.com": "dropclock-21",
    "amazon.co.uk": "dropclock-21",
    "amazon.ca": "dropclock-21",
    "amazon.de": "dropclock-21",
    "amazon.fr": "dropclock-21",
    "amazon.es": "dropclock-21",
    "amazon.it": "dropclock-21",
    "amazon.pl": "dropclock-21",
    "amazon.nl": "dropclock-21",
}

# Google Search Console ownership file, served at /<name> (HTML-file verification).
GOOGLE_VERIFICATION_FILE = "googleae33614df66708bc.html"
# -----------------------------------------------------------------------------

LANG_ORDER = ["en", "de", "fr", "es", "it", "pl", "nl", "ar"]
STORE = {
    "en": "amazon.com", "ar": "amazon.ae", "de": "amazon.de", "fr": "amazon.fr",
    "es": "amazon.es", "it": "amazon.it", "pl": "amazon.pl", "nl": "amazon.nl",
}
NATIVE = {
    "en": "English", "de": "Deutsch", "fr": "Français", "es": "Español",
    "it": "Italiano", "pl": "Polski", "nl": "Nederlands", "ar": "العربية",
}
CITY_TZ = ["Europe/Berlin", "Europe/Paris", "Europe/Madrid", "Europe/Rome",
           "Europe/Warsaw", "Europe/Amsterdam", "Asia/Dubai"]

T = {
    "en": dict(
        title="GTA 6 unlock time by city - countdown",
        desc="When does GTA 6 unlock where you live? Countdown to November 19, 2026 on PS5 and Xbox Series X|S.",
        h1="When does GTA 6 unlock for you?",
        sub="Countdown to November 19, 2026 for PS5 and Xbox Series X|S.",
        assumed="Rockstar has not confirmed one worldwide unlock time. This countdown assumes midnight in your local time zone on November 19. We will switch to the official time as soon as it is announced.",
        official="Official unlock time confirmed by Rockstar.",
        cd=["Days", "Hours", "Min", "Sec"], released="GTA 6 is out!",
        local="Your local time", col_city="City", col_time="Unlock (local time)",
        assumed_cell="00:00 (assumed)", nav_hw="PS5 storage", nav_home="Countdown",
        hw_title="Which SSD for PS5: what to check before you buy",
        hw_desc="Requirements for PS5 storage expansion: M.2 NVMe Gen4, read speed, heatsink and more.",
        hw_h1="More storage for your PS5: what to know before you buy",
        hw_intro="Big games fill the internal SSD fast. These are the requirements for PS5 storage expansion.",
        specs_h="What to check",
        specs=["PCIe Gen4 x4 NVMe SSD in M.2 format (usually 2280)",
               "Recommended read speed: 5,500 MB/s or higher",
               "A heatsink is required, either built in or fitted separately",
               "Capacities from 250 GB to 8 TB are supported",
               "An external USB drive can store PS5 games but not run them"],
        xbox="Xbox Series X|S uses a proprietary expansion card: a regular M.2 SSD will not fit.",
        buy_h="See on Amazon",
        buy=["PS5-compatible M.2 SSDs", "Xbox expansion card", "DualSense controller"],
        queries=["PS5 M.2 SSD heatsink", "Xbox Series expansion card", "DualSense controller"],
        disclosure="As an Amazon Associate we earn from qualifying purchases. The price you pay does not change.",
        footer="Independent fan site. Not affiliated with Rockstar Games or Take-Two Interactive. GTA is a trademark of its respective owners.",
        cities=["Berlin", "Paris", "Madrid", "Rome", "Warsaw", "Amsterdam", "Dubai"],
        tzlabel="Detected time zone",
    ),
    "de": dict(
        title="GTA 6 Freischaltzeit nach Stadt - Countdown",
        desc="Wann startet GTA 6 bei dir? Countdown bis zum 19. November 2026 für PS5 und Xbox Series X|S.",
        h1="Wann wird GTA 6 für dich freigeschaltet?",
        sub="Countdown bis zum 19. November 2026 für PS5 und Xbox Series X|S.",
        assumed="Rockstar hat keine weltweit einheitliche Freischaltzeit bestätigt. Dieser Countdown geht von Mitternacht in deiner lokalen Zeitzone am 19. November aus. Sobald die offizielle Zeit bekannt ist, stellen wir um.",
        official="Offizielle Freischaltzeit von Rockstar bestätigt.",
        cd=["Tage", "Std.", "Min.", "Sek."], released="GTA 6 ist da!",
        local="Deine Ortszeit", col_city="Stadt", col_time="Freischaltung (Ortszeit)",
        assumed_cell="00:00 (angenommen)", nav_hw="PS5-Speicher", nav_home="Countdown",
        hw_title="Die richtige SSD für die PS5: worauf du achten musst",
        hw_desc="Anforderungen an die PS5-Speichererweiterung: M.2 NVMe Gen4, Lesegeschwindigkeit, Kühlkörper und mehr.",
        hw_h1="Mehr Speicher für die PS5: Das musst du vor dem Kauf wissen",
        hw_intro="Große Spiele füllen die interne SSD schnell. Hier sind die Anforderungen für die PS5-Speichererweiterung.",
        specs_h="Worauf du achten musst",
        specs=["PCIe-Gen4-x4-NVMe-SSD im M.2-Format (meist 2280)",
               "Empfohlene Lesegeschwindigkeit: 5.500 MB/s oder mehr",
               "Ein Kühlkörper ist erforderlich, entweder integriert oder separat montiert",
               "Kapazitäten von 250 GB bis 8 TB werden unterstützt",
               "Externe USB-Laufwerke können PS5-Spiele nur speichern, nicht abspielen"],
        xbox="Die Xbox Series X|S nutzt eine proprietäre Speichererweiterungskarte: normale M.2-SSDs passen nicht.",
        buy_h="Bei Amazon ansehen",
        buy=["PS5-kompatible M.2-SSDs", "Xbox-Speichererweiterung", "DualSense-Controller"],
        queries=["PS5 M.2 SSD Heatsink", "Xbox Series Speichererweiterungskarte", "DualSense Controller"],
        disclosure="Als Amazon-Partner verdiene ich an qualifizierten Verkäufen. Für dich entstehen keine Mehrkosten.",
        footer="Unabhängige Fanseite. Nicht mit Rockstar Games oder Take-Two Interactive verbunden. GTA ist eine Marke der jeweiligen Inhaber.",
        cities=["Berlin", "Paris", "Madrid", "Rom", "Warschau", "Amsterdam", "Dubai"],
        tzlabel="Erkannte Zeitzone",
    ),
    "fr": dict(
        title="Heure de déblocage de GTA 6 par ville - compte à rebours",
        desc="À quelle heure GTA 6 se débloque chez toi ? Compte à rebours jusqu'au 19 novembre 2026 sur PS5 et Xbox Series X|S.",
        h1="À quelle heure GTA 6 se débloque-t-il chez toi ?",
        sub="Compte à rebours jusqu'au 19 novembre 2026 sur PS5 et Xbox Series X|S.",
        assumed="Rockstar n'a pas confirmé d'heure de déblocage unique dans le monde. Ce compte à rebours suppose minuit dans ton fuseau horaire local le 19 novembre. Nous passerons à l'heure officielle dès son annonce.",
        official="Heure de déblocage officielle confirmée par Rockstar.",
        cd=["Jours", "Heures", "Min", "Sec"], released="GTA 6 est disponible !",
        local="Ton heure locale", col_city="Ville", col_time="Déblocage (heure locale)",
        assumed_cell="00:00 (supposé)", nav_hw="Stockage PS5", nav_home="Compte à rebours",
        hw_title="Quel SSD pour la PS5 : ce qu'il faut vérifier avant d'acheter",
        hw_desc="Exigences pour l'extension de stockage de la PS5 : M.2 NVMe Gen4, vitesse de lecture, dissipateur et plus.",
        hw_h1="Plus de stockage pour la PS5 : ce qu'il faut savoir avant d'acheter",
        hw_intro="Les gros jeux remplissent vite le SSD interne. Voici les exigences pour l'extension de stockage de la PS5.",
        specs_h="Ce qu'il faut vérifier",
        specs=["SSD NVMe PCIe Gen4 x4 au format M.2 (souvent 2280)",
               "Vitesse de lecture recommandée : 5 500 Mo/s ou plus",
               "Un dissipateur thermique est obligatoire, intégré ou monté séparément",
               "Capacités prises en charge : de 250 Go à 8 To",
               "Un disque USB externe peut stocker les jeux PS5 mais pas les lancer"],
        xbox="La Xbox Series X|S utilise une carte d'extension propriétaire : un SSD M.2 classique ne convient pas.",
        buy_h="Voir sur Amazon",
        buy=["SSD M.2 compatibles PS5", "Carte d'extension Xbox", "Manette DualSense"],
        queries=["SSD M.2 PS5 dissipateur", "Carte d'extension Xbox Series", "Manette DualSense"],
        disclosure="En tant que Partenaire Amazon, je réalise un bénéfice sur les achats remplissant les conditions requises. Le prix ne change pas pour toi.",
        footer="Site de fans indépendant. Non affilié à Rockstar Games ni à Take-Two Interactive. GTA est une marque de ses propriétaires.",
        cities=["Berlin", "Paris", "Madrid", "Rome", "Varsovie", "Amsterdam", "Dubaï"],
        tzlabel="Fuseau horaire détecté",
    ),
    "es": dict(
        title="Hora de desbloqueo de GTA 6 por ciudad - cuenta atrás",
        desc="¿A qué hora se desbloquea GTA 6 donde vives? Cuenta atrás hasta el 19 de noviembre de 2026 en PS5 y Xbox Series X|S.",
        h1="¿Cuándo se desbloquea GTA 6 donde vives?",
        sub="Cuenta atrás hasta el 19 de noviembre de 2026 en PS5 y Xbox Series X|S.",
        assumed="Rockstar no ha confirmado una hora de desbloqueo única en todo el mundo. Esta cuenta atrás asume la medianoche en tu zona horaria local el 19 de noviembre. Cambiaremos a la hora oficial en cuanto se anuncie.",
        official="Hora de desbloqueo oficial confirmada por Rockstar.",
        cd=["Días", "Horas", "Min", "Seg"], released="¡GTA 6 ya está aquí!",
        local="Tu hora local", col_city="Ciudad", col_time="Desbloqueo (hora local)",
        assumed_cell="00:00 (supuesto)", nav_hw="Almacenamiento PS5", nav_home="Cuenta atrás",
        hw_title="Qué SSD comprar para la PS5: lo que debes comprobar",
        hw_desc="Requisitos para ampliar el almacenamiento de la PS5: M.2 NVMe Gen4, velocidad de lectura, disipador y más.",
        hw_h1="Más almacenamiento para la PS5: lo que debes saber antes de comprar",
        hw_intro="Los juegos grandes llenan rápido el SSD interno. Estos son los requisitos de la ampliación de almacenamiento de la PS5.",
        specs_h="Qué debes comprobar",
        specs=["SSD NVMe PCIe Gen4 x4 en formato M.2 (normalmente 2280)",
               "Velocidad de lectura recomendada: 5.500 MB/s o más",
               "Es obligatorio un disipador de calor, integrado o montado aparte",
               "Se admiten capacidades de 250 GB a 8 TB",
               "Un disco USB externo puede guardar juegos de PS5, pero no ejecutarlos"],
        xbox="La Xbox Series X|S usa una tarjeta de expansión propietaria: un SSD M.2 normal no sirve.",
        buy_h="Ver en Amazon",
        buy=["SSD M.2 compatibles con PS5", "Tarjeta de expansión Xbox", "Mando DualSense"],
        queries=["SSD M.2 PS5 disipador", "Tarjeta de expansión Xbox Series", "Mando DualSense"],
        disclosure="Como afiliado de Amazon, obtengo ingresos por las compras adscritas que cumplen los requisitos aplicables. No pagas nada extra.",
        footer="Sitio de fans independiente. Sin relación con Rockstar Games ni Take-Two Interactive. GTA es marca de sus respectivos propietarios.",
        cities=["Berlín", "París", "Madrid", "Roma", "Varsovia", "Ámsterdam", "Dubái"],
        tzlabel="Zona horaria detectada",
    ),
    "it": dict(
        title="Orario di sblocco di GTA 6 per città - conto alla rovescia",
        desc="A che ora si sblocca GTA 6 da te? Conto alla rovescia fino al 19 novembre 2026 su PS5 e Xbox Series X|S.",
        h1="Quando si sblocca GTA 6 da te?",
        sub="Conto alla rovescia fino al 19 novembre 2026 su PS5 e Xbox Series X|S.",
        assumed="Rockstar non ha confermato un unico orario di sblocco mondiale. Questo conto alla rovescia presuppone la mezzanotte nel tuo fuso orario locale il 19 novembre. Passeremo all'orario ufficiale appena verrà annunciato.",
        official="Orario di sblocco ufficiale confermato da Rockstar.",
        cd=["Giorni", "Ore", "Min", "Sec"], released="GTA 6 è uscito!",
        local="Il tuo orario locale", col_city="Città", col_time="Sblocco (ora locale)",
        assumed_cell="00:00 (presunto)", nav_hw="Archiviazione PS5", nav_home="Conto alla rovescia",
        hw_title="Quale SSD per PS5: cosa controllare prima di comprare",
        hw_desc="Requisiti per l'espansione di memoria della PS5: M.2 NVMe Gen4, velocità di lettura, dissipatore e altro.",
        hw_h1="Più spazio per la PS5: cosa sapere prima di comprare",
        hw_intro="I giochi grandi riempiono in fretta l'SSD interno. Ecco i requisiti per l'espansione di memoria della PS5.",
        specs_h="Cosa controllare",
        specs=["SSD NVMe PCIe Gen4 x4 in formato M.2 (di solito 2280)",
               "Velocità di lettura consigliata: 5.500 MB/s o più",
               "Serve un dissipatore di calore, integrato o montato separatamente",
               "Sono supportate capacità da 250 GB a 8 TB",
               "Un disco USB esterno può archiviare i giochi PS5 ma non eseguirli"],
        xbox="Xbox Series X|S usa una scheda di espansione proprietaria: un normale SSD M.2 non è compatibile.",
        buy_h="Guarda su Amazon",
        buy=["SSD M.2 compatibili con PS5", "Scheda di espansione Xbox", "Controller DualSense"],
        queries=["SSD M.2 PS5 dissipatore", "Scheda di espansione Xbox Series", "Controller DualSense"],
        disclosure="In qualità di Affiliato Amazon, ricevo un guadagno dagli acquisti idonei. Per te il prezzo non cambia.",
        footer="Sito indipendente di fan. Non affiliato a Rockstar Games né a Take-Two Interactive. GTA è un marchio dei rispettivi proprietari.",
        cities=["Berlino", "Parigi", "Madrid", "Roma", "Varsavia", "Amsterdam", "Dubai"],
        tzlabel="Fuso orario rilevato",
    ),
    "pl": dict(
        title="Godzina odblokowania GTA 6 według miasta - odliczanie",
        desc="O której odblokuje się GTA 6 u Ciebie? Odliczanie do 19 listopada 2026 na PS5 i Xbox Series X|S.",
        h1="Kiedy GTA 6 odblokuje się u Ciebie?",
        sub="Odliczanie do 19 listopada 2026 na PS5 i Xbox Series X|S.",
        assumed="Rockstar nie potwierdził jednej wspólnej godziny odblokowania na całym świecie. To odliczanie zakłada północ w Twojej strefie czasowej 19 listopada. Przełączymy je na oficjalną godzinę, gdy tylko zostanie ogłoszona.",
        official="Oficjalna godzina odblokowania potwierdzona przez Rockstar.",
        cd=["Dni", "Godz.", "Min", "Sek."], released="GTA 6 już jest!",
        local="Twój czas lokalny", col_city="Miasto", col_time="Odblokowanie (czas lokalny)",
        assumed_cell="00:00 (zakładane)", nav_hw="Pamięć PS5", nav_home="Odliczanie",
        hw_title="Jaki dysk SSD do PS5: na co zwrócić uwagę przed zakupem",
        hw_desc="Wymagania dla rozszerzenia pamięci PS5: M.2 NVMe Gen4, prędkość odczytu, radiator i więcej.",
        hw_h1="Więcej miejsca na PS5: co warto wiedzieć przed zakupem",
        hw_intro="Duże gry szybko zapełniają wewnętrzny dysk SSD. Oto wymagania dla rozszerzenia pamięci PS5.",
        specs_h="Na co zwrócić uwagę",
        specs=["Dysk SSD NVMe PCIe Gen4 x4 w formacie M.2 (zwykle 2280)",
               "Zalecana prędkość odczytu: 5500 MB/s lub więcej",
               "Wymagany jest radiator, wbudowany lub montowany osobno",
               "Obsługiwane pojemności: od 250 GB do 8 TB",
               "Zewnętrzny dysk USB może przechowywać gry na PS5, ale nie można ich z niego uruchamiać"],
        xbox="Xbox Series X|S używa własnościowej karty rozszerzenia: zwykły dysk M.2 nie pasuje.",
        buy_h="Zobacz na Amazon",
        buy=["Dyski M.2 zgodne z PS5", "Karta rozszerzenia Xbox", "Kontroler DualSense"],
        queries=["dysk SSD M.2 PS5 radiator", "Karta rozszerzeń Xbox Series", "Kontroler DualSense"],
        disclosure="Jako Partner Amazon zarabiam na kwalifikujących się zakupach. Dla Ciebie cena się nie zmienia.",
        footer="Niezależna strona fanów. Brak powiązań z Rockstar Games ani Take-Two Interactive. GTA jest znakiem towarowym odpowiednich właścicieli.",
        cities=["Berlin", "Paryż", "Madryt", "Rzym", "Warszawa", "Amsterdam", "Dubaj"],
        tzlabel="Wykryta strefa czasowa",
    ),
    "nl": dict(
        title="Ontgrendeltijd van GTA 6 per stad - aftelklok",
        desc="Hoe laat wordt GTA 6 bij jou ontgrendeld? Aftellen naar 19 november 2026 op PS5 en Xbox Series X|S.",
        h1="Wanneer wordt GTA 6 bij jou ontgrendeld?",
        sub="Aftellen naar 19 november 2026 op PS5 en Xbox Series X|S.",
        assumed="Rockstar heeft geen wereldwijd uniforme ontgrendeltijd bevestigd. Deze aftelklok gaat uit van middernacht in jouw lokale tijdzone op 19 november. Zodra de officiële tijd bekend is, schakelen we over.",
        official="Officiële ontgrendeltijd bevestigd door Rockstar.",
        cd=["Dagen", "Uur", "Min", "Sec"], released="GTA 6 is uit!",
        local="Jouw lokale tijd", col_city="Stad", col_time="Ontgrendeling (lokale tijd)",
        assumed_cell="00:00 (aangenomen)", nav_hw="PS5-opslag", nav_home="Aftellen",
        hw_title="Welke SSD voor de PS5: waar je op moet letten",
        hw_desc="Eisen voor PS5-opslaguitbreiding: M.2 NVMe Gen4, leessnelheid, heatsink en meer.",
        hw_h1="Meer opslag voor de PS5: dit moet je weten voor je koopt",
        hw_intro="Grote games vullen de interne SSD snel. Dit zijn de eisen voor PS5-opslaguitbreiding.",
        specs_h="Waar je op moet letten",
        specs=["PCIe Gen4 x4 NVMe-SSD in M.2-formaat (meestal 2280)",
               "Aanbevolen leessnelheid: 5.500 MB/s of hoger",
               "Een heatsink is verplicht, ingebouwd of apart gemonteerd",
               "Capaciteiten van 250 GB tot 8 TB worden ondersteund",
               "Een externe USB-schijf kan PS5-games opslaan, maar niet afspelen"],
        xbox="De Xbox Series X|S gebruikt een eigen uitbreidingskaart: een gewone M.2-SSD past niet.",
        buy_h="Bekijk op Amazon",
        buy=["PS5-compatibele M.2-SSD's", "Xbox-uitbreidingskaart", "DualSense-controller"],
        queries=["PS5 M.2 SSD heatsink", "Xbox Series uitbreidingskaart", "DualSense controller"],
        disclosure="Als Amazon-partner verdien ik aan kwalificerende aankopen. Voor jou verandert de prijs niet.",
        footer="Onafhankelijke fansite. Niet gelieerd aan Rockstar Games of Take-Two Interactive. GTA is een merk van de betreffende eigenaren.",
        cities=["Berlijn", "Parijs", "Madrid", "Rome", "Warschau", "Amsterdam", "Dubai"],
        tzlabel="Gedetecteerde tijdzone",
    ),
    "ar": dict(
        title="موعد فتح GTA 6 حسب المدينة - العد التنازلي",
        desc="متى تُفتح GTA 6 في مدينتك؟ عدّ تنازلي حتى 19 نوفمبر 2026 على PS5 وXbox Series X|S.",
        h1="متى تُفتح GTA 6 في مدينتك؟",
        sub="عدّ تنازلي حتى 19 نوفمبر 2026 على PS5 وXbox Series X|S.",
        assumed="لم تؤكد Rockstar موعد فتح موحّدًا في جميع أنحاء العالم. يفترض هذا العدّ التنازلي منتصف الليل بتوقيتك المحلي في 19 نوفمبر. سنحدّثه إلى الموعد الرسمي فور الإعلان عنه.",
        official="الموعد الرسمي للفتح مؤكَّد من Rockstar.",
        cd=["أيام", "ساعات", "دقائق", "ثوانٍ"], released="GTA 6 متاحة الآن!",
        local="توقيتك المحلي", col_city="المدينة", col_time="الفتح (بالتوقيت المحلي)",
        assumed_cell="00:00 (افتراضي)", nav_hw="تخزين PS5", nav_home="العد التنازلي",
        hw_title="أي SSD تختار لجهاز PS5: ما يجب التحقق منه قبل الشراء",
        hw_desc="متطلبات توسعة تخزين PS5: M.2 NVMe من الجيل الرابع، سرعة القراءة، المبرّد الحراري وغيرها.",
        hw_h1="مساحة تخزين أكبر لجهاز PS5: ما يجب معرفته قبل الشراء",
        hw_intro="تملأ الألعاب الكبيرة وحدة SSD الداخلية بسرعة. هذه متطلبات توسعة التخزين في PS5.",
        specs_h="ما يجب التحقق منه",
        specs=["وحدة SSD من نوع NVMe بواجهة PCIe Gen4 x4 بحجم M.2 (غالبًا 2280)",
               "سرعة القراءة الموصى بها: 5500 ميغابايت/ثانية أو أكثر",
               "المبرّد الحراري مطلوب، سواء كان مدمجًا أو مثبّتًا بشكل منفصل",
               "السعات المدعومة من 250 غيغابايت إلى 8 تيرابايت",
               "يمكن لقرص USB الخارجي تخزين ألعاب PS5 لكن لا يمكن تشغيلها منه"],
        xbox="يستخدم Xbox Series X|S بطاقة توسعة خاصة: لا تناسبه وحدات M.2 العادية.",
        buy_h="اطّلع على Amazon",
        buy=["وحدات M.2 SSD المتوافقة مع PS5", "بطاقة توسعة Xbox", "يد تحكم DualSense"],
        queries=["PS5 M.2 SSD heatsink", "Xbox Series expansion card", "DualSense controller"],
        disclosure="بصفتنا شركاء Amazon، نحصل على عمولة من عمليات الشراء المؤهلة، دون أي تكلفة إضافية عليك.",
        footer="موقع معجبين مستقل. لا علاقة له بـ Rockstar Games أو Take-Two Interactive. GTA علامة تجارية لأصحابها.",
        cities=["برلين", "باريس", "مدريد", "روما", "وارسو", "أمستردام", "دبي"],
        tzlabel="المنطقة الزمنية المكتشفة",
    ),
}

CSS = """
:root{--bg:#14061f;--ink:#fff3f8;--mut:#c9b3dc;--flamingo:#ff4f8b;--orange:#ff9a3c;--teal:#28d9c8;--line:rgba(255,79,139,.3)}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{color-scheme:dark}
body{margin:0;background:radial-gradient(900px 420px at 50% -60px,#4a1260 0%,rgba(20,6,31,0) 70%),var(--bg);color:var(--ink);font:17px/1.65 system-ui,-apple-system,"Segoe UI",Roboto,"Noto Sans Arabic",sans-serif}
.wrap{max-width:760px;margin:0 auto;padding:18px 16px 56px}
:focus-visible{outline:3px solid var(--teal);outline-offset:3px;border-radius:6px}
header{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;justify-content:space-between}
.brand{font:italic 900 1.45rem/1 "Arial Black","Helvetica Neue",Arial,sans-serif;letter-spacing:-.02em}
.brand::before{content:"";display:inline-block;width:.8em;height:.8em;margin-inline-end:.45em;border-radius:50%;background:linear-gradient(180deg,#ffe38a,#ff4f8b);vertical-align:-.05em}
nav a,.langs a{color:var(--mut);text-decoration:none;margin-inline-end:16px}
nav a:hover,.langs a:hover{color:var(--ink)}
nav a.on,.langs a.on{color:var(--ink);font-weight:700;box-shadow:inset 0 -2px 0 var(--flamingo)}
.langs{display:flex;flex-wrap:wrap;gap:6px 0;padding:12px 0 0;font-size:.92rem}
.hero{position:relative;height:220px;margin:14px 0 0;overflow:hidden;border-radius:18px;background:linear-gradient(180deg,#16062b 0%,#58135f 48%,#ff4f8b 86%,#ffa95c 100%);box-shadow:0 18px 50px rgba(255,79,139,.18)}
.hero.small{height:120px}
.sun{position:absolute;left:50%;bottom:46px;width:170px;height:170px;margin-left:-85px;border-radius:50%;background:linear-gradient(180deg,#ffe38a 0%,#ffb347 42%,#ff4f8b 100%);box-shadow:0 0 70px rgba(255,120,150,.75);-webkit-mask-image:linear-gradient(#000 0 52%,transparent 52% 56%,#000 56% 63%,transparent 63% 68%,#000 68% 75%,transparent 75% 81%,#000 81% 88%,transparent 88% 95%,#000 95%);mask-image:linear-gradient(#000 0 52%,transparent 52% 56%,#000 56% 63%,transparent 63% 68%,#000 68% 75%,transparent 75% 81%,#000 81% 88%,transparent 88% 95%,#000 95%);animation:rise 1.4s cubic-bezier(.2,.7,.2,1) both}
.hero.small .sun{width:100px;height:100px;margin-left:-50px;bottom:28px}
@keyframes rise{from{transform:translateY(60px);opacity:0}to{transform:none;opacity:1}}
.floor{position:absolute;left:0;right:0;bottom:0;height:48px;background:#14061f;overflow:hidden;border-top:1px solid rgba(255,79,139,.7)}
.hero.small .floor{height:30px}
.floor::before{content:"";position:absolute;left:-50%;right:-50%;top:0;height:300%;background-image:linear-gradient(rgba(255,79,139,.6) 1px,transparent 1px),linear-gradient(90deg,rgba(255,79,139,.6) 1px,transparent 1px);background-size:40px 40px;transform:perspective(120px) rotateX(60deg);transform-origin:top center;animation:grid 4s linear infinite}
@keyframes grid{to{background-position:0 40px}}
.palm{position:absolute;bottom:22px;height:150px;width:auto;color:#07020f}
.hero.small .palm{height:84px;bottom:14px}
.palm.l{left:7%}
.palm.r{right:7%;transform:scaleX(-1)}
h1{font:italic 900 clamp(2rem,6.5vw,3.2rem)/1.05 "Arial Black","Helvetica Neue",Arial,sans-serif;letter-spacing:-.03em;margin:30px 0 10px}
h2{font-size:1.25rem;margin:30px 0 8px}
html[lang=ar] h1,html[lang=ar] .brand,html[lang=ar] .cd b,html[lang=ar] .out{font-family:system-ui,"Noto Sans Arabic",sans-serif;font-style:normal;letter-spacing:0}
.sub{color:var(--mut);margin:0 0 20px;max-width:62ch}
.note{border-inline-start:4px solid var(--flamingo);padding:10px 14px;background:rgba(255,79,139,.08);border-start-end-radius:10px;border-end-end-radius:10px;color:var(--mut);font-size:.95rem;max-width:68ch}
.cd{display:grid;grid-template-columns:repeat(4,1fr);margin:26px 0;border:1px solid var(--line);border-radius:16px;overflow:hidden;background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.02));box-shadow:0 0 28px rgba(255,79,139,.16)}
.cd div{padding:16px 4px 12px;text-align:center}
.cd div+div{border-inline-start:1px solid var(--line)}
.cd b{display:block;font:italic 900 clamp(2rem,9vw,3.4rem)/1.05 "Arial Black","Helvetica Neue",Arial,sans-serif;font-variant-numeric:tabular-nums;background:linear-gradient(180deg,#ffe38a,#ff4f8b);-webkit-background-clip:text;background-clip:text;color:transparent}
.cd span{color:var(--mut);font-size:.85rem}
.out{font:italic 900 2rem/1.2 "Arial Black","Helvetica Neue",Arial,sans-serif;text-align:center;margin:26px 0}
table{width:100%;border-collapse:collapse;margin:14px 0 26px}
th,td{padding:11px 8px;border-bottom:1px solid var(--line);text-align:start}
th{color:var(--teal);font-weight:600;font-size:.9rem}
tbody tr:last-child td{border-bottom:0}
ul.specs{padding-inline-start:20px}
ul.specs li{margin:8px 0}
.btns{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0}
.btn{display:inline-block;background:linear-gradient(90deg,var(--flamingo),var(--orange));color:#1c0626;text-decoration:none;padding:12px 18px;border-radius:999px;font-weight:800;transition:transform .15s,box-shadow .15s}
.btn:hover{transform:translateY(-1px);box-shadow:0 8px 24px rgba(255,79,139,.35)}
.small{color:var(--mut);font-size:.85rem}
footer{margin-top:40px;padding-top:16px;border-top:1px solid var(--line)}
@media (max-width:520px){.hero{height:180px}.sun{width:140px;height:140px;margin-left:-70px;bottom:40px}.palm{height:120px}}
@media (prefers-reduced-motion:reduce){.sun,.floor::before{animation:none}.btn{transition:none}}
"""


def path_for(lang, page):
    base = "/" if lang == "en" else f"/{lang}/"
    return base if page == "home" else f"{base}ps5-storage/"


def affiliate_url(lang, query):
    domain = STORE[lang]
    return f"https://www.{domain}/s?k={quote_plus(query)}&tag={AFFILIATE_TAGS[domain]}"


PALM_SYMBOL = (
    '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><symbol id="palm" viewBox="0 0 120 220">'
    '<path d="M62 220 C 60 160, 66 110, 60 60" stroke="currentColor" stroke-width="7" fill="none" stroke-linecap="round"/>'
    '<g stroke="currentColor" stroke-width="5" fill="none" stroke-linecap="round">'
    '<path d="M60 60 C 40 40, 15 40, 0 62"/><path d="M60 60 C 45 30, 25 18, 5 22"/>'
    '<path d="M60 60 C 58 30, 62 12, 74 0"/><path d="M60 60 C 80 38, 105 38, 120 60"/>'
    '<path d="M60 60 C 75 30, 95 18, 115 22"/><path d="M60 60 C 50 45, 35 50, 25 75"/>'
    '<path d="M60 60 C 72 48, 88 52, 98 76"/></g></symbol></svg>'
)
FAVICON = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
    "%3Cdefs%3E%3ClinearGradient id='g' x1='0' y1='0' x2='0' y2='1'%3E%3Cstop offset='0' stop-color='%23ffe38a'/%3E"
    "%3Cstop offset='1' stop-color='%23ff4f8b'/%3E%3C/linearGradient%3E%3C/defs%3E"
    "%3Ccircle cx='16' cy='16' r='14' fill='url(%23g)'/%3E%3C/svg%3E"
)


def hero(page):
    size = "" if page == "home" else " small"
    return (
        PALM_SYMBOL
        + '<div class="hero' + size + '" aria-hidden="true"><div class="sun"></div><div class="floor"></div>'
        '<svg class="palm l" viewBox="0 0 120 220"><use href="#palm"/></svg>'
        '<svg class="palm r" viewBox="0 0 120 220"><use href="#palm"/></svg></div>'
    )


def layout(lang, page, title, desc, body, script=""):
    t = T[lang]
    direction = "rtl" if lang == "ar" else "ltr"
    alts = "".join(
        f'<link rel="alternate" hreflang="{l}" href="{SITE_URL}{path_for(l, page)}">'
        for l in LANG_ORDER
    )
    alts += f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}{path_for("en", page)}">'
    langs = "".join(
        f'<a href="{path_for(l, page)}" hreflang="{l}"{" class=on" if l == lang else ""}>{NATIVE[l]}</a>'
        for l in LANG_ORDER
    )
    nav = (
        f'<a href="{path_for(lang, "home")}"{" class=on" if page == "home" else ""}>{escape(t["nav_home"])}</a>'
        f'<a href="{path_for(lang, "hw")}"{" class=on" if page == "hw" else ""}>{escape(t["nav_hw"])}</a>'
    )
    canonical = f'{SITE_URL}{path_for(lang, page)}'
    return f"""<!doctype html>
<html lang="{lang}" dir="{direction}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} | {BRAND}</title>
<meta name="description" content="{escape(desc)}">
<link rel="canonical" href="{canonical}">
<link rel="icon" href="{FAVICON}">
<meta name="theme-color" content="#14061f">
{alts}
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:image" content="{SITE_URL}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header><span class="brand">{BRAND}</span><nav>{nav}</nav></header>
<div class="langs">{langs}</div>
{hero(page)}
{body}
<footer class="small">{escape(t["footer"])}</footer>
</div>
{script}
</body>
</html>
"""


def home_page(lang):
    t = T[lang]
    status = t["official"] if UNLOCK_UTC else t["assumed"]
    cd = "".join(f'<div><b id="cd{i}">--</b><span>{escape(label)}</span></div>' for i, label in enumerate(t["cd"]))
    rows = "".join(
        f'<tr><td>{escape(name)}</td><td data-tz="{tz}">{escape(t["assumed_cell"])}</td></tr>'
        for name, tz in zip(t["cities"], CITY_TZ)
    )
    body = f"""
<h1>{escape(t["h1"])}</h1>
<p class="sub">{escape(t["sub"])}</p>
<div class="note">{escape(status)}</div>
<div class="cd" id="cd">{cd}</div>
<div class="out" id="out" hidden>{escape(t["released"])}</div>
<p class="small">{escape(t["local"])}: <b id="mine">{escape(t["assumed_cell"])}</b> &middot; {escape(t["tzlabel"])}: <span id="tz">-</span></p>
<table>
<thead><tr><th>{escape(t["col_city"])}</th><th>{escape(t["col_time"])}</th></tr></thead>
<tbody>{rows}</tbody>
</table>
<p><a class="btn" href="{path_for(lang, "hw")}">{escape(t["nav_hw"])}</a></p>
"""
    cfg = json.dumps({
        "unlock_utc": UNLOCK_UTC,
        "target_local": TARGET_LOCAL,
        "locale": lang,
    })
    script = "<script>window.__CFG=" + cfg + ";" + COUNTDOWN_JS + "</script>"
    return layout(lang, "home", t["title"], t["desc"], body, script)


def hw_page(lang):
    t = T[lang]
    specs = "".join(f"<li>{escape(s)}</li>" for s in t["specs"])
    btns = "".join(
        f'<a class="btn" rel="sponsored nofollow noopener" target="_blank" data-q="{escape(q)}" href="{escape(affiliate_url(lang, q))}">{escape(label)}</a>'
        for label, q in zip(t["buy"], t["queries"])
    )
    tag = AFFILIATE_TAGS[STORE[lang]]
    if tag.startswith("YOURTAG"):
        buy_block = ""  # no working affiliate tag for this store yet: hide links
    else:
        buy_block = (
            f'<h2>{escape(t["buy_h"])}</h2>'
            f'<div class="btns">{btns}</div>'
            f'<p class="small">{escape(t["disclosure"])}</p>'
        )
    body = f"""
<h1>{escape(t["hw_h1"])}</h1>
<p class="sub">{escape(t["hw_intro"])}</p>
<h2>{escape(t["specs_h"])}</h2>
<ul class="specs">{specs}</ul>
<p>{escape(t["xbox"])}</p>
{buy_block}
"""
    script = ""
    if lang == "en" and buy_block:
        cfg = json.dumps({"tags": {d: AFFILIATE_TAGS[d] for d in ("amazon.com", "amazon.co.uk", "amazon.ca", "amazon.de")}})
        script = "<script>window.__CFG=" + cfg + ";" + STORE_JS + "</script>"
    return layout(lang, "hw", t["hw_title"], t["hw_desc"], body, script)


STORE_JS = """
(function(){
var C=window.__CFG,tz="";
try{tz=Intl.DateTimeFormat().resolvedOptions().timeZone||"";}catch(e){}
var d="amazon.com";
if(/^Europe\\/(London|Belfast|Jersey|Guernsey|Isle_of_Man)$/.test(tz)){d="amazon.co.uk";}
else if(/^America\\/(Toronto|Vancouver|Edmonton|Winnipeg|Halifax|St_Johns|Regina|Montreal|Moncton|Glace_Bay|Iqaluit|Whitehorse|Yellowknife|Swift_Current|Goose_Bay|Dawson|Dawson_Creek|Fort_Nelson|Cambridge_Bay|Inuvik|Rankin_Inlet|Resolute|Atikokan|Blanc-Sablon)$/.test(tz)){d="amazon.ca";}
else if(/^(Europe\\/(Berlin|Busingen|Paris|Madrid|Rome|Amsterdam|Brussels|Luxembourg|Vienna|Warsaw|Prague|Bratislava|Budapest|Ljubljana|Zagreb|Lisbon|Dublin|Athens|Nicosia|Sofia|Bucharest|Helsinki|Stockholm|Copenhagen|Tallinn|Riga|Vilnius|Malta)|Atlantic\\/(Canary|Madeira|Azores))$/.test(tz)){d="amazon.de";}
var links=document.querySelectorAll("a[data-q]");
for(var i=0;i<links.length;i++){
  var q=links[i].getAttribute("data-q");
  links[i].setAttribute("href","https://www."+d+"/s?k="+encodeURIComponent(q).replace(/%20/g,"+")+"&tag="+C.tags[d]);
}
})();
"""

COUNTDOWN_JS = """
(function(){
var C=window.__CFG;
var target=C.unlock_utc?Date.parse(C.unlock_utc):new Date(C.target_local).getTime();
function p(n){return n<10?"0"+n:""+n;}
function $(id){return document.getElementById(id);}
try{$("tz").textContent=Intl.DateTimeFormat().resolvedOptions().timeZone;}catch(e){}
function fmt(tz){
  try{
    var o={dateStyle:"medium",timeStyle:"short"};
    if(tz){o.timeZone=tz;}
    return new Intl.DateTimeFormat(C.locale,o).format(new Date(target));
  }catch(e){return "";}
}
if(C.unlock_utc){
  var cells=document.querySelectorAll("td[data-tz]");
  for(var i=0;i<cells.length;i++){var s=fmt(cells[i].getAttribute("data-tz"));if(s){cells[i].textContent=s;}}
  var m=fmt();if(m){$("mine").textContent=m;}
}
function tick(){
  var d=target-Date.now();
  if(d<=0){$("cd").hidden=true;$("out").hidden=false;return;}
  var s=Math.floor(d/1000);
  var days=Math.floor(s/86400);s-=days*86400;
  var h=Math.floor(s/3600);s-=h*3600;
  var mi=Math.floor(s/60);s-=mi*60;
  $("cd0").textContent=days;$("cd1").textContent=p(h);$("cd2").textContent=p(mi);$("cd3").textContent=p(s);
  setTimeout(tick,1000);
}
tick();
})();
"""


def write(path, content):
    full = os.path.join("dist", path.lstrip("/"))
    if full.endswith("/"):
        full += "index.html"
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


def sitemap():
    urls = []
    for page in ("home", "hw"):
        for lang in LANG_ORDER:
            alts = "".join(
                f'<xhtml:link rel="alternate" hreflang="{l}" href="{SITE_URL}{path_for(l, page)}"/>'
                for l in LANG_ORDER
            )
            urls.append(f"<url><loc>{SITE_URL}{path_for(lang, page)}</loc>{alts}</url>")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
        + "".join(urls) + "</urlset>"
    )


def main():
    shutil.rmtree("dist", ignore_errors=True)
    for lang in LANG_ORDER:
        write(path_for(lang, "home"), home_page(lang))
        write(path_for(lang, "hw"), hw_page(lang))
    write("/sitemap.xml", sitemap())
    write("/robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    if os.path.isdir("static"):
        shutil.copytree("static", "dist", dirs_exist_ok=True)
    if GOOGLE_VERIFICATION_FILE:
        write("/" + GOOGLE_VERIFICATION_FILE, "google-site-verification: " + GOOGLE_VERIFICATION_FILE)
    pages = len(LANG_ORDER) * 2
    print(f"Built {pages} pages in ./dist")
    if "example.com" in SITE_URL:
        print("WARNING: SITE_URL is still example.com - set your domain before deploying.")
    if any(v.startswith("YOURTAG") for v in AFFILIATE_TAGS.values()):
        print("NOTE: stores with placeholder tags (YOURTAG-*) show no buy links until you set a real tag.")


if __name__ == "__main__":
    main()
