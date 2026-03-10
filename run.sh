#!/bin/bash

# AI Triage System - Startup Script
# Usage: ./run.sh [backend|frontend|all]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Python is installed
check_python() {
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        print_error "Python is not installed. Please install Python 3.9 or higher."
        exit 1
    fi
    print_success "Python is installed"
}

# Check if dependencies are installed
check_dependencies() {
    if ! python -c "import fastapi" 2>/dev/null; then
        print_warning "Dependencies not installed. Installing..."
        pip install -r requirements.txt
        print_success "Dependencies installed"
    else
        print_success "Dependencies are installed"
    fi
}

# Run backend server
run_backend() {
    print_status "Starting FastAPI Backend Server..."
    print_status "API will be available at: http://localhost:8000"
    print_status "API Documentation: http://localhost:8000/docs"
    echo "----------------------------------------"
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
}

# Run frontend dashboard
run_frontend() {
    print_status "Starting Streamlit Dashboard..."
    print_status "Dashboard will be available at: http://localhost:8501"
    echo "----------------------------------------"
    streamlit run frontend/dashboard.py
}

# Run both (in background)
run_all() {
    print_status "Starting AI Triage System (Backend + Frontend)..."
    echo ""
    print_status "Backend will be available at: http://localhost:8000"
    print_status "Frontend will be available at: http://localhost:8501"
    echo ""
    print_warning "Press Ctrl+C to stop both services"
    echo "========================================"
    
    # Start backend in background
    uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    print_status "Backend started (PID: $BACKEND_PID)"
    
    # Wait for backend to start
    sleep 3
    
    # Start frontend
    streamlit run frontend/dashboard.py &
    FRONTEND_PID=$!
    print_status "Frontend started (PID: $FRONTEND_PID)"
    
    # Wait for user interrupt
    echo ""
    print_success "Both services are running!"
    print_status "Press Ctrl+C to stop"
    
    # Trap Ctrl+C to kill both processes
    trap "print_warning 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT
    
    wait
}

# Main script
main() {
    echo "========================================"
    echo "  AI Triage System - Startup Script"
    echo "========================================"
    echo ""
    
    check_python
    check_dependencies
    
    echo ""
    
    case "${1:-all}" in
        backend)
            run_backend
            ;;
        frontend)
            run_frontend
            ;;
        all)
            run_all
            ;;
        *)
            echo "Usage: $0 [backend|frontend|all]"
            echo ""
            echo "Commands:"
            echo "  backend   - Start only the FastAPI backend"
            echo "  frontend  - Start only the Streamlit dashboard"
            echo "  all       - Start both backend and frontend (default)"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
