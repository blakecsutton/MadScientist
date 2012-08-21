from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models.aggregates import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from forms import LoginForm, EntryForm, FacetForm, TagForm
from models import Entry, Facet, Tag, EntryGroup
from django.forms.formsets import formset_factory

# import the logging library and get an instance of the logger
import logging
logger = logging.getLogger(__name__)

@login_required(login_url="/madscientist/login")
def home(request):
  
  # Just show the groups view with the most recently updated group as the active group.
  entries = Entry.objects.filter(creator=request.user).order_by('date_created')
  most_recent_group = entries[0].group

  return entry_list(request, most_recent_group.id)

@login_required(login_url="/madscientist/login/")
def entry_list(request, group_id):
    """ This is the main view for the site, which displays the list of ideas and the related tags.
        Later, will want to add the ability to filter by tag, as well as search.
    """
    
    # Reject requests for non-public groups the current user did not create
    group = EntryGroup.objects.get(pk=group_id)
    
    # If user doesn't have permission to see this group, redirect
    if (request.user != group.creator and
        not group.public):
        
        return render_to_response('madscientist/forbidden.html',
                                  context_instance=RequestContext(request)) 
        
    # Get the list of entries for the current user and group
    entries = Entry.objects.filter(creator=request.user, group=group_id)
    
    # Find all of the user's tags for this group.
    tags = Tag.objects.filter(creator=request.user, group=group_id)
    tags = tags.annotate(num_ideas=Count('entry'))
    
    # Fetch a list of empty facets in case we want to display them
    facets = Facet.objects.filter(creator=request.user, group=group_id)
    empty_facets = facets.annotate(num_tags=Count('tag')).filter(num_tags=0).values('name')
    
    # Display options for use in the template
    options = {'active_tags': []}
    
    # Copy the querydict of get data, or None if there's no GET request.
    active_options = request.GET.copy()
    
    # Handle the option to filter the list by a single tag
    if 'tag' in active_options:
        
        # Set display string to identify currently visible tags in the template.
        tag_filter = active_options.getlist('tag', None)
        
        for tag_id in tag_filter:
          if tag_id.isdigit():
            options['active_tags'].append(tag_id)
            
        logger.debug("active_tags list is: {}".format(options['active_tags']))
              
        # If tags were received, actually filter the entry list by tag name
        for tag in options['active_tags']:
          # Successively filter by each active tag.
          entries = entries.filter(tags=tag)
            
    # Handle the option to show empty tags in the sidebar
    show_empty_tags = False
    if 'show_empty_tags' in active_options:
          
      # Pull out the actual value and convert to int.
      value = active_options.get('show_empty_tags')
      if value.isdigit():
        value = int(value)
      else:
        value = 0
      
      if value == 1:
        show_empty_tags = True
  
    # Actually enforce whether or not empty tags are shown     
    options['show_empty_tags'] = show_empty_tags
    if not show_empty_tags:
        nonempty_tags = tags.filter(num_ideas__gt=0) 
        tags = nonempty_tags
        
    entries = entries.order_by('-date_created')
    
    # Handle the option of expanding a particular entry in full
    if request.method == 'GET' and 'expand' in request.GET:
        
        expanded = request.GET.get('expand', None)
        if expanded and expanded.isdigit():
          options['expand_id'] = expanded
        
    # Group by facet and then name, and format for display in the template
    tags = tags.order_by('facet', 'name').values('id', 'name', 'facet__name', 'num_ideas')
       
    # Marks tags as active if they appear in list of active tags (by id)
    for tag in tags:
      tag['active'] = (str(tag['id']) in options['active_tags'])
   
    
    # Todo in future: add an ordering fields to EntryGroups so users can rearrange tabs.
    # Also probably a "pinned" flag to indicate whether or not to currently display it.
    groups = EntryGroup.objects.filter(creator=request.user)
        
    context = {'entry_list': entries,
               'tags': tags,
               'empty_facets': empty_facets,
               'active_options': active_options,
               'options': options,
               'group_list': groups,
               'current_group': group}
    
    return render_to_response('madscientist/base.html',
                              context_instance=RequestContext(request, context))     
  
