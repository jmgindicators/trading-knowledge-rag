# Metodología de Trading — JMG Indicators

> Documento de demostración para el sistema RAG. Describe la filosofía y la estructura general de la metodología. Los parámetros concretos de los indicadores, los umbrales y las reglas exactas de entrada son propietarios y no se incluyen.

## 1. Visión del mercado

El mercado es un sistema profundamente emocional, donde la mayoría pierde por falta de disciplina, exceso de ego y ausencia de reglas. La ventaja surge precisamente de no participar en ese caos emocional.

Se trabaja con precisión: esperar a que el precio llegue a las zonas y actuar solo cuando la estructura confirma la hipótesis. No se persigue al mercado; se deja que el mercado venga.

## 2. La ventaja (edge)

La idea central es identificar **el inicio del impulso en zonas de oferta y demanda confirmadas por actividad institucional**, combinando varias herramientas que se confirman entre sí:

- Un indicador de **zonas estructurales** basado en el rango de la sesión nocturna: el mapa del terreno.
- Un indicador de **zonas de momentum** con rating de calidad: el timing de la entrada.
- Un indicador de **lectura de manos fuertes** que detecta operaciones de gran tamaño y su dirección: la confirmación.
- El análisis del **comportamiento de la vela**: cierre, mecha, agotamiento, absorción y rechazo.

Cuando los elementos se alinean, se ejecuta. Si falta uno, se espera.

## 3. Prioridad absoluta

La prioridad es proteger el capital. No se buscan entradas si el setup no se cumple al 100 %. Es preferible no operar antes que forzar una operación mediocre.

El "no operar" también es una operación ganadora cuando no hay condiciones.

## 4. Instrumento y plataforma

- **Instrumento**: futuros del Nasdaq, principalmente MNQ (Micro E-mini Nasdaq)
- **Plataforma**: NinjaTrader 8
- **Estilo**: intradía selectivo, pocas operaciones de alta calidad

## 5. Sistema de zonas (dos capas)

La operativa combina dos capas de zonas con funciones distintas. No se sustituyen: se complementan. La capa estructural indica DÓNDE puede haber un giro o un muro; la capa de momentum decide CUÁNDO entrar. Lo potente es cuando ambas se alinean.

### Capa 1 — Zonas estructurales

Función: el mapa del terreno. A partir del rango de la sesión nocturna se proyectan zonas de soporte y resistencia y niveles de extensión que sirven como contexto del día: cerca de un muro, de un giro potencial o de un nivel de liquidez.

### Capa 2 — Zonas de momentum

Función: el timing fino. Las zonas de oferta y demanda se clasifican por calidad y por alineación con el marco temporal superior. Se trabaja con un marco principal y se afina la entrada en marcos menores. Solo se consideran las zonas de mayor calidad.

## 6. Lectura de manos fuertes

Un indicador propio detecta operaciones de gran tamaño en el flujo de datos y estima su dirección (presión compradora o vendedora). Cada señal se clasifica por fuerza mediante varios filtros de calidad que tienen en cuenta el rechazo de la vela, la posición del cierre y la confluencia con señales recientes.

- **Señal fuerte**: todos los filtros cumplidos. Máxima convicción.
- **Señal media**: operativa válida con cautela.
- **Señal débil**: solo informativa.

Regla general: se opera con señales fuertes o medias en zonas relevantes.

## 7. Tipos de setup

Todos los setups exigen confirmación de manos fuertes en el sentido de la operación.

### Gatillo A — Absorción en zona (giro / inicio de impulso)

El precio entra en una zona de calidad, la vela pierde fuerza y aparece absorción. La entrada se sitúa al inicio del giro, con el stop al otro lado del extremo de la zona o de la mecha de rechazo. Oferta y demanda funcionan en espejo.

### Gatillo B — Ruptura con momentum (continuación)

El precio rompe una zona con confirmación de manos fuertes y busca los máximos o mínimos anteriores. Entrada a favor de la ruptura, stop al otro lado de la zona.

### Setup C — Smart Money Concepts (SMC)

Lectura de estructura de mercado (BOS, CHoCH), order blocks e imbalances, en confluencia con las zonas propias. Entrada en retesteo tras la ruptura de estructura, con confirmación de manos fuertes.

## 8. Condiciones para operar

Solo se entra cuando se cumplen todas las condiciones:

- Aparece uno de los gatillos con claridad
- La zona es de calidad suficiente en el marco principal
- Las manos fuertes confirman en la dirección del trade
- La vela y su cierre validan la dirección
- Las medias móviles (SMA20, SMA50, SMA200) son coherentes con la dirección
- El contexto estructural del día no contradice la entrada

Si falta cualquiera de estas condiciones, no se opera.

## 9. Gestión del riesgo

- **Riesgo máximo por operación**: fijo y definido antes de entrar; nunca se aumenta tras una pérdida
- **Ratio riesgo/beneficio objetivo**: mínimo 1:1, buscando 1:2 o superior siempre que sea posible
- **Stop loss inicial**: al otro lado de la zona o del extremo de la mecha de rechazo, según el setup
- **Tamaño de posición**: se calcula a partir del stop y del riesgo máximo, no al revés

## 10. Gestión de la salida (trailing con medias)

Una vez en operación, el stop se gestiona usando las medias móviles como referencia escalonada:

- **SMA20**: cuando el precio la cruza claramente a favor, el stop puede acompañarla (protección agresiva).
- **SMA50**: si el movimiento continúa con fuerza, el stop pasa a la SMA50 para dar más aire a la operación.
- **SMA200**: actúa como target principal e imán cuando el precio se aleja mucho de ella.
- **Cierre por falta de fuerza**: si el precio llega al objetivo sin fuerza, se cierra la operación sin esperar.

## 11. Horario operativo

No hay horario fijo: la operativa depende de cuándo el precio llega a las zonas, no del reloj. La paciencia es parte del edge.

## 12. Límites inquebrantables

Nunca:

- Operar por venganza después de una pérdida
- Aumentar el tamaño de posición tras una pérdida
- Improvisar entradas fuera de los setups definidos
- Escuchar al ego cuando dice "esta vez sí"
- Forzar una operación porque "llevo días sin operar"
- Cambiar de criterio a mitad de la operación

La disciplina es el escudo.

## 13. Gestión emocional y del ego

- **Pocas operaciones al día** como regla general. La calidad supera a la cantidad.
- **El ego no participa en la operativa**: se reconoce y se deja fuera de las decisiones. El mercado no debe nada.
- **Cabeza fría**: al entrar, la pérdida ya está aceptada. Al tomar beneficios, no se intenta exprimir el último tick.

## 14. Filosofía

Lema: **"Malo mori pugnando quam vivere genibus flexis"** (prefiero morir luchando que vivir arrodillado). Esta mentalidad guía tanto el trading como la forma de afrontar cualquier reto.

**Sin prisa pero sin pausa**: la consistencia diaria vale más que cualquier golpe puntual. El proceso está por encima del resultado de cada operación.

---

*Contenido educativo. No es recomendación de inversión. El trading de futuros conlleva un riesgo sustancial de pérdida.*
