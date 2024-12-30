from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
      path('accueil/', views.accueil, name='accueil'),  
      path('parcourir/',views.parcourir_chart,name='parcourir_chart'),
      path('upload/', views.visualisation, name='app1-upload_file'),
      path('upload_excel/', views.upload_excel, name='upload_excel'),
      path('index/', views.index, name='app1-index'),
      path('calcules/',views.calcules, name='calcules'),
       path('select_calculations/', views.select_calculations, name='select_calculations'),
      path('visualisation-les-donnnes/', views.visualisation_de_donnnes, name='app1-visualisation_de_donnnes'),
      path('traitement_graphe/', views.traitement_graphe, name='app1-traitement_graphe'),
      path('choix_colonnes/',views.choixcolonnes,name='app1-choix_colonnes'),
      path('visualiserchart/', views.visualiser_chart, name='visualiser_chart'),
      path('diagramme/', views.diagramme, name='diagramme'), 
      path('perform_calculations/', views.perform_calculations, name='perform_calculations'),
       path('bernoulli/', views.bernoullii, name='bernoulli'),
      path('binomial/', views.binomial, name='binomial'),
      path('exponentielle/', views.exponentielle, name='exponentielle'),
      path('normal/', views.normal, name='normal'),
      path('poisson/', views.poissonn, name='poisson'),
      path('uniforme/', views.uniforme, name='uniforme'),
      path('uniformecontinue/', views.uniformecontinue, name='uniformecontinue'),
      path('graphe_bernoulli/', views.afficher_bernoullii, name='afficher_bernoulli'),
      path('graphe_binomial/', views.afficher_binomial, name='afficher_binomial'),
      path('graphe_exponentielle/', views.afficher_exponentielle, name='afficher_exponentielle'),
      path('graphe_normal/', views.afficher_normal, name='afficher_normal'),
      path('graphe_poisson/', views.afficher_poissonn, name='afficher_poissonn'),
      path('graphe_uniforme/', views.afficher_uniforme, name='afficher_uniforme'),
      path('graphe_uniformecontinue/', views.afficher_uniformecontinue, name='afficher_uniformecontinue'),
      path('calcule_statistique/',views.calcules, name='calcule_statistique'),
      path('parcourir/',views.parcourir_chart,name='parcourir_chart')
]


     