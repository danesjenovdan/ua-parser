#!/bin/bash
echo "parse people"
scrapy crawl people
echo "parse speeches"
scrapy crawl speeches
echo "parse votes"
python vote_parser.py
cd /app
echo "set session to votes"
python manage.py set_session_to_votes_ua
echo "lematize speeches"
python manage.py lemmatize_speeches
echo "set tfidf"
python manage.py set_tfidf_for_sessions
echo "start setting motion tags"
python manage.py set_motion_tags
echo "send notifications"
python manage.py send_daily_notifications
