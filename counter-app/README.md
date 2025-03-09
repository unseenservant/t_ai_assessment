# Kubernetes Counter App

A simple full-stack application deployed on Kubernetes (minikube) that demonstrates a counter with persistence.

## Architecture

This application consists of three main components:

1. **Frontend**: A simple HTML/CSS/JavaScript UI that displays a counter and a button to increment it.
2. **Backend**: A Flask API that handles requests to get and increment the counter.
3. **Database**: PostgreSQL for data persistence.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│    Frontend     │────▶│     Backend     │────▶│    Database     │
│  (HTML/JS/CSS)  │     │     (Flask)     │     │  (PostgreSQL)   │
│                 │◀────│                 │◀────│                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               │
                               ▼
                        ┌─────────────────┐
                        │                 │
                        │   Prometheus    │
                        │    Metrics      │
                        │                 │
                        └─────────────────┘
```

### Kubernetes Architecture

The application is deployed on Kubernetes with the following resources:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Kubernetes Cluster                       │
│                                                                 │
│  ┌─────────────────┐       ┌─────────────────┐                  │
│  │                 │       │                 │                  │
│  │  Flask Service  │       │ PostgreSQL Svc  │                  │
│  │   (NodePort)    │       │  (ClusterIP)    │                  │
│  │                 │       │                 │                  │
│  └────────┬────────┘       └────────┬────────┘                  │
│           │                         │                           │
│  ┌────────┼────────┐       ┌────────┼────────┐                  │
│  │        │        │       │        │        │                  │
│  │  ┌─────▼─────┐  │       │  ┌─────▼─────┐  │                  │
│  │  │           │  │       │  │           │  │                  │
│  │  │  Flask    │  │       │  │ PostgreSQL│  │                  │
│  │  │  Pod      │◀─┼───────┼──│  Pod      │  │                  │
│  │  │           │  │       │  │           │  │                  │
│  │  └───────────┘  │       │  └───────────┘  │                  │
│  │        ▲        │       │        ▲        │                  │
│  │        │        │       │        │        │                  │
│  │  ┌─────┴─────┐  │       │  ┌─────┴─────┐  │                  │
│  │  │           │  │       │  │           │  │                  │
│  │  │   HPA     │  │       │  │Persistent │  │                  │
│  │  │           │  │       │  │ Volume    │  │                  │
│  │  └───────────┘  │       │  └───────────┘  │                  │
│  │                 │       │                 │                  │
│  └─────────────────┘       └─────────────────┘                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- [Docker](https://www.docker.com/get-started)
- [minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [Helm 3](https://helm.sh/docs/intro/install/)

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

#### Using kubectl:

```bash
cd ..
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/postgres-pv.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/flask-deployment.yaml
kubectl apply -f k8s/flask-hpa.yaml
kubectl apply -f k8s/flask-pdb.yaml
kubectl apply -f k8s/postgres-pdb.yaml
kubectl apply -f k8s/network-policy.yaml
```

#### Using Helm:

```bash
helm install counter-app ./counter-app-chart
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
- **HorizontalPodAutoscaler**: Automatically scales the Flask application based on CPU utilization
- **PodDisruptionBudget**: Ensures high availability during voluntary disruptions
- **NetworkPolicy**: Restricts pod communication for enhanced security
- **ServiceMonitor**: Configures Prometheus to scrape metrics from the application
- **PrometheusRule**: Defines alerting rules for the application
- **CronJob**: Schedules regular database backups

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
  - `flask-hpa.yaml`: Horizontal Pod Autoscaler for the Flask application
  - `flask-pdb.yaml`: Pod Disruption Budget for the Flask application
  - `postgres-pdb.yaml`: Pod Disruption Budget for PostgreSQL
  - `network-policy.yaml`: Network policies for pod communication
  - `backup-cronjob.yaml`: CronJob for database backups
  - `monitoring.yaml`: ServiceMonitor and PrometheusRule for monitoring
- `counter-app-chart/`: Helm chart for deploying the application
  - `templates/`: Helm templates
  - `values.yaml`: Default configuration values
  - `Chart.yaml`: Chart metadata

## DevOps Best Practices

This application implements several DevOps best practices:

1. **Security**:
   - Non-root users in containers
   - Security contexts with least privileges
   - Network policies to restrict pod communication
   - Secrets for sensitive data

2. **Resource Management**:
   - Appropriate resource requests and limits
   - Horizontal pod autoscaling
   - Pod disruption budgets for high availability
   - Topology spread constraints and node affinity

3. **Observability**:
   - Structured logging with proper log levels
   - Prometheus metrics for monitoring
   - Grafana dashboards for visualization
   - Health checks and probes

4. **Persistence**:
   - Persistent volumes with appropriate storage classes
   - Backup and restore procedures
   - Storage retention policies

5. **Deployment**:
   - Rolling updates for zero-downtime deployments
   - Readiness and liveness probes
   - Init containers for dependencies

For more details on the development process, see [DEV_PROCESS.md](DEV_PROCESS.md).

## Cleanup

To delete all resources created by this application:

### Using kubectl:

```bash
kubectl delete -f k8s/
```

### Using Helm:

```bash
helm uninstall counter-app
```

To stop minikube:

```bash
minikube stop
