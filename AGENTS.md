# Agent Development Guide for Ontolutils

This file provides guidelines and commands for agentic coding agents working on the ontolutils repository.

## Build, Test, and Quality Commands

### Core Commands
```bash
# Install with development dependencies
pip install -e ".[test]"

# Run all tests
pytest

# Run tests with coverage
pytest --cov --cov-report=xml

# Run a single test file
pytest tests/test_classes.py

# Run a specific test function
pytest tests/test_classes.py::test_thing_creation

# Run tests with verbose output
pytest -v

# Lint code (pylint configured with lenient settings)
pylint ontolutils/

# Check for type issues (if mypy available)
python -m mypy ontolutils/

# Build package
python -m build

# Run comprehensive test suite (as in CI)
pytest --cov --cov-report=xml
```

### Test Configuration
- Tests located in `tests/` directory
- Test files follow pattern `test_*.py`
- Test functions follow pattern `def test_*()`
- pytest configuration in `pyproject.toml`
- Coverage excludes tests and dev files (see `.coveragerc`)

## Code Style Guidelines

### Import Organization
```python
# Standard library imports first
import datetime
import json
import logging
from typing import Optional, List, Union

# Third-party imports
import rdflib
import yaml
from pydantic import BaseModel, Field, model_validator

# Local imports
from ontolutils import Thing, urirefs, namespaces
from ontolutils.classes.decorator import URIRefManager
```

### Type Annotations
- Use type hints consistently throughout the codebase
- Import types from `typing` module
- Use `Optional[T]` for nullable fields
- Use `Union[T, List[T]]` for fields that accept single or multiple values
- Leverage `pydantic` for validation and serialization

### Class Design Patterns
```python
# Use decorators for ontology classes
@namespaces(prov="https://www.w3.org/ns/prov#",
            foaf="https://xmlns.com/foaf/0.1/")
@urirefs(Person='prov:Person',
         firstName='foaf:firstName',
         lastName='foaf:lastName')
class Person(Thing):
    firstName: str
    lastName: Optional[str] = Field(default=None, alias="last_name")
```

### Naming Conventions
- **Classes**: PascalCase (e.g., `Thing`, `Person`, `ValidationResult`)
- **Functions/Methods**: snake_case (e.g., `get_urirefs`, `serialize`, `validate_data`)
- **Variables**: snake_case (e.g., `person_data`, `graph`, `context`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_LOGGING_LEVEL`, `URL_SCHEMES`)
- **Private members**: underscore prefix (e.g., `_get_pyshacl`, `_cache`)

### Error Handling
```python
# Use specific exception types
try:
    import pyshacl as sh
    return sh
except ImportError as e:
    raise ImportError(
        "pyshacl is required but not installed"
    ) from e

# Validate input parameters
if not isinstance(data, dict):
    raise TypeError(f"Expected dict, got {type(data)}")

# Use logging for debug/info, exceptions for errors
logger.debug("Processing validation for %s", identifier)
```

### Logging
- Use the module-level logger: `logger = logging.getLogger('ontolutils')`
- Log levels: DEBUG for detailed info, INFO for general flow, WARNING for issues
- Format: `logger.debug("Message with %s placeholder", variable)`

### Pydantic Models
```python
# Use Field for configuration
class MyClass(BaseModel):
    name: str = Field(description="Human-readable name")
    optional_field: Optional[str] = Field(default=None)

    @model_validator(mode="before")
    def validate_data(cls, data):
        return data
```

### RDF/JSON-LD Patterns
- Use `rdflib` for RDF graph operations
- Leverage pydantic for JSON-LD serialization via `model_dump_jsonld()`
- Support multiple serialization formats: "json-ld", "ttl", "n3", "nt", "xml"
- Use `Thing.serialize(format="ttl")` for output

### File Structure Conventions
- **Main package**: `ontolutils/`
- **Core classes**: `ontolutils/classes/`
- **Examples**: `ontolutils/ex/` (organized by ontology)
- **Namespace library**: `ontolutils/namespacelib/`
- **Utilities**: `ontolutils/utils/`
- **Tests**: `tests/` (mirrors package structure)

### Code Quality Notes
- Pylint configured with lenient settings (fail-under=10)
- Line length warnings disabled
- Some naming convention warnings disabled for flexibility
- Focus on functional correctness over strict style compliance

## Development Workflow

1. **Set up environment**: `pip install -e ".[test]"`
2. **Run tests**: `pytest tests/your_test_file.py`
3. **Check linting**: `pylint ontolutils/your_module.py`
4. **Test coverage**: `pytest --cov ontolutils/your_module.py`
5. **Commit changes** (only when explicitly requested)
6. **Build for release**: `python -m build`

## Testing Guidelines

- Write unit tests for new functionality
- Test both happy path and error cases
- Use pytest fixtures for common setup
- Test serialization/deserialization round trips
- Validate RDF output structure when applicable
- Mock external dependencies when testing isolated components

## Key Dependencies

- **rdflib**: RDF graph manipulation
- **pydantic**: Data validation and serialization
- **PyYAML**: Configuration file support
- **pytest**: Testing framework
- Optional: **pyshacl** for SHACL validation

## Git and Pull Request Rules

- Work on a descriptive topic branch; never commit directly to `main`.
- Commit only when the user requests it. When publication is authorized, push
  the topic branch and create or update a pull request.
- Check the remote branch and existing open PRs before publishing to avoid
  duplicate branches or PRs. Target `main` unless a dependent PR needs a clearly
  identified base branch; link stacked PRs and retarget them after the base merges.
- Preserve unrelated staged, unstaged, and untracked work. Use an isolated
  worktree when a checkout contains mixed changes. Do not switch, reset, clean,
  or stash away another task's work to prepare a commit.
- Stage explicit, reviewed paths. Do not use blanket `git add .` or `git add -A`.
  Check the branch, `git status`, and the complete staged diff before committing;
  run `git diff --cached --check` and relevant tests.
- Keep commits focused and use messages that describe the resulting change.
  Verify the final commit range against its PR base, including inherited commits.
- Keep `.work/` local and ignored. Never stage, force-add, commit, or publish its
  notes, logs, environments, snapshots, or build output. Publish accepted source
  changes and guidance through normal project files only.
- Exclude credentials, generated sites, caches, local environments, experimental
  model outputs, and unrelated assets from commits. Add a new source or fixture
  deliberately rather than treating every untracked file as task output.
- PR descriptions should explain the problem, resulting behavior, and validation.
  Report actual test results and limitations; do not claim hosted CI, other Python
  versions, or fresh dependency resolution unless they were verified.
- Verify the pushed branch and PR URL after publication. Do not merge PRs,
  force-push, delete shared branches, publish packages, or change release versions
  unless the user explicitly authorizes that action.
