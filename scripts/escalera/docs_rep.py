import json


def sub(p, old, new):
    s = open(p, encoding='utf-8').read()
    assert s.count(old) == 1, (p, old[:60])
    open(p, 'w', encoding='utf-8').write(s.replace(old, new))


def append(p, text):
    s = open(p, encoding='utf-8').read().rstrip('\n')
    open(p, 'w', encoding='utf-8').write(s + '\n' + text.rstrip('\n') + '\n')


RES = ('ΔD de la sonda mixta (aprende − congelado) en las semillas 10–19: +0,080, +0,087, +0,210, +0,048, +0,156, +0,169, +0,157, +0,086, +0,252, +0,091 '
       '(**10/10 > 0**, mediana **+0,124**); Cbar existentes, mediana −0,011; diferencia de medianas **+0,134**; Mann-Whitney unilateral **p = 9·10⁻⁵**')

append('docs/bitacora.md', f'''
## 28-10-2026

- **04:16 · La réplica de C pasa (ADR-034, `diseno.md` v2.6): 4 de 4 condiciones.** Los 10 mundos nuevos terminaron a las 04:00 y la sonda mixta, a las 04:16. {RES}. Prueba de signos p = 0,001. Nulo (3 semillas, sin plasticidad): ΔD −0,021, −0,002, +0,015. Descriptivas: P(comer buena), aprende − congelado, mediana +0,137 (10/10 > 0; Cbar +0,036); P(comer en vacío) −0,007; ventaja de ingesta mediana +63 % (Cbar +27 %). La predicción del panel (mediana +0,10–0,12; P(pasa) 35–45 %) se queda corta. Con las 20 semillas de C: 19/20 positivas, mediana +0,163. **Conclusión firme:** con una señal de valor fija puesta por nosotros (δ), la plasticidad evolucionada aprende en vida qué comer entre alternativas a la vista; la ablación muestra que depende de δ; no hay aprendizaje de a dónde ir (primaria de C 0/10) y la supervivencia ante el alga dañina es innata. Siguiente, según ADR-034: b′ (B + C con δ por sucesos, intento 15), que se construye y prueba en CPU antes de lanzar nada. Datos en `runs/fase1d/_sonda_c_rep.jsonl` y `_sonda_c_rep_nulo.jsonl`.
''')

append('docs/decisiones.md', f'''
**Réplica (28-10, 04:16): pasa.** {RES}; nulo −0,021 a +0,015. El aprendizaje en vida de qué comer con δ queda confirmado. Siguiente: b′ (punto 5).
''')

sub('docs/escalera/diseno.md', '- **Predicción del panel:** mediana ≈ +0,10–0,12; P(pasa) ≈ 35–45 %.\n',
    '- **Predicción del panel:** mediana ≈ +0,10–0,12; P(pasa) ≈ 35–45 %.\n'
    f'- **Resultado (28-10, 04:16): pasa (4/4 condiciones).** {RES}. Nulo −0,021 a +0,015.\n')

p = 'docs/mapa.json'
m = json.load(open(p, encoding='utf-8'))


def find(n):
    if isinstance(n, dict):
        if n.get('id') == 'repC':
            return n
        for v in n.values():
            r = find(v)
            if r:
                return r
    elif isinstance(n, list):
        for v in n:
            r = find(v)
            if r:
                return r


node = find(m)
node['estado'] = 'hecho'
node['resultado'] = '✓'
node['texto'] += (' Resultado (28-10, 04:16): pasa. ΔD > 0 en 10/10 (mediana +0,124; Cbar −0,011; diferencia +0,134; Mann-Whitney p = 9·10⁻⁵); '
                  'nulo ≈ 0. Aprenden en vida qué comer con δ: confirmado. Siguiente: b′.')
open(p, 'w', encoding='utf-8').write(json.dumps(m, indent=1, ensure_ascii=False) + '\n')

sub('docs/escalera/hoja_de_ruta.md', '| **Plan B 1b · Réplica de C** (en curso desde el 27-10, 21:43; ADR-034)',
    '| **Plan B 1b · Réplica de C** ✓ (pasa, 28-10, 04:16: ΔD > 0 en 10/10, mediana +0,124, p = 9·10⁻⁵; ADR-034)')

sub('docs/caminos.md', '**C (27-10):** primaria 0/10, pero con δ real aprenden en vida qué comer (ΔD +0,176, 9/10; el barajado no)',
    '**C (27-10):** primaria 0/10, pero con δ real aprenden en vida qué comer (ΔD +0,176, 9/10; el barajado no); **réplica (28-10): confirmado** (10/10, mediana +0,124, p = 9·10⁻⁵). Falta a dónde ir: b′')

sub('README.md', 'Aprenden qué comer cuando están encima, no a dónde ir.',
    'Aprenden qué comer cuando están encima, no a dónde ir. **Una réplica con 10 mundos nuevos lo confirmó (28-10): aprenden en los 10**, y apagando la señal desaparece. El siguiente paso (b′) intenta que aprendan también a dónde ir.')

sub('CLAUDE.md', 'Después, b′ (B + C con δ por sucesos, intento 15), que solo se construye en CPU hasta que acabe la réplica.',
    '**La ablación confirmó (21:52) y la réplica pasa (28-10, 04:16: ΔD > 0 en 10/10, mediana +0,124, frente a Cbar p = 9·10⁻⁵): aprender qué comer con δ, confirmado.** Siguiente: b′ (B + C con δ por sucesos, intento 15), que se construye y prueba en CPU antes de lanzar nada.')
print('ok')
