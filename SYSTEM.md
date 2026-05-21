# AI360Trading — SYSTEM.md v16.5
# Last Updated: 21 May 2026
# Owner: Amit Kumar, Haridwar | ai360trading@gmail.com
# Repo: https://github.com/systronics/ai360trading
# Website: https://ai360trading.in
# 6 family members depend on this system — ZERO errors allowed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RULE 1 FOR ANY AI — READ GITHUB FILE BEFORE ANY CODE CHANGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Raw URL format:
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/FILENAME

Always provide COMPLETE file — never partial snippets or diffs.
Cost must stay Rs.0/month forever.
Everything must be automated — never suggest manual work.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ALL RAW GITHUB URLS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/trading_bot.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/upload_youtube.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/upload_facebook.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/upload_kids_youtube.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/generate_reel.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/generate_reel_morning.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/generate_shorts.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/generate_kids_video.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/generate_education.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/generate_articles.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/ai_client.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/human_touch.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/token_refresh.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/indian_holidays.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/content_calendar.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/kids_content_calendar.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/requirements.txt
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/.github/workflows/trading_bot.yml
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/.github/workflows/daily-videos.yml
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/.github/workflows/daily-shorts.yml
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/.github/workflows/daily_reel.yml
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/.github/workflows/daily-articles.yml
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/.github/workflows/kids-daily.yml
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/.github/workflows/daily-morning-reel.yml
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/.github/workflows/token_refresh.yml
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/.github/workflows/keepalive.yml
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/SYSTEM.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# KEY IDs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ai360tradingAlgo sheet:     1fPNGL6AHs-7M-oC22zILg9FlyWi-7DF9NoVVqZQs2vk
ai360tradingRecomm sheet:   17qv8wKgxEDEylB74zUWzxCHESMhFWf8xz1tNzLSuRP8
Facebook Page ID:           108076910943724
Facebook Kids Page ID:      1021152881090398
Instagram Business ID:      17841400933677509
AppScript v15.6 Drive:      1cBimCblQZ_tISDxXZ_rqTlogPS4Ty17h

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONTENT SCHEDULE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
07:00 AM IST — Morning Reel (daily-morning-reel.yml) — EVERY DAY
08:00 AM IST — HerooQuest Kids (kids-daily.yml) — EVERY DAY — 3 jobs
10:00 AM IST — Education Video (daily-videos.yml) — MON-SAT
11:30 AM IST — Daily Shorts (daily-shorts.yml) — MON-FRI + SAT-SUN 1:30PM
08:30 PM IST — ZENO Evening Reel (daily_reel.yml) — EVERY DAY
Every 5 min  — Trading Bot (trading_bot.yml) — 8:15AM-4:29PM MON-FRI

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FILES STATUS — CURRENT GITHUB (21 May 2026)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
trading_bot.py          v15.0  ✅  Y1 memory fix, CHAT_ID correct
upload_facebook.py      v2.4   ✅  Instagram resumable upload fixed
                                   get_page_token() for page token
                                   IG Business ID: 17841400933677509
upload_youtube.py       v2.2   ✅  Shorts thumbnail skip (403 fix)
upload_kids_youtube.py  v2.3   ✅  30 SEO tags + story-specific thumbnail
generate_reel.py        v2.1   ✅  save_meta() defined + no bgmusic
generate_reel_morning.py v2.2  ✅  Live market data + sentiment
generate_shorts.py      v3.1   ✅  bgmusic removed
generate_kids_video.py  v2.3   ✅  Cinematic + Pollinations.ai
ai_client.py            v2.4   ✅  Groq + Gemini 2.5 + Anthropic + OpenAI
human_touch.py          v2.2   ✅  safe_thumbnail_text() + education hooks
token_refresh.py        v2.1   ✅  CHAT_ID_BASIC fix
requirements.txt        v2.3   ✅  google-genai added
daily-morning-reel.yml  v2.2   ✅  7 days/week
daily-videos.yml        v2.2   ✅  10 AM IST
daily-shorts.yml        v2.1   ✅  All 4 AI keys + INSTAGRAM_BUSINESS_ACCOUNT_ID
daily_reel.yml          v2.1   ✅  All 4 AI keys + INSTAGRAM_BUSINESS_ACCOUNT_ID
kids-daily.yml          v2.1   ✅  3 separate jobs
token_refresh.yml       v2.2   ✅  1st + 15th monthly
trading_bot.yml         v2.1   ✅  CHAT_ID_BASIC correct

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# APPSCRIPT STATUS (21 May 2026)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Version: v15.6 + timeout fixes applied ✅
Location: Ai360tradingAlgo → Extensions → Apps Script (NOT in GitHub)
Drive backup: 1cBimCblQZ_tISDxXZ_rqTlogPS4Ty17h

