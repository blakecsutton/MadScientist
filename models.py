from django.db import models
from datetime import datetime

class Facet(models.Model):
    """ This is a Facet, a general category used to group tags. It is a one-level hierarchy, and 
        although there is no enforcement it is expected that there are relatively few facets.
    
        Facets have a 1:N relationship with tags, as in tags must belong to exactly 1 facet, while
        facts can contain multiple tags. The description field is required because facets should have
        a lot of thought put into them.
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    
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
    """
    name = models.CharField(max_length=100)
    facet = models.ForeignKey(Facet, null=True, blank=True, default=None)

    def __unicode__(self):
         
        return self.name

class Idea(models.Model):
    """ This is an Idea, which consists of a title (short but identifiable) and a description,
        which may be very long and included markup such as links to resources or inspiration
        for the idea. There is also an optional Image field for a local image (such as a scanned
        sketch/diagram/image, or maybe a photo of the completed project?).
    """
    date_created = models.DateField(default=datetime.now())
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(blank=True, upload_to='madscientist/uploads')
    
    tag = models.ManyToManyField(Tag, null=True, blank=True, default=None)
    
    def __unicode__(self):
        return self.title
    
    



    
    

    
    
    