# Deploying to Vercel

This Django project is configured for deployment on Vercel.

## Prerequisites

1. A Vercel account (sign up at https://vercel.com)
2. Your project pushed to a Git repository (GitHub, GitLab, or Bitbucket)

## Environment Variables

Before deploying, you need to set the following environment variables in Vercel:

1. **GROQ_API_KEY** - Your Groq API key (required)
2. **SECRET_KEY** - Django secret key (optional, defaults to development key)
3. **DEBUG** - Set to `False` for production (optional, defaults to False)
4. **ALLOWED_HOSTS** - Comma-separated list of allowed hosts (optional, defaults to *)

## Deployment Steps

1. **Push your code to GitHub/GitLab/Bitbucket**

2. **Import project to Vercel:**
   - Go to https://vercel.com/dashboard
   - Click "New Project"
   - Import your Git repository
   - Vercel will auto-detect the settings from `vercel.json`

3. **Configure Environment Variables:**
   - In your Vercel project settings, go to "Environment Variables"
   - Add the following variables:
     - `GROQ_API_KEY`: Your Groq API key
     - `SECRET_KEY`: Generate a new secret key (optional but recommended)
     - `DEBUG`: Set to `False` for production
     - `ALLOWED_HOSTS`: Your Vercel domain (e.g., `your-project.vercel.app`)

4. **Deploy:**
   - Click "Deploy"
   - Wait for the build to complete
   - Your app will be available at `https://your-project.vercel.app`

## Important Notes

- **Database**: SQLite is configured by default. For production, consider using a proper database like PostgreSQL.
- **Static Files**: Static files are served from the `static/` directory. Make sure to run `python manage.py collectstatic` if needed.
- **Migrations**: Run migrations after deployment if needed.
- **Sessions**: Django sessions use the database by default. In serverless environments, consider using Redis or another session backend.

## Generating a New Secret Key

To generate a new Django secret key for production:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

## Troubleshooting

- If you encounter import errors, make sure all dependencies are listed in `requirements.txt`
- Check Vercel build logs for any errors
- Ensure environment variables are set correctly
- For database issues, consider using a managed database service

