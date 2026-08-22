#!/bin/bash
# ==============================================================================
# ▶  WHERE TO RUN : YOUR LOCAL MACHINE (the machine running LXD)
# ▶  WHEN         : Once — Phase 1, Task 4 — after Task 1 (repo scaffold) is done
# ▶  PURPOSE      : Create the 3 generic media-pipeline LXD containers:
#                     pipeline-structure, pipeline-speech, pipeline-render
#                   Bare containers only — base OS + Python + basic build
#                   tools + correct mounts/resource limits. NO module-specific
#                   dependencies (ffmpeg, whisper, torch, python-pptx, etc.)
#                   are installed here — that's Task 5, done incrementally as
#                   each module is actually implemented.
# ▶  HOW          : ./02_create_containers.sh
#                   ./02_create_containers.sh --dry-run     (preview only)
#                   ./02_create_containers.sh --repo-root /path/to/media-pipeline
#
# ▶  ASSUMES      : LXD is already installed and initialized (lxd init done),
#                   with the default "lxdbr0" bridge network available. This
#                   script does NOT install or initialize LXD itself.
# ▶  GPU           : No GPU passthrough configured — confirmed CPU-only
#                    machine. Whisper (Task 5) will run on CPU.
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

ok()     { echo -e "${GREEN}  ✓  $1${NC}"; }
info()   { echo -e "${CYAN}  →  $1${NC}"; }
warn()   { echo -e "${YELLOW}  !  $1${NC}"; }
error()  { echo -e "${RED}  ✗  $1${NC}" >&2; }
header() { echo -e "\n${CYAN}────────────────────────────────────────────────────────────${NC}\n  $1\n${CYAN}────────────────────────────────────────────────────────────${NC}"; }

# ── Args ─────────────────────────────────────────────────────────────────
DRY_RUN="false"
REPO_ROOT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)   DRY_RUN="true"; shift ;;
        --repo-root) REPO_ROOT="$2"; shift 2 ;;
        *) error "Unknown argument: $1"; exit 1 ;;
    esac
done

