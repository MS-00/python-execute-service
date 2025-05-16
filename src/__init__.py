from flask import Flask, redirect

import logging
import os
import json


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "thread": record.threadName,
            "message": record.getMessage(),
        }

        # If the message is valid JSON, pretty-print it
        try:
            msg_obj = json.loads(record.getMessage())
            log_record["message"] = msg_obj
        except Exception:
            pass

        return json.dumps(log_record, indent=2)


def create_app():
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

    logging.basicConfig(
        filename="record.log",
        level=logging.DEBUG,
    )

    # Set the custom JSON formatter
    for handler in logging.getLogger().handlers:
        handler.setFormatter(JsonFormatter())

    from src.routes.script import script_bp

    app.register_blueprint(script_bp, url_prefix="/script/")

    @app.route("/")
    def home():
        return redirect("/script/editor")

    return app
