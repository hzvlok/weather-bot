import telebot
from telebot import types
import requests

# Токены (получи их перед запуском)
TELEGRAM_TOKEN = "8138541419:AAEYnArKvkRkgdL908MSOgz4an4rhGGs_hU"  # Получи у @BotFather
WEATHER_API_KEY = "4c7a54327100a7663cb8cd417ff1abeb"    # Получи на openweathermap.org

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Эмодзи для красоты
WEATHER_EMOJI = {
    'clear sky': '☀️',
    'few clouds': '🌤',
    'scattered clouds': '⛅',
    'broken clouds': '☁️',
    'shower rain': '🌧',
    'rain': '🌧',
    'thunderstorm': '⛈',
    'snow': '❄️',
    'mist': '🌫',
}

def get_weather_emoji(description):
    """Получить эмодзи для описания погоды"""
    description_lower = description.lower()
    for key, emoji in WEATHER_EMOJI.items():
        if key in description_lower:
            return emoji
    return '🌍'

def get_weather_data(city):
    """Получить данные о погоде для города"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': WEATHER_API_KEY,
            'units': 'metric',
            'lang': 'ru'
        }
        
        print(f"🔍 Запрос погоды для города: {city}")
        print(f"🔑 API ключ (первые 10 символов): {WEATHER_API_KEY[:10]}...")
        
        response = requests.get(url, params=params, timeout=10)
        
        print(f"📡 Код ответа: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Данные получены успешно!")
            return response.json()
        elif response.status_code == 404:
            print("❌ Город не найден")
            return None
        elif response.status_code == 401:
            print("❌ Неверный API ключ!")
            print(f"Ответ сервера: {response.text}")
            return "INVALID_KEY"
        else:
            print(f"❌ Ошибка API: {response.status_code}")
            print(f"Ответ сервера: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Превышено время ожидания")
        return "TIMEOUT"
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка соединения с интернетом")
        return "NO_INTERNET"
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

def format_weather_message(data):
    """Форматировать сообщение с погодой"""
    temp = round(data['main']['temp'])
    feels_like = round(data['main']['feels_like'])
    description = data['weather'][0]['description'].capitalize()
    city_name = data['name']
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']
    pressure = data['main']['pressure']
    
    emoji = get_weather_emoji(data['weather'][0]['description'])
    
    message = f"""
{emoji} <b>{city_name}</b>

🌡 Температура: <b>{temp}°C</b>
🤔 Ощущается как: {feels_like}°C
📝 {description}

💧 Влажность: {humidity}%
💨 Ветер: {wind_speed} м/с
🔽 Давление: {pressure} гПа
"""
    
    return message

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Приветственное сообщение"""
    welcome_text = """
👋 Привет! Я бот для получения информации о погоде.

Просто отправь мне название города, и я покажу текущую погоду!

Примеры:
• Одесса
• London
• New York

Команды:
/start - Показать это сообщение
/help - Помощь
/test - Проверить настройки
"""
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['test'])
def test_settings(message):
    """Проверка настроек бота"""
    test_msg = "🔧 Проверка настроек:\n\n"
    
    # Проверка токена бота
    if TELEGRAM_TOKEN != "YOUR_TELEGRAM_BOT_TOKEN":
        test_msg += "✅ Telegram токен: Установлен\n"
    else:
        test_msg += "❌ Telegram токен: НЕ установлен\n"
    
    # Проверка API ключа
    if WEATHER_API_KEY != "YOUR_WEATHER_API_KEY":
        test_msg += f"✅ Weather API ключ: Установлен\n"
        test_msg += f"   Первые 10 символов: {WEATHER_API_KEY[:10]}...\n\n"
    else:
        test_msg += "❌ Weather API ключ: НЕ установлен\n\n"
    
    test_msg += "Сейчас проверю подключение к API погоды...\n"
    
    bot.reply_to(message, test_msg)
    
    # Тестовый запрос
    status_msg = bot.send_message(message.chat.id, "⏳ Тестирую API...")
    weather_data = get_weather_data("London")
    
    if weather_data == "INVALID_KEY":
        bot.edit_message_text(
            "❌ API ключ неверный или не активирован!\n\n"
            "Что делать:\n"
            "1. Проверь правильность ключа\n"
            "2. Подожди 10-15 минут после создания\n"
            "3. Убедись что ключ скопирован полностью",
            status_msg.chat.id,
            status_msg.message_id
        )
    elif weather_data == "TIMEOUT":
        bot.edit_message_text(
            "❌ Превышено время ожидания ответа от сервера",
            status_msg.chat.id,
            status_msg.message_id
        )
    elif weather_data == "NO_INTERNET":
        bot.edit_message_text(
            "❌ Нет подключения к интернету",
            status_msg.chat.id,
            status_msg.message_id
        )
    elif weather_data:
        bot.edit_message_text(
            "✅ Всё работает отлично! Можешь отправлять названия городов.",
            status_msg.chat.id,
            status_msg.message_id
        )
    else:
        bot.edit_message_text(
            "❌ Неизвестная ошибка. Проверь консоль для деталей.",
            status_msg.chat.id,
            status_msg.message_id
        )

