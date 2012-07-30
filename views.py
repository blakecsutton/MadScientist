from django.db.models.aggregates import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from forms import IdeaForm, LoginForm
from models import Idea, Tag



def idea_list(request):
    """ This is the main view for the site, which displays the list of ideas and the related tags.
        Later, will want to add the ability to filter by tag, as well as search.
    """
    
    if request.method == 'GET' and 'tag' in request.GET:
        tag_filter = str(request.GET['tag'])
        
        ideas = Idea.objects.filter(tag__name=tag_filter).order_by('-date_created')
        
        # Find the other tags associated with the current idea set
        tags = Tag.objects.filter(idea__tag__name=tag_filter).annotate(num_ideas=Count('idea')).filter(num_ideas__gt=0)
        
    else:
        tag_filter = ""
        
        ideas = Idea.objects.order_by('-date_created')
        tags = Tag.objects.annotate(num_ideas=Count('idea')).filter(num_ideas__gt=0)
        
    # Group by facet and then name, and format for display in the template
    tags = tags.order_by('facet', 'name').values('id', 'name', 'facet__name', 'num_ideas')
       
    context = {'idea_list': ideas,
               'tags': tags,
               'tag_filter': tag_filter }
    
    return render_to_response('madscientist/base.html', 
                              context_instance=RequestContext(request, context))     
    
def idea_detail(request, idea_id):
  """ This is a view which shows the full information on a single idea, specified by primary
      key idea_id. If idea_id does not match an idea in the database, it returns the main page.
  """
  
  try:
    idea = Idea.objects.get(pk=idea_id)
  except Idea.DoesNotExist:
    return idea_list(request)
  
  # Get the number of ideas associated 
  tags = Tag.objects.annotate(num_ideas=Count('idea')).filter(num_ideas__gt=0).filter(idea=idea_id)
  tags = tags.order_by('facet', 'name').values('id', 'name', 'facet__name', 'num_ideas')
  
  context = { 'idea': idea,
              'tags': tags }
  
  return render_to_response('madscientist/detail.html', 
                            context_instance=RequestContext(request, context))
@login_required(login_url="/madscientist/login/")
def add_idea(request):
    """ This is a view to add an idea. Note that this duplicates functionality in the admin pages,
        however this view, unlike the administration site, can have restricted access by user, which
        I will be adding eventually. """
           
    if request.method == 'POST':
        # Bind the post request to the previously defined IdeaForm
        form = IdeaForm(request.POST)
        
        if form.is_valid():
            
            # Since IdeaForm is a ModelForm, we can save to the database directly if the form
            # validated.
            form.save()
            
            # After saving, redirect back to the main page
            return HttpResponseRedirect('/madscientist/')
    
    else:
        # Otherwise, display a blank version of the form
        form = IdeaForm()
        
    context = {'form': form }
    
    return render_to_response('madscientist/add_idea.html',
                              context_instance=RequestContext(request, context))

def logout_user(request):
  """ This is a view which logs out the current user. """
  logout(request)
  return render_to_response('madscientist/success.html',
                            context_instance=RequestContext(request))
    
def login_user(request):
  """ This is a view for logging in a user of the site.
  """
  message = "um, hiii..."
  
  # If the form was submitted
  if request.method == 'POST':
    
    # Bind the POST data to the form, this includes error information
    # if it doesn't validate.
    form = LoginForm(request.POST)
    
    # Valid the form info
    if form.is_valid():
      
      username = form.cleaned_data['username']
      password = form.cleaned_data['password']
      user = authenticate(username=username, password=password)
      
      if user is not None:
        if user.is_active:
          
          # Log in the user so their info is saved in the session.
          login(request, user)
          
          return HttpResponseRedirect('/madscientist/')
        
        else:
          # Disabled account
          message = "Your account has been disabled."
        
      else:
        # Incorrect username/password
        message = "Your username or password is incorrect."
        
  else:
    form = LoginForm()
    
  context = {'form': form,
             'message': message}
  
  return render_to_response('madscientist/login.html',
                             context_instance=RequestContext(request, context)) 
      
      
      
      
      