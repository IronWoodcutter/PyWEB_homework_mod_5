import aiohttp
import asyncio
import json
import platform
import sys

from datetime import datetime, timedelta


BASE_CURRENCIES = ['EUR', 'USD']
# OPTIONAL_CURRENCIES = ['CHF', 'GBP', 'PLZ', 'SEK', 'XAU', 'CAD']


class HttpError(Exception):
    pass


async def request(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result
                else:
                    raise HttpError(f"Error status: {resp.status} for {url}")
        except (aiohttp.ClientConnectorError, aiohttp.InvalidURL) as err:
            raise HttpError(f'Connection error: {url}', str(err))


async def get_currency(day):
    d = datetime.now() - timedelta(days=int(day))
    shift = d.strftime('%d.%m.%Y')
    try:
        response = await request(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={shift}')
        return response
    except HttpError as err:
        print(err)
        return None


async def main(index_day):
    list_currency = []
    for day in range(int(index_day)):
        info = await get_currency(day)
        currency_data = {}
        currency_info = {}
        for rate in info['exchangeRate']:
            if rate['currency'] in BASE_CURRENCIES:
                currency_info['sale'] = rate['saleRateNB']
                currency_info['purchase'] = rate['purchaseRateNB']
                currency_data[rate['currency']] = currency_info
        list_currency.append({info['date']: currency_data})

    return list_currency


if __name__ == '__main__':
    if int(sys.argv[1]) <= 10:
        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        r = asyncio.run(main(sys.argv[1]))
        with open('result.json', 'w', encoding='utf-8') as fd:
            json.dump(r, fd, ensure_ascii=False, indent=2)
        with open('result.json') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                print(line, end='')
    else:
        print("Unfortunately, the archive is only 10 days old, please enter a smaller number of days")
