from django.urls import path

from . import views

app_name = "events"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path('events_access/', views.EventsAccessView.as_view(), name='events-access'),
    path('stats/', views.PizzaOrderStatsView.as_view(), name='stats'),
    path("orgs/", views.OrgIndexView.as_view(), name="org-index"),
    path("<slug:path>/", views.OrgDetailView.as_view(), name="org-detail"),
    path("<slug:path>/<uuid:pk>/", views.EventView.as_view(), name="event"),
    path("<slug:path>/<uuid:pk>/create-pizza-order/", views.create_pizza_order, name='create-pizza-order'),
    path("<slug:path>/<int:pk>/claim-slices/", views.claim_slices, name='claim-slices'),
    path("<slug:path>/<int:pk>/delete-slices/", views.PizzaSlicesDeleteView.as_view(), name='delete-slices'),
]
