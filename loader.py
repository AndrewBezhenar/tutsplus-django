
# Setup the Django environment so we can access our models
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hackernews.settings')

import sys
import json

from datetime import datetime
from django.utils.timezone import utc

from django.contrib.auth.models import User
from stories.models import Story

import requests

# This script made possible with the help of the Official Hacker News API by hacker-news.firebaseio.com
# provided by Ronnie Roller (http://ronnieroller.com) 
# was updated for the new Official Hacker News API by Andrew Bezhenar (https://github.com/AndrewBezhenar)

HACKER_NEWS_API_TOP_STORIES_URL = 'https://hacker-news.firebaseio.com/v0/topstories.json'
HACKER_NEWS_API_STORY_URL = 'https://hacker-news.firebaseio.com/v0/item/%d.json'

# The Hacker News API errors out from time to time, this number controls
# how many times the script attempts to retrieve the data from the service.
RETRY_ATTEMPTS = 3

# TODO: change the username to your username
USERNAME='andrew'

def get_data(api_url):
    for i in range(RETRY_ATTEMPTS + 1):
        # Send Get request 
        response = requests.get(api_url)

        # If the service errored, hit it again
        if response.status_code != 200:
            if i <= RETRY_ATTEMPTS:
                print("An error occured while retrieving the data, retrying (%d)..." % i+1)
            continue

        # If everything went ok, try to load the data from json
        try:
            items = json.loads(response.content)
            break
        except ValueError, e:
            if i <= RETRY_ATTEMPTS:
                print("An error occurred while loading the data, retrying (%d)..." % i+1)
            continue
    else:
        sys.exit("Too many errors occurred while attempting to retrieve the data")
    return items

def created_at(unix_time):         
    return datetime.utcfromtimestamp(unix_time).replace(tzinfo=utc)

def main():
    # Get the Top 100 Stories id's as list of int's
    top_stories_ids = get_data(HACKER_NEWS_API_TOP_STORIES_URL)

    # Get & load the json data of the Top 30 Stories by their id's
    for id in top_stories_ids[:30]:
        story = get_data(HACKER_NEWS_API_STORY_URL % id)        
        story_created_at = created_at(story['time'])

        # Add the stories to the database
        moderator = User.objects.get(username=USERNAME)        
        story = Story(
            title=story['title'],
            url=story['url'],
            points=story['score'],
            moderator=moderator,)
        story.save()        
        story.created_at = story_created_at        
        story.save()
        # print 'successfully added a story: "%s"' % story

if __name__ == '__main__':
    main()
