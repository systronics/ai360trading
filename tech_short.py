"""
tech_short.py v1.0 (2026-11-01) — Hindi "how everyday technology works" Shorts (NEW channel/page line, NOT the trading channel).

Owner brief 2026-11-01: real, animated explainers that hold the public: shock question in the first 3 seconds, an easy
analogy, then a one-line takeaway / next-video hook. 5 scenes, each a Pillow-animated diagram (thermometer, particles
through a chip, bars, battery, tick cards) + natural spoken Hindi (hand-written, fact-checked) + loudness-normalised voice
+ a soft whoosh on every scene change. On-screen words are Roman (Hinglish) so every font renders.

SAMPLE ONLY for now: `python tech_short.py --sample phone_heat` writes to output/tech/. It never uploads; wiring to a
channel/page is a separate owner-approved step (the new channel + page do not exist yet).
"""
import os
import sys
import json
import math
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import emotion_story as E

W, H, FPS = 1080, 1920, 24
CHANNEL_HANDLE = os.environ.get("TECH_HANDLE", "")   # e.g. "@YourChannel"; empty until the owner has the new channel
SPOKEN_CTA = " फ़ॉलो ज़रूर करना।"
BG_TOP, BG_BOT = (10, 14, 32), (22, 30, 64)
WHITE, GOLD, MUTED = (255, 255, 255), (255, 200, 50), (170, 180, 205)
RED, ORANGE, BLUE, GREEN, CYAN = (255, 80, 70), (255, 150, 40), (90, 160, 255), (0, 210, 120), (70, 220, 240)

# ───────────────────────────── topics (hand-written, facts checked) ───────────────────────────────
TOPICS = {
    "phone_heat": {
        "title": "Phone Hot Kyun Hota Hai?",
        "yt_title": "Phone Hot Kyun Hota Hai? Asli Reason #shorts",
        "thumb": ("PHONE HOT", "KYUN?"), "thumb_hi": "फोन गर्म क्यों होता है?", "thumb_sub": "ASLI WAJAH + 3 TIPS",
        "thumb_long": "CHARGING MEIN PHONE ITNA GARAM KYUN HOTA HAI? ASLI REASON",
        "thumb_hot": "GARAM",
        "tag": "HOW IT WORKS",
        "tags": ["phone hot kyun hota hai", "phone heating problem", "mobile heat hinglish", "tech explained hinglish", "how it works hinglish", "shorts"],
        "lines": [
            "आपका फ़ोन चार्ज करते टाइम इतना हॉट क्यों हो जाता है? चलो, अंदर देखते हैं।",
            "फ़ोन की चिप में करंट पतले वायर से गुज़रता है, और वायर उसे थोड़ा रोकते हैं। जैसे भीड़ वाली गली में धक्का-मुक्की होती है ना, वैसे ही करंट में फ़्रिक्शन होता है, और वही हीट बन जाता है।",
            "गेम खेलते हो तो चिप फ़ुल स्पीड पर चलती है। ज़्यादा काम, ज़्यादा करंट, ज़्यादा हीट।",
            "चार्जिंग में भी यही होता है। बैटरी भरते टाइम कुछ करंट हीट बनकर निकल जाता है, और फ़ास्ट चार्जर में ज़्यादा।",
            "तो धूप में चार्ज मत करो, मोटा कवर निकाल दो, और चार्जिंग में हैवी गेम मत खेलो। सीधी बात, हीट मतलब करंट की धक्का-मुक्की। अगली बार, बैटरी जल्दी क्यों ख़त्म होती है।",
        ],
        "caps": ["PHONE HOT KYUN HOTA HAI?", "CURRENT + FRICTION = HEAT", "ZYADA KAAM = ZYADA HEAT", "CHARGING MEIN BHI HEAT", "HEAT = FRICTION"],
        "scenes": ["thermo", "chip", "bars", "battery", "tips"],
        "queries": [["hand holding smartphone close up", "smartphone screen hand"], ["circuit board macro close up", "electronic circuit board"],
                    ["hands playing mobile game", "gaming on smartphone close up"], ["phone charging on wooden table", "smartphone plugged in charger"],
                    ["smartphone on wooden table", "sunlight on desk window"]],
        "tips": ["DHOOP MEIN CHARGE MAT KARO", "COVER NIKAAL DO", "CHARGING + GAME MAT KHELO"],
    },
}

