import json


def sub(p, old, new):
    s = open(p, encoding='utf-8').read()
    assert s.count(old) == 1, (p, old[:60])
    open(p, 'w', encoding='utf-8').write(s.replace(old, new))


def append(p, text):
    s = open(p, encoding='utf-8').read().rstrip('\n')
    open(p, 'w', encoding='utf-8').write(s + '\n' + text.rstrip('\n') + '\n')


PRIM = ('H-control pasa; E − X (trampa del alga invertida, examen barajado) > 0 en ≥ 9/10 mundos de b′ y mediana ≥ +0,04; '
        'Mann-Whitney unilateral b′ > b′bar con p < 0,01 y diferencia de medianas ≥ +0,03')

append('docs/escalera/panel/10_bprima_ronda2.md', '''- **Biología (07:31):** acepta, sin objeción bloqueante. Hay que registrar que las semillas 0–9 dan el mismo mundo inicial que C. Sugiere escribir que 7–8/10, o una mediana entre 0,02 y 0,04, es indicio no concluyente.
- **Método (07:31):** acepta. Pide que k/2, si hace falta, se aplique a los 20 mundos (b′bar comparte k y sigue siendo el nulo válido) y que conste que la calibración (épocas 50–100) no mira el aprendizaje.
- **Ingeniería (07:31):** acepta. Advierte que W_MAX se mira en la época 100 en la calibración y en la 300 en la tanda: si la saturación crece con la edad, la calibración puede dar luz verde y el resultado acabar no interpretable. Basta con registrarlo.

## Decisión (unánime, 07:31)
La síntesis, con las tres notas. Ver ADR-035.
''')

append('docs/decisiones.md', f'''
## ADR-035 · 28-10-2026 · b′: primaria y lanzamiento (decisión del panel 10)

**Contexto.** La réplica de C pasa (ADR-034). b′ está construido (punto 5 de ADR-034; intento 15): rama `escalera-bprima` (worktree `panspermia-bprima`, sustrato 3.9.0), con `DELTA_EVENT_EPS` (δ solo en los pasos con |r| > ε; r̄ se actualiza siempre). Con ε = 0 es C bit a bit.
- **Medida de r en P5-inmediato-C:** |r| es bimodal. Las migajas (< 0,001) son el 66 % de los sucesos; los bocados buenos completos (+0,5), el 31 %; los malos (−0,75), el 1,2 %. **ε = 0,05**: el control positivo da lo mismo con 0,01 y con 0,2.
- **Control positivo** (`tests/test_bprima.py`): A − B +0,60 con b′ y trazas, frente a +0,05 de C con trazas y −0,09 de b′ sin trazas. El orden es A > señuelo > B.
- **Dos pegas:** todos los pesos suben a la vez (deriva común), y la k = 8,65 «por construcción» se apoyaba en migajas: con ella, cada bocado completo satura m a ±1.
- Informes en `docs/escalera/panel/10_*`.

**Decisión del panel 10 (28-10-2026, 07:29–07:31), unánime.**
1. **b′ tal cual:** ε = 0,05, k = 8,65 (m binaria con el signo del resultado en los sucesos), TRACE_TAU 40. No se toca δ: tocarlo gasta intento. La deriva común se mide como descriptiva.
2. **Tanda:** P5-inmediato con b′ (DELTA_ON 1) y b′bar (DELTA_ON 2, δ filtrado y barajado), los dos con trazas y ε; 10 + 10 mundos con las semillas 0–9 (el mismo mundo inicial que C y Cbar, que no son independientes de C), 300 épocas, desde cero. Colas `bprimacal865.json`, `bprimacal433.json` y `bprima.json` (esta la genera la cadena).
3. **Calibración solo de viabilidad:** 3 mundos (s0–s2) × 100 épocas. Es viable si no hay extinción, la población media de las épocas 50–100 es ≥ 1.000 y la mediana de la fracción de pesos plásticos en W_MAX en la época 100 es < 50 %. Si no es viable, un único ajuste: k/2 para los 20 mundos. No se mira ninguna medida de aprendizaje.
4. **Primaria (`diseno.md` v2.7), deben cumplirse todas:** {PRIM}.
5. **Negativo:** E − X > 0 en ≤ 6/10, o mediana ≤ +0,02. 7–8/10, o una mediana entre +0,02 y +0,04, es indicio no concluyente, sin segunda tanda automática.
6. **Guarda:** ΔD de la sonda mixta > 0 en ≥ 9/10 (en C fue 10/10). No es vía de éxito; si falla, se registra «las trazas dañan lo de C».
7. **No interpretable:** mediana de mundos > 50 % de pesos plásticos en W_MAX en la época 300. La calibración lo mira en la época 100 y puede crecer con la edad (Ingeniería).
8. **Descriptivas, sin puerta:** |w| medio, fracción en W_MAX (referencia: C 1–13 %, Cbar ≈ 1 %, `_wmax_c.jsonl`), f_mod, fracción de m saturada, fracción de pasos con suceso y P(comer buena). Sin crianza (en C era innata). La ablación de las trazas en la sonda se hace solo si b′ pasa.

**Predicciones:** P(pasa) ≈ 12–15 % (Método da un rango de 8–20 %); la guarda ΔD, ≈ 80 %.

**Ejecución:** cadena `scratchpad/bprima.sh`, lanzada a las 07:37 y comprobada viva. Espera a la suite en GPU (`runs/fase1d/suite_bprima.log`, desde las 07:29), calibra, lanza los 20 mundos y mide (trampa en los dos brazos, H-control, sonda mixta, nulo y saturación con `scratchpad/wmax.py`). Logs en `runs/fase1d/bprima_cadena.log` y `bprima.log`; marcas `bprima_hecho` y `bprima_medidas_hechas`. `madura_alga.with_brain` pone la traza a cero, como al nacer; sin `TRACE_ON` no cambia nada.
''')

