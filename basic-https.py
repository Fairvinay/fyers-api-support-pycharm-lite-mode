import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello HTTPS"

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    cert_file = os.path.join(base_dir, "ssl", "server.crt")
    key_file = os.path.join(base_dir, "ssl", "server.key")

    app.run(
        host="0.0.0.0",
        port=9384,
        ssl_context=(cert_file, key_file)
    )
