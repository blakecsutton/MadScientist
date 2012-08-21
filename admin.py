from django.contrib import admin
from forms import AdminEntryForm
from models import Facet, Tag
from models import EntryGroup, Entry

# Logging
import logging
logger = logging.getLogger(__name__)

class CommonMedia:
  js = (
    'https://ajax.googleapis.com/ajax/libs/dojo/1.6.0/dojo/dojo.xd.js',
    'editor/js/editor.js',
  )
  css = {
    'all': ('editor/css/editor.css',),
  }

# Class to encapsulate standard user permissions and save user to the model
# automatically.
class UserControlledAdmin(admin.ModelAdmin):
    
    def has_change_permission(self, request, obj=None):
      """ The user can only change objects of which they are creator. """
      if request.user.is_superuser:
        return True
      elif obj:
        return (obj.creator == request.user)
      else:
        return True
    
    def has_delete_permission(self, request, obj=None):
      """ The user can only delete object if they're the creator. """
      if request.user.is_superuser:
        return True
      elif obj:
        return (obj.creator == request.user)
      else:
        return True
      
    def save_model(self, request, obj, form, change):
      """ Automatically save the currently authenticated user into the 
            creator field of the EntryGroup. """
            
      # Only need to save the user the first time the object is created
      if not change:
        obj.creator = request.user
        
      obj.save()
      
class EntryGroupAdmin(UserControlledAdmin):

    def queryset(self, request):
      
      """ Returns only the EntryGroup objects which were created by the current user. """
      if request.user.is_superuser:
        return EntryGroup.objects.all()
      else:
        return EntryGroup.objects.filter(creator=request.user)
      
    list_display = ['creator', 'short_title', 'title', 'description', 'public']
    list_editable = ['short_title', 'public']
    list_filter = ['public']
    order = ['-date_modified']
    
    # Exclude this from the form because it is auto-generated in save_model
    exclude = ['creator']

class EntryAdmin(UserControlledAdmin):
  
    def queryset(self, request):
      """ Returns only the TextEntry objects which belong to EntryGroups created by the current user. """
      if request.user.is_superuser:
        return Entry.objects.all()
      else:
        return Entry.objects.filter(creator=request.user)
        
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
      """ For the group foreign key to EntryGroup, restrict choices to
          to groups that the current owns (except for the superuser). """
      if db_field.name == "group":
        
        if not request.user.is_superuser:
          kwargs["queryset"] = EntryGroup.objects.filter(creator=request.user)
          
        return super(EntryAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)       
  
    def formfield_for_manytomany(self, db_field, request, **kwargs):
      """ For the tags foreign key to Tag, only display tags the current
          user created. """
          
    
      if db_field.name == "tags":
        
        if not request.user.is_superuser:
          kwargs["queryset"] = Tag.objects.filter(creator=request.user)
          
        return super(EntryAdmin, self).formfield_for_manytomany(db_field, request, **kwargs) 
   
    # Customization for browsing Entries in the admin
    list_display = ['group', 'title', 'image', 'body', 'date_created']
    list_filter = ['date_created', 'tags']
    ordering = ['-date_created']    
    list_editable = ['title']
    
    # Customization for editing Entries
    fields = ['group', 'title', 'image', 'tags', 'body']
    exclude = ['creator'] 
    
    form = AdminEntryForm
    
    # This pulls in the rich text editor
    #Media = CommonMedia
        

# So you can add tags that go under a facet from the facet creation / editing page
class TagInline(admin.TabularInline):
      
  model = Tag
  ordering = ['name']
  extra = 2
  
  # Get the creator from the session and the group from the outer Facet object.
  exclude = ['creator', 'group']

class FacetAdmin(UserControlledAdmin):
    
  def queryset(self, request):
    """ Returns only the user's facets. """
    if request.user.is_superuser:
      return Facet.objects.all()
    else:
      return Facet.objects.filter(creator=request.user)
    
  def save_formset(self, request, form, formset, change):
    """ Automatically save the currently authenticated user into the 
        creator field of the tag when it's created inline. """
      
    # Create model instances for each formset, but don't save to database.
    instances = formset.save(commit=False)
    
    facet = form.save(commit=False)
    group = facet.group
      
    # Cycle through model instances from the formset
    for instance in instances:
      
        #Check if it is the correct type of inline
        if isinstance(instance, Tag):
            instance.creator = request.user
            instance.group = group
            instance.save()

      
  list_display = ['name', 'group', 'description']
  inlines = [TagInline]
  ordering = ['name']
  exclude = ['creator']     

class TagAdmin(UserControlledAdmin):
  
  def queryset(self, request):
    """ Returns only the user's tags. """
    if request.user.is_superuser:
      return Tag.objects.all()
    else:
      return Tag.objects.filter(creator=request.user)
  
  def formfield_for_foreignkey(self, db_field, request, **kwargs):
    """ Make sure only the current user's facets appear as choices when
        creating a new tag. """
  
    if db_field.name == "facet":
        
      if not request.user.is_superuser:
        kwargs["queryset"] = Facet.objects.filter(creator=request.user)
        
    if db_field.name == "group":
        
      if not request.user.is_superuser:
        kwargs["queryset"] = EntryGroup.objects.filter(creator=request.user)
                  
    return super(TagAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
  
  def save_model(self, request, obj, form, change):
    
    # If no facet was specified, automatically assign it 
    # to the "Uncategorized" facet (create it if it doesn't exist)
    
    # And now explicity evoke the super method
    super(TagAdmin, self).save_model(request, obj, form, change)          
  
  list_display = ['group', 'facet', 'name']
  list_filter = ['group', 'facet']
  list_editable = ['name']
  ordering = ['facet']
  exclude = ['creator']

admin.site.register(EntryGroup, EntryGroupAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(Facet, FacetAdmin)
admin.site.register(Tag, TagAdmin)