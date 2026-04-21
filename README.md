# Steam Games API

A RESTful API for browsing, managing, and analysing Steam game data. Built with Django REST Framework and MySQL.

## Technology Stack

| Layer | Technology |
|---|---|
| Backend Framework | Django 5.x + Django REST Framework |
| Database | MySQL 8.x |
| Authentication | JWT via `djangorestframework-simplejwt` |
| Documentation | drf-spectacular (OpenAPI 3.0 / Swagger) |
| Dataset | [Kaggle Steam Store Games](https://www.kaggle.com/datasets/nikdavis/steam-store-games) |

## API Documentation

The full API documentation (all endpoints, parameters, response schemas, authentication, and error codes) is available in **`API_Documentation.pdf`** in the root of this repository.

When running locally, interactive documentation is also available at:
- **Swagger UI**: `http://127.0.0.1:8000/api/docs/`
- **ReDoc**: `http://127.0.0.1:8000/api/redoc/`

## API Endpoints Overview

All endpoints are prefixed with `/api/v1/`.

### Authentication

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| POST | `/auth/register/` | No | Register a new user account |
| POST | `/auth/token/` | No | Obtain JWT access and refresh tokens |
| POST | `/auth/token/refresh/` | No | Refresh an expired access token |
| POST | `/auth/token/verify/` | No | Verify a token is valid |
| GET / PUT | `/auth/profile/` | Yes | View or update the current user's profile |

### Games

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| GET | `/games/` | No | List all games (supports search, filter, ordering) |
| POST | `/games/` | Admin only | Create a new game entry |
| GET | `/games/{id}/` | No | Retrieve a single game by ID |
| PUT / PATCH | `/games/{id}/` | Admin only | Update a game entry |
| DELETE | `/games/{id}/` | Admin only | Delete a game entry |
| GET | `/games/{id}/similar/` | No | Get games similar to the specified game |

### Analytics

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| GET | `/games/stats/` | No | Overall dataset statistics (total games, avg price, etc.) |
| GET | `/games/genre_breakdown/` | No | Game count broken down by genre |
| GET | `/games/top_rated/` | No | Top-rated games by positive review ratio |
| GET | `/games/release_trend/` | No | Number of game releases per year |
| GET | `/games/price_distribution/` | No | Distribution of games across price ranges |
| GET | `/games/platform_stats/` | No | Breakdown of Windows / Mac / Linux support |
| GET | `/games/developer_leaderboard/` | No | Top developers by number of published games |

### Reviews

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| GET | `/reviews/` | No | List all reviews |
| POST | `/reviews/` | Yes | Submit a review for a game |
| GET | `/reviews/{id}/` | No | Retrieve a single review |
| PUT / PATCH | `/reviews/{id}/` | Owner only | Update your own review |
| DELETE | `/reviews/{id}/` | Owner only | Delete your own review |

## Local Setup

### Prerequisites
- Python 3.11+
- MySQL Server 8.x

### Steps

```bash
# 1. Clone the repository
git clone <your-repository-url>
cd steam_api

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

Log into MySQL and create the database:

```sql
CREATE DATABASE steam_games_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'steamapi'@'localhost' IDENTIFIED BY 'SteamAPI2026x';
GRANT ALL PRIVILEGES ON steam_games_db.* TO 'steamapi'@'localhost';
GRANT ALL PRIVILEGES ON test_steam_games_db.* TO 'steamapi'@'localhost';
FLUSH PRIVILEGES;
```

```bash
# 4. Run migrations and import dataset
python manage.py migrate
python manage.py import_steam_data --path data/steam.csv

# 5. Create an admin user
python manage.py createsuperuser

# 6. Start the development server
python manage.py runserver
```

## Testing

The project includes 49 tests covering CRUD operations, authentication, permissions, and analytics endpoints.

```bash
python manage.py test games --verbosity=2
```

## Deployment

This API is deployed on PythonAnywhere and accessible at:
`https://<username>.pythonanywhere.com/api/v1/`

## Acknowledgements

Dataset provided by Nik Davis on [Kaggle](https://www.kaggle.com/datasets/nikdavis/steam-store-games).