def _more_topics():
    T = TOPICS
    T["wifi_slow"] = {
        "title": "WiFi Slow Kyun Chalta Hai?", "yt_title": "WiFi Slow Kyun Chalta Hai? Asli Reason #shorts", "tag": "ROZ KI TECH",
        "thumb": ("WIFI SLOW", "KYUN?"), "thumb_hi": "WiFi स्लो क्यों चलता है?", "thumb_sub": "ASLI WAJAH + FIX", "thumb_long": "WIFI KABHI KABHI ITNA SLOW KYUN HO JATA HAI? ASLI REASON", "thumb_hot": "SLOW",
        "tags": ["wifi slow kyun chalta hai", "wifi speed kaise badhaye", "router problem hinglish", "tech explained hinglish", "shorts"],
        "lines": [
            "आपका WiFi कभी-कभी इतना स्लो क्यों हो जाता है? पता है असली वजह?",
            "WiFi एक रेडियो सिग्नल है, और दीवारें, ख़ासकर मोटी दीवारें, उसे कमज़ोर कर देती हैं। जैसे दीवार के पीछे से कोई आवाज़ दे, तो आवाज़ धीमी पहुँचती है, वैसे ही।",
            "दूसरी वजह भीड़ है। जितने ज़्यादा फ़ोन, टीवी और लैपटॉप जुड़ेंगे, स्पीड उतनों में बँट जाएगी, जैसे एक पाइप से कई नल चलाओ।",
            "और पड़ोसियों के WiFi भी टकरा सकते हैं, ख़ासकर टू पॉइंट फ़ोर गीगाहर्ट्ज़ पर। फ़ाइव गीगाहर्ट्ज़ तेज़ है, पर दीवार पार करने में कमज़ोर।",
            "तो राउटर खुली, ऊँची जगह रखो, और पास में हो तो फ़ाइव गीगाहर्ट्ज़ चुनो। सीधी बात, दीवार और भीड़ स्पीड खाते हैं। अगली बार, राउटर की लाइट का मतलब।",
        ],
        "caps": ["WIFI SLOW KYUN?", "DEEVAR SIGNAL KHATI HAI", "BHEED = SPEED KAM", "PADOSI KA WIFI BHI", "DEEVAR + BHEED = SLOW"],
        "scenes": [{"type": "card", "lines": ["WIFI SLOW?", "ASLI WAJAH"], "color": "red"},
                   {"type": "bars2", "rows": [("SIGNAL: KHULI JAGAH", 0.95, "green"), ("SIGNAL: MOTI DEEVAR KE PAAR", 0.35, "red")]},
                   {"type": "bars2", "rows": [("SPEED: 1 DEVICE", 0.95, "green"), ("SPEED: BAHUT DEVICE", 0.3, "red")]},
                   {"type": "bars2", "rows": [("2.4 GHZ: DOOR TAK, BHEED", 0.6, "orange"), ("5 GHZ: TEZ, DEEVAR MEIN KAMZOR", 0.85, "blue")]},
                   {"type": "tips", "items": ["ROUTER KHULI, UNCHI JAGAH", "PAAS MEIN 5 GHZ CHUNO", "BEKAAR DEVICE HATAO"]}],
        "queries": [["wifi router close up", "wifi router on shelf"], ["brick wall close up", "concrete wall texture"],
                    ["smartphones on table", "many devices laptop phone table"], ["router blinking lights", "router antennas close up"],
                    ["router on shelf living room", "hand holding smartphone"]]}
    T["laptop_hang"] = {
        "title": "Laptop Hang Kyun Hota Hai?", "yt_title": "Laptop Hang Kyun Hota Hai? Asli Wajah #shorts", "tag": "ROZ KI TECH",
        "thumb": ("LAPTOP HANG", "KYUN?"), "thumb_hi": "लैपटॉप हैंग क्यों होता है?", "thumb_sub": "ASLI WAJAH + FIX", "thumb_long": "LAPTOP BAAR BAAR HANG KYUN HOTA HAI? ASLI REASON", "thumb_hot": "HANG",
        "tags": ["laptop hang kyun hota hai", "laptop slow problem", "computer slow hinglish", "tech explained hinglish", "shorts"],
        "lines": [
            "आपका लैपटॉप बार-बार हैंग क्यों हो जाता है? चलो, वजह समझते हैं।",
            "लैपटॉप में RAM एक छोटी मेज़ की तरह है, जिस पर चल रहे सारे ऐप्स का काम रखा जाता है। मेज़ भर जाए, तो सब कुछ धीमा हो जाता है।",
            "जब RAM कम पड़ती है, तो सिस्टम काम को हार्ड डिस्क पर रखने लगता है, और हार्ड डिस्क, ख़ासकर पुरानी वाली, RAM से बहुत धीमी होती है। बस यहीं से हैंग शुरू होता है।",
            "ऊपर से बैकग्राउंड में चलते ऐप्स और ब्राउज़र के ढेर सारे टैब भी RAM खा जाते हैं।",
            "तो बेकार टैब बंद करो, स्टार्टअप ऐप्स कम करो, और हो सके तो हार्ड डिस्क की जगह SSD लगवाओ। सीधी बात, RAM की मेज़ भरी तो लैपटॉप हाँफता है। अगली बार बताऊँगा, कंप्यूटर ऑन क्यों नहीं होता।",
        ],
        "caps": ["LAPTOP HANG KYUN?", "RAM = CHHOTI MEZ", "RAM KAM = DISK PAR KAAM", "TAB + APPS = RAM KHATAM", "TAB BAND KARO, SSD LAGAO"],
        "scenes": [{"type": "card", "lines": ["LAPTOP HANG?", "ASLI WAJAH"], "color": "red"},
                   {"type": "bars2", "rows": [("RAM: KHALI", 0.2, "green"), ("RAM: BHARI HUI", 0.95, "red")]},
                   {"type": "bars2", "rows": [("RAM SPEED", 0.95, "green"), ("HARD DISK SPEED", 0.2, "red")]},
                   {"type": "bars2", "rows": [("BROWSER TABS", 0.9, "orange"), ("BACKGROUND APPS", 0.7, "orange")]},
                   {"type": "tips", "items": ["BEKAAR TAB BAND KARO", "STARTUP APPS KAM KARO", "HARD DISK KI JAGAH SSD"]}],
        "queries": [["laptop screen loading close up", "hands typing laptop"], ["computer memory ram close up", "ram module close up"],
                    ["hard disk drive close up", "computer hard drive"], ["browser tabs laptop screen", "laptop screen browsing"],
                    ["ssd computer close up", "laptop on desk"]]}
    T["pc_no_start"] = {
        "title": "Computer On Kyun Nahi Hota?", "yt_title": "Computer On Nahi Ho Raha? Pehle Ye 3 Cheez Check Karo #shorts", "tag": "ROZ KI TECH",
        "thumb": ("PC ON NAHI", "KYUN?"), "thumb_hi": "कंप्यूटर ऑन नहीं हो रहा?", "thumb_sub": "PEHLE YE 3 CHEEZ CHECK", "thumb_long": "COMPUTER ON NAHI HO RAHA? PEHLE YE 3 CHEEZ CHECK KARO", "thumb_hot": "NAHI",
        "tags": ["computer on nahi ho raha", "pc not turning on hinglish", "computer problem solution", "tech explained hinglish", "shorts"],
        "lines": [
            "आपका कंप्यूटर ऑन क्यों नहीं हो रहा? पहले ये तीन चीज़ें चेक करो।",
            "पहली, बिजली। सॉकेट, एक्सटेंशन बोर्ड और केबल, तीनों में बिजली पहुँच रही है या नहीं, किसी दूसरे उपकरण को लगाकर देखो।",
            "दूसरी, कई बार कंप्यूटर चालू होता है, पर स्क्रीन पर कुछ नहीं दिखता। तब मॉनिटर की केबल और इनपुट सेटिंग देखो।",
            "तीसरी, अगर कंप्यूटर चालू होकर तुरंत बंद हो जाए, या बीप की आवाज़ आए, तो अंदर कोई पार्ट ढीला या ख़राब हो सकता है। इसे ख़ुद खोलने की जगह किसी टेक्नीशियन को दिखाओ।",
            "तो पहले बिजली, फिर स्क्रीन, फिर टेक्नीशियन। सीधी बात, पहले आसान चीज़ें चेक करो। अगली बार बताऊँगा, फ़ोन की बैटरी जल्दी क्यों ख़त्म होती है।",
        ],
        "caps": ["PC ON NAHI HO RAHA?", "1. BIJLI CHECK KARO", "2. SCREEN / MONITOR CABLE", "3. BEEP? TECHNICIAN BULAO", "PEHLE AASAAN CHEEZ"],
        "scenes": [{"type": "card", "lines": ["PC ON NAHI?", "3 CHEEZ CHECK"], "color": "gold"},
                   {"type": "tips", "items": ["SOCKET MEIN BIJLI?", "EXTENSION BOARD OK?", "KEBAL OK?"]},
                   {"type": "tips", "items": ["MONITOR KEBAL TIGHT?", "INPUT SETTING SAHI?", "SCREEN ON HAI?"]},
                   {"type": "tips", "items": ["BEEP AAYE TO RUKO", "KHUD MAT KHOLO", "TECHNICIAN KO DIKHAO"]},
                   {"type": "card", "lines": ["BIJLI, SCREEN,", "TECHNICIAN"], "color": "green"}],
        "queries": [["power socket plug close up", "extension cord socket"], ["power socket plug close up", "electric plug wall"],
                    ["computer monitor cable close up", "monitor on desk"], ["technician repairing computer", "computer repair hands"],
                    ["desktop computer on desk", "computer setup desk"]]}
    T["mixer_hot"] = {
        "title": "Mixer Garam Kyun Hota Hai?", "yt_title": "Mixer Grinder Garam Kyun Hota Hai? Asli Wajah #shorts", "tag": "ROZ KI TECH",
        "thumb": ("MIXER HOT", "KYUN?"), "thumb_hi": "मिक्सर गर्म क्यों होता है?", "thumb_sub": "ASLI WAJAH + FIX", "thumb_long": "MIXER CHALATE CHALATE ITNA GARAM KYUN HO JATA HAI?", "thumb_hot": "GARAM",
        "tags": ["mixer garam kyun hota hai", "mixer grinder heating", "kitchen tips hinglish", "tech explained hinglish", "shorts"],
        "lines": [
            "मिक्सर चलाते-चलाते इतना गरम क्यों हो जाता है?",
            "मिक्सर के अंदर एक मोटर घूमती है, और मोटर में बिजली चलती है तो गरमी बनती है, ठीक वैसे ही जैसे फ़ोन की चिप में बनी थी।",
            "जब आप भारी चीज़ें, जैसे सूखे मसाले या मोटा आटा, ज़्यादा देर पीसते हो, तो मोटर पर लोड बढ़ जाता है, और गरमी भी।",
            "इसीलिए ज़्यादातर मिक्सर में हवा आने-जाने के छेद होते हैं। अगर वो बंद हों, तो मोटर और जल्दी गरम होती है।",
            "तो थोड़ा-थोड़ा पीसो, बीच में ब्रेक दो, और जार में ज़्यादा सामान मत भरो। अगर जलने की गंध आए, तो तुरंत बंद करके बिजली निकालो। सीधी बात, ज़्यादा लोड, ज़्यादा गरमी।",
        ],
        "caps": ["MIXER GARAM KYUN?", "MOTOR = GARMI", "ZYADA LOAD = ZYADA GARMI", "HAWA KE CHHED BAND = GARMI", "THODA PEESO, BREAK DO"],
        "scenes": [{"type": "card", "lines": ["MIXER GARAM?", "ASLI WAJAH"], "color": "orange"},
                   {"type": "bars2", "rows": [("MOTOR KA KAAM", 0.6, "blue"), ("GARMI", 0.5, "orange")]},
                   {"type": "bars2", "rows": [("HALKA PEESNA: GARMI", 0.3, "green"), ("BHARI PEESNA: GARMI", 0.95, "red")]},
                   {"type": "bars2", "rows": [("HAWA KE CHHED KHULE", 0.3, "green"), ("HAWA KE CHHED BAND", 0.9, "red")]},
                   {"type": "tips", "items": ["THODA THODA PEESO", "BEECH MEIN BREAK DO", "JAR ZYADA MAT BHARO"]}],
        "queries": [["mixer grinder kitchen", "kitchen mixer running"], ["electric motor close up", "motor machine close up"],
                    ["grinding spices", "spices in bowl close up"], ["kitchen appliance close up", "mixer grinder jar"],
                    ["kitchen counter", "hands cooking close up"]]}


