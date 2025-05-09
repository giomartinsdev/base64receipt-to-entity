.PHONY: start stop logs clean build install test help

# Default target
.DEFAULT_GOAL := help

# Start the application
start: ## Start the receipt API service
    docker-compose up -d receipt_api

# Stop the application
stop: ## Stop the receipt API service
    docker-compose down

# View logs
logs: ## View logs of the receipt API service
    docker-compose logs -f receipt_api

# Build the application
build: ## Build the receipt API Docker image
    docker-compose build receipt_api

# Clean up
clean: ## Remove all containers, volumes, and images
    docker-compose down -v
    docker system prune -f

# Install dependencies
install: ## Install Python dependencies
    pip install -r requirements.txt

# Run tests
test: ## Run tests
    pytest

# Help command
help: ## Show this help
    @echo "Available commands:"
    @grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
