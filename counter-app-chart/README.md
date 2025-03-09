# Counter App Helm Chart

A Helm chart for deploying the Counter App with Flask and PostgreSQL on Kubernetes.

## Introduction

This chart deploys a simple counter application with a Flask backend and PostgreSQL database for persistence. The application allows users to view and increment a counter, with the count stored in a PostgreSQL database.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- Docker (for building the image)
- Minikube (for local development)

## Installing the Chart

To install the chart with the release name `counter-app`:

```bash
# Make sure the Docker image is available
# If using minikube, run:
eval $(minikube docker-env)

# Build the Docker image
docker build -t counter-app:latest counter-app/app/

# Prepare minikube directories for persistent storage
minikube ssh
sudo mkdir -p /mnt/data/postgres
sudo mkdir -p /mnt/data/postgres-backup
sudo chmod -R 777 /mnt/data
exit

# Install the chart
helm install counter-app ./counter-app-chart
```

## Uninstalling the Chart

To uninstall/delete the `counter-app` deployment:

```bash
helm uninstall counter-app
```

For a complete cleanup including persistent volumes:

```bash
# Tear down all resources
./setup.sh --tear-down
```

## Chart Structure

The chart has been organized into logical components:

- `postgres-resources.yaml`: Core PostgreSQL resources (PV, PVC, ConfigMap, Secret, Deployment, Service)
- `app-resources.yaml`: Core application resources (Deployment, Service, HPA)
- `optional-resources.yaml`: Optional resources (Backups, Network Policies, PDBs)
- `monitoring-resources.yaml`: Monitoring resources (Prometheus, Grafana)

## Configuration

The following table lists the configurable parameters of the Counter App chart and their default values.

| Parameter                           | Description                                      | Default                    |
|-------------------------------------|--------------------------------------------------|----------------------------|
| `app.name`                          | Name of the Flask application                    | `counter-app`              |
| `app.replicaCount`                  | Number of Flask application replicas             | `1`                        |
| `app.image.repository`              | Flask application image repository               | `counter-app`              |
| `app.image.tag`                     | Flask application image tag                      | `latest`                   |
| `app.image.pullPolicy`              | Flask application image pull policy              | `Never`                    |
| `app.service.type`                  | Kubernetes service type for Flask application    | `NodePort`                 |
| `app.service.port`                  | Kubernetes service port for Flask application    | `80`                       |
| `app.service.targetPort`            | Container port for Flask application             | `5000`                     |
| `app.strategy.rollingUpdate.maxSurge` | Max number of pods that can be created above desired number | `1`          |
| `app.strategy.rollingUpdate.maxUnavailable` | Max number of pods that can be unavailable during update | `0`      |
| `app.podDisruptionBudget.enabled`   | Enable Pod Disruption Budget for Flask app      | `true`                     |
| `app.podDisruptionBudget.minAvailable` | Minimum pods available during disruption     | `1`                        |
| `app.resources.limits.cpu`          | CPU limits for Flask application                 | `300m`                     |
| `app.resources.limits.memory`       | Memory limits for Flask application              | `256Mi`                    |
| `app.resources.requests.cpu`        | CPU requests for Flask application               | `100m`                     |
| `app.resources.requests.memory`     | Memory requests for Flask application            | `128Mi`                    |
| `app.livenessProbe.*`               | Liveness probe settings for Flask app            | See values.yaml            |
| `app.readinessProbe.*`              | Readiness probe settings for Flask app           | See values.yaml            |
| `app.autoscaling.enabled`           | Enable autoscaling for Flask application         | `true`                     |
| `app.autoscaling.minReplicas`       | Minimum number of replicas                       | `1`                        |
| `app.autoscaling.maxReplicas`       | Maximum number of replicas                       | `2`                        |
| `app.autoscaling.targetCPUUtilizationPercentage` | Target CPU utilization percentage   | `80`                       |
| `postgres.name`                     | Name of the PostgreSQL deployment                | `postgres`                 |
| `postgres.image.repository`         | PostgreSQL image repository                      | `postgres`                 |
| `postgres.image.tag`                | PostgreSQL image tag                             | `13`                       |
| `postgres.image.pullPolicy`         | PostgreSQL image pull policy                     | `IfNotPresent`             |
| `postgres.service.port`             | Kubernetes service port for PostgreSQL           | `5432`                     |
| `postgres.persistence.size`         | Size of PostgreSQL PV                            | `1Gi`                      |
| `postgres.persistence.path`         | Host path for PostgreSQL PV                      | `/mnt/data/postgres`       |
| `postgres.persistence.reclaimPolicy` | PV reclaim policy                               | `Retain`                   |
| `postgres.backup.enabled`           | Enable PostgreSQL backups                        | `true`                     |
| `postgres.backup.schedule`          | Backup schedule (cron format)                    | `0 1 * * *`                |
| `postgres.backup.retentionDays`     | Number of days to retain backups                 | `7`                        |
| `postgres.backup.storageClass`      | Storage class for backup volume                  | `standard`                 |
| `postgres.backup.storage`           | Size of backup volume                            | `1Gi`                      |
| `postgres.podDisruptionBudget.enabled` | Enable Pod Disruption Budget for PostgreSQL   | `true`                     |
| `postgres.podDisruptionBudget.minAvailable` | Minimum pods available during disruption | `1`                        |
| `postgres.resources.limits.cpu`     | CPU limits for PostgreSQL                        | `500m`                     |
| `postgres.resources.limits.memory`  | Memory limits for PostgreSQL                     | `512Mi`                    |
| `postgres.resources.requests.cpu`   | CPU requests for PostgreSQL                      | `250m`                     |
| `postgres.resources.requests.memory`| Memory requests for PostgreSQL                   | `256Mi`                    |
| `postgres.livenessProbe.*`          | Liveness probe settings for PostgreSQL           | See values.yaml            |
| `postgres.readinessProbe.*`         | Readiness probe settings for PostgreSQL          | See values.yaml            |
| `database.name`                     | PostgreSQL database name                         | `counter_db`               |
| `database.user`                     | PostgreSQL username                              | `postgres`                 |
| `database.password`                 | PostgreSQL password                              | `postgres`                 |
| `networkPolicy.enabled`             | Enable network policies                          | `true`                     |
| `monitoring.enabled`                | Enable Prometheus/Grafana monitoring             | `false`                    |