# Default repo root: this script lives at <repo>/bootstrap/02_create_containers.sh
if [ -z "$REPO_ROOT" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

WORKDIR_PATH="$REPO_ROOT/res/workdir"
RESOURCES_PATH="$REPO_ROOT/res/library"
PROFILES_DIR="$REPO_ROOT/infra/lxd/profiles"

echo -e "\n${CYAN}media-pipeline — Phase 1, Task 4: Create LXD Containers${NC}"
echo "Repo root       : $REPO_ROOT"
echo "Workdir mount   : $WORKDIR_PATH"
echo "Resources mount : $RESOURCES_PATH"
echo "Dry run         : $DRY_RUN"

# ── Container definitions: name | profile template file | needs /resources mount ──
# (mount access is already baked into each profile template — this list just
# drives which profile maps to which container name)
CONTAINERS=(
    "pipeline-structure:structure.yaml"
    "pipeline-speech:speech.yaml"
    "pipeline-render:render.yaml"
)

# ── Pre-flight checks ────────────────────────────────────────────────────

header "[1/6] Pre-flight checks"

if ! command -v lxc &> /dev/null; then
    error "LXD (lxc CLI) not found — install and initialize LXD first (lxd init)"
    exit 1
fi
ok "LXD is installed"

if ! lxc list &> /dev/null; then
    error "LXD does not appear to be initialized — run 'lxd init' first"
    exit 1
fi
ok "LXD is initialized"

if ! lxc network list 2>/dev/null | grep -q "lxdbr0"; then
    warn "Default bridge 'lxdbr0' not found — containers may still work if you have a different default network, but this is worth checking"
else
    ok "Default bridge 'lxdbr0' found"
fi

for d in "$WORKDIR_PATH" "$RESOURCES_PATH"; do
    if [ ! -d "$d" ]; then
        error "Expected directory does not exist: $d"
        error "Did you run bootstrap/01_setup_repo.py (Task 1) first?"
        exit 1
    fi
done
ok "res/workdir and res/library exist on host"

if [ ! -d "$PROFILES_DIR" ]; then
    error "Profile templates directory not found: $PROFILES_DIR"
    exit 1
fi
ok "Profile templates found at $PROFILES_DIR"

info "Checking host internet connectivity (needed later for apt-get inside containers) ..."
if curl -sI --max-time 5 https://pypi.org &> /dev/null; then
    ok "Host has internet access"
else
    warn "Host could not reach pypi.org — containers may fail to run apt-get/pip later"
    warn "Continuing anyway; connectivity is re-checked per-container before package install"
fi

# ── Create profiles + containers ────────────────────────────────────────

header "[2/6] Creating LXD profiles"

for entry in "${CONTAINERS[@]}"; do
    name="${entry%%:*}"
    template="${entry##*:}"
    profile_name="$name"
    template_path="$PROFILES_DIR/$template"

    if [ ! -f "$template_path" ]; then
        error "Missing profile template: $template_path"
        exit 1
    fi

    # Render template: substitute {{WORKDIR_PATH}} / {{RESOURCES_PATH}} with real paths
    rendered=$(sed \
        -e "s|{{WORKDIR_PATH}}|$WORKDIR_PATH|g" \
        -e "s|{{RESOURCES_PATH}}|$RESOURCES_PATH|g" \
        "$template_path")

    if [ "$DRY_RUN" = "true" ]; then
        info "[dry-run] would create/update profile '$profile_name' from $template"
        continue
    fi

    if lxc profile show "$profile_name" &> /dev/null; then
        info "Profile '$profile_name' already exists — updating"
        echo "$rendered" | lxc profile edit "$profile_name"
    else
        lxc profile create "$profile_name" &> /dev/null
        echo "$rendered" | lxc profile edit "$profile_name"
        ok "Profile '$profile_name' created"
    fi
done

header "[3/6] Launching containers"

for entry in "${CONTAINERS[@]}"; do
    name="${entry%%:*}"
    profile_name="$name"

    if [ "$DRY_RUN" = "true" ]; then
        info "[dry-run] would launch container '$name' with profile '$profile_name'"
        continue
    fi

    if lxc list --format csv -c n | grep -qx "$name"; then
        warn "Container '$name' already exists — skipping launch (delete it first to recreate)"
        continue
    fi

    info "Launching $name ..."
    lxc launch ubuntu:24.04 "$name" --profile "$profile_name"
    ok "Container '$name' launched"
done

if [ "$DRY_RUN" = "true" ]; then
    header "Dry run complete — nothing was created"
    exit 0
fi

header "[4/6] Waiting for containers to come up"
sleep 8
for entry in "${CONTAINERS[@]}"; do
    name="${entry%%:*}"
    if lxc exec "$name" -- true &> /dev/null; then
        ok "$name is responsive"
    else
        warn "$name did not respond yet — it may need a few more seconds"
    fi
done

# ── Verify each container can actually reach the internet BEFORE attempting
#    apt-get — fails fast with a clear message instead of a buried apt error ──

header "[5/6] Checking network connectivity inside each container"

# Uses bash's built-in /dev/tcp for a raw TCP connect test — deliberately NOT
# curl, since a bare ubuntu:24.04 image doesn't have curl installed yet
# (that only happens in step 6, which comes AFTER this check).

NETWORK_OK="true"
for entry in "${CONTAINERS[@]}"; do
    name="${entry%%:*}"
    info "Checking $name ..."
    if lxc exec "$name" -- bash -c "timeout 5 bash -c '</dev/tcp/pypi.org/443' 2>/dev/null"; then
        ok "$name has internet access"
    else
        error "$name cannot reach pypi.org — apt-get/pip will fail inside this container"
        NETWORK_OK="false"
    fi
done

if [ "$NETWORK_OK" = "false" ]; then
    error "One or more containers have no internet access."
    error "Check that lxdbr0 is NAT'd correctly and your host's own network is up:"
    error "  lxc network show lxdbr0"
    error "  lxc exec <container> -- ping -c 2 8.8.8.8"
    error "  lxc exec <container> -- cat /etc/resolv.conf   (DNS check)"
    exit 1
fi

# ── Baseline packages only — NOT module-specific deps (that's Task 5) ────

header "[6/6] Installing baseline packages (python3, pip, curl, build tools)"

for entry in "${CONTAINERS[@]}"; do
    name="${entry%%:*}"
    info "Provisioning $name ..."
    lxc exec "$name" -- bash -c "
        apt-get update -qq &&
        apt-get install -y -qq python3 python3-pip python3-venv curl ca-certificates build-essential
    " &> /dev/null
    ok "$name — baseline packages installed"
done

# ── Summary ──────────────────────────────────────────────────────────────

header "Done! Container status"
lxc list ^pipeline-

echo -e "
${BLUE}Mounts configured:${NC}
  pipeline-structure   /workdir (rw)   /resources (rw)
  pipeline-speech       /workdir (rw)
  pipeline-render        /workdir (rw)   /resources (ro)

${BLUE}Resource limits:${NC}
  pipeline-structure   2 CPU   2GB RAM   8GB disk
  pipeline-speech       3 CPU   4GB RAM   8GB disk
  pipeline-render        2 CPU   2GB RAM   8GB disk

${BLUE}What's installed right now:${NC} base Ubuntu 24.04 + python3 + pip + build tools only.
No ffmpeg, whisper, torch, or python-pptx yet — those are installed per-module
in Task 5, only when we actually implement the stage that needs them.

${BLUE}Useful commands:${NC}
  lxc list                              # see all containers
  lxc exec pipeline-structure -- bash   # shell into a container
  lxc info pipeline-speech              # resource usage for one container
  lxc stop <name>  /  lxc start <name>  # pause / resume a container

${BLUE}Next step:${NC} Task 5 — install per-module dependencies, incrementally,
as each pipeline module is actually implemented.
"
