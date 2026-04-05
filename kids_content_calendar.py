# kids_content_calendar.py
# Auto-picks daily topic for US/UK/DE/CN/IN kids audience
import datetime, random, os

CATEGORIES = {
    "historical": [
        {"hi": "अकबर और बीरबल की कहानी", "en": "Akbar and Birbal — The Wise Minister", "tags": ["India","Mughal","history"]},
        {"hi": "नासा का पहला चाँद मिशन", "en": "Apollo 11 — First Moon Landing Story", "tags": ["NASA","space","USA"]},
        {"hi": "विश्व युद्ध की कहानी बच्चों के लिए", "en": "World War II for Kids — Brave Stories", "tags": ["WW2","history","UK"]},
        {"hi": "महान दीवार चीन की कहानी", "en": "The Great Wall of China — Epic Story", "tags": ["China","history","architecture"]},
        {"hi": "रानी एलिज़ाबेथ की कहानी", "en": "Queen Elizabeth — A Royal Story for Kids", "tags": ["UK","royals","history"]},
        {"hi": "आइंस्टीन की बचपन की कहानी", "en": "Young Einstein — The Boy Who Changed Science", "tags": ["Germany","science","biography"]},
    ],
    "religious": [
        {"hi": "रामायण — राम और हनुमान", "en": "Ramayana — The Story of Rama for Kids", "tags": ["Hindu","India","mythology"]},
        {"hi": "बुद्ध की ज्ञान की कहानी", "en": "Buddha — The Prince Who Found Peace", "tags": ["Buddhism","India","spiritual"]},
        {"hi": "ईसा मसीह की प्रेम की कहानी", "en": "Jesus and the Power of Kindness", "tags": ["Christianity","Bible","USA","UK"]},
        {"hi": "गुरु नानक देव की कहानी", "en": "Guru Nanak — Founder of Sikhism", "tags": ["Sikhism","India","Punjab"]},
        {"hi": "महाभारत — अर्जुन की सीख", "en": "Mahabharata — Arjuna's Greatest Lesson", "tags": ["Hindu","India","mythology"]},
    ],
    "science": [
        {"hi": "डायनासोर क्यों विलुप्त हुए?", "en": "Why Did Dinosaurs Disappear? — Science for Kids", "tags": ["dinosaurs","science","USA","UK"]},
        {"hi": "ब्लैक होल क्या होता है?", "en": "What is a Black Hole? — Space for Kids", "tags": ["space","NASA","science"]},
        {"hi": "समुद्र की गहराई में क्या है?", "en": "Deep Ocean Mysteries for Kids", "tags": ["ocean","science","nature"]},
        {"hi": "मानव शरीर कैसे काम करता है?", "en": "How Does the Human Body Work?", "tags": ["biology","health","education"]},
        {"hi": "ज्वालामुखी कैसे फटता है?", "en": "How Volcanoes Erupt — Earth Science for Kids", "tags": ["geology","science","nature"]},
    ],
    "moral_stories": [
        {"hi": "पंचतंत्र — शेर और चूहा", "en": "The Lion and the Mouse — Panchatantra", "tags": ["India","moral","Panchatantra"]},
        {"hi": "ईसप की कहानी — कछुआ और खरगोश", "en": "The Tortoise and the Hare — Aesop's Fables", "tags": ["Aesop","moral","UK","USA"]},
        {"hi": "ईमानदारी सबसे बड़ी ताकत", "en": "Honesty is the Greatest Strength — World Folk Tales", "tags": ["moral","global","values"]},
    ],
    "emotional": [
        {"hi": "असली दोस्ती की कहानी", "en": "The Power of True Friendship — Animated Story", "tags": ["friendship","emotional","kids"]},
        {"hi": "हिम्मत से हर मुश्किल हल होती है", "en": "Courage — The Boy Who Never Gave Up", "tags": ["courage","motivation","kids"]},
        {"hi": "माँ की ममता — एक दिल छूने वाली कहानी", "en": "A Mother's Love — Emotional Story for Kids", "tags": ["family","emotional","India"]},
    ],
    "biographies": [
        {"hi": "APJ अब्दुल कलाम — मिसाइल मैन की कहानी", "en": "APJ Abdul Kalam — Missile Man of India", "tags": ["India","science","biography"]},
        {"hi": "मैरी क्यूरी — पहली महिला वैज्ञानिक", "en": "Marie Curie — First Woman to Win Nobel Prize", "tags": ["science","biography","Germany","UK"]},
        {"hi": "नेल्सन मंडेला की हिम्मत की कहानी", "en": "Nelson Mandela — Freedom Fighter for Kids", "tags": ["biography","courage","global"]},
    ],
    "fairy_tales": [
        {"hi": "जादुई जंगल की परी कहानी", "en": "The Enchanted Forest — A Magical Fairy Tale", "tags": ["fairy tale","magic","UK","USA"]},
        {"hi": "ड्रैगन और बहादुर बच्चा", "en": "The Dragon and the Brave Child — Fantasy Story", "tags": ["dragon","fantasy","China","USA"]},
    ],
    "geography": [
        {"hi": "भारत की अद्भुत जगहें बच्चों के लिए", "en": "Amazing Places of India — Kids Geography", "tags": ["India","travel","geography"]},
        {"hi": "जर्मनी — बच्चों के लिए दुनिया की सैर", "en": "Germany for Kids — Castles, Cars and Culture", "tags": ["Germany","geography","Europe"]},
        {"hi": "चीन की दीवार से ड्रैगन तक", "en": "China for Kids — Dragons, Food and Traditions", "tags": ["China","culture","geography"]},
    ],
}

# CPM priority weights per country
COUNTRY_WEIGHTS = {
    "historical": ["USA","UK","IN","DE","CN"],
    "religious":  ["IN","USA","UK","DE"],
    "science":    ["USA","UK","DE","CN","IN"],
    "moral_stories": ["IN","USA","UK"],
    "emotional":  ["IN","UK","USA"],
    "biographies":["IN","USA","UK","DE"],
    "fairy_tales":["USA","UK","DE","CN"],
    "geography":  ["USA","UK","IN","DE","CN"],
}

# Category rotation seeded by day-of-year for zero repetition within a week
CATEGORY_ROTATION = [
    "historical","science","moral_stories","religious","emotional",
    "biographies","fairy_tales","geography","historical","science",
    "moral_stories","emotional","biographies","religious","geography",
]

def get_today_topic() -> dict:
    today = datetime.date.today()
    day_of_year = today.timetuple().tm_yday
    category = CATEGORY_ROTATION[day_of_year % len(CATEGORY_ROTATION)]
    items = CATEGORIES[category]
    topic = items[day_of_year % len(items)]
    return {
        "category": category,
        "hindi_title": topic["hi"],
        "english_title": topic["en"],
        "seo_tags": topic["tags"],
        "target_countries": COUNTRY_WEIGHTS.get(category, ["IN","USA","UK"]),
        "date": today.isoformat(),
    }

if __name__ == "__main__":
    import json
    print(json.dumps(get_today_topic(), ensure_ascii=False, indent=2))
