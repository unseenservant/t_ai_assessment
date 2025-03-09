# Counter App Helm Chart Demo

This document demonstrates the functionality of the Counter App deployed using Helm, with a focus on verifying that the database correctly stores counter values.

## Deployment Status

After deploying the Helm chart, we can check the status of all resources:

```bash
$ kubectl get all
NAME                               READY   STATUS    RESTARTS   AGE
pod/counter-app-76cd7dd6cb-wx55v   1/1     Running   0          17s
pod/postgres-6b58c76ccd-75dvd      1/1     Running   0          18m

NAME                  TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
service/counter-app   NodePort    10.99.205.94    <none>        80:32698/TCP   15m
service/kubernetes    ClusterIP   10.96.0.1       <none>        443/TCP        25m
service/postgres      ClusterIP   10.109.173.42   <none>        5432/TCP       15m

NAME                          READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/counter-app   1/1     1            1           15m
deployment.apps/postgres      1/1     1            1           15m

NAME                                     DESIRED   CURRENT   READY   AGE
replicaset.apps/counter-app-76cd7dd6cb   1         1         1       4m8s
replicaset.apps/postgres-6b58c76ccd      1         1         1       15m

NAME                                          REFERENCE                TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
horizontalpodautoscaler.autoscaling/counter-app-hpa   Deployment/counter-app   0%/80%    1         2         1          5m
```

## Health Check and Autoscaling

The application includes:

1. **Health Check Endpoint**: A `/health` endpoint that verifies database connectivity
   ```bash
   $ curl http://$(minikube ip):$(kubectl get svc counter-app -o jsonpath='{.spec.ports[0].nodePort}')/health
   {"status": "healthy", "database": "connected"}
   ```

2. **Horizontal Pod Autoscaler**: Automatically scales the Flask application based on CPU utilization
   ```bash
   $ kubectl get hpa
   NAME             REFERENCE                TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
   counter-app-hpa   Deployment/counter-app   0%/80%    1         2         1          5m
   ```

## Accessing the Application

The application can be accessed using:

```bash
$ minikube service counter-app --url
http://192.168.67.2:32698
```

## Database Verification

### Checking Counter Value in Database

After interacting with the UI and incrementing the counter, we can verify that the value is stored in the PostgreSQL database:

```bash
$ kubectl exec -it $(kubectl get pods -l app=postgres -o name | cut -d'/' -f2) -- psql -U postgres -d counter_db -c "SELECT * FROM counter;"
 id | value
----+-------
  1 |     3
(1 row)
```

This shows that the counter value (3) is correctly stored in the database.

### Testing Persistence

To verify that the counter value persists even when the application pod is deleted and recreated:

1. Delete the counter-app pod:

```bash
$ kubectl delete pod -l app=counter-app
pod "counter-app-76cd7dd6cb-kn2h4" deleted
```

2. Wait for the new pod to be created and become ready:

```bash
$ kubectl get pods
NAME                           READY   STATUS    RESTARTS   AGE
counter-app-76cd7dd6cb-wx55v   1/1     Running   0          17s
postgres-6b58c76ccd-75dvd      1/1     Running   0          18m
```

3. Check the counter value in the database again:

```bash
$ kubectl exec -it $(kubectl get pods -l app=postgres -o name | cut -d'/' -f2) -- psql -U postgres -d counter_db -c "SELECT * FROM counter;"
 id | value
----+-------
  1 |     3
(1 row)
```

The counter value remains at 3, confirming that the data persists across pod restarts.

## Helm Chart Deployment Commands

To deploy or upgrade the application using the Helm chart:

```bash
# Connect to minikube's Docker daemon
eval $(minikube docker-env)

# Build the Docker image
docker build -t counter-app:latest -f counter-app/app/Dockerfile counter-app/app/

# Install/upgrade the chart
helm install counter-app ./counter-app-chart
# or
helm upgrade counter-app ./counter-app-chart
```

## Customization

The deployment can be customized by modifying values.yaml or using --set parameters:

```bash
helm install counter-app ./counter-app-chart --set app.replicaCount=2,postgres.resources.limits.memory=1Gi
```

## Screenshots

[Screenshots will be added later to show the UI and counter functionality]
