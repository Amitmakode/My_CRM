from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('lead/add/', views.add_lead, name='add_lead'),
    path('lead/<int:pk>/', views.lead_detail, name='lead_detail'),
    path('lead/<int:pk>/edit/', views.edit_lead, name='edit_lead'),
    path('lead/<int:pk>/delete/', views.delete_lead, name='delete_lead'),
    path('lead/<int:pk>/followup/', views.add_followup, name='add_followup'),
    path('followup/<int:pk>/complete/', views.complete_followup, name='complete_followup'),
    path('users/', views.manage_users, name='manage_users'),
    path('users/create/', views.create_user, name='create_user'),
    path('import/', views.import_leads, name='import_leads'),
    path('export/', views.export_leads, name='export_leads'),
    path('all-leads/', views.all_leads, name='all_leads'),
    path('analytics/', views.analytics, name='analytics'),
]