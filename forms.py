from django import forms
from django.forms.util import ErrorList
from models import Entry, Tag, Facet
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
    # which would trigger an error because both group and creator are
    # required fields. 
    instance = super(EntryForm, self).save(commit=False)

    # Now that we have an instance of the model, we can add back in the
    # other fields we handle outside of the modelform.
    instance.save()
  
    instance.tags = self.cleaned_data['tags']
    
    if commit:
        instance.save()
        self.save_m2m()
        
    return instance 
  
  title = forms.CharField(error_messages={'required': 'Oops, your idea needs a title.'})
  required_css_class = "required"

  class Meta:
    
    model = Entry
    exclude = ['creator', 'group', 'tag']
    fields = ['title', 'image', 'body']

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
      
class LoginForm(forms.Form):
  """ Very simple form to login a user. """
  username = forms.CharField(label="Username")
  password = forms.CharField(widget=forms.PasswordInput(), label="Password")
      
