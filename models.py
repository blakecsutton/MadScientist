from django.db import models
from django.contrib.auth.models import User
    
class EntryGroup(models.Model):
  """ This is a group of Entries (a list, or a board in the context of Trello or 
      Pinterest). All Entries which belong to this group will appear together 
      one one tab, page, etc.
  """
  # The user who created the board. Only this user can add/edit/update/delete
  # entries. Set to allow null entries so the user can be added automatically under
  # the covers instead of explicitly.
  creator = models.ForeignKey(User)
  
  # Automatically update the timestamp whenever the model is saved.
  date_modified = models.DateField(auto_now=True)
  
  # Longer title (or you can just copy the short title)
  title = models.CharField(max_length=200)
  
  # Shorter title which appears on the tab
  short_title = models.CharField(max_length=200)
  
  description = models.TextField(null=True, blank=True)
  
  # Flag for whether or not the group's contents are viewable by anyone.
  public = models.BooleanField(default=False)
  
  def __unicode__(self):
    return self.short_title
  
class Facet(models.Model):
    """ This is a Facet, a general category used to group tags. It is a one-level hierarchy, and 
        although there is no enforcement it is expected that there are relatively few facets.
    
        Facets have a 1:N relationship with tags, as in tags must belong to exactly 1 facet, while
        facts can contain multiple tags. The description field is required because facets should have
        a lot of thought put into them.
    """
    creator = models.ForeignKey(User)
    
    group = models.ForeignKey(EntryGroup)
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return "%s" % self.name
    
class Tag(models.Model):
    """ This is a Tag, a single word/phrase attached to Ideas for categorization and browsing purposes.
        Tags have an optional N:1 relationship with a Facet, that is each tag can have 0 or 1 Facets 
        associated with it.
        
        Tags need no description field because the name of the tag taken in conjunction with a possible
        parent facet should provide enough information to figure out what it means.
        
        Tags also have an optional M:N relationship with ideas: many ideas can have the same tag, and many tags
        can be attached to one idea. Every tag does not have to have an idea attached to it (supports 
        setting up a tagging system in advance) and every idea does not have to be tagged with something 
        (adds flexibility if an idea doesn't fit in the current system).
        
        Tags belong to exactly one EntryGroup. Although it is possible that users might want to 
        share tags across groups, that possibilitiy is currently eclipsed by the desire to keep
        tag clouds minimal and organized.
    """
    creator = models.ForeignKey(User)
    
    group = models.ForeignKey(EntryGroup)
    
    name = models.CharField(max_length=100)
    
    facet = models.ForeignKey(Facet, blank=True, null=True)

    def __unicode__(self):
         
        return self.name
    
class Entry(models.Model):
  """ This is a single Entry, which belongs to one and only one Group.
      All entries also have titles, dates, and optional tags. """
      
  creator = models.ForeignKey(User)
  
  group = models.ForeignKey(EntryGroup)
  
  date_created = models.DateField(auto_now_add=True)
  
  title = models.CharField(max_length=200)
  
  tags = models.ManyToManyField(Tag, null=True, blank=True, default=None)
  
  body = models.TextField(null=True, blank=True)
  
  image = models.ImageField(null=True, blank=True, upload_to='madscientist')
    
  def __unicode__(self):
      return self.title
    
  class Meta:
    verbose_name = "Entry"
    verbose_name_plural = "Entries"