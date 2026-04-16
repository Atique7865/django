# Django User Management Application

This project is a simple three-tier Django application with:

- **Presentation tier:** Django templates, views, and static CSS
- **Business tier:** a service layer in `users/services.py`
- **Data tier:** Django ORM with the built-in `User` model and SQLite

It includes:

- A login page
- A dashboard with user statistics
- User list, detail, create, update, and delete screens
- Django admin access
- Docker support with Nginx serving static files

## 1. Run locally with a virtual environment

### Prerequisites

- Python 3.14 or later
- `pip`

### Step-by-step setup

1. Open a terminal in the project folder:

   ```powershell
   cd C:\projects\django
   ```

2. Create a virtual environment:

   ```powershell
   python -m venv .venv
   ```

3. Activate the virtual environment:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

4. Install the dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

5. Run the database migrations:

   ```powershell
   python manage.py migrate
   ```

6. Create an admin user:

   ```powershell
   python manage.py createsuperuser
   ```

   Enter the username, email, and password when prompted.

7. Start the development server:

   ```powershell
   python manage.py runserver
   ```

8. Open the application in your browser:

   - Main UI: `http://127.0.0.1:8000/`
   - Admin panel: `http://127.0.0.1:8000/admin/`

## 2. How to go to the admin panel

1. Make sure the local server is running:

   ```powershell
   python manage.py runserver
   ```

2. Open this URL in the browser:

   ```text
   http://127.0.0.1:8000/admin/
   ```

3. Log in with the superuser account you created using:

   ```powershell
   python manage.py createsuperuser
   ```

4. After login, you can manage users, groups, and all Django admin features from the admin site.

## 3. Local application usage

1. Go to `http://127.0.0.1:8000/`
2. Sign in with a **staff** or **superuser** account
3. Use the dashboard and the **Users** menu to:
   - list users
   - search users
   - create users
   - edit users
   - delete users

## 4. Project structure

```text
django/
|-- config/
|-- docker/
|-- nginx/
|-- static/
|-- templates/
|-- users/
|-- Dockerfile
|-- docker-compose.yml
|-- manage.py
|-- README.md
|-- requirements.txt
```

## 5. Dockerize and run locally with Nginx

This setup uses:

- **web** container: Django + Gunicorn
- **nginx** container: reverse proxy + static file server

### Prerequisites

- Docker Desktop
- Docker Compose

### Step-by-step Docker run

1. Open a terminal in the project folder:

   ```powershell
   cd C:\projects\django
   ```

2. Build the containers:

   ```powershell
   docker compose build
   ```

3. Start the application:

   ```powershell
   docker compose up
   ```

4. Open the application in the browser:

   - Main UI: `http://localhost:8080/`
   - Admin panel: `http://localhost:8080/admin/`

### Create the admin user inside Docker

Open a new terminal in the same folder and run:

```powershell
docker compose exec web python manage.py createsuperuser
```

Then log in at:

```text
http://localhost:8080/admin/
```

### Run in detached mode

```powershell
docker compose up -d
```

### Stop the containers

```powershell
docker compose down
```

### Remove containers and volumes

```powershell
docker compose down -v
```

## 6. How static files are served in Docker

1. The `web` container runs:
   - `python manage.py migrate`
   - `python manage.py collectstatic --noinput`
   - `gunicorn config.wsgi:application --bind 0.0.0.0:8000`

2. Static files are collected into `/app/staticfiles`

3. Docker shares those files with the Nginx container through the `static_volume` volume

4. Nginx serves `/static/` directly and proxies all other requests to Django

## 7. Useful commands

### Run tests

```powershell
python manage.py test
```

### Run Django system checks

```powershell
python manage.py check
```

### Collect static files locally

```powershell
python manage.py collectstatic --noinput
```
