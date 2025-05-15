from flask import Blueprint, jsonify, request, render_template


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

    return jsonify({"result": "some result", "stdout": "some output"}), 200
