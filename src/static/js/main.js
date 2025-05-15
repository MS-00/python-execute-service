document.addEventListener("DOMContentLoaded", function () {
    const textarea = document.getElementById("python-code");

    setDemoCode();

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

    function setDemoCode() {
        textarea.value =
            "# This is a comment\n" +
            "def main():\n" +
            "\tprint('Hello world!')\n";
    }

    const resetButton = document.getElementById("reset-button");

    resetButton.addEventListener("click", function (e) {
        e.preventDefault();

        setDemoCode();

        const pre = document.querySelector("#script-result pre");

        pre.textContent = "";
    });

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
                const pre = document.querySelector("#script-result pre");

                pre.textContent = JSON.stringify(data, null, 2);
            })
            .catch((error) => {
                console.error("Error:", error);
            });
    });
});
