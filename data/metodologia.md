# Metodología de Trading — Jose Miguel Gonzalez

## 1. Visión del mercado

El mercado es un sistema profundamente emocional, donde la mayoría pierde por falta de disciplina, exceso de ego y ausencia de reglas. Mi ventaja surge precisamente de no participar en ese caos emocional.

Trabajo con precisión quirúrgica: espero que el precio llegue a mis zonas y actúo solo cuando la estructura confirma mi hipótesis. No persigo el mercado, dejo que el mercado venga a mí.

## 2. Mi ventaja (Edge)

Mi edge consiste en identificar **el inicio del impulso en zonas de oferta y demanda confirmadas por volumen institucional**, combinando varias herramientas que se confirman entre sí:

- Indicador propio de **zonas macro / estructurales** basado en el rango de la sesión nocturna (TradingZonesFuturos): el mapa del terreno.
- Indicador propio de **zonas de momentum** (JmgUnizones Pro) en 15 min, afinado en 1 y 5 min: el timing fino de la entrada.
- Indicador propio de **lectura de manos fuertes** (BigTradesDir, volumen institucional con detección direccional): confirmación obligatoria.
- Análisis de **comportamiento de la vela**: cierre, mecha, agotamiento, absorción y rechazo.

Cuando los elementos se alinean, ejecuto. Si falta uno, espero.

## 3. Prioridad absoluta

Mi prioridad es proteger el capital. No busco entradas si mi setup no se cumple al 100%. Prefiero no operar antes que forzar una operación mediocre.

El "no operar" es también una operación ganadora cuando no hay condiciones.

## 4. Instrumento y plataforma

- **Instrumento**: futuros del NQ (Nasdaq), principalmente MNQ (Micro E-mini Nasdaq)
- **Plataforma**: NinjaTrader 8
- **Estilo**: scalper, una operación al día
- **Cuenta operativa**: Bulenox Master Account (fondeada profesionalmente)

## 5. Sistema de zonas (dos capas)

Mi operativa combina DOS capas de zonas con funciones distintas. No se sustituyen: se complementan. La capa macro me dice DÓNDE puede haber un cambio de tendencia o un muro; la capa de momentum decide CUÁNDO entrar. Lo potente es cuando ambas se alinean.

### Capa 1 — Zonas macro / estructurales (TradingZonesFuturos, Initial Balance nocturno)

Función: el mapa del terreno. Me indica dónde puede haber un cambio de tendencia, un muro, o niveles relevantes en el contexto del día.

- **Recogida de datos**: desde las 21:00 (cierre Wall Street) hasta las 06:00 hora de Madrid (cuando cierran las bolsas asiáticas). Durante este periodo, el indicador captura el máximo y el mínimo del rango.
- **Initial Balance (IB)**: el rango high-low de esa sesión nocturna se considera válido si su tamaño es de al menos 10 puntos.
- **Zonas operativas**: una vez cerrada la fase de recogida, el indicador dibuja dos zonas rectangulares sombreadas:
  - **Zona alta (resistencia)**: entre IB High + 62.5 y IB High + 125. Color azul.
  - **Zona baja (soporte)**: entre IB Low - 62.5 e IB Low - 125. Color azul.
- **Niveles de extensión** (objetivos y extremos):
  - Extensión 50% del rango (arriba y abajo): línea verde discontinua, target intermedio.
  - Extensión 100% del rango (arriba y abajo): línea roja discontinua, extremo del movimiento.
- **Rol actual**: contexto macro. Define el sesgo estructural del día (dónde estoy en el rango: cerca de un muro, de un giro potencial, de un nivel de liquidez).

### Capa 2 — Zonas de momentum (JmgUnizones Pro + BigTradesDir)

Función: el timing fino. Me indica cuándo entrar, en el momento inicial del impulso, para cubrirme justo del mínimo (en demanda) o máximo (en oferta) siguiente.

- **JmgUnizones Pro** detecta zonas de oferta y demanda con rating de calidad (estrellas) y confirmación de timeframe superior (HTF).
- **Rating mínimo de zona válida**: 2 estrellas. No opero zonas de 1 estrella (mismo criterio de exigencia que con BigTradesDir: media o fuerte).
- **Marco principal**: 15 min. Es el timeframe que manda para definir la zona y el sesgo de la entrada.
- **Marcos de afinado**: 1 y 5 min, para clavar el gatillo exacto dentro de la zona de 15 min según el volumen.
- **OB 50%**: la línea media del order block que pinta el indicador dentro de la zona. Es el nivel de referencia donde espero la reacción (absorción o ruptura).
- **BigTradesDir**: lectura de manos fuertes (institucional). OBLIGATORIO en todas las entradas. Sin confirmación de BigTradesDir no hay entrada.

