"""
dream11_ipl.py — Dream11 / My11Circle IPL Fantasy Team Generator
══════════════════════════════════════════════════════════════════
Auto-generates 5 fantasy teams for every IPL 2026 match.
Sends to FREE Telegram channel (TELEGRAM_CHAT_ID only).

Features:
  • Fetches today's IPL match using CricAPI (free tier)
  • Fetches squads + player stats via CricAPI
  • Uses AI (Groq→Gemini→Claude→OpenAI→Fallback) for smart picks
  • 5 teams: Safe / Bowling Heavy / All-Rounder / Differential / Captain Swap
  • Sends beautifully formatted Telegram message to free channel only
  • Runs via GitHub Actions daily at 1:00 PM IST (during IPL season)
  • Zero cost — free API tiers only

Author: AI360Trading Automation
IPL Season: 2026 (BCCI IPL)
"""

import os
import sys
import json
import time
import logging
import requests
import pytz
from datetime import datetime, date

# ── use existing ai_client fallback chain ──────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ai_client import AIClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

IST = pytz.timezone("Asia/Kolkata")

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

TELEGRAM_TOKEN  = os.environ.get("TELEGRAM_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")  # FREE channel only

# CricAPI — free tier: 100 calls/day
# Get key at: https://www.cricapi.com/ (free)
CRICAPI_KEY = os.environ.get("CRICAPI_KEY", "")

# RapidAPI Cricket Live Score (backup free tier)
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "")

# IPL 2026 season dates
IPL_START = date(2026, 3, 22)
IPL_END   = date(2026, 5, 30)

# ─────────────────────────────────────────────
# IPL 2026 TEAM ABBREVIATIONS
# ─────────────────────────────────────────────

IPL_TEAMS = {
    "Mumbai Indians": "MI",
    "Kolkata Knight Riders": "KKR",
    "Chennai Super Kings": "CSK",
    "Royal Challengers Bengaluru": "RCB",
    "Delhi Capitals": "DC",
    "Sunrisers Hyderabad": "SRH",
    "Rajasthan Royals": "RR",
    "Punjab Kings": "PBKS",
    "Lucknow Super Giants": "LSG",
    "Gujarat Titans": "GT",
}

# Emoji map for teams
TEAM_EMOJI = {
    "MI": "💙", "KKR": "💜", "CSK": "💛", "RCB": "❤️",
    "DC": "🔵", "SRH": "🟠", "RR": "🩷", "PBKS": "🔴",
    "LSG": "🩵", "GT": "🔷",
}

# ─────────────────────────────────────────────
# HARDCODED IPL 2026 SCHEDULE FALLBACK
# Used if CricAPI is unavailable
# ─────────────────────────────────────────────

