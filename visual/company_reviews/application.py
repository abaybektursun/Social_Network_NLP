#!/usr/bin/python3

from flask import render_template
from flask import Flask

app = Flask(__name__)
#app.config.from_object('config')

@app.route('/')
def hello(name=None):
    return render_template('index.html', name=name)

if __name__ == '__main__':
  app.run()
