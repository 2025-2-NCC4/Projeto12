from flask import Flask
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'Frontend', 'templates'),
    static_folder=os.path.join(BASE_DIR, 'Frontend', 'static')
)


if __name__ == '__main__':
    from views import *  
    app.run(debug=True)
