# Copilot instructions for `futils`

## Build, test, and lint commands

Use Python 3.11 (see `mise.toml`) and install dependencies before running commands:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
```

Run the test suite:

```bash
pytest
```

Run a single test:

```bash
pytest tests/unit/movie/test_fixname.py::TestMovieFile::test_make_file_name
```

Build a source distribution:

```bash
python setup.py sdist
```

There is currently no repository-configured lint command/tool.

## High-level architecture

+ CLI entrypoint is `fu/futils.py` (Typer app). It wires top-level commands (`imgresize`, `moviefixname`, `tvshowfixnames`, `iterate`, `iteratefrom`, `index`, `index-removed`, `rm-indexed`, `config`) and mounts sub-apps: `exif` and `tv-show`.
- Most file operations are implemented as interactive workflows:
  1. scan input files,
  2. build a preview/order object (including conflicts/warnings),
  3. ask for user confirmation,
  4. execute file mutations (`os.replace`, `os.remove`, writes).
- Shared infrastructure:
  - `fu/utils/path.py` centralizes path/file helpers (`is_dir`, `is_file`, `path_files`, `get_file_name`, `get_file_ext`) and is used across commands.
  - `fu/utils/console.py` defines a Rich `Console` theme (`info`, `success`, `warning`, `error`) used for all user-facing output.
  - `fu/common/errors.py` contains shared domain exceptions used instead of generic errors in command logic.
- TV show renaming has two implementations:
  - Legacy flow in `fu/tvshow/fixname.py`, still used by `tvshowfixnames`.
  - New command-structured flow in `fu/commands/tv_show/fix_names.py`, exposed as `fu tv-show fix-names`.
- EXIF features are also split:
  - `fu/exif/app.py` exposes commands.
  - Metadata reading is handled by `fu/exif/models.py` (`ROExifImage`) and legacy `fu/exif/inspect_datetime.py`.

## Key conventions in this codebase

- Treat `path_files(...)` as **non-recursive**: commands generally operate on direct children of a directory, not nested trees.
- Validate filesystem inputs early using `is_dir`/`is_file` helpers and raise/print project-specific errors (`InvalidPathError`, `MissingRequiredDataError`) rather than introducing custom ad-hoc checks.
- Keep command code interactive-first: use `rich.prompt` (`Confirm`, `Prompt`, `IntPrompt`) and present a preview before destructive operations.
- Keep naming logic inside dataclass-like domain objects (`MovieFile`, `TVShowChapter`, `Episode`) using `make_file_name()` / `make_target_file_path()` methods.
- Tests are `pytest` + `unittest.mock`, with temporary filesystem fixtures; prefer mocking side effects (`os.replace`, prompts, `typer.launch`) rather than touching real user files.

## Command structure patterns — critical rules

There are two distinct command patterns in this codebase. **Choose the right one before writing any code.**

### Pattern A: Direct command (single operation with options)
Use when `fu <name>` does one thing, possibly with flags/options. Examples: `moviefixname`, `config`.

**Module structure:**
```
fu/commands/<name>/
  __init__.py
  <domain_module>.py     # pure domain/file logic, no CLI concerns
  commands.py            # Command subclass(es), one per distinct operation
```

**Wiring in `futils.py`:**
```python
from fu.commands.<name>.commands import FooCmd, BarCmd

@app.command()
def mycommand(...):
  """..."""
  FooCmd().execute()
```

- **No `app.py`** in the module — there is no Typer sub-app.
- **Do NOT use `app.add_typer()`** for direct commands.
- The `@app.command()` function in `futils.py` owns Typer option/argument parsing and instantiates the right `Command` subclass.

### Pattern B: Command group (multiple sub-commands)
Use when `fu <group> <subcommand>` exposes several related sub-commands. Examples: `tv-show`, `exif`.

**Module structure:**
```
fu/commands/<group>/
  __init__.py
  app.py                 # typer.Typer() instance + @app.command() functions
  <operation>.py         # Command subclass(es) for each sub-command
```

**Wiring in `futils.py`:**
```python
from fu.commands.<group> import app as <group>_app
app.add_typer(<group>_app.app, name='<group>')
```

- `app.py` exists **only** for command groups. Never create `app.py` for a direct command.
- Each function in `app.py` instantiates its `Command` subclass and calls `.execute()`.

### Deciding between the two patterns
Ask: does `fu <name>` do one thing (possibly with flags), or does it act as a namespace for sub-commands?
- Single operation with flags → **Pattern A** (`@app.command()` in `futils.py`, no `app.py`)
- Namespace with sub-commands → **Pattern B** (`app.add_typer()` in `futils.py`, module has `app.py`)

### Command class conventions (`fu/commands/base_command.py`)
- Each distinct operation gets its own `Command` subclass with a single `execute()` method.
- **Never encode operation mode as a constructor parameter** (e.g. `MyCmd(mode='edit')`). Use separate classes instead.
- Use `self.logger.info/warning/error()` — never call `console.print()` directly inside a `Command` subclass.
- Constructor signature: `def __init__(self, logger=None)` with `super().__init__("name", logger or RichConsoleLogger())`.
