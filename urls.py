from django.conf.urls.defaults import patterns

urlpatterns = patterns('django.views.generic.simple',
                       
    (r'^splash$', 'direct_to_template', {'template': 'madscientist/splash.html'})
)
"""
@TODO: Make URLs include the username and such.
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

