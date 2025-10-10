from main import app      
from flask import render_template

@app.route('/')
def Main():
    return render_template('Main.html')