## 6. Lectura de manos fuertes (Indicador BigTradesDir)

Mi indicador propio detecta operaciones grandes (institucionales) en el flujo de datos por segundo y determina su dirección.

### Detección

- Trabaja sobre datos por segundo
- Tres niveles de volumen para clasificar el tamaño de la operación: 900, 1.500 y 2.500 contratos
- Para cada big trade, calcula la dirección:
  - Si el cierre de la vela está en la mitad superior o igual al mid → **compra agresiva** (color verde)
  - Si el cierre está en la mitad inferior → **venta agresiva** (color rojo)

### Filtros de calidad

No todas las big trades son señal. Aplico tres filtros y clasifico la fuerza:

- **Filtro 1 — Pin bar / vela de rechazo**: la mecha debe ser al menos el doble del cuerpo y representar al menos el 40% del rango total. Indica rechazo en una dirección y recuperación en la contraria.
- **Filtro 2 — Cierre fuerte**: para una compra, el cierre debe estar en el tercio superior del rango (>= 66%). Para una venta, en el tercio inferior (<= 34%). Cuanto más cerca del extremo, más convicción.
- **Filtro 3 — Confluencia**: al menos 2 de las últimas 3 big trades deben ir en la misma dirección. Una sola operación grande es ruido; un patrón de operaciones es presión institucional real.

### Clasificación de la señal

- **Señal fuerte (3 estrellas)**: los 3 filtros cumplidos. Flecha + elipse grande. Máxima convicción.
- **Señal media (2 estrellas)**: 2 filtros cumplidos. Flecha + elipse normal. Operativa válida con cautela.
- **Señal débil (1 estrella)**: 1 filtro o menos. Solo elipse pequeña, sin flecha. No opero salvo confluencia muy fuerte con otras herramientas.

Mi regla: opero principalmente con señales fuertes o medias en zonas relevantes.

## 7. Tipos de setup que ejecuto

Dos gatillos de entrada principales. Los dos exigen confirmación de BigTradesDir (señal media o fuerte, en sentido del trade). Sin esa confirmación, no opero.

### Gatillo A — Absorción en el OB 50% (giro / inicio de impulso)

Evolución del antiguo "Setup B — zona como muro / rebote". Es uno de mis setups preferidos.

- El precio entra en la zona de oferta/demanda de Unizones en 15 min (mínimo 2 estrellas).
- Llega a la línea del OB 50% (mitad del order block).
- La vela en ese nivel empieza a desinflarse (pierde fuerza, agotamiento).
- Bajo a 1 o 5 min según el volumen para afinar el gatillo.
- Pongo la entrada en 15 min sobre la **absorción** de la vela: el principio del giro. Así me sitúo en el momento inicial del impulso y me cubro justo del mínimo (en demanda) o máximo (en oferta) siguiente.
- **BigTradesDir** debe confirmar en sentido del giro.
- **Simetría** (oferta y demanda en espejo limpio): en demanda, vela desinflándose en el OB 50% = giro alcista, entrada long. En oferta, vela desinflándose en el OB 50% = giro bajista, entrada short.
- Stop al otro lado del extremo de la mecha de rechazo / del OB.

### Gatillo B — Ruptura de OB con momentum (continuación hacia máximos/mínimos previos)

Evolución del antiguo "Setup A — ruptura de zona con volumen".

- Señal de BigTradesDir en 1 min (en oferta o demanda).
- El precio viene a romper el OB para salir en la dirección que describe ese OB.
- Esa ruptura confirmada con manos fuertes es una señal muy potente: alta probabilidad de que el precio busque máximos (o mínimos) anteriores. Momentum.
- Entrada a favor de la ruptura, stop al otro lado del OB.

### Setup C — Smart Money Concepts (SMC)

- Lectura de estructura de mercado: BOS (break of structure), CHoCH (change of character)
- Identificación de zonas de oferta y demanda institucionales
- Order blocks y bloques de imbalance
- Confluencia con mis zonas propias (Unizones / IB) para confirmar
- Entrada en retesteo de zona SMC tras BOS, con confirmación de manos fuertes

