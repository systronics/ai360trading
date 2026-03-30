"""
dream11_ipl.py — Dream11 / My11Circle IPL Fantasy Team Generator
══════════════════════════════════════════════════════════════════
Auto-generates 5 fantasy teams for every IPL 2026 match.
Sends to FREE Telegram channel (TELEGRAM_CHAT_ID only).

SQUAD DATABASE: Updated for IPL 2026 post-auction (December 16, 2025)
KEY TRADES:
  Ravindra Jadeja: CSK → RR
  Sanju Samson:    RR  → CSK
  Sam Curran:      CSK → RR
  Nitish Rana:     RR  → DC
  Sherfane Rutherford: GT → MI
  Shardul Thakur:  LSG → MI
  Arjun Tendulkar: MI  → LSG
  Mohammad Shami:  SRH → LSG
  Mayank Markande: KKR → MI
  Donovan Ferreira: DC → RR

PLAYING XI RESOLUTION (3-layer):
  1. ENV vars PLAYING_XI_T1 / PLAYING_XI_T2 (manual after toss — most accurate)
  2. CricAPI /match_info lineup (auto, post-toss only)
  3. Smart squad filter from IPL 2026 squads (pre-toss fallback)

Author: AI360Trading Automation
"""

import os
import sys
import json
import time
import logging
import requests
import pytz
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ai_client import AIClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

IST = pytz.timezone("Asia/Kolkata")

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
CRICAPI_KEY      = os.environ.get("CRICAPI_KEY", "")

PLAYING_XI_T1_ENV = os.environ.get("PLAYING_XI_T1", "").strip()
PLAYING_XI_T2_ENV = os.environ.get("PLAYING_XI_T2", "").strip()

IPL_START = date(2026, 3, 22)
IPL_END   = date(2026, 5, 30)

# ─────────────────────────────────────────────
# TEAM / EMOJI MAPS
# ─────────────────────────────────────────────

TEAM_EMOJI = {
    "MI": "💙", "KKR": "💜", "CSK": "💛", "RCB": "❤️",
    "DC": "🔵", "SRH": "🟠", "RR": "🩷", "PBKS": "🔴",
    "LSG": "🩵", "GT": "🔷",
}

TEAM_FULL_NAMES = {
    "MI":   "mumbai indians",
    "KKR":  "kolkata knight riders",
    "CSK":  "chennai super kings",
    "RCB":  "royal challengers",
    "DC":   "delhi capitals",
    "SRH":  "sunrisers hyderabad",
    "RR":   "rajasthan royals",
    "PBKS": "punjab kings",
    "LSG":  "lucknow super giants",
    "GT":   "gujarat titans",
}

# ─────────────────────────────────────────────
# IPL 2026 SCHEDULE
# ─────────────────────────────────────────────