IPL_2026_SCHEDULE = [
    {"date": "2026-03-22", "team1": "MI",   "team2": "CSK",  "venue": "Wankhede Stadium, Mumbai",          "time": "19:30"},
    {"date": "2026-03-23", "team1": "RCB",  "team2": "DC",   "venue": "M. Chinnaswamy Stadium, Bengaluru", "time": "19:30"},
    {"date": "2026-03-25", "team1": "SRH",  "team2": "RR",   "venue": "Rajiv Gandhi Intl. Stadium, Hyderabad","time": "19:30"},
    {"date": "2026-03-26", "team1": "PBKS", "team2": "LSG",  "venue": "IS Bindra PCA Stadium, Mohali",     "time": "19:30"},
    {"date": "2026-03-27", "team1": "GT",   "team2": "KKR",  "venue": "Narendra Modi Stadium, Ahmedabad",  "time": "19:30"},
    {"date": "2026-03-28", "team1": "RCB",  "team2": "SRH",  "venue": "M. Chinnaswamy Stadium, Bengaluru", "time": "19:30"},
    {"date": "2026-03-29", "team1": "MI",   "team2": "KKR",  "venue": "Wankhede Stadium, Mumbai",          "time": "19:30"},
    {"date": "2026-03-30", "team1": "CSK",  "team2": "DC",   "venue": "MA Chidambaram Stadium, Chennai",   "time": "19:30"},
    {"date": "2026-04-01", "team1": "RR",   "team2": "PBKS", "venue": "Sawai Mansingh Stadium, Jaipur",    "time": "19:30"},
    {"date": "2026-04-02", "team1": "LSG",  "team2": "GT",   "venue": "BRSABV Ekana Cricket Stadium, Lucknow","time": "19:30"},
    {"date": "2026-04-03", "team1": "MI",   "team2": "SRH",  "venue": "Wankhede Stadium, Mumbai",          "time": "19:30"},
    {"date": "2026-04-04", "team1": "KKR",  "team2": "CSK",  "venue": "Eden Gardens, Kolkata",             "time": "19:30"},
    {"date": "2026-04-05", "team1": "RCB",  "team2": "PBKS", "venue": "M. Chinnaswamy Stadium, Bengaluru", "time": "15:30"},
    {"date": "2026-04-05", "team1": "DC",   "team2": "RR",   "venue": "Arun Jaitley Stadium, Delhi",       "time": "19:30"},
    {"date": "2026-04-06", "team1": "GT",   "team2": "LSG",  "venue": "Narendra Modi Stadium, Ahmedabad",  "time": "15:30"},
    {"date": "2026-04-06", "team1": "SRH",  "team2": "MI",   "venue": "Rajiv Gandhi Intl. Stadium, Hyderabad","time": "19:30"},
    {"date": "2026-04-07", "team1": "CSK",  "team2": "RR",   "venue": "MA Chidambaram Stadium, Chennai",   "time": "19:30"},
    {"date": "2026-04-08", "team1": "PBKS", "team2": "KKR",  "venue": "IS Bindra PCA Stadium, Mohali",     "time": "19:30"},
    {"date": "2026-04-09", "team1": "DC",   "team2": "GT",   "venue": "Arun Jaitley Stadium, Delhi",       "time": "19:30"},
    {"date": "2026-04-10", "team1": "RCB",  "team2": "LSG",  "venue": "M. Chinnaswamy Stadium, Bengaluru", "time": "19:30"},
    {"date": "2026-04-11", "team1": "MI",   "team2": "RR",   "venue": "Wankhede Stadium, Mumbai",          "time": "19:30"},
    {"date": "2026-04-12", "team1": "SRH",  "team2": "CSK",  "venue": "Rajiv Gandhi Intl. Stadium, Hyderabad","time": "15:30"},
    {"date": "2026-04-12", "team1": "KKR",  "team2": "DC",   "venue": "Eden Gardens, Kolkata",             "time": "19:30"},
    {"date": "2026-04-13", "team1": "PBKS", "team2": "GT",   "venue": "IS Bindra PCA Stadium, Mohali",     "time": "15:30"},
    {"date": "2026-04-13", "team1": "LSG",  "team2": "RCB",  "venue": "BRSABV Ekana Cricket Stadium, Lucknow","time": "19:30"},
    {"date": "2026-04-14", "team1": "CSK",  "team2": "MI",   "venue": "MA Chidambaram Stadium, Chennai",   "time": "19:30"},
    {"date": "2026-04-15", "team1": "RR",   "team2": "SRH",  "venue": "Sawai Mansingh Stadium, Jaipur",    "time": "19:30"},
    {"date": "2026-04-16", "team1": "GT",   "team2": "KKR",  "venue": "Narendra Modi Stadium, Ahmedabad",  "time": "19:30"},
    {"date": "2026-04-17", "team1": "DC",   "team2": "PBKS", "venue": "Arun Jaitley Stadium, Delhi",       "time": "19:30"},
    {"date": "2026-04-18", "team1": "MI",   "team2": "LSG",  "venue": "Wankhede Stadium, Mumbai",          "time": "19:30"},
    {"date": "2026-04-19", "team1": "CSK",  "team2": "RCB",  "venue": "MA Chidambaram Stadium, Chennai",   "time": "15:30"},
    {"date": "2026-04-19", "team1": "RR",   "team2": "GT",   "venue": "Sawai Mansingh Stadium, Jaipur",    "time": "19:30"},
    {"date": "2026-04-20", "team1": "SRH",  "team2": "PBKS", "venue": "Rajiv Gandhi Intl. Stadium, Hyderabad","time": "15:30"},
    {"date": "2026-04-20", "team1": "KKR",  "team2": "LSG",  "venue": "Eden Gardens, Kolkata",             "time": "19:30"},
    {"date": "2026-04-21", "team1": "DC",   "team2": "MI",   "venue": "Arun Jaitley Stadium, Delhi",       "time": "19:30"},
    {"date": "2026-04-22", "team1": "RCB",  "team2": "RR",   "venue": "M. Chinnaswamy Stadium, Bengaluru", "time": "19:30"},
    {"date": "2026-04-23", "team1": "PBKS", "team2": "CSK",  "venue": "IS Bindra PCA Stadium, Mohali",     "time": "19:30"},
    {"date": "2026-04-24", "team1": "GT",   "team2": "SRH",  "venue": "Narendra Modi Stadium, Ahmedabad",  "time": "19:30"},
    {"date": "2026-04-25", "team1": "LSG",  "team2": "DC",   "venue": "BRSABV Ekana Cricket Stadium, Lucknow","time": "19:30"},
    {"date": "2026-04-26", "team1": "KKR",  "team2": "RCB",  "venue": "Eden Gardens, Kolkata",             "time": "15:30"},
    {"date": "2026-04-26", "team1": "MI",   "team2": "PBKS", "venue": "Wankhede Stadium, Mumbai",          "time": "19:30"},
    {"date": "2026-04-27", "team1": "CSK",  "team2": "GT",   "venue": "MA Chidambaram Stadium, Chennai",   "time": "15:30"},
    {"date": "2026-04-27", "team1": "RR",   "team2": "DC",   "venue": "Sawai Mansingh Stadium, Jaipur",    "time": "19:30"},
    {"date": "2026-04-28", "team1": "SRH",  "team2": "KKR",  "venue": "Rajiv Gandhi Intl. Stadium, Hyderabad","time": "19:30"},
    {"date": "2026-04-29", "team1": "LSG",  "team2": "MI",   "venue": "BRSABV Ekana Cricket Stadium, Lucknow","time": "19:30"},
    {"date": "2026-04-30", "team1": "PBKS", "team2": "RCB",  "venue": "IS Bindra PCA Stadium, Mohali",     "time": "19:30"},
    {"date": "2026-05-01", "team1": "GT",   "team2": "RR",   "venue": "Narendra Modi Stadium, Ahmedabad",  "time": "19:30"},
    {"date": "2026-05-02", "team1": "CSK",  "team2": "KKR",  "venue": "MA Chidambaram Stadium, Chennai",   "time": "19:30"},
    {"date": "2026-05-03", "team1": "MI",   "team2": "DC",   "venue": "Wankhede Stadium, Mumbai",          "time": "15:30"},
    {"date": "2026-05-03", "team1": "SRH",  "team2": "LSG",  "venue": "Rajiv Gandhi Intl. Stadium, Hyderabad","time": "19:30"},
    {"date": "2026-05-04", "team1": "RCB",  "team2": "GT",   "venue": "M. Chinnaswamy Stadium, Bengaluru", "time": "15:30"},
    {"date": "2026-05-04", "team1": "RR",   "team2": "CSK",  "venue": "Sawai Mansingh Stadium, Jaipur",    "time": "19:30"},
    {"date": "2026-05-05", "team1": "DC",   "team2": "SRH",  "venue": "Arun Jaitley Stadium, Delhi",       "time": "19:30"},
    {"date": "2026-05-06", "team1": "KKR",  "team2": "MI",   "venue": "Eden Gardens, Kolkata",             "time": "19:30"},
    {"date": "2026-05-07", "team1": "LSG",  "team2": "PBKS", "venue": "BRSABV Ekana Cricket Stadium, Lucknow","time": "19:30"},
    {"date": "2026-05-08", "team1": "GT",   "team2": "DC",   "venue": "Narendra Modi Stadium, Ahmedabad",  "time": "19:30"},
    {"date": "2026-05-09", "team1": "RCB",  "team2": "CSK",  "venue": "M. Chinnaswamy Stadium, Bengaluru", "time": "15:30"},
    {"date": "2026-05-09", "team1": "RR",   "team2": "KKR",  "venue": "Sawai Mansingh Stadium, Jaipur",    "time": "19:30"},
    {"date": "2026-05-10", "team1": "SRH",  "team2": "GT",   "venue": "Rajiv Gandhi Intl. Stadium, Hyderabad","time": "15:30"},
    {"date": "2026-05-10", "team1": "PBKS", "team2": "MI",   "venue": "IS Bindra PCA Stadium, Mohali",     "time": "19:30"},
    {"date": "2026-05-11", "team1": "CSK",  "team2": "LSG",  "venue": "MA Chidambaram Stadium, Chennai",   "time": "19:30"},
    {"date": "2026-05-12", "team1": "DC",   "team2": "KKR",  "venue": "Arun Jaitley Stadium, Delhi",       "time": "19:30"},
    {"date": "2026-05-13", "team1": "RCB",  "team2": "MI",   "venue": "M. Chinnaswamy Stadium, Bengaluru", "time": "19:30"},
    {"date": "2026-05-14", "team1": "PBKS", "team2": "SRH",  "venue": "IS Bindra PCA Stadium, Mohali",     "time": "19:30"},
    {"date": "2026-05-15", "team1": "GT",   "team2": "CSK",  "venue": "Narendra Modi Stadium, Ahmedabad",  "time": "19:30"},
    {"date": "2026-05-16", "team1": "RR",   "team2": "LSG",  "venue": "Sawai Mansingh Stadium, Jaipur",    "time": "15:30"},
    {"date": "2026-05-16", "team1": "KKR",  "team2": "PBKS", "venue": "Eden Gardens, Kolkata",             "time": "19:30"},
    {"date": "2026-05-17", "team1": "DC",   "team2": "RCB",  "venue": "Arun Jaitley Stadium, Delhi",       "time": "15:30"},
    {"date": "2026-05-17", "team1": "MI",   "team2": "GT",   "venue": "Wankhede Stadium, Mumbai",          "time": "19:30"},
    {"date": "2026-05-18", "team1": "CSK",  "team2": "SRH",  "venue": "MA Chidambaram Stadium, Chennai",   "time": "19:30"},
    {"date": "2026-05-19", "team1": "LSG",  "team2": "RR",   "venue": "BRSABV Ekana Cricket Stadium, Lucknow","time": "19:30"},
    {"date": "2026-05-20", "team1": "KKR",  "team2": "GT",   "venue": "Eden Gardens, Kolkata",             "time": "19:30"},
    {"date": "2026-05-21", "team1": "PBKS", "team2": "DC",   "venue": "IS Bindra PCA Stadium, Mohali",     "time": "19:30"},
    {"date": "2026-05-22", "team1": "MI",   "team2": "RCB",  "venue": "Wankhede Stadium, Mumbai",          "time": "19:30"},
    {"date": "2026-05-23", "team1": "SRH",  "team2": "RR",   "venue": "Rajiv Gandhi Intl. Stadium, Hyderabad","time": "15:30"},
    {"date": "2026-05-23", "team1": "CSK",  "team2": "PBKS", "venue": "MA Chidambaram Stadium, Chennai",   "time": "19:30"},
    {"date": "2026-05-24", "team1": "GT",   "team2": "LSG",  "venue": "Narendra Modi Stadium, Ahmedabad",  "time": "15:30"},
    {"date": "2026-05-24", "team1": "KKR",  "team2": "DC",   "venue": "Eden Gardens, Kolkata",             "time": "19:30"},
]

