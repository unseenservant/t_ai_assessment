#!/bin/sh
# Simple script to check for kubectl, minikube, helm3, and docker
# With option to build docker image

# Check if running in unattended mode
unattended=false
if [ "$1" = "--unattended" ]; then
    unattended=true
fi

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

# Report results
if [ -z "$missing" ]; then
    echo "All required tools are installed."
    
    # In unattended mode, build without prompting
    if [ "$unattended" = true ]; then
        build_docker_image
    else
        # Prompt user for docker build
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