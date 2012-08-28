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
    (r'^login-error/$', 'login_user'),
    
    (r'^groups/(?P<group_id>\d+)/$', 'entry_list'),
    
    (r'^groups/add/$', 'edit_group'),
    (r'^groups/edit/(?P<group_id>\d+)/$', 'edit_group'),
    (r'^groups/delete/(?P<group_id>\d+)/$', 'delete_group'),
    
    (r'^groups/(?P<group_id>\d+)/add/$', 'edit_entry'),
    (r'^groups/(?P<group_id>\d+)/edit/(?P<entry_id>\d+)/$', 'edit_entry'),
    (r'^groups/(?P<group_id>\d+)/delete/(?P<entry_id>\d+)/$', 'delete_entry'),
    
    (r'^groups/(?P<group_id>\d+)/tags/', 'edit_tags'),
    
    (r'^groups/(?P<group_id>\d+)/facets/edit/(?P<facet_id>\d+)/', 'edit_facet'),
    (r'^groups/(?P<group_id>\d+)/facets/delete/(?P<facet_id>\d+)/', 'delete_facet')
    
) 

