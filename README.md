# Установка и запуск приложения

### 1. Клонирование репозитория
  - git clone https://github.com/typicalstandard/cash_registe.git
  - cd cash_registe

### 2. Установка виртуального окружения
  - python -m venv myenv
  - myenv\Scripts\activate  

### 3. Установка зависимостей
  - pip install -r requirements.txt

### 4. Настройка базы данных
  - python manage.py makemigrations
  -python manage.py migrate

### 5. Настройка внешних инструментов
 - Скачайте и установите wkhtmltopdf:
  https://wkhtmltopdf.org/

### 7. Запуск локального серв
  - python manage.py runserver
