# envguard

> CLI tool to validate and diff `.env` files across environments before deployment.

---

## Installation

```bash
pip install envguard
```

Or with pipx:

```bash
pipx install envguard
```

---

## Usage

**Validate a `.env` file against a template:**

```bash
envguard validate --template .env.example --env .env.production
```

**Diff two environment files:**

```bash
envguard diff .env.staging .env.production
```

**Check for missing or extra keys before deploying:**

```bash
envguard check --strict --env .env.production
```

Example output:

```
✔ All required keys present
✘ Missing keys: DATABASE_URL, REDIS_HOST
⚠ Extra keys not in template: DEBUG_MODE
```

---

## Why envguard?

- Catch missing secrets before they cause production failures
- Compare environments to spot configuration drift
- Integrate into CI/CD pipelines with exit codes

---

## License

MIT © 2024 envguard contributors