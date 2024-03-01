#!/bin/bash
cd [YOUR_DIRECTORY]
python3 Scraper_Cron.py 1>> Log_Files/ScraperError.log 2>> Log_Files/ScraperError.log&

