# Panel 09 · Ronda 2 y cierre (27-10-2026, 21:39–21:43)

**Propuesta del moderador:**
1. Ablación de δ en la sonda mixta, ya.
2. Si la ablación confirma, réplica de C con 10 semillas nuevas, con un único criterio.
3. Mientras corre la réplica, construir y probar b′ en CPU. Se lanza después, como intento 15.

## Biología
- Acepta (1)–(3), sin objeción bloqueante.
- Cbar: vale el existente, pero con el mismo código, la misma sonda y los mismos parámetros; cualquier diferencia se declara antes de mirar los datos.
- Lectura de la ablación: si ΔD baja sin desaparecer, el aprendizaje es en parte «prestado» por la evolución, y el artículo diría «la evolución con δ produce genomas que aprenden».
- Cautelas para b′:
  - el control positivo necesita un señuelo activo con la misma frecuencia;
  - ε se fija con el control positivo, nunca con E − X.
- En el cierre acepta el criterio final de Método: es el suyo de la ronda 1, endurecido con la mediana ≥ 0,08, y 8/10 queda como indicio.

## Método
- Acepta (1)–(3), sin objeción bloqueante. Nada de b′ se calibra ni se lanza hasta que acabe la réplica.
- **Criterio único** (deben cumplirse todos):
  - ΔD > 0 en ≥ 9/10 semillas nuevas de C;
  - mediana de ΔD ≥ 0,08;
  - diferencia de medianas frente a Cbar > 0,08;
  - Mann-Whitney unilateral frente a los 10 Cbar existentes, p < 0,01.
- Negativo: ≤ 7/10 positivos, o diferencia de medianas ≤ 0,08. Con 8/10, indicio no confirmado.
- **Si la ablación sale negativa:**
  - no se lanza la réplica;
  - el ΔD se reclasifica como efecto del genoma evolucionado con δ;
  - se pasa a (f), publicar la maduración, con b′ en espera; reformular cualquier réplica requiere otra ronda.

## Ingeniería
- Acepta (1)–(3) y retira que b′ haga de réplica, porque es otro mecanismo.
- Los dos cambios de b′ (δ por sucesos y trazas) dependen el uno del otro. Un brazo C-evento sin trazas sería informativo, pero no es bloqueante (cuesta ~8 h). Si b′ sale positivo, la ablación se hace después con TRACE_ON=0.
- Condiciones:
  - (i) declarar antes de lanzar que la réplica compara con los Cbar existentes;
  - (ii) congelar el commit y comprobar el determinismo con un mundo repetido.
- Réplica en serie, semillas 10–19: ~6–7 h más ~1 h de medidas.
- Con la GPU ocupada, en CPU solo diagnósticos ligeros; la suite de b′, después.

## Decisión (unánime, 21:43)
Ver ADR-034.
