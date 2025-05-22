from flask import Blueprint, request, jsonify
from models.db import mongo
from bson import ObjectId
import bcrypt

bp = Blueprint("route1", __name__)

@bp.route("/set_parklot", methods=["POST"])
def set_parklot():
    data = request.json or {}
    mac = data.get("mac")
    val = data.get("val")
    if mac is None or val not in [0, 1]:
        return jsonify({"error": "Invalid parameters"}), 400

    result = mongo.db.parklots.update_one(
        {"mac": mac},
        {"$set": {"val": val}},
        upsert=True  # 如果不存在则插入新文档
    )
    if result.matched_count > 0 or result.upserted_id:
        return jsonify({"message": "Parklot status updated"}), 201
    else:
        return jsonify({"error": "Parklot not found"}), 404


