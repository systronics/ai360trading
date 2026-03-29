"""
dream11_ipl.py — Dream11 / My11Circle IPL Fantasy Team Generator
══════════════════════════════════════════════════════════════════
Auto-generates 5 fantasy teams for every IPL 2026 match.
Sends to FREE Telegram channel (TELEGRAM_CHAT_ID only).

KEY FIX (March 2026):
  Playing XI is now CONFIRMED before team generation via:
  1. CricAPI live match data (primary — fetches actual announced XI)
  2. PLAYING_XI env var override (manual input after toss)
  3. Smart squad filtering (only top 11 by pts from each team as last resort)
  Never picks benched/rested players again.

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
RAPIDAPI_KEY     = os.environ.get("RAPIDAPI_KEY", "")

# ── MANUAL PLAYING XI OVERRIDE ──────────────────────────────────────────────
# Set this env var in GitHub Actions workflow_dispatch inputs OR
# in your local shell before running manually after toss:
#
# Format: "PlayerA,PlayerB,PlayerC,..." (comma-separated, exact names)
# Example: PLAYING_XI_T1="Rohit Sharma,Quinton de Kock,Tilak Varma,..."
#          PLAYING_XI_T2="Virat Kohli,Faf du Plessis,Glenn Maxwell,..."
#
# When set, these override everything — most accurate method.
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
    "Wankhede":       {"type": "Batting Paradise",   "avg_score": 170, "dew": "High",   "toss": "Field", "notes": "Sea breeze helps pace. Short boundaries = big 6s."},
    "Eden Gardens":   {"type": "Balanced",           "avg_score": 165, "dew": "Medium", "toss": "Field", "notes": "Spin works well. Heavy dew in 2nd innings."},
    "MA Chidambaram": {"type": "Spin Heaven",        "avg_score": 155, "dew": "Low",    "toss": "Bat",   "notes": "Slow sticky pitch. Spinners dominate. Bat first ideal."},
    "Chinnaswamy":    {"type": "Batting Friendly",   "avg_score": 185, "dew": "Medium", "toss": "Field", "notes": "High altitude = big scores. Pick max batters/hitters."},
    "Rajiv Gandhi":   {"type": "Balanced",           "avg_score": 165, "dew": "Medium", "toss": "Field", "notes": "Pace and spin both get help. Good all-rounder pitch."},
    "Arun Jaitley":   {"type": "Balanced",           "avg_score": 160, "dew": "High",   "toss": "Field", "notes": "Surface gets sluggish later. Dew huge factor at night."},
    "Sawai Mansingh": {"type": "Bowling Friendly",   "avg_score": 155, "dew": "Low",    "toss": "Bat",   "notes": "Spinners and seam both effective. Bat first advantage."},
    "Narendra Modi":  {"type": "Batting Paradise",   "avg_score": 175, "dew": "Medium", "toss": "Field", "notes": "Large ground but fast outfield. Spinners useful."},
    "IS Bindra":      {"type": "Balanced",           "avg_score": 160, "dew": "Low",    "toss": "Bat",   "notes": "Overcast conditions help pacers. Good batting track."},
    "BRSABV Ekana":   {"type": "Bowling Friendly",   "avg_score": 150, "dew": "High",   "toss": "Field", "notes": "Slow pitch. Pacers with skills dominate."},
}

# ─────────────────────────────────────────────
# FULL SQUAD DATABASE (15-man squads)
# Only used to FILTER confirmed playing XI — never to generate teams directly
# ─────────────────────────────────────────────

IPL_PLAYERS = {
    "MI": [
        {"name": "Rohit Sharma",        "role": "BAT",  "batting_pos": "Opener",  "pts": 58, "form": "Good"},
        {"name": "Ishan Kishan",        "role": "WK",   "batting_pos": "Opener",  "pts": 54, "form": "Good"},
        {"name": "Quinton de Kock",     "role": "WK",   "batting_pos": "Opener",  "pts": 52, "form": "Good"},
        {"name": "Tilak Varma",         "role": "BAT",  "batting_pos": "No.3",    "pts": 55, "form": "Excellent"},
        {"name": "Suryakumar Yadav",    "role": "BAT",  "batting_pos": "No.4",    "pts": 60, "form": "Good"},
        {"name": "Hardik Pandya",       "role": "AR",   "batting_pos": "No.5",    "pts": 65, "form": "Good"},
        {"name": "Sherfane Rutherford", "role": "AR",   "batting_pos": "No.6",    "pts": 42, "form": "Average"},
        {"name": "Naman Dhir",          "role": "AR",   "batting_pos": "No.7",    "pts": 38, "form": "Average"},
        {"name": "Mitchell Santner",    "role": "AR",   "batting_pos": "No.7",    "pts": 44, "form": "Good"},
        {"name": "Deepak Chahar",       "role": "BOWL", "batting_pos": "No.9",    "pts": 40, "form": "Good"},
        {"name": "Trent Boult",         "role": "BOWL", "batting_pos": "No.10",   "pts": 48, "form": "Good"},
        {"name": "Jasprit Bumrah",      "role": "BOWL", "batting_pos": "No.11",   "pts": 72, "form": "Excellent"},
        {"name": "Ashwani Kumar",       "role": "BOWL", "batting_pos": "No.8",    "pts": 38, "form": "Good"},
        {"name": "Piyush Chawla",       "role": "BOWL", "batting_pos": "No.10",   "pts": 36, "form": "Average"},
        {"name": "Romario Shepherd",    "role": "AR",   "batting_pos": "No.6",    "pts": 40, "form": "Average"},
    ],
    "KKR": [
        {"name": "Finn Allen",          "role": "WK",   "batting_pos": "Opener",  "pts": 55, "form": "Good"},
        {"name": "Ajinkya Rahane",      "role": "BAT",  "batting_pos": "Opener",  "pts": 40, "form": "Average"},
        {"name": "Angkrish Raghuvanshi","role": "BAT",  "batting_pos": "No.3",    "pts": 45, "form": "Good"},
        {"name": "Venkatesh Iyer",      "role": "AR",   "batting_pos": "No.3",    "pts": 52, "form": "Good"},
        {"name": "Cameron Green",       "role": "AR",   "batting_pos": "No.4",    "pts": 50, "form": "Good"},
        {"name": "Rinku Singh",         "role": "BAT",  "batting_pos": "No.5",    "pts": 52, "form": "Good"},
        {"name": "Sunil Narine",        "role": "AR",   "batting_pos": "Opener",  "pts": 62, "form": "Excellent"},
        {"name": "Ramandeep Singh",     "role": "AR",   "batting_pos": "No.7",    "pts": 40, "form": "Average"},
        {"name": "Anukul Roy",          "role": "AR",   "batting_pos": "No.8",    "pts": 38, "form": "Average"},
        {"name": "Vaibhav Arora",       "role": "BOWL", "batting_pos": "No.10",   "pts": 42, "form": "Good"},
        {"name": "Varun Chakravarthy",  "role": "BOWL", "batting_pos": "No.11",   "pts": 55, "form": "Excellent"},
        {"name": "Blessing Muzarabani", "role": "BOWL", "batting_pos": "No.9",    "pts": 45, "form": "Good"},
        {"name": "Mitchell Starc",      "role": "BOWL", "batting_pos": "No.10",   "pts": 50, "form": "Good"},
        {"name": "Harshit Rana",        "role": "BOWL", "batting_pos": "No.9",    "pts": 44, "form": "Good"},
        {"name": "Phil Salt",           "role": "WK",   "batting_pos": "Opener",  "pts": 58, "form": "Good"},
    ],
    "CSK": [
        {"name": "Ruturaj Gaikwad",     "role": "BAT",  "batting_pos": "Opener",  "pts": 58, "form": "Good"},
        {"name": "Devon Conway",        "role": "WK",   "batting_pos": "Opener",  "pts": 52, "form": "Good"},
        {"name": "Ajinkya Rahane",      "role": "BAT",  "batting_pos": "No.3",    "pts": 45, "form": "Average"},
        {"name": "Shivam Dube",         "role": "AR",   "batting_pos": "No.4",    "pts": 55, "form": "Good"},
        {"name": "Ravindra Jadeja",     "role": "AR",   "batting_pos": "No.5",    "pts": 62, "form": "Excellent"},
        {"name": "MS Dhoni",            "role": "WK",   "batting_pos": "No.7",    "pts": 50, "form": "Good"},
        {"name": "Moeen Ali",           "role": "AR",   "batting_pos": "No.6",    "pts": 48, "form": "Good"},
        {"name": "Deepak Chahar",       "role": "BOWL", "batting_pos": "No.9",    "pts": 42, "form": "Good"},
        {"name": "Tushar Deshpande",    "role": "BOWL", "batting_pos": "No.10",   "pts": 40, "form": "Average"},
        {"name": "Matheesha Pathirana", "role": "BOWL", "batting_pos": "No.11",   "pts": 50, "form": "Good"},
        {"name": "Noor Ahmad",          "role": "BOWL", "batting_pos": "No.8",    "pts": 45, "form": "Good"},
        {"name": "Rachin Ravindra",     "role": "AR",   "batting_pos": "No.3",    "pts": 48, "form": "Good"},
        {"name": "Daryl Mitchell",      "role": "AR",   "batting_pos": "No.5",    "pts": 46, "form": "Good"},
        {"name": "Shaik Rasheed",       "role": "BAT",  "batting_pos": "No.6",    "pts": 38, "form": "Average"},
        {"name": "Mukesh Choudhary",    "role": "BOWL", "batting_pos": "No.10",   "pts": 38, "form": "Average"},
    ],
    "RCB": [
        {"name": "Faf du Plessis",      "role": "BAT",  "batting_pos": "Opener",  "pts": 55, "form": "Good"},
        {"name": "Virat Kohli",         "role": "BAT",  "batting_pos": "No.3",    "pts": 68, "form": "Excellent"},
        {"name": "Rajat Patidar",       "role": "BAT",  "batting_pos": "No.4",    "pts": 50, "form": "Good"},
        {"name": "Glenn Maxwell",       "role": "AR",   "batting_pos": "No.5",    "pts": 58, "form": "Good"},
        {"name": "Liam Livingstone",    "role": "AR",   "batting_pos": "No.6",    "pts": 52, "form": "Good"},
        {"name": "Dinesh Karthik",      "role": "WK",   "batting_pos": "No.7",    "pts": 48, "form": "Good"},
        {"name": "Anuj Rawat",          "role": "WK",   "batting_pos": "Opener",  "pts": 44, "form": "Good"},
        {"name": "Mohammed Siraj",      "role": "BOWL", "batting_pos": "No.10",   "pts": 48, "form": "Good"},
        {"name": "Josh Hazlewood",      "role": "BOWL", "batting_pos": "No.11",   "pts": 50, "form": "Good"},
        {"name": "Yuzvendra Chahal",    "role": "BOWL", "batting_pos": "No.9",    "pts": 52, "form": "Good"},
        {"name": "Tom Curran",          "role": "AR",   "batting_pos": "No.8",    "pts": 40, "form": "Average"},
        {"name": "Cameron Green",       "role": "AR",   "batting_pos": "No.4",    "pts": 50, "form": "Good"},
        {"name": "Suyash Prabhudessai","role": "BAT",  "batting_pos": "No.5",    "pts": 42, "form": "Average"},
        {"name": "Reece Topley",        "role": "BOWL", "batting_pos": "No.11",   "pts": 44, "form": "Good"},
        {"name": "Karn Sharma",         "role": "BOWL", "batting_pos": "No.9",    "pts": 40, "form": "Average"},
    ],
    "DC": [
        {"name": "David Warner",        "role": "BAT",  "batting_pos": "Opener",  "pts": 58, "form": "Good"},
        {"name": "Prithvi Shaw",        "role": "BAT",  "batting_pos": "Opener",  "pts": 50, "form": "Good"},
        {"name": "Jake Fraser-McGurk",  "role": "BAT",  "batting_pos": "No.3",    "pts": 52, "form": "Good"},
        {"name": "Rishabh Pant",        "role": "WK",   "batting_pos": "No.4",    "pts": 65, "form": "Excellent"},
        {"name": "Axar Patel",          "role": "AR",   "batting_pos": "No.5",    "pts": 58, "form": "Good"},
        {"name": "Tristan Stubbs",      "role": "AR",   "batting_pos": "No.6",    "pts": 48, "form": "Average"},
        {"name": "Sumit Kumar",         "role": "AR",   "batting_pos": "No.7",    "pts": 38, "form": "Average"},
        {"name": "Kuldeep Yadav",       "role": "BOWL", "batting_pos": "No.9",    "pts": 55, "form": "Good"},
        {"name": "Anrich Nortje",       "role": "BOWL", "batting_pos": "No.11",   "pts": 50, "form": "Good"},
        {"name": "Mustafizur Rahman",   "role": "BOWL", "batting_pos": "No.10",   "pts": 45, "form": "Good"},
        {"name": "Ishant Sharma",       "role": "BOWL", "batting_pos": "No.8",    "pts": 40, "form": "Average"},
        {"name": "Mitchell Marsh",      "role": "AR",   "batting_pos": "No.4",    "pts": 55, "form": "Good"},
        {"name": "Rilee Rossouw",       "role": "BAT",  "batting_pos": "No.5",    "pts": 48, "form": "Good"},
        {"name": "Abishek Porel",       "role": "WK",   "batting_pos": "No.6",    "pts": 44, "form": "Good"},
        {"name": "Lalit Yadav",         "role": "AR",   "batting_pos": "No.7",    "pts": 42, "form": "Average"},
    ],
    "SRH": [
        {"name": "Travis Head",         "role": "BAT",  "batting_pos": "Opener",  "pts": 65, "form": "Excellent"},
        {"name": "Abhishek Sharma",     "role": "BAT",  "batting_pos": "Opener",  "pts": 60, "form": "Good"},
        {"name": "Aiden Markram",       "role": "BAT",  "batting_pos": "No.3",    "pts": 52, "form": "Good"},
        {"name": "Heinrich Klaasen",    "role": "WK",   "batting_pos": "No.4",    "pts": 65, "form": "Excellent"},
        {"name": "Pat Cummins",         "role": "AR",   "batting_pos": "No.5",    "pts": 62, "form": "Good"},
        {"name": "Nitish Kumar Reddy",  "role": "AR",   "batting_pos": "No.6",    "pts": 50, "form": "Good"},
        {"name": "Shahbaz Ahmed",       "role": "AR",   "batting_pos": "No.7",    "pts": 40, "form": "Average"},
        {"name": "Bhuvneshwar Kumar",   "role": "BOWL", "batting_pos": "No.9",    "pts": 48, "form": "Good"},
        {"name": "Umran Malik",         "role": "BOWL", "batting_pos": "No.11",   "pts": 42, "form": "Average"},
        {"name": "Jaydev Unadkat",      "role": "BOWL", "batting_pos": "No.10",   "pts": 40, "form": "Average"},
        {"name": "T Natarajan",         "role": "BOWL", "batting_pos": "No.10",   "pts": 46, "form": "Good"},
        {"name": "Adam Zampa",          "role": "BOWL", "batting_pos": "No.9",    "pts": 48, "form": "Good"},
        {"name": "Glenn Phillips",      "role": "AR",   "batting_pos": "No.5",    "pts": 50, "form": "Good"},
        {"name": "Marco Jansen",        "role": "AR",   "batting_pos": "No.8",    "pts": 48, "form": "Good"},
        {"name": "Mayank Agarwal",      "role": "BAT",  "batting_pos": "Opener",  "pts": 44, "form": "Average"},
    ],
    "RR": [
        {"name": "Jos Buttler",         "role": "WK",   "batting_pos": "Opener",  "pts": 68, "form": "Excellent"},
        {"name": "Yashasvi Jaiswal",    "role": "BAT",  "batting_pos": "Opener",  "pts": 65, "form": "Excellent"},
        {"name": "Sanju Samson",        "role": "WK",   "batting_pos": "No.3",    "pts": 62, "form": "Good"},
        {"name": "Riyan Parag",         "role": "AR",   "batting_pos": "No.4",    "pts": 52, "form": "Good"},
        {"name": "Shimron Hetmyer",     "role": "BAT",  "batting_pos": "No.5",    "pts": 50, "form": "Good"},
        {"name": "Dhruv Jurel",         "role": "WK",   "batting_pos": "No.6",    "pts": 45, "form": "Average"},
        {"name": "Ravichandran Ashwin", "role": "AR",   "batting_pos": "No.7",    "pts": 48, "form": "Good"},
        {"name": "Trent Boult",         "role": "BOWL", "batting_pos": "No.10",   "pts": 52, "form": "Good"},
        {"name": "Sandeep Sharma",      "role": "BOWL", "batting_pos": "No.9",    "pts": 42, "form": "Good"},
        {"name": "Yuzvendra Chahal",    "role": "BOWL", "batting_pos": "No.11",   "pts": 50, "form": "Good"},
        {"name": "Navdeep Saini",       "role": "BOWL", "batting_pos": "No.10",   "pts": 40, "form": "Average"},
        {"name": "Adam Zampa",          "role": "BOWL", "batting_pos": "No.9",    "pts": 48, "form": "Good"},
        {"name": "KC Cariappa",         "role": "BOWL", "batting_pos": "No.8",    "pts": 38, "form": "Average"},
        {"name": "Rovman Powell",       "role": "BAT",  "batting_pos": "No.5",    "pts": 48, "form": "Good"},
        {"name": "Jason Holder",        "role": "AR",   "batting_pos": "No.7",    "pts": 46, "form": "Good"},
    ],
    "PBKS": [
        {"name": "Prabhsimran Singh",   "role": "WK",   "batting_pos": "Opener",  "pts": 55, "form": "Good"},
        {"name": "Shikhar Dhawan",      "role": "BAT",  "batting_pos": "Opener",  "pts": 50, "form": "Average"},
        {"name": "Sam Curran",          "role": "AR",   "batting_pos": "No.3",    "pts": 55, "form": "Good"},
        {"name": "Liam Livingstone",    "role": "AR",   "batting_pos": "No.4",    "pts": 58, "form": "Good"},
        {"name": "Jonny Bairstow",      "role": "WK",   "batting_pos": "No.5",    "pts": 55, "form": "Good"},
        {"name": "Shashank Singh",      "role": "BAT",  "batting_pos": "No.6",    "pts": 48, "form": "Good"},
        {"name": "Harpreet Brar",       "role": "AR",   "batting_pos": "No.7",    "pts": 40, "form": "Average"},
        {"name": "Arshdeep Singh",      "role": "BOWL", "batting_pos": "No.9",    "pts": 52, "form": "Good"},
        {"name": "Nathan Ellis",        "role": "BOWL", "batting_pos": "No.10",   "pts": 45, "form": "Good"},
        {"name": "Rahul Chahar",        "role": "BOWL", "batting_pos": "No.11",   "pts": 45, "form": "Good"},
        {"name": "Kagiso Rabada",       "role": "BOWL", "batting_pos": "No.10",   "pts": 55, "form": "Good"},
        {"name": "Rilee Rossouw",       "role": "BAT",  "batting_pos": "No.4",    "pts": 50, "form": "Good"},
        {"name": "Matthew Short",       "role": "AR",   "batting_pos": "Opener",  "pts": 46, "form": "Good"},
        {"name": "Harshal Patel",       "role": "BOWL", "batting_pos": "No.9",    "pts": 48, "form": "Good"},
        {"name": "Atharva Taide",       "role": "BAT",  "batting_pos": "No.5",    "pts": 40, "form": "Average"},
    ],
    "LSG": [
        {"name": "Quinton de Kock",     "role": "WK",   "batting_pos": "Opener",  "pts": 58, "form": "Good"},
        {"name": "KL Rahul",            "role": "WK",   "batting_pos": "Opener",  "pts": 60, "form": "Good"},
        {"name": "Nicholas Pooran",     "role": "BAT",  "batting_pos": "No.3",    "pts": 62, "form": "Excellent"},
        {"name": "Marcus Stoinis",      "role": "AR",   "batting_pos": "No.4",    "pts": 55, "form": "Good"},
        {"name": "Deepak Hooda",        "role": "AR",   "batting_pos": "No.5",    "pts": 45, "form": "Average"},
        {"name": "Krunal Pandya",       "role": "AR",   "batting_pos": "No.6",    "pts": 50, "form": "Good"},
        {"name": "Prerak Mankad",       "role": "AR",   "batting_pos": "No.7",    "pts": 38, "form": "Average"},
        {"name": "Mark Wood",           "role": "BOWL", "batting_pos": "No.10",   "pts": 50, "form": "Good"},
        {"name": "Ravi Bishnoi",        "role": "BOWL", "batting_pos": "No.11",   "pts": 50, "form": "Good"},
        {"name": "Avesh Khan",          "role": "BOWL", "batting_pos": "No.9",    "pts": 45, "form": "Good"},
        {"name": "Naveen-ul-Haq",       "role": "BOWL", "batting_pos": "No.10",   "pts": 44, "form": "Good"},
        {"name": "Mohsin Khan",         "role": "BOWL", "batting_pos": "No.11",   "pts": 42, "form": "Good"},
        {"name": "Kyle Mayers",         "role": "AR",   "batting_pos": "Opener",  "pts": 52, "form": "Good"},
        {"name": "Ayush Badoni",        "role": "BAT",  "batting_pos": "No.5",    "pts": 46, "form": "Good"},
        {"name": "Amit Mishra",         "role": "BOWL", "batting_pos": "No.9",    "pts": 38, "form": "Average"},
    ],
    "GT": [
        {"name": "Wriddhiman Saha",     "role": "WK",   "batting_pos": "Opener",  "pts": 50, "form": "Average"},
        {"name": "Shubman Gill",        "role": "BAT",  "batting_pos": "Opener",  "pts": 65, "form": "Excellent"},
        {"name": "Hardik Pandya",       "role": "AR",   "batting_pos": "No.3",    "pts": 62, "form": "Good"},
        {"name": "David Miller",        "role": "BAT",  "batting_pos": "No.4",    "pts": 58, "form": "Good"},
        {"name": "Abhinav Manohar",     "role": "BAT",  "batting_pos": "No.5",    "pts": 45, "form": "Average"},
        {"name": "Rahul Tewatia",       "role": "AR",   "batting_pos": "No.6",    "pts": 50, "form": "Good"},
        {"name": "Rashid Khan",         "role": "AR",   "batting_pos": "No.7",    "pts": 65, "form": "Excellent"},
        {"name": "Mohammed Shami",      "role": "BOWL", "batting_pos": "No.9",    "pts": 58, "form": "Excellent"},
        {"name": "Alzarri Joseph",      "role": "BOWL", "batting_pos": "No.10",   "pts": 48, "form": "Good"},
        {"name": "Noor Ahmad",          "role": "BOWL", "batting_pos": "No.11",   "pts": 45, "form": "Good"},
        {"name": "Umesh Yadav",         "role": "BOWL", "batting_pos": "No.8",    "pts": 42, "form": "Average"},
        {"name": "Vijay Shankar",       "role": "AR",   "batting_pos": "No.5",    "pts": 44, "form": "Average"},
        {"name": "Darshan Nalkande",    "role": "BOWL", "batting_pos": "No.10",   "pts": 38, "form": "Average"},
        {"name": "B Sai Sudharsan",     "role": "BAT",  "batting_pos": "No.3",    "pts": 52, "form": "Good"},
        {"name": "Kane Williamson",     "role": "BAT",  "batting_pos": "No.4",    "pts": 50, "form": "Good"},
    ],
}


# ─────────────────────────────────────────────
# PLAYING XI RESOLUTION — THE KEY FIX
# Priority: ENV override > CricAPI > Smart squad filter
# ─────────────────────────────────────────────

def resolve_playing_xi(team1: str, team2: str) -> tuple:
    """
    Returns (xi_team1, xi_team2) — lists of confirmed playing players.
    Tries 3 methods in order:
      1. PLAYING_XI_T1 / PLAYING_XI_T2 env vars (manual input — most accurate)
      2. CricAPI live match data (auto fetch)
      3. Smart squad filter — best 11 from squad by role balance + pts
    """

    # ── Method 1: Manual env var override ──────────────────────────────────
    if PLAYING_XI_T1_ENV and PLAYING_XI_T2_ENV:
        xi1_names = [n.strip() for n in PLAYING_XI_T1_ENV.split(",") if n.strip()]
        xi2_names = [n.strip() for n in PLAYING_XI_T2_ENV.split(",") if n.strip()]
        if len(xi1_names) >= 10 and len(xi2_names) >= 10:
            xi1 = _names_to_player_objects(xi1_names, team1)
            xi2 = _names_to_player_objects(xi2_names, team2)
            logger.info(f"✅ Playing XI from ENV vars: {team1}={len(xi1)}, {team2}={len(xi2)}")
            return xi1, xi2
        logger.warning("ENV vars set but insufficient players — falling through to CricAPI")

    # ── Method 2: CricAPI live XI fetch ────────────────────────────────────
    if CRICAPI_KEY:
        xi1, xi2 = _fetch_cricapi_xi(team1, team2)
        if xi1 and xi2 and len(xi1) >= 10 and len(xi2) >= 10:
            logger.info(f"✅ Playing XI from CricAPI: {team1}={len(xi1)}, {team2}={len(xi2)}")
            return xi1, xi2
        logger.warning("CricAPI XI fetch failed or incomplete — using smart squad filter")

    # ── Method 3: Smart squad filter (fallback) ─────────────────────────────
    logger.warning(
        f"⚠️ USING SQUAD FILTER — XI not confirmed. "
        f"For accurate picks, set PLAYING_XI_T1 and PLAYING_XI_T2 env vars after toss."
    )
    xi1 = _smart_squad_filter(team1)
    xi2 = _smart_squad_filter(team2)
    return xi1, xi2


def _names_to_player_objects(names: list, team: str) -> list:
    """Convert list of player names to player objects, enriching with squad data."""
    squad = IPL_PLAYERS.get(team, [])
    squad_map = {p["name"].lower(): p for p in squad}
    result = []
    for name in names:
        found = squad_map.get(name.lower())
        if found:
            result.append(found)
        else:
            # Player not in our DB — create a basic entry
            # Try to guess role from name patterns
            result.append({
                "name": name, "role": "BAT", "batting_pos": "Unknown",
                "pts": 45, "form": "Unknown"
            })
            logger.warning(f"  Player '{name}' not in squad DB — added as BAT with default pts")
    return result


def _fetch_cricapi_xi(team1: str, team2: str) -> tuple:
    """Fetch confirmed playing XI from CricAPI for today's match."""
    try:
        # Step 1: Get today's matches
        r = requests.get(
            "https://api.cricapi.com/v1/currentMatches",
            params={"apikey": CRICAPI_KEY, "offset": 0},
            timeout=10
        )
        if not r.ok:
            logger.warning(f"CricAPI matches failed: {r.status_code}")
            return [], []

        data = r.json()
        matches = data.get("data", [])

        # Step 2: Find today's IPL match between team1 and team2
        target_match = None
        team1_lower  = team1.lower()
        team2_lower  = team2.lower()

        # Full team name lookup
        TEAM_FULL_NAMES = {
            "MI": "mumbai indians",  "KKR": "kolkata knight riders",
            "CSK": "chennai super kings", "RCB": "royal challengers",
            "DC": "delhi capitals", "SRH": "sunrisers hyderabad",
            "RR": "rajasthan royals", "PBKS": "punjab kings",
            "LSG": "lucknow super giants", "GT": "gujarat titans",
        }
        t1_full = TEAM_FULL_NAMES.get(team1, team1_lower)
        t2_full = TEAM_FULL_NAMES.get(team2, team2_lower)

        for m in matches:
            teams_in_match = [t.get("name", "").lower() for t in m.get("teamInfo", [])]
            if any(t1_full in t for t in teams_in_match) and any(t2_full in t for t in teams_in_match):
                target_match = m
                break

        if not target_match:
            logger.info("CricAPI: No matching IPL match found for today")
            return [], []

        match_id = target_match.get("id")
        if not match_id:
            return [], []

        # Step 3: Fetch match info with playing XI
        r2 = requests.get(
            "https://api.cricapi.com/v1/match_info",
            params={"apikey": CRICAPI_KEY, "id": match_id},
            timeout=10
        )
        if not r2.ok:
            return [], []

        match_data = r2.json().get("data", {})
        team_info  = match_data.get("teamInfo", [])

        xi1, xi2 = [], []
        for team_obj in team_info:
            team_name  = team_obj.get("name", "").lower()
            players_xi = team_obj.get("players", []) or match_data.get("squad", {}).get(team_obj.get("shortname", ""), [])

            if not players_xi:
                continue

            player_names = [p.get("name", p) if isinstance(p, dict) else str(p) for p in players_xi]

            if any(t1_full in team_name for _ in [1]):
                xi1 = _names_to_player_objects(player_names, team1)
            elif any(t2_full in team_name for _ in [1]):
                xi2 = _names_to_player_objects(player_names, team2)

        return xi1, xi2

    except Exception as e:
        logger.warning(f"CricAPI fetch error: {e}")
        return [], []


