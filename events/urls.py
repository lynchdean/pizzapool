from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from pizzapool import settings
from . import views

app_name = "events"
urlpatterns = [
    path('', views.HomePage.as_view(), name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name='logout'),
    path('user/<str:username>', views.UserView.as_view(), name='user'),
    path("<slug:path>/", views.OrgDetailView.as_view(), name="org-detail"),
    path("<slug:path>/edit/", views.edit_organisation, name="org-edit"),
    path("<slug:path>/create/", views.EventCreateView.as_view(), name="event-create"),
    path("<slug:path>/<slug>/", views.EventView.as_view(), name="event-detail"),
    path("<slug:path>/<slug>/edit/", views.edit_event, name="event-edit"),
    path("<slug:path>/<slug>/delete/", views.EventDeleteView.as_view(), name="event-delete"),
    path("<slug:path>/<slug>/create-order/", views.create_pizza_order, name='create-pizza-order'),
    path("<slug:path>/<slug>/<int:pk>/delete-order/", views.OrderDeleteView.as_view(), name='order-delete'),
    path("<slug:path>/<int:pk>/claim/", views.claim_slices, name='claim-slices'),
    path("<slug:path>/<int:pk>/delete-slices/", views.PizzaSlicesDeleteView.as_view(), name='delete-slices'),
]
