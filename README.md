# Steam Games API

A RESTful API built with Django REST Framework (DRF) and MySQL to browse, manage, and analyze Steam game data. Developed for **XJCO3011 Coursework 1**.

## Features

- **Full CRUD Operations**: Browse, create, update, and delete games and user reviews.
- **Advanced Analytics**: Dedicated endpoints for data analysis (e.g., genre breakdown, release trends, developer leaderboards, and price distribution).
- **Authentication & Authorization**: JWT-based authentication via `rest_framework_simplejwt`.
- **Search, Filter, and Order**: Powered by `django-filter` and DRF's built-in backends.
- **Interactive Documentation**: Auto-generated Swagger UI and ReDoc via `drf-spectacular`.
- **Robust Testing**: Comprehensive unit and integration test suite covering models, serializers, CRUD, and analytics.

## Technology Stack

- **Backend Framework**: Django 5.x + Django REST Framework (DRF)
- **Database**: MySQL 8.x
- **Authentication**: JWT (JSON Web Tokens)
- **Documentation**: drf-spectacular (OpenAPI 3.0)
- **Dataset**: [Kaggle Steam Store Games Dataset](https://www.kaggle.com/datasets/nikdavis/steam-store-games)

## Installation & Setup

### 1. Prerequisites
- Python 3.11+
- MySQL Server 8.x

### 2. Clone the Repository
```bash
git clone <your-repository-url>
cd steam_api
```

### 3. Create Virtual Environment & Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Configure MySQL Database
Log into MySQL and create the database and user:
```sql
CREATE DATABASE steam_games_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'steamapi'@'localhost' IDENTIFIED BY 'SteamAPI2026x';
GRANT ALL PRIVILEGES ON steam_games_db.* TO 'steamapi'@'localhost';
GRANT ALL PRIVILEGES ON test_steam_games_db.* TO 'steamapi'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Import the Dataset
The project includes a custom management command to parse and import the Kaggle CSV dataset:
```bash
python manage.py import_steam_data --path data/steam.csv
```

### 7. Run the Server
```bash
python manage.py runserver
```

## API Documentation

Once the server is running, you can explore the API endpoints interactively:

- **Swagger UI**: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **ReDoc**: [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)
- **Raw OpenAPI Schema**: [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)

## Testing

Run the test suite to ensure everything is working correctly:
```bash
python manage.py test games --verbosity=2
```

## Acknowledgements

This project uses the Steam Store Games dataset provided by Nik Davis on Kaggle.
