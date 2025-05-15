from flask import Blueprint, jsonify, request, render_template

import logging
import io
import sys

script_bp = Blueprint("script", __name__)


@script_bp.route("/editor", methods=["GET"])
def script_editor():
    return render_template("editor.html")


@script_bp.route("/execute", methods=["POST"])
def script_execute():
    data = request.json
    script = data.get("script")

    if not script:
        return jsonify({"error": "No script provided"}), 400

    local_namespace = {}

    try:
        # Redirect stdout to capture print output
        stdout_buffer = io.StringIO()
        sys_stdout_original = sys.stdout
        sys.stdout = stdout_buffer

        try:
            # Use the same namespace for globals and locals so functions can reference each other
            exec(script, local_namespace, local_namespace)

            # Check if 'main' is in the local namespace and is callable
            if "main" in local_namespace and callable(local_namespace["main"]):
                result = local_namespace["main"]()
                # Check if result is a dict (JSON serializable)
                if not isinstance(result, dict):
                    return jsonify(
                        {"error": "'main' must return a JSON-serializable dict"}
                    ), 400
            else:
                return jsonify(
                    {"error": "'main' function not found or not callable"}
                ), 400
        finally:
            sys.stdout = sys_stdout_original

        stdout = stdout_buffer.getvalue()
    except Exception as e:
        logging.error(f"Error executing script: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify({"result": result, "stdout": stdout}), 200
