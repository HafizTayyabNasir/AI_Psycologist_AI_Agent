import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elvion_project.settings')

try:
    from django.core.wsgi import get_wsgi_application
    
    application = get_wsgi_application()
except Exception as e:
    import traceback
    error_details = traceback.format_exc()
    
    def application(environ, start_response):
        start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
        return [f'Django initialization error: {str(e)}\n\n{error_details}'.encode()]

app = application