Applied fixes:
  ✅ Hard bearish block (score>=40, Sector Leader, RS>=15)
  ✅ Momentum breakout detection
  ✅ Options ATH block
  ✅ Volume bypass for +3% movers
  ✅ Sector momentum detection
  ✅ Options row offset fix
  ✅ VIX fetch deadline:5 (timeout fix)
  ✅ Skip momentumSectors scan in BEARISH (timeout fix)
  ✅ Batch setValues() for options columns (timeout fix)

AlertLog sheet:
  ✅ Column Y added (right-click col X → insert right — DONE)
  ✅ T4 cell cleared (DONE)
  Memory: Y1 = Python bot memory | BotMemory sheet = AppScript memory

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FACEBOOK + INSTAGRAM STATUS (21 May 2026)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Token type: Page Token ✅ (NOT User Token — this was root cause of all failures)
How to generate correctly:
  Graph Explorer → User or Page → Get Page Access Token
  → Edit Settings → Opt in all and future pages → Continue
  → Copy token → Exchange for 60-day → GitHub META_ACCESS_TOKEN

Exchange URL:
  https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token
  &client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=SHORT_TOKEN

Verify: https://graph.facebook.com/me/accounts?access_token=YOUR_TOKEN
Should return both pages:
  {"id": "108076910943724", "name": "AI360 Trading"}
  {"id": "1021152881090398", "name": "HerooQuest"}

META_ACCESS_TOKEN: ✅ Updated with Page Token (21 May 2026, 60-day)
Token refresh: Automatic 1st + 15th every month via token_refresh.yml

Instagram:
  Business Account ID: 17841400933677509 ✅
  Professional account ✅
  Linked to Facebook Page ✅
  upload_facebook.py v2.4 handles upload ✅
  FIRST SUCCESSFUL POST: ID 17894455140330590 (20 May 2026) ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PLATFORMS STATUS (21 May 2026)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YouTube AI360:          ✅ Auto
YouTube HerooQuest:     ✅ Auto — 3 videos/day, story thumbnails
Facebook AI360:         ✅ Fixed — Page Token updated
Facebook HerooQuest:    ✅ Auto
Instagram AI360:        ✅ Working — first post confirmed
GitHub Pages:           ✅ Auto — articles
Telegram (3 channels):  ✅ Auto
Facebook Group:         ❌ Manual — needs Advanced Access

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TRADING STATUS (21 May 2026)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Market: BEARISH (Nifty 23666 < 20DMA 23993)
Paper trades: 3W / 5L | Win rate 37.5%
All 5 losses = entered in BEARISH market
v15.6 hard block prevents new bearish entries

Active trades:
  ONGC  → Entry 298.35 | SL 293.45 | Day 7
  BHEL  → Entry 396.95 | SL 382.75 | Day 7 | +2.99%
  IDEA  → Entry 13.06  | SL 12.54  | Day 5 | +3.83% near target ₹14.10

