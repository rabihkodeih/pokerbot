from bots.views import home, monitoring, chat, scheduler, scripts
from django.conf.urls import patterns, include, url
from django.contrib import admin

# Uncomment the next two lines to enable the admin:
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    
     #User mgt
     url(r'^bots/user/login', 'django.contrib.auth.views.login', {'template_name':'templates/user/login.html'}),
     url(r'^bots/user/logout', 'django.contrib.auth.views.logout', {'next_page':'/bots'}),
     
     url(r'^bots/home/', include(home.urls)),
     url(r'^bots/monitoring/', include(monitoring.urls)),
     url(r'^bots/chat/', include(chat.urls)),
     url(r'^bots/scheduler/', include(scheduler.urls)),
     url(r'^bots/scripts/', include(scripts.urls)),
#     url(r'^bots/robopoker/', include(robopoker.urls)),
     url(r'^bots/$', 'bots.views.home.home'),
)
