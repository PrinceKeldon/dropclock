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

# Game data lives in games.json (featured game, release date, unlock time, sources).
with open("games.json", encoding="utf-8") as _f:
    DATA = json.load(_f)
GAME = next(g for g in DATA["games"] if g["slug"] == DATA["featured"])
UNLOCK_UTC = GAME["unlock"].get("utc")        # set to e.g. "2026-11-19T05:00:00Z" once one official time exists
TARGET_LOCAL = GAME["unlock"]["local"]
SRC = {x["key"]: x for x in GAME["sources"]}
PAGES = ("home", "hw", "size", "help")

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


MONTHS = {
    "en": "January February March April May June July August September October November December".split(),
    "de": "Januar Februar März April Mai Juni Juli August September Oktober November Dezember".split(),
    "fr": "janvier février mars avril mai juin juillet août septembre octobre novembre décembre".split(),
    "es": "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split(),
    "it": "gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre".split(),
    "pl": "stycznia lutego marca kwietnia maja czerwca lipca sierpnia września października listopada grudnia".split(),
    "nl": "januari februari maart april mei juni juli augustus september oktober november december".split(),
    "ar": "يناير فبراير مارس أبريل مايو يونيو يوليو أغسطس سبتمبر أكتوبر نوفمبر ديسمبر".split(),
}
DATE_FMT = {
    "en": "{m} {d}, {y}", "de": "{d}. {m} {y}", "fr": "{d} {m} {y}", "es": "{d} de {m} de {y}",
    "it": "{d} {m} {y}", "pl": "{d} {m} {y}", "nl": "{d} {m} {y}", "ar": "{d} {m} {y}",
}


def fmt_date(lang, iso):
    y, m, d = (int(x) for x in iso.split("-"))
    return DATE_FMT[lang].format(d=d, m=MONTHS[lang][m - 1], y=y)


