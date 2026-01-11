"""
Простой анализатор курсов валют
Получает курсы с API ЦБ РФ и анализирует изменения
"""

import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import os
# Все доступные валюты
ALL_CURRENCIES = {
    'USD': 'Доллар США',
    'EUR': 'Евро',
    'CNY': 'Китайский юань',
    'GBP': 'Британский фунт',
    'JPY': 'Японская иена',
    'CHF': 'Швейцарский франк',
    'CAD': 'Канадский доллар',
    'AUD': 'Австралийский доллар',
    'SGD': 'Сингапурский доллар',
    'HKD': 'Гонконгский доллар',
    'NOK': 'Норвежская крона',
    'SEK': 'Шведская крона',
    'TRY': 'Турецкая лира',
    'UAH': 'Украинская гривна',
    'KZT': 'Казахстанский тенге',
    'BYN': 'Белорусский рубль',
    'INR': 'Индийская рупия',
    'BRL': 'Бразильский реал',
    'ZAR': 'Южноафриканский рэнд',
    'KRW': 'Южнокорейская вона'
}
print("="*60)
print("💰 АНАЛИЗАТОР КУРСОВ ВАЛЮТ")
print("="*60)
print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# API для курсов валют (сайт ЦБ РФ)
API_URL = "https://www.cbr-xml-daily.ru/daily_json.js"

def get_exchange_rates():
    """Получает текущие курсы валют"""
    try:
        print("🌐 Получаем текущие курсы валют...")
        response = requests.get(API_URL, timeout=10)
        data = response.json()
        print("✅ Данные успешно получены!")
        return data
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def analyze_currencies(data, selected_currencies=None):
    """Анализирует курсы выбранных валют"""
    if not data or 'Valute' not in data:
        print("❌ Нет данных о валютах")
        return None
    
    if selected_currencies is None:
        selected_currencies = ['USD', 'EUR', 'CNY', 'GBP', 'JPY']
    
    print(f"\n📊 АНАЛИЗ КУРСОВ ВАЛЮТ ({len(selected_currencies)} валют):")
    print("-" * 60)
    
    currencies = []
    available_count = 0
    
    for code in selected_currencies:
        if code in data['Valute']:
            currency = data['Valute'][code]
            available_count += 1
            

            change = currency['Value'] - currency['Previous']
            change_percent = (change / currency['Previous']) * 100 if currency['Previous'] != 0 else 0
            

            if change > 0.01:  # Значительный рост
                recommendation = "📈 СИЛЬНЫЙ РОСТ - ОЧЕНЬ выгодно продавать"
            elif change > 0:
                recommendation = "📈 Рост - выгодно продавать"
            elif change < -0.01:  # Значительное падение
                recommendation = "📉 СИЛЬНОЕ ПАДЕНИЕ - ОЧЕНЬ выгодно покупать"
            elif change < 0:
                recommendation = "📉 Падение - выгодно покупать"
            else:
                recommendation = "➡️ Без изменений"
            
            currency_info = {
                'Код': code,
                'Название': currency['Name'],
                'Курс': round(currency['Value'], 4),
                'Изменение': round(change, 4),
                'Изменение %': round(change_percent, 2),
                'Рекомендация': recommendation,
                'Номинал': currency['Nominal']
            }
            
            currencies.append(currency_info)
            
            print(f"{code} ({currency['Name']}):")
            print(f"  Курс: {currency['Value']:.4f} ₽ за {currency['Nominal']} ед.")
            print(f"  Изменение: {change:+.4f} ₽ ({change_percent:+.2f}%)")
            print(f"  {recommendation}")
            print()
        else:
            print(f"⚠️ Валюта {code} не найдена в данных ЦБ РФ")
    
    print(f"✅ Обработано {available_count} из {len(selected_currencies)} запрошенных валют")
    return currencies
def save_to_csv(currencies, filename="currency_rates.csv"):
    """Сохраняет данные в CSV"""
    if not currencies:
        print("❌ Нет данных для сохранения")
        return None
    
    df = pd.DataFrame(currencies)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"💾 Данные сохранены в {filename}")
    

    df.to_json("currency_rates.json", orient='records', force_ascii=False, indent=2)
    print("💾 Данные также сохранены в currency_rates.json")
    
    return df