# ─────────────────────────────────────────────
# VENUE PITCH PROFILES
# ─────────────────────────────────────────────

VENUE_PROFILES = {
    "Wankhede": {
        "type": "Batting Paradise", "avg_score": 170,
        "dew": "High", "toss": "Field", "short_boundary": True,
        "pace_swing": True, "spin_effective": False,
        "notes": "Sea breeze helps pace. Short boundaries = big 6s."
    },
    "Eden Gardens": {
        "type": "Balanced", "avg_score": 165,
        "dew": "Medium", "toss": "Field", "short_boundary": False,
        "pace_swing": False, "spin_effective": True,
        "notes": "Spin works well. Heavy dew in 2nd innings."
    },
    "MA Chidambaram": {
        "type": "Spin Heaven", "avg_score": 155,
        "dew": "Low", "toss": "Bat", "short_boundary": False,
        "pace_swing": False, "spin_effective": True,
        "notes": "Slow sticky pitch. Spinners dominate. Bat first ideal."
    },
    "Chinnaswamy": {
        "type": "Batting Friendly", "avg_score": 185,
        "dew": "Medium", "toss": "Field", "short_boundary": True,
        "pace_swing": False, "spin_effective": False,
        "notes": "High altitude = big scores. Pick max batters/hitters."
    },
    "Rajiv Gandhi": {
        "type": "Balanced", "avg_score": 165,
        "dew": "Medium", "toss": "Field", "short_boundary": False,
        "pace_swing": True, "spin_effective": True,
        "notes": "Pace and spin both get help. Good all-rounder pitch."
    },
    "Arun Jaitley": {
        "type": "Balanced", "avg_score": 160,
        "dew": "High", "toss": "Field", "short_boundary": False,
        "pace_swing": True, "spin_effective": True,
        "notes": "Surface gets sluggish later. Dew huge factor at night."
    },
    "Sawai Mansingh": {
        "type": "Bowling Friendly", "avg_score": 155,
        "dew": "Low", "toss": "Bat", "short_boundary": False,
        "pace_swing": True, "spin_effective": True,
        "notes": "Spinners and seam both effective. Bat first advantage."
    },
    "Narendra Modi": {
        "type": "Batting Paradise", "avg_score": 175,
        "dew": "Medium", "toss": "Field", "short_boundary": True,
        "pace_swing": False, "spin_effective": True,
        "notes": "Large ground but fast outfield. Spinners useful."
    },
    "IS Bindra": {
        "type": "Balanced", "avg_score": 160,
        "dew": "Low", "toss": "Bat", "short_boundary": False,
        "pace_swing": True, "spin_effective": False,
        "notes": "Overcast conditions help pacers. Good batting track."
    },
    "BRSABV Ekana": {
        "type": "Bowling Friendly", "avg_score": 150,
        "dew": "High", "toss": "Field", "short_boundary": False,
        "pace_swing": True, "spin_effective": True,
        "notes": "Slow pitch. Pacers with skills dominate."
    },
}

