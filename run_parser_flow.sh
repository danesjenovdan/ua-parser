#!/bin/bash
echo "parse people"
python people_parser.py
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
echo "run analysis for today"
python manage.py daily_update
echo "update speeches to solr"
python manage.py upload_speeches_to_solr
echo "update votes to solr"
python manage.py upload_votes_to_solr
echo "send notifications"
python manage.py send_daily_notifications
