import app.views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', app.views.index, name='index'),
    url(r'^login$', app.views.login, name='login'),
    url(r'^signup$', app.views.signup, name='signup'),
]