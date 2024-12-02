from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
      path('upload_excel/', views.upload_excel, name='upload_excel'),
      path('index/', views.index, name='app1-index'),
      path('calcules/',views.calcules, name='calcules'),
       path('select_calculations/', views.select_calculations, name='select_calculations'),
      path('perform_calculations/', views.perform_calculations, name='perform_calculations')
]


