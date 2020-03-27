"""interactive URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from closets.views import ClosetsCreateView
from overview.views import OverviewCreateView, OverviewUpdateView

urlpatterns = [
    path('fulldash/admin/', admin.site.urls),
    path('fulldash/create/', OverviewCreateView.as_view(), name='overview_create'),
    path('fulldash/<int:id>/update/',
         OverviewUpdateView.as_view(), name='overview_update'),
    path('fulldash/<int:id>/closets/',
         ClosetsCreateView.as_view(), name='closets_create'),
]
