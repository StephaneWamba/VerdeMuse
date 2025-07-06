#!/bin/bash

# VerdeMuse Deployment Script - Optimized Version
# This script deploys the optimized VerdeMuse application with performance improvements

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${ENVIRONMENT:-production}
COMPOSE_FILE="docker-compose.prod.yml"
DOCKERFILE="Dockerfile.optimized"

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}    VerdeMuse Deployment Script${NC}"
    echo -e "${BLUE}    Performance Optimized Version${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_step() {
    echo -e "\n${GREEN}[STEP]${NC} $1"
}

print_warning() {
    echo -e "\n${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "\n${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "\n${GREEN}[SUCCESS]${NC} $1"
}

check_dependencies() {
    print_step "Checking dependencies..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if files exist
    if [ ! -f "$COMPOSE_FILE" ]; then
        print_error "Production compose file not found: $COMPOSE_FILE"
        exit 1
    fi
    
    if [ ! -f "$DOCKERFILE" ]; then
        print_error "Optimized Dockerfile not found: $DOCKERFILE"
        exit 1
    fi
    
    print_success "All dependencies are available"
}

setup_environment() {
    print_step "Setting up environment..."
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        cat > .env << EOF
# VerdeMuse Environment Configuration
ENVIRONMENT=production
DEBUG=false

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Vector Database
VECTOR_DB_PATH=/app/data/embeddings

# Logging
LOG_LEVEL=INFO

# Security (Change these in production!)
SECRET_KEY=your-super-secure-secret-key-change-this
ACCESS_TOKEN_EXPIRE_MINUTES=60

# LLM Configuration
MISTRAL_API_KEY=your-mistral-api-key
OPENAI_API_KEY=your-openai-api-key

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
EOF
        print_warning "Please update .env file with your actual configuration values"
    fi
    
    # Create necessary directories
    mkdir -p data/embeddings
    mkdir -p cache
    mkdir -p logs
    
    print_success "Environment setup complete"
}

build_images() {
    print_step "Building optimized Docker images..."
    
    # Build images with caching
    docker-compose -f $COMPOSE_FILE build --parallel
    
    # Prune unused images to save space
    docker image prune -f
    
    print_success "Docker images built successfully"
}

deploy_services() {
    print_step "Deploying services..."
    
    # Stop existing services
    docker-compose -f $COMPOSE_FILE down --remove-orphans
    
    # Start services in detached mode
    docker-compose -f $COMPOSE_FILE up -d
    
    print_success "Services deployed successfully"
}

wait_for_services() {
    print_step "Waiting for services to be ready..."
    
    # Wait for API to be ready
    local api_ready=false
    local max_attempts=30
    local attempt=0
    
    while [ "$api_ready" = false ] && [ $attempt -lt $max_attempts ]; do
        if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
            api_ready=true
            print_success "API is ready"
        else
            echo -n "."
            sleep 2
            ((attempt++))
        fi
    done
    
    if [ "$api_ready" = false ]; then
        print_error "API failed to start within timeout"
        exit 1
    fi
    
    # Wait for Streamlit to be ready
    local streamlit_ready=false
    attempt=0
    
    while [ "$streamlit_ready" = false ] && [ $attempt -lt $max_attempts ]; do
        if curl -f -s http://localhost:8501 > /dev/null 2>&1; then
            streamlit_ready=true
            print_success "Streamlit is ready"
        else
            echo -n "."
            sleep 2
            ((attempt++))
        fi
    done
    
    if [ "$streamlit_ready" = false ]; then
        print_error "Streamlit failed to start within timeout"
        exit 1
    fi
    
    print_success "All services are ready"
}

show_status() {
    print_step "Service Status:"
    docker-compose -f $COMPOSE_FILE ps
    
    echo -e "\n${BLUE}Application URLs:${NC}"
    echo "🌐 Main Application: http://localhost"
    echo "📊 API Documentation: http://localhost/api/docs"
    echo "🔍 Health Check: http://localhost/health"
    echo "📈 Prometheus: http://localhost:9090"
    echo "📊 Grafana: http://localhost:3000"
    echo "🔍 Cache Stats: http://localhost/api/stats/cache"
    
    echo -e "\n${BLUE}Performance Optimizations Applied:${NC}"
    echo "✅ Multi-stage Docker build for smaller images"
    echo "✅ Redis-based conversation storage"
    echo "✅ LLM response caching"
    echo "✅ Nginx load balancing and compression"
    echo "✅ Resource limits and health checks"
    echo "✅ Monitoring with Prometheus and Grafana"
}

generate_knowledge_base() {
    print_step "Generating knowledge base..."
    
    # Run the knowledge base generation script
    docker-compose -f $COMPOSE_FILE exec api python scripts/generate_knowledge_base.py
    
    print_success "Knowledge base generated"
}

performance_test() {
    print_step "Running performance tests..."
    
    # Simple performance test
    echo "Testing API response time..."
    time curl -s http://localhost/health > /dev/null
    
    echo "Testing concurrent requests..."
    for i in {1..10}; do
        curl -s http://localhost/health > /dev/null &
    done
    wait
    
    print_success "Performance tests completed"
}

# Main execution
main() {
    print_header
    
    case "${1:-deploy}" in
        "deploy")
            check_dependencies
            setup_environment
            build_images
            deploy_services
            wait_for_services
            generate_knowledge_base
            show_status
            ;;
        "build")
            check_dependencies
            build_images
            ;;
        "start")
            docker-compose -f $COMPOSE_FILE up -d
            wait_for_services
            show_status
            ;;
        "stop")
            docker-compose -f $COMPOSE_FILE down
            ;;
        "restart")
            docker-compose -f $COMPOSE_FILE restart
            wait_for_services
            show_status
            ;;
        "status")
            show_status
            ;;
        "logs")
            docker-compose -f $COMPOSE_FILE logs -f
            ;;
        "test")
            performance_test
            ;;
        "clean")
            docker-compose -f $COMPOSE_FILE down --volumes --remove-orphans
            docker system prune -f
            ;;
        "help")
            echo "Usage: $0 [command]"
            echo "Commands:"
            echo "  deploy  - Full deployment (default)"
            echo "  build   - Build Docker images only"
            echo "  start   - Start services"
            echo "  stop    - Stop services"
            echo "  restart - Restart services"
            echo "  status  - Show service status"
            echo "  logs    - Follow logs"
            echo "  test    - Run performance tests"
            echo "  clean   - Clean up containers and images"
            echo "  help    - Show this help message"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Run '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"