@login_required(login_url="/madscientist/login/")
def add_entry(request, group_id):
    """ This is a view to add an idea to a specific group. """
    
    # Reject requests for non-public groups the current user did not create
    group = EntryGroup.objects.get(pk=group_id)
 
    # If user doesn't have permission to see this group, redirect
    if request.user != group.creator:
          return render_to_response('madscientist/forbidden.html',
                              context_instance=RequestContext(request)) 
    
    # Get tags for the current group and user to show them as options for the entry.
    tags = Tag.objects.filter(creator=request.user, group=group_id)
    tags = tags.order_by('facet', 'name').values('id', 'name', 'facet__name', 'facet__id')
    
    # Fetch a list of empty facets in case we want to display them
    facets = Facet.objects.filter(creator=request.user, group=group_id)
    empty_facets = facets.annotate(num_tags=Count('tag')).filter(num_tags=0).values('id', 'name')
    
    groups = EntryGroup.objects.filter(creator=request.user)

    if request.method == 'POST':
      
      submit_new_entry = request.POST.get('submit_new_entry', False)
      submit_new_facet = request.POST.get('submit_new_facet', False)
      submit_new_tag = request.POST.get('submit_new_tag', False)
      
      if submit_new_tag:
        # Use the value attribute to figure out which text field to check
        tag_facet_id = submit_new_tag.split('-')[2]
        #tag_input_name = submit_new_tag
        tag_name = request.POST.get(submit_new_tag, "")
        
        logger.debug("Submit_new_tag is: {}".format(submit_new_tag))
        logger.debug("Pulling {} out of the POST gives you {}".format(submit_new_tag, tag_name))
        
        # Doing own validation here
        if len(tag_name) > 0:
          logger.debug("Tag form is valid, yo.")
          
          if tag_facet_id != "None":
            tag_facet = Facet.objects.get(pk=tag_facet_id)
          else:
            tag_facet = None
            
          tag_draft = {'name': tag_name,
                       'creator': request.user,
                       'group': group,
                       'facet': tag_facet}
          
          new_tag = Tag(**tag_draft)
          new_tag.save()
        
      if submit_new_facet:
        
        facet_form = FacetForm(request.POST, prefix="facet")
        
        if facet_form.is_valid():

          facet_form.cleaned_data['creator'] = request.user
          facet_form.cleaned_data['group'] = group
          
          facet_form.save()
 
      # Adding tags and facets are inside the same form.
      # Let's always bind the POST data to all the forms so they get remembered.
      # But let's decide which forms to validate based on which submit button is pressed.
      if submit_new_entry: 
      
        # Bind the post request to the Entry ModelForm for validation and redisplay 
        # in case of errors.
        entry_form = EntryForm(request.POST)

        if entry_form.is_valid():
          
          # Manually add the current user and current group (from the url)
          # as validated data in the modelform.
          entry_form.cleaned_data['creator'] = request.user
          entry_form.cleaned_data['group'] = group
            
          # Convert the list of tag id inputs into a list of Tag models      
          entry_tag_list = request.POST.getlist('tags[]')
          entry_tags = Tag.objects.in_bulk(entry_tag_list)
          entry_form.cleaned_data['tags'] = entry_tags
          
          # Using the models' validated data, actually create a corresponding 
          # model instance and save it to the database.
          entry_form.save()
          
          # After saving, redirect back to the page of the group where you saved
          # the new entry
          return HttpResponseRedirect('/madscientist/groups/{}/'.format(group_id))
      else:
        
        # Manually re-display entry form information if a sub-form was submitted.
        
        # Convert list of tag inputs to actual tag objects
        entry_tag_list = request.POST.getlist("tags[]")
        entry_tags = Tag.objects.in_bulk(entry_tag_list)
        
        entry_draft = {"title": request.POST.get("", ""),
                       "body": request.POST.get("body", ""),
                       "image": request.POST.get("image", ""),
                       "tags": entry_tag_list}
        entry_form = EntryForm(initial=entry_draft)

    else:
        # Otherwise, display a blank version of the form
        entry_form = EntryForm()
        
    context = {'tags': tags,
               'empty_facets': empty_facets,
               'group_list': groups,
               'current_group': group,
               'entry_form': entry_form}
    
    return render_to_response('madscientist/add_entry.html',
                              context_instance=RequestContext(request, context))

def add_facet(request, group_id):
  """ This is a view to add a new facet to the group. """

  # Reject requests for non-public groups the current user did not create
  group = EntryGroup.objects.get(pk=group_id)
  
  # If user doesn't have permission to see this group, redirect
  if request.user != group.creator:
        return render_to_response('madscientist/forbidden.html',
                            context_instance=RequestContext(request)) 
  
  if request.method == 'POST':
    
    form = FacetForm(request.POST)
  
  
  return True

def logout_user(request):
  """ This is a view which logs out the current user. """
  logout(request)
  return render_to_response('madscientist/success.html',
                            context_instance=RequestContext(request))
    
def login_user(request):
  """ This is a view for logging in a user of the site.
  """
  message = ""
  
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
      
          if request.GET:
                     
            next_page = request.GET['next']
            
            return HttpResponseRedirect(next_page)
          else:
            return HttpResponseRedirect("/madscientist/")
        
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
      
      
      
      
      
