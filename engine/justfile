# Run unit tests only (fast — no media I/O)
test:
    pytest tests/unit -v

# Run the full suite including integration + golden-file tests
test-full:
    pytest tests -v --cov=src/pipeline

# Lint + type-check + run tests — the entire "CI" for this project (1.7)
check:
    ruff check .
    mypy src/pipeline
    just test

# Show status of all jobs in the local state store
status:
    python -m pipeline.cli db inspect
