from flask import Flask, redirect

import logging


def create_app():
    app = Flask(__name__)

    logging.basicConfig(
        filename="record.log",
        level=logging.DEBUG,
        format=f"%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s",
    )

    # Register blueprints here
    from src.routes.script import script_bp

    app.register_blueprint(script_bp, url_prefix="/script/")

    @app.route("/")
    def home():
        return redirect("/script/editor")

    return app