T = {
    "en": dict(
        title="{game} unlock time by city - countdown",
        desc="When does {game} unlock where you live? Countdown to {date} on PS5 and Xbox Series X|S.",
        h1="When does {game} unlock for you?",
        sub="Countdown to {date} for PS5 and Xbox Series X|S.",
        official="Official unlock time confirmed by Rockstar.",
        cd=["Days", "Hours", "Min", "Sec"], released="{game} is out!",
        local="Your local time", col_city="City", col_time="Unlock (local time)",
        assumed_cell="00:00", nav_hw="PS5 storage", nav_home="Countdown",
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
        title="{game} Freischaltzeit nach Stadt - Countdown",
        desc="Wann startet {game} bei dir? Countdown bis zum {date} für PS5 und Xbox Series X|S.",
        h1="Wann wird {game} für dich freigeschaltet?",
        sub="Countdown bis zum {date} für PS5 und Xbox Series X|S.",
        official="Offizielle Freischaltzeit von Rockstar bestätigt.",
        cd=["Tage", "Std.", "Min.", "Sek."], released="{game} ist da!",
        local="Deine Ortszeit", col_city="Stadt", col_time="Freischaltung (Ortszeit)",
        assumed_cell="00:00", nav_hw="PS5-Speicher", nav_home="Countdown",
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
        title="Heure de déblocage de {game} par ville - compte à rebours",
        desc="À quelle heure {game} se débloque chez toi ? Compte à rebours jusqu'au {date} sur PS5 et Xbox Series X|S.",
        h1="À quelle heure {game} se débloque-t-il chez toi ?",
        sub="Compte à rebours jusqu'au {date} sur PS5 et Xbox Series X|S.",
        official="Heure de déblocage officielle confirmée par Rockstar.",
        cd=["Jours", "Heures", "Min", "Sec"], released="{game} est disponible !",
        local="Ton heure locale", col_city="Ville", col_time="Déblocage (heure locale)",
        assumed_cell="00:00", nav_hw="Stockage PS5", nav_home="Compte à rebours",
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
        title="Hora de desbloqueo de {game} por ciudad - cuenta atrás",
        desc="¿A qué hora se desbloquea {game} donde vives? Cuenta atrás hasta el {date} en PS5 y Xbox Series X|S.",
        h1="¿Cuándo se desbloquea {game} donde vives?",
        sub="Cuenta atrás hasta el {date} en PS5 y Xbox Series X|S.",
        official="Hora de desbloqueo oficial confirmada por Rockstar.",
        cd=["Días", "Horas", "Min", "Seg"], released="¡{game} ya está aquí!",
        local="Tu hora local", col_city="Ciudad", col_time="Desbloqueo (hora local)",
        assumed_cell="00:00", nav_hw="Almacenamiento PS5", nav_home="Cuenta atrás",
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
        title="Orario di sblocco di {game} per città - conto alla rovescia",
        desc="A che ora si sblocca {game} da te? Conto alla rovescia fino al {date} su PS5 e Xbox Series X|S.",
        h1="Quando si sblocca {game} da te?",
        sub="Conto alla rovescia fino al {date} su PS5 e Xbox Series X|S.",
        official="Orario di sblocco ufficiale confermato da Rockstar.",
        cd=["Giorni", "Ore", "Min", "Sec"], released="{game} è uscito!",
        local="Il tuo orario locale", col_city="Città", col_time="Sblocco (ora locale)",
        assumed_cell="00:00", nav_hw="Archiviazione PS5", nav_home="Conto alla rovescia",
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
        title="Godzina odblokowania {game} według miasta - odliczanie",
        desc="O której odblokuje się {game} u Ciebie? Odliczanie do {date} na PS5 i Xbox Series X|S.",
        h1="Kiedy {game} odblokuje się u Ciebie?",
        sub="Odliczanie do {date} na PS5 i Xbox Series X|S.",
        official="Oficjalna godzina odblokowania potwierdzona przez Rockstar.",
        cd=["Dni", "Godz.", "Min", "Sek."], released="{game} już jest!",
        local="Twój czas lokalny", col_city="Miasto", col_time="Odblokowanie (czas lokalny)",
        assumed_cell="00:00", nav_hw="Pamięć PS5", nav_home="Odliczanie",
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
        title="Ontgrendeltijd van {game} per stad - aftelklok",
        desc="Hoe laat wordt {game} bij jou ontgrendeld? Aftellen naar {date} op PS5 en Xbox Series X|S.",
        h1="Wanneer wordt {game} bij jou ontgrendeld?",
        sub="Aftellen naar {date} op PS5 en Xbox Series X|S.",
        official="Officiële ontgrendeltijd bevestigd door Rockstar.",
        cd=["Dagen", "Uur", "Min", "Sec"], released="{game} is uit!",
        local="Jouw lokale tijd", col_city="Stad", col_time="Ontgrendeling (lokale tijd)",
        assumed_cell="00:00", nav_hw="PS5-opslag", nav_home="Aftellen",
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
        title="موعد فتح {game} حسب المدينة - العد التنازلي",
        desc="متى تُفتح {game} في مدينتك؟ عدّ تنازلي حتى {date} على PS5 وXbox Series X|S.",
        h1="متى تُفتح {game} في مدينتك؟",
        sub="عدّ تنازلي حتى {date} على PS5 وXbox Series X|S.",
        official="الموعد الرسمي للفتح مؤكَّد من Rockstar.",
        cd=["أيام", "ساعات", "دقائق", "ثوانٍ"], released="{game} متاحة الآن!",
        local="توقيتك المحلي", col_city="المدينة", col_time="الفتح (بالتوقيت المحلي)",
        assumed_cell="00:00", nav_hw="تخزين PS5", nav_home="العد التنازلي",
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

# Extra copy for the storage-size and download-help pages and the updated launch note.
# Placeholders: {game} {size} {date} (release date) {checked} (facts last checked).
T2 = {
    "en": dict(
        note="PlayStation says the launch rolls out at midnight local time, country by country, on {date}. Check your console's store page for your exact time. Xbox Series X|S timing may differ.",
        src_label="Sources",
        nav_size="{game} size", nav_help="Download help",
        size_title="How much storage does {game} need on PS5 and Xbox?",
        size_desc="Rockstar says {game} needs up to {size} GB of free space. What that means for PS5 and Xbox Series X|S, and what to do if you are short.",
        size_h1="How much storage does {game} need?",
        size_intro="Rockstar says the {game} pre-load needs up to {size} GB of free space, depending on your device.",
        size_points=["Plan for up to {size} GB of free space before you start the download.",
                     "The game is out on PS5 and Xbox Series X|S. Rockstar lists these two platforms.",
                     "Physical copies come as a download code in the box. There is no disc, so a physical copy does not save space.",
                     "Rockstar gives the figure as “up to”, so the exact size on your console can differ."],
        size_next_h="Not enough space?",
        size_next="Delete games you no longer play, or add storage. PS5 supports an M.2 NVMe SSD (requirements are in our storage guide). Xbox Series X|S needs its own expansion card.",
        help_title="{game} won't download? What Rockstar says to check",
        help_desc="A checklist built from Rockstar's official pre-load FAQ for PS5 and Xbox Series X|S.",
        help_h1="{game} won't download? Check these first",
        help_intro="These steps come from Rockstar's official pre-load FAQ. We have no fixes of our own, and we will add more only when official sources confirm them.",
        help_ps5_h="PS5",
        help_ps5=["Turn on auto-downloads.", "Leave the console on, or in Rest Mode.", "Free up to {size} GB of space.",
                  "If you bought a physical copy, redeem the code from the box. There is no disc."],
        help_xbox_h="Xbox Series X|S",
        help_xbox=["Turn on automatic updates.", "Leave the console on, or in Sleep mode.", "Free up to {size} GB of space.",
                   "If you bought a physical copy, redeem the code from the box. There is no disc."],
        help_more_h="Still stuck?",
        help_more="Rockstar's pre-load FAQ links to troubleshooting articles for each console, and its support team takes requests 24/7. Use the links below.",
        checked="Last checked: {checked}",
        src_note="We summarize official pages and may be out of date. Check the sources before you act.",
    ),
    "de": dict(
        note="Laut PlayStation startet das Spiel am {date} um Mitternacht Ortszeit, Land für Land. Prüfe die Store-Seite deiner Konsole für deine genaue Zeit. Auf Xbox Series X|S kann sie abweichen.",
        src_label="Quellen",
        nav_size="{game}-Größe", nav_help="Download-Hilfe",
        size_title="Wie viel Speicher braucht {game} auf PS5 und Xbox?",
        size_desc="Laut Rockstar braucht {game} bis zu {size} GB freien Speicher. Was das für PS5 und Xbox Series X|S bedeutet und was du bei Platzmangel tun kannst.",
        size_h1="Wie viel Speicher braucht {game}?",
        size_intro="Laut Rockstar braucht der Vorab-Download von {game} je nach Gerät bis zu {size} GB freien Speicher.",
        size_points=["Plane vor dem Download bis zu {size} GB freien Speicher ein.",
                     "Das Spiel ist für PS5 und Xbox Series X|S erschienen. Rockstar nennt diese beiden Plattformen.",
                     "Physische Kopien enthalten nur einen Download-Code, keine Disc. Du sparst dadurch also keinen Speicher.",
                     "Rockstar gibt den Wert als „bis zu“ an, die genaue Größe auf deiner Konsole kann daher abweichen."],
        size_next_h="Nicht genug Platz?",
        size_next="Lösche Spiele, die du nicht mehr spielst, oder erweitere den Speicher. Die PS5 unterstützt eine M.2-NVMe-SSD (Anforderungen in unserem Speicher-Ratgeber). Die Xbox Series X|S braucht eine eigene Speichererweiterungskarte.",
        help_title="{game} lädt nicht? Das empfiehlt Rockstar zu prüfen",
        help_desc="Eine Checkliste aus Rockstars offizieller Vorab-Download-FAQ für PS5 und Xbox Series X|S.",
        help_h1="{game} lädt nicht? Prüfe zuerst das",
        help_intro="Diese Schritte stammen aus Rockstars offizieller Vorab-Download-FAQ. Eigene Lösungen haben wir nicht und ergänzen weitere nur, wenn offizielle Quellen sie bestätigen.",
        help_ps5_h="PS5",
        help_ps5=["Aktiviere automatische Downloads.", "Lass die Konsole eingeschaltet oder im Ruhemodus.", "Gib bis zu {size} GB Speicher frei.",
                  "Bei einer physischen Kopie löst du den Code aus der Verpackung ein. Es gibt keine Disc."],
        help_xbox_h="Xbox Series X|S",
        help_xbox=["Aktiviere automatische Updates.", "Lass die Konsole eingeschaltet oder im Energiesparmodus.", "Gib bis zu {size} GB Speicher frei.",
                   "Bei einer physischen Kopie löst du den Code aus der Verpackung ein. Es gibt keine Disc."],
        help_more_h="Immer noch Probleme?",
        help_more="Rockstars Vorab-Download-FAQ verlinkt Fehlerbehebungs-Artikel für jede Konsole, und der Support nimmt Anfragen rund um die Uhr entgegen. Nutze die Links unten.",
        checked="Zuletzt geprüft: {checked}",
        src_note="Wir fassen offizielle Seiten zusammen und können veraltet sein. Prüfe die Quellen, bevor du handelst.",
    ),
    "fr": dict(
        note="Selon PlayStation, le jeu se débloque à minuit, heure locale, pays par pays, le {date}. Consulte la page du store de ta console pour ton heure exacte. Sur Xbox Series X|S, elle peut différer.",
        src_label="Sources",
        nav_size="Taille de {game}", nav_help="Aide au téléchargement",
        size_title="De combien d'espace {game} a-t-il besoin sur PS5 et Xbox ?",
        size_desc="Rockstar indique jusqu'à {size} Go d'espace libre pour {game}. Ce que cela signifie pour PS5 et Xbox Series X|S, et que faire s'il manque de la place.",
        size_h1="De combien d'espace {game} a-t-il besoin ?",
        size_intro="Selon Rockstar, le préchargement de {game} demande jusqu'à {size} Go d'espace libre, selon ton appareil.",
        size_points=["Prévois jusqu'à {size} Go d'espace libre avant de lancer le téléchargement.",
                     "Le jeu est sorti sur PS5 et Xbox Series X|S. Rockstar indique ces deux plateformes.",
                     "Les copies physiques contiennent un code de téléchargement, pas de disque. Elles ne font donc pas gagner d'espace.",
                     "Rockstar donne ce chiffre comme un maximum (« jusqu'à »), la taille exacte sur ta console peut donc différer."],
        size_next_h="Pas assez de place ?",
        size_next="Supprime les jeux auxquels tu ne joues plus ou ajoute du stockage. La PS5 accepte un SSD M.2 NVMe (exigences dans notre guide de stockage). La Xbox Series X|S a besoin de sa propre carte d'extension.",
        help_title="{game} ne se télécharge pas ? Ce que Rockstar conseille de vérifier",
        help_desc="Une liste de vérifications tirée de la FAQ officielle de Rockstar sur le préchargement, pour PS5 et Xbox Series X|S.",
        help_h1="{game} ne se télécharge pas ? Vérifie d'abord ceci",
        help_intro="Ces étapes viennent de la FAQ officielle de Rockstar sur le préchargement. Nous n'avons pas de solutions à nous et n'en ajouterons que si des sources officielles les confirment.",
        help_ps5_h="PS5",
        help_ps5=["Active les téléchargements automatiques.", "Laisse la console allumée ou en mode repos.", "Libère jusqu'à {size} Go d'espace.",
                  "Si tu as une copie physique, active le code fourni dans la boîte. Il n'y a pas de disque."],
        help_xbox_h="Xbox Series X|S",
        help_xbox=["Active les mises à jour automatiques.", "Laisse la console allumée ou en veille.", "Libère jusqu'à {size} Go d'espace.",
                   "Si tu as une copie physique, active le code fourni dans la boîte. Il n'y a pas de disque."],
        help_more_h="Toujours bloqué ?",
        help_more="La FAQ de Rockstar renvoie vers des articles de dépannage pour chaque console, et son support répond aux demandes 24 h/24. Utilise les liens ci-dessous.",
        checked="Dernière vérification : {checked}",
        src_note="Nous résumons des pages officielles et nos informations peuvent être périmées. Vérifie les sources avant d'agir.",
    ),
    "es": dict(
        note="Según PlayStation, el juego se desbloquea a medianoche, hora local, país por país, el {date}. Consulta la página de la tienda de tu consola para saber tu hora exacta. En Xbox Series X|S puede variar.",
        src_label="Fuentes",
        nav_size="Tamaño de {game}", nav_help="Ayuda con la descarga",
        size_title="¿Cuánto espacio necesita {game} en PS5 y Xbox?",
        size_desc="Rockstar indica hasta {size} GB de espacio libre para {game}. Qué significa para PS5 y Xbox Series X|S y qué hacer si te falta espacio.",
        size_h1="¿Cuánto espacio necesita {game}?",
        size_intro="Según Rockstar, la precarga de {game} necesita hasta {size} GB de espacio libre, según tu dispositivo.",
        size_points=["Prepara hasta {size} GB de espacio libre antes de empezar la descarga.",
                     "El juego ya está disponible en PS5 y Xbox Series X|S. Rockstar indica estas dos plataformas.",
                     "Las copias físicas incluyen un código de descarga, no un disco. Por eso no ahorran espacio.",
                     "Rockstar da la cifra como «hasta», así que el tamaño exacto en tu consola puede variar."],
        size_next_h="¿No tienes espacio suficiente?",
        size_next="Borra juegos que ya no uses o amplía el almacenamiento. La PS5 admite un SSD M.2 NVMe (requisitos en nuestra guía de almacenamiento). La Xbox Series X|S necesita su propia tarjeta de expansión.",
        help_title="¿{game} no se descarga? Qué recomienda revisar Rockstar",
        help_desc="Una lista de comprobación basada en las preguntas frecuentes oficiales de Rockstar sobre la precarga, para PS5 y Xbox Series X|S.",
        help_h1="¿{game} no se descarga? Revisa esto primero",
        help_intro="Estos pasos salen de las preguntas frecuentes oficiales de Rockstar sobre la precarga. No tenemos soluciones propias y solo añadiremos más cuando fuentes oficiales las confirmen.",
        help_ps5_h="PS5",
        help_ps5=["Activa las descargas automáticas.", "Deja la consola encendida o en modo reposo.", "Libera hasta {size} GB de espacio.",
                  "Si compraste una copia física, canjea el código de la caja. No hay disco."],
        help_xbox_h="Xbox Series X|S",
        help_xbox=["Activa las actualizaciones automáticas.", "Deja la consola encendida o en modo suspensión.", "Libera hasta {size} GB de espacio.",
                   "Si compraste una copia física, canjea el código de la caja. No hay disco."],
        help_more_h="¿Sigues atascado?",
        help_more="Las preguntas frecuentes de Rockstar enlazan a artículos de solución de problemas para cada consola, y su soporte atiende solicitudes las 24 horas. Usa los enlaces de abajo.",
        checked="Última comprobación: {checked}",
        src_note="Resumimos páginas oficiales y la información puede estar desactualizada. Comprueba las fuentes antes de actuar.",
    ),
    "it": dict(
        note="Secondo PlayStation, il gioco si sblocca a mezzanotte ora locale, paese per paese, il {date}. Controlla la pagina dello store della tua console per l'orario esatto. Su Xbox Series X|S potrebbe essere diverso.",
        src_label="Fonti",
        nav_size="Dimensioni di {game}", nav_help="Aiuto con il download",
        size_title="Quanto spazio serve a {game} su PS5 e Xbox?",
        size_desc="Rockstar indica fino a {size} GB di spazio libero per {game}. Cosa significa per PS5 e Xbox Series X|S e cosa fare se manca spazio.",
        size_h1="Quanto spazio serve a {game}?",
        size_intro="Secondo Rockstar, il pre-caricamento di {game} richiede fino a {size} GB di spazio libero, a seconda del dispositivo.",
        size_points=["Prevedi fino a {size} GB di spazio libero prima di avviare il download.",
                     "Il gioco è uscito su PS5 e Xbox Series X|S. Rockstar indica queste due piattaforme.",
                     "Le copie fisiche contengono un codice di download, non un disco. Quindi non fanno risparmiare spazio.",
                     "Rockstar indica il valore come «fino a», perciò la dimensione esatta sulla tua console può variare."],
        size_next_h="Spazio insufficiente?",
        size_next="Elimina i giochi che non usi più o aggiungi memoria. La PS5 supporta un SSD M.2 NVMe (requisiti nella nostra guida all'archiviazione). La Xbox Series X|S richiede una propria scheda di espansione.",
        help_title="{game} non si scarica? Cosa consiglia di controllare Rockstar",
        help_desc="Una checklist basata sulle FAQ ufficiali di Rockstar sul pre-caricamento, per PS5 e Xbox Series X|S.",
        help_h1="{game} non si scarica? Controlla prima questo",
        help_intro="Questi passaggi vengono dalle FAQ ufficiali di Rockstar sul pre-caricamento. Non abbiamo soluzioni nostre e ne aggiungeremo altre solo se fonti ufficiali le confermano.",
        help_ps5_h="PS5",
        help_ps5=["Attiva i download automatici.", "Lascia la console accesa o in modalità riposo.", "Libera fino a {size} GB di spazio.",
                  "Se hai una copia fisica, riscatta il codice nella confezione. Non c'è il disco."],
        help_xbox_h="Xbox Series X|S",
        help_xbox=["Attiva gli aggiornamenti automatici.", "Lascia la console accesa o in modalità sospensione.", "Libera fino a {size} GB di spazio.",
                   "Se hai una copia fisica, riscatta il codice nella confezione. Non c'è il disco."],
        help_more_h="Sei ancora bloccato?",
        help_more="Le FAQ di Rockstar rimandano ad articoli di risoluzione dei problemi per ogni console e il supporto accetta richieste 24 ore su 24. Usa i link qui sotto.",
        checked="Ultimo controllo: {checked}",
        src_note="Riassumiamo pagine ufficiali e le informazioni potrebbero essere superate. Controlla le fonti prima di agire.",
    ),
    "pl": dict(
        note="Według PlayStation gra odblokowuje się o północy czasu lokalnego, kraj po kraju, {date}. Sprawdź stronę sklepu na swojej konsoli, aby poznać dokładną godzinę. Na Xbox Series X|S może być inaczej.",
        src_label="Źródła",
        nav_size="Rozmiar {game}", nav_help="Pomoc z pobieraniem",
        size_title="Ile miejsca potrzebuje {game} na PS5 i Xbox?",
        size_desc="Rockstar podaje do {size} GB wolnego miejsca dla {game}. Co to oznacza dla PS5 i Xbox Series X|S i co zrobić, gdy brakuje miejsca.",
        size_h1="Ile miejsca potrzebuje {game}?",
        size_intro="Według Rockstar przedpobranie {game} wymaga do {size} GB wolnego miejsca, w zależności od urządzenia.",
        size_points=["Przygotuj do {size} GB wolnego miejsca, zanim zaczniesz pobieranie.",
                     "Gra jest dostępna na PS5 i Xbox Series X|S. Rockstar wymienia te dwie platformy.",
                     "Wersje pudełkowe zawierają kod do pobrania, a nie płytę. Nie oszczędzają więc miejsca.",
                     "Rockstar podaje wartość jako „do”, więc dokładny rozmiar na Twojej konsoli może się różnić."],
        size_next_h="Za mało miejsca?",
        size_next="Usuń gry, w które już nie grasz, lub dodaj pamięć. PS5 obsługuje dysk M.2 NVMe SSD (wymagania w naszym poradniku o pamięci). Xbox Series X|S wymaga własnej karty rozszerzenia.",
        help_title="{game} się nie pobiera? Co radzi sprawdzić Rockstar",
        help_desc="Lista kontrolna oparta na oficjalnym FAQ Rockstar o przedpobraniu, dla PS5 i Xbox Series X|S.",
        help_h1="{game} się nie pobiera? Sprawdź najpierw to",
        help_intro="Te kroki pochodzą z oficjalnego FAQ Rockstar o przedpobraniu. Nie mamy własnych rozwiązań i dodamy kolejne tylko wtedy, gdy potwierdzą je oficjalne źródła.",
        help_ps5_h="PS5",
        help_ps5=["Włącz automatyczne pobieranie.", "Zostaw konsolę włączoną lub w trybie spoczynku.", "Zwolnij do {size} GB miejsca.",
                  "Jeśli masz wersję pudełkową, zrealizuj kod z pudełka. Płyty nie ma."],
        help_xbox_h="Xbox Series X|S",
        help_xbox=["Włącz automatyczne aktualizacje.", "Zostaw konsolę włączoną lub w trybie uśpienia.", "Zwolnij do {size} GB miejsca.",
                   "Jeśli masz wersję pudełkową, zrealizuj kod z pudełka. Płyty nie ma."],
        help_more_h="Nadal nie działa?",
        help_more="FAQ Rockstar odsyła do artykułów z rozwiązywaniem problemów dla każdej konsoli, a pomoc techniczna przyjmuje zgłoszenia całą dobę. Skorzystaj z linków poniżej.",
        checked="Ostatnio sprawdzono: {checked}",
        src_note="Streszczamy oficjalne strony i informacje mogą być nieaktualne. Sprawdź źródła, zanim coś zrobisz.",
    ),
    "nl": dict(
        note="Volgens PlayStation wordt het spel op {date} om middernacht lokale tijd ontgrendeld, land voor land. Bekijk de storepagina van je console voor je exacte tijd. Op Xbox Series X|S kan die afwijken.",
        src_label="Bronnen",
        nav_size="Grootte van {game}", nav_help="Downloadhulp",
        size_title="Hoeveel opslag heeft {game} nodig op PS5 en Xbox?",
        size_desc="Rockstar noemt tot {size} GB vrije ruimte voor {game}. Wat dat betekent voor PS5 en Xbox Series X|S en wat je kunt doen bij te weinig ruimte.",
        size_h1="Hoeveel opslag heeft {game} nodig?",
        size_intro="Volgens Rockstar heeft het vooraf downloaden van {game} tot {size} GB vrije ruimte nodig, afhankelijk van je apparaat.",
        size_points=["Reken op tot {size} GB vrije ruimte voordat je de download start.",
                     "Het spel is uit voor PS5 en Xbox Series X|S. Rockstar noemt deze twee platforms.",
                     "Fysieke exemplaren bevatten een downloadcode, geen disc. Ze besparen dus geen ruimte.",
                     "Rockstar geeft de waarde als “tot”, dus de exacte grootte op jouw console kan verschillen."],
        size_next_h="Te weinig ruimte?",
        size_next="Verwijder games die je niet meer speelt of voeg opslag toe. De PS5 ondersteunt een M.2 NVMe-SSD (eisen in onze opslaggids). De Xbox Series X|S heeft een eigen uitbreidingskaart nodig.",
        help_title="Wil {game} niet downloaden? Dit raadt Rockstar aan te controleren",
        help_desc="Een checklist op basis van Rockstars officiële veelgestelde vragen over vooraf downloaden, voor PS5 en Xbox Series X|S.",
        help_h1="Wil {game} niet downloaden? Controleer eerst dit",
        help_intro="Deze stappen komen uit Rockstars officiële veelgestelde vragen over vooraf downloaden. We hebben geen eigen oplossingen en voegen er alleen meer toe als officiële bronnen ze bevestigen.",
        help_ps5_h="PS5",
        help_ps5=["Zet automatische downloads aan.", "Laat de console aan staan of in rustmodus.", "Maak tot {size} GB ruimte vrij.",
                  "Heb je een fysiek exemplaar? Verzilver dan de code uit de doos. Er zit geen disc in."],
        help_xbox_h="Xbox Series X|S",
        help_xbox=["Zet automatische updates aan.", "Laat de console aan staan of in slaapstand.", "Maak tot {size} GB ruimte vrij.",
                   "Heb je een fysiek exemplaar? Verzilver dan de code uit de doos. Er zit geen disc in."],
        help_more_h="Nog steeds vast?",
        help_more="De veelgestelde vragen van Rockstar verwijzen naar probleemoplossingsartikelen per console, en de support neemt dag en nacht verzoeken aan. Gebruik de links hieronder.",
        checked="Laatst gecontroleerd: {checked}",
        src_note="We vatten officiële pagina's samen en kunnen achterlopen. Controleer de bronnen voordat je iets doet.",
    ),
    "ar": dict(
        note="وفقًا لـ PlayStation، تُفتح اللعبة عند منتصف الليل بالتوقيت المحلي، دولة بعد أخرى، في {date}. راجع صفحة المتجر على جهازك لمعرفة وقتك الدقيق. قد يختلف الوقت على Xbox Series X|S.",
        src_label="المصادر",
        nav_size="حجم {game}", nav_help="مساعدة التنزيل",
        size_title="كم من المساحة تحتاج {game} على PS5 وXbox؟",
        size_desc="تذكر Rockstar أن {game} تحتاج إلى ما يصل إلى {size} غيغابايت من المساحة الحرة. ماذا يعني ذلك لجهازي PS5 وXbox Series X|S وماذا تفعل إذا كانت المساحة غير كافية.",
        size_h1="كم من المساحة تحتاج {game}؟",
        size_intro="تذكر Rockstar أن التحميل المسبق لـ {game} يحتاج إلى ما يصل إلى {size} غيغابايت من المساحة الحرة، حسب جهازك.",
        size_points=["جهّز ما يصل إلى {size} غيغابايت من المساحة الحرة قبل بدء التنزيل.",
                     "اللعبة متاحة على PS5 وXbox Series X|S. هاتان هما المنصتان اللتان تذكرهما Rockstar.",
                     "تحتوي النسخ الفعلية على رمز تنزيل وليس قرصًا، لذلك لا توفر أي مساحة.",
                     "تذكر Rockstar الرقم على أنه «حتى»، لذلك قد يختلف الحجم الدقيق على جهازك."],
        size_next_h="المساحة غير كافية؟",
        size_next="احذف الألعاب التي لم تعد تلعبها أو أضف مساحة تخزين. يدعم PS5 قرص M.2 NVMe SSD (المتطلبات في دليل التخزين لدينا). أما Xbox Series X|S فيحتاج إلى بطاقة توسعة خاصة به.",
        help_title="لا يتم تنزيل {game}؟ ما تنصح Rockstar بالتحقق منه",
        help_desc="قائمة تحقق مبنية على الأسئلة الشائعة الرسمية من Rockstar حول التحميل المسبق، لجهازي PS5 وXbox Series X|S.",
        help_h1="لا يتم تنزيل {game}؟ تحقق من هذا أولًا",
        help_intro="هذه الخطوات مأخوذة من الأسئلة الشائعة الرسمية من Rockstar حول التحميل المسبق. ليست لدينا حلول خاصة بنا، ولن نضيف المزيد إلا إذا أكدته مصادر رسمية.",
        help_ps5_h="PS5",
        help_ps5=["فعّل التنزيلات التلقائية.", "اترك الجهاز قيد التشغيل أو في وضع الراحة (Rest Mode).", "وفّر ما يصل إلى {size} غيغابايت من المساحة.",
                  "إذا اشتريت نسخة فعلية، فعّل الرمز الموجود في العلبة. لا يوجد قرص."],
        help_xbox_h="Xbox Series X|S",
        help_xbox=["فعّل التحديثات التلقائية.", "اترك الجهاز قيد التشغيل أو في وضع السكون (Sleep).", "وفّر ما يصل إلى {size} غيغابايت من المساحة.",
                   "إذا اشتريت نسخة فعلية، فعّل الرمز الموجود في العلبة. لا يوجد قرص."],
        help_more_h="ما زالت المشكلة قائمة؟",
        help_more="تحيل الأسئلة الشائعة من Rockstar إلى مقالات استكشاف الأخطاء لكل جهاز، ويستقبل فريق الدعم الطلبات على مدار الساعة. استخدم الروابط أدناه.",
        checked="آخر تحقق: {checked}",
        src_note="نلخّص صفحات رسمية وقد تكون المعلومات قديمة. تحقق من المصادر قبل التصرف.",
    ),
}


for _lang, _extra in T2.items():
    T[_lang].update(_extra)


def _finalize_texts():
    for lang, t in T.items():
        subs = {
            "{game}": GAME["name"],
            "{size}": str(GAME.get("storage_gb", "")),
            "{date}": fmt_date(lang, GAME["release_date"]),
            "{checked}": fmt_date(lang, GAME["facts_checked"]),
        }

        def apply(v):
            for k, val in subs.items():
                v = v.replace(k, val)
            return v

        for k, v in list(t.items()):
            if isinstance(v, str):
                t[k] = apply(v)
            elif isinstance(v, list):
                t[k] = [apply(x) if isinstance(x, str) else x for x in v]


_finalize_texts()

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
nav{display:flex;flex-wrap:wrap;gap:4px 0}
nav a,.langs a{color:var(--mut);text-decoration:none;margin-inline-end:16px;white-space:nowrap}
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
    if page == "home":
        return base
    if page == "hw":
        return f"{base}ps5-storage/"
    if page == "size":
        return f"{base}{GAME['slug']}/storage/"
    return f"{base}{GAME['slug']}/help/"


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
        f'<a href="{path_for(lang, "size")}"{" class=on" if page == "size" else ""}>{escape(t["nav_size"])}</a>'
        f'<a href="{path_for(lang, "help")}"{" class=on" if page == "help" else ""}>{escape(t["nav_help"])}</a>'
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


def sources_block(lang, keys):
    t = T[lang]
    items = "".join(
        f'<li><a href="{escape(SRC[k]["url"])}" rel="noopener" target="_blank">{escape(SRC[k]["title"])}</a></li>'
        for k in keys
    )
    return (
        f'<h2>{escape(t["src_label"])}</h2><ul class="specs">{items}</ul>'
        f'<p class="small">{escape(t["checked"])}. {escape(t["src_note"])}</p>'
    )


def size_page(lang):
    t = T[lang]
    pts = "".join(f"<li>{escape(x)}</li>" for x in t["size_points"])
    body = f"""
<h1>{escape(t["size_h1"])}</h1>
<p class="sub">{escape(t["size_intro"])}</p>
<ul class="specs">{pts}</ul>
<h2>{escape(t["size_next_h"])}</h2>
<p>{escape(t["size_next"])}</p>
<div class="btns"><a class="btn" href="{path_for(lang, "hw")}">{escape(t["nav_hw"])}</a></div>
{sources_block(lang, ["rockstar_preload", "rockstar_platforms"])}
"""
    return layout(lang, "size", t["size_title"], t["size_desc"], body)


def help_page(lang):
    t = T[lang]
    ps5 = "".join(f"<li>{escape(x)}</li>" for x in t["help_ps5"])
    xbox = "".join(f"<li>{escape(x)}</li>" for x in t["help_xbox"])
    body = f"""
<h1>{escape(t["help_h1"])}</h1>
<p class="sub">{escape(t["help_intro"])}</p>
<h2>{escape(t["help_ps5_h"])}</h2>
<ul class="specs">{ps5}</ul>
<h2>{escape(t["help_xbox_h"])}</h2>
<ul class="specs">{xbox}</ul>
<h2>{escape(t["help_more_h"])}</h2>
<p>{escape(t["help_more"])}</p>
{sources_block(lang, ["rockstar_preload", "rockstar_platforms"])}
"""
    return layout(lang, "help", t["help_title"], t["help_desc"], body)


def home_page(lang):
    t = T[lang]
    status = t["official"] if UNLOCK_UTC else t["note"]
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
<div class="btns">
<a class="btn" href="{path_for(lang, "size")}">{escape(t["nav_size"])}</a>
<a class="btn" href="{path_for(lang, "help")}">{escape(t["nav_help"])}</a>
<a class="btn" href="{path_for(lang, "hw")}">{escape(t["nav_hw"])}</a>
</div>
<p class="small">{escape(t["local"])}: <b id="mine">{escape(t["assumed_cell"])}</b> &middot; {escape(t["tzlabel"])}: <span id="tz">-</span></p>
<table>
<thead><tr><th>{escape(t["col_city"])}</th><th>{escape(t["col_time"])}</th></tr></thead>
<tbody>{rows}</tbody>
</table>
{sources_block(lang, ["playstation_blog"])}
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
    for page in PAGES:
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
        write(path_for(lang, "size"), size_page(lang))
        write(path_for(lang, "help"), help_page(lang))
    write("/sitemap.xml", sitemap())
    write("/robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    if os.path.isdir("static"):
        shutil.copytree("static", "dist", dirs_exist_ok=True)
    if GOOGLE_VERIFICATION_FILE:
        write("/" + GOOGLE_VERIFICATION_FILE, "google-site-verification: " + GOOGLE_VERIFICATION_FILE)
    pages = len(LANG_ORDER) * len(PAGES)
    print(f"Built {pages} pages in ./dist")
    if "example.com" in SITE_URL:
        print("WARNING: SITE_URL is still example.com - set your domain before deploying.")
    if any(v.startswith("YOURTAG") for v in AFFILIATE_TAGS.values()):
        print("NOTE: stores with placeholder tags (YOURTAG-*) show no buy links until you set a real tag.")


if __name__ == "__main__":
    main()