IPL_2026_SCHEDULE = [
    {"date": "2026-03-22", "team1": "MI",   "team2": "CSK",  "venue": "Wankhede Stadium, Mumbai",               "time": "19:30"},
    {"date": "2026-03-23", "team1": "RCB",  "team2": "DC",   "venue": "M. Chinnaswamy Stadium, Bengaluru",      "time": "19:30"},
    {"date": "2026-03-25", "team1": "SRH",  "team2": "RR",   "venue": "Rajiv Gandhi Intl. Stadium, Hyderabad",  "time": "19:30"},
    {"date": "2026-03-26", "team1": "PBKS", "team2": "LSG",  "venue": "IS Bindra PCA Stadium, Mohali",          "time": "19:30"},
    {"date": "2026-03-27", "team1": "GT",   "team2": "KKR",  "venue": "Narendra Modi Stadium, Ahmedabad",       "time": "19:30"},
    {"date": "2026-03-28", "team1": "RCB",  "team2": "SRH",  "venue": "M. Chinnaswamy Stadium, Bengaluru",      "time": "19:30"},
    {"date": "2026-03-29", "team1": "MI",   "team2": "KKR",  "venue": "Wankhede Stadium, Mumbai",               "time": "19:30"},
    {"date": "2026-03-30", "team1": "CSK",  "team2": "DC",   "venue": "MA Chidambaram Stadium, Chennai",        "time": "19:30"},
    {"date": "2026-04-01", "team1": "RR",   "team2": "PBKS", "venue": "Sawai Mansingh Stadium, Jaipur",         "time": "19:30"},
    {"date": "2026-04-02", "team1": "LSG",  "team2": "GT",   "venue": "BRSABV Ekana Cricket Stadium, Lucknow",  "time": "19:30"},
    {"date": "2026-04-03", "team1": "MI",   "team2": "SRH",  "venue": "Wankhede Stadium, Mumbai",               "time": "19:30"},
    {"date": "2026-04-04", "team1": "KKR",  "team2": "CSK",  "venue": "Eden Gardens, Kolkata",                  "time": "19:30"},
    {"date": "2026-04-05", "team1": "RCB",  "team2": "PBKS", "venue": "M. Chinnaswamy Stadium, Bengaluru",      "time": "15:30"},
    {"date": "2026-04-05", "team1": "DC",   "team2": "RR",   "venue": "Arun Jaitley Stadium, Delhi",            "time": "19:30"},
    {"date": "2026-04-06", "team1": "GT",   "team2": "LSG",  "venue": "Narendra Modi Stadium, Ahmedabad",       "time": "15:30"},
    {"date": "2026-04-06", "team1": "SRH",  "team2": "MI",   "venue": "Rajiv Gandhi Intl. Stadium, Hyderabad",  "time": "19:30"},
    {"date": "2026-04-07", "team1": "CSK",  "team2": "RR",   "venue": "MA Chidambaram Stadium, Chennai",        "time": "19:30"},
    {"date": "2026-04-08", "team1": "PBKS", "team2": "KKR",  "venue": "IS Bindra PCA Stadium, Mohali",          "time": "19:30"},
    {"date": "2026-04-09", "team1": "DC",   "team2": "GT",   "venue": "Arun Jaitley Stadium, Delhi",            "time": "19:30"},
    {"date": "2026-04-10", "team1": "RCB",  "team2": "LSG",  "venue": "M. Chinnaswamy Stadium, Bengaluru",      "time": "19:30"},
    {"date": "2026-04-11", "team1": "MI",   "team2": "RR",   "venue": "Wankhede Stadium, Mumbai",               "time": "19:30"},
    {"date": "2026-04-12", "team1": "SRH",  "team2": "CSK",  "venue": "Rajiv Gandhi Intl. Stadium, Hyderabad",  "time": "15:30"},
    {"date": "2026-04-12", "team1": "KKR",  "team2": "DC",   "venue": "Eden Gardens, Kolkata",                  "time": "19:30"},
    {"date": "2026-04-13", "team1": "PBKS", "team2": "GT",   "venue": "IS Bindra PCA Stadium, Mohali",          "time": "15:30"},
    {"date": "2026-04-13", "team1": "LSG",  "team2": "RCB",  "venue": "BRSABV Ekana Cricket Stadium, Lucknow",  "time": "19:30"},
    {"date": "2026-04-14", "team1": "CSK",  "team2": "MI",   "venue": "MA Chidambaram Stadium, Chennai",        "time": "19:30"},
    {"date": "2026-04-15", "team1": "RR",   "team2": "SRH",  "venue": "Sawai Mansingh Stadium, Jaipur",         "time": "19:30"},
    {"date": "2026-04-16", "team1": "GT",   "team2": "KKR",  "venue": "Narendra Modi Stadium, Ahmedabad",       "time": "19:30"},
    {"date": "2026-04-17", "team1": "DC",   "team2": "PBKS", "venue": "Arun Jaitley Stadium, Delhi",            "time": "19:30"},
    {"date": "2026-04-18", "team1": "MI",   "team2": "LSG",  "venue": "Wankhede Stadium, Mumbai",               "time": "19:30"},
    {"date": "2026-04-19", "team1": "CSK",  "team2": "RCB",  "venue": "MA Chidambaram Stadium, Chennai",        "time": "15:30"},
    {"date": "2026-04-19", "team1": "RR",   "team2": "GT",   "venue": "Sawai Mansingh Stadium, Jaipur",         "time": "19:30"},
    {"date": "2026-04-20", "team1": "SRH",  "team2": "PBKS", "venue": "Rajiv Gandhi Intl. Stadium, Hyderabad",  "time": "15:30"},
    {"date": "2026-04-20", "team1": "KKR",  "team2": "LSG",  "venue": "Eden Gardens, Kolkata",                  "time": "19:30"},
    {"date": "2026-04-21", "team1": "DC",   "team2": "MI",   "venue": "Arun Jaitley Stadium, Delhi",            "time": "19:30"},
    {"date": "2026-04-22", "team1": "RCB",  "team2": "RR",   "venue": "M. Chinnaswamy Stadium, Bengaluru",      "time": "19:30"},
    {"date": "2026-04-23", "team1": "PBKS", "team2": "CSK",  "venue": "IS Bindra PCA Stadium, Mohali",          "time": "19:30"},
    {"date": "2026-04-24", "team1": "GT",   "team2": "SRH",  "venue": "Narendra Modi Stadium, Ahmedabad",       "time": "19:30"},
    {"date": "2026-04-25", "team1": "LSG",  "team2": "DC",   "venue": "BRSABV Ekana Cricket Stadium, Lucknow",  "time": "19:30"},
    {"date": "2026-04-26", "team1": "KKR",  "team2": "RCB",  "venue": "Eden Gardens, Kolkata",                  "time": "15:30"},
    {"date": "2026-04-26", "team1": "MI",   "team2": "PBKS", "venue": "Wankhede Stadium, Mumbai",               "time": "19:30"},
    {"date": "2026-04-27", "team1": "CSK",  "team2": "GT",   "venue": "MA Chidambaram Stadium, Chennai",        "time": "15:30"},
    {"date": "2026-04-27", "team1": "RR",   "team2": "DC",   "venue": "Sawai Mansingh Stadium, Jaipur",         "time": "19:30"},
    {"date": "2026-04-28", "team1": "SRH",  "team2": "KKR",  "venue": "Rajiv Gandhi Intl. Stadium, Hyderabad",  "time": "19:30"},
    {"date": "2026-04-29", "team1": "LSG",  "team2": "MI",   "venue": "BRSABV Ekana Cricket Stadium, Lucknow",  "time": "19:30"},
    {"date": "2026-04-30", "team1": "PBKS", "team2": "RCB",  "venue": "IS Bindra PCA Stadium, Mohali",          "time": "19:30"},
    {"date": "2026-05-01", "team1": "GT",   "team2": "RR",   "venue": "Narendra Modi Stadium, Ahmedabad",       "time": "19:30"},
    {"date": "2026-05-02", "team1": "CSK",  "team2": "KKR",  "venue": "MA Chidambaram Stadium, Chennai",        "time": "19:30"},
    {"date": "2026-05-03", "team1": "MI",   "team2": "DC",   "venue": "Wankhede Stadium, Mumbai",               "time": "15:30"},
    {"date": "2026-05-03", "team1": "SRH",  "team2": "LSG",  "venue": "Rajiv Gandhi Intl. Stadium, Hyderabad",  "time": "19:30"},
    {"date": "2026-05-04", "team1": "RCB",  "team2": "GT",   "venue": "M. Chinnaswamy Stadium, Bengaluru",      "time": "15:30"},
    {"date": "2026-05-04", "team1": "RR",   "team2": "CSK",  "venue": "Sawai Mansingh Stadium, Jaipur",         "time": "19:30"},
    {"date": "2026-05-05", "team1": "DC",   "team2": "SRH",  "venue": "Arun Jaitley Stadium, Delhi",            "time": "19:30"},
    {"date": "2026-05-06", "team1": "KKR",  "team2": "MI",   "venue": "Eden Gardens, Kolkata",                  "time": "19:30"},
    {"date": "2026-05-07", "team1": "LSG",  "team2": "PBKS", "venue": "BRSABV Ekana Cricket Stadium, Lucknow",  "time": "19:30"},
    {"date": "2026-05-08", "team1": "GT",   "team2": "DC",   "venue": "Narendra Modi Stadium, Ahmedabad",       "time": "19:30"},
    {"date": "2026-05-09", "team1": "RCB",  "team2": "CSK",  "venue": "M. Chinnaswamy Stadium, Bengaluru",      "time": "15:30"},
    {"date": "2026-05-09", "team1": "RR",   "team2": "KKR",  "venue": "Sawai Mansingh Stadium, Jaipur",         "time": "19:30"},
    {"date": "2026-05-10", "team1": "SRH",  "team2": "GT",   "venue": "Rajiv Gandhi Intl. Stadium, Hyderabad",  "time": "15:30"},
    {"date": "2026-05-10", "team1": "PBKS", "team2": "MI",   "venue": "IS Bindra PCA Stadium, Mohali",          "time": "19:30"},
    {"date": "2026-05-11", "team1": "CSK",  "team2": "LSG",  "venue": "MA Chidambaram Stadium, Chennai",        "time": "19:30"},
    {"date": "2026-05-12", "team1": "DC",   "team2": "KKR",  "venue": "Arun Jaitley Stadium, Delhi",            "time": "19:30"},
    {"date": "2026-05-13", "team1": "RCB",  "team2": "MI",   "venue": "M. Chinnaswamy Stadium, Bengaluru",      "time": "19:30"},
    {"date": "2026-05-14", "team1": "PBKS", "team2": "SRH",  "venue": "IS Bindra PCA Stadium, Mohali",          "time": "19:30"},
    {"date": "2026-05-15", "team1": "GT",   "team2": "CSK",  "venue": "Narendra Modi Stadium, Ahmedabad",       "time": "19:30"},
    {"date": "2026-05-16", "team1": "RR",   "team2": "LSG",  "venue": "Sawai Mansingh Stadium, Jaipur",         "time": "15:30"},
    {"date": "2026-05-16", "team1": "KKR",  "team2": "PBKS", "venue": "Eden Gardens, Kolkata",                  "time": "19:30"},
    {"date": "2026-05-17", "team1": "DC",   "team2": "RCB",  "venue": "Arun Jaitley Stadium, Delhi",            "time": "15:30"},
    {"date": "2026-05-17", "team1": "MI",   "team2": "GT",   "venue": "Wankhede Stadium, Mumbai",               "time": "19:30"},
    {"date": "2026-05-18", "team1": "CSK",  "team2": "SRH",  "venue": "MA Chidambaram Stadium, Chennai",        "time": "19:30"},
    {"date": "2026-05-19", "team1": "LSG",  "team2": "RR",   "venue": "BRSABV Ekana Cricket Stadium, Lucknow",  "time": "19:30"},
    {"date": "2026-05-20", "team1": "KKR",  "team2": "GT",   "venue": "Eden Gardens, Kolkata",                  "time": "19:30"},
    {"date": "2026-05-21", "team1": "PBKS", "team2": "DC",   "venue": "IS Bindra PCA Stadium, Mohali",          "time": "19:30"},
    {"date": "2026-05-22", "team1": "MI",   "team2": "RCB",  "venue": "Wankhede Stadium, Mumbai",               "time": "19:30"},
    {"date": "2026-05-23", "team1": "SRH",  "team2": "RR",   "venue": "Rajiv Gandhi Intl. Stadium, Hyderabad",  "time": "15:30"},
    {"date": "2026-05-23", "team1": "CSK",  "team2": "PBKS", "venue": "MA Chidambaram Stadium, Chennai",        "time": "19:30"},
    {"date": "2026-05-24", "team1": "GT",   "team2": "LSG",  "venue": "Narendra Modi Stadium, Ahmedabad",       "time": "15:30"},
    {"date": "2026-05-24", "team1": "KKR",  "team2": "DC",   "venue": "Eden Gardens, Kolkata",                  "time": "19:30"},
]

# ─────────────────────────────────────────────
# VENUE PITCH PROFILES
# ─────────────────────────────────────────────

