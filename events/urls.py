import django.contrib.auth.views as auth_views
from django.urls import path

from pizzapool import settings
from . import views

app_name = "events"
urlpatterns = [
    # Index
    path('', views.HomePage.as_view(), name='home'),
    # Auth
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name='logout'),
    # Events
    path('user/<str:username>', views.UserView.as_view(), name='user'),
    path("<slug:path>/", views.OrgDetailView.as_view(), name="org-detail"),
    path("<slug:path>/edit/", views.OrgUpdateView.as_view(), name="org-update"),
    path("<slug:path>/create-event/", views.EventCreateView.as_view(), name="event-create"),
    path("<slug:path>/<slug>/", views.EventDetailView.as_view(), name="event-detail"),
    path("<slug:path>/<slug>/edit/", views.EventEditView.as_view(), name="event-edit"),
    path("<slug:path>/<slug>/delete/", views.EventDeleteView.as_view(), name="event-delete"),
    path("<slug:path>/<slug>/create-order/", views.OrderCreateView.as_view(), name='create-pizza-order'),
    path("<slug:path>/<slug>/<int:pk>/delete-order/", views.OrderDeleteView.as_view(), name='order-delete'),
    path("<slug:path>/<int:pk>/claim/", views.ServingCreateView.as_view(), name='claim-servings'),
    path("<slug:path>/<int:pk>/delete-servings/", views.ServingDeleteView.as_view(), name='delete-servings'),
]