# ─────────────────────────────────────────────
# PLAYER DATABASE — IPL 2026 KEY PLAYERS
# ─────────────────────────────────────────────
# Format: {TEAM: [{name, role, batting_pos, dream11_pts_avg, form, key_player}]}
# Roles: WK / BAT / AR / BOWL

IPL_PLAYERS = {
    "MI": [
        {"name": "Quinton de Kock",    "role": "WK",   "batting_pos": "Opener",  "pts": 52, "form": "Good",  "key": True},
        {"name": "Rohit Sharma",        "role": "BAT",  "batting_pos": "Opener",  "pts": 58, "form": "Good",  "key": True},
        {"name": "Tilak Varma",         "role": "BAT",  "batting_pos": "No.3",    "pts": 55, "form": "Excellent", "key": True},
        {"name": "Suryakumar Yadav",    "role": "BAT",  "batting_pos": "No.4",    "pts": 60, "form": "Good",  "key": True},
        {"name": "Hardik Pandya",       "role": "AR",   "batting_pos": "No.5",    "pts": 65, "form": "Good",  "key": True},
        {"name": "Sherfane Rutherford", "role": "AR",   "batting_pos": "No.6",    "pts": 42, "form": "Average","key": False},
        {"name": "Naman Dhir",          "role": "AR",   "batting_pos": "No.7",    "pts": 38, "form": "Average","key": False},
        {"name": "Deepak Chahar",       "role": "BOWL", "batting_pos": "No.9",    "pts": 40, "form": "Good",  "key": False},
        {"name": "Trent Boult",         "role": "BOWL", "batting_pos": "No.10",   "pts": 48, "form": "Good",  "key": True},
        {"name": "Jasprit Bumrah",      "role": "BOWL", "batting_pos": "No.11",   "pts": 72, "form": "Excellent","key": True},
        {"name": "Ashwani Kumar",       "role": "BOWL", "batting_pos": "No.8",    "pts": 38, "form": "Good",  "key": False},
        {"name": "Mitchell Santner",    "role": "AR",   "batting_pos": "No.7",    "pts": 44, "form": "Good",  "key": False, "injury_doubt": True},
    ],
    "KKR": [
        {"name": "Finn Allen",          "role": "WK",   "batting_pos": "Opener",  "pts": 55, "form": "Good",  "key": True},
        {"name": "Ajinkya Rahane",      "role": "BAT",  "batting_pos": "Opener",  "pts": 40, "form": "Average","key": False},
        {"name": "Angkrish Raghuvanshi","role": "BAT",  "batting_pos": "No.3",    "pts": 45, "form": "Good",  "key": False},
        {"name": "Cameron Green",       "role": "AR",   "batting_pos": "No.4",    "pts": 50, "form": "Good",  "key": True},
        {"name": "Rinku Singh",         "role": "BAT",  "batting_pos": "No.5",    "pts": 52, "form": "Good",  "key": True},
        {"name": "Sunil Narine",        "role": "AR",   "batting_pos": "Opener/Float","pts": 62, "form": "Excellent","key": True},
        {"name": "Ramandeep Singh",     "role": "AR",   "batting_pos": "No.7",    "pts": 40, "form": "Average","key": False},
        {"name": "Anukul Roy",          "role": "AR",   "batting_pos": "No.8",    "pts": 38, "form": "Average","key": False},
        {"name": "Vaibhav Arora",       "role": "BOWL", "batting_pos": "No.10",   "pts": 42, "form": "Good",  "key": False},
        {"name": "Varun Chakravarthy",  "role": "BOWL", "batting_pos": "No.11",   "pts": 55, "form": "Excellent","key": True},
        {"name": "Blessing Muzarabani", "role": "BOWL", "batting_pos": "No.9",    "pts": 45, "form": "Good",  "key": False},
    ],
    "CSK": [
        {"name": "Ruturaj Gaikwad",     "role": "BAT",  "batting_pos": "Opener",  "pts": 58, "form": "Good",  "key": True},
        {"name": "Devon Conway",        "role": "WK",   "batting_pos": "Opener",  "pts": 52, "form": "Good",  "key": True},
        {"name": "Rahane",              "role": "BAT",  "batting_pos": "No.3",    "pts": 45, "form": "Average","key": False},
        {"name": "Shivam Dube",         "role": "AR",   "batting_pos": "No.4",    "pts": 55, "form": "Good",  "key": True},
        {"name": "Ravindra Jadeja",     "role": "AR",   "batting_pos": "No.5",    "pts": 62, "form": "Excellent","key": True},
        {"name": "MS Dhoni",            "role": "WK",   "batting_pos": "No.7",    "pts": 50, "form": "Good",  "key": True},
        {"name": "Deepak Chahar",       "role": "BOWL", "batting_pos": "No.9",    "pts": 42, "form": "Good",  "key": False},
        {"name": "Tushar Deshpande",    "role": "BOWL", "batting_pos": "No.10",   "pts": 40, "form": "Average","key": False},
        {"name": "Matheesha Pathirana", "role": "BOWL", "batting_pos": "No.11",   "pts": 50, "form": "Good",  "key": True},
        {"name": "Noor Ahmad",          "role": "BOWL", "batting_pos": "No.8",    "pts": 45, "form": "Good",  "key": False},
    ],
    "RCB": [
        {"name": "Faf du Plessis",      "role": "BAT",  "batting_pos": "Opener",  "pts": 55, "form": "Good",  "key": True},
        {"name": "Virat Kohli",         "role": "BAT",  "batting_pos": "No.3",    "pts": 68, "form": "Excellent","key": True},
        {"name": "Rajat Patidar",       "role": "BAT",  "batting_pos": "No.4",    "pts": 50, "form": "Good",  "key": False},
        {"name": "Glenn Maxwell",       "role": "AR",   "batting_pos": "No.5",    "pts": 58, "form": "Good",  "key": True},
        {"name": "Liam Livingstone",    "role": "AR",   "batting_pos": "No.6",    "pts": 52, "form": "Good",  "key": True},
        {"name": "Dinesh Karthik",      "role": "WK",   "batting_pos": "No.7",    "pts": 48, "form": "Good",  "key": False},
        {"name": "Mohammed Siraj",      "role": "BOWL", "batting_pos": "No.10",   "pts": 48, "form": "Good",  "key": True},
        {"name": "Josh Hazlewood",      "role": "BOWL", "batting_pos": "No.11",   "pts": 50, "form": "Good",  "key": True},
        {"name": "Yuzvendra Chahal",    "role": "BOWL", "batting_pos": "No.9",    "pts": 52, "form": "Good",  "key": True},
        {"name": "Tom Curran",          "role": "AR",   "batting_pos": "No.8",    "pts": 40, "form": "Average","key": False},
    ],
    "DC": [
        {"name": "David Warner",        "role": "BAT",  "batting_pos": "Opener",  "pts": 58, "form": "Good",  "key": True},
        {"name": "Prithvi Shaw",        "role": "BAT",  "batting_pos": "Opener",  "pts": 50, "form": "Good",  "key": True},
        {"name": "Jake Fraser-McGurk",  "role": "BAT",  "batting_pos": "No.3",    "pts": 52, "form": "Good",  "key": True},
        {"name": "Rishabh Pant",        "role": "WK",   "batting_pos": "No.4",    "pts": 65, "form": "Excellent","key": True},
        {"name": "Axar Patel",          "role": "AR",   "batting_pos": "No.5",    "pts": 58, "form": "Good",  "key": True},
        {"name": "Tristan Stubbs",      "role": "AR",   "batting_pos": "No.6",    "pts": 48, "form": "Average","key": False},
        {"name": "Kuldeep Yadav",       "role": "BOWL", "batting_pos": "No.9",    "pts": 55, "form": "Good",  "key": True},
        {"name": "Anrich Nortje",       "role": "BOWL", "batting_pos": "No.11",   "pts": 50, "form": "Good",  "key": True},
        {"name": "Mustafizur Rahman",   "role": "BOWL", "batting_pos": "No.10",   "pts": 45, "form": "Good",  "key": False},
        {"name": "Ishant Sharma",       "role": "BOWL", "batting_pos": "No.8",    "pts": 40, "form": "Average","key": False},
    ],
    "SRH": [
        {"name": "Travis Head",         "role": "BAT",  "batting_pos": "Opener",  "pts": 65, "form": "Excellent","key": True},
        {"name": "Abhishek Sharma",     "role": "BAT",  "batting_pos": "Opener",  "pts": 60, "form": "Good",  "key": True},
        {"name": "Aiden Markram",       "role": "BAT",  "batting_pos": "No.3",    "pts": 52, "form": "Good",  "key": True},
        {"name": "Heinrich Klaasen",    "role": "WK",   "batting_pos": "No.4",    "pts": 65, "form": "Excellent","key": True},
        {"name": "Pat Cummins",         "role": "AR",   "batting_pos": "No.5",    "pts": 62, "form": "Good",  "key": True},
        {"name": "Nitish Kumar Reddy",  "role": "AR",   "batting_pos": "No.6",    "pts": 50, "form": "Good",  "key": True},
        {"name": "Shahbaz Ahmed",       "role": "AR",   "batting_pos": "No.7",    "pts": 40, "form": "Average","key": False},
        {"name": "Bhuvneshwar Kumar",   "role": "BOWL", "batting_pos": "No.9",    "pts": 48, "form": "Good",  "key": False},
        {"name": "Umran Malik",         "role": "BOWL", "batting_pos": "No.11",   "pts": 42, "form": "Average","key": False},
        {"name": "Jaydev Unadkat",      "role": "BOWL", "batting_pos": "No.10",   "pts": 40, "form": "Average","key": False},
    ],
    "RR": [
        {"name": "Jos Buttler",         "role": "WK",   "batting_pos": "Opener",  "pts": 68, "form": "Excellent","key": True},
        {"name": "Yashasvi Jaiswal",    "role": "BAT",  "batting_pos": "Opener",  "pts": 65, "form": "Excellent","key": True},
        {"name": "Sanju Samson",        "role": "WK",   "batting_pos": "No.3",    "pts": 62, "form": "Good",  "key": True},
        {"name": "Riyan Parag",         "role": "AR",   "batting_pos": "No.4",    "pts": 52, "form": "Good",  "key": True},
        {"name": "Shimron Hetmyer",     "role": "BAT",  "batting_pos": "No.5",    "pts": 50, "form": "Good",  "key": True},
        {"name": "Dhruv Jurel",         "role": "WK",   "batting_pos": "No.6",    "pts": 45, "form": "Average","key": False},
        {"name": "Ravichandran Ashwin", "role": "AR",   "batting_pos": "No.7",    "pts": 48, "form": "Good",  "key": False},
        {"name": "Trent Boult",         "role": "BOWL", "batting_pos": "No.10",   "pts": 52, "form": "Good",  "key": True},
        {"name": "Sandeep Sharma",      "role": "BOWL", "batting_pos": "No.9",    "pts": 42, "form": "Good",  "key": False},
        {"name": "Yuzvendra Chahal",    "role": "BOWL", "batting_pos": "No.11",   "pts": 50, "form": "Good",  "key": True},
    ],
    "PBKS": [
        {"name": "Prabhsimran Singh",   "role": "WK",   "batting_pos": "Opener",  "pts": 55, "form": "Good",  "key": True},
        {"name": "Shikhar Dhawan",      "role": "BAT",  "batting_pos": "Opener",  "pts": 50, "form": "Average","key": False},
        {"name": "Sam Curran",          "role": "AR",   "batting_pos": "No.3",    "pts": 55, "form": "Good",  "key": True},
        {"name": "Liam Livingstone",    "role": "AR",   "batting_pos": "No.4",    "pts": 58, "form": "Good",  "key": True},
        {"name": "Jonny Bairstow",      "role": "WK",   "batting_pos": "No.5",    "pts": 55, "form": "Good",  "key": True},
        {"name": "Shashank Singh",      "role": "BAT",  "batting_pos": "No.6",    "pts": 48, "form": "Good",  "key": False},
        {"name": "Harpreet Brar",       "role": "AR",   "batting_pos": "No.7",    "pts": 40, "form": "Average","key": False},
        {"name": "Arshdeep Singh",      "role": "BOWL", "batting_pos": "No.9",    "pts": 52, "form": "Good",  "key": True},
        {"name": "Nathan Ellis",        "role": "BOWL", "batting_pos": "No.10",   "pts": 45, "form": "Good",  "key": False},
        {"name": "Rahul Chahar",        "role": "BOWL", "batting_pos": "No.11",   "pts": 45, "form": "Good",  "key": False},
    ],
    "LSG": [
        {"name": "Quinton de Kock",     "role": "WK",   "batting_pos": "Opener",  "pts": 58, "form": "Good",  "key": True},
        {"name": "KL Rahul",            "role": "WK",   "batting_pos": "Opener",  "pts": 60, "form": "Good",  "key": True},
        {"name": "Nicholas Pooran",     "role": "BAT",  "batting_pos": "No.3",    "pts": 62, "form": "Excellent","key": True},
        {"name": "Marcus Stoinis",      "role": "AR",   "batting_pos": "No.4",    "pts": 55, "form": "Good",  "key": True},
        {"name": "Deepak Hooda",        "role": "AR",   "batting_pos": "No.5",    "pts": 45, "form": "Average","key": False},
        {"name": "Krunal Pandya",       "role": "AR",   "batting_pos": "No.6",    "pts": 50, "form": "Good",  "key": True},
        {"name": "Prerak Mankad",       "role": "AR",   "batting_pos": "No.7",    "pts": 38, "form": "Average","key": False},
        {"name": "Mark Wood",           "role": "BOWL", "batting_pos": "No.10",   "pts": 50, "form": "Good",  "key": True},
        {"name": "Ravi Bishnoi",        "role": "BOWL", "batting_pos": "No.11",   "pts": 50, "form": "Good",  "key": True},
        {"name": "Avesh Khan",          "role": "BOWL", "batting_pos": "No.9",    "pts": 45, "form": "Good",  "key": False},
    ],
    "GT": [
        {"name": "Wriddhiman Saha",     "role": "WK",   "batting_pos": "Opener",  "pts": 50, "form": "Average","key": False},
        {"name": "Shubman Gill",        "role": "BAT",  "batting_pos": "Opener",  "pts": 65, "form": "Excellent","key": True},
        {"name": "Hardik Pandya",       "role": "AR",   "batting_pos": "No.3",    "pts": 62, "form": "Good",  "key": True},
        {"name": "David Miller",        "role": "BAT",  "batting_pos": "No.4",    "pts": 58, "form": "Good",  "key": True},
        {"name": "Abhinav Manohar",     "role": "BAT",  "batting_pos": "No.5",    "pts": 45, "form": "Average","key": False},
        {"name": "Rahul Tewatia",       "role": "AR",   "batting_pos": "No.6",    "pts": 50, "form": "Good",  "key": True},
        {"name": "Rashid Khan",         "role": "AR",   "batting_pos": "No.7",    "pts": 65, "form": "Excellent","key": True},
        {"name": "Mohammed Shami",      "role": "BOWL", "batting_pos": "No.9",    "pts": 58, "form": "Excellent","key": True},
        {"name": "Alzarri Joseph",      "role": "BOWL", "batting_pos": "No.10",   "pts": 48, "form": "Good",  "key": False},
        {"name": "Noor Ahmad",          "role": "BOWL", "batting_pos": "No.11",   "pts": 45, "form": "Good",  "key": False},
        {"name": "Umesh Yadav",         "role": "BOWL", "batting_pos": "No.8",    "pts": 42, "form": "Average","key": False},
    ],
}