def _news_topics():
    TOPICS["news_72h"] = {
        "title": "72 Ghante Ka Rashan: Sach Kya Hai?", "yt_title": "72 Ghante Ka Rashan: WW3 Ya Sirf Preparedness? Sach Kya Hai #shorts",
        "tag": "TRENDING SACH", "icons": "alarm", "thumb_scene": 4, "thumb_crop": (420, 420, 1080, 791), "thumb_queries": ["canned food shelf", "water bottles stack", "emergency kit supplies", "flashlight on table"],
        "thumb": ("72 GHANTE", "SACH KYA?"), "thumb_hi": "72 घंटे का राशन? WW3?", "thumb_sub": "SACH KYA HAI? DEKHO",
        "thumb_long": "72 GHANTE KA RASHAN: KYA SACH MEIN WW3 AA RAHA HAI? SACH JAANO", "thumb_hot": "SACH",
        "tags": ["72 ghante ka rashan", "ww3 sach kya hai", "emergency kit uk", "be ready campaign", "news explained hinglish", "shorts"],
        "lines": [
            "सोशल मीडिया पर चल रहा है कि कई देश 72 घंटे का राशन रखने को कह रहे हैं। क्या तीसरा विश्व युद्ध आने वाला है?",
            "सीधा जवाब, कोई सबूत नहीं मिला। ब्रिटेन की सरकार ने अक्टूबर में Be Ready अभियान शुरू किया: बिजली, पानी या इंटरनेट बंद हो, तो तीन दिन का सामान रखें।",
            "वजह साइबर हमले, तूफ़ान, बाढ़ और सप्लाई का रुकना है। मदद पहुँचने में दो-तीन दिन लग सकते हैं, इसीलिए तीन दिन का नियम है। यह नया नहीं।",
            "वायरल पोस्ट की सत्रह देशों वाली बात मुझे किसी भरोसेमंद रिपोर्ट में नहीं मिली। घबराने की ज़रूरत नहीं।",
            "हाँ, बाढ़-भूकंप वाले इलाक़ों में तीन दिन का पानी, सूखा खाना, टॉर्च, पावर बैंक, कैश और दवाइयाँ रखना समझदारी है। डरो नहीं, तैयार रहो।",
        ],
        "caps": ["WW3 AA RAHA HAI?", "UK KA BE READY CAMPAIGN", "3 DIN KA NIYAM, NAYA NAHI", "17 DESHON KI BAAT: CONFIRM NAHI", "DARNA NAHI, TAIYAAR RAHNA"],
        "scenes": [{"type": "card", "lines": ["72 GHANTE KA", "RASHAN: SACH?"], "color": "red"},
                   {"type": "card", "lines": ["UK: BE READY", "3 DIN KA SAMAAN"], "color": "gold"},
                   {"type": "bars2", "rows": [("CYBER HAMLE / BIJLI BAND", 0.7, "orange"), ("TOOFAN / BAADH", 0.8, "blue"), ("SUPPLY RUKNA", 0.6, "gold")]},
                   {"type": "card", "lines": ["17 DESHON KI BAAT", "KAHIN CONFIRM NAHI"], "color": "red"},
                   {"type": "tips", "items": ["PAANI + SOOKHA KHANA", "TORCH + POWER BANK", "CASH + DAWAIYAN"]}],
        "queries": [["emergency supplies kit", "canned food water bottles shelf"], ["power outage city night", "candle light darkness"],
                    ["storm flood street", "server room close up"], ["reading news on smartphone", "scrolling smartphone hand"],
                    ["flashlight power bank first aid kit", "emergency kit backpack"]],
        "desc_extra": ("Sources checked: UK government 'Be Ready' campaign coverage (Oct 2026), EU preparedness strategy (Mar 2025). "
                       "The '17 countries' claim could not be confirmed in reliable reports. This is a fact-check style explainer, not advice or a prediction."),
    }


_news_topics()


_FONT_CACHE = {}


_more_topics()


def font(sz):
    if sz not in _FONT_CACHE:
        _FONT_CACHE[sz] = E._font(sz)
    return _FONT_CACHE[sz]


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, k):
    return a + (b - a) * k


def mix(c1, c2, k):
    return tuple(int(lerp(c1[i], c2[i], k)) for i in range(3))


_BG = None


def background():
    global _BG
    if _BG is None:
        ys = np.linspace(0, 1, H)[:, None, None]
        top, bot = np.array(BG_TOP)[None, None, :], np.array(BG_BOT)[None, None, :]
        arr = (top * (1 - ys) + bot * ys) * np.ones((H, W, 3))
        im = Image.fromarray(arr.astype(np.uint8))
        d = ImageDraw.Draw(im, "RGBA")
        for x in range(0, W, 90):
            d.line([(x, 0), (x, H)], fill=(255, 255, 255, 10), width=1)
        for y in range(0, H, 90):
            d.line([(0, y), (W, y)], fill=(255, 255, 255, 10), width=1)
        _BG = im
    return _BG.copy()


def glow(d, cx, cy, r, color, strength=1.0):
    for i in range(7):
        k = i / 7
        rr = r * (1.6 - k * 1.2)
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=color + (int(16 * strength * (0.4 + k)),))


def text_c(d, xy, s, f, fill=WHITE, outline=(0, 0, 0), width=4):
    x, y = xy
    for dx in range(-width, width + 1, 2):
        for dy in range(-width, width + 1, 2):
            d.text((x + dx, y + dy), s, font=f, fill=outline + (255,), anchor="mm")
    d.text((x, y), s, font=f, fill=fill + (255,), anchor="mm")


def waves(d, cx, base_y, width, t, heat, color=ORANGE, n=4):
    """Rising wavy heat lines; heat 0..1 controls how many and how bright."""
    for i in range(n):
        x0 = cx - width / 2 + width * (i + 0.5) / n
        pts = []
        for k in range(24):
            y = base_y - k * 14 - (t * 90) % 40
            x = x0 + math.sin(k * 0.55 + t * 4 + i) * 12
            pts.append((x, y))
        a = int(190 * heat * (0.6 + 0.4 * math.sin(t * 3 + i)))
        d.line(pts, fill=color + (max(0, a),), width=7, joint="curve")


# ───────────────────────────── scene painters: (d, t, dur) ───────────────────────────────