History wins:  BSE +3.87% | IDEA +5.94% | ADANIPORTS +5.58%
History loss:  BHARATFORG | TATASTEEL | BANDHANBNK | SAIL | NESTLEIND
               (all entered in BEARISH — v15.6 blocks these now)

Phase 4: 30 paper trades → live Rs.1,000 | Currently 8 done, 22 more needed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PENDING TASKS (what is NOT done yet)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 URGENT:
  1. generate_shorts.py: Add Instagram upload
     Same pattern as upload_facebook.py v2.4
     generate_shorts.py handles FB upload internally (not separate step)
     Need to add upload_reel_to_instagram() call after FB upload in file

🟡 NEXT SESSION:
  2. AppScript v15.7: _runPositionalScanner()
     Drive: 1-ZmoNcMVXK1EdLDHCvyRYLYZNwq4uj9S
     ADD to END of v15.6 code (not replace)
     Update onOpen() menu to add "📈 UPDATE POSITIONAL PICKS"
     Run setupPositionalTrigger() once → Sunday 6PM auto trigger

  3. Positional Picks page (ai360trading.in/positional-picks/)
     Sheet tab PositionalPicks (gid=566178621) needs data
     Either manual add OR run AppScript v15.7 scanner

  4. Facebook Group Advanced Access
     Go to: business.facebook.com → Advanced Access application

🟢 FUTURE:
  5. Kling AI $6/month for HerooQuest true animation
  6. Phase 4: Live trading Rs.1,000 after 30 paper trades
  7. English YouTube channel (YOUTUBE_CREDENTIALS_EN secret needed)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GITHUB SECRETS (all required)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
META_ACCESS_TOKEN              ← Page Token — updated 21 May 2026
META_ACCESS_TOKEN_KIDS         ← HerooQuest page token
META_APP_ID                    ← Facebook App ID
META_APP_SECRET                ← Facebook App Secret
FACEBOOK_PAGE_ID               ← 108076910943724
FACEBOOK_KIDS_PAGE_ID          ← 1021152881090398
INSTAGRAM_BUSINESS_ACCOUNT_ID  ← 17841400933677509
YOUTUBE_CREDENTIALS            ← AI360 Trading YouTube OAuth
YOUTUBE_CREDENTIALS_KIDS       ← HerooQuest YouTube OAuth
GROQ_API_KEY                   ← Primary AI (100k/day free)
GEMINI_API_KEY                 ← Gemini 2.5 Flash
ANTHROPIC_API_KEY              ← Claude fallback
OPENAI_API_KEY                 ← GPT fallback
HF_TOKEN                       ← HuggingFace FLUX.1
TELEGRAM_BOT_TOKEN             ← Bot token
CHAT_ID_BASIC                  ← Free channel
CHAT_ID_ADVANCE                ← Rs.499/month channel
CHAT_ID_PREMIUM                ← Bundle channel
GH_TOKEN                       ← GitHub API for secret updates
GCP_SERVICE_ACCOUNT_JSON       ← Google Sheets for trading bot

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DRIVE FILE REGISTRY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
upload_facebook.py v2.4:        1YXYYS9E8OCTfOWvBbI9pXiWsJW4GN1Yf
upload_kids_youtube.py v2.3:    1WTMEMxPBN_o6ut4Xqo0jtVaWQ6c2fqpv
generate_reel.py v2.1 FINAL:    1-0vTOtn_71vMVoAqMyB51b962tpyFj7b
AppScript v15.6:                1cBimCblQZ_tISDxXZ_rqTlogPS4Ty17h
AppScript v15.7 positional:     1-ZmoNcMVXK1EdLDHCvyRYLYZNwq4uj9S
swing-dashboard.html FINAL:     1_ekz3KUE69n2ifkhiCywBWyFWlRgA-Kb
positional-picks.html FINAL:    1VbXmUnre6bUJLgDF9Vp1v_AC-6BUgHrN
SYSTEM.md v16.5:                1CrT4gs-EjvbYHO6QGKGXHBoPHmsFTVPO
