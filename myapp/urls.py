from django.urls import path
from . import views
from .views import CurrencyRateListView,CurrencyRateDifferenceView
urlpatterns = [
    path('scrape-ecb/', views.scrape_ecb_data, name='scrape_ecb'),
    path('currency-rates/', CurrencyRateListView.as_view(), name='currency-rates-list'),
    path('currency-rate-difference/', CurrencyRateDifferenceView.as_view(), name='currency-rate-difference'),

]
