#!/bin/bash
# Test runner script for ollama_agents library

echo "=========================================="
echo "Ollama Agents Library Test Runner"
echo "=========================================="
echo ""

# Function to print colored output
print_success() {
    echo "✓ $1"
}

print_error() {
    echo "✗ $1"
}

print_info() {
    echo "→ $1"
}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "python3 is not installed"
    exit 1
fi

print_success "Python3 found: $(python3 --version)"

# Check if pytest is installed
if ! python3 -c "import pytest" 2>/dev/null; then
    print_error "pytest is not installed"
    print_info "Installing pytest..."
    pip install pytest pytest-asyncio
fi

print_success "pytest is installed"

# Check if library is importable
if ! python3 -c "import ollama_agents" 2>/dev/null; then
    print_error "ollama_agents library cannot be imported"
    print_info "Installing library in development mode..."
    pip install -e .
fi

print_success "ollama_agents library is importable"

echo ""
echo "=========================================="
echo "Running Tests"
echo "=========================================="
echo ""

# Run tests based on argument
case "$1" in
    "examples")
        print_info "Running example validation tests..."
        python3 -m pytest tests/test_examples.py -v
        ;;
    "all")
        print_info "Running all tests..."
        python3 -m pytest tests/ -v
        ;;
    "list")
        print_info "Listing all examples..."
        python3 run_examples.py --list
        ;;
    "run")
        if [ -z "$2" ]; then
            print_error "Please specify an example name"
            print_info "Available examples:"
            python3 run_examples.py --list
            exit 1
        fi
        print_info "Running example: $2"
        python3 run_examples.py "$2"
        ;;
    *)
        print_info "Usage: $0 {examples|all|list|run <example_name>}"
        echo ""
        echo "Options:"
        echo "  examples            Run example validation tests"
        echo "  all                 Run all tests"
        echo "  list                List all available examples"
        echo "  run <example_name>  Run a specific example"
        echo ""
        echo "Examples:"
        echo "  $0 examples"
        echo "  $0 all"
        echo "  $0 list"
        echo "  $0 run basic_examples"
        exit 1
        ;;
esac

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    print_success "All tests passed!"
else
    print_error "Some tests failed"
fi

exit $exit_code
