from django.contrib import admin
from forms import IdeaForm
from models import Idea, Facet, Tag

class CommonMedia:
  js = (
    'https://ajax.googleapis.com/ajax/libs/dojo/1.6.0/dojo/dojo.xd.js',
    'editor/js/editor.js',
  )
  css = {
    'all': ('editor/css/editor.css',),
  }


class IdeaAdmin(admin.ModelAdmin):
             
    list_display = ['date_created', 'title', 'description']
    list_editable = ['title']
    list_filter = ['date_created', 'tag']
    ordering = ['-date_created']    
    
    # Use a ModelForm with my custom widget for tagging
    form = IdeaForm
    
    # This pulls in the rich text editor
    Media = CommonMedia

# So you can add tags that go under a facet from the facet creation / editing page
class TagInline(admin.TabularInline):
    model = Tag
    ordering = ['name']
    extra = 4

class FacetAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    inlines = [TagInline]
    ordering = ['name']

class TagAdmin(admin.ModelAdmin):
    list_display = ['facet', 'name']
    list_filter = ['facet']
    list_editable = ['name']
    ordering = ['facet']

admin.site.register(Idea, IdeaAdmin)
admin.site.register(Facet, FacetAdmin)
admin.site.register(Tag, TagAdmin)