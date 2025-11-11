This folder contains a VS Code devcontainer configuration for developing the `stock-option-filter` workspace inside an Ubuntu-based container.

What it provides
- Ubuntu 22.04 base image
- Non-root user `ubuntu` (uid/gid 1000) with passwordless sudo
- Python 3, pip, venv, git, build-essential
- Workspace mounted at `/workspace`

How to use (recommended)
1. Install the VS Code Remote - Containers extension.
2. In VS Code: `Remote-Containers: Open Folder in Container...` and choose this workspace folder.

Optional: Build & run locally with Docker (PowerShell)
```powershell
# From the repository root (where the .devcontainer folder is):
docker build -t stock-option-filter-dev -f .devcontainer/Dockerfile .

# Run an interactive container and mount the workspace (adjust paths as needed):
docker run --rm -it -v ${PWD}:/workspace -w /workspace stock-option-filter-dev
```

Notes
- The container creates a virtual environment `.venv` in the workspace during the `postCreateCommand` when opened with VS Code. If you run the container manually, activate the venv with:
  `source .venv/bin/activate`
- If you have a `requirements.txt` in the repo root, it will be installed automatically inside the venv after container creation.
