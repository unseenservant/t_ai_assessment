# Kubernetes Counter App

A simple full-stack application deployed on Kubernetes (minikube) that demonstrates a counter with persistence.

## Architecture

This application consists of three main components:

1. **Frontend**: A simple HTML/CSS/JavaScript UI that displays a counter and a button to increment it.
2. **Backend**: A Flask API that handles requests to get and increment the counter.
3. **Database**: PostgreSQL for data persistence.

## Prerequisites

- [Docker](https://www.docker.com/get-started)
- [minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)

## Setup and Deployment

### 1. Start minikube

```bash
minikube start
```

### 2. Enable the minikube Docker daemon

```bash
eval $(minikube docker-env)
```

### 3. Build the Docker image

```bash
cd counter-app/app
docker build -t counter-app:latest .
```

### 4. Deploy the application to Kubernetes

```bash
cd ..
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/postgres-pv.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/flask-deployment.yaml
```

### 5. Access the application

```bash
minikube service counter-app
```

This will open the application in your default web browser.

## Kubernetes Resources

- **ConfigMap**: Stores database configuration
- **Secret**: Stores database credentials
- **PersistentVolume & PersistentVolumeClaim**: Provides persistent storage for PostgreSQL
- **Deployments**: Manages the PostgreSQL and Flask application pods
- **Services**: Exposes the PostgreSQL database internally and the Flask application externally

## Application Structure

- `app/`: Contains the Flask application code
  - `static/`: Static assets (CSS, JavaScript)
  - `templates/`: HTML templates
  - `app.py`: Main Flask application
  - `Dockerfile`: Instructions for building the application container
  - `requirements.txt`: Python dependencies
- `k8s/`: Kubernetes manifests
  - `configmap.yaml`: Database configuration
  - `secret.yaml`: Database credentials
  - `postgres-pv.yaml`: Persistent volume configuration
  - `postgres-deployment.yaml`: PostgreSQL deployment and service
  - `flask-deployment.yaml`: Flask application deployment and service

## Cleanup

To delete all resources created by this application:

```bash
kubectl delete -f k8s/
```

To stop minikube:

```bash
minikube stop
