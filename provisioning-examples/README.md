# GitHub Actions Workflows

This repository contains GitHub Actions workflows for building, pushing, and deploying the Counter App to Kubernetes clusters on AWS (EKS) and Google Cloud (GKE).

## Workflow Files

### `docker-build-push-workflow.yml`
Builds the Docker image from the Flask application and pushes it to DockerHub.
- Triggers on pushes to main branch or manual workflow dispatch
- Builds using Docker Buildx
- Tags images with commit SHA or git tag and 'latest'
- Outputs version and image information for deployment workflows

### `eks-deploy-workflow.yml`
Deploys the application to AWS EKS using Helm.
- Triggers after successful image build or manual dispatch
- Configures AWS credentials and connects to EKS
- Installs/upgrades the Helm chart with EKS-specific settings

### `gke-deploy-workflow.yml`
Deploys the application to Google Kubernetes Engine using Helm.
- Similar to EKS workflow but configured for GKE
- Sets up Google Cloud authentication
- Deploys with GKE-specific parameters

### `store-artifact-workflow.yml`
Helper workflow to store data between workflow runs.
- Stores image tags and version information
- Used by deployment workflows to determine which image to deploy

## Prerequisites

The following secrets must be configured in your GitHub repository:

- `DOCKER_USERNAME`: DockerHub username
- `DOCKER_PASSWORD`: DockerHub password
- `AWS_ACCESS_KEY_ID`: AWS access key with EKS permissions
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `GCP_SA_KEY`: Base64-encoded GCP service account key JSON

## Usage

These workflows are designed to work in sequence:

1. The Docker build workflow runs first
2. The EKS and GKE deployment workflows run after the Docker image is built
3. Alternatively, each workflow can be manually triggered

For manual deployments, you can specify a particular image tag using the workflow dispatch inputs.