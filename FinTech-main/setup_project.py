import os
import sys

def create_django_structure():
    # Ensure django is installed
    try:
        import django
    except ImportError:
        print("Django is not installed yet. Please run 'pip install django' first.")
        return

    # 1. Create project core and manage.py programmatically
    print("Scaffolding Django project...")
    from django.core.management import execute_from_command_line

    # Equivalent to: django-admin startproject core .
    execute_from_command_line(['', 'startproject', 'core', '.'])

    # Equivalent to: python manage.py startapp api
    execute_from_command_line(['manage.py', 'startapp', 'api'])

    # Equivalent to: python manage.py startapp ml_engine
    execute_from_command_line(['manage.py', 'startapp', 'ml_engine'])

    print("Project and apps scaffolded successfully!")

if __name__ == '__main__':
    create_django_structure()