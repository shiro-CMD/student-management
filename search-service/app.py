import os
import re
from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://host.minikube.internal:27017")
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
students = client["college_db"]["students"]

# never return the password or Mongo's internal _id
PROJECTION = {"_id": 0, "student_password": 0}


@app.route("/health")
def health():
    return {"service": "search-service", "status": "UP"}


@app.route("/search", methods=["GET"])
def search():
    """GET /search?id=1   or   GET /search?name=rahul"""
    sid = request.args.get("id")
    name = request.args.get("name")
    if not sid and not name:
        return jsonify({"error": "Provide 'id' or 'name' query parameter"}), 400

    try:
        if sid:
            if not sid.isdigit():
                return jsonify({"error": "id must be a number"}), 400
            query = {"Student_id": int(sid)}
        else:
            query = {"Student_name": {"$regex": re.escape(name), "$options": "i"}}
        rows = list(students.find(query, PROJECTION))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if not rows:
        return jsonify({"message": "No student found", "students": []}), 404
    return jsonify({"count": len(rows), "students": rows}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
