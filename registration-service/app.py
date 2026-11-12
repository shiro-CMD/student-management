import os
import time
from flask import Flask, request, jsonify
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import DuplicateKeyError
from werkzeug.security import generate_password_hash

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://host.minikube.internal:27017")
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
db = client["college_db"]
students = db["students"]
counters = db["counters"]


def init_db(retries=20):
    for _ in range(retries):
        try:
            client.admin.command("ping")
            students.create_index("student_email", unique=True)
            return
        except Exception as e:
            print("Waiting for MongoDB...", e, flush=True)
            time.sleep(2)
    raise RuntimeError("MongoDB not reachable")


def next_student_id():
    """Auto-increment Student_id (1, 2, 3, ...)"""
    doc = counters.find_one_and_update(
        {"_id": "student_id"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return doc["seq"]


@app.route("/health")
def health():
    return {"service": "registration-service", "status": "UP"}


@app.route("/register", methods=["POST"])
def register():
    data = {k.lower(): v for k, v in (request.get_json(silent=True) or {}).items()}
    required = ["student_name", "student_mobile", "student_email", "student_password"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    doc = {
        "Student_id": next_student_id(),
        "Student_name": data["student_name"],
        "student_mobile": data["student_mobile"],
        "student_email": data["student_email"],
        "student_password": generate_password_hash(data["student_password"]),
    }
    try:
        students.insert_one(doc)
    except DuplicateKeyError:
        return jsonify({"error": "Email already registered"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"message": "Student registered successfully",
                    "Student_id": doc["Student_id"]}), 201


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
