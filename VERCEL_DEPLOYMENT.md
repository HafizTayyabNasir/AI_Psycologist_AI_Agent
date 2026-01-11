# Vercel Deployment Guide

Your Django project has been configured for Vercel deployment.

## Files Created/Modified

1. **vercel.json** - Vercel configuration file
2. **api/index.py** - Serverless function entry point for Django
3. **api/__init__.py** - Python package marker
4. **elvion_project/settings.py** - Updated to use environment variables
5. **README_VERCEL.md** - Deployment instructions

## Environment Variables Required in Vercel

Go to your Vercel project settings → Environment Variables and add:

1. **GROQ_API_KEY** (Required)
   - Your Groq API key
   - Already configured in code to use `os.getenv("GROQ_API_KEY")`

2. **SECRET_KEY** (Recommended)
   - Django secret key for production
   - Generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

3. **DEBUG** (Optional)
   - Set to `False` for production
   - Defaults to `False` if not set

4. **ALLOWED_HOSTS** (Optional)
   - Comma-separated list: `your-project.vercel.app,*.vercel.app`
   - Defaults to `*` if not set

## Quick Deployment Steps

1. Push code to GitHub/GitLab/Bitbucket
2. Go to https://vercel.com/dashboard
3. Click "New Project" and import your repository
4. Add environment variables (especially GROQ_API_KEY)
5. Click "Deploy"

## Important Notes

⚠️ **SQLite Database Limitation**: 
- SQLite uses the filesystem, which is read-only in Vercel serverless functions
- Consider using PostgreSQL (Vercel Postgres) or another database service for production

⚠️ **Sessions**: 
- Django sessions may not persist correctly in serverless environments
- Consider using database-backed sessions or Redis

✅ **GROQ_API_KEY**: 
- Already configured to read from environment variables
- No code changes needed - just add it in Vercel dashboard

## Testing Locally

To test locally with Vercel:

```bash
npm i -g vercel
vercel dev
```

## Project Structure

```
.
├── api/
│   ├── __init__.py
│   └── index.py          # Vercel serverless function entry point
├── chatbot/
├── elvion_project/
├── website/
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
└── README_VERCEL.md      # Detailed deployment guide
```