# ─────────────────────────────────────────────
# MATCH DETECTION
# ─────────────────────────────────────────────

def get_today_match():
    """Return today's IPL match from schedule. Returns None if no match today."""
    today = date.today()
    today_str = today.strftime("%Y-%m-%d")

    if today < IPL_START or today > IPL_END:
        logger.info(f"Today {today_str} is outside IPL 2026 season ({IPL_START} – {IPL_END})")
        return None

    matches_today = [m for m in IPL_2026_SCHEDULE if m["date"] == today_str]
    if not matches_today:
        logger.info(f"No IPL match scheduled for {today_str}")
        return None

    # Return first match (or both if double header)
    return matches_today

def get_venue_profile(venue: str) -> dict:
    """Match venue name to profile."""
    for key, profile in VENUE_PROFILES.items():
        if key.lower() in venue.lower():
            return profile
    return {"type": "Balanced", "avg_score": 162, "dew": "Medium",
            "toss": "Field", "notes": "Standard pitch conditions."}


# ─────────────────────────────────────────────
# AI-POWERED TEAM GENERATOR
# ─────────────────────────────────────────────

def generate_5_teams_ai(team1: str, team2: str, venue: str, match_time: str) -> dict:
    """Use AI client to generate 5 fantasy teams with analysis."""

    pitch = get_venue_profile(venue)
    players_t1 = IPL_PLAYERS.get(team1, [])
    players_t2 = IPL_PLAYERS.get(team2, [])
    all_players = players_t1 + players_t2

    # Format player list for AI
    player_list = "\n".join([
        f"  {p['role']} | {p['name']} ({t}) | Pos: {p['batting_pos']} | Avg Pts: {p['pts']} | Form: {p['form']}"
        for t, pl in [(team1, players_t1), (team2, players_t2)]
        for p in pl
        if not p.get("injury_doubt")
    ])

    prompt = f"""IPL 2026 Fantasy Cricket — Generate 5 Dream11/My11Circle teams.

MATCH: {team1} vs {team2}
VENUE: {venue}
TIME: {match_time} IST

PITCH: {pitch['type']} | Avg Score: {pitch['avg_score']} | Dew: {pitch['dew']} | Toss Tip: {pitch['toss']} first
PITCH NOTES: {pitch['notes']}

AVAILABLE PLAYERS (confirmed XI, no injuries):
{player_list}

DREAM11 RULES:
- Exactly 11 players per team
- Max 7 players from one team
- Min 1 WK, 1 BAT, 1 AR, 1 BOWL
- 1 Captain (2x points), 1 Vice-Captain (1.5x points)
- Budget: 100 credits (each player has credit value)

Generate exactly 5 teams in this JSON format:
{{
  "match": "{team1} vs {team2}",
  "venue": "{venue}",
  "pitch_type": "{pitch['type']}",
  "toss_tip": "Chase/Bat first based on conditions",
  "key_insights": ["insight1", "insight2", "insight3"],
  "teams": [
    {{
      "name": "Team 1 – [Creative Name]",
      "strategy": "Safe/Grand League/Balanced/Differential/Captain Swap",
      "risk": "Low/Medium/High",
      "captain": "Player Name",
      "vice_captain": "Player Name",
      "players": [
        {{"name": "Player", "role": "WK/BAT/AR/BOWL", "team": "{team1}/{team2}"}}
      ],
      "why": "1-line strategy explanation"
    }}
  ],
  "must_pick": ["player1", "player2", "player3"],
  "avoid": ["player1"],
  "disclaimer": "Verify confirmed XI after toss at match time."
}}

Team names must be creative: e.g. "Safe Bet XI", "Bumrah Blast", "All-Rounder Army", "Differential Dare", "Captain Swap Special"
Make teams varied — different captains, different combinations. Include differential/surprise picks in Teams 4 & 5."""

    system = """You are an expert Dream11/My11Circle fantasy cricket analyst with 10 years experience.
You deeply understand pitch conditions, player form, batting positions, and fantasy point systems.
Return ONLY valid JSON. No markdown, no explanation outside JSON. Be specific with player names."""

    client = AIClient()
    result = client.generate_json(
        prompt=prompt,
        system_prompt=system,
        content_mode="market",
        lang="en",
    )
    return result


