import time
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from django.utils.timezone import now
from django.http import JsonResponse
from .models import CurrencyRate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from .serializers import CurrencyRateSerializer
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta

@csrf_exempt
def scrape_ecb_data(request):
    options = Options()
    # options.add_argument('--headless')  
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = uc.Chrome(options=options,version_main=130)

    # Open the ECB page
    url = "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html"
    driver.get(url)

    time.sleep(5)  

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    currency_table = soup.find('table', class_='forextable')
    currency_rows = currency_table.find_all('tr')[1:]  

    results = []

    for row in currency_rows:
        columns = row.find_all('td')
        if len(columns) >= 4:  
            currency_code = columns[0].get('id')
            currency_name = columns[1].get_text(strip=True)
            exchange_rate = columns[2].get_text(strip=True)

            if currency_code and currency_name and exchange_rate:
                currency_rate = CurrencyRate(
                    currency_code=currency_code,
                    currency_name=currency_name,
                    exchange_rate=exchange_rate,
                    date=now(),
                )
                currency_rate.save()
                results.append({
                    "currency_code": currency_code,
                    "currency_name": currency_name,
                    "exchange_rate": exchange_rate,
                })

    driver.quit()

    return JsonResponse({"status": "success", "data": results})




class CurrencyRateListView(APIView):
    def get(self, request):
        today = now().date()
        currencies = CurrencyRate.objects.filter(date__date=today)
        serializer = CurrencyRateSerializer(currencies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CurrencyRateDifferenceView(APIView):
    def get(self, request):
        today = now().date()
        yesterday = today - timedelta(days=1)

        # Fetch today's and yesterday's rates
        today_rates = CurrencyRate.objects.filter(date__date=today)
        yesterday_rates = CurrencyRate.objects.filter(date__date=yesterday)

        differences = []
        for today_rate in today_rates:
            try:
                # Find yesterday's rate for the same currency
                yesterday_rate = yesterday_rates.get(currency_code=today_rate.currency_code)
                rate_diff = today_rate.exchange_rate - yesterday_rate.exchange_rate

                # Calculate percentage difference
                percent_diff = (rate_diff / yesterday_rate.exchange_rate) * 100

                differences.append({
                    'currency_code': today_rate.currency_code,
                    'currency_name': today_rate.currency_name,
                    'today_rate': today_rate.exchange_rate,
                    'yesterday_rate': yesterday_rate.exchange_rate,
                    'difference': round(percent_diff, 2)  # Rounded to 2 decimal places
                })
            except CurrencyRate.DoesNotExist:
                continue  

        return Response(differences, status=status.HTTP_200_OK)