def generate_report(df):
    """Генерирует отчёт"""
    print("\n📈 АНАЛИТИЧЕСКИЙ ОТЧЁТ:")
    print("-" * 50)
    

    best_to_buy = df[df['Изменение'] < 0].sort_values('Изменение').head(1)
    if not best_to_buy.empty:
        currency = best_to_buy.iloc[0]
        print(f"💰 Лучшая валюта для ПОКУПКИ: {currency['Код']}")
        print(f"   Курс: {currency['Курс']} ₽")
        print(f"   Изменение: {currency['Изменение']:+.4f} ₽")
        print(f"   Причина: курс упал, можно купить дешевле")
    
    print()
    
    best_to_sell = df[df['Изменение'] > 0].sort_values('Изменение', ascending=False).head(1)
    if not best_to_sell.empty:
        currency = best_to_sell.iloc[0]
        print(f"💰 Лучшая валюта для ПРОДАЖИ: {currency['Код']}")
        print(f"   Курс: {currency['Курс']} ₽")
        print(f"   Изменение: {currency['Изменение']:+.4f} ₽")
        print(f"   Причина: курс вырос, можно продать дороже")
    
    print()
    
    print("📊 ОБЩАЯ СТАТИСТИКА:")
    print(f"   • Средний курс доллара: {df[df['Код'] == 'USD']['Курс'].values[0]} ₽")
    print(f"   • Средний курс евро: {df[df['Код'] == 'EUR']['Курс'].values[0]} ₽")
    print(f"   • Всего отслеживаемых валют: {len(df)}")
    
    report_text = f"""
    ОТЧЁТ ПО КУРСАМ ВАЛЮТ
    ======================
    Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    РЕКОМЕНДАЦИИ:
    1. Для покупки: {best_to_buy['Код'].values[0] if not best_to_buy.empty else 'Нет вариантов'}
    2. Для продажи: {best_to_sell['Код'].values[0] if not best_to_sell.empty else 'Нет вариантов'}
    
    КУРСЫ ВАЛЮТ:
    """
    
    for _, row in df.iterrows():
        report_text += f"\n{row['Код']}: {row['Курс']} ₽ ({row['Изменение']:+.4f} ₽)"
    
    with open('currency_report.txt', 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print("📄 Подробный отчёт сохранён в currency_report.txt")

def main():
    """Основная деф проекта"""
    print("="*60)
    print("💰 РАСШИРЕННЫЙ АНАЛИЗАТОР КУРСОВ ВАЛЮТ")
    print("="*60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("🌍 ДОСТУПНЫЕ ВАЛЮТЫ ДЛЯ АНАЛИЗА:")
    print("-" * 40)
    for i, (code, name) in enumerate(list(ALL_CURRENCIES.items())[:15], 1):
        print(f"{i:2d}. {code} - {name}")
    print(f"... и ещё {len(ALL_CURRENCIES)-15} валют")
    print()
    
    print("🎯 ВЫБЕРИТЕ РЕЖИМ АНАЛИЗА:")
    print("1. Быстрый анализ (5 основных валют)")
    print("2. Расширенный анализ (10 популярных валют)")
    print("3. Полный анализ (все доступные валюты(20))")
    print("4. Выбрать валюты вручную")
    
    try:
        choice = input("\nВаш выбор (1-4): ").strip()
        
        if choice == '1':
            selected = ['USD', 'EUR', 'CNY', 'GBP', 'JPY']
            print("✅ Выбраны 5 основных валют")
        elif choice == '2':
            selected = ['USD', 'EUR', 'GBP', 'CHF', 'JPY', 'CAD', 'AUD', 'CNY', 'SGD', 'HKD']
            print("✅ Выбраны 10 популярных валют")
        elif choice == '3':
            selected = list(ALL_CURRENCIES.keys())
            print(f"✅ Выбраны все {len(selected)} валют")
        elif choice == '4':
            print("\n📝 ВВЕДИТЕ КОДЫ ВАЛЮТ (через запятую):")
            print("Пример: USD, EUR, CNY, GBP, JPY, CHF, CAD")
            user_input = input("Ваши валюты: ").strip().upper()
            selected = [c.strip() for c in user_input.split(',') if c.strip()]
            print(f"✅ Выбраны {len(selected)} валют: {', '.join(selected)}")
        else:
            print("⚠️ Неверный выбор. Используем 5 основных валют.")
            selected = ['USD', 'EUR', 'CNY', 'GBP', 'JPY']
    
    except:
        print("⚠️ Ошибка ввода. Используем 5 основных валют.")
        selected = ['USD', 'EUR', 'CNY', 'GBP', 'JPY']
    
    print("\n🚀 Запуск анализа...")
    
    data = get_exchange_rates()
    
    if not data:
        print("❌ Не удалось получить данные. Проверьте подключение к интернету.")
        return
    
    currencies = analyze_currencies(data, selected)
    
    if not currencies:
        print("❌ Не удалось проанализировать данные")
        return
    
    filename = f"currency_rates_{len(selected)}_currencies.csv"
    df = save_to_csv(currencies, filename)
    
    generate_report(df)
    
    print("\n" + "="*60)
    print("✅ АНАЛИЗ ЗАВЕРШЁН!")
    print("="*60)
    print(f"\n📁 Созданные файлы:")
    print(f"• {filename} - данные по {len(df)} валютам")
    print("• currency_rates.json - данные в JSON")
    print("• currency_report.txt - текстовый отчёт")
    print("\n🎯 Для визуализации запустите Jupyter Notebook")
if __name__ == "__main__":
    main()
