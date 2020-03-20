from django.urls import path
from .views import OverviewCreateView

app_name = "overview"
urlpatterns = [
    path('create', OverviewCreateView.as_view(), name='create'),
]