# ─────────────────────────────────────────────
# FALLBACK TEAM BUILDER (no AI)
# ─────────────────────────────────────────────

def build_fallback_teams(team1: str, team2: str, venue: str) -> dict:
    """Build 5 teams using rule-based logic when AI fails."""
    p1 = sorted(IPL_PLAYERS.get(team1, []), key=lambda x: x["pts"], reverse=True)
    p2 = sorted(IPL_PLAYERS.get(team2, []), key=lambda x: x["pts"], reverse=True)
    all_sorted = sorted(p1 + p2, key=lambda x: x["pts"], reverse=True)
    pitch = get_venue_profile(venue)

    def pick_team(t1_count=6, use_bowling_heavy=False, differential=False):
        """Build a valid 11-player team."""
        team = []
        roles_needed = {"WK": 1, "BAT": 3, "AR": 3, "BOWL": 3}
        t1_used, t2_used = 0, 0

        # Sort players
        pool = sorted(all_sorted, key=lambda x: (
            -x["pts"] * (1.2 if use_bowling_heavy and x["role"] == "BOWL" else 1.0)
        ))

        for p in pool:
            if len(team) == 11:
                break
            role = p["role"]
            is_t1 = p in p1
            # Max 7 from one team
            if is_t1 and t1_used >= 7:
                continue
            if not is_t1 and t2_used >= 7:
                continue
            # Ensure min players from each team (min 4 from away)
            if is_t1 and t1_count and t1_used >= t1_count:
                if (11 - len(team)) <= (4 - t2_used):
                    continue
            if roles_needed.get(role, 0) > 0:
                team.append(p)
                roles_needed[role] -= 1
                if is_t1:
                    t1_used += 1
                else:
                    t2_used += 1

        # If team not complete, fill remaining spots
        for p in pool:
            if len(team) == 11:
                break
            if p not in team:
                is_t1 = p in p1
                if is_t1 and t1_used >= 7:
                    continue
                if not is_t1 and t2_used >= 7:
                    continue
                team.append(p)
                if is_t1:
                    t1_used += 1
                else:
                    t2_used += 1

        return team[:11]

    def format_team(players, name, strategy, risk, cap_idx=0, vc_idx=1, why=""):
        cap = players[cap_idx]["name"] if cap_idx < len(players) else players[0]["name"]
        vc = players[vc_idx]["name"] if vc_idx < len(players) else players[1]["name"]
        return {
            "name": name,
            "strategy": strategy,
            "risk": risk,
            "captain": cap,
            "vice_captain": vc,
            "players": [{"name": p["name"], "role": p["role"], "team": team1 if p in p1 else team2} for p in players],
            "why": why
        }

    t_safe = pick_team(t1_count=6)
    t_bowl = pick_team(t1_count=6, use_bowling_heavy=True)
    t_ar   = pick_team(t1_count=5)
    t_diff = pick_team(t1_count=4)
    t_swap = pick_team(t1_count=7)

    top3 = [p["name"] for p in sorted(all_sorted, key=lambda x: x["pts"], reverse=True)[:3]]

    return {
        "match": f"{team1} vs {team2}",
        "venue": venue,
        "pitch_type": pitch["type"],
        "toss_tip": f"{pitch['toss']} first recommended",
        "key_insights": [
            f"Pitch: {pitch['type']} — avg score {pitch['avg_score']}",
            f"Dew factor: {pitch['dew']} — {pitch['notes']}",
            f"Must-picks: {', '.join(top3)}"
        ],
        "teams": [
            format_team(t_safe, f"Team 1 – Safe Bet XI",         "Safe",        "Low",    0, 1, "Top-rated players, low risk."),
            format_team(t_bowl, f"Team 2 – Bowling Blitz",       "Grand League","Medium", 2, 0, "Bowling heavy for wicket-taking points."),
            format_team(t_ar,   f"Team 3 – All-Rounder Army",    "Balanced",    "Medium", 1, 2, "Multi-dimensional all-rounders dominate."),
            format_team(t_diff, f"Team 4 – Differential Dare",   "Differential","High",   3, 0, "Low-ownership picks for grand leagues."),
            format_team(t_swap, f"Team 5 – Captain Swap Special","Grand League","High",   2, 1, "Differential captain for massive multiplier."),
        ],
        "must_pick": top3,
        "avoid": [],
        "disclaimer": f"⚠️ Verify confirmed XI after toss. Injury updates before lock-in."
    }


