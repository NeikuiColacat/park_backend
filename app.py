from flask import Flask
from models.db import mongo, init_db
from routes.route1 import bp as r1 

app = Flask(__name__)
init_db(app)

app.register_blueprint(r1) 

if __name__ == "__main__":
    app.run('0.0.0.0',debug=True,port=5000)