# Student Management System (Microservices + Docker + Kubernetes + MongoDB)

Runs fully locally: MongoDB in a Docker container, microservices in Minikube (2 Pods).

Postman -> **API Gateway** -> Registration / Search -> **MongoDB**

| Component | Port | Where |
|---|---|---|
| api-gateway | 8080 | Pod 1 |
| registration-service | 5001 | Pod 1 (same pod as gateway) |
| search-service | 5002 | Pod 2 |
| MongoDB `college_db.students` | 27017 | Docker container on host |

Fields: `Student_id, Student_name, student_mobile, student_email, student_password`

## Run
```bash
# 1. MongoDB first (normal terminal, BEFORE docker-env)
docker run -d --name student-mongo -p 27017:27017 mongo:7

# 2. Minikube
minikube start --driver=docker
eval $(minikube docker-env)

# 3. Build images
docker build -t api-gateway:1.0          ./api-gateway
docker build -t registration-service:1.0 ./registration-service
docker build -t search-service:1.0       ./search-service

# 4. Deploy (2 pods + services)
kubectl apply -f k8s/pod1-gateway-registration.yaml
kubectl apply -f k8s/pod2-search.yaml
kubectl apply -f k8s/services.yaml
kubectl get pods

# 5. Access via gateway
kubectl port-forward svc/api-gateway-service 8080:8080
```

## Postman
- `POST http://localhost:8080/api/students/register`
```json
{"student_name":"Rahul Sharma","student_mobile":"9876543210","student_email":"rahul@college.edu","student_password":"Pass@123"}
```
- `GET http://localhost:8080/api/students/search?id=1`
- `GET http://localhost:8080/api/students/search?name=rahul`

## Database screenshot (normal terminal, not the docker-env one)
```bash
docker exec -it student-mongo mongosh college_db --eval "db.students.find().pretty()"
```

## GitHub
```bash
git init && git add . && git commit -m "Student management microservices"
git branch -M main
git remote add origin https://github.com/<your-username>/student-management.git
git push -u origin main
```
