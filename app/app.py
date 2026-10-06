from flask import Flask
from database import init_db

app = Flask(__name__)


@app.route("/")
def home():
    return "Welcome to SecureCart!"


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

    