VENUE_PROFILES = {
    "Wankhede":       {"type": "Batting Paradise",  "avg_score": 170, "dew": "High",   "toss": "Field", "notes": "Sea breeze helps pacers. Short square boundaries = big 6s."},
    "Eden Gardens":   {"type": "Balanced",          "avg_score": 165, "dew": "Medium", "toss": "Field", "notes": "Spin effective. Heavy dew in 2nd innings."},
    "MA Chidambaram": {"type": "Spin Heaven",       "avg_score": 155, "dew": "Low",    "toss": "Bat",   "notes": "Slow sticky pitch. Spinners dominate. Bat first ideal."},
    "Chinnaswamy":    {"type": "Batting Friendly",  "avg_score": 185, "dew": "Medium", "toss": "Field", "notes": "High altitude = big scores. Pick max batters/hitters."},
    "Rajiv Gandhi":   {"type": "Balanced",          "avg_score": 165, "dew": "Medium", "toss": "Field", "notes": "Pace and spin both get help."},
    "Arun Jaitley":   {"type": "Balanced",          "avg_score": 160, "dew": "High",   "toss": "Field", "notes": "Dew huge factor at night. Sluggish surface later."},
    "Sawai Mansingh": {"type": "Bowling Friendly",  "avg_score": 155, "dew": "Low",    "toss": "Bat",   "notes": "Spinners and seam both effective. Bat first advantage."},
    "Narendra Modi":  {"type": "Batting Paradise",  "avg_score": 175, "dew": "Medium", "toss": "Field", "notes": "Large ground but fast outfield. Spinners useful."},
    "IS Bindra":      {"type": "Balanced",          "avg_score": 160, "dew": "Low",    "toss": "Bat",   "notes": "Overcast helps pacers. Good batting track."},
    "BRSABV Ekana":   {"type": "Bowling Friendly",  "avg_score": 150, "dew": "High",   "toss": "Field", "notes": "Slow pitch. Pacers dominate."},
}

# ─────────────────────────────────────────────
# IPL 2026 SQUAD DATABASE — FULLY UPDATED
# Source: Official IPL 2026 squads post-auction (Dec 16 2025)
# pts = estimated Dream11 average points (based on form & role)
# ─────────────────────────────────────────────

