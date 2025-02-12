# WishLister Bot 🎁

Telegram бот для создания и управления списками желаний с возможностью анонимного бронирования подарков.

## 🌟 Возможности

- **Управление желаниями**
  - Создание желаний с фото, ценой и ссылкой
  - Просмотр своего списка желаний
  - Отметка исполненных желаний
  - Удаление желаний

- **Социальные функции**
  - Подписка на других пользователей
  - Просмотр списка подписчиков
  - Анонимное бронирование желаний
  - Уведомления о новых желаниях

## 🛠 Технологический стек

- Python 3.11+
- python-telegram-bot 20.0+
- SQLite3
- Docker & Docker Compose
- Poetry (опционально)

## 📋 Требования

- Python 3.11 или выше
- Docker и Docker Compose (для продакшена)
- Токен Telegram бота от @BotFather

## 🚀 Быстрый старт

### Локальная разработка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/wishlister-bot.git
cd wishlister-bot
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/macOS
venv\Scripts\activate     # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` в корневой директории:
```env
BOT_TOKEN=your_telegram_bot_token_here
```

5. Запустите бота:
```bash
python main.py
```

### Запуск через Docker

1. Убедитесь, что Docker и Docker Compose установлены

2. Создайте файл `.env`

3. Запустите контейнер:
```bash
docker-compose up -d --build
```

## 📁 Структура проекта

```
wishlister/
├── database/
│   ├── __init__.py
│   └── db.py              # Работа с базой данных
├── handlers/
│   ├── __init__.py
│   ├── menu.py            # Обработчики меню
│   ├── wishes.py          # Управление желаниями
│   └── subscriptions.py   # Подписки и социальные функции
├── utils/
│   ├── __init__.py
│   ├── keyboards.py       # Клавиатуры и кнопки
│   └── states.py         # Состояния бота
├── .env                   # Конфигурация (не в репозитории)
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── main.py               # Точка входа
├── README.md
└── requirements.txt
```

## 🔧 Конфигурация

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|---------------|
| BOT_TOKEN  | Токен Telegram бота | - |
| DATABASE_PATH | Путь к файлу БД | data/wishlist.db |

## 📝 База данных

### Таблицы

#### users
- user_id (PRIMARY KEY)
- username
- notifications

#### wishes
- id (PRIMARY KEY)
- user_id (FOREIGN KEY)
- title
- price
- link
- photo_id
- date_added
- status
- booked_by

#### subscriptions
- subscriber_id (FOREIGN KEY)
- target_user_id (FOREIGN KEY)

## 🚀 Деплой

### На сервер через Docker

1. Подготовка сервера:
```bash
sudo apt update && sudo apt upgrade -y
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install docker-compose -y
```

2. Настройка проекта:
```bash
mkdir -p /opt/wishlister-bot/data
cd /opt/wishlister-bot
# Скопируйте файлы проекта
# Создайте .env файл
```

3. Запуск:
```bash
docker-compose up -d
```

### Мониторинг

- Логи: `docker-compose logs -f`
- Статус: `docker-compose ps`
- Использование ресурсов: `docker stats`

## 🔄 Обновление

```bash
git pull
docker-compose down
docker-compose up -d --build
```

## 📦 Бэкапы

Настройте регулярное резервное копирование базы данных:

```bash
#!/bin/bash
backup_dir="/path/to/backups"
date=$(date +%Y%m%d_%H%M%S)
cp data/wishlist.db "${backup_dir}/wishlist_${date}.db"
find "${backup_dir}" -name "wishlist_*.db" -mtime +7 -delete
```

## 👥 Участие в разработке

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Отправьте пулл-реквест

## 📄 Лицензия

MIT License. См. файл [LICENSE](LICENSE)

## 📞 Поддержка

- Создайте Issue в репозитории
- Свяжитесь с разработчиком: [@fountainbleu](https://t.me/fountainbleu)
