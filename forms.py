from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms.util import ErrorList
from models import Entry, Tag, Facet, EntryGroup
from widgets import FacetedColumnCheckboxSelectMultiple
import logging

# import the logging library and get an instance of the logger
logger = logging.getLogger(__name__)

class AdminEntryForm(forms.ModelForm):
  """ Form used in the admin for adding entries. """
  
  # Set up my custom widget of columns of checkboxes grouped by facet.
  # It's important to sort the queryset by facet, otherwise the widget 
  # grouping will be incorrect.
  
  tags = forms.ModelMultipleChoiceField(required=False,
                                       queryset=Tag.objects.order_by('facet', 'name'),
                                       widget=FacetedColumnCheckboxSelectMultiple)
    
  class Meta:
    model = Entry

class CustomForm(forms.Form):
  
  # This constructor exists purely so I can override the default value of 
  # label_suffix for this form and get rid of the automatic colons, instead
  # of having that detail in the view logic.
  def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
               initial=None, error_class=ErrorList, label_suffix='',
               empty_permitted=False):
    
    super(CustomForm, self).__init__(data, files, auto_id, prefix, initial,
                                          error_class, label_suffix, empty_permitted)
    
    
class CustomModelForm(forms.ModelForm):
  
  # This constructor exists purely so I can override the default value of 
  # label_suffix for this form and get rid of the automatic colons, instead
  # of having that detail in the view logic.
  def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
               initial=None, error_class=ErrorList, label_suffix='',
               empty_permitted=False, instance=None):
    
    super(CustomModelForm, self).__init__(data, files, auto_id, prefix, initial,
                                          error_class, label_suffix, empty_permitted, instance)
    
class EntryForm(CustomModelForm):
  """ This is the form used on the website for adding entries. 
      Excludes group because that is provided by dd-entry url and
      creator because that is provided by the session. """          
             
  def save(self, commit=True):
    """ For this form save is overriden so that we can manually
        add back in two required fields excluded from the 
        form shown to the user. """
    
    # Save the filled in model fields without saving to the database,
    # so that we have a primary key as needed for many-to-many
    # relationships.
    instance = super(EntryForm, self).save(commit=False)
    instance.save()
    
    instance.tags = self.cleaned_data['tags']
  
    if commit:
        self.save_m2m()

    return instance 
  
  title = forms.CharField(error_messages={'required': 'Oops, your idea needs a title.'})
  required_css_class = "required"

  class Meta:
    
    model = Entry
    exclude = ['creator', 'group', 'tag']
    fields = ['title', 'image', 'body']

class EntryGroupForm(CustomModelForm):
  
  title = forms.CharField(error_messages={'required': 'Oops, your group needs a title.'})
  short_title = forms.CharField(error_messages={'required': 'Oops, your group needs a short title to display on the tab.'})
  required_css_class = "required"  
  
  class Meta:
    model = EntryGroup
    exclude = ['creator']
    fields = ['public', 'short_title','title', 'description']


class TagForm(CustomModelForm):
  
  class Meta:
    model = Tag
    exclude = ['creator', 'group', 'facet']
    
  def save(self, commit=True):
    """ For this form save is overriden so that we can manually
        add back in two required fields excluded from the 
        form shown to the user. """
    
    # Save the filled in model fields without saving to the database,
    # which would trigger an error because both group and creator are
    # required fields. 
    instance = super(TagForm, self).save(commit=False)
    
    # @TODO: Move these auto-filled fields to the view. 
    # Now that we have an instance of the model, we can add back in the
    # other fields we handle outside of the modelform.
    instance.creator = self.cleaned_data['creator']
    instance.group = self.cleaned_data['group']
    instance.facet = self.cleaned_data['facet']
    
    instance.save()

    return instance     

class FacetForm(CustomModelForm):
  
  name = forms.CharField(label="")
  
  class Meta:
    model = Facet
    exclude = ['creator', 'group', 'description']
    
  def save(self, commit=True):
    """ For this form save is overriden so that we can manually
        add back in two required fields excluded from the 
        form shown to the user. """
    
    # Save the filled in model fields without saving to the database,
    # which would trigger an error because both group and creator are
    # required fields. 
    instance = super(FacetForm, self).save(commit=False)
    
    # Now that we have an instance of the model, we can add back in the
    # other fields we handle outside of the modelform.
    instance.creator = self.cleaned_data['creator']
    instance.group = self.cleaned_data['group']
    
    instance.save()
     
    return instance     
  
class DetailedFacetForm(CustomModelForm):
  
  name = forms.CharField(error_messages={'required': 'Oops, your category needs a name.'})
  required_css_class = "required"  
  
  class Meta:
    model = Facet
    exclude = ['creator', 'group']
      
class LoginForm(CustomForm):
  """ Very simple form to login a user. """
  username = forms.CharField(label="Username")
  password = forms.CharField(widget=forms.PasswordInput(), label="Password")

    
class NewUserForm(CustomForm):
  """ Very simple form to create a new user. 
      To be replaced with the django-registration app someday. """
  
  email = forms.EmailField(label="Email", required=True)
  username = forms.CharField(label="Username", required=True) 
  password = forms.CharField(widget=forms.PasswordInput(), label="Password", required=True)
  
  def clean_username(self):
    """ Basic username validator.
    """
    
    # Check if there are spaces in the username, since this causes problems.
    username = self.cleaned_data['username']
    if ' ' in username:
      raise ValidationError("Username can't have spaces.")
    
    # Check for existing user with same username.
    existing_user = User.objects.filter(username=username)
    if existing_user:
      raise ValidationError("This username has already been taken.")
    
    return self.cleaned_data['username']