IPL_PLAYERS = {

    # ── CHENNAI SUPER KINGS ──────────────────────────────────────────────
    # Key changes: Sanju Samson IN (from RR), Jadeja/Conway/Rahane OUT
    # Buys: Prashant Veer, Kartik Sharma, Matt Henry, Matthew Short, Sarfaraz Khan
    "CSK": [
        {"name": "MS Dhoni",          "role": "WK",   "batting_pos": "No.7",   "pts": 48, "form": "Good"},
        {"name": "Ruturaj Gaikwad",   "role": "BAT",  "batting_pos": "Opener", "pts": 58, "form": "Good"},
        {"name": "Sanju Samson",      "role": "WK",   "batting_pos": "Opener", "pts": 62, "form": "Excellent"},
        {"name": "Ayush Mhatre",      "role": "BAT",  "batting_pos": "No.3",   "pts": 50, "form": "Good"},
        {"name": "Dewald Brevis",     "role": "BAT",  "batting_pos": "No.4",   "pts": 48, "form": "Good"},
        {"name": "Shivam Dube",       "role": "AR",   "batting_pos": "No.5",   "pts": 55, "form": "Good"},
        {"name": "Matthew Short",     "role": "AR",   "batting_pos": "No.3",   "pts": 46, "form": "Good"},
        {"name": "Jamie Overton",     "role": "AR",   "batting_pos": "No.6",   "pts": 44, "form": "Good"},
        {"name": "Kartik Sharma",     "role": "AR",   "batting_pos": "No.5",   "pts": 50, "form": "Good"},
        {"name": "Noor Ahmad",        "role": "BOWL", "batting_pos": "No.9",   "pts": 48, "form": "Good"},
        {"name": "Matt Henry",        "role": "BOWL", "batting_pos": "No.10",  "pts": 45, "form": "Good"},
        {"name": "Anshul Kamboj",     "role": "BOWL", "batting_pos": "No.11",  "pts": 42, "form": "Good"},
        {"name": "Khaleel Ahmed",     "role": "BOWL", "batting_pos": "No.10",  "pts": 44, "form": "Good"},
        {"name": "Sarfaraz Khan",     "role": "BAT",  "batting_pos": "No.4",   "pts": 45, "form": "Good"},
        {"name": "Prashant Veer",     "role": "BOWL", "batting_pos": "No.9",   "pts": 46, "form": "Good"},
        {"name": "Nathan Ellis",      "role": "BOWL", "batting_pos": "No.10",  "pts": 44, "form": "Good"},
        {"name": "Shreyas Gopal",     "role": "BOWL", "batting_pos": "No.9",   "pts": 40, "form": "Average"},
        {"name": "Mukesh Choudhary",  "role": "BOWL", "batting_pos": "No.11",  "pts": 38, "form": "Average"},
        {"name": "Urvil Patel",       "role": "WK",   "batting_pos": "Opener", "pts": 42, "form": "Average"},
        {"name": "Rahul Chahar",      "role": "BOWL", "batting_pos": "No.9",   "pts": 42, "form": "Good"},
        {"name": "Akeal Hosein",      "role": "AR",   "batting_pos": "No.8",   "pts": 38, "form": "Average"},
    ],

    # ── DELHI CAPITALS ───────────────────────────────────────────────────
    # Key changes: Nitish Rana IN (from RR), Rishabh Pant OUT (to LSG)
    # Buys: Ben Duckett, Pathum Nissanka, David Miller, Kyle Jamieson, Lungi Ngidi
    "DC": [
        {"name": "KL Rahul",          "role": "WK",   "batting_pos": "Opener", "pts": 60, "form": "Good"},
        {"name": "Abishek Porel",     "role": "WK",   "batting_pos": "No.6",   "pts": 44, "form": "Good"},
        {"name": "Nitish Rana",       "role": "BAT",  "batting_pos": "Opener", "pts": 48, "form": "Good"},
        {"name": "Pathum Nissanka",   "role": "BAT",  "batting_pos": "No.3",   "pts": 50, "form": "Good"},
        {"name": "Ben Duckett",       "role": "BAT",  "batting_pos": "No.3",   "pts": 52, "form": "Good"},
        {"name": "Axar Patel",        "role": "AR",   "batting_pos": "No.5",   "pts": 58, "form": "Good"},
        {"name": "Tristan Stubbs",    "role": "AR",   "batting_pos": "No.6",   "pts": 48, "form": "Average"},
        {"name": "David Miller",      "role": "BAT",  "batting_pos": "No.5",   "pts": 52, "form": "Good"},
        {"name": "Ashutosh Sharma",   "role": "AR",   "batting_pos": "No.7",   "pts": 40, "form": "Good"},
        {"name": "Kuldeep Yadav",     "role": "BOWL", "batting_pos": "No.9",   "pts": 55, "form": "Good"},
        {"name": "Mitchell Starc",    "role": "BOWL", "batting_pos": "No.11",  "pts": 52, "form": "Good"},
        {"name": "T Natarajan",       "role": "BOWL", "batting_pos": "No.10",  "pts": 46, "form": "Good"},
        {"name": "Kyle Jamieson",     "role": "AR",   "batting_pos": "No.8",   "pts": 44, "form": "Good"},
        {"name": "Lungi Ngidi",       "role": "BOWL", "batting_pos": "No.10",  "pts": 44, "form": "Good"},
        {"name": "Karun Nair",        "role": "BAT",  "batting_pos": "No.4",   "pts": 42, "form": "Good"},
        {"name": "Sameer Rizvi",      "role": "BAT",  "batting_pos": "No.5",   "pts": 40, "form": "Average"},
        {"name": "Prithvi Shaw",      "role": "BAT",  "batting_pos": "Opener", "pts": 48, "form": "Good"},
        {"name": "Auqib Nabi Dar",    "role": "BOWL", "batting_pos": "No.9",   "pts": 42, "form": "Good"},
    ],

    # ── GUJARAT TITANS ───────────────────────────────────────────────────
    # Key changes: Hardik/Rashid Khan gone; Shubman Gill captain, Jos Buttler in
    # Major retentions: Shubman Gill, Sai Sudharsan, Rashid Khan, Kagiso Rabada
    "GT": [
        {"name": "Shubman Gill",      "role": "BAT",  "batting_pos": "Opener", "pts": 65, "form": "Excellent"},
        {"name": "B Sai Sudharsan",   "role": "BAT",  "batting_pos": "No.3",   "pts": 55, "form": "Good"},
        {"name": "Jos Buttler",       "role": "WK",   "batting_pos": "Opener", "pts": 60, "form": "Good"},
        {"name": "Anuj Rawat",        "role": "WK",   "batting_pos": "No.6",   "pts": 42, "form": "Average"},
        {"name": "Kumar Kushagra",    "role": "WK",   "batting_pos": "No.7",   "pts": 40, "form": "Average"},
        {"name": "Glenn Phillips",    "role": "AR",   "batting_pos": "No.4",   "pts": 52, "form": "Good"},
        {"name": "Shahrukh Khan",     "role": "BAT",  "batting_pos": "No.5",   "pts": 44, "form": "Good"},
        {"name": "Rahul Tewatia",     "role": "AR",   "batting_pos": "No.6",   "pts": 50, "form": "Good"},
        {"name": "Washington Sundar", "role": "AR",   "batting_pos": "No.7",   "pts": 52, "form": "Good"},
        {"name": "Jason Holder",      "role": "AR",   "batting_pos": "No.8",   "pts": 48, "form": "Good"},
        {"name": "Rashid Khan",       "role": "AR",   "batting_pos": "No.8",   "pts": 65, "form": "Excellent"},
        {"name": "Kagiso Rabada",     "role": "BOWL", "batting_pos": "No.10",  "pts": 58, "form": "Good"},
        {"name": "Mohammed Siraj",    "role": "BOWL", "batting_pos": "No.11",  "pts": 50, "form": "Good"},
        {"name": "Prasidh Krishna",   "role": "BOWL", "batting_pos": "No.10",  "pts": 48, "form": "Good"},
        {"name": "Nishant Sindhu",    "role": "AR",   "batting_pos": "No.7",   "pts": 40, "form": "Good"},
        {"name": "Sai Kishore",       "role": "BOWL", "batting_pos": "No.9",   "pts": 44, "form": "Good"},
        {"name": "Jayant Yadav",      "role": "AR",   "batting_pos": "No.8",   "pts": 40, "form": "Average"},
        {"name": "Ishant Sharma",     "role": "BOWL", "batting_pos": "No.11",  "pts": 36, "form": "Average"},
        {"name": "Manav Suthar",      "role": "BOWL", "batting_pos": "No.9",   "pts": 38, "form": "Average"},
        {"name": "Gurnoor Brar",      "role": "BOWL", "batting_pos": "No.10",  "pts": 40, "form": "Good"},
    ],

    # ── KOLKATA KNIGHT RIDERS ────────────────────────────────────────────
    # Key changes: Cameron Green, Matheesha Pathirana, Rachin Ravindra in
    # Mustafizur Rahman released (replaced by Blessing Muzarabani)
    "KKR": [
        {"name": "Sunil Narine",         "role": "AR",   "batting_pos": "Opener", "pts": 62, "form": "Excellent"},
        {"name": "Ajinkya Rahane",        "role": "BAT",  "batting_pos": "Opener", "pts": 40, "form": "Average"},
        {"name": "Angkrish Raghuvanshi", "role": "BAT",  "batting_pos": "No.3",   "pts": 46, "form": "Good"},
        {"name": "Rinku Singh",          "role": "BAT",  "batting_pos": "No.5",   "pts": 52, "form": "Good"},
        {"name": "Rovman Powell",        "role": "BAT",  "batting_pos": "No.5",   "pts": 48, "form": "Good"},
        {"name": "Finn Allen",           "role": "WK",   "batting_pos": "Opener", "pts": 55, "form": "Good"},
        {"name": "Cameron Green",        "role": "AR",   "batting_pos": "No.4",   "pts": 58, "form": "Good"},
        {"name": "Rachin Ravindra",      "role": "AR",   "batting_pos": "No.3",   "pts": 50, "form": "Good"},
        {"name": "Ramandeep Singh",      "role": "AR",   "batting_pos": "No.7",   "pts": 40, "form": "Average"},
        {"name": "Anukul Roy",           "role": "AR",   "batting_pos": "No.8",   "pts": 38, "form": "Average"},
        {"name": "Varun Chakravarthy",   "role": "BOWL", "batting_pos": "No.11",  "pts": 55, "form": "Excellent"},
        {"name": "Harshit Rana",         "role": "BOWL", "batting_pos": "No.9",   "pts": 46, "form": "Good"},
        {"name": "Matheesha Pathirana",  "role": "BOWL", "batting_pos": "No.11",  "pts": 52, "form": "Good"},
        {"name": "Vaibhav Arora",        "role": "BOWL", "batting_pos": "No.10",  "pts": 42, "form": "Good"},
        {"name": "Akash Deep",           "role": "BOWL", "batting_pos": "No.10",  "pts": 44, "form": "Good"},
        {"name": "Blessing Muzarabani",  "role": "BOWL", "batting_pos": "No.9",   "pts": 44, "form": "Good"},
        {"name": "Umran Malik",          "role": "BOWL", "batting_pos": "No.11",  "pts": 38, "form": "Average"},
        {"name": "Manish Pandey",        "role": "BAT",  "batting_pos": "No.4",   "pts": 38, "form": "Average"},
    ],

    # ── MUMBAI INDIANS ───────────────────────────────────────────────────
    # Key additions: Quinton de Kock (from auction), Sherfane Rutherford (GT trade),
    #                Shardul Thakur (LSG trade), Mayank Markande (KKR trade)
    # Ishan Kishan OUT
    "MI": [
        {"name": "Rohit Sharma",       "role": "BAT",  "batting_pos": "Opener", "pts": 58, "form": "Good"},
        {"name": "Ryan Rickelton",     "role": "WK",   "batting_pos": "Opener", "pts": 50, "form": "Good"},
        {"name": "Quinton de Kock",    "role": "WK",   "batting_pos": "Opener", "pts": 52, "form": "Good"},
        {"name": "Suryakumar Yadav",   "role": "BAT",  "batting_pos": "No.3",   "pts": 60, "form": "Good"},
        {"name": "Tilak Varma",        "role": "BAT",  "batting_pos": "No.4",   "pts": 55, "form": "Excellent"},
        {"name": "Hardik Pandya",      "role": "AR",   "batting_pos": "No.5",   "pts": 65, "form": "Good"},
        {"name": "Sherfane Rutherford","role": "AR",   "batting_pos": "No.6",   "pts": 42, "form": "Average"},
        {"name": "Will Jacks",         "role": "AR",   "batting_pos": "No.6",   "pts": 50, "form": "Good"},
        {"name": "Mitchell Santner",   "role": "AR",   "batting_pos": "No.7",   "pts": 44, "form": "Good"},
        {"name": "Naman Dhir",         "role": "AR",   "batting_pos": "No.7",   "pts": 38, "form": "Average"},
        {"name": "Shardul Thakur",     "role": "AR",   "batting_pos": "No.8",   "pts": 46, "form": "Good"},
        {"name": "Deepak Chahar",      "role": "BOWL", "batting_pos": "No.9",   "pts": 42, "form": "Good"},
        {"name": "Trent Boult",        "role": "BOWL", "batting_pos": "No.11",  "pts": 50, "form": "Good"},
        {"name": "Jasprit Bumrah",     "role": "BOWL", "batting_pos": "No.11",  "pts": 72, "form": "Excellent"},
        {"name": "Ashwani Kumar",      "role": "BOWL", "batting_pos": "No.9",   "pts": 38, "form": "Good"},
        {"name": "Robin Minz",         "role": "WK",   "batting_pos": "No.7",   "pts": 36, "form": "Average"},
        {"name": "Corbin Bosch",       "role": "AR",   "batting_pos": "No.8",   "pts": 40, "form": "Good"},
        {"name": "Mayank Markande",    "role": "BOWL", "batting_pos": "No.9",   "pts": 38, "form": "Average"},
    ],

    # ── PUNJAB KINGS ─────────────────────────────────────────────────────
    # Key retentions: Arshdeep Singh, Shashank Singh, Priyansh Arya, Prabhsimran Singh
    # Sam Curran moved to RR
    "PBKS": [
        {"name": "Prabhsimran Singh",  "role": "WK",   "batting_pos": "Opener", "pts": 55, "form": "Good"},
        {"name": "Priyansh Arya",      "role": "BAT",  "batting_pos": "Opener", "pts": 52, "form": "Good"},
        {"name": "Shreyas Iyer",       "role": "BAT",  "batting_pos": "No.3",   "pts": 55, "form": "Good"},
        {"name": "Nehal Wadhera",      "role": "BAT",  "batting_pos": "No.4",   "pts": 46, "form": "Good"},
        {"name": "Shashank Singh",     "role": "BAT",  "batting_pos": "No.5",   "pts": 50, "form": "Good"},
        {"name": "Marcus Stoinis",     "role": "AR",   "batting_pos": "No.4",   "pts": 55, "form": "Good"},
        {"name": "Azmatullah Omarzai", "role": "AR",   "batting_pos": "No.6",   "pts": 48, "form": "Good"},
        {"name": "Harpreet Brar",      "role": "AR",   "batting_pos": "No.7",   "pts": 40, "form": "Average"},
        {"name": "Marco Jansen",       "role": "AR",   "batting_pos": "No.8",   "pts": 48, "form": "Good"},
        {"name": "Arshdeep Singh",     "role": "BOWL", "batting_pos": "No.9",   "pts": 55, "form": "Good"},
        {"name": "Yuzvendra Chahal",   "role": "BOWL", "batting_pos": "No.11",  "pts": 52, "form": "Good"},
        {"name": "Lockie Ferguson",    "role": "BOWL", "batting_pos": "No.10",  "pts": 48, "form": "Good"},
        {"name": "Harnoor Singh",      "role": "BAT",  "batting_pos": "Opener", "pts": 40, "form": "Average"},
        {"name": "Mitchell Owen",      "role": "BAT",  "batting_pos": "No.3",   "pts": 44, "form": "Good"},
        {"name": "Musheer Khan",       "role": "BAT",  "batting_pos": "No.5",   "pts": 42, "form": "Good"},
        {"name": "Vijaykumar Vyshak",  "role": "BOWL", "batting_pos": "No.10",  "pts": 40, "form": "Good"},
        {"name": "Xavier Bartlett",    "role": "BOWL", "batting_pos": "No.10",  "pts": 40, "form": "Average"},
    ],

    # ── RAJASTHAN ROYALS ─────────────────────────────────────────────────
    # Key changes: Ravindra Jadeja IN (CSK trade), Sam Curran IN (CSK trade),
    #              Donovan Ferreira IN (DC trade), Jos Buttler OUT (GT),
    #              Yashasvi Jaiswal retained, Vaibhav Suryavanshi big new talent
    "RR": [
        {"name": "Yashasvi Jaiswal",    "role": "BAT",  "batting_pos": "Opener", "pts": 65, "form": "Excellent"},
        {"name": "Vaibhav Suryavanshi", "role": "BAT",  "batting_pos": "Opener", "pts": 55, "form": "Good"},
        {"name": "Dhruv Jurel",         "role": "WK",   "batting_pos": "No.4",   "pts": 48, "form": "Good"},
        {"name": "Riyan Parag",         "role": "AR",   "batting_pos": "No.3",   "pts": 52, "form": "Good"},
        {"name": "Shimron Hetmyer",     "role": "BAT",  "batting_pos": "No.5",   "pts": 50, "form": "Good"},
        {"name": "Ravindra Jadeja",     "role": "AR",   "batting_pos": "No.5",   "pts": 62, "form": "Excellent"},
        {"name": "Sam Curran",          "role": "AR",   "batting_pos": "No.6",   "pts": 55, "form": "Good"},
        {"name": "Donovan Ferreira",    "role": "AR",   "batting_pos": "No.6",   "pts": 44, "form": "Good"},
        {"name": "Ravi Bishnoi",        "role": "BOWL", "batting_pos": "No.10",  "pts": 52, "form": "Good"},
        {"name": "Jofra Archer",        "role": "BOWL", "batting_pos": "No.11",  "pts": 58, "form": "Good"},
        {"name": "Nandre Burger",       "role": "BOWL", "batting_pos": "No.10",  "pts": 48, "form": "Good"},
        {"name": "Sandeep Sharma",      "role": "BOWL", "batting_pos": "No.9",   "pts": 44, "form": "Good"},
        {"name": "Brijesh Sharma",      "role": "BOWL", "batting_pos": "No.9",   "pts": 42, "form": "Good"},
        {"name": "Tushar Deshpande",    "role": "BOWL", "batting_pos": "No.10",  "pts": 40, "form": "Average"},
        {"name": "Lhuan-dre Pretorius", "role": "AR",   "batting_pos": "No.7",   "pts": 44, "form": "Good"},
        {"name": "Adam Milne",          "role": "BOWL", "batting_pos": "No.11",  "pts": 42, "form": "Good"},
        {"name": "Yudhvir Singh",       "role": "BOWL", "batting_pos": "No.9",   "pts": 40, "form": "Average"},
        {"name": "Kuldeep Sen",         "role": "BOWL", "batting_pos": "No.10",  "pts": 38, "form": "Average"},
    ],

    # ── ROYAL CHALLENGERS BENGALURU ──────────────────────────────────────
    # Key changes: Venkatesh Iyer IN (auction), Krunal Pandya retained
    # Faf du Plessis, Glenn Maxwell, Liam Livingstone OUT
    "RCB": [
        {"name": "Virat Kohli",         "role": "BAT",  "batting_pos": "Opener", "pts": 68, "form": "Excellent"},
        {"name": "Rajat Patidar",       "role": "BAT",  "batting_pos": "No.3",   "pts": 52, "form": "Good"},
        {"name": "Phil Salt",           "role": "WK",   "batting_pos": "Opener", "pts": 58, "form": "Good"},
        {"name": "Jitesh Sharma",       "role": "WK",   "batting_pos": "No.5",   "pts": 48, "form": "Good"},
        {"name": "Tim David",           "role": "BAT",  "batting_pos": "No.4",   "pts": 52, "form": "Good"},
        {"name": "Devdutt Padikkal",    "role": "BAT",  "batting_pos": "No.4",   "pts": 48, "form": "Good"},
        {"name": "Venkatesh Iyer",      "role": "AR",   "batting_pos": "No.5",   "pts": 54, "form": "Good"},
        {"name": "Jaco Bethell",        "role": "AR",   "batting_pos": "No.6",   "pts": 50, "form": "Good"},
        {"name": "Krunal Pandya",       "role": "AR",   "batting_pos": "No.6",   "pts": 50, "form": "Good"},
        {"name": "Romario Shepherd",    "role": "AR",   "batting_pos": "No.7",   "pts": 42, "form": "Average"},
        {"name": "Josh Hazlewood",      "role": "BOWL", "batting_pos": "No.11",  "pts": 52, "form": "Good"},
        {"name": "Bhuvneshwar Kumar",   "role": "BOWL", "batting_pos": "No.10",  "pts": 46, "form": "Good"},
        {"name": "Yash Dayal",          "role": "BOWL", "batting_pos": "No.10",  "pts": 44, "form": "Good"},
        {"name": "Mangesh Yadav",       "role": "BOWL", "batting_pos": "No.9",   "pts": 44, "form": "Good"},
        {"name": "Rasikh Salam",        "role": "BOWL", "batting_pos": "No.11",  "pts": 40, "form": "Good"},
        {"name": "Nuwan Thushara",      "role": "BOWL", "batting_pos": "No.10",  "pts": 40, "form": "Average"},
        {"name": "Suyash Sharma",       "role": "BOWL", "batting_pos": "No.9",   "pts": 42, "form": "Good"},
        {"name": "Swapnil Singh",       "role": "AR",   "batting_pos": "No.8",   "pts": 38, "form": "Average"},
    ],

    # ── SUNRISERS HYDERABAD ──────────────────────────────────────────────
    # Key additions: Liam Livingstone (13cr), Ishan Kishan, Kamindu Mendis
    # Mohammad Shami traded to LSG
    "SRH": [
        {"name": "Travis Head",        "role": "BAT",  "batting_pos": "Opener", "pts": 65, "form": "Excellent"},
        {"name": "Abhishek Sharma",    "role": "BAT",  "batting_pos": "Opener", "pts": 60, "form": "Good"},
        {"name": "Ishan Kishan",       "role": "WK",   "batting_pos": "No.3",   "pts": 54, "form": "Good"},
        {"name": "Heinrich Klaasen",   "role": "WK",   "batting_pos": "No.4",   "pts": 65, "form": "Excellent"},
        {"name": "Liam Livingstone",   "role": "AR",   "batting_pos": "No.5",   "pts": 58, "form": "Good"},
        {"name": "Nitish Kumar Reddy", "role": "AR",   "batting_pos": "No.6",   "pts": 52, "form": "Good"},
        {"name": "Pat Cummins",        "role": "AR",   "batting_pos": "No.7",   "pts": 60, "form": "Good"},
        {"name": "Kamindu Mendis",     "role": "AR",   "batting_pos": "No.6",   "pts": 50, "form": "Good"},
        {"name": "Brydon Carse",       "role": "BOWL", "batting_pos": "No.9",   "pts": 48, "form": "Good"},
        {"name": "Harshal Patel",      "role": "BOWL", "batting_pos": "No.9",   "pts": 48, "form": "Good"},
        {"name": "Jaydev Unadkat",     "role": "BOWL", "batting_pos": "No.10",  "pts": 40, "form": "Average"},
        {"name": "Aiden Markram",      "role": "BAT",  "batting_pos": "No.4",   "pts": 52, "form": "Good"},
        {"name": "Shivam Mavi",        "role": "BOWL", "batting_pos": "No.10",  "pts": 42, "form": "Good"},
        {"name": "Jack Edwards",       "role": "BOWL", "batting_pos": "No.9",   "pts": 44, "form": "Good"},
        {"name": "Aniket Verma",       "role": "BAT",  "batting_pos": "No.5",   "pts": 40, "form": "Good"},
        {"name": "Abdul Samad",        "role": "AR",   "batting_pos": "No.7",   "pts": 42, "form": "Good"},
        {"name": "Harsh Dubey",        "role": "BOWL", "batting_pos": "No.9",   "pts": 38, "form": "Average"},
    ],

    # ── LUCKNOW SUPER GIANTS ─────────────────────────────────────────────
    # Key changes: Rishabh Pant IN (retained from 2025), Mohammad Shami IN (SRH trade),
    #              Arjun Tendulkar IN (MI trade), KL Rahul OUT (to DC)
    "LSG": [
        {"name": "Rishabh Pant",       "role": "WK",   "batting_pos": "Opener", "pts": 65, "form": "Excellent"},
        {"name": "Nicholas Pooran",    "role": "BAT",  "batting_pos": "No.3",   "pts": 60, "form": "Excellent"},
        {"name": "Ayush Badoni",       "role": "BAT",  "batting_pos": "No.4",   "pts": 48, "form": "Good"},
        {"name": "Akshat Raghuvanshi", "role": "BAT",  "batting_pos": "No.5",   "pts": 44, "form": "Good"},
        {"name": "Aiden Markram",      "role": "BAT",  "batting_pos": "No.3",   "pts": 52, "form": "Good"},
        {"name": "Matthew Breetzke",   "role": "BAT",  "batting_pos": "No.4",   "pts": 46, "form": "Good"},
        {"name": "Josh Inglis",        "role": "WK",   "batting_pos": "Opener", "pts": 50, "form": "Good"},
        {"name": "Arshin Kulkarni",    "role": "AR",   "batting_pos": "No.6",   "pts": 42, "form": "Good"},
        {"name": "Mitchell Marsh",     "role": "AR",   "batting_pos": "No.5",   "pts": 55, "form": "Good"},
        {"name": "Shahbaz Ahmed",      "role": "AR",   "batting_pos": "No.7",   "pts": 40, "form": "Average"},
        {"name": "Wanindu Hasaranga",  "role": "AR",   "batting_pos": "No.8",   "pts": 52, "form": "Good"},
        {"name": "Mohammad Shami",     "role": "BOWL", "batting_pos": "No.10",  "pts": 58, "form": "Excellent"},
        {"name": "Avesh Khan",         "role": "BOWL", "batting_pos": "No.9",   "pts": 46, "form": "Good"},
        {"name": "Mohsin Khan",        "role": "BOWL", "batting_pos": "No.11",  "pts": 44, "form": "Good"},
        {"name": "Anrich Nortje",      "role": "BOWL", "batting_pos": "No.11",  "pts": 50, "form": "Good"},
        {"name": "Mukul Choudhary",    "role": "BOWL", "batting_pos": "No.10",  "pts": 44, "form": "Good"},
        {"name": "Akash Singh",        "role": "BOWL", "batting_pos": "No.10",  "pts": 40, "form": "Average"},
        {"name": "Digvesh Rathi",      "role": "BOWL", "batting_pos": "No.9",   "pts": 38, "form": "Average"},
        {"name": "Mayank Yadav",       "role": "BOWL", "batting_pos": "No.11",  "pts": 46, "form": "Good"},
        {"name": "Arjun Tendulkar",    "role": "AR",   "batting_pos": "No.8",   "pts": 36, "form": "Average"},
    ],
}