sub('docs/escalera/diseno.md', '- **Resultado (28-10, 04:16): pasa (4/4 condiciones).** ',
    '- **Resultado (28-10, 04:16): pasa (4/4 condiciones).** ')
s = open('docs/escalera/diseno.md', encoding='utf-8').read()
i = s.index('- **Resultado (28-10, 04:16): pasa (4/4 condiciones).** ')
j = s.index('\n', i) + 1
s = s[:j] + f'''
**v2.7 · 28-10-2026, 07:31 · b′: δ solo en sucesos + trazas (ADR-035, decisión del panel 10; intento 15).** P5-inmediato con TRACE_ON 1 (τ 40), DELTA_EVENT_EPS 0,05 y k 8,65 (k/2 si la calibración de viabilidad falla). b′ (δ real) y b′bar (δ filtrado y barajado), semillas 0–9 × 300 épocas.
- **Primaria:** {PRIM}.
- **Negativo:** ≤ 6/10 o mediana ≤ +0,02. **Indicio no concluyente:** 7–8/10, o mediana entre +0,02 y +0,04.
- **Guarda:** ΔD de la sonda mixta > 0 en ≥ 9/10 (no es vía de éxito). **No interpretable:** mediana > 50 % de pesos plásticos en W_MAX en la época 300.
- **Descriptivas:** |w|, W_MAX, f_mod, m saturada, fracción de pasos con suceso, P(comer buena).
- **Predicción del panel:** P(pasa) ≈ 12–15 %; guarda ≈ 80 %.
''' + s[j:]
open('docs/escalera/diseno.md', 'w', encoding='utf-8').write(s)

p = 'docs/mapa.json'
m = json.load(open(p, encoding='utf-8'))


def find(n, parent=None):
    if isinstance(n, dict):
        if n.get('id') == 'repC':
            return n, parent
        for v in n.values():
            r = find(v, n)
            if r:
                return r
    elif isinstance(n, list):
        for v in n:
            r = find(v, n)
            if r:
                return r


