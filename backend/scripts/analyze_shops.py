#!/usr/bin/env python3
import sys
import json

shops = json.load(sys.stdin)
print(f'Всего магазинов на production: {len(shops)}\n')

# По городам
print('По городам:')
cities = {}
for s in shops:
    city = s.get('city') or 'Не указан'
    cities[city] = cities.get(city, 0) + 1
for city, count in sorted(cities.items()):
    print(f'  {city}: {count}')

# Магазины с уникальными названиями
print('\n🏪 Магазины с уникальными названиями:')
unique = [s for s in shops if s['name'] != 'Мой магазин']
for s in unique:
    city = s.get('city') or 'город не указан'
    status = '🟢' if s['is_open'] else '🔴'
    print(f'  {status} ID {s["id"]}: {s["name"]} ({city}) - {s["phone"]}')

# Статус открытия
print(f'\n📊 Статистика:')
default_names = len([s for s in shops if s['name'] == 'Мой магазин'])
print(f'  Начали регистрацию (название по умолчанию): {default_names}')
print(f'  Завершили настройку (уникальное название): {len(unique)}')
print(f'  Открытых магазинов (is_open=true): {len([s for s in shops if s["is_open"]])}')