@bot.message_handler(func=lambda message: True)
def handle_city(message):
    """Обработка названия города"""
    city = message.text.strip()
    
    if not city:
        bot.reply_to(message, "❌ Пожалуйста, введите название города")
        return
    
    # Показываем, что бот работает
    status_msg = bot.reply_to(message, "⏳ Получаю данные о погоде...")
    
    weather_data = get_weather_data(city)
    
    if weather_data is None:
        bot.edit_message_text(
            "❌ Город не найден. Проверьте правильность написания.",
            status_msg.chat.id,
            status_msg.message_id
        )
    elif weather_data == "INVALID_KEY":
        bot.edit_message_text(
            "❌ API ключ неверный или не активирован!\n\n"
            "Проверь:\n"
            "• Ключ скопирован правильно?\n"
            "• Прошло 10-15 минут после создания?\n"
            "• Нет лишних пробелов в коде?",
            status_msg.chat.id,
            status_msg.message_id
        )
    elif weather_data == "TIMEOUT":
        bot.edit_message_text(
            "❌ Превышено время ожидания. Попробуйте позже.",
            status_msg.chat.id,
            status_msg.message_id
        )
    elif weather_data == "NO_INTERNET":
        bot.edit_message_text(
            "❌ Проблема с интернет-соединением.",
            status_msg.chat.id,
            status_msg.message_id
        )
    elif weather_data is False:
        bot.edit_message_text(
            "❌ Не удалось получить данные о погоде.\n"
            "Проверьте консоль для деталей.",
            status_msg.chat.id,
            status_msg.message_id
        )
    else:
        weather_message = format_weather_message(weather_data)
        bot.edit_message_text(
            weather_message,
            status_msg.chat.id,
            status_msg.message_id,
            parse_mode='HTML'
        )

def main():
    """Запуск бота"""
    print("=" * 50)
    print("🤖 Запуск бота погоды...")
    print("=" * 50)
    
    if TELEGRAM_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("❌ ОШИБКА: Укажите токен телеграм-бота!")
        print("Получите токен у @BotFather в Telegram")
        return
    else:
        print(f"✅ Telegram токен установлен")
    
    if WEATHER_API_KEY == "YOUR_WEATHER_API_KEY":
        print("❌ ОШИБКА: Укажите API ключ для погоды!")
        print("Получите ключ на openweathermap.org")
        return
    else:
        print(f"✅ Weather API ключ установлен (первые 10 символов): {WEATHER_API_KEY[:10]}...")
    
    print("\n💡 Отправь боту /test для проверки настроек")
    print("=" * 50)
    print("🚀 Бот запущен и готов к работе!\n")
    
    # Запуск бота
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main()