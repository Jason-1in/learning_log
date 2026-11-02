from django.shortcuts import render, redirect 
from django.contrib.auth.decorators import login_required
from django.http import Http404

from .models import Topic, Entry
from .forms import TopicForm, EntryForm

# Create your views here. - eesentially appearances for webpages 

def index(request):
    """The home page for Learning Log."""
    return render (request, 'learning_logs/index.html')


def check_topic_owner(request, topic):
    return topic.owner == request.user
    
@login_required
def topics(request):
    """Show all Topics"""
    topics = Topic.objects.filter(owner=request.user).order_by ('date_added')
    context = {'topics': topics}
    return render (request, 'learning_logs/topics.html', context) #context is a dictionary in which the keys are the names

@login_required
def topic(request, topic_id):
    """Show a single topic and all its entries."""
    topic = Topic.objects.get(id=topic_id)
    if check_topic_owner(request, topic):
        entries = topic.entry_set.order_by('-date_added') #- sign means reverse order
        context = {'topic': topic, 'entries': entries}
        return render (request, 'learning_logs/topic.html', context)
    #Make sure the topic belongs to the current user
    else:
        raise Http404

@login_required
def new_topic(request):
    """Add a new topic"""
    if request.method != "POST":
        #no data submitted; create a blank form.
        form = TopicForm()
    else:
        #POST data submitted; porocess data
        form = TopicForm (data = request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect ('learning_logs:topics') #send the user bnack to topics page after submission of a topic
    #Display a blank or invalid form
    context = {'form': form}
    return render (request, 'learning_logs/new_topic.html', context)

@login_required
def new_entry (request, topic_id): 
    """Add a new entry for a particular topic"""
    topic = Topic.objects.get(id=topic_id)
    if request.method != 'POST':
         #No data submitted; create a blank form
         form = EntryForm()
    else: 
         #POST data submitted; process data
        form = EntryForm (data = request.POST)
        if form.is_valid():
            if check_topic_owner(request, topic):
                new_entry = form.save(commit=False)
                new_entry.topic = topic
                new_entry.save()
                return redirect ('learning_logs:topic', topic_id = topic_id)
            else:
                #Add error page here saving you do not own this topic later
                raise Http404
    #Display a blank or invalid form 
    context= {'topic':topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)

@login_required
def edit_entry(request, entry_id):
    """Edit an existing entry"""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    if check_topic_owner(request, topic):
        if request.method != 'POST':
                #Inital request; prefill form with current entry
                form = EntryForm (instance = entry)
        else:
            #POST data submitted; process data
            form = EntryForm (instance=entry, data = request.POST)
            if form.is_valid():
                form.save()
                return redirect ('learning_logs:topic', topic_id=topic.id)
        context = {'entry':entry, 'topic':topic, 'form':form}
        return render (request, 'learning_logs/edit_entry.html',context)
    else:
        raise Http404