# bootstrap/

One-time setup scripts. Run in order, once per machine:

1. `01_setup_repo.py`             — creates the folder structure (this script)
2. `02_create_containers.sh`      — creates the 3 LXD containers
3. `03_install_container_deps.sh` — installs dependencies inside each container
4. `04_verify_environment.sh`     — healthcheck: containers up, mounts working, GPU visible

Scripts 2-4 are not yet written — added when Task 1 is confirmed complete and
we move to container creation (Phase 1 execution sequence, steps 4-5).