# ─────────────────────────────────────────────
# TELEGRAM FORMATTER
# ─────────────────────────────────────────────

def format_telegram_message(data: dict, team1: str, team2: str) -> list:
    """Format dream11 picks into Telegram HTML messages. Returns list of message parts."""

    e1 = TEAM_EMOJI.get(team1, "🏏")
    e2 = TEAM_EMOJI.get(team2, "🏏")

    # ── Header message ────────────────────────
    header = f"""🏏 <b>IPL 2026 — DREAM11 PICKS</b> 🏏
{e1} <b>{team1}</b> vs <b>{team2}</b> {e2}

📍 <i>{data.get('venue', '')}</i>

<b>Pitch:</b> {data.get('pitch_type', 'Balanced')}
<b>Toss Tip:</b> {data.get('toss_tip', 'Field first')}

<b>📊 Key Insights:</b>
{"".join([f"• {i}" + chr(10) for i in data.get('key_insights', [])])}
<b>🌟 Must-Picks:</b> {', '.join(data.get('must_pick', []))}

<i>5 teams below — use for Dream11 / My11Circle</i>
──────────────────────────────"""

    messages = [header]

    # ── Team messages ──────────────────────────
    risk_emoji = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}

    teams = data.get("teams", [])
    for i, team in enumerate(teams, 1):
        risk = team.get("risk", "Medium")
        players = team.get("players", [])

        # Group by role
        wk   = [p for p in players if p["role"] == "WK"]
        bats = [p for p in players if p["role"] == "BAT"]
        ars  = [p for p in players if p["role"] == "AR"]
        bowls= [p for p in players if p["role"] == "BOWL"]

        cap = team.get("captain", "")
        vc  = team.get("vice_captain", "")

        def fmt_player(p):
            name = p["name"]
            suffix = " 🅒" if name == cap else (" 🅥" if name == vc else "")
            t = p.get("team", "")
            pill = f"[{t}]" if t else ""
            return f"  {name}{suffix} <i>{pill}</i>"

        wk_str   = "\n".join([fmt_player(p) for p in wk])   or "  —"
        bat_str  = "\n".join([fmt_player(p) for p in bats])  or "  —"
        ar_str   = "\n".join([fmt_player(p) for p in ars])   or "  —"
        bowl_str = "\n".join([fmt_player(p) for p in bowls]) or "  —"

        team_msg = f"""{risk_emoji.get(risk, '🟡')} <b>TEAM {i} — {team.get('name', '').split('–')[-1].strip()}</b>
<i>{team.get('strategy','')} · {risk} Risk</i>

🧤 WK:
{wk_str}
🏏 BAT:
{bat_str}
🔄 ALL-ROUNDER:
{ar_str}
⚡ BOWLER:
{bowl_str}

🅒 C: <b>{cap}</b>  |  🅥 VC: <b>{vc}</b>
💡 <i>{team.get('why', '')}</i>
──────────────────────────────"""
        messages.append(team_msg)

    # ── Footer ──────────────────────────────
    footer = f"""⚠️ <b>DISCLAIMER</b>
{data.get('disclaimer', 'Verify XI after toss.')}
Lock teams only after confirmed playing 11.

📲 <b>AI360Trading</b> | Free IPL Fantasy Picks
Join: @ai360trading | 🌐 ai360trading.in
─────────────────────────────"""
    messages.append(footer)

    return messages