def sc_thermo(d, t, dur, real=False):
    k = ease(t / max(dur * 0.85, 0.1))
    temp = lerp(31, 46, k)
    col = mix(BLUE, RED, k)
    cx, cy = 540, 880
    if real:
        d.rounded_rectangle((90, 560, 790, 960), radius=40, fill=(10, 14, 32, 205), outline=col + (255,), width=6)
        text_c(d, (440, 740), f"{temp:.0f}°C", font(210), fill=WHITE, width=5)
        text_c(d, (440, 900), "PHONE TEMPERATURE", font(40), fill=MUTED, width=2)
        tx, ty0, ty1 = 900, 560, 960
        d.rounded_rectangle((tx - 22, ty0, tx + 22, ty1), radius=22, fill=(255, 255, 255, 60), outline=WHITE + (220,), width=4)
        fh = (ty1 - ty0 - 10) * k
        d.rounded_rectangle((tx - 13, ty1 - 8 - fh, tx + 13, ty1 - 8), radius=13, fill=col + (255,))
        return
    glow(d, cx, cy, 340, col, 0.6 + k)
    d.rounded_rectangle((cx - 200, cy - 340, cx + 200, cy + 340), radius=56, fill=(18, 22, 44, 255), outline=col + (255,), width=10)
    d.rounded_rectangle((cx - 170, cy - 300, cx + 170, cy + 300), radius=30, fill=mix((20, 40, 90), (120, 20, 20), k) + (255,))
    d.rounded_rectangle((cx - 40, cy - 322, cx + 40, cy - 308), radius=7, fill=(0, 0, 0, 255))
    text_c(d, (cx, cy - 40), f"{temp:.0f}°C", font(190), fill=WHITE, width=5)
    text_c(d, (cx, cy + 120), "TEMPERATURE", font(40), fill=MUTED, width=2)
    waves(d, cx, cy - 360, 300, t, k)
    # thermometer
    tx, ty0, ty1 = 880, 620, 1150
    d.rounded_rectangle((tx - 24, ty0, tx + 24, ty1), radius=24, fill=(255, 255, 255, 40), outline=WHITE + (200,), width=4)
    fh = (ty1 - ty0 - 10) * k
    d.rounded_rectangle((tx - 14, ty1 - 8 - fh, tx + 14, ty1 - 8), radius=14, fill=col + (255,))
    d.ellipse((tx - 42, ty1 - 20, tx + 42, ty1 + 64), fill=col + (255,))


def sc_chip(d, t, dur, real=False):
    k = ease(t / max(dur * 0.9, 0.1))
    cx, cy, s = 540, 900, 190
    heat = 0.25 + 0.75 * k
    if real:
        d.rectangle((0, 0, W, H), fill=(255, 90, 20, int(70 * k)))
        for ri in range(6):
            y = 640 + ri * 80
            d.line([(30, y), (W - 30, y)], fill=(255, 255, 255, 50), width=4)
            for j in range(8):
                p = ((t * 0.5 + j / 8 + ri * 0.11) % 1.0)
                x = lerp(30, W - 30, p)
                d.ellipse((x - 12, y - 12, x + 12, y + 12), fill=GOLD + (255,))
        rnd = np.random.RandomState(int(t * 12) % 997)
        for _ in range(int(6 + 40 * k)):
            x, y = rnd.uniform(300, 780), rnd.uniform(600, 1100)
            d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=ORANGE + (235,))
        d.rounded_rectangle((60, 520, 330, 590), radius=30, fill=(10, 14, 32, 215), outline=GOLD + (255,), width=3)
        d.text((195, 555), "CURRENT", font=font(40), fill=GOLD + (255,), anchor="mm")
        d.rounded_rectangle((200, 1160, 880, 1250), radius=40, fill=(10, 14, 32, 220), outline=ORANGE + (255,), width=4)
        d.text((540, 1205), "FRICTION  =  HEAT", font=font(52), fill=ORANGE + (255,), anchor="mm")
        return
    glow(d, cx, cy, 260, ORANGE, heat * 1.4)
    d.rounded_rectangle((cx - s, cy - s, cx + s, cy + s), radius=30, fill=(25, 30, 56, 255), outline=mix(CYAN, ORANGE, k) + (255,), width=8)
    d.rounded_rectangle((cx - 90, cy - 90, cx + 90, cy + 90), radius=18, fill=mix((30, 60, 90), (150, 60, 20), k) + (255,))
    text_c(d, (cx, cy), "CHIP", font(70), fill=WHITE, width=3)
    for i in range(-3, 4):
        d.line([(cx + i * 50, cy - s - 40), (cx + i * 50, cy - s)], fill=MUTED + (255,), width=6)
        d.line([(cx + i * 50, cy + s), (cx + i * 50, cy + s + 40)], fill=MUTED + (255,), width=6)
        d.line([(cx - s - 40, cy + i * 50), (cx - s, cy + i * 50)], fill=MUTED + (255,), width=6)
        d.line([(cx + s, cy + i * 50), (cx + s + 40, cy + i * 50)], fill=MUTED + (255,), width=6)
    # electricity particles flowing in from the left along 5 traces
    rows = [-2, -1, 0, 1, 2]
    for ri, r in enumerate(rows):
        y = cy + r * 50
        d.line([(60, y), (cx - s - 40, y)], fill=(255, 255, 255, 40), width=5)
        for j in range(7):
            p = ((t * 0.55 + j / 7 + ri * 0.13) % 1.0)
            x = lerp(60, cx - s - 40, p)
            d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=GOLD + (255,))
    # sparks (friction) inside / around chip, more with time
    rnd = np.random.RandomState(int(t * 12) % 997)
    for _ in range(int(4 + 26 * k)):
        a = rnd.uniform(0, 6.28)
        rr = rnd.uniform(40, s + 20)
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=ORANGE + (230,))
    waves(d, cx, cy - s - 60, 300, t, heat, n=5)
    text_c(d, (170, cy - 170), "CURRENT", font(54), fill=GOLD, width=3)
    text_c(d, (540, cy + s + 150), "FRICTION  =  HEAT", font(64), fill=ORANGE, width=3)


def sc_bars(d, t, dur, real=False):
    k1 = ease(t / max(dur * 0.8, 0.1))
    k2 = ease((t - 0.35) / max(dur * 0.8, 0.1))
    x0, x1 = 120, 960
    if real:
        d.rounded_rectangle((60, 470, 1020, 1060), radius=44, fill=(10, 14, 32, 205))
    for y, label, k, col in ((620, "WORK  (GAME)", k1, BLUE), (900, "HEAT", k2, RED)):
        text_c(d, (540, y - 80), label, font(60), fill=WHITE, width=3)
        d.rounded_rectangle((x0, y - 38, x1, y + 38), radius=38, fill=(255, 255, 255, 30), outline=(255, 255, 255, 90), width=3)
        d.rounded_rectangle((x0 + 5, y - 33, x0 + 5 + (x1 - x0 - 10) * k, y + 33), radius=33, fill=col + (255,))
        text_c(d, (x1 - 10, y - 80), f"{int(k * 100)}%", font(48), fill=MUTED, width=2)
    if real:
        return
    # flame
    fx, fy, fs = 540, 1215, 70 + 80 * k2
    flick = math.sin(t * 9) * 8
    d.polygon([(fx, fy - fs * 1.5), (fx + fs * 0.7 + flick, fy - fs * 0.3), (fx + fs * 0.45, fy + fs * 0.6),
               (fx, fy + fs * 0.75), (fx - fs * 0.45, fy + fs * 0.6), (fx - fs * 0.7 - flick, fy - fs * 0.3)], fill=ORANGE + (255,))
    d.polygon([(fx, fy - fs * 0.6), (fx + fs * 0.3, fy + fs * 0.2), (fx, fy + fs * 0.55), (fx - fs * 0.3, fy + fs * 0.2)], fill=GOLD + (255,))


