"""Panspermia: ecosistema evolutivo distribuido. Ver docs/spec.md."""
import os as _os

# Antes de que nadie importe JAX: sin preasignación del 75 % de la VRAM (en Windows/WSL el
# escritorio ocupa parte de la GPU) y operaciones de GPU deterministas (spec §Motor de isla).
_os.environ.setdefault("XLA_PYTHON_CLIENT_PREALLOCATE", "false")
if "--xla_gpu_deterministic_ops" not in _os.environ.get("XLA_FLAGS", ""):
    _os.environ["XLA_FLAGS"] = (_os.environ.get("XLA_FLAGS", "") + " --xla_gpu_deterministic_ops=true").strip()

from .config import SUBSTRATE_VERSION

__all__ = ["SUBSTRATE_VERSION"]