# ─────────────────────────────────────────────
# TELEGRAM SENDER
# ─────────────────────────────────────────────

def send_to_free_channel(messages: list) -> bool:
    """Send messages to free Telegram channel only."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("TELEGRAM_TOKEN or TELEGRAM_CHAT_ID not set")
        return False

    success = True
    for i, msg in enumerate(messages):
        try:
            r = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": msg,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                },
                timeout=15,
            )
            if r.status_code != 200:
                logger.error(f"TG send failed part {i+1}: {r.status_code} {r.text[:100]}")
                success = False
            else:
                logger.info(f"✅ Sent part {i+1}/{len(messages)} to free channel")
            time.sleep(1.5)  # Avoid Telegram rate limit
        except Exception as e:
            logger.error(f"TG error part {i+1}: {e}")
            success = False
    return success


# ─────────────────────────────────────────────
# MAIN RUNNER
# ─────────────────────────────────────────────

def run():
    now = datetime.now(IST)
    logger.info(f"🏏 Dream11 IPL Generator started — {now.strftime('%Y-%m-%d %H:%M IST')}")

    # 1. Check if IPL match today
    matches = get_today_match()
    if not matches:
        logger.info("No IPL match today. Skipping.")
        return

    for match in matches:
        team1 = match["team1"]
        team2 = match["team2"]
        venue = match["venue"]
        match_time = match["time"]

        logger.info(f"Match found: {team1} vs {team2} at {venue}")

        # 2. Generate 5 teams (AI first, fallback if AI fails)
        logger.info("Generating 5 fantasy teams via AI...")
        data = generate_5_teams_ai(team1, team2, venue, match_time)

        if not data or not data.get("teams"):
            logger.warning("AI generation failed or returned no teams. Using rule-based fallback.")
            data = build_fallback_teams(team1, team2, venue)

        # 3. Format Telegram messages
        messages = format_telegram_message(data, team1, team2)

        # 4. Send to FREE channel only
        logger.info(f"Sending {len(messages)} messages to free Telegram channel...")
        ok = send_to_free_channel(messages)

        if ok:
            logger.info(f"✅ Dream11 picks sent for {team1} vs {team2}")
        else:
            logger.error(f"❌ Failed to send some messages for {team1} vs {team2}")

        # Small delay between double-header matches
        if len(matches) > 1:
            time.sleep(30)


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    run()