# ─────────────────────────────────────────────
# CRICAPI — MATCH FINDER + XI FETCHER
# ─────────────────────────────────────────────

def _cricapi_get(endpoint: str, params: dict) -> dict | None:
    params["apikey"] = CRICAPI_KEY
    params.setdefault("offset", 0)
    try:
        r = requests.get(
            f"https://api.cricapi.com/v1/{endpoint}",
            params=params, timeout=10,
        )
        if not r.ok:
            logger.warning(f"CricAPI /{endpoint} HTTP {r.status_code}")
            return None
        body = r.json()
        if body.get("status") != "success":
            logger.warning(f"CricAPI /{endpoint}: {body.get('status')} — {body.get('reason','')}")
            return None
        return body
    except Exception as e:
        logger.warning(f"CricAPI /{endpoint} error: {e}")
        return None


def _team_name_matches(api_name: str, short_code: str) -> bool:
    full = TEAM_FULL_NAMES.get(short_code.upper(), short_code.lower())
    api_lower = api_name.lower().strip()
    return full in api_lower or api_lower in full


def _find_match_id(team1: str, team2: str) -> str | None:
    today_str = date.today().strftime("%Y-%m-%d")
    for endpoint in ["currentMatches", "matches"]:
        body = _cricapi_get(endpoint, {})
        if not body:
            continue
        for m in body.get("data", []):
            m_date = (m.get("date") or m.get("dateTimeGMT") or "")[:10]
            if m_date != today_str:
                continue
            series = (m.get("series") or m.get("seriesName") or "").lower()
            m_type = (m.get("matchType") or "").lower()
            if "ipl" not in series and m_type not in ("t20", "ipl"):
                continue
            team_names = [t.get("name", "") for t in m.get("teamInfo", [])] or m.get("teams", [])
            if (any(_team_name_matches(n, team1) for n in team_names) and
                    any(_team_name_matches(n, team2) for n in team_names)):
                match_id = m.get("id", "")
                logger.info(f"✅ CricAPI match: '{m.get('name','')}' id={match_id}")
                return match_id
    logger.info(f"CricAPI: no match today for {team1} vs {team2}")
    return None


