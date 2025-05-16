from flask import Blueprint, jsonify, request, render_template

import logging
import subprocess

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

    try:
        # Log the incoming script safely (truncate if too long)
        safe_script = (
            script if len(script) < 2000 else script[:2000] + "... [truncated]"
        )
        logging.info({"incoming_script": safe_script})

        # Auto-wrap user script to call main() and print result as JSON if dict
        wrapped_script = (
            script.strip()
            + """\n
import json
if __name__ == '__main__':
    if 'main' not in globals() or not callable(main):
        print('__NO_MAIN__')
    else:
        result = main()
        if not isinstance(result, dict):
            print('__MAIN_NOT_DICT__')
        else:
            print(json.dumps(result))
            """
        )

        # Pass the script to nsjail via stdin
        nsjail_cmd = [
            "nsjail",
            "--config",
            "/app/nsjail.cfg",
            "--user",
            "65534",
            "--group",
            "65534",
            "--",
            "/usr/local/bin/python3",
            "-",
        ]
        proc = subprocess.run(
            nsjail_cmd,
            input=wrapped_script,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="/tmp",
        )

        if proc.returncode != 0:
            user_error = extract_user_error(proc.stderr)

            logging.error(
                {
                    "stdout": proc.stdout,
                    # "stderr": proc.stderr,
                    "returncode": proc.returncode,
                    "user_error": user_error,
                }
            )

            return jsonify(
                {"error": "Script execution failed", "user_error": user_error}
            ), 400

        result, error_type, filtered_stdout = parse_script_result(proc.stdout)

        if error_type == "no_main":
            return jsonify(
                {
                    "error": "'main' function not found or not callable",
                    # "stdout": filtered_stdout,
                }
            ), 400

        if error_type == "main_not_dict":
            return jsonify(
                {
                    "error": "'main' must return a JSON-serializable dict",
                    # "stdout": filtered_stdout,
                }
            ), 400

        response = {"stdout": filtered_stdout}
        if result is not None:
            response["result"] = result
        return jsonify(response), 200

    except Exception as e:
        logging.error(f"Error executing script: {e}")
        return jsonify({"error": str(e)}), 500


def extract_user_error(stderr: str) -> str:
    """Extracts the most relevant Python error/traceback from stderr, skipping NSJail log lines."""
    import re

    tb_match = re.search(r"(Traceback[\s\S]+?)(?=\n\[|$)", stderr)
    if tb_match:
        return tb_match.group(1).strip()

    # If no traceback, try to extract the last non-NSJail line
    lines = [
        line
        for line in stderr.splitlines()
        if not line.startswith("[I]") and not line.startswith("[W]")
    ]

    return lines[-1] if lines else stderr.strip()


def parse_script_result(stdout: str):
    """Parse the last JSON dict from stdout as result, and filter it from stdout."""
    import json

    stdout_lines = stdout.splitlines()
    result = None
    json_line = None
    error_type = None

    for line in reversed(stdout_lines):
        if line == "__NO_MAIN__":
            error_type = "no_main"
            break
        elif line == "__MAIN_NOT_DICT__":
            error_type = "main_not_dict"
            break
        try:
            parsed = json.loads(line)
            if isinstance(parsed, dict):
                result = parsed
                json_line = line
                break
        except Exception:
            continue

    # Remove the JSON line or error marker from stdout if found
    if json_line:
        filtered_stdout = "\n".join(line for line in stdout_lines if line != json_line)
    elif error_type:
        filtered_stdout = "\n".join(
            line
            for line in stdout_lines
            if line not in ("__NO_MAIN__", "__MAIN_NOT_DICT__")
        )
    else:
        filtered_stdout = stdout
    return result, error_type, filtered_stdout
