# Troubleshooting Vercel Deployment

## Common Issues and Solutions

### Error: FUNCTION_INVOCATION_FAILED / 500 INTERNAL_SERVER_ERROR

This error usually occurs due to one of the following issues:

#### 1. Check Vercel Logs
- Go to your Vercel dashboard
- Click on your project
- Go to the "Deployments" tab
- Click on the failed deployment
- Check the "Functions" tab for detailed error logs

#### 2. Common Causes:

**Missing Environment Variables:**
- Ensure `GROQ_API_KEY` is set in Vercel dashboard
- Check `SECRET_KEY` is set (or it will use default)
- Verify `DEBUG` is set to `False` for production
- Set `ALLOWED_HOSTS` to your Vercel domain

**Database Issues:**
- SQLite doesn't work in Vercel serverless (read-only filesystem)
- Consider using Vercel Postgres or another database service
- For testing, you might need to disable database operations temporarily

**Import Errors:**
- Check that all dependencies are in `requirements.txt`
- Verify Python version compatibility
- Check for missing modules in error logs

#### 3. Testing Locally with Vercel CLI

```bash
npm i -g vercel
vercel dev
```

This will help you test the deployment locally and see errors before deploying.

#### 4. Alternative: Use Django-Vercel Package

If the current setup doesn't work, consider using the `django-vercel` package:

1. Add to `requirements.txt`:
   ```
   django-vercel
   ```

2. Update `api/index.py`:
   ```python
   from django_vercel import handler
   ```

3. This package handles the WSGI-to-serverless conversion automatically

#### 5. Check Build Logs

In Vercel dashboard:
- Go to Deployment → Build Logs
- Look for Python import errors
- Check for missing dependencies
- Verify Python version (Vercel uses Python 3.9 by default)

#### 6. Database Configuration

For production, update `settings.py` to use a proper database:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

#### 7. Static Files

If static files aren't loading:
- Vercel serves static files from the `static/` directory automatically
- Make sure `STATIC_URL` and `STATIC_ROOT` are configured correctly
- Run `python manage.py collectstatic` locally and commit the `staticfiles/` directory (if needed)

#### 8. Session Storage

Django sessions might not persist in serverless:
- Consider using database-backed sessions
- Or use a cache-based session backend (Redis)
- Or use cookie-based sessions with `SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'`

## Getting More Information

1. **Check Vercel Function Logs:**
   - Dashboard → Project → Functions → View Logs

2. **Enable Debug Mode Temporarily:**
   - Set `DEBUG=True` in environment variables (for debugging only)
   - This will show more detailed error messages

3. **Test WSGI Application Locally:**
   ```bash
   python manage.py runserver
   ```
   Ensure your app works locally first

## Recommended Solution for Production

For a production Django app on Vercel, consider:
1. Using Vercel Postgres for database
2. Using Redis for sessions/caching (Vercel KV)
3. Using `django-vercel` package for easier integration
4. Or consider using Railway, Render, or Heroku for Django deployment (they're more Django-friendly)

