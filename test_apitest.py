from models.db import mongo, init_db
from flask import Flask

app = Flask(__name__)
init_db(app)

with app.app_context():
    mongo.db.parklots.insert_many([
        {"mac": "ABC1", "val": 0},
        {"mac": "ABC2", "val": 0},
        {"mac": "ABC3", "val": 1}
    ])
    print("测试数据已插入")