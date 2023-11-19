from django.apps import apps
from django.contrib import admin
from django.contrib.auth.models import Group  # Import the Group model

# Get a list of all installed models
app_models = apps.get_models()

# Exclude the Group model from the list
models_to_register = [model for model in app_models if model is not Group]

# Register all models except Group with the admin site
for model in models_to_register:
    admin.site.register(model)
