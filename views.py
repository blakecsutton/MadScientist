from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Count
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from forms import LoginForm, EntryForm, FacetForm, EntryGroupForm, \
  DetailedFacetForm, NewUserForm
from models import Entry, Facet, Tag, EntryGroup
import logging

# import the logging library and get an instance of the logger
logger = logging.getLogger(__name__)

@login_required(login_url="/madscientist/login")
def home(request, username=None):

  # Check that username in the URL matches username in the session.
  if username:
    
    logger.debug("Username is {}".format(username))
    
    if request.user.username != username:
      raise PermissionDenied()
    
  # Just show the groups view with the most recently updated group as the active group.
  entries = Entry.objects.filter(creator=request.user).order_by('date_created')
  
  if entries:
    group_id = entries[0].group.id
  else:
    group_id = None
    
  return entry_list(request, request.user.username, group_id)

@login_required(login_url="/madscientist/login/")
def entry_list(request, username, group_id):
    """ This is the main view for the site, which displays the list of ideas and the related tags.
        Later, will want to add the ability to filter by tag, as well as search.
    """
    
    if username:
      
      if request.user.username != username:
        raise PermissionDenied()
    
    if group_id:
      
      # Reject requests for non-public groups the current user did not create
      group = get_object_or_404(EntryGroup, pk=group_id)
    
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
      
    else:
      context = {}
      
    return render_to_response('madscientist/base.html',
                              context_instance=RequestContext(request, context))     
  
@login_required(login_url="/madscientist/login/")
def edit_entry(request, group_id, entry_id=None):
    """ This is a view to either edit or add an entry to a specific group. 
        If no entry_id is provided, the view assumes you are adding a new entry,
        otherwise it will edit the entry with the corresponding id. """
    
    # Reject requests for groups the current user did not create
    group = EntryGroup.objects.get(pk=group_id)
 
    # If user doesn't have permission to see this group, raise Forbidden error.
    if request.user != group.creator:
      raise PermissionDenied()
    
    # If an entry id was provided, use it to look up the corresponding entry.    
    if entry_id:
      entry = get_object_or_404(Entry, pk=entry_id)
      entry_tags = entry.tags.values_list('id', flat=True)
      
      # If the entry's group doesn't match the current group, raise an error.
      if entry.group != group:
        raise Http404()
      
      if entry.creator != request.user:
        raise PermissionDenied()
    else:
      # Otherwise, create new Entry object for the current user, in the current group.
      entry = Entry(creator=request.user, group=group)
      entry_tags = []
    
    # Get tags for the current group and user to show them as options for the entry.
    tags = Tag.objects.filter(creator=request.user, group=group_id)
    tags = tags.order_by('facet', 'name').values('id', 'name', 'facet__name', 'facet__id')
    
    # Fetch a list of empty facets in case we want to display them
    facets = Facet.objects.filter(creator=request.user, group=group_id)
    empty_facets = facets.annotate(num_tags=Count('tag')).filter(num_tags=0).values('id', 'name')

    if request.method == 'POST':
      
      # Get flags used to see which sub-forms were submitted.
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
        entry_form = EntryForm(request.POST, instance=entry)

        if entry_form.is_valid():
            
          # Convert the list of tag id inputs into a list of Tag models      
          entry_tag_list = request.POST.getlist('tags[]')
          entry_tags = Tag.objects.in_bulk(entry_tag_list)
          entry_form.cleaned_data['tags'] = entry_tags
                               
          # Using the models' validated data, actually create a corresponding 
          # model instance and save it to the database.
          entry_form.save()
          
          # After saving, redirect back to the page of the group where you saved
          # the new entry
          return HttpResponseRedirect(reverse('madscientist.views.entry_list', kwargs={'group_id': group_id}))
      else:
        
        # Manually re-display entry form information if a sub-form was submitted.
        
        # Convert list of tag inputs to actual tag objects
        entry_tag_list = request.POST.getlist("tags[]")
        
        entry_tags = Tag.objects.in_bulk(entry_tag_list)
        entry_tags = [tag_id for tag_id in entry_tags]
        
        entry_draft = {"title": request.POST.get("title", ""),
                       "body": request.POST.get("body", ""),
                       "image": request.POST.get("image", "")}
        entry_form = EntryForm(initial=entry_draft)

    else:
        # Otherwise, display a blank version of the form
        entry_form = EntryForm(instance=entry)
        
    groups = EntryGroup.objects.filter(creator=request.user)
        
    context = {'tags': tags,
               'empty_facets': empty_facets,
               'group_list': groups,
               'current_group': group,
               'entry_form': entry_form,
               'entry_tags': entry_tags,
               'entry_id': entry_id}
    
    return render_to_response('madscientist/add_entry.html',
                              context_instance=RequestContext(request, context))

