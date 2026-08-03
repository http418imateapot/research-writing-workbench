# Installation and Local Build

## Prerequisites

- Git.
- Python 3.12 or newer for repository development.
- A local environment that supports Agent Skills for installation.

The runtime CLIs use only the Python standard library. Development validation uses `requirements-dev.txt`.

## Build on Windows

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\build.bat --check
.\build.bat
```

## Build on Linux or macOS

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
./build.sh --check
./build.sh
```

`build.py --check` validates and assembles in temporary storage without replacing `dist/`. A full build replaces only the resolved repository-root `dist` directory after staging succeeds.

## Install a Skill

Use a generated self-contained directory under `dist/agents-skills/<skill>/`. For a repository-scoped Codex installation, copy the chosen directory to `.agents/skills/<skill>/` in the target repository. For a user-scoped installation, use the Skill location supported by the current host. Restart or refresh the host if it does not detect the new Skill automatically.

The source directories under `skills/` are authoring inputs and may rely on build-time dependency injection. Install generated directories, not source directories, when a self-contained package is required.

The `dist/claude/*.zip` files are deterministic one-root archives. Their presence does not assert official compatibility with any particular product or version; verify the target platform's current import requirements before use.

## Verify the release candidate

```powershell
Get-FileHash dist\*.zip -Algorithm SHA256
Get-Content dist\checksums.sha256
git ls-files dist
```

`git ls-files dist` must print nothing. A local release candidate is not a GitHub Release and has not been published merely because the build succeeds.
