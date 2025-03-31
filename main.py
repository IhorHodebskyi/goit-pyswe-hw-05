import sys
import asyncio
import aiohttp
from datetime import datetime, timedelta


class PrivatBankAPI:
    BASE_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date={date}"

    async def fetch_exchange_rate(self, session, date: str):
        url = self.BASE_URL.format(date=date)
        try:
            async with session.get(url) as response:
                data = await response.json()
                return self.parse_exchange_rate(data, date)
        except aiohttp.ClientError as error:
            print(f"Error: {error}")
            return None
        
    @staticmethod
    def parse_exchange_rate(data, date: str):
        rates = {currency['currency']: {'sale': currency['saleRate'], 'purchase': currency['purchaseRate']}
                 for currency in data.get('exchangeRate', [])
                 if currency['currency'] in ['EUR', 'USD']}
        return {date: rates} if rates else None


class CurrencyFetcher:
    def __init__(self, days: int = 10):
        self.days = min(days, 10)
        self.api = PrivatBankAPI()
        
    async def fetch_rates(self):
        tasks: list = []
        async with aiohttp.ClientSession() as session:
            for i in range(self.days):
                date = (datetime.now() - timedelta(days=i)).strftime('%d.%m.%Y')
                tasks.append(self.api.fetch_exchange_rate(session, date))

            results = await asyncio.gather(*tasks)
        return [result for result in results if result] 


async def main():

    fetcher = CurrencyFetcher()
    rates = await fetcher.fetch_rates()
    print(f"{rates}")


if __name__ == "__main__":
  
    asyncio.run(main())