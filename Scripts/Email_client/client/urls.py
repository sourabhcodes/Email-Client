from django.urls import path
from . import views

urlpatterns = [
    path('',views.first),
    path('login',views.login),
    path('checklog',views.logchecker),
    path('mailBox/<int:mn>/<int:page>',views.mailBox),
    path('openmail/<int:mbn>/<int:mid>',views.getMail),
    path('composeMail',views.composeMail),
    path('sendMail',views.sendMail),
    path('deleteMails',views.deleteMail),
    path('flagthis/<int:mid>',views.flagmail),
    path('removeflag/<int:mid>',views.removeflag),
    path('newbox',views.createbox),
    path('movemail/<int:mbn>/<int:mid>/<int:box>',views.movemail),
    path('downloadAttached/<int:mid>',views.downloadAttached),
    path('SearchThis',views.searchThis),
    path('Feedbackform',views.Feedback),
    path('logout',views.logout),
]