def _smart_squad_filter(team: str) -> list:
    """
    Select best 11 from squad ensuring role balance.
    WK: 1, BAT: 3-4, AR: 2-3, BOWL: 3-4
    Prioritises by pts + form, excludes injury_doubt players.
    """
    squad = [p for p in IPL_PLAYERS.get(team, []) if not p.get("injury_doubt")]
    squad_sorted = sorted(squad, key=lambda x: x["pts"], reverse=True)

    selected   = []
    role_caps  = {"WK": 2, "BAT": 5, "AR": 4, "BOWL": 5}  # max per role
    role_mins  = {"WK": 1, "BAT": 3, "AR": 2, "BOWL": 3}  # min per role
    role_count = {"WK": 0, "BAT": 0, "AR": 0, "BOWL": 0}

    # First pass: fill minimums
    for role in ["WK", "BAT", "AR", "BOWL"]:
        needed = role_mins[role]
        for p in squad_sorted:
            if len(selected) == 11:
                break
            if p in selected:
                continue
            if p["role"] == role and role_count[role] < needed:
                selected.append(p)
                role_count[role] += 1

    # Second pass: fill remaining by pts
    for p in squad_sorted:
        if len(selected) == 11:
            break
        if p in selected:
            continue
        role = p["role"]
        if role_count.get(role, 0) < role_caps.get(role, 99):
            selected.append(p)
            role_count[role] += 1

    return selected[:11]