def _fetch_xi_from_match_info(match_id: str, team1: str, team2: str) -> tuple[list, list]:
    body = _cricapi_get("match_info", {"id": match_id})
    if not body:
        return [], []
    match_data = body.get("data", {})
    lineup = match_data.get("lineup") or {}
    if isinstance(lineup, dict) and len(lineup) >= 2:
        entries = list(lineup.values())
        def extract_names(raw):
            return [n for n in [
                p.get("name") or p.get("player") or "" if isinstance(p, dict) else str(p)
                for p in raw
            ] if n]
        xi1_names = extract_names(entries[0] if entries else [])
        xi2_names = extract_names(entries[1] if len(entries) > 1 else [])
        if len(xi1_names) >= 10 and len(xi2_names) >= 10:
            logger.info(f"✅ CricAPI confirmed XI: {len(xi1_names)} + {len(xi2_names)}")
            return xi1_names, xi2_names
    logger.info("CricAPI: Playing XI not yet announced (pre-toss)")
    return [], []


# ─────────────────────────────────────────────
# PLAYING XI RESOLUTION
# ─────────────────────────────────────────────

def resolve_playing_xi(team1: str, team2: str) -> tuple[list, list, str]:
    """Returns (xi_team1, xi_team2, xi_source)"""

    # Method 1: Manual ENV
    if PLAYING_XI_T1_ENV and PLAYING_XI_T2_ENV:
        xi1_names = [n.strip() for n in PLAYING_XI_T1_ENV.split(",") if n.strip()]
        xi2_names = [n.strip() for n in PLAYING_XI_T2_ENV.split(",") if n.strip()]
        if len(xi1_names) >= 10 and len(xi2_names) >= 10:
            xi1 = _names_to_player_objects(xi1_names, team1)
            xi2 = _names_to_player_objects(xi2_names, team2)
            logger.info(f"✅ XI from ENV (manual): {team1}={len(xi1)}, {team2}={len(xi2)}")
            return xi1, xi2, "env_manual"
        logger.warning("PLAYING_XI env vars set but < 10 players — ignoring")

    # Method 2: CricAPI (post-toss only)
    if CRICAPI_KEY:
        match_id = _find_match_id(team1, team2)
        if match_id:
            xi1_names, xi2_names = _fetch_xi_from_match_info(match_id, team1, team2)
            if xi1_names and xi2_names and len(xi1_names) >= 10 and len(xi2_names) >= 10:
                xi1 = _names_to_player_objects(xi1_names, team1)
                xi2 = _names_to_player_objects(xi2_names, team2)
                logger.info(f"✅ XI from CricAPI (confirmed): {team1}={len(xi1)}, {team2}={len(xi2)}")
                return xi1, xi2, "cricapi_confirmed"
            logger.info("CricAPI match found but XI not announced yet")
        else:
            logger.warning("CricAPI match lookup failed")
    else:
        logger.info("No CRICAPI_KEY — using squad filter")

    # Method 3: Smart squad filter
    logger.warning(
        "⚠️ XI not confirmed — using 2026 squad filter. "
        "Set PLAYING_XI_T1 and PLAYING_XI_T2 after toss for accuracy."
    )
    xi1 = _smart_squad_filter(team1)
    xi2 = _smart_squad_filter(team2)
    return xi1, xi2, "squad_estimated"


