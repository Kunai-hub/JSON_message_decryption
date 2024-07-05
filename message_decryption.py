# -*- coding: utf-8 -*-

import csv
import json
import re
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, ROUND_HALF_EVEN
from pprint import pprint

# Шифр:
# - дата: "jbdDDMMYY"
# - город: "jbcCITYNAMEjbc"
# - сумма потраченных за день денег в местной валюте: "jbeFLOATjbe" (местная валюта - фунты)


re_date = r'jbd(\d{6})'
re_city = r'jbc(\w+)jbc'
re_money = r'jbe(\d+\.\d+)jbe'

with open('secret_message.json', mode='r') as file_with_messages:
    messages = json.load(file_with_messages)

cities = set()
for message in messages.values():
    city = re.search(re_city, message)[1]
    cities.add(city)

exchange_rates = {
    'берлин': Decimal(0.84),
    'лондон': Decimal(1.0),
    'токио': Decimal(0.005),
    'москва': Decimal(0.0091)
}


def str_date_to_datetime(str_date):
    """
    Перевод из строчной даты в класс datetime в формате "DDMMYY"

    :param str_date: строчная дата в формате "DDMMYY"
    :return: дата datetime в формате "DDMMYY"
    """
    return datetime.strptime(str_date, '%d%m%y')


def str_money_to_decimal(str_money, city):
    """
    Перевод из строчной суммы потраченных денег в класс Decimal с учетом курса валюты страны

    :param str_money: строчная сумма потраченных денег
    :param city: город, в валюту которого нужно перевести сумму
    :return: сумма потраченных денег Decimal в фунтах
    """
    return Decimal(str_money) * exchange_rates[city]


result = []
for num_message, message in messages.items():
    str_date = re.search(re_date, message)[1]
    city = re.search(re_city, message)[1]
    str_money = re.search(re_money, message)[1]

    result.append(
        {
            'date': str_date_to_datetime(str_date),
            'city': city,
            'expenses': str_money_to_decimal(str_money, city)
        }
    )

sorted_result = sorted(result, key=lambda x: x['date'])

formatted_result = [
    {
        'date': res['date'].strftime('%d.%m.%Y'),
        'city': res['city'],
        'expenses': str(res['expenses'].quantize(Decimal('1.00'), ROUND_HALF_EVEN))
    }
    for res in sorted_result
]

with open('decrypted_messages.csv', mode='w', newline='', encoding='utf8') as out_file:
    writer = csv.DictWriter(out_file, fieldnames=['date', 'city', 'expenses'])
    writer.writeheader()
    writer.writerows(formatted_result)


# =====================================================================================================================


aggregated_result = defaultdict(lambda: {'date': '', 'cities': set(), 'expenses_sum': Decimal(0), 'date_for_sort': ''})

for res in sorted_result:
    month_datetime = datetime(year=res['date'].year, month=res['date'].month, day=1)
    month = month_datetime.strftime('%m.%Y')
    aggregated_result[month]['date'] = month
    aggregated_result[month]['cities'].add(res['city'])
    aggregated_result[month]['expenses_sum'] += res['expenses']
    aggregated_result[month]['date_for_sort'] = month_datetime

sorted_aggregated_result = sorted(aggregated_result.values(), key=lambda x: x['date_for_sort'])

formatted_aggregated_result = [
    {
        'date': res['date'],
        'cities': ', '.join(res['cities']),
        'expenses_sum': str(res['expenses_sum'].quantize(Decimal('1.00'), ROUND_HALF_EVEN))
    }
    for res in sorted_aggregated_result
]

with open('decrypted_messages_aggregated.csv', mode='w', newline='', encoding='utf8') as out_file_aggregated:
    writer_aggregated = csv.DictWriter(out_file_aggregated, fieldnames=['date', 'cities', 'expenses_sum'])
    writer_aggregated.writeheader()
    writer_aggregated.writerows(formatted_aggregated_result)
