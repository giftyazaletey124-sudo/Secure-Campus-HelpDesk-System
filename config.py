import os

class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "PASTE_YOUR_GENERATED_KEY_HERE"
    )

    DATABASE = "instance/helpdesk.db"