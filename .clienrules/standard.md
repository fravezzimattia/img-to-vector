## Python clean code standards

### Mandatory project rules

- always use dataclasses or typed dicts.
- never yolo dictionary access.

### Code style and readability

- follow pep 8 and keep formatting consistent.
- write clear, intention-revealing names for variables, functions, classes, and modules.
- prefer explicit, readable code over clever one-liners.
- keep functions and methods small, focused, and at a single level of abstraction.
- avoid deep nesting; use guard clauses and early returns.
- remove dead code, commented-out code, and unused imports.
- avoid magic numbers and magic strings; extract named constants.

### Typing and data modeling

- use type hints on all public functions, methods, class attributes, and module-level constants.
- use dataclass or typeddict for structured data instead of ad-hoc dictionaries.
- prefer explicit return types, including `None` where relevant.
- using `Any` is strictly forbidden; if you have to type something as Any, always tell the user.
- using `object` is very not recommended; if you can generate a custom type.
- use enums for finite sets of values.

### Functions and classes

- each function should do one thing and do it well.
- limit function parameters; group related values into dataclasses when needed.
- avoid boolean flag parameters that change behavior; split into separate functions.
- keep class responsibilities cohesive (single responsibility principle).
- prefer composition over inheritance unless inheritance is clearly justified.
- keep public APIs minimal and well-defined.

### Error handling and reliability

- never swallow exceptions silently.
- catch specific exceptions, not broad `Exception`, unless re-raising with context.
- fail fast on invalid input with clear, actionable error messages.
- validate external input at boundaries.
- use custom exception types for domain-level errors when useful.

### Dictionary and collection safety

- never access dictionary keys unsafely.
- prefer `dict.get()` with explicit fallback, membership checks (`in`), or typed structures.
- handle missing or malformed data explicitly.
- avoid mutating collections while iterating unless intentionally controlled.

### Documentation and comments

- write docstrings for public modules, classes, and functions.
- keep docstrings concise and focused on behavior, inputs, outputs, and side effects.
- comment the *why*, not the *what*.
- keep comments synchronized with code changes.

### Testing

- write tests for business logic and edge cases.
- keep tests deterministic, isolated, and readable.
- use descriptive test names that explain behavior.
- test outcomes, not implementation details.
- include negative-path and error-handling tests.

### Logging and observability

- use structured, meaningful logs for important events and failures.
- never log secrets, tokens, passwords, or personal sensitive data.
- prefer contextual logging over noisy logs.

### Project structure and dependencies

- maintain a clear module structure with separated concerns (domain, services, helpers, io).
- keep side effects at the boundaries (api calls, filesystem, databases, network).
- avoid circular dependencies.
- prefer standard library and simple solutions before adding new dependencies.
- remove or upgrade stale dependencies regularly.

### Performance and maintainability

- optimize only after measuring.
- prioritize correctness and clarity before micro-optimizations.
- avoid premature abstraction; refactor when patterns are stable.
- keep backward compatibility in shared interfaces unless explicitly planned.

### Security basics

- never hardcode secrets or credentials.
- read sensitive configuration from environment or secure vaults.
- sanitize and validate all external inputs.
- use safe defaults and least privilege principles.

### Python best practices

- target a clearly defined python version (default should be 3.12, check .pyproject.toml) and keep compatibility explicit.
- use a consistent formatter/linter setup (e.g. ruff) and enforce it in pre-commit.
- keep imports sorted, explicit, and grouped (stdlib, third-party, local).
- prefer `pathlib.Path` over manual string path manipulation.
- use `with` context managers for files, locks, and external resources.
- use timezone-aware datetimes; avoid naive `datetime` in domain logic.
- use `None` as default for mutable arguments and initialize inside the function.
- prefer iterators/generators for large streams of data to reduce memory usage.
- avoid side effects in comprehensions; keep comprehensions simple and readable.
- prefer `collections` and stdlib utilities before custom implementations.
- model constants with `Enum`/module constants instead of ad-hoc literals.
- keep environment/config parsing centralized in a dedicated config layer.
- use dependency injection at boundaries to simplify testing and decouple services.
- avoid global mutable state; prefer explicit state passing.
- design modules with clear public APIs (`__all__` when useful).
- keep `__init__.py` lightweight and free of heavy side effects.
- write idempotent startup/initialization code where possible.
- make external calls (http, db, cloud) resilient with retries/timeouts and bounded backoff.
- always set explicit timeout values for network operations.
- prefer structured response/domain models over raw dictionaries.
- define serialization/deserialization boundaries explicitly.
- validate input data close to entry points (api, cli, queue consumers, files).
- raise domain-specific exceptions and map them at boundaries.
- keep logging levels meaningful (`debug`, `info`, `warning`, `error`, `critical`).
- include correlation/request identifiers in logs for traceability.
- keep tests fast: unit tests by default, integration tests for boundaries.
- use fixtures/factories to remove duplication in tests.
- freeze time, random seeds, and external dependencies to keep tests deterministic.
- document module purpose and architecture decisions in concise ADR/readme notes.
- prefer small, incremental refactors over big-bang rewrites.
- keep dependency versions constrained and review changelogs before upgrades.
