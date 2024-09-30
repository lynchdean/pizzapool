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
    path('stats/', views.PizzaOrderStatsView.as_view(), name='stats'),
    path("orgs/", views.OrgIndexView.as_view(), name="org-index"),
    path("<slug:path>/", views.OrgDetailView.as_view(), name="org-detail"),
    path("<slug:path>/<uuid:pk>/", views.EventView.as_view(), name="event"),
    path("<slug:path>/<uuid:pk>/create-pizza-order/", views.create_pizza_order, name='create-pizza-order'),
    path("<slug:path>/<int:pk>/claim-slices/", views.claim_slices, name='claim-slices'),
    path("<slug:path>/<int:pk>/delete-slices/", views.PizzaSlicesDeleteView.as_view(), name='delete-slices'),
]
