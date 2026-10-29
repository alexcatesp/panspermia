import json

p = 'docs/decisiones.md'; s = open(p, encoding='utf-8').read().rstrip('\n')
s += '''

## ADR-034 · 27-10-2026 · Réplica de C con la sonda mixta como primaria (decisión del panel 09)

**Contexto.** C (ADR-033) es negativo en la primaria (0/10) y tiene un indicio fuerte en la secundaria ΔD de la sonda mixta: +0,176 en 9/10, frente a −0,011 en Cbar (p = 0,0008). La supervivencia en la crianza invertida resultó innata (bitácora, 27-10, 21:35). Informes en `docs/escalera/panel/09_*`.

**Decisión del panel 09 (27-10-2026, entre las 21:37 y las 21:43), unánime en el cierre.**
1. **Veredicto de C:** negativo en la primaria. El ΔD es un indicio fuerte, exploratorio y sin confirmar. ΔD, P(comer buena) y la ventaja de ingesta salen de la misma sonda: no son tres confirmaciones. ρ(m_eff, resultado) no se cita, porque es en parte por construcción. No se habla de «aprendizaje de consecuencias» hasta la réplica.
2. **Ablación de δ en la sonda mixta**, sobre los 10 genomas de C con DELTA_ON=0 (solo observa). Regla fijada antes de ver los datos: ΔD sin δ menor que con δ real en ≥ 9/10 y mediana ≤ 0,088. **Si no confirma:** no hay réplica; el ΔD pasa a ser un efecto del genoma; (f) publicar la maduración, con b′ en espera.
3. **Si confirma, réplica:** P5-inmediato-C con semillas nuevas 10–19, mismo código (`escalera-c`, sustrato 3.8.0) y mismos parámetros (cola `c_rep.json`). Se compara con los **10 Cbar existentes**, que no se repiten, declarado antes de lanzar. Antes, comprobación de determinismo: C s0 a 100 épocas contra su checkpoint 100.
4. **Primaria (`diseno.md` v2.6)**, deben cumplirse todas:
   - ΔD > 0 en ≥ 9/10;
   - mediana de ΔD ≥ 0,08;
   - diferencia de medianas frente a Cbar > 0,08;
   - Mann-Whitney unilateral frente a Cbar, p < 0,01.
   Negativo con ≤ 7/10 positivos o con diferencia ≤ 0,08. 8/10 cuenta como indicio no confirmado. P(comer buena) y la ventaja de ingesta son descriptivas. Nulo: 3 semillas.
5. **b′ = B + C con δ solo en sucesos** (|r| > ε; r̄ se actualiza siempre; trazas `TRACE_TAU` 40). Será el **intento 15**. Ahora solo se construye y se prueba en CPU con pruebas ligeras; la suite completa va en la GPU libre.
   - Control positivo con una pista 40 pasos antes del bocado y un señuelo con la misma frecuencia.
   - ε se fija con el control positivo; k = 8,65 queda fijado por construcción.
   - Control: δ barajado solo en sucesos.
   - **Nada de b′ se calibra ni se lanza hasta que acabe la réplica.** Tocar δ es un diseño nuevo y gasta intento.
6. **Para el artículo (provisional):** «con una señal de valor fija puesta por nosotros, la plasticidad evolucionada aprende en vida qué comer entre alternativas ya a la vista, pero no a dónde ir; la supervivencia ante el alga dañina es innata». Si la ablación muestra un efecto parcial, se diría «la evolución con δ produce genomas que aprenden».

**Predicciones:** réplica con mediana de ΔD ≈ +0,10–0,12 y 7–8/10 positivos; P(pasa) ≈ 35–45 %. b′: P(pasa) ≈ 12 %.

**Ejecución:** ablación desde las 21:38 (`scratchpad/sonda_ablacion_c.sh`). Cadena `scratchpad/c_rep.sh` desde las 21:43: espera a la ablación y solo sigue si confirma (si no, marca `c_rep_no`); después determinismo, 10 mundos y sonda mixta. Logs en `runs/fase1d/c_rep_cadena.log` y `c_rep_mundos.log`; marcas `c_rep_hecho` y `c_rep_medidas_hechas`.
'''
open(p, 'w', encoding='utf-8').write(s + '\n')

