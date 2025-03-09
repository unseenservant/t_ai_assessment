# Counter App Development Process

This document outlines the development process for the Counter App, including setup, testing, and deployment procedures.

## Local Development Setup

### Prerequisites

- [Docker](https://www.docker.com/get-started)
- [minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [Helm 3](https://helm.sh/docs/intro/install/)

### Initial Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd counter-app
```

2. Run the setup script to verify prerequisites:

```bash
./script.sh
```

3. Start minikube:

```bash
minikube start
```

4. Enable the minikube Docker daemon:

```bash
eval $(minikube docker-env)
```

### Building the Application

1. Build the Docker image:

```bash
cd app
docker build -t counter-app:latest .
cd ..
```

### Running Locally (Without Kubernetes)

For quick development and testing, you can run the application locally:

1. Install Python dependencies:

```bash
cd app
pip install -r requirements.txt
```

2. Run a local PostgreSQL instance (using Docker):

```bash
docker run -d --name postgres-dev \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=counter_db \
  -p 5432:5432 \
  postgres:13
```

3. Set environment variables:

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=postgres
export DB_PASSWORD=postgres
export DB_NAME=counter_db
```

4. Run the Flask application:

```bash
python app.py
```

The application will be available at http://localhost:5000.

### Running with Kubernetes

1. Deploy using kubectl:

```bash
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

2. Access the application:

```bash
minikube service counter-app
```

### Running with Helm

1. Install the Helm chart:

```bash
helm install counter-app ./counter-app-chart
```

2. Access the application:

```bash
minikube service counter-app
```

## Development Workflow

### Code Structure

- `app/app.py`: Main Flask application
- `app/static/`: Static assets (CSS, JavaScript)
- `app/templates/`: HTML templates
- `k8s/`: Kubernetes manifests
- `counter-app-chart/`: Helm chart

### Making Changes

1. Make changes to the code
2. Rebuild the Docker image:

```bash
cd app
docker build -t counter-app:latest .
```

3. Update the deployment:

```bash
# If using kubectl
kubectl rollout restart deployment counter-app

# If using Helm
helm upgrade counter-app ./counter-app-chart
```

### Testing

#### Manual Testing

1. Access the application UI:

```bash
minikube service counter-app
```

2. Test the API endpoints:

```bash
# Get counter value
curl $(minikube service counter-app --url)/api/counter

# Increment counter
curl -X POST $(minikube service counter-app --url)/api/counter/increment
```

3. Check the health endpoint:

```bash
curl $(minikube service counter-app --url)/health
```

#### Verifying Database Persistence

1. Check the counter value in the database:

```bash
kubectl exec -it $(kubectl get pods -l app=postgres -o name | cut -d'/' -f2) -- psql -U postgres -d counter_db -c "SELECT * FROM counter;"
```

2. Delete the counter-app pod to test persistence:

```bash
kubectl delete pod -l app=counter-app
```

3. After the new pod is running, check the counter value again:

```bash
curl $(minikube service counter-app --url)/api/counter
```

### Monitoring

The application exposes Prometheus metrics at the `/metrics` endpoint. You can access these metrics by:

```bash
curl $(minikube service counter-app --url)/metrics
```

If you have Prometheus and Grafana installed in your cluster, you can use the provided ServiceMonitor and Grafana dashboard to monitor the application.

## Troubleshooting

### Common Issues

1. **Database connection issues**:
   - Check if the PostgreSQL pod is running: `kubectl get pods -l app=postgres`
   - Check PostgreSQL logs: `kubectl logs -l app=postgres`
   - Verify the database credentials in the secret: `kubectl get secret postgres-secret -o yaml`

2. **Application not starting**:
   - Check the application logs: `kubectl logs -l app=counter-app`
   - Verify the environment variables: `kubectl describe pod -l app=counter-app`

3. **Metrics not showing up**:
   - Check if the metrics endpoint is accessible: `curl $(minikube service counter-app --url)/metrics`
   - Verify the ServiceMonitor configuration: `kubectl get servicemonitor counter-app-monitor -o yaml`

### Debugging

For more detailed debugging:

1. Get a shell in the application pod:

```bash
kubectl exec -it $(kubectl get pods -l app=counter-app -o name | cut -d'/' -f2) -- /bin/bash
```

2. Get a shell in the database pod:

```bash
kubectl exec -it $(kubectl get pods -l app=postgres -o name | cut -d'/' -f2) -- /bin/bash
```

## Cleanup

### Kubernetes Cleanup

```bash
kubectl delete -f k8s/
```

### Helm Cleanup

```bash
helm uninstall counter-app
```

### Minikube Cleanup

```bash
minikube stop
```

## Best Practices

1. **Security**:
   - Always use non-root users in containers
   - Apply security contexts to pods and containers
   - Use network policies to restrict pod communication
   - Store sensitive data in Kubernetes secrets

2. **Resource Management**:
   - Set appropriate resource requests and limits
   - Use horizontal pod autoscaling for the application
   - Implement pod disruption budgets for high availability

3. **Monitoring and Observability**:
   - Use structured logging with proper log levels
   - Expose Prometheus metrics for monitoring
   - Create Grafana dashboards for visualization

4. **Persistence**:
   - Use persistent volumes for database storage
   - Implement backup and restore procedures
   - Configure proper storage retention policies

5. **Deployment**:
   - Use rolling updates for zero-downtime deployments
   - Implement readiness and liveness probes
   - Use init containers for dependencies
