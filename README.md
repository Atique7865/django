# Django User Management Application

This repository contains a simple Django user management application backed by PostgreSQL. It includes:

- login and logout
- a dashboard with user statistics
- list, search, create, update, and delete screens for Django auth users
- Docker packaging with Gunicorn, PostgreSQL, and Nginx
- example Kubernetes manifests for deploying the stack

## 1. Project structure

```text
django/
|-- config/
|-- docker/
|-- k8s/
|-- nginx/
|-- static/
|-- templates/
|-- users/
|-- .env.example
|-- Dockerfile
|-- docker-compose.yml
|-- manage.py
|-- README.md
|-- requirements.txt
```

## 2. How the application works

1. Django uses the built-in `User` model from `django.contrib.auth`.
2. The `users` app adds forms, a service layer, templates, and views for CRUD operations.
3. PostgreSQL is the main database for local, Docker, and Kubernetes deployments.
4. Gunicorn serves the Django app in containers.
5. Nginx sits in front of Django in the Docker deployment and serves `/static/` directly.

## 3. Run locally with PostgreSQL

### Prerequisites

- Python 3.12 or later
- PostgreSQL 16 or later
- `pip`

### Step 1: create a PostgreSQL database and user

Open `psql` with an admin account and run:

```sql
CREATE DATABASE user_management;
CREATE USER user_management WITH PASSWORD 'manik@123';
GRANT ALL PRIVILEGES ON DATABASE user_management TO user_management;
```

### Step 2: create and activate a virtual environment

```powershell
cd C:\projects\django
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: install dependencies

```powershell
pip install -r requirements.txt
```

### Step 4: set environment variables

```powershell
$env:DJANGO_SECRET_KEY = "dev-secret-key"
$env:DJANGO_DEBUG = "True"
$env:DJANGO_ALLOWED_HOSTS = "127.0.0.1,localhost"
$env:POSTGRES_DB = "user_management"
$env:POSTGRES_USER = "user_management"
$env:POSTGRES_PASSWORD = "manik@123"
$env:POSTGRES_HOST = "localhost"
$env:POSTGRES_PORT = "5432"
```

### Step 5: run migrations

```powershell
python manage.py migrate
```

### Step 6: create a superuser

```powershell
python manage.py createsuperuser
```

Use a staff or superuser account to access the UI.

### Step 7: start the development server

```powershell
python manage.py runserver
```

### Step 8: open the application

- App: `http://127.0.0.1:8000/`
- Admin: `http://127.0.0.1:8000/admin/`

## 4. Production-style Dockerization with Nginx

This project already includes the files needed for a production-style container layout:

- `Dockerfile` builds the Django + Gunicorn image
- `docker/entrypoint.sh` waits for PostgreSQL, runs migrations, and collects static files
- `nginx/default.conf` proxies requests to Django and serves static files

### Step 1: build the application image

```powershell
docker build -t django-user-management:latest .
```

### Step 2: create a Docker network and volumes

```powershell
docker network create user-management-net
docker volume create postgres_data
docker volume create static_volume
```

### Step 3: run PostgreSQL

```powershell
docker run -d `
  --name user-management-db `
  --network user-management-net `
  -e POSTGRES_DB=user_management `
  -e POSTGRES_USER=user_management `
  -e POSTGRES_PASSWORD=manik@123 `
  -v postgres_data:/var/lib/postgresql/data `
  postgres:16-alpine
```

### Step 4: run the Django application

```powershell
docker run -d `
  --name user-management-web `
  --network user-management-net `
  -e DJANGO_SECRET_KEY=change-me `
  -e DJANGO_DEBUG=False `
  -e DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1 `
  -e DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:8080 `
  -e POSTGRES_DB=user_management `
  -e POSTGRES_USER=user_management `
  -e POSTGRES_PASSWORD=manik@123 `
  -e POSTGRES_HOST=user-management-db `
  -e POSTGRES_PORT=5432 `
  -v static_volume:/app/staticfiles `
  django-user-management:latest
```

### Step 5: run Nginx

```powershell
docker run -d `
  --name user-management-nginx `
  --network user-management-net `
  -p 8080:80 `
  -v static_volume:/vol/static:ro `
  -v ${PWD}\nginx\default.conf:/etc/nginx/conf.d/default.conf:ro `
  nginx:1.27-alpine
```

