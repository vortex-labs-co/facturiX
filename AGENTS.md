# AGENTS.md

## Descripción del proyecto
Facturix: app web de facturación para Vortex Labs (Colombia). Django 6 + PostgreSQL (Supabase), plantillas + Bootstrap 5.

## Estructura
- `config/` = settings y urls del proyecto
- `core/` = app principal (vistas, urls, comandos)
- `templates/` = plantillas HTML (base.html, registration/login.html, dashboard.html)
- `static/` = archivos estáticos
- `venv/` = entorno virtual

## Comandos
- Activar venv: `.\venv\Scripts\Activate.ps1`
- Migraciones: `python manage.py migrate`
- Servidor: `python manage.py runserver`
- Crear roles: `python manage.py crear_roles`
- Crear admin: `python manage.py createsuperuser`

## Convenciones
- Colores: fondo #0A0C13, azul #00628C, oscuro #004E70, gris #565E74
- Roles: Admin, Contador, Consulta
- `.env` guarda secretos; ver `.env.example`
