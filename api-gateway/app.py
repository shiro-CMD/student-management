import os
import requests
from flask import Flask, request, Response

app = Flask(__name__)

# Same pod as gateway -> localhost. Different pod -> Kubernetes Service DNS name.
REGISTRATION_URL = os.getenv("REGISTRATION_URL", "http://localhost:5001")
SEARCH_URL = os.getenv("SEARCH_URL", "http://search-service:5002")


def forward(method, url):
    resp = requests.request(
        method=method,
        url=url,
        params=request.args,
        json=request.get_json(silent=True),
        timeout=10,
    )
    return Response(resp.content, status=resp.status_code,
                    content_type=resp.headers.get("Content-Type", "application/json"))


@app.route("/health")
def health():
    return {"service": "api-gateway", "status": "UP"}


@app.route("/api/students/register", methods=["POST"])
def register():
    return forward("POST", f"{REGISTRATION_URL}/register")


@app.route("/api/students/search", methods=["GET"])
def search():
    return forward("GET", f"{SEARCH_URL}/search")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