## 8. Condiciones obligatorias para operar

Solo entro cuando se cumplen TODAS estas condiciones:

- Aparece uno de mis gatillos con claridad (A, B o C)
- Zona de Unizones válida en 15 min (marco principal), con rating mínimo de 2 estrellas y, cuando aplica, confirmación HTF
- El volumen institucional (BigTradesDir) confirma con señal media o fuerte en la dirección del trade (obligatorio, sin excepción)
- La vela y su cierre validan la dirección (absorción en gatillo A, cierre de ruptura en gatillo B)
- Las medias móviles SMA20 y SMA50 muestran zonas de rebote coherentes con la dirección
- Existe distancia suficiente respecto a la SMA200 para que actúe como imán o target
- El sesgo macro del IB no contradice la entrada

Si falta cualquiera de estas condiciones, no opero. Punto.

## 9. Gestión del riesgo

- **Riesgo máximo por operación**: 300 USD
- **Ratio riesgo/beneficio objetivo**: mínimo 1:1, busco siempre que sea posible 1:2 o superior
- **Stop loss inicial**: al otro lado de la zona o del extremo de la mecha de rechazo, según el setup
- **Tamaño de posición**: calculado en función del stop loss y del riesgo máximo, no al revés

## 10. Gestión de la salida (Trailing con medias)

Una vez en operación, gestiono el stop usando las medias móviles como referencia escalonada:

- **SMA20**: cuando el precio la cruza claramente a mi favor, muevo el stop a la SMA20 (protección agresiva). Cierra el trade si el precio vuelve a romper la SMA20 contra mí.
- **SMA50**: si el precio sigue avanzando y rompe la SMA50 a mi favor, muevo el stop a la SMA50. Esto deja respiración a la operación cuando hay momentum.
- **SMA200**: es mi **target principal**. Las medias actúan como imanes cuando hay distancia excesiva entre el precio y la SMA200. Mi expectativa es que el precio llegue a la SMA200.
- **Cierre por falta de fuerza**: si el precio alcanza la SMA200 pero llega sin fuerza (sin volumen, vela débil), cierro la operación inmediatamente. No espero a ver "qué pasa".

## 11. Horario operativo

No tengo horarios establecidos. Mi operativa depende de cuándo el precio llega a mis zonas, no del reloj.

- **Inicio de la jornada operativa**: 06:00 hora de Madrid. Es cuando mi indicador termina de recoger los datos de las sesiones nocturnas (EEUU + Asia) y las zonas operativas quedan definidas.
- **A partir de las 06:00**: el setup puede aparecer en cualquier momento del día. La paciencia es parte del edge.

## 12. Límites inquebrantables

Nunca haré:

- Operar por venganza después de una pérdida
- Aumentar el tamaño de posición tras una pérdida (revenge trading disfrazado)
- Improvisar entradas fuera de mis gatillos A, B o C
- Escuchar al ego cuando me dice "esta vez sí"
- Forzar una operación porque "llevo días sin operar"
- Cambiar de criterio a media operación

Mi disciplina es mi escudo.

## 13. Gestión emocional y del ego

- **Una sola operación al día** como regla general. La calidad supera a la cantidad.
- **Segunda operación**: solo si aparece un setup todavía más claro y limpio que el primero. Es excepcional, no la norma.
- **Mi ego no participa en la operativa**: lo reconozco, lo escucho, y lo dejo fuera del proceso de decisión. El mercado no me debe nada.
- **Cabeza fría y corazón en paz**: cuando entro, ya he aceptado la pérdida si toca. Si toca tomar beneficios, los tomo sin tratar de exprimir el último tick.

## 14. Filosofía personal

Mi lema operativo y vital es: **"Malo Mori Pugnando Quam Vivere Genuflexus"** (prefiero morir luchando antes que vivir de rodillas). Esta mentalidad guía no solo mi trading, sino mi forma de afrontar cualquier reto.

**Sin prisa pero sin pausa**: la consistencia diaria vale más que cualquier golpe puntual. El trader que perdura no es el que más gana en una sesión, sino el que sigue ahí dentro de cinco años con cabeza fría y cuenta creciendo.

El proceso está por encima del resultado de cada trade. Si el proceso es bueno y se repite con disciplina, el resultado es matemático.
