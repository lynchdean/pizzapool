from django.urls import path

from . import views

app_name = "events"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<uuid:pk>/", views.EventView.as_view(), name="event"),
    path("<uuid:pk>/create-pizza-order/", views.create_pizza_order, name='create-pizza-order')
]