@login_required(login_url="/madscientist/login/")
def delete_entry(request, group_id, entry_id):
  """ This is a view to delete particular entry. 
      It will fail if the current user did not create the entry or the entry
      specified does not belong to the specified group. """
  
  group = get_object_or_404(EntryGroup, pk=group_id)
  if request.user == group.creator:
    
    entry = get_object_or_404(Entry, pk=entry_id)
    if entry.group != group:
      raise Http404()
  else:
    raise PermissionDenied()
  
  # And then delete the  entry
  entry.delete()
  return HttpResponseRedirect(reverse('madscientist.views.entry_list', kwargs={'group_id': group_id}))

@login_required(login_url="/madscientist/login/")
def edit_group(request, group_id=None):
  """ This is a view to add or edit an EntryGroup. """
  
  # Either retrieve the object to be edited or begin 
  # a shell EntryGroup instance
  if group_id:
    group = get_object_or_404(EntryGroup, pk=group_id)
    
    if group.creator != request.user:
      raise PermissionDenied()
  
  else:
    group = EntryGroup(creator=request.user)
  
  # If the form was submitted
  if request.method == 'POST':
    
    # Bind the request data to the form plus the model instance
    group_form = EntryGroupForm(request.POST, instance=group)
    
    logger.debug("ohai!")
    
    # Use the model form's automatic validation and save
    if group_form.is_valid():
      instance = group_form.save()
      
      # Then redirect to the group's page.
      return HttpResponseRedirect(reverse('madscientist.views.entry_list', 
                                          kwargs={'group_id': instance.id}))
    
  else:
    group_form = EntryGroupForm(instance=group)
    
  # Get a list of all the groups for displaying on the tab bar.
  # Look into ways to abstract this out since it happens on all pages.
  groups = EntryGroup.objects.filter(creator=request.user)
    
  context = {'group_list': groups,
             'group_form': group_form,
             'group_id': group_id}
  
  return render_to_response('madscientist/add_group.html',
                            context_instance=RequestContext(request, context))    
    
@login_required(login_url="/madscientist/login/") 
def delete_group(request, group_id):
  """ This is a view to delete a particular EntryGroup. 
      It will fail if the current user did not create the group. """
  
  group = get_object_or_404(EntryGroup, pk=group_id)
  if request.user != group.creator:
    raise PermissionDenied()
  
  # If it's all good, delete the group.
  # @TODO: would be nice to have a warning about this in the future.
  group.delete()
  
  return HttpResponseRedirect(reverse('madscientist.views.home'))

@login_required(login_url="/madscientist/login/")
def edit_tags(request, group_id):
    """ This is a view to manage the tags for a group (edit, delete, and add).
        Note that you don't control which entries are tagged with what here, only
        the names of tags and their parent categories (facets).
        The edit_entry view only allows adding new tags and facets as a shortcut. """
    
    # Reject requests for groups the current user did not create
    group = EntryGroup.objects.get(pk=group_id)
 
    # If user doesn't have permission to see this group, raise Forbidden error.
    if request.user != group.creator:
      raise PermissionDenied()
    
    # Get tags for the current group and user to show them as options for the entry.
    tags = Tag.objects.filter(creator=request.user, group=group_id)
    tags = tags.order_by('facet', 'name').values('id', 'name', 'facet__name', 'facet__id')
    
    # Fetch a list of empty facets in case we want to display them
    facets = Facet.objects.filter(creator=request.user, group=group_id)
    empty_facets = facets.annotate(num_tags=Count('tag')).filter(num_tags=0).values('id', 'name')

    if request.method == 'POST':
      
      # Get flags used to see which sub-forms were submitted.
      submit_new_facet = request.POST.get('submit_new_facet', False)
      update_tags = request.POST.get('update_tags', False)
      
      if update_tags:
        # The value attribute of the button tells you which facet fieldset was activated.
        tag_facet_id = update_tags.split('-')[2]
        tag_name = request.POST.get(update_tags, "")
        
        if tag_facet_id != "None":
          tag_facet = Facet.objects.get(pk=tag_facet_id)
        else:
          tag_facet = None
          
        # Handle editing any tags which already exist
        edited_tags = Tag.objects.filter(facet=tag_facet)
    
        for edited_tag in edited_tags:
          # Look up field value in the POST request using the tag's id.
          new_name = request.POST.get("tag_{}".format(edited_tag.id), "").strip()
          
          if len(new_name) > 0:
            edited_tag.name = new_name
            edited_tag.save()
          else:
            # Delete the tag if you edit its name to 0 length or only blanks.
            edited_tag.delete()

        # Now handle adding new tag if it's there
        if len(tag_name) > 0:
            
          tag_draft = {'name': tag_name,
                       'creator': request.user,
                       'group': group,
                       'facet': tag_facet}
          
          new_tag = Tag(**tag_draft)
          new_tag.save()
          
      if submit_new_facet:
        
        facet_form = DetailedFacetForm(request.POST)
        
        if facet_form.is_valid():

          facet_form.cleaned_data['creator'] = request.user
          facet_form.cleaned_data['group'] = group
          
          facet_form.save()
        
    groups = EntryGroup.objects.filter(creator=request.user)
    
    facet_form = DetailedFacetForm()
        
    context = {'tags': tags,
               'empty_facets': empty_facets,
               'group_list': groups,
               'facet_form': facet_form,
               'current_group': group}
    
    return render_to_response('madscientist/manage_tags.html',
                              context_instance=RequestContext(request, context))
    
