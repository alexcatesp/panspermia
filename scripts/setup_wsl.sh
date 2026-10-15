#!/usr/bin/env bash
# Prepara el entorno de Panspermia dentro de WSL2 (Ubuntu 24.04) con JAX sobre CUDA 12.
# Uso (desde WSL, en la raíz del repo): bash scripts/setup_wsl.sh
# Nota: se usa pip y no `uv pip install` porque uv 0.13.1 rechazaba al azar ruedas NVIDIA válidas
# ("Invalid Wheel-Version") y devolvía código 0.
set -euo pipefail

VENV="${PANSPERMIA_VENV:-$HOME/.venvs/panspermia}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"

if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
# shellcheck disable=SC1091
source "$HOME/.local/bin/env"
[ -x "$VENV/bin/python" ] || uv venv --seed -p 3.12 "$VENV"
# shellcheck disable=SC1091
source "$VENV/bin/activate"
python -m pip --version >/dev/null 2>&1 || uv pip install pip
python -m pip install --upgrade pip
python -m pip install -e "$REPO[dev]"

python - <<'EOF'
import jax
print("jax", jax.__version__, jax.devices())
EOF
