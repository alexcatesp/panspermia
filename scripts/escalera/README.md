# Herramientas de la escalera (copia del scratchpad de las sesiones)

Scripts de medida, diagnóstico y cadenas de la escalera de complejidad (fase 1d), escritos durante las sesiones en el scratchpad temporal y copiados aquí el 29-10-2026 para que no se pierdan. **Solo observan**: no forman parte del núcleo ni influyen en la reproducción.

- **Medidas principales:**
  - `madura_alga.py`: trampa del alga invertida; `--scatter` es el examen barajado.
  - `madura_control.py`: H-control.
  - `sonda_mixta.py`: media población congelada en el mismo mundo.
  - `crianza_c.py`: crianza invertida.
  - `wmax.py`: saturación de pesos.
  - `mide_r2.py`: distribución de r en los mundos de C.
- **Cadenas** (`*.sh`): lanzan los mundos y las medidas de cada peldaño (por ejemplo `c.sh`, `c_rep.sh`, `bprima.sh`). Llevan rutas absolutas de WSL (`/mnt/c/.../scratchpad`), así que para reutilizarlas hay que cambiar `S=` por esta carpeta.
- **Análisis:** `analiza_c.py` y similares leen los `runs/fase1d/_*.jsonl`.

Cada script se ejecuta con el `PYTHONPATH` de la rama del peldaño (ver la bitácora y `CLAUDE.md`).
