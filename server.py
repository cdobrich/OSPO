#!/usr/bin/env python3

from flask import Flask
from time import sleep


PORT = 8000
app = Flask(__name__)

@app.route("/hello")
def hello():
    sleep(30 / 1000)
    return "hello world\n"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)



