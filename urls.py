from django.conf.urls.defaults import patterns

urlpatterns = patterns('django.views.generic.simple',
                       
    (r'^splash$', 'direct_to_template', {'template': 'madscientist/splash.html'})
)

urlpatterns += patterns('',                  
    (r'^$', 'madscientist.views.home'),
    (r'^login/$', 'madscientist.views.login_user'),
    (r'^logout/$', 'madscientist.views.logout_user'),
    (r'^groups/(?P<group_id>\d+)/$', 'madscientist.views.entry_list'),
    (r'^groups/(?P<group_id>\d+)/add/$', 'madscientist.views.edit_entry'),
    (r'^groups/(?P<group_id>\d+)/edit/(?P<entry_id>\d+)/$', 'madscientist.views.edit_entry')
) 

