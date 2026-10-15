# Panspermia

Ecosistema de vida artificial distribuido: agentes que evolucionan por selección natural (sin función de fitness), aprenden durante su vida con plasticidad hebbiana evolucionada y migran entre "islas" que cada participante ejecuta en su PC.

**Estado**: diseño cerrado, fase 0 (núcleo 2D) en desarrollo.

## Documentos

- [Especificación](docs/spec.md) — arquitectura, genoma, cerebro, red P2P, métricas, fases, salvaguardas.
- [Bibliografía](docs/bibliografia.md) — trabajos en los que se basa.
- [Decisiones](docs/decisiones.md) — registro de decisiones de diseño.

## Requisitos

- Python ≥ 3.11
- GPU NVIDIA con CUDA 12 (Linux o Windows con WSL2)

```bash
pip install -e ".[dev]"
pytest
```

## Licencias

Código: [Apache-2.0](LICENSE) · Documentación: CC BY 4.0 · Genomas compartidos: CC0.
