# Python Execute Service

This service allows you to safely execute arbitrary Python scripts in a sandboxed environment. The result of the `main()` function and the script's stdout are returned via a REST API.

## Features

- Secure execution using nsjail
- Only the output of `main()` is returned as `result`
- Print statements are captured in `stdout`
- Returns clear errors if `main()` is missing or not a dict
- Supports basic libraries: `os`, `pandas`, `numpy`

## Requirements

- Docker

## Build and Run Locally

```powershell
# Build the Docker image
docker build -t python-execute-service .
# Run the service
docker run -p 8080:8080 python-execute-service
```

## Editor Web Page

You can also use the built-in web page to test the API in your browser:
[http://localhost:8080/script/editor](http://localhost:8080/script/editor)

This page provides a simple textarea where you can write your Python script, submit it, and view the API response.

## API Endpoints

### `POST /script/execute`

- **Description:** Execute a Python script in a secure sandbox and return the result of the `main()` function and any printed output.
- **Request Body:**

  ```json
  {
    "script": "def main():\n    return {\"hello\": \"world\"}\nprint(\"This is stdout\")"
  }
  ```

- **Response:**

  - `200 OK` (success):

    ```json
    {
      "result": {"hello": "world"},
      "stdout": "This is stdout"
    }
    ```

  - `400 Bad Request` (error):

    ```json
    {
      "error": "'main' function not found or not callable"
    }
    ```

### `GET /script/editor`

- **Description:** Opens a web page for interactively writing and testing scripts against the API.
- **Usage:** Open [http://localhost:8080/script/editor](http://localhost:8080/script/editor) in your browser.

## View Logs

```powershell
docker exec -it <CONTAINER_ID/NAME> tail -f /app/record.log
```

## Example Response

```json
{
  "result": { "hello": "world" },
  "stdout": "This is stdout"
}
```

## Example cURL Request

```bash
curl --request POST \
  --url http://localhost:8080/script/execute \
  --header 'Content-Type: application/json' \
  --data '{
    "script": "# There must be a 'main' function and it should return a dict \ndef main():\n\tprint('Hello world!')\n\treturn {\"msg\":\"Hello!!\"}\n"
}'
```

## Security

- Scripts are executed in a strict nsjail sandbox with CPU, memory, and file limits.
- No network access.

## Input Validation

- The `script` field is required in the POST body.
- The script must define a callable `main()` that returns a JSON-serializable dict.

## License

MIT