c, par = find(m)
par.insert(par.index(c) + 1, {
    "id": "bprima", "padre": "repC", "titulo": "b′: δ por sucesos + trazas", "corto": "a dónde ir (intento 15)", "estado": "en curso",
    "resultado": None,
    "anade": "trazas de elegibilidad (τ 40) y δ solo en los pasos con bocado o cobro (|r| > 0,05), sobre C",
    "texto": ("Panel 10 (28-10, 07:29–07:31), unánime. Control positivo: A − B +0,60 frente a +0,05 de C (sin trazas, −0,09). "
              f"Primaria (diseno v2.7): {PRIM}. Guarda ΔD ≥ 9/10. Predicción 12–15 %. Cadena scratchpad/bprima.sh desde las 07:37 "
              "(suite, calibración de viabilidad, 20 mundos, medidas)."),
    "ref": "docs/decisiones.md", "recurso": "GPU", "principal": True, "cola": "bprima.json", "condicion": "P5-inmediato-bprima"})
open(p, 'w', encoding='utf-8').write(json.dumps(m, indent=1, ensure_ascii=False) + '\n')

s = open('docs/escalera/hoja_de_ruta.md', encoding='utf-8').read()
old = [l for l in s.split('\n') if l.startswith('| **Plan B 1b · Réplica de C**')][0]
s = s.replace(old, old + '\n| **Plan B 2 · b′** (en curso desde el 28-10, 07:37; ADR-035; intento 15) | Trazas (τ 40) + δ solo en sucesos (ε 0,05), sobre C | ¿Aprenden a dónde ir? Trampa del alga invertida: E − X > 0 en ≥ 9/10, mediana ≥ 0,04, por encima de b′bar (p < 0,01) | ~12 h | Ablación de las trazas; después, ¿a dónde ir con veneno diferido? | Publicar: aprender qué comer (C) y la maduración |')
open('docs/escalera/hoja_de_ruta.md', 'w', encoding='utf-8').write(s)

sub('CLAUDE.md', 'Siguiente: b′ (B + C con δ por sucesos, intento 15), que se construye y prueba en CPU antes de lanzar nada.',
    '**b′ (ADR-035, panel 10, 28-10):** rama `escalera-bprima` (worktree `panspermia-bprima`, sustrato 3.9.0, `config.DELTA_EVENT_EPS` 0,05: δ solo en sucesos; con 0 es C bit a bit; `tests/test_bprima.py`), con trazas. Cadena `scratchpad/bprima.sh` desde las 07:37 (suite, calibración de viabilidad `bprimacal865.json`/`433`, 20 mundos de `bprima.json`, medidas; logs `runs/fase1d/bprima_cadena.log` y `bprima.log`; marcas `bprima_hecho` y `bprima_medidas_hechas`). Primaria en `diseno.md` v2.7. Saturación de pesos con `scratchpad/wmax.py`. **No tocar `panspermia-bprima` mientras corre.**')

sub('README.md', 'El siguiente paso (b′) intenta que aprendan también a dónde ir.',
    'El siguiente paso (b′, en marcha desde el 28-10) intenta que aprendan también a dónde ir: la señal solo habla cuando comen, y una «memoria corta» de cada conexión (trazas) le da el mérito a lo que vieron hasta unos 40 pasos antes.')

append('docs/bitacora.md', f'''
### 07:29–07:37 (28-10) · Panel 10: b′ tal cual y lanzamiento (ADR-035, unánime)

Ronda 1 a las 07:29–07:30; ronda 2 y cierre a las 07:31 (`docs/escalera/panel/10_*`). b′ tal cual (ε 0,05, k 8,65, τ 40). b′ y b′bar, semillas 0–9 × 300 épocas, tras una calibración solo de viabilidad (3 × 100 épocas; un único ajuste, k/2). Primaria (`diseno.md` v2.7): {PRIM}. Guarda: ΔD ≥ 9/10. Predicción: 12–15 %. Referencia de saturación (`scratchpad/wmax.py`, época 300): C tiene un 1–13 % de pesos plásticos en W_MAX y Cbar ≈ 1 % (`_wmax_c.jsonl`). `madura_alga.with_brain` pone la traza a cero (sin efecto en C). Cadena `scratchpad/bprima.sh` lanzada a las 07:37 y comprobada viva; espera a la suite.
''')
print('ok')
