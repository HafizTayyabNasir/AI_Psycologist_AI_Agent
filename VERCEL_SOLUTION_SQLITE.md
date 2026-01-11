# Solution: SQLite Database Issue on Vercel

## Most Likely Issue: SQLite Won't Work on Vercel

Vercel's serverless filesystem is **read-only**, so SQLite cannot create or write to `db.sqlite3`.

## Solution Options:

### Option 1: Use PostgreSQL (Recommended)

1. **Add Vercel Postgres:**
   - Go to Vercel Dashboard → Your Project → Storage
   - Click "Create Database" → Choose "Postgres"
   - This will create a PostgreSQL database

2. **Get Connection String:**
   - Copy the `POSTGRES_URL` environment variable
   - It will be automatically added to your environment variables

3. **Update `elvion_project/settings.py`:**

Replace the DATABASES section with:

```python
import os

if 'POSTGRES_URL' in os.environ:
    # Vercel Postgres
    import psycopg2
    from urllib.parse import urlparse
    
    url = urlparse(os.environ['POSTGRES_URL'])
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': url.path[1:],
            'USER': url.username,
            'PASSWORD': url.password,
            'HOST': url.hostname,
            'PORT': url.port,
        }
    }
else:
    # Local development (SQLite)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

4. **Add to `requirements.txt`:**
```
psycopg2-binary>=2.9.0
```

5. **Run Migrations:**
   - After deploying, run migrations on Vercel
   - Or use Vercel CLI: `vercel env pull` then `python manage.py migrate`

### Option 2: Use Supabase (Free PostgreSQL)

1. Create a free Supabase account
2. Create a new project
3. Get the connection string
4. Add it as `DATABASE_URL` environment variable
5. Update settings.py to use it

### Option 3: Temporarily Disable Database (Testing Only)

If you just want to test if the deployment works:

1. Comment out database-related apps in `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # "django.contrib.admin",
    # "django.contrib.auth",
    # "django.contrib.contenttypes",
    # "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'website.apps.WebsiteConfig',
    'chatbot.apps.ChatbotConfig',
]
```

2. Comment out database middleware:
```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    # "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

⚠️ **This is only for testing** - Your app won't work properly without a database.

## Recommended Action:

**Use Option 1 (Vercel Postgres)** - It's the best solution for Django on Vercel.