Specify each parameter using the `--set key=value[,key=value]` argument to `helm install`.

For example:

```bash
helm install counter-app ./counter-app-chart --set app.replicaCount=2,postgres.persistence.size=2Gi
```

Alternatively, a YAML file that specifies the values for the parameters can be provided while installing the chart:

```bash
helm install counter-app ./counter-app-chart -f values.yaml
```

## Persistence

The PostgreSQL database uses a PersistentVolume to store data. The chart creates:

1. A PersistentVolume (`postgres-data-pv`) pointing to `/mnt/data/postgres` on the host
2. A PersistentVolumeClaim (`postgres-data-pvc`) that explicitly binds to this PV
3. A backup PV/PVC pair if backups are enabled

The PostgreSQL container uses the `PGDATA` environment variable to ensure data is stored in the correct location.

## Backups

If enabled, PostgreSQL backups are:
- Scheduled according to the `postgres.backup.schedule` cron expression
- Stored in the backup PV
- Retained for the number of days specified in `postgres.backup.retentionDays`

## Monitoring

If `monitoring.enabled` is set to `true`, the chart will create:
- A ServiceMonitor for Prometheus to scrape metrics
- A PrometheusRule for alerting
- A Grafana dashboard ConfigMap

Note: This requires the Prometheus Operator CRDs to be installed in your cluster.

## Accessing the Application

After deploying the chart, you can access the application:

```bash
# For minikube
minikube service counter-app

# For other environments
kubectl port-forward svc/counter-app 8080:80
# Then access at http://localhost:8080
```

## Troubleshooting

Common issues:

1. **PVs not binding to PVCs**
   - Ensure directories exist in Minikube
   - Check storage permissions (`chmod -R 777 /mnt/data`)

2. **PostgreSQL fails to start**
   - Check logs: `kubectl logs -l app=postgres`

3. **Complete cleanup**
   - Run `./setup.sh --tear-down` to remove all resources including PVs