p = 'docs/escalera/diseno.md'; s = open(p, encoding='utf-8').read()
anchor = '- **Resultado (27-10, 14:37): no pasa (0/10)'
i = s.index(anchor); j = s.index('\n', i) + 1
add = '''
**v2.6 · 27-10-2026, 21:43 · Réplica de C (ADR-034, decisión del panel 09).** Depende de la ablación de δ en la sonda mixta: ΔD con δ apagado menor que con δ real en ≥ 9/10 y mediana ≤ 0,088. Si no confirma, no hay réplica. P5-inmediato-C con semillas nuevas 10–19 (sustrato 3.8.0, mismos parámetros), comparado con los 10 Cbar existentes.
- **Primaria:** ΔD de la sonda mixta (aprende − congelado) > 0 en ≥ 9/10, **y** mediana ≥ 0,08, **y** diferencia de medianas frente a Cbar > 0,08, **y** Mann-Whitney unilateral frente a Cbar p < 0,01.
- **Negativo:** ≤ 7/10 o diferencia ≤ 0,08. **Indicio:** 8/10.
- **Descriptivas:** P(comer buena), ventaja de ingesta; nulo con 3 semillas.
- **Predicción del panel:** mediana ≈ +0,10–0,12; P(pasa) ≈ 35–45 %.
'''
s = s[:j] + add + s[j:]
open(p, 'w', encoding='utf-8').write(s)

p = 'docs/mapa.json'; m = json.load(open(p, encoding='utf-8'))
def find(n, parent=None):
    if isinstance(n, dict):
        if n.get('id') == 'modC':
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
node = {"id": "repC", "padre": "modC", "titulo": "Réplica de C (sonda mixta)", "corto": "ΔD con semillas nuevas", "estado": "en curso", "resultado": None,
        "anade": "nada: el mismo C con semillas nuevas 10–19; la primaria pasa a ser el ΔD de la sonda mixta (ADR-034)",
        "texto": "Panel 09 (27-10, 21:37–21:43), unánime. Antes, ablación de δ en la sonda (si ΔD no depende de δ, no hay réplica y se publica la maduración). Primaria (diseno v2.6): ΔD > 0 en ≥ 9/10, mediana ≥ 0,08, diferencia frente a los Cbar existentes > 0,08 y Mann-Whitney p < 0,01. Predicción: 35–45 %. Cadena scratchpad/c_rep.sh desde las 21:43 (determinismo, 10 mundos, sonda). Después, b′ (B + C con δ por sucesos), intento 15.",
        "ref": "docs/decisiones.md", "recurso": "GPU", "principal": True, "cola": "c_rep.json", "condicion": "P5-inmediato-C"}
assert isinstance(par, list)
par.insert(par.index(c) + 1, node)
open(p, 'w', encoding='utf-8').write(json.dumps(m, indent=1, ensure_ascii=False) + '\n')

p = 'docs/escalera/hoja_de_ruta.md'; s = open(p, encoding='utf-8').read()
old = [l for l in s.split('\n') if l.startswith('| **Plan B 1 · C**')][0]
s = s.replace(old, old + '\n| **Plan B 1b · Réplica de C** (en curso desde el 27-10, 21:43; ADR-034) | El mismo C, semillas 10–19; primaria: ΔD de la sonda mixta | ¿ΔD > 0 en ≥ 9/10, mediana ≥ 0,08 y por encima de Cbar (p < 0,01)? Antes, la ablación de δ | ~8 h | b′: B + C con δ por sucesos (intento 15) | Publicar la maduración |')
open(p, 'w', encoding='utf-8').write(s)

p = 'CLAUDE.md'; s = open(p, encoding='utf-8').read()
a = 'queda la sonda mixta. Panel 09 convocado.'
assert a in s
s = s.replace(a, 'queda la sonda mixta. **Panel 09 (ADR-034, 21:43):** ablación de δ en la sonda (`scratchpad/sonda_ablacion_c.sh`); si confirma, réplica de C con semillas 10–19 (cola `c_rep.json`, `scratchpad/c_rep.sh`, primaria en `diseno.md` v2.6, frente a los Cbar existentes; logs `runs/fase1d/c_rep_cadena.log`; marcas `c_rep_no`, `c_rep_hecho`, `c_rep_medidas_hechas`). Después, b′ (B + C con δ por sucesos, intento 15), que solo se construye en CPU hasta que acabe la réplica. **No tocar `panspermia-c` mientras corre.**')
open(p, 'w', encoding='utf-8').write(s)

p = 'docs/bitacora.md'; s = open(p, encoding='utf-8').read().rstrip('\n')
s += '''
- **21:39–21:43 · Panel 09, ronda 2 y cierre: unánime (ADR-034).** Ablación; si confirma, réplica de C (semillas 10–19) con el ΔD como primaria (≥ 9/10, mediana ≥ 0,08, diferencia frente a los Cbar existentes > 0,08, Mann-Whitney p < 0,01). Después, b′ como intento 15. Cadena `scratchpad/c_rep.sh` lanzada a las 21:43 y comprobada viva; espera a la ablación.
'''
open(p, 'w', encoding='utf-8').write(s + '\n')
print('ok')
