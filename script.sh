#!/bin/sh
# Simple script to check for kubectl, minikube, helm3, and docker
# With option to build docker image or tear down resources

# Display usage information
usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Options:
  --unattended        Run in unattended mode (no prompts)
  --tear-down         Remove all resources
  --install-helm-release  Install Helm release for counter-app
  --help              Display this help message

Description:
  This script checks for required tools (kubectl, minikube, helm3, docker),
  and provides options to build Docker images or manage Kubernetes resources.
EOF
    exit "${1:-0}"
}

# Check command-line arguments
unattended=false
tear_down=false
install_helm_release=false

for arg in "$@"; do
  case "$arg" in
    --unattended)
      unattended=true
      ;;
    --tear-down)
      tear_down=true
      ;;
    --install-helm-release)
      install_helm_release=true
      ;;
    --help)
      usage
      ;;
    -*)
      echo "Unknown option: $arg" >&2
      usage 1
      ;;
  esac
done

missing=""

# Check each tool
command -v kubectl >/dev/null 2>&1 || missing="$missing kubectl"
command -v minikube >/dev/null 2>&1 || missing="$missing minikube"
command -v docker >/dev/null 2>&1 || missing="$missing docker"

# Special check for helm3
if command -v helm >/dev/null 2>&1; then
    helm version 2>/dev/null | grep -q "v3" || missing="$missing helm3"
else
    missing="$missing helm3"
fi

# Build docker image function
build_docker_image() {
    echo "Building docker image..."
    cd counter-app/app || { echo "Error: counter-app directory not found"; exit 1; }
    docker build -t counter-app:latest .
    build_status=$?
    cd - >/dev/null
    
    if [ $build_status -eq 0 ]; then
        echo "Docker image counter-app:latest built successfully."
    else
        echo "Error building docker image."
        exit 1
    fi
}

# Tear down resources function
tear_down_resources() {
    echo "Removing Kubernetes resources..."
    helm uninstall counter-app 2>/dev/null || true
    kubectl delete pvc --all
    kubectl delete pv postgres-data-pv postgres-backup-pv 2>/dev/null || true
    
    echo "Cleaning up persistent data..."
    minikube ssh "sudo rm -rf /mnt/data/postgres*" || echo "Warning: Could not clean up minikube data"
    
    echo "Removing Docker image..."
    docker image rm counter-app:latest 2>/dev/null || true
    
    echo "All resources have been removed."
}

# Install helm release function
install_helm_release() {
    current_dir=$(pwd)
    base_dir=$(basename "$current_dir")
    
    if [ "$base_dir" = "trojai_assessment" ]; then
        # Build docker image first
        build_docker_image
        
        echo "Installing helm release for counter-app..."
        helm install counter-app ./counter-app-chart
        if [ $? -eq 0 ]; then
            echo "Helm release counter-app installed successfully."
        else
            echo "Error installing helm release."
            exit 1
        fi
    else
        echo "Error: Current directory is not 'trojai_assessment'"
        echo "Current directory: $current_dir"
        exit 1
    fi
}

# Execute tear down if requested
if [ "$tear_down" = true ]; then
    tear_down_resources
    exit 0
fi

# Execute helm release installation if requested
if [ "$install_helm_release" = true ]; then
    install_helm_release
    exit 0
fi

# Report results for prerequisite checks
if [ -z "$missing" ]; then
    echo "All required tools are installed."
    
    # Always build docker image in unattended mode
    if [ "$unattended" = true ]; then
        build_docker_image
    else
        # Prompt user for docker build only if not in unattended mode and not installing helm
        printf "Would you like to build the docker image? (y/n): "
        read -r response
        case "$response" in
            [Yy]*)
                build_docker_image
                ;;
            *)
                echo "Skipping docker image build."
                ;;
        esac
    fi
    
    exit 0
else
    echo "Missing tools:$missing"
    echo "Please install these prerequisites and try again."
    exit 1
fi