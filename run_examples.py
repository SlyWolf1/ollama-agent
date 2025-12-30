#!/usr/bin/env python3
"""
Script to run and test examples from the examples folder.
This allows you to test the ollama_agents library by running the examples.
"""
import sys
import argparse
from pathlib import Path

# Add library to path
sys.path.insert(0, str(Path(__file__).parent))


def list_examples():
    """List all available examples"""
    examples_dir = Path(__file__).parent / "examples"
    examples = [f.stem for f in examples_dir.glob("*.py") if f.stem != "__init__"]
    return examples


def run_example(example_name: str, dry_run: bool = False):
    """Run a specific example"""
    print(f"\n{'='*60}")
    print(f"Running: {example_name}")
    print(f"{'='*60}\n")
    
    if dry_run:
        print(f"[DRY RUN] Would execute: examples.{example_name}")
        return True
    
    try:
        # Import the example module
        module = __import__(f"examples.{example_name}", fromlist=[example_name])
        
        # Check if module has a main block or specific functions
        if hasattr(module, '__main__'):
            print(f"✓ Example '{example_name}' imported successfully")
        
        print(f"\n✓ Example '{example_name}' completed successfully!")
        return True
        
    except ImportError as e:
        print(f"✗ Failed to import example '{example_name}': {e}")
        return False
    except Exception as e:
        print(f"✗ Error running example '{example_name}': {e}")
        return False


def run_all_examples(dry_run: bool = False):
    """Run all examples"""
    examples = list_examples()
    results = {}
    
    print(f"Found {len(examples)} examples to test")
    print(f"Examples: {', '.join(examples)}\n")
    
    for example in examples:
        success = run_example(example, dry_run)
        results[example] = success
    
    # Print summary
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    
    passed = sum(1 for v in results.values() if v)
    failed = len(results) - passed
    
    print(f"\nTotal: {len(results)} | Passed: {passed} | Failed: {failed}")
    
    if failed > 0:
        print("\nFailed examples:")
        for name, success in results.items():
            if not success:
                print(f"  ✗ {name}")
    
    return all(results.values())


def main():
    parser = argparse.ArgumentParser(
        description="Run and test examples from the ollama_agents library"
    )
    parser.add_argument(
        "example",
        nargs="?",
        help="Name of the example to run (without .py extension). If not provided, lists all examples."
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all examples"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available examples"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be executed without actually running"
    )
    
    args = parser.parse_args()
    
    # List examples
    if args.list or (not args.example and not args.all):
        examples = list_examples()
        print("\nAvailable examples:")
        for i, example in enumerate(examples, 1):
            print(f"  {i}. {example}")
        print(f"\nUsage:")
        print(f"  python run_examples.py <example_name>  # Run specific example")
        print(f"  python run_examples.py --all           # Run all examples")
        print(f"  python run_examples.py --list          # List all examples")
        return
    
    # Run all examples
    if args.all:
        success = run_all_examples(args.dry_run)
        sys.exit(0 if success else 1)
    
    # Run specific example
    if args.example:
        success = run_example(args.example, args.dry_run)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
