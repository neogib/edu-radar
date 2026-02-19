# Contributing

Thanks for contributing to EduRadar.

## Development Rules

- Keep backend changes aligned with FastAPI + SQLModel patterns.
- Use explicit typed code (Python and TypeScript).
- Preserve relational integrity and existing schema assumptions.

## Code Quality

Before opening a PR:

- Run formatting/linting.
- Run tests related to your changes.
- Keep changes focused and small when possible.

## Pull Requests

Include in your PR:

- What changed.
- Why it changed.
- Any migration or data-impact notes.
- Screenshots for UI changes (if relevant).

Use conventional commit messages and reference related issues when applicable.

## Data and Performance

This project handles large datasets and map views.

- Prefer efficient queries and small payloads.
- Avoid loading unnecessary data in API responses.
- Consider map rendering performance when changing frontend behavior.
