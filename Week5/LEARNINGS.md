# Week 5 — Learnings

## What are `__pycache__` files?

`__pycache__` is a directory that Python automatically creates alongside your source files when modules are imported. It contains compiled bytecode files (`.pyc`), which are the interpreter's compiled version of your `.py` source files (e.g., `module.cpython-38.pyc`). Python generates these to speed up subsequent imports — instead of re-parsing and re-compiling the source each time, it can load the cached bytecode directly, as long as the source file hasn't changed since.

These files are entirely a build/runtime artifact of the interpreter — they are regenerated automatically whenever the corresponding source file changes, and are tied to the specific Python version that created them.

## Is it safe to add them to `.gitignore`?

Yes — it's not just safe, it's standard practice. `__pycache__` directories (and `.pyc`/`.pyo` files in general):

- Are machine- and interpreter-version-specific (a `.pyc` compiled under Python 3.8 won't necessarily be reused by Python 3.11)
- Are fully reproducible from the source `.py` files — nothing is lost by excluding them
- Add noise to diffs and repo size without providing any value to other contributors

A common `.gitignore` entry covering this is:

```
__pycache__/
*.py[cod]
```

Adding this prevents these auto-generated files from cluttering version control while keeping all the actual source code tracked.
