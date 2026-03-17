name: Daily Trading Video Bot

on:
  schedule:
    # This runs at 04:00 UTC (9:30 AM IST) every day
    - cron: '0 4 * * *'
  workflow_dispatch: # Allows you to run it manually anytime

jobs:
  build-and-upload:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/checkout@v4
        with:
          python-version: '3.11'

      - name: Install Dependencies
        run: |
          pip install groq pillow edge-tts moviepy google-api-python-client google-auth-oauthlib google-auth-httplib2

      - name: Run Video Generator
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
        run: python generate_videos.py

      - name: Keep Runner Clean
        run: rm -rf output/