def _names_to_player_objects(names: list, team: str) -> list:
    squad = IPL_PLAYERS.get(team, [])
    squad_map = {p["name"].lower(): p for p in squad}
    result = []
    for name in names:
        found = squad_map.get(name.lower())
        if found:
            result.append(found)
        else:
            result.append({"name": name, "role": "BAT", "batting_pos": "Unknown", "pts": 45, "form": "Unknown"})
            logger.warning(f"  '{name}' not in {team} squad DB — added with defaults")
    return result


def _smart_squad_filter(team: str) -> list:
    squad = sorted(
        [p for p in IPL_PLAYERS.get(team, []) if not p.get("injury_doubt")],
        key=lambda x: x["pts"], reverse=True,
    )
    selected   = []
    role_count = {"WK": 0, "BAT": 0, "AR": 0, "BOWL": 0}
    role_min   = {"WK": 1, "BAT": 3, "AR": 2, "BOWL": 3}
    role_max   = {"WK": 2, "BAT": 5, "AR": 4, "BOWL": 5}

    for role in ["WK", "BAT", "AR", "BOWL"]:
        for p in squad:
            if p in selected or len(selected) == 11:
                break
            if p["role"] == role and role_count[role] < role_min[role]:
                selected.append(p); role_count[role] += 1

    for p in squad:
        if len(selected) == 11:
            break
        if p in selected:
            continue
        role = p["role"]
        if role_count.get(role, 0) < role_max.get(role, 99):
            selected.append(p); role_count[role] += 1

    return selected[:11]


# ─────────────────────────────────────────────
# SCHEDULE / VENUE HELPERS
# ─────────────────────────────────────────────

def get_today_match():
    today_str = date.today().strftime("%Y-%m-%d")
    today     = date.today()
    if today < IPL_START or today > IPL_END:
        logger.info(f"Outside IPL 2026 season (today={today_str})")
        return None
    matches = [m for m in IPL_2026_SCHEDULE if m["date"] == today_str]
    return matches if matches else None


def get_venue_profile(venue: str) -> dict:
    for key, profile in VENUE_PROFILES.items():
        if key.lower() in venue.lower():
            return profile
    return {"type": "Balanced", "avg_score": 162, "dew": "Medium",
            "toss": "Field", "notes": "Standard pitch conditions."}


# ─────────────────────────────────────────────
# AI TEAM GENERATOR
# ─────────────────────────────────────────────

def generate_5_teams_ai(team1: str, team2: str, venue: str, match_time: str,
                         xi1: list, xi2: list, xi_source: str) -> dict | None:
    pitch = get_venue_profile(venue)
    xi_label = {
        "env_manual":        "✅ CONFIRMED (manual input)",
        "cricapi_confirmed": "✅ CONFIRMED (CricAPI live)",
        "squad_estimated":   "⚠️ ESTIMATED (squad filter — verify after toss)",
    }.get(xi_source, xi_source)

    player_list = "\n".join([
        f"  {p['role']} | {p['name']} ({t}) | Pos: {p.get('batting_pos','?')} "
        f"| Pts: {p.get('pts',45)} | Form: {p.get('form','Good')}"
        for t, xi in [(team1, xi1), (team2, xi2)] for p in xi
    ])

    prompt = f"""IPL 2026 Fantasy Cricket — Generate 5 Dream11/My11Circle teams.

MATCH: {team1} vs {team2}
VENUE: {venue}
TIME: {match_time} IST
XI: {xi_label}

PITCH: {pitch['type']} | Avg: {pitch['avg_score']} | Dew: {pitch['dew']} | Toss: {pitch['toss']} first
NOTE: {pitch['notes']}

PLAYING XI ({len(xi1)+len(xi2)} players — ONLY pick from these):
{player_list}

DREAM11 RULES:
- Exactly 11 players per team
- ONLY from the list above — no other players
- Max 7 from one team, min 4 from each
- Min 1 WK, 1 BAT, 1 AR, 1 BOWL
- 1 Captain (2x) + 1 Vice-Captain (1.5x)

Return ONLY valid JSON (no markdown):
{{
  "match": "{team1} vs {team2}",
  "venue": "{venue}",
  "pitch_type": "{pitch['type']}",
  "toss_tip": "recommendation",
  "xi_source": "{xi_source}",
  "key_insights": ["insight1", "insight2", "insight3"],
  "teams": [
    {{
      "name": "Team N – Name",
      "strategy": "Safe/Grand League/Balanced/Differential/Captain Swap",
      "risk": "Low/Medium/High",
      "captain": "Exact Name from list",
      "vice_captain": "Exact Name from list",
      "players": [{{"name": "Exact Name", "role": "WK/BAT/AR/BOWL", "team": "{team1} or {team2}"}}],
      "why": "1-line explanation"
    }}
  ],
  "must_pick": ["top 3"],
  "avoid": ["avoid and why"],
  "disclaimer": "XI: {xi_source}. Verify before locking."
}}

Team strategies: Safe Bet / Bowling Blitz / All-Rounder Army / Differential Dare / Captain Swap"""

    client = AIClient()
    try:
        result = client.generate_json(
            prompt=prompt,
            system_prompt="Expert Dream11 analyst. ONLY pick from the provided XI. Never invent players. Return ONLY valid JSON.",
            content_mode="market", lang="en",
        )
        if result and result.get("teams"):
            result = _validate_teams(result, xi1, xi2)
            return result
    except Exception as e:
        logger.warning(f"AI error: {e}")
    return None


def _validate_teams(data: dict, xi1: list, xi2: list) -> dict:
    valid = {p["name"].lower() for p in xi1 + xi2}
    for team in data.get("teams", []):
        original = team.get("players", [])
        cleaned  = [p for p in original if p["name"].lower() in valid]
        removed  = [p["name"] for p in original if p["name"].lower() not in valid]
        if removed:
            logger.warning(f"  Removed hallucinated players: {removed}")
        cap_names = {p["name"] for p in cleaned}
        if team.get("captain") not in cap_names and cleaned:
            team["captain"] = cleaned[0]["name"]
        if team.get("vice_captain") not in cap_names and len(cleaned) > 1:
            team["vice_captain"] = cleaned[1]["name"]
        team["players"] = cleaned
    return data


# ─────────────────────────────────────────────
# FALLBACK RULE-BASED TEAMS
# ─────────────────────────────────────────────

