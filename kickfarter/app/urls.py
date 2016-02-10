import app.views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', app.views.index, name='index'),
    url(r'^login$', app.views.login_view, name='login'),
    url(r'^logout', app.views.logout_view, name='logout'),
    url(r'^signup$', app.views.signup, name='signup'),
    url(r'^profile$', app.views.profile, name='profile'),
    url(r'^start$', app.views.start_project, name='start_project'),
    url(r'^discover$', app.views.discover, name='discover'),
]