@login_required(login_url="/madscientist/login/")
def edit_facet(request, group_id, facet_id=None):

    # Reject requests for groups the current user did not create
    group = EntryGroup.objects.get(pk=group_id)
 
    # If user doesn't have permission to see this group, raise Forbidden error.
    if request.user != group.creator:
      raise PermissionDenied()
    
    if facet_id:
      facet = get_object_or_404(Facet, pk=facet_id)
    else:
      facet = Facet(creator=request.user, group=group_id)
    
    if request.method == 'POST':
      facet_form = DetailedFacetForm(request.POST, instance=facet)
      
      logger.debug("form has been bound")
      
      if facet_form.is_valid():
        
        facet_form.save()
        
        # Then redirect to the tag manager page
        return HttpResponseRedirect(reverse('madscientist.views.edit_tags', kwargs={'group_id': group_id}))
        
    else:
      facet_form = DetailedFacetForm(instance=facet)
      
    groups = EntryGroup.objects.filter(creator=request.user)
    

    context = {'group_list': groups,
               'facet_id': facet_id,
               'facet_form': facet_form,
               'current_group': group}
    
    return render_to_response('madscientist/edit_facet.html',
                              context_instance=RequestContext(request, context))

@login_required(login_url="/madscientist/login/")
def delete_facet(request, group_id, facet_id):
  
    # Reject requests for groups the current user did not create
    group = get_object_or_404(EntryGroup, pk=group_id)
 
    # If user doesn't have permission to see this group, raise Forbidden error.
    if request.user != group.creator:
      raise PermissionDenied()
    
    facet = get_object_or_404(Facet, pk=facet_id)
    
    # If the facet doesn't belong to the group in the url, raise an error
    if facet.group != group:
      raise Http404()
    
    # If everything is okay, delete the facet
    facet.delete()
    
    # And return to Tag Manager page
    return HttpResponseRedirect(reverse('madscientist.views.edit_tags', kwargs={'group_id': group_id}))
  
@login_required(login_url="/madscientist/login/")   
def logout_user(request):
  
  logger.debug("What is going on here?")
  logout(request)
  return render_to_response('madscientist/success.html',
                            context_instance=RequestContext(request))
    
def login_user(request):
  """ This is a view for logging in a user of the site.
  """
  
  # If the form was submitted
  if request.method == 'POST':
    
    # Check if the login form was submitted
    if "login" in request.POST:
      
      signup_form = NewUserForm()
    
      # Bind the POST data to the form, this includes error information
      # if it doesn't validate.
      login_form = LoginForm(request.POST)
      
      # Trigger validation
      if login_form.is_valid():
        
        username = login_form.cleaned_data['username']
        password = login_form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        
        if user is not None:
          
          if user.is_active:
            
            # Log in the user so their info is saved in the session.
            login(request, user)
        
            if request.GET:
                       
              next_page = request.GET['next']
              
              return HttpResponseRedirect(next_page)
            else:
              return HttpResponseRedirect(reverse('madscientist.views.home', 
                                                  kwargs={'username': request.user.username}))
          
          else:
            # Disabled account
            login_form.is_valid = False
            login_form.errors['username'] = ["Your account has been disabled."]
          
        else:
          # User not found or incorrect password
          login_form.is_valid = False
          login_form.errors['username'] = ["Your username or password is incorrect"]

      
    else:
      login_form = LoginForm()
        
      # Check if the signup form was submitted.
      if "signup" in request.POST:

        signup_form = NewUserForm(request.POST)
        if signup_form.is_valid():
          
          # Check for existing user with same username
          existing_user = User.objects.filter(username=signup_form.cleaned_data['username'])
          
          if existing_user:
            signup_form.is_valid = False
            signup_form.errors['username'] = ["This username has already been taken."]
          else:
            new_user = User.objects.create_user(**signup_form.cleaned_data)
            new_user.save()

            # Authenticate and log in as the newly created user
            username = signup_form.cleaned_data['username']
            password = signup_form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponseRedirect(reverse('madscientist.views.home', 
                                                kwargs={'username': request.user.username}))
                
  else:
    # Create a blank login form and a blank signup form,
    # which will be displayed if there were no form submissions.
    login_form = LoginForm()
    signup_form = NewUserForm()
    
  context = {'login_form': login_form,
             'signup_form': signup_form}
  
  return render_to_response('madscientist/login.html',
                             context_instance=RequestContext(request, context)) 
      
      
      
      
      
