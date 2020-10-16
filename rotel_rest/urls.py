"""rotel_rest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from rotel_rest  import views

urlpatterns = [
  path('', views.home),    
  path('rotel_setvalue/<str:command>/<int:value>', views.rotel_setvalue),    
  path('rotel_getvalue/<str:command>', views.rotel_getvalue),    
  path('rotel_sendcommand/<str:command>', views.rotel_sendcommand),    
  path('rotel_wakeup/', views.rotel_wakeup),    
  ## path('admin/', admin.site.urls),
]
