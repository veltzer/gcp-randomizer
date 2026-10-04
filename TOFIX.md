# TOFIX

Findings from a code scan on 2026-10-04.

## Medium

- `pyproject.toml:10` - `webtest` is a runtime dependency, but only `tests/app_test.py:3` imports it; it ends up in the Cloud Run image via `uv sync --frozen --no-dev` (`Dockerfile:13`). Move it to the `dev` dependency group next to `types-WebTest`.
- `support/gjslint.cfg`, `support/jsl.conf` - configs for Closure Linter and JavaScript Lint, two dead JS linters nothing invokes; the repo has no JavaScript besides one inline `onclick` (`src/templates/index.html:58`). Delete `support/`.
- `src/templates/index.html:51-58`, `src/templates/general.html:15-20` - the `/general` free-form randomizer (`src/main.py:69`) is not linked from the landing page and has no link back, so it is reachable only by typing the URL. Add navigation links between the two pages.

## Low

- `pyproject.toml:26` - `mypy_path = "src:python:scripts"` names `python/` and `scripts/`, which do not exist here; set it to `"src"`.
- `src/main.py:71` - the `general()` docstring says "this is the root url"; it is the free-form list randomizer.
- `doc/TODO.txt`, `doc/DONE.txt` - both files are empty; delete them.
- `README.md:6` - the README never says what the app does (modes page, `/general` list shuffler) or how it is run and deployed (`gcloud_run_deploy.sh`, `.gcp.conf`). Add that through a `tera.snippets/main.md.tera` snippet, the template's extension point.
