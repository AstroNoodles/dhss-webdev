import psycopg2
import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
from dataclasses import dataclass
import datetime

app = Flask(__name__)

@app.route('/')
def index():
    print('hello')
    sample_webpage="settings"
    return render_template(f'{sample_webpage}.html')

if __name__ == '__main__':
    app = Flask(__name__)
    app.run()