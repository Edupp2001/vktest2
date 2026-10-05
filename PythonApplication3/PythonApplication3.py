import json
import urllib.request
import urllib.parse
import time
import ssl
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class WeatherData:
    city: str
    temperature: int
    country: str


def load_cities(filepath: str) -> list[str]:
    """Читает список городов из файла, убирает дубликаты и пустые строки."""
    cities = []
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                city = line.strip()
                if city and city not in cities:
                    cities.append(city)
    except FileNotFoundError:
        print(f"Ошибка: Файл {filepath} не найден. Проверьте путь.")
    return cities


def fetch_weather(city: str) -> WeatherData | None:
    """Получает данные о погоде через API wttr.in с повторными попытками."""
    encoded_city = urllib.parse.quote(city)
    # Попробуем https, если не выйдет - http
    urls = [
        f"https://wttr.in/{encoded_city}?format=j1",
        f"http://wttr.in/{encoded_city}?format=j1"
    ]
    
    # Игнорируем ошибки SSL, так как на Windows они бывают даже на валидных сайтах
    context = ssl._create_unverified_context()
    
    for url in urls:
        for attempt in range(3): # 3 попытки для каждого протокола
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                # Увеличиваем таймаут до 30 секунд
                with urllib.request.urlopen(req, timeout=30, context=context) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode('utf-8'))
                        
                        temp_c = int(data['current_condition'][0]['temp_C'])
                        country = data['nearest_area'][0]['country'][0]['value']
                        
                        return WeatherData(city=city, temperature=temp_c, country=country)
            except Exception as e:
                print(f"  [Попытка {attempt + 1}/3] Не удалось получить данные для {city} ({url}): {e}")
                time.sleep(2) # Пауза перед следующей попыткой
                
    return None


def main():
    # Обратите внимание на путь: скрипт в папке PythonApplication3, а файл в корне репозитория
    cities_file = '../Cities.txt' 
    cities = load_cities(cities_file)
    
    if not cities:
        print("Список городов пуст или файл не найден.")
        return

    weather_records = []

    print("--- Погода по городам ---")
    for city in cities:
        record = fetch_weather(city)
        if record:
            weather_records.append(record)
            # Формат: Tokyo, Japan +18 °C
            print(f"{record.city}, {record.country} {record.temperature:+d} °C")
        
        # Задержка, чтобы не получить бан от бесплатного API
        time.sleep(2)

    print("\n--- Статистика по странам ---")
    
    country_stats = defaultdict(list)
    for record in weather_records:
        country_stats[record.country].append(record.temperature)

    for country, temps in country_stats.items():
        count = len(temps)
        avg_temp = round(sum(temps) / count)
        min_temp = min(temps)
        max_temp = max(temps)
        
        # Формат: Japan — 3 cities, avg: +19 °C, min: +16 °C, max: +22 °C
        print(f"{country} — {count} cities, avg: {avg_temp:+d} °C, min: {min_temp:+d} °C, max: {max_temp:+d} °C")


if __name__ == "__main__":
    main()