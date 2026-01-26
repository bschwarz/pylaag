# Changelog

All notable changes to the laag Python library will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of laag Python library
- Core package (pylaag-core) with base classes and utilities
- OpenAPI package (pylaag-openapi) with full OpenAPI 3.0+ support
- RAML package (pylaag-raml) with RAML 1.0/0.8 support
- Smithy package (pylaag-smithy) with Smithy 2.0 support
- Comprehensive documentation including User Guide, API Reference, and Quick Reference
- Property-based testing with Hypothesis
- Type hints throughout the library
- Sample data generation from schemas
- Client code generation (Python, JavaScript, TypeScript)
- Curl command generation
- Extension property support across all formats
- Cross-format consistency validation

### Features by Package

#### pylaag-core
- LaagBase abstract class for all document types
- Error handling system (LaagError, ValidationError, ParseError, NotFoundError)
- Utility functions for nested object navigation (get_nested, set_nested, delete_nested)
- Extension property management

#### pylaag-openapi
- OpenAPIDocument class with JSON/YAML parsing and serialization
- PathManager for managing paths and operations
- ComponentManager for managing reusable components
- SampleGenerator for generating sample data from schemas
- CodeGenerator for generating client code in multiple languages
- CurlGenerator for generating curl commands
- Support for all HTTP methods (GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD, TRACE)
- Reference resolution for $ref pointers

#### pylaag-raml
- RAMLDocument class with YAML parsing and serialization
- ResourceManager for managing resources and methods
- TypeManager for managing type definitions
- Support for RAML 1.0 and 0.8 specifications

#### pylaag-smithy
- SmithyDocument class with JSON parsing and serialization
- ShapeManager for managing shapes
- TraitManager for managing traits
- OperationManager for managing operations
- Support for Smithy 2.0 specification

### Testing
- 312 tests with 100% pass rate
- 131 property-based tests with 100+ iterations each
- 93% code coverage (exceeds 80% minimum)
- Integration tests for cross-format consistency
- Unit tests for all major functionality

### Documentation
- Comprehensive User Guide with tutorials and examples
- Complete API Reference for all classes and methods
- Quick Reference for common tasks
- Migration Guide for TypeScript users
- README with quick start examples

### Development Tools
- uv for dependency management
- pytest for testing
- hypothesis for property-based testing
- mypy for type checking
- ruff for linting and formatting
- pytest-cov for coverage reporting

## [0.1.0] - YYYY-MM-DD

### Added
- Initial public release

---

## Version History

### Versioning Scheme

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backwards compatible manner
- **PATCH** version for backwards compatible bug fixes

### Release Process

1. Update CHANGELOG.md with release notes
2. Update version in pyproject.toml files
3. Run full test suite: `uv run pytest`
4. Run type checking: `uv run mypy packages`
5. Run linting: `uv run ruff check packages`
6. Build packages: `uv build`
7. Tag release: `git tag v0.1.0`
8. Push to repository: `git push && git push --tags`
9. Publish to PyPI: `uv publish`

### Support Policy

- **Current version**: Full support with bug fixes and new features
- **Previous minor version**: Security fixes and critical bug fixes only
- **Older versions**: No active support (upgrade recommended)

---

## Links

- [GitHub Repository](https://github.com/laag/laag-python)
- [Issue Tracker](https://github.com/laag/laag-python/issues)
- [Documentation](docs/README.md)
- [PyPI Package](https://pypi.org/project/pylaag-core/)
