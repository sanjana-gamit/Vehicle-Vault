import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vehiclevault.settings")
django.setup()

from django.db import connection

print("Dropping all tables to reset database schema...")
with connection.cursor() as cursor:
    cursor.execute("DROP SCHEMA public CASCADE;")
    cursor.execute("CREATE SCHEMA public;")
    cursor.execute("GRANT ALL ON SCHEMA public TO postgres;")
    cursor.execute("GRANT ALL ON SCHEMA public TO public;")
print("Tables dropped successfully.")
