from os import path
from django.db import migrations

with open(path.join(path.dirname(__file__), 'views_creation.sql'), 'r') as f:
    migration_sql = migrations.RunSQL(f.read())
