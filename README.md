# 🍞 Bake with Love - Bakery Website

A full-stack bakery e-commerce website built with Django, PostgreSQL, and Docker.

![Bakery Website](https://img.shields.io/badge/Django-4.2-green) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue) ![Docker](https://img.shields.io/badge/Docker-Ready-blue)

## Features

### 🛒 Customer Features
- Browse products by categories (Cakes, Cookies, Breads, etc.)
- Add products to cart
- Place orders with delivery address
- View order history in dashboard
- User registration and authentication

### 👨‍💼 Admin Features
- Dashboard with analytics (revenue, orders, users)
- Product management (CRUD)
- Category management
- Order management with status updates
- User management
- Contact message management

## Tech Stack

- **Backend**: Django 4.2, Python 3.11
- **Database**: PostgreSQL 15
- **Frontend**: HTML5, CSS3, JavaScript
- **Containerization**: Docker, Docker Compose
- **Web Server**: Nginx, Gunicorn

## Quick Start

### Prerequisites
- Docker and Docker Compose installed

### 1. Clone the repository
```bash
git clone <repository-url>
cd "bake with love"
```

### 2. Create environment file
```bash
cp .env.example .env
```

### 3. Build and run with Docker
```bash
docker-compose up --build
```

### 4. Create a superuser (admin)
```bash
docker-compose exec web python manage.py createsuperuser
```

### 5. Access the application
- **Website**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin-panel/
- **Django Admin**: http://localhost:8000/django-admin/

## Project Structure

```
bake with love/
├── bakery_project/     # Django settings
├── core/               # Products, cart, orders
├── accounts/           # User authentication
├── dashboard/          # User dashboard
├── admin_panel/        # Admin dashboard
├── templates/          # HTML templates
├── static/             # CSS, JS, images
├── nginx/              # Nginx configuration
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Development

### Run without Docker
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## Default Credentials

After creating a superuser, mark them as admin:
```bash
docker-compose exec web python manage.py shell
>>> from accounts.models import CustomUser
>>> user = CustomUser.objects.get(email='your@email.com')
>>> user.is_admin_user = True
>>> user.save()
```

## License

MIT License - Feel free to use this project for learning and development.

---

Made with ❤️ for bakery lovers
