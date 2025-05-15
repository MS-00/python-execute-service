document.addEventListener("DOMContentLoaded", function () {
    const textarea = document.getElementById("python-code");

    textarea.value =
        "# There must be a 'main' function and it should return a dict \n" +
        "def main():\n" +
        "\tprint('Hello world!')\n" +
        '\treturn {"msg":"Hello!!"}\n';

    textarea.addEventListener("keydown", function (e) {
        if (e.key === "Tab") {
            e.preventDefault();
            const start = this.selectionStart;
            const end = this.selectionEnd;
            const value = this.value;

            // Check if multiple lines are selected
            if (start !== end && value.slice(start, end).includes("\n")) {
                // Get start of first line
                const lineStart = value.lastIndexOf("\n", start - 1) + 1;
                // Get selected text
                const selectedText = value.slice(lineStart, end);
                // Add tab to each line
                const newText = selectedText.replace(/(^|\n)/g, "$1\t");
                // Replace in textarea
                this.value =
                    value.slice(0, lineStart) + newText + value.slice(end);
                // Adjust selection
                this.selectionStart = lineStart;
                this.selectionEnd = lineStart + newText.length;
            } else {
                // Single line or no selection: insert tab at cursor
                this.value =
                    value.substring(0, start) + "\t" + value.substring(end);
                this.selectionStart = this.selectionEnd = start + 1;
            }
        }
    });

    const resetButton = document.getElementById("reset-button");

    resetButton.addEventListener("click", function (e) {
        e.preventDefault();

        textarea.value =
            "# There must be a 'main' function and it should return a dict \n" +
            "def main():\n" +
            "\t# your code ...\n" +
            "\treturn {}\n";

        const pres = document.querySelectorAll("#script-result pre");

        pres.forEach((pre) => {
            setPreContent(pre, "");
        });
    });

    function setPreContent(pre, text) {
        const span = pre.querySelector("span");

        pre.innerHTML = "";
        if (span) {
            pre.appendChild(span);
        }

        pre.appendChild(document.createTextNode(text || ""));
    }

    const form = document.querySelector("form");

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const script = textarea.value;

        fetch(form.action, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ script }),
        })
            .then((response) => response.json())
            .then((data) => {
                setPreContent(
                    document.querySelector("#script-result #json-response"),
                    JSON.stringify(data, null, 2)
                );
                setPreContent(
                    document.querySelector("#script-result #json-result"),
                    JSON.stringify(data.result, null, 2)
                );
                setPreContent(
                    document.querySelector("#script-result #json-stdout"),
                    data.stdout
                );
            })
            .catch((error) => {
                console.error("Error:", error);
            });
    });
});
