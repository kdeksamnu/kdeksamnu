from flask import Flask
from config import DevelopmentConfig
from extensions import cache, limiter
from db import execute_db

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    cache.init_app(app)
    limiter.init_app(app)

    # Initialize DB table if not exists
    with app.app_context():
        execute_db("""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                instructions TEXT NOT NULL
            )
        """)

    # Register Blueprint
    from routes import recipes_bp
    app.register_blueprint(recipes_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
