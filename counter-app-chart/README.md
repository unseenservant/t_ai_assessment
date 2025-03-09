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

# Install the chart
helm install counter-app ./counter-app-chart
```

## Uninstalling the Chart

To uninstall/delete the `counter-app` deployment:

```bash
helm uninstall counter-app
```

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
| `app.resources.limits.cpu`          | CPU limits for Flask application                 | `300m`                     |
| `app.resources.limits.memory`       | Memory limits for Flask application              | `256Mi`                    |
| `app.resources.requests.cpu`        | CPU requests for Flask application               | `100m`                     |
| `app.resources.requests.memory`     | Memory requests for Flask application            | `128Mi`                    |
| `postgres.name`                     | Name of the PostgreSQL deployment                | `postgres`                 |
| `postgres.replicaCount`             | Number of PostgreSQL replicas                    | `1`                        |
| `postgres.image.repository`         | PostgreSQL image repository                      | `postgres`                 |
| `postgres.image.tag`                | PostgreSQL image tag                             | `13`                       |
| `postgres.image.pullPolicy`         | PostgreSQL image pull policy                     | `IfNotPresent`             |
| `postgres.service.port`             | Kubernetes service port for PostgreSQL           | `5432`                     |
| `postgres.persistence.enabled`      | Enable persistence for PostgreSQL                | `true`                     |
| `postgres.persistence.storageClass` | Storage class for PostgreSQL PV                  | `manual`                   |
| `postgres.persistence.size`         | Size of PostgreSQL PV                            | `1Gi`                      |
| `postgres.persistence.path`         | Host path for PostgreSQL PV                      | `/mnt/data`                |
| `postgres.resources.limits.cpu`     | CPU limits for PostgreSQL                        | `500m`                     |
| `postgres.resources.limits.memory`  | Memory limits for PostgreSQL                     | `512Mi`                    |
| `postgres.resources.requests.cpu`   | CPU requests for PostgreSQL                      | `250m`                     |
| `postgres.resources.requests.memory`| Memory requests for PostgreSQL                   | `256Mi`                    |
| `database.name`                     | PostgreSQL database name                         | `counter_db`               |
| `database.user`                     | PostgreSQL username                              | `postgres`                 |
| `database.password`                 | PostgreSQL password                              | `postgres`                 |

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

The PostgreSQL database uses a PersistentVolume to store data. The default configuration uses a hostPath volume, which is suitable for development with minikube but not for production. For production, you should configure an appropriate storage class.

## Accessing the Application

After deploying the chart, you can access the application using the instructions provided in the NOTES.txt output.

For minikube, you can simply run:

```bash
minikube service counter-app
```

This will open the application in your default web browser.