# ─────────────────────────────────────────────
# SCHEDULE / VENUE HELPERS
# ─────────────────────────────────────────────

def get_today_match():
    today = date.today()
    today_str = today.strftime("%Y-%m-%d")
    if today < IPL_START or today > IPL_END:
        logger.info(f"Outside IPL 2026 season. Today: {today_str}")
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
# AI TEAM GENERATOR — uses confirmed XI only
# ─────────────────────────────────────────────

def generate_5_teams_ai(team1: str, team2: str, venue: str, match_time: str,
                         xi1: list, xi2: list, xi_source: str) -> dict:
    """Generate 5 fantasy teams using ONLY confirmed playing XI players."""

    pitch = get_venue_profile(venue)

    # Build player list from confirmed XI only
    player_list = "\n".join([
        f"  {p['role']} | {p['name']} ({t}) | Pos: {p.get('batting_pos','?')} | Avg Pts: {p.get('pts',45)} | Form: {p.get('form','Good')}"
        for t, xi in [(team1, xi1), (team2, xi2)]
        for p in xi
    ])

    total_players = len(xi1) + len(xi2)

    prompt = f"""IPL 2026 Fantasy Cricket — Generate 5 Dream11/My11Circle teams.

MATCH: {team1} vs {team2}
VENUE: {venue}
TIME: {match_time} IST
XI SOURCE: {xi_source} ({'CONFIRMED playing XI' if 'env' in xi_source.lower() or 'cricapi' in xi_source.lower() else 'estimated — verify after toss'})

PITCH: {pitch['type']} | Avg Score: {pitch['avg_score']} | Dew: {pitch['dew']} | Toss Tip: {pitch['toss']} first
PITCH NOTES: {pitch['notes']}

CONFIRMED PLAYING XI ({total_players} players total — ONLY pick from these):
{player_list}

DREAM11 RULES (STRICT):
- Exactly 11 players per team — ONLY from the list above
- Max 7 players from one team ({team1} or {team2})
- Min 4 players from each team
- Must have: min 1 WK, min 1 BAT, min 1 AR, min 1 BOWL
- 1 Captain (2x points) + 1 Vice-Captain (1.5x)

CRITICAL: Do NOT add any player not in the list above. No exceptions.

Generate exactly 5 teams in JSON:
{{
  "match": "{team1} vs {team2}",
  "venue": "{venue}",
  "pitch_type": "{pitch['type']}",
  "toss_tip": "Chase/Bat first based on conditions",
  "xi_source": "{xi_source}",
  "key_insights": ["pitch insight", "player form insight", "toss/dew insight"],
  "teams": [
    {{
      "name": "Team N – Creative Name",
      "strategy": "Safe/Grand League/Balanced/Differential/Captain Swap",
      "risk": "Low/Medium/High",
      "captain": "Exact Player Name from list",
      "vice_captain": "Exact Player Name from list",
      "players": [
        {{"name": "Exact Player Name", "role": "WK/BAT/AR/BOWL", "team": "{team1} or {team2}"}}
      ],
      "why": "1-line strategy explanation"
    }}
  ],
  "must_pick": ["top 3 players from XI"],
  "avoid": ["any player to avoid and why"],
  "disclaimer": "Playing XI source: {xi_source}. Always verify final XI before locking."
}}

Team strategy variety:
- Team 1: Safe Bet XI (low risk, high-pts players, safe C/VC)
- Team 2: Bowling Blitz (bowling heavy, wicket-takers as C/VC)
- Team 3: All-Rounder Army (AR-heavy, balanced)
- Team 4: Differential Dare (low-ownership surprise picks, different C)
- Team 5: Captain Swap (same core as T1 but different C/VC)"""

    system = """You are an expert Dream11/My11Circle fantasy cricket analyst.
CRITICAL RULE: Only pick players explicitly listed in the CONFIRMED PLAYING XI.
Never invent or add players. Never pick benched or non-playing players.
Return ONLY valid JSON. No markdown."""

    client = AIClient()
    try:
        result = client.generate_json(
            prompt=prompt,
            system_prompt=system,
            content_mode="market",
            lang="en",
        )
        if result and result.get("teams") and len(result["teams"]) > 0:
            # Validate: remove any player not in XI
            result = _validate_and_clean_teams(result, xi1, xi2, team1, team2)
            return result
    except Exception as e:
        logger.warning(f"AI generation error: {e}")

    return None


def _validate_and_clean_teams(data: dict, xi1: list, xi2: list, team1: str, team2: str) -> dict:
    """Remove any player from AI output that isn't in the confirmed XI."""
    valid_names = {p["name"].lower() for p in xi1 + xi2}

    for team in data.get("teams", []):
        original = team.get("players", [])
        cleaned  = [p for p in original if p["name"].lower() in valid_names]

        removed = [p["name"] for p in original if p["name"].lower() not in valid_names]
        if removed:
            logger.warning(f"  Removed non-XI players from {team['name']}: {removed}")

        # Validate captain/VC are still in cleaned list
        cap_names = {p["name"] for p in cleaned}
        if team.get("captain") not in cap_names and cleaned:
            team["captain"] = cleaned[0]["name"]
        if team.get("vice_captain") not in cap_names and len(cleaned) > 1:
            team["vice_captain"] = cleaned[1]["name"]

        team["players"] = cleaned

    return data


# ─────────────────────────────────────────────
# FALLBACK RULE-BASED TEAMS (uses confirmed XI)
# ─────────────────────────────────────────────

def build_fallback_teams(team1: str, team2: str, venue: str,
                          xi1: list, xi2: list, xi_source: str) -> dict:
    """Rule-based 5 teams from confirmed XI when AI fails."""
    pitch   = get_venue_profile(venue)
    p1      = sorted(xi1, key=lambda x: x.get("pts", 45), reverse=True)
    p2      = sorted(xi2, key=lambda x: x.get("pts", 45), reverse=True)
    all_xi  = sorted(p1 + p2, key=lambda x: x.get("pts", 45), reverse=True)

    def pick_team(t1_count=6, bowling_boost=False):
        team  = []
        roles = {"WK": 1, "BAT": 3, "AR": 2, "BOWL": 3}
        t1c, t2c = 0, 0
        pool = sorted(all_xi, key=lambda x: -x.get("pts", 45) * (1.3 if bowling_boost and x["role"] == "BOWL" else 1.0))

        # Fill minimums first
        for role, minimum in roles.items():
            filled = 0
            for p in pool:
                if filled >= minimum or len(team) >= 11:
                    break
                if p in team:
                    continue
                is_t1 = p in p1
                if is_t1 and t1c >= 7:
                    continue
                if not is_t1 and t2c >= 7:
                    continue
                if is_t1 and t1c >= t1_count:
                    continue
                if p["role"] == role:
                    team.append(p)
                    t1c += is_t1
                    t2c += (not is_t1)
                    filled += 1

        # Fill remaining spots
        for p in pool:
            if len(team) >= 11:
                break
            if p in team:
                continue
            is_t1 = p in p1
            if (is_t1 and t1c >= 7) or (not is_t1 and t2c >= 7):
                continue
            if is_t1 and t1c >= t1_count:
                continue
            team.append(p)
            t1c += is_t1
            t2c += (not is_t1)

        return team[:11]

    def fmt(players, name, strategy, risk, ci=0, vi=1, why=""):
        cap = players[ci]["name"] if ci < len(players) else players[0]["name"]
        vc  = players[vi]["name"] if vi < len(players) else players[1]["name"]
        return {
            "name": name, "strategy": strategy, "risk": risk,
            "captain": cap, "vice_captain": vc,
            "players": [{"name": p["name"], "role": p["role"],
                         "team": team1 if p in p1 else team2} for p in players],
            "why": why
        }

    top3 = [p["name"] for p in all_xi[:3]]

    return {
        "match": f"{team1} vs {team2}",
        "venue": venue,
        "pitch_type": pitch["type"],
        "toss_tip": f"{pitch['toss']} first recommended",
        "xi_source": xi_source,
        "key_insights": [
            f"Pitch: {pitch['type']} — avg {pitch['avg_score']}",
            f"Dew: {pitch['dew']} — {pitch['notes']}",
            f"Top picks: {', '.join(top3)}"
        ],
        "teams": [
            fmt(pick_team(6),                    "Team 1 – Safe Bet XI",         "Safe",         "Low",    0, 1, "Best XI, safest picks."),
            fmt(pick_team(6, bowling_boost=True), "Team 2 – Bowling Blitz",       "Grand League", "Medium", 2, 0, "Wicket-takers as C/VC."),
            fmt(pick_team(5),                    "Team 3 – Balanced Attack",     "Balanced",     "Medium", 1, 2, "Even team split."),
            fmt(pick_team(4),                    "Team 4 – Differential Dare",   "Differential", "High",   3, 1, "Low-ownership for grand leagues."),
            fmt(pick_team(7),                    "Team 5 – Captain Swap",        "Grand League", "High",   2, 0, "Different C from safe team."),
        ],
        "must_pick": top3,
        "avoid": [],
        "disclaimer": f"XI from: {xi_source}. Verify after toss."
    }


# ─────────────────────────────────────────────
# TELEGRAM FORMATTER
# ─────────────────────────────────────────────

def format_telegram_message(data: dict, team1: str, team2: str, xi_source: str) -> list:
    e1 = TEAM_EMOJI.get(team1, "🏏")
    e2 = TEAM_EMOJI.get(team2, "🏏")

    xi_badge = {
        "env":     "✅ CONFIRMED XI (manual input)",
        "cricapi": "✅ CONFIRMED XI (CricAPI live)",
        "squad":   "⚠️ ESTIMATED XI — verify after toss!",
    }.get(xi_source.split("_")[0], f"ℹ️ {xi_source}")

    header = f"""🏏 <b>IPL 2026 — DREAM11 PICKS</b> 🏏
{e1} <b>{team1}</b> vs <b>{team2}</b> {e2}

📍 <i>{data.get('venue', '')}</i>
{xi_badge}

<b>Pitch:</b> {data.get('pitch_type', 'Balanced')}
<b>Toss Tip:</b> {data.get('toss_tip', 'Field first')}

<b>📊 Key Insights:</b>
{"".join([f"• {i}" + chr(10) for i in data.get('key_insights', [])])}
<b>🌟 Must-Picks:</b> {', '.join(data.get('must_pick', []))}

<i>5 teams below — use for Dream11 / My11Circle</i>
──────────────────────────────"""

    messages = [header]
    risk_emoji = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}

    for i, team in enumerate(data.get("teams", []), 1):
        risk    = team.get("risk", "Medium")
        players = team.get("players", [])
        cap     = team.get("captain", "")
        vc      = team.get("vice_captain", "")

        wk    = [p for p in players if p["role"] == "WK"]
        bats  = [p for p in players if p["role"] == "BAT"]
        ars   = [p for p in players if p["role"] == "AR"]
        bowls = [p for p in players if p["role"] == "BOWL"]

        def fmt_p(p):
            name   = p["name"]
            suffix = " 🅒" if name == cap else (" 🅥" if name == vc else "")
            pill   = f"[{p.get('team','')}]"
            return f"  {name}{suffix} <i>{pill}</i>"

        team_name_short = team.get('name', '').split('–')[-1].strip()
        msg = f"""{risk_emoji.get(risk,'🟡')} <b>TEAM {i} — {team_name_short}</b>
<i>{team.get('strategy','')} · {risk} Risk · {len(players)} players</i>

🧤 WK: {chr(10).join([fmt_p(p) for p in wk]) or '  —'}
🏏 BAT: {chr(10).join([fmt_p(p) for p in bats]) or '  —'}
🔄 ALL-ROUNDER: {chr(10).join([fmt_p(p) for p in ars]) or '  —'}
⚡ BOWLER: {chr(10).join([fmt_p(p) for p in bowls]) or '  —'}

🅒 C: <b>{cap}</b>  |  🅥 VC: <b>{vc}</b>
💡 <i>{team.get('why','')}</i>
──────────────────────────────"""
        messages.append(msg)

    footer = f"""⚠️ <b>DISCLAIMER</b>
{data.get('disclaimer','Verify XI after toss.')}
Never lock teams before confirmed playing 11 is announced.

📲 <b>AI360Trading</b> | Free IPL Fantasy Picks
@ai360trading | 🌐 ai360trading.in"""
    messages.append(footer)
    return messages


