"""tech_topics3.py v1.0 (2026-11-07) - four more AI360 Technology Short topics chosen from REAL search data (free YouTube/Google autocomplete, `_data/tech_keywords.json`, 2026-11-07):
'phone ki battery jaldi khatam ho jati hai', 'mobile virus kaise hataye', 'whatsapp hack kaise pata kare', 'digital arrest scam'. Same rules as tech_topics2: simple Hinglish (Devanagari narration),
facts only, no invented numbers (the only digit is the real national cyber-crime helpline 1930, spoken as words), no risky repair advice, no brand names except WhatsApp where the topic IS that app,
a clear 'what to do' ending, and a closing line that never promises a specific next video. Registered into tech_short.TOPICS by register() (fail-open)."""

ORDER = ["battery_drain", "digital_arrest", "mobile_virus", "whatsapp_hack"]
NEXT = " कल मिलते हैं एक नई टेक प्रॉब्लम के साथ।"


def _t(**k):
    k.setdefault("tag", "ROZ KI TECH")
    return k


OBJ3D = {
    "battery_drain": "a smartphone with a nearly empty glowing red battery icon and small energy particles draining away",
    "digital_arrest": "a smartphone video-call screen with a red warning triangle and handcuffs icon",
    "mobile_virus": "a smartphone with a glowing red bug-shaped virus icon and a cracked shield",
    "whatsapp_hack": "a smartphone showing a generic green chat bubble icon with a red broken padlock",
}

THUMB_QUERIES = {
    "battery_drain": ["smartphone low battery close up", "phone battery icon screen close up"],
    "digital_arrest": ["smartphone video call close up", "phone ringing unknown number close up"],
    "mobile_virus": ["smartphone warning screen close up", "phone apps screen close up"],
    "whatsapp_hack": ["smartphone messages notification close up", "phone lock screen close up"],
}