def sc_battery(d, t, dur, real=False):
    k = ease(t / max(dur * 0.9, 0.1))
    cx, cy = 540, 900
    heat = 0.2 + 0.8 * k
    if real:
        cy = 700
        d.rounded_rectangle((90, 470, 990, 1010), radius=44, fill=(10, 14, 32, 205))
        d.rounded_rectangle((cx - 230, cy - 120, cx + 230, cy + 120), radius=34, fill=(18, 22, 44, 255), outline=WHITE + (255,), width=9)
        d.rounded_rectangle((cx + 230, cy - 45, cx + 270, cy + 45), radius=10, fill=WHITE + (255,))
        d.rounded_rectangle((cx - 218, cy - 108, cx - 218 + 440 * k, cy + 108), radius=24, fill=mix(GREEN, ORANGE, k) + (255,))
        text_c(d, (cx, cy), f"{int(k * 100)}%", font(100), fill=WHITE, width=4)
        text_c(d, (cx, cy + 210), "FAST CHARGER = ZYADA HEAT", font(46), fill=ORANGE, width=3)
        return
    glow(d, cx, cy, 300, mix(GREEN, ORANGE, k), 0.8)
    d.rounded_rectangle((cx - 230, cy - 130, cx + 230, cy + 130), radius=34, fill=(18, 22, 44, 255), outline=WHITE + (255,), width=9)
    d.rounded_rectangle((cx + 230, cy - 45, cx + 270, cy + 45), radius=10, fill=WHITE + (255,))
    fill_w = 440 * k
    d.rounded_rectangle((cx - 218, cy - 118, cx - 218 + fill_w, cy + 118), radius=24, fill=mix(GREEN, ORANGE, k) + (255,))
    text_c(d, (cx, cy), f"{int(k * 100)}%", font(110), fill=WHITE, width=4)
    # bolt
    bx, by = cx, cy - 330
    s = 1.0 + 0.08 * math.sin(t * 8)
    d.polygon([(bx + 20 * s, by - 90 * s), (bx - 55 * s, by + 15 * s), (bx - 5 * s, by + 15 * s), (bx - 25 * s, by + 95 * s),
               (bx + 55 * s, by - 20 * s), (bx + 5 * s, by - 20 * s)], fill=GOLD + (255,))
    waves(d, cx, cy - 150, 380, t, heat, n=5)
    text_c(d, (cx, cy + 270), "FAST CHARGER = ZYADA HEAT", font(50), fill=ORANGE, width=3)


def sc_tips(d, t, dur, tips):
    """Action steps: gold header, then numbered steps that slide in one by one (reads like a to-do, not like answer options)."""
    k0 = ease(t / 0.4)
    text_c(d, (540, 520), "AB YE KARO", font(84), fill=GOLD, width=6)
    for i, s in enumerate(tips):
        k = ease((t - 0.6 - i * 1.0) / 0.5)
        y = 700 + i * 170
        x = lerp(1300, 0, k)
        d.rounded_rectangle((70 + x, y - 70, 1010 + x, y + 70), radius=30, fill=(10, 14, 32, 220))
        d.ellipse((95 + x, y - 48, 191 + x, y + 48), fill=GOLD + (255,))
        d.text((143 + x, y), str(i + 1), font=font(70), fill=(10, 10, 20, 255), anchor="mm")
        d.text((225 + x, y), s, font=fit_font(d, s, 740, 52, 34), fill=WHITE + (255,), anchor="lm")


def fit_font(d, s, maxw, start, lo=44):
    sz = start
    while sz > lo and d.textlength(s, font=font(sz)) > maxw:
        sz -= 4
    return font(sz)


def sc_card(d, t, dur, spec):
    """Big hook card: 1-3 short lines on a translucent panel (no numbers)."""
    k = ease(t / 0.5)
    lines = spec["lines"]
    col = {"red": RED, "gold": GOLD, "green": GREEN, "blue": BLUE, "orange": ORANGE}.get(spec.get("color", "gold"), GOLD)
    hgt = 130 * len(lines) + 90
    y0 = 760 - hgt / 2
    d.rounded_rectangle((70, y0, 1010, y0 + hgt), radius=44, fill=(10, 14, 32, int(210 * k)), outline=col + (int(255 * k),), width=6)
    for i, ln in enumerate(lines):
        text_c(d, (540, y0 + 90 + i * 130), ln, fit_font(d, ln, 840, 96), fill=col if i == len(lines) - 1 else WHITE, width=5)


def sc_bars2(d, t, dur, spec):
    """Qualitative bars (no numbers): rows of (label, fill 0..1, colour). They fill one after another."""
    rows = spec["rows"]
    d.rounded_rectangle((60, 470, 1020, 470 + 170 + 220 * len(rows)), radius=44, fill=(10, 14, 32, 205))
    x0, x1 = 120, 960
    for i, (label, fill, cname) in enumerate(rows):
        y = 620 + i * 230
        k = ease((t - 0.3 - i * 0.5) / max(dur * 0.55, 0.1)) * fill
        col = {"red": RED, "blue": BLUE, "green": GREEN, "orange": ORANGE, "gold": GOLD}.get(cname, BLUE)
        text_c(d, (540, y - 82), label, font(50), fill=WHITE, width=3)
        d.rounded_rectangle((x0, y - 36, x1, y + 36), radius=36, fill=(255, 255, 255, 30), outline=(255, 255, 255, 90), width=3)
        if k > 0.01:
            d.rounded_rectangle((x0 + 5, y - 31, x0 + 5 + (x1 - x0 - 10) * k, y + 31), radius=31, fill=col + (255,))


PAINTERS = {"thermo": sc_thermo, "chip": sc_chip, "bars": sc_bars, "battery": sc_battery}


def frame_fn(topic, idx, n, dur, base=None):
    """Returns make_frame(t) for scene idx."""
    kind = topic["scenes"][idx]
    real = base is not None
    last_good = []
    cap = topic["caps"][idx]
    accent = GOLD

    def mk(t):
        if real:
            fr = np.asarray(base(min(t, max(dur - 0.05, 0.0))), dtype=np.float32)
            if float(fr.mean()) < 4.0 and last_good:   # footage ran out (black): hold the last good frame instead
                fr = last_good[0]
            else:
                last_good[:] = [fr]
            shade = np.linspace(0.62, 0.34, H, dtype=np.float32)[:, None, None]
            im = Image.fromarray(np.clip(fr * shade, 0, 255).astype(np.uint8))
        else:
            im = background()
        d = ImageDraw.Draw(im, "RGBA")
        # top chips
        d.rounded_rectangle((44, 52, 44 + 330, 52 + 66), radius=33, fill=(10, 14, 32, 215), outline=accent + (255,), width=3)
        d.text((44 + 165, 52 + 33), topic["tag"], font=font(36), fill=WHITE + (255,), anchor="mm")
        # scene body
        if isinstance(kind, dict):
            ty = kind["type"]
            if ty == "card":
                sc_card(d, t, dur, kind)
            elif ty == "bars2":
                sc_bars2(d, t, dur, kind)
            elif ty == "tips":
                sc_tips(d, t, dur, kind["items"])
        elif kind == "tips":
            sc_tips(d, t, dur, topic["tips"])
        else:
            PAINTERS[kind](d, t, dur, real)
        # caption (safe zone above platform buttons), fade-in + tiny rise
        a = ease(t / 0.35)
        yy = H - 520 - (1 - a) * 24
        cf = fit_font(d, cap, 980, 62, 34)
        for dx, dy in ((4, 4), (-3, 3), (3, -3)):
            d.text((W / 2 + dx, yy + dy), cap, font=cf, fill=(0, 0, 0, int(255 * a)), anchor="mm")
        d.text((W / 2, yy), cap, font=cf, fill=WHITE + (int(255 * a),), anchor="mm")
        d.rectangle((W / 2 - 130, yy + 62, W / 2 + 130, yy + 70), fill=accent + (int(255 * a),))
        if idx == n - 1 and dur > 4.0:
            ck = ease((t - (dur - 3.4)) / 0.4)
            if ck > 0:
                handle = CHANNEL_HANDLE
                lab = "FOLLOW KARO   |   LIKE   |   SHARE"
                d.rounded_rectangle((60, 1160, 1020, 1160 + (170 if handle else 110)), radius=34, fill=(200, 25, 30, int(240 * ck)), outline=WHITE + (int(255 * ck),), width=5)
                d.text((540, 1160 + 55), lab, font=fit_font(d, lab, 880, 56, 34), fill=WHITE + (int(255 * ck),), anchor="mm")
                if handle:
                    d.text((540, 1160 + 128), handle, font=fit_font(d, handle, 880, 46, 30), fill=GOLD + (int(255 * ck),), anchor="mm")
        # progress segments
        seg = (W - 160) / n
        for i in range(n):
            col = accent + (255,) if i <= idx else (255, 255, 255, 90)
            d.rounded_rectangle((80 + i * seg + 6, H - 330, 80 + (i + 1) * seg - 6, H - 320), radius=5, fill=col)
        d.text((W / 2, H - 270), "Synthetic AI voice | Educational", font=font(30), fill=(210, 218, 238, 255), anchor="mm")
        return np.array(im)

    return mk


