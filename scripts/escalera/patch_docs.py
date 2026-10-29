from pathlib import Path
R = Path("D:/Development/panspermia")
def sub(p, old, new):
    f = R / p; s = f.read_text(encoding="utf-8"); assert s.count(old) == 1, (p, old[:50]); f.write_text(s.replace(old, new), encoding="utf-8", newline="\n")
sub("CLAUDE.md", "Orden en la GPU: E2 → E9 → E1b (`scratchpad/chain_e9_e1b.sh`; E1b solo arranca si existe `runs/fase1d/e1b_ok`).",
    "Orden en la GPU: E2 → **escalera** → E9 → E1b (`scratchpad/chain_esc_e9_e1b.sh`; la escalera solo arranca si existe `runs/fase1d/escalera_ok`, y E1b si existe `runs/fase1d/e1b_ok`).")
sub("CLAUDE.md", "## Convenciones", """- **Escalera de complejidad (ADR-014, decisión del responsable del 18-10)**: rehacer el camino un interruptor cada vez, con una pregunta de sí o no por peldaño, prerregistrada en `docs/escalera/diseno.md`. Los peldaños son P0 mundo feliz → P1 peaje → P2 comida quieta → P3 hijos pagados → P4 comida móvil → P5 veneno.
  - Rama `escalera` (worktree `panspermia-escalera`, sustrato 2.1.0). Interruptores en `EnvParams` (`metabolism`, `max_age`, `repro_mode`, `attack_on`, `chem_on`, `signal_on`; la comida se apaga con `k_mean` 0 y se deja quieta con `drift` 0), con valores por defecto que dejan el mundo de siempre. Cola `experiments/fase1d/escalera.json`.
  - El responsable quiere un **árbol binario**: si un peldaño sale bien, el siguiente construye sobre esa variable; si sale mal, la descarta y prueba otra. Antes de dibujar las ramas, discutirlas con él.
  - Al proponer un experimento, decir de qué peldaño cuelga y qué única cosa añade.
  - El panel muestra cada peldaño (`escalera` en `docs/mapa.json`): planteamiento, vídeo de sus 5 mundos (`/api/video`) y resultados con el veredicto provisional.

## Convenciones""")
sub("README.md", "## Documentos", """**Escalera de complejidad** (ADR-014, rama `escalera`): rehace el camino **un interruptor cada vez**, desde un mundo feliz sin selección (P0), pasando por el peaje a vivir (P1), la comida (P2–P4) y los hijos pagados (P3), hasta la comida venenosa (P5). Cada peldaño responde a una pregunta de sí o no prerregistrada (`docs/escalera/diseno.md`). Se ejecuta tras E2 y antes de E9 y E1b.

## Documentos""")
sub("README.md", "PYTHONPATH=src python -m panspermia.panel runs/fase1d          # panel en vivo: árbol de posibilidades y avance (127.0.0.1:8766)",
    "PYTHONPATH=src python -m panspermia.panel runs/fase1d          # panel en vivo: escalera (planteamiento, vídeo y resultados por peldaño), árbol y avance (127.0.0.1:8766)")
s = (R / "docs/caminos.md").read_text(encoding="utf-8")
s = s.rstrip("\n") + "\n| Añadir varias variables por fase (fases 0, 1 y 1b) | Aparcado | No se puede atribuir el efecto a una variable; nunca hubo un control sin selección | Si la escalera reproduce, peldaño a peldaño, lo visto en la 1d | ADR-014, `docs/escalera/diseno.md` |\n"
(R / "docs/caminos.md").write_text(s, encoding="utf-8", newline="\n")
print("ok")