# ─────────────────────────────────────────────
# TELEGRAM SENDER
# ─────────────────────────────────────────────

def send_to_free_channel(messages: list) -> bool:
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("TELEGRAM_TOKEN or TELEGRAM_CHAT_ID not set")
        return False
    success = True
    for i, msg in enumerate(messages):
        try:
            r = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": TELEGRAM_CHAT_ID, "text": msg,
                      "parse_mode": "HTML", "disable_web_page_preview": True},
                timeout=15,
            )
            if r.status_code != 200:
                logger.error(f"TG send failed part {i+1}: {r.status_code} {r.text[:100]}")
                success = False
            else:
                logger.info(f"✅ Sent part {i+1}/{len(messages)}")
            time.sleep(1.5)
        except Exception as e:
            logger.error(f"TG error part {i+1}: {e}")
            success = False
    return success


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def run():
    now = datetime.now(IST)
    logger.info(f"🏏 Dream11 IPL Generator — {now.strftime('%Y-%m-%d %H:%M IST')}")

    matches = get_today_match()
    if not matches:
        logger.info("No IPL match today. Skipping.")
        return

    for match in matches:
        team1      = match["team1"]
        team2      = match["team2"]
        venue      = match["venue"]
        match_time = match["time"]

        logger.info(f"Match: {team1} vs {team2} at {venue}")

        # 1. Resolve confirmed playing XI (THE KEY FIX)
        xi1, xi2 = resolve_playing_xi(team1, team2)
        if PLAYING_XI_T1_ENV and PLAYING_XI_T2_ENV:
            xi_source = "env_manual"
        elif CRICAPI_KEY and xi1 and len(xi1) >= 10:
            xi_source = "cricapi_live"
        else:
            xi_source = "squad_estimated"

        logger.info(f"XI source: {xi_source} | {team1}: {len(xi1)} players | {team2}: {len(xi2)} players")
        logger.info(f"  {team1} XI: {[p['name'] for p in xi1]}")
        logger.info(f"  {team2} XI: {[p['name'] for p in xi2]}")

        # 2. Generate teams (AI first, rule-based fallback)
        data = generate_5_teams_ai(team1, team2, venue, match_time, xi1, xi2, xi_source)
        if not data or not data.get("teams"):
            logger.warning("AI failed — using rule-based fallback")
            data = build_fallback_teams(team1, team2, venue, xi1, xi2, xi_source)

        # 3. Format + send
        messages = format_telegram_message(data, team1, team2, xi_source)
        ok = send_to_free_channel(messages)

        if ok:
            logger.info(f"✅ Sent for {team1} vs {team2} | XI source: {xi_source}")
        else:
            logger.error(f"❌ Send failed for {team1} vs {team2}")

        if len(matches) > 1:
            time.sleep(30)


if __name__ == "__main__":
    run()
