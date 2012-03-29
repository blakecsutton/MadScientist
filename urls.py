from django.conf.urls.defaults import patterns

urlpatterns = patterns('',                  
    (r'^$', 'madscientist.views.idea_list'),
    (r'^add/$', 'madscientist.views.add_idea'),
    (r'^ideas/(?P<idea_id>\d+)/$', 'madscientist.views.idea_detail')
) 

