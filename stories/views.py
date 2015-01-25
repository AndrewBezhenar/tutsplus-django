import datetime

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils.timezone import utc
from django.contrib.auth.decorators import login_required

from stories.models import Story
from stories.forms import StoryForm

def score(story, gravity=1.8, timebase=120):
    points = (story.points - 1) ** 0.8
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    age = int((now - story.created_at).total_seconds()) / 60

    return points / (age + timebase) ** gravity


def top_stories(top=180, consider=1000):
    latest_stories = Story.objects.all().order_by('-created_at')[:consider]
    ranked_stories = sorted([(score(story), story) for story in latest_stories], reverse=True)  # descented order
    return [story for _, story in ranked_stories][:top]


def index(request):
    stories = top_stories(top=30)
    return render(request, 'stories/index.html', {
    	'stories': stories,
    	'user': request.user
    })

@login_required
def story(request):
	if request.method == 'POST':
		form = StoryForm(request.POST)
		if form.is_valid():
			story = form.save(commit=False) # not gonna save to db, create instanse of model class
			story.moderator = request.user
			story.save()
			return HttpResponseRedirect('/')
	else:
		form = StoryForm()
	return render(request, 'story.html', {'form' : form})