TOPICS3 = {
    "battery_drain": _t(
        title="Phone Ki Battery Jaldi Khatam Kyu Hoti Hai?", yt_title="Phone Ki Battery Jaldi Khatam Kyu Hoti Hai? 5 Asli Wajah #shorts", kind="explain", badge="BATTERY", icon="battery", tint="orange",
        thumb=("BATTERY", "KHATAM?"), thumb_hi="बैटरी जल्दी क्यों ख़त्म होती है?", thumb_sub="ASLI WAJAH + FIX", thumb_long="PHONE KI BATTERY JALDI KHATAM KYU HOTI HAI? ASLI WAJAH AUR FIX", thumb_hot="KHATAM",
        tags=["phone ki battery jaldi khatam kyu hoti hai", "battery jaldi khatam hone ka solution", "mobile battery tips hinglish", "battery drain fix", "tech tips hinglish", "shorts"],
        lines=[
            "फ़ोन की बैटरी इतनी जल्दी ख़त्म क्यों हो जाती है? इसकी पाँच बड़ी वजह आज समझ लो।",
            "सबसे बड़ी वजह स्क्रीन है। तेज़ ब्राइटनेस और स्क्रीन ऑन रहना, सबसे ज़्यादा बैटरी खाता है। ब्राइटनेस ऑटो पर रखो।",
            "दूसरी, बैकग्राउंड में चलते ऐप। सेटिंग में बैटरी यूज़ खोलो, जो ऐप सबसे ज़्यादा खा रहा हो, उसे रोको या हटाओ।",
            "तीसरी, कमज़ोर नेटवर्क। जहाँ सिग्नल कम होता है, फ़ोन ज़्यादा ज़ोर लगाता है। और गर्मी, लोकेशन हमेशा ऑन रखना भी बैटरी खींचता है।",
            "और अगर फ़ोन बहुत पुराना है, तो बैटरी ख़ुद कमज़ोर हो चुकी होगी। तब बैटरी बदलवाओ, पर किसी टेक्नीशियन से, खुद फ़ोन मत खोलना।" + NEXT,
        ],
        caps=["BATTERY JALDI KYU?", "SCREEN = BADA KHARCHA", "BACKGROUND APP ROKO", "KAMZOR SIGNAL = ZYADA ZOR", "PURANI BATTERY: TECHNICIAN"],
        scenes=[{"type": "card", "lines": ["BATTERY JALDI", "KHATAM KYU?"], "color": "orange"},
                {"type": "bars2", "rows": [("SCREEN TEZ + ON", 0.9, "red"), ("AUTO BRIGHTNESS", 0.35, "green")]},
                {"type": "tips", "items": ["SETTINGS: BATTERY USE", "SABSE ZYADA WALA ROKO", "NAYA UPDATE KARO"]},
                {"type": "bars2", "rows": [("KAMZOR SIGNAL", 0.8, "red"), ("ACHHA SIGNAL", 0.3, "green")]},
                {"type": "card", "lines": ["PURANA PHONE?", "BATTERY TECHNICIAN SE"], "color": "green"}],
        queries=[["smartphone low battery screen", "phone battery icon close up"], ["bright phone screen night", "hand scrolling smartphone"],
                 ["smartphone settings screen", "mobile apps screen close up"], ["smartphone signal bars close up", "phone network icon"],
                 ["phone repair technician", "smartphone repair shop"]]),
    "digital_arrest": _t(
        title="Digital Arrest Scam Kya Hai?", yt_title="Digital Arrest Scam Kya Hai? Aise Bacho #shorts", kind="serious", badge="SCAM ALERT", icon="warn", tint="red",
        thumb=("DIGITAL", "ARREST?"), thumb_hi="डिजिटल अरेस्ट: सच या ठगी?", thumb_sub="AISE BACHO", thumb_long="DIGITAL ARREST SCAM KYA HAI? VIDEO CALL PAR DARAYE TO AISE BACHO", thumb_hot="ARREST",
        tags=["digital arrest scam kya hai", "digital arrest scam se kaise bache", "cyber fraud hinglish", "cyber crime helpline 1930", "tech tips hinglish", "shorts"],
        lines=[
            "कोई वीडियो कॉल पर कहे, आप डिजिटल अरेस्ट हैं, तो ये क्या है? ये एक ठगी है, इससे सावधान रहो।",
            "ठग ख़ुद को पुलिस या जाँच एजेंसी का अफ़सर बताते हैं, वर्दी दिखाते हैं, और कहते हैं कि आप वीडियो कॉल पर बने रहो।",
            "फिर डर दिखाकर कहते हैं कि पैसे जाँच के लिए भेजो। याद रखो, कोई असली एजेंसी वीडियो कॉल पर डिजिटल अरेस्ट नहीं करती।",
            "ऐसा कॉल आए तो घबराओ मत, कॉल काट दो, और किसी को पैसे या बैंक की जानकारी मत दो। घर वालों से बात करो।",
            "ठगी हो जाए, तो तुरंत एक नौ तीन शून्य पर कॉल करो और बैंक को बताओ। डर के आगे रुकना ही बचाव है।" + NEXT,
        ],
        caps=["DIGITAL ARREST = THAGI", "FAKE OFFICER, FAKE VARDI", "PAISE BHEJO = THAGI", "CALL KAAT DO, RUKO", "THAGI HO TO: 1930"],
        scenes=[{"type": "card", "lines": ["DIGITAL ARREST", "= THAGI"], "color": "red"},
                {"type": "bars2", "rows": [("VIDEO CALL PAR 'OFFICER'", 0.9, "red"), ("ASLI AGENCY KA TAREEKA", 0.05, "green")]},
                {"type": "card", "lines": ["PAISE BHEJO?", "SEEDHI THAGI"], "color": "red"},
                {"type": "tips", "items": ["CALL KAAT DO", "BANK DETAIL MAT DO", "GHAR WALON SE BAAT KARO"]},
                {"type": "card", "lines": ["THAGI HO TO:", "1930 PAR CALL"], "color": "green"}],
        queries=[["smartphone video call close up", "phone incoming call close up"], ["laptop video call screen", "smartphone calling dark"],
                 ["upi payment smartphone", "mobile banking app close up"], ["ending phone call close up", "hand putting phone down"],
                 ["calling phone close up", "smartphone call screen"]]),
    "mobile_virus": _t(
        title="Mobile Mein Virus Hai Ya Nahi, Kaise Pata Kare?", yt_title="Mobile Mein Virus Hai Ya Nahi? Kaise Pata Kare Aur Hataye #shorts", kind="serious", badge="VIRUS?", icon="warn", tint="red",
        thumb=("MOBILE", "VIRUS?"), thumb_hi="फ़ोन में वायरस है?", thumb_sub="PEHCHANO + HATAO", thumb_long="MOBILE MEIN VIRUS HAI YA NAHI? KAISE PATA KARE AUR HATAYE", thumb_hot="VIRUS",
        tags=["mobile virus kaise hataye", "mobile mein virus hai ya nahi kaise pata kare", "phone virus remove hinglish", "phone safety tips", "tech tips hinglish", "shorts"],
        lines=[
            "फ़ोन में वायरस है या नहीं, कैसे पता चले? पहले ये निशानियाँ देखो।",
            "अचानक बहुत सारे विज्ञापन आना, ऐसे ऐप दिखना जो आपने इंस्टॉल नहीं किए, और बैटरी और डेटा का बहुत जल्दी ख़त्म होना, ये ख़तरे की निशानी हैं।",
            "सबसे पहले सेटिंग में जाकर ऐप की लिस्ट देखो, और जो ऐप अनजान लगे, उसे हटा दो।",
            "आगे से ऐप सिर्फ़ ऑफ़िशियल ऐप स्टोर से लो। व्हाट्सऐप या किसी लिंक से आई एपीके फ़ाइल कभी इंस्टॉल मत करो।",
            "फिर भी ठीक न हो, तो ज़रूरी डेटा का बैकअप लो, फ़ोन रीसेट करो, या किसी टेक्नीशियन को दिखाओ। सावधानी ही सबसे बड़ा एंटीवायरस है।" + NEXT,
        ],
        caps=["VIRUS KI NISHANI", "AJEEB ADS + ANJAAN APP", "ANJAAN APP HATAO", "SIRF OFFICIAL APP STORE", "BACKUP, RESET YA TECHNICIAN"],
        scenes=[{"type": "card", "lines": ["MOBILE MEIN", "VIRUS HAI?"], "color": "red"},
                {"type": "tips", "items": ["AJEEB ADS BAHUT", "ANJAAN APP DIKHE", "BATTERY + DATA JALDI KHATAM"]},
                {"type": "card", "lines": ["SETTINGS: APPS", "ANJAAN APP HATAO"], "color": "gold"},
                {"type": "bars2", "rows": [("OFFICIAL APP STORE", 0.1, "green"), ("APK FILE LINK SE", 0.9, "red")]},
                {"type": "card", "lines": ["NA THEEK HO TO:", "BACKUP + TECHNICIAN"], "color": "green"}],
        queries=[["smartphone warning screen close up", "phone screen pop up close up"], ["smartphone apps grid close up", "mobile apps screen"],
                 ["smartphone settings screen", "hand tapping phone settings"], ["app store smartphone close up", "downloading app phone"],
                 ["phone repair technician", "smartphone repair shop"]]),
    "whatsapp_hack": _t(
        title="WhatsApp Hack Hua Hai Kaise Pata Kare?", yt_title="WhatsApp Hack Hua Hai Kaise Pata Kare? Aise Bachao #shorts", kind="serious", badge="HACK?", icon="lock", tint="red",
        thumb=("WHATSAPP", "HACK?"), thumb_hi="व्हाट्सऐप हैक हुआ है?", thumb_sub="AISE PATA KARO", thumb_long="WHATSAPP HACK HUA HAI KAISE PATA KARE? AISE BACHAO", thumb_hot="HACK",
        tags=["whatsapp hack kaise pata kare", "whatsapp hack hone se kaise bache", "whatsapp security hinglish", "cyber crime helpline 1930", "tech tips hinglish", "shorts"],
        lines=[
            "व्हाट्सऐप हैक हुआ है या नहीं, कैसे पता करें? ये तीन चीज़ें देखो।",
            "पहली, आपके नाम से दोस्तों को अजीब मैसेज या पैसे माँगने के मैसेज जा रहे हों। दूसरी, अचानक ऐप से लॉग आउट हो जाना।",
            "तीसरी, सेटिंग में लिंक्ड डिवाइसेज़ खोलो। अगर कोई अनजान डिवाइस दिखे, तो उसे तुरंत लॉग आउट कर दो।",
            "बचने के लिए टू-स्टेप वेरिफ़िकेशन चालू करो। और छह अंकों का कोड किसी को मत बताओ, दोस्त बनकर माँगे तब भी नहीं।",
            "हैक हो जाए, तो अपने नंबर से दोबारा लॉग इन करो, दोस्तों को बताओ, और एक नौ तीन शून्य पर शिकायत करो। कोड किसी को नहीं।" + NEXT,
        ],
        caps=["HACK KI NISHANI", "AAPKE NAAM SE AJEEB MSG", "LINKED DEVICES CHECK KARO", "TWO-STEP ON, CODE SECRET", "HACK HO TO: 1930"],
        scenes=[{"type": "card", "lines": ["WHATSAPP", "HACK HUA?"], "color": "red"},
                {"type": "tips", "items": ["AAPKE NAAM SE AJEEB MSG", "ACHANAK LOG OUT", "ANJAAN DEVICE LINKED"]},
                {"type": "card", "lines": ["SETTINGS: LINKED", "DEVICES CHECK KARO"], "color": "gold"},
                {"type": "bars2", "rows": [("CODE KISI KO DIYA: KHATRA", 0.95, "red"), ("TWO-STEP ON: SAFE", 0.15, "green")]},
                {"type": "card", "lines": ["HACK HO TO:", "1930 PAR SHIKAYAT"], "color": "green"}],
        queries=[["smartphone chat messages close up", "texting on smartphone close up"], ["smartphone notification close up", "phone lock screen close up"],
                 ["smartphone settings screen", "hand tapping phone settings"], ["typing pin on smartphone", "smartphone security lock close up"],
                 ["calling phone close up", "smartphone call screen"]]),
}


def register(topics):
    """Add the topics to tech_short.TOPICS (never overwrites an existing key)."""
    for k, v in TOPICS3.items():
        if k in THUMB_QUERIES:
            v.setdefault("thumb_queries", THUMB_QUERIES[k])
        topics.setdefault(k, v)
    return topics
