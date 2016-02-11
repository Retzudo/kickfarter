import app.views
from django.conf.urls import url
from django.conf.urls.static import static
from kickfarter import settings

urlpatterns = [
    url(r'^$', app.views.index, name='index'),
    url(r'^login$', app.views.login_view, name='login'),
    url(r'^logout', app.views.logout_view, name='logout'),
    url(r'^signup$', app.views.signup, name='signup'),
    url(r'^profile$', app.views.profile, name='profile'),
    url(r'^start$', app.views.start_project, name='start_project'),
    url(r'^discover$', app.views.discover, name='discover'),
    url(r'^project/(?P<id>\d+)/edit$', app.views.edit_project, name='edit_project'),
    url(r'^project/(?P<id>\d+)$', app.views.view_project, name='view_project'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