GEMINI_STYLES = [
    ("Puck", "Say this like an energetic, curious young Indian YouTuber hooking viewers in the first seconds, fast and punchy, with real surprise on the key word:"),
    ("Charon", "Say this like a friendly teacher explaining to a friend, warm, clear, lively, slight smile, natural Hinglish pacing, stress on the analogy words:"),
    ("Charon", "Say this with rising energy, like building momentum, each phrase a little stronger than the last, friendly and clear:"),
    ("Charon", "Say this like a friend pointing out something that surprises people, clear, lively, matter-of-fact with a little emphasis:"),
    ("Charon", "Say this like a confident, reassuring friend giving three quick tips, firm and upbeat, ending with a curious teaser for the next video:"),
]
_GEM = {"model": None, "last": 0.0}


def gemini_voice(text, path, idx):
    """Emotional free Gemini TTS (Puck hook, Charon explain). Returns the wav path, or None to fall back to Edge TTS.
    Free tier is about 2 requests/minute, so calls are spaced."""
    import time
    import base64
    import wave
    import requests
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        return None
    try:
        if _GEM["model"] is None:
            r = requests.get("https://generativelanguage.googleapis.com/v1beta/models", params={"key": key, "pageSize": 200}, timeout=30)
            names = [m["name"].split("/")[-1] for m in r.json().get("models", []) if "tts" in m["name"].lower()]
            _GEM["models"] = sorted(names, key=lambda n: ("3.1" in n, "flash" in n, "lite" not in n, "preview" not in n), reverse=True)
            _GEM["model"] = _GEM["models"][0] if _GEM["models"] else ""
            print("[TECH] gemini tts models:", _GEM["models"])
        if not _GEM["model"]:
            return None
        voice, style = GEMINI_STYLES[min(idx, len(GEMINI_STYLES) - 1)]
        body = {"contents": [{"parts": [{"text": f"{style} {text}"}]}],
                "generationConfig": {"responseModalities": ["AUDIO"],
                                     "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
        for attempt in range(7):
            wait = 25 - (time.time() - _GEM["last"])
            if wait > 0:
                time.sleep(wait)
            _GEM["last"] = time.time()
            r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{_GEM['model']}:generateContent",
                              params={"key": key}, json=body, timeout=120)
            if r.status_code == 200:
                pcm = base64.b64decode(r.json()["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
                secs = len(pcm) / 48000.0
                max_secs = len(text.split()) / 2.4 * 1.35 + 1.2   # normal pace is ~2.5 words/s; far longer means the model read the style note or crawled
                if secs > max_secs:
                    print(f"[TECH] gemini audio too long on {_GEM['model']}: {secs:.1f}s > {max_secs:.1f}s, rotating model")
                    ms = _GEM.get("models", [])
                    if len(ms) > 1:
                        _GEM["model"] = ms[(ms.index(_GEM["model"]) + 1) % len(ms)]
                        continue
                    return None
                wav = Path(str(path)).with_suffix(".wav")
                with wave.open(str(wav), "wb") as w:
                    w.setnchannels(1)
                    w.setsampwidth(2)
                    w.setframerate(24000)
                    w.writeframes(pcm)
                return wav
            print(f"[TECH] gemini tts {r.status_code} on {_GEM['model']} (attempt {attempt + 1})")
            if r.status_code == 429 and len(_GEM.get("models", [])) > 1:
                # each model has its own free quota: rotate to the next one
                ms = _GEM["models"]
                _GEM["model"] = ms[(ms.index(_GEM["model"]) + 1) % len(ms)]
                continue
            ra = r.headers.get("Retry-After", "")
            time.sleep(min(90, float(ra) + 2) if ra.replace(".", "").isdigit() else 70)
    except Exception as e:
        print(f"[TECH] gemini tts failed, using Edge voice: {str(e)[:100]}")
    return None


def whoosh(dur_s=0.4, sr=44100):
    n = int(dur_s * sr)
    rnd = np.random.RandomState(7)
    noise = rnd.randn(n).astype(np.float32)
    # crude low-pass by moving average, sweep envelope
    k = 40
    noise = np.convolve(noise, np.ones(k) / k, mode="same")
    env = np.sin(np.linspace(0, math.pi, n)) ** 2
    out = noise * env
    out /= (np.abs(out).max() or 1.0)
    return (out * 0.35).astype(np.float32)


def pick_thumb_frame(base, dur):
    """Pick the most usable frame: mid brightness, not blown out, plenty of detail."""
    best, best_s = None, -1e9
    for t in (0.4, 1.0, 1.6, 2.2, 2.8, 3.4):
        try:
            fr = np.asarray(base(min(t, max(dur - 0.1, 0.0))))
        except Exception:
            continue
        g = fr.mean(axis=2)
        blown = float((g > 235).mean())
        dark = float((g < 25).mean())
        detail = float(np.abs(np.diff(g[::4, ::4], axis=1)).mean())
        s = detail - 80 * blown - 40 * dark - abs(float(g.mean()) - 120) * 0.15
        if s > best_s:
            best, best_s = fr, s
    return best


_DEVA = ["/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf", "/usr/share/fonts/truetype/noto/NotoSansDevanagariUI-Bold.ttf",
         "/usr/share/fonts/opentype/noto/NotoSansDevanagari-Bold.ttf", "/usr/share/fonts/truetype/lohit-devanagari/Lohit-Devanagari.ttf",
         "C:/Windows/Fonts/NirmalaB.ttf", "C:/Windows/Fonts/mangalb.ttf"]


def deva_font(sz):
    from PIL import ImageFont
    for p_ in _DEVA:
        if os.path.exists(p_):
            return ImageFont.truetype(p_, sz)
    return None


def _crop169(im, topic):
    """16:9 thumbnail crop. Topics can set thumb_crop=(x0,y0,x1,y1) to keep people out of frame (zoom into the objects)."""
    box = topic.get("thumb_crop") or (0, 380, W, 380 + int(W * 9 / 16))
    return im.crop(box).resize((1280, 720), Image.LANCZOS)


def _runs(s):
    """Split a string into (is_devanagari, text) runs so each run uses a font that has its glyphs."""
    out = []
    for ch in s:
        dev = "\u0900" <= ch <= "\u097f"
        if ch == " " and out:
            dev = out[-1][0]
        if out and out[-1][0] == dev:
            out[-1][1] += ch
        else:
            out.append([dev, ch])
    return out


def mixed_width(d, s, size):
    fd, fl = deva_font(size), font(size)
    return sum(d.textlength(t, font=(fd if dev else fl)) for dev, t in _runs(s))


def mixed_text(d, cx, cy, s, size, fill=WHITE, outline=(0, 0, 0), width=4):
    fd, fl = deva_font(size), font(size)
    runs = _runs(s)
    total = sum(d.textlength(t, font=(fd if dev else fl)) for dev, t in runs)
    x = cx - total / 2
    for dev, t in runs:
        f = fd if dev else fl
        for dx in range(-width, width + 1, 2):
            for dy in range(-width, width + 1, 2):
                d.text((x + dx, cy + dy), t, font=f, fill=outline + (255,), anchor="lm")
        d.text((x, cy), t, font=f, fill=fill + (255,), anchor="lm")
        x += d.textlength(t, font=f)


def _alarm(d, cx, cy, s):
    d.polygon([(cx, cy - s), (cx + s * 1.05, cy + s * 0.8), (cx - s * 1.05, cy + s * 0.8)], fill=RED + (255,), outline=WHITE + (255,))
    d.rectangle((cx - s * 0.09, cy - s * 0.4, cx + s * 0.09, cy + s * 0.25), fill=WHITE + (255,))
    d.ellipse((cx - s * 0.11, cy + s * 0.38, cx + s * 0.11, cy + s * 0.6), fill=WHITE + (255,))


def _flame(d, cx, cy, s):
    d.polygon([(cx, cy - s * 1.5), (cx + s * 0.7, cy - s * 0.3), (cx + s * 0.45, cy + s * 0.6), (cx, cy + s * 0.75),
               (cx - s * 0.45, cy + s * 0.6), (cx - s * 0.7, cy - s * 0.3)], fill=ORANGE + (255,))
    d.polygon([(cx, cy - s * 0.6), (cx + s * 0.3, cy + s * 0.2), (cx, cy + s * 0.55), (cx - s * 0.3, cy + s * 0.2)], fill=GOLD + (255,))


def _thermo_icon(d, cx, cy, s):
    d.rounded_rectangle((cx - s * 0.2, cy - s, cx + s * 0.2, cy + s * 0.6), radius=int(s * 0.2), fill=(255, 255, 255, 255), outline=(40, 40, 40, 255), width=4)
    d.ellipse((cx - s * 0.42, cy + s * 0.35, cx + s * 0.42, cy + s * 1.19), fill=RED + (255,), outline=(40, 40, 40, 255), width=4)
    d.rounded_rectangle((cx - s * 0.1, cy - s * 0.2, cx + s * 0.1, cy + s * 0.7), radius=int(s * 0.1), fill=RED + (255,))


def pattern_thumbnail(frame, topic, path):
    """Pattern from the top phone-heating videos (screenshots 2026-11-01): red banner with a big Devanagari question, yellow Hinglish
    strip, real phone photo with a heat (warm) side and a cool (blue) side, thermometer + flame icons. Honest strip text, no '100% solution'."""
    from PIL import ImageEnhance
    hi = topic.get("thumb_hi")
    f_hi = deva_font(104) if hi else None
    if not hi or f_hi is None:
        return real_thumbnail(frame, topic, path)
    im = Image.fromarray(frame).convert("RGB")
    im = _crop169(im, topic)
    im = ImageEnhance.Color(im).enhance(1.5)
    im = ImageEnhance.Contrast(im).enhance(1.2)
    heat = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
    hd = ImageDraw.Draw(heat)
    for x in range(1280):   # warm on the left, cool on the right
        k = x / 1280
        hd.line([(x, 0), (x, 720)], fill=(255, 80, 20, int(120 * (1 - k) ** 1.5)) if k < 0.5 else (30, 140, 255, int(110 * (k - 0.5) * 2)))
    im = Image.alpha_composite(im.convert("RGBA"), heat).convert("RGB")
    d = ImageDraw.Draw(im, "RGBA")
    # red banner with the Devanagari question
    d.rectangle((0, 0, 1280, 250), fill=(200, 20, 25, 255))
    d.rectangle((0, 250, 1280, 262), fill=GOLD + (255,))
    words = hi.split()
    lines, cur = [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if mixed_width(d, t, 104) <= 1180 or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    lines.append(cur)
    lines = lines[:2]
    y = 125 if len(lines) == 1 else 78
    for ln in lines:
        mixed_text(d, 640, y, ln, 104, fill=WHITE, outline=(60, 0, 0), width=4)
        y += 120
    # icons
    if topic.get("icons") == "alarm":
        _alarm(d, 150, 450, 80)
        _alarm(d, 1130, 450, 80)
    else:
        _flame(d, 150, 480, 70)
        _thermo_icon(d, 1130, 470, 80)
    # yellow strip
    sub = topic.get("thumb_sub", "ASLI WAJAH + FIX")
    f_s = font(84)
    w2 = d.textlength(sub, font=f_s) + 80
    d.rounded_rectangle((640 - w2 / 2, 560, 640 + w2 / 2, 680), radius=26, fill=(10, 10, 10, 235), outline=GOLD + (255,), width=6)
    d.text((640, 620), sub, font=f_s, fill=GOLD + (255,), anchor="mm")
    im.save(path, quality=93)


def real_thumbnail(frame, topic, path):
    """1280x720 click-thumbnail from a REAL footage frame. One focal point: huge 2-line hook on a warm, vignetted real photo
    (no extra badges/arrows). Text stays in the centre 70% so crops never cut it."""
    from PIL import ImageEnhance, ImageFilter
    im = Image.fromarray(frame).convert("RGB")
    im = _crop169(im, topic)
    im = ImageEnhance.Color(im).enhance(1.35)
    im = ImageEnhance.Contrast(im).enhance(1.18)
    # warm "heat" tint rising from the bottom, vignette at the edges
    heat = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
    hd = ImageDraw.Draw(heat)
    for y in range(720):
        hd.line([(0, y), (1280, y)], fill=(255, 70, 20, int(110 * (y / 720) ** 1.6)))
    im = Image.alpha_composite(im.convert("RGBA"), heat)
    vg = Image.new("L", (1280, 720), 0)
    vd = ImageDraw.Draw(vg)
    vd.ellipse((-260, -200, 1540, 920), fill=255)
    vg = vg.filter(ImageFilter.GaussianBlur(120))
    dark = Image.new("RGBA", (1280, 720), (0, 0, 0, 150))
    im = Image.composite(im, Image.alpha_composite(im, dark), vg).convert("RGB")
    d = ImageDraw.Draw(im, "RGBA")
    l1, l2 = topic["thumb"] if isinstance(topic["thumb"], (list, tuple)) else (topic["thumb"], "")
    text_c(d, (640, 215), l1, font(118), fill=GOLD, width=7)
    if l2:
        w = d.textlength(l2, font=font(128)) + 80
        d.rounded_rectangle((640 - w / 2, 330, 640 + w / 2, 490), radius=34, fill=(225, 25, 25, 255), outline=WHITE + (255,), width=6)
        text_c(d, (640, 410), l2, font(128), fill=WHITE, outline=(80, 0, 0), width=6)
    im.save(path, quality=93)


def wrap_lines(d, s, f, maxw):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=f) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def long_thumbnail(frame, topic, path):
    """Variant B (owner 2026-11-01: a colourful image with a LONG sentence also works, readers spend time on it):
    very saturated real photo, a full question in 3 stacked lines on dark bars, key word highlighted."""
    from PIL import ImageEnhance
    im = Image.fromarray(frame).convert("RGB")
    im = _crop169(im, topic)
    im = ImageEnhance.Color(im).enhance(1.7)
    im = ImageEnhance.Contrast(im).enhance(1.15)
    im = ImageEnhance.Brightness(im).enhance(1.08)
    d = ImageDraw.Draw(im, "RGBA")
    sentence = topic.get("thumb_long", topic["title"].upper())
    f = font(78)
    lines = wrap_lines(d, sentence, f, 1120)[:3]
    y = 80
    hot = topic.get("thumb_hot", "")
    for ln in lines:
        w_ = d.textlength(ln, font=f)
        d.rounded_rectangle((640 - w_ / 2 - 28, y - 6, 640 + w_ / 2 + 28, y + 100), radius=22, fill=(8, 10, 24, 215))
        col = RED if (hot and hot in ln) else WHITE
        d.text((640, y + 48), ln, font=f, fill=col + (255,) if col != WHITE else GOLD + (255,), anchor="mm")
        y += 118
    im.save(path, quality=93)


def thumbs_only(key, out_dir, cache_dir='bank_tech'):
    """Fast path: only the click thumbnails (no voice/video), from the topic's thumb_queries (else the first scene's queries)."""
    import story_real as SR
    topic = TOPICS[key]
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    pk = os.environ.get("PEXELS_API_KEY", "")
    best, best_s = None, -1e9
    used = set()
    for q in topic.get("thumb_queries") or topic["queries"][topic.get("thumb_scene", 0)]:
        try:
            paths = SR.get_footage(q, pk, cache_dir, used, 6.0, tries=2)
            if not paths:
                continue
            sc = SR.scene_video(paths, 6.0, np.zeros((H, W, 3), np.uint8), np.zeros((H, W), np.float32))
            fr = pick_thumb_frame(sc.plain.get_frame, 6.0)
            if fr is None:
                continue
            g = fr.mean(axis=2)
            s = float(np.abs(np.diff(g[::4, ::4], axis=1)).mean()) - 80 * float((g > 235).mean()) - 40 * float((g < 25).mean())
            if s > best_s:
                best, best_s = fr, s
        except Exception as e:
            print(f"[TECH] thumb query {q!r} skipped: {str(e)[:80]}")
    if best is None:
        raise RuntimeError("no thumbnail frame")
    Image.fromarray(best).save(out_dir / f"{key}_thumbframe.png")
    real_thumbnail(best, topic, out_dir / f"{key}_thumb.jpg")
    long_thumbnail(best, topic, out_dir / f"{key}_thumb_long.jpg")
    pattern_thumbnail(best, topic, out_dir / f"{key}_thumb_pattern.jpg")
    print("[TECH] thumbnails done")


def build(key, out_dir, real=False, cache_dir='bank_tech'):
    from moviepy.editor import VideoClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips
    from moviepy.audio.AudioClip import AudioArrayClip
    from story_real import normalize_voice
    import story_motion as SM
    topic = TOPICS[key]
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    n = len(topic["lines"])
    scenes, used, thumb_frame, thumbs_done = [], set(), None, False
    for i, line in enumerate(topic["lines"]):
        if i == n - 1 and SPOKEN_CTA.strip() not in line:
            line = line.rstrip() + SPOKEN_CTA
        ap = out_dir / f"{key}_{i}.mp3"
        # fast, energetic delivery; slightly lower pitch on the hook for weight
        rate, pitch = ("+26%", "+2Hz") if i == 0 else (("+20%", "+0Hz") if i < 4 else ("+18%", "+0Hz"))
        gv = gemini_voice(line, ap, i)
        if gv is None:
            E.make_voice(line, ap, rate, pitch)
            gv = ap
        voice = AudioFileClip(str(normalize_voice(gv)))
        dur = voice.duration + 0.35
        base = None
        if real:
            import story_real as SR
            pk = os.environ.get("PEXELS_API_KEY", "")
            if not pk:
                raise RuntimeError("PEXELS_API_KEY missing (real mode runs in CI)")
            Path(cache_dir).mkdir(parents=True, exist_ok=True)
            paths = []
            for q in topic["queries"][i]:
                paths = SR.get_footage(q, pk, cache_dir, used, dur)
                if paths:
                    break
            if not paths:
                raise RuntimeError(f"no footage for scene {i + 1}")
            sc = SR.scene_video(paths, dur, np.zeros((H, W, 3), np.uint8), np.zeros((H, W), np.float32), zoom_out=(i % 2 == 1))
            base = sc.plain.get_frame
            if i == topic.get("thumb_scene", 0):
                thumb_frame = pick_thumb_frame(base, dur)
        clip = VideoClip(frame_fn(topic, i, n, dur, base), duration=dur).set_fps(FPS)
        bed = SM.ambient(dur, mood="calm")
        rms = float(np.sqrt(np.mean(np.square(bed)))) or 1e-6
        bed = np.clip(bed * (0.02 / rms), -1, 1)
        bed = AudioArrayClip(np.stack([bed, bed], axis=1), fps=44100)
        w = whoosh()
        w = AudioArrayClip(np.stack([w, w], axis=1), fps=44100).set_start(0)
        clip = clip.set_audio(CompositeAudioClip([bed, w, voice.set_start(0.05)]).set_duration(dur))
        scenes.append(clip)
        print(f"[TECH:{key}] scene {i + 1}/{n} ok ({dur:.1f}s)")
    if real and topic.get("thumb_queries"):
        try:
            thumbs_only(key, out_dir, cache_dir)
            thumb_frame, thumbs_done = None, True   # thumbnails already written
        except Exception as e:
            print(f"[TECH] thumb_queries failed, using scene frame: {str(e)[:80]}")
    final = concatenate_videoclips(scenes, method="compose")
    mp4 = out_dir / f"{key}_tech.mp4"
    final.write_videofile(str(mp4), fps=FPS, codec="libx264", audio_codec="aac", preset="medium", logger=None)
    # thumbnail: hot-phone frame, big hook text
    thumb = out_dir / f"{key}_thumb.jpg"
    try:
        if thumbs_done:
            raise StopIteration
        if thumb_frame is not None:
            real_thumbnail(thumb_frame, topic, thumb)
            pattern_thumbnail(thumb_frame, topic, out_dir / f"{key}_thumb_pattern.jpg")
            long_thumbnail(thumb_frame, topic, out_dir / f"{key}_thumb_long.jpg")
            Image.fromarray(thumb_frame).save(out_dir / f"{key}_thumbframe.png")
            raise StopIteration
        fr = Image.fromarray(frame_fn(topic, 0, n, 6.0)(5.0)).convert("RGB")
        crop = fr.crop((0, 380, W, 380 + int(W * 9 / 16))).resize((1280, 720))
        d = ImageDraw.Draw(crop, "RGBA")
        d.rectangle((0, 0, 1280, 720), fill=(0, 0, 0, 60))
        text_c(d, (640, 110), topic["thumb"], font(110), fill=GOLD, width=6)
        crop.save(thumb, quality=92)
    except StopIteration:
        pass
    except Exception as e:
        print(f"[TECH] thumbnail skipped: {e}")
        thumb = None
    NL = chr(10)
    meta = {"title": topic["yt_title"], "tags": topic["tags"], "duration_s": round(final.duration, 1),
            "description": (topic["title"] + NL + NL + (topic.get("desc_extra", "") + NL + NL if topic.get("desc_extra") else "") + "Simple Hinglish explainer. This is an educational explainer. The voice is a synthetic (AI) voice; "
                            "diagrams are simplified illustrations." + NL + NL + "#TechExplained #HowItWorks #Hindi")}
    (out_dir / f"{key}_meta.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"[TECH:{key}] done: {mp4} ({meta['duration_s']}s)")
    return mp4, thumb, meta


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", default=None)
    ap.add_argument("--out", default="output/tech")
    ap.add_argument("--real", action="store_true")
    ap.add_argument("--thumbs-only", action="store_true")
    a = ap.parse_args()
    if a.sample and a.thumbs_only:
        thumbs_only(a.sample, a.out)
    elif a.sample:
        build(a.sample, a.out, real=a.real)
    else:
        print("usage: python tech_short.py --sample phone_heat")