### Step 6: create the first admin user

```powershell
docker exec -it user-management-web python manage.py createsuperuser
```

### Step 7: access the application

- App: `http://localhost:8080/`
- Admin: `http://localhost:8080/admin/`

## 5. Run with Docker Compose

### Step 1: create the environment file

```powershell
Copy-Item .env.example .env
```

Edit `.env` and replace the secret values before using it outside local development.

### Step 2: build and start the stack

```powershell
docker compose up --build -d
```

This starts:

- `db`: PostgreSQL
- `web`: Django + Gunicorn
- `nginx`: reverse proxy and static file server

### Step 3: create a superuser

```powershell
docker compose exec web python manage.py createsuperuser
```

### Step 4: open the app

- App: `http://localhost:8080/`
- Admin: `http://localhost:8080/admin/`

### Step 5: useful Docker Compose commands

Start logs:

```powershell
docker compose logs -f
```

Stop the stack:

```powershell
docker compose down
```

Stop and remove the database volume too:

```powershell
docker compose down -v
```

## 6. How to write and use the Kubernetes YAML manifests

The `k8s/` folder contains working starter manifests:

- `namespace.yaml`
- `postgres-secret.yaml`
- `postgres-pvc.yaml`
- `postgres-deployment.yaml`
- `postgres-service.yaml`
- `django-secret.yaml`
- `django-configmap.yaml`
- `django-deployment.yaml`
- `django-service.yaml`
- `ingress.yaml`

### Step 1: build and push the Docker image

Replace `your-registry` with your registry name:

```powershell
docker build -t your-registry/django-user-management:latest .
docker push your-registry/django-user-management:latest
```

### Step 2: update the Kubernetes manifests

1. Open `k8s\django-deployment.yaml` and replace `your-registry/django-user-management:latest` with your real image.
2. Open `k8s\django-secret.yaml` and set a strong `DJANGO_SECRET_KEY`.
3. Open `k8s\postgres-secret.yaml` and set a real PostgreSQL password.
4. Open `k8s\django-configmap.yaml` and replace `user-management.example.com` with your real domain.
5. If needed, change the storage size in `k8s\postgres-pvc.yaml`.

### Step 3: apply the manifests

```powershell
kubectl apply -f k8s\namespace.yaml
kubectl apply -f k8s\postgres-secret.yaml
kubectl apply -f k8s\postgres-pvc.yaml
kubectl apply -f k8s\postgres-deployment.yaml
kubectl apply -f k8s\postgres-service.yaml
kubectl apply -f k8s\django-secret.yaml
kubectl apply -f k8s\django-configmap.yaml
kubectl apply -f k8s\django-deployment.yaml
kubectl apply -f k8s\django-service.yaml
kubectl apply -f k8s\ingress.yaml
```

### Step 4: verify the deployment

```powershell
kubectl get pods -n user-management
kubectl get svc -n user-management
kubectl get ingress -n user-management
```

### Step 5: create the first admin user in Kubernetes

Get the Django pod name:

```powershell
kubectl get pods -n user-management
```

Then run:

```powershell
kubectl exec -it <django-pod-name> -n user-management -- python manage.py createsuperuser
```

### Step 6: point your domain to the ingress controller

1. Install an Nginx ingress controller in the cluster if one is not already installed.
2. Point your DNS record to the ingress controller public IP or load balancer.
3. Visit `https://user-management.example.com` after the DNS and ingress are ready.

## 7. What each Kubernetes manifest does

1. `namespace.yaml` creates an isolated namespace.
2. `postgres-secret.yaml` stores database credentials.
3. `postgres-pvc.yaml` reserves persistent storage for PostgreSQL.
4. `postgres-deployment.yaml` runs PostgreSQL.
5. `postgres-service.yaml` exposes PostgreSQL internally.
6. `django-secret.yaml` stores the Django secret key and database password.
7. `django-configmap.yaml` stores non-secret Django and PostgreSQL settings.
8. `django-deployment.yaml` runs the application container.
9. `django-service.yaml` exposes Django internally to the ingress.
10. `ingress.yaml` publishes the application externally through ingress-nginx.

## 8. Local validation commands

Run tests:

```powershell
$env:DJANGO_USE_SQLITE = "True"
python manage.py test
```

Run Django checks:

```powershell
$env:DJANGO_USE_SQLITE = "True"
python manage.py check
```
