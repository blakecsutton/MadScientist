from django.conf.urls.defaults import patterns

# This import is here because this seems to be the only way to make the
# custom 403 handler view register.
import django.conf.urls

# Custom 403 template for this app
django.conf.urls.handler403 = 'madscientist.views.error_forbidden'

urlpatterns = patterns('django.views.generic.simple',
                       
    (r'^whats-it-do/', 'direct_to_template', {'template': 'madscientist/what.html'}),
    (r'^take-the-tour/', 'direct_to_template', {'template': 'madscientist/tour.html'}),
    (r'^about/', 'direct_to_template', {'template': 'madscientist/about.html'}),
    
)


"""
@TODO: Make URLs include the username and slugs.
Pinterest style:

Boards pages is pinterest.com/savagerose/
Each board page is /savagerose/tutorials/ -- it lowercases words and replaces spaces with dashes
"""
urlpatterns += patterns('madscientist.views',                  
    (r'^$', 'home'),
    
    (r'^login/$', 'login_user'),
    (r'^logout/$', 'logout_user'),

    (r'^add/$', 'edit_group'),
    (r'^edit/(?P<group_id>\d+)/$', 'edit_group'),
    (r'^delete/(?P<group_id>\d+)/$', 'delete_group'),
    
    (r'^(?P<group_id>\d+)/add/$', 'edit_entry'),
    (r'^(?P<group_id>\d+)/edit/(?P<entry_id>\d+)/$', 'edit_entry'),
    (r'^(?P<group_id>\d+)/delete/(?P<entry_id>\d+)/$', 'delete_entry'),
    
    (r'^(?P<group_id>\d+)/tags/', 'edit_tags'),
    
    (r'^(?P<group_id>\d+)/facets/edit/(?P<facet_id>\d+)/', 'edit_facet'),
    (r'^(?P<group_id>\d+)/facets/delete/(?P<facet_id>\d+)/', 'delete_facet'),
    
    # Important for these to be last because all other patterns should be checked
    # for matches first
    (r'^(?P<username>\w+)/$', 'home'),
    (r'^(?P<username>\w+)/(?P<group_id>\d+)/$', 'entry_list'),
    
) 
