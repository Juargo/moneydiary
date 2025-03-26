"""Database configuration"""

import os
from dotenv import load_dotenv

load_dotenv()

TORTOISE_ORM = {
    "connections": {
        "default": (
            f"mysql://{os.getenv('MYSQL_USER')}:"
            f"{os.getenv('MYSQL_PASSWORD')}@"
            f"{os.getenv('MYSQL_HOST')}:"
            f"{os.getenv('MYSQL_PORT')}/"
            f"{os.getenv('MYSQL_DB')}"
        )
    },
    "apps": {
        "models": {
            "models": ["app.db.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
