import app.views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', app.views.index, name='index'),
    url(r'^login$', app.views.login_view, name='login'),
    url(r'^logout', app.views.logout_view, name='logout'),
    url(r'^signup$', app.views.signup, name='signup'),
]