def build_fallback_teams(team1: str, team2: str, venue: str,
                          xi1: list, xi2: list, xi_source: str) -> dict:
    pitch  = get_venue_profile(venue)
    p1     = sorted(xi1, key=lambda x: x.get("pts", 45), reverse=True)
    p2     = sorted(xi2, key=lambda x: x.get("pts", 45), reverse=True)
    all_xi = sorted(p1 + p2, key=lambda x: x.get("pts", 45), reverse=True)

    def pick_team(t1_max=6, bowling_boost=False):
        team_out = []; role_count = {"WK":0,"BAT":0,"AR":0,"BOWL":0}
        role_min = {"WK":1,"BAT":3,"AR":2,"BOWL":3}; role_max = {"WK":2,"BAT":5,"AR":4,"BOWL":5}
        t1c = t2c = 0
        pool = sorted(all_xi, key=lambda x: -x.get("pts",45)*(1.3 if bowling_boost and x["role"]=="BOWL" else 1.0))
        for role in ["WK","BAT","AR","BOWL"]:
            for p in pool:
                if role_count[role] >= role_min[role] or len(team_out)==11: break
                if p in team_out: continue
                is_t1 = p in p1
                if (is_t1 and (t1c>=7 or t1c>=t1_max)) or (not is_t1 and t2c>=7): continue
                if p["role"]==role:
                    team_out.append(p); role_count[role]+=1; t1c+=is_t1; t2c+=(not is_t1)
        for p in pool:
            if len(team_out)==11: break
            if p in team_out: continue
            is_t1 = p in p1
            if (is_t1 and (t1c>=7 or t1c>=t1_max)) or (not is_t1 and t2c>=7): continue
            if role_count.get(p["role"],0) < role_max.get(p["role"],99):
                team_out.append(p); role_count[p["role"]]+=1; t1c+=is_t1; t2c+=(not is_t1)
        return team_out[:11]

    def fmt(players, name, strategy, risk, ci=0, vi=1, why=""):
        cap = players[ci]["name"] if ci<len(players) else players[0]["name"]
        vc  = players[vi]["name"] if vi<len(players) else players[1]["name"]
        return {"name":name,"strategy":strategy,"risk":risk,"captain":cap,"vice_captain":vc,
                "players":[{"name":p["name"],"role":p["role"],"team":team1 if p in p1 else team2} for p in players],"why":why}

    top3 = [p["name"] for p in all_xi[:3]]
    return {
        "match":f"{team1} vs {team2}","venue":venue,"pitch_type":pitch["type"],
        "toss_tip":f"{pitch['toss']} first recommended","xi_source":xi_source,
        "key_insights":[f"Pitch: {pitch['type']} avg {pitch['avg_score']}",
                        f"Dew: {pitch['dew']} — {pitch['notes']}",f"Top: {', '.join(top3)}"],
        "teams":[
            fmt(pick_team(6),"Team 1 – Safe Bet XI","Safe","Low",0,1,"Best XI, safe C/VC."),
            fmt(pick_team(6,bowling_boost=True),"Team 2 – Bowling Blitz","Grand League","Medium",2,0,"Wicket-takers as C/VC."),
            fmt(pick_team(5),"Team 3 – Balanced Attack","Balanced","Medium",1,2,"Even team split."),
            fmt(pick_team(4),"Team 4 – Differential Dare","Differential","High",3,1,"Low-ownership picks."),
            fmt(pick_team(7),"Team 5 – Captain Swap","Grand League","High",2,0,"Different captain from T1."),
        ],
        "must_pick":top3,"avoid":[],
        "disclaimer":f"XI from: {xi_source}. Verify final XI before locking.",
    }


# ─────────────────────────────────────────────
# TELEGRAM FORMATTER
# ─────────────────────────────────────────────

def format_telegram_message(data: dict, team1: str, team2: str, xi_source: str) -> list:
    e1 = TEAM_EMOJI.get(team1, "🏏"); e2 = TEAM_EMOJI.get(team2, "🏏")
    xi_badge = {
        "env_manual":        "✅ CONFIRMED XI (manual input after toss)",
        "cricapi_confirmed": "✅ CONFIRMED XI (CricAPI live)",
        "squad_estimated":   "⚠️ ESTIMATED XI — verify after toss!",
    }.get(xi_source, f"ℹ️ {xi_source}")

    insights = "".join([f"• {i}\n" for i in data.get("key_insights", [])])
    header = (
        f"🏏 <b>IPL 2026 — DREAM11 PICKS</b> 🏏\n"
        f"{e1} <b>{team1}</b> vs <b>{team2}</b> {e2}\n\n"
        f"📍 <i>{data.get('venue','')}</i>\n{xi_badge}\n\n"
        f"<b>Pitch:</b> {data.get('pitch_type','Balanced')}\n"
        f"<b>Toss Tip:</b> {data.get('toss_tip','Field first')}\n\n"
        f"<b>📊 Key Insights:</b>\n{insights}"
        f"<b>🌟 Must-Picks:</b> {', '.join(data.get('must_pick',[]))}\n\n"
        f"<i>5 teams — Dream11 / My11Circle</i>\n──────────────────────────────"
    )
    messages = [header]
    risk_emoji = {"Low":"🟢","Medium":"🟡","High":"🔴"}

    for i, team in enumerate(data.get("teams",[]), 1):
        risk = team.get("risk","Medium"); players = team.get("players",[]); cap = team.get("captain",""); vc = team.get("vice_captain","")
        def fmt_p(p):
            suffix = " 🅒" if p["name"]==cap else (" 🅥" if p["name"]==vc else "")
            return f"  {p['name']}{suffix} <i>[{p.get('team','')}]</i>"
        wk_l=[p for p in players if p["role"]=="WK"]; bat_l=[p for p in players if p["role"]=="BAT"]
        ar_l=[p for p in players if p["role"]=="AR"]; bowl_l=[p for p in players if p["role"]=="BOWL"]
        label = team.get("name","").split("–")[-1].strip()
        msg = (
            f"{risk_emoji.get(risk,'🟡')} <b>TEAM {i} — {label}</b>\n"
            f"<i>{team.get('strategy','')} · {risk} Risk · {len(players)} players</i>\n\n"
            f"🧤 WK:\n{chr(10).join([fmt_p(p) for p in wk_l]) or '  —'}\n"
            f"🏏 BAT:\n{chr(10).join([fmt_p(p) for p in bat_l]) or '  —'}\n"
            f"🔄 ALL-ROUNDER:\n{chr(10).join([fmt_p(p) for p in ar_l]) or '  —'}\n"
            f"⚡ BOWLER:\n{chr(10).join([fmt_p(p) for p in bowl_l]) or '  —'}\n\n"
            f"🅒 C: <b>{cap}</b>  |  🅥 VC: <b>{vc}</b>\n"
            f"💡 <i>{team.get('why','')}</i>\n──────────────────────────────"
        )
        messages.append(msg)

    footer = (
        f"⚠️ <b>DISCLAIMER</b>\n{data.get('disclaimer','Verify XI after toss.')}\n"
        f"Never lock before confirmed playing 11 announced.\n\n"
        f"📲 <b>AI360Trading</b> | Free IPL Fantasy\n@ai360trading | 🌐 ai360trading.in"
    )
    messages.append(footer)
    return messages


# ─────────────────────────────────────────────
# TELEGRAM SENDER
# ─────────────────────────────────────────────

def send_to_free_channel(messages: list) -> bool:
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("TELEGRAM_TOKEN or TELEGRAM_CHAT_ID not set"); return False
    success = True
    for i, msg in enumerate(messages):
        try:
            r = requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id":TELEGRAM_CHAT_ID,"text":msg,"parse_mode":"HTML","disable_web_page_preview":True},timeout=15)
            if r.status_code != 200:
                logger.error(f"TG part {i+1} failed: {r.status_code}"); success = False
            else:
                logger.info(f"✅ Sent part {i+1}/{len(messages)}")
            time.sleep(1.5)
        except Exception as e:
            logger.error(f"TG error part {i+1}: {e}"); success = False
    return success


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def run():
    now = datetime.now(IST)
    logger.info(f"🏏 Dream11 IPL Generator — {now.strftime('%Y-%m-%d %H:%M IST')}")
    matches = get_today_match()
    if not matches:
        logger.info("No IPL match today. Skipping."); return

    for match in matches:
        team1=match["team1"]; team2=match["team2"]; venue=match["venue"]; match_time=match["time"]
        logger.info(f"Match: {team1} vs {team2} at {venue}")

        xi1, xi2, xi_source = resolve_playing_xi(team1, team2)
        logger.info(f"XI source: {xi_source} | {team1}: {len(xi1)} | {team2}: {len(xi2)}")
        logger.info(f"  {team1} XI: {[p['name'] for p in xi1]}")
        logger.info(f"  {team2} XI: {[p['name'] for p in xi2]}")

        data = generate_5_teams_ai(team1, team2, venue, match_time, xi1, xi2, xi_source)
        if not data or not data.get("teams"):
            logger.warning("AI failed — using rule-based fallback")
            data = build_fallback_teams(team1, team2, venue, xi1, xi2, xi_source)

        messages = format_telegram_message(data, team1, team2, xi_source)
        ok = send_to_free_channel(messages)
        logger.info(f"{'✅ Sent' if ok else '❌ Failed'} for {team1} vs {team2} | source: {xi_source}")

        if len(matches) > 1:
            time.sleep(30)


if __name__ == "__main__":
    run()
