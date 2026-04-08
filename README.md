# 🧩 Test de Intruso Lógico – Razonamiento Abstracto

## Basado en el Wisconsin Card Sorting Test (WCST) y el Category Test

---

## 🧠 ¿Qué mide este test?

Evalúa la **capacidad de categorización**, el **razonamiento abstracto** y la **flexibilidad cognitiva** en pacientes con daño cerebral adquirido (ACV) o enfermedades neurodegenerativas. El paciente debe identificar, entre cuatro imágenes, cuál **NO pertenece** a la misma categoría que las otras tres (tarea de “odd‑one‑out”).

### Fundamento clínico – Gold Standard

La tarea de intruso lógico se fundamenta en tests neuropsicológicos clásicos:

- **Wisconsin Card Sorting Test (WCST)**: Considerado el **gold standard** para evaluar la formación de conceptos abstractos y la capacidad de cambiar de estrategia cognitiva (flexibilidad mental).
- **Category Test (de la Batería Halstead‑Reitan)**: Mide el aprendizaje de conceptos abstractos y la resolución de problemas complejos.
- **Nonverbal Semantic Test (NVST)**: Incluye un subtest de clasificación semántica no verbal mediante una tarea de “odd‑one‑out” con imágenes, especialmente útil en pacientes con disfunción del sistema nervioso central.

Nuestra versión adapta la tarea al **castellano** (variedad argentina/uruguaya), utilizando imágenes de objetos cotidianos, formas geométricas y atributos perceptuales, divididas en tres tipos de series: **semánticas** (10), **perceptuales** (5) y **funcionales** (5).

---

## 👥 Población objetivo

- Pacientes con **ACV en hemisferio izquierdo o derecho** que afecten funciones ejecutivas.
- Personas con **demencia frontotemporal**, **enfermedad de Alzheimer** o **Parkinson** con deterioro cognitivo.
- Pacientes con **traumatismo encéfalo craneano** (TEC) que requieran evaluación de razonamiento abstracto.
- **Sujetos control** para obtener datos normativos.

El diseño es accesible para personas con **hemiparesia** (uso de una sola mano, botones grandes, sin doble clic) y **trastornos visuales** (alto contraste, imágenes grandes, fuente grande).

---

## ♿ Accesibilidad y adaptación para pacientes con ACV

El software sigue las **pautas de accesibilidad de Material Design** y recomendaciones para pacientes neurológicos:

| Característica | Implementación |
|----------------|----------------|
| **Botones grandes** | Tamaño de imagen: 300×300 píxeles. Botones de respuesta: 300×360 (imagen+texto) o 300×300 (solo imagen). |
| **Alto contraste** | Fondo #F5F5F5 (gris muy claro), botones blancos con borde negro, texto negro sobre fondo blanco o gris claro. |
| **Sin doble clic** | La respuesta se registra al primer clic. |
| **Navegación por teclado** | No implementada por defecto (4 opciones), pero se puede usar el mouse fácilmente. |
| **Ventana maximizable** | El test se abre en pantalla completa o maximizada (compatible con Windows, Linux y macOS). |
| **Placeholders** | Si falta una imagen, se muestra un recuadro gris con el nombre de la palabra en fuente grande (24 px). |
| **Tiempo de reacción** | Se registra automáticamente desde que se muestra el ítem hasta la respuesta. |
| **Feedback visual** | No hay sonidos (evita estrés), solo cambios visuales. |

### Adaptación cultural al castellano

Los 20 ítems fueron diseñados con palabras y objetos reconocibles en Argentina y Uruguay. Las categorías incluyen:

- **Semánticas**: animales, frutas, transporte, herramientas, ropa, insectos, muebles, electrodomésticos, oficina, juguetes.
- **Perceptuales**: color, forma, tamaño, orientación, textura.
- **Funcionales**: cocina, jardinería, escritura, limpieza, música.

Ejemplo de serie semántica: *perro, gato, mesa, pájaro* → el intruso es *mesa*.

---

## 🎮 Modos de uso del sistema

El usuario puede seleccionar el **modo visual** antes de comenzar, con tres niveles de dificultad:

| Modo visual | Dificultad | Descripción |
|-------------|------------|-------------|
| Imagen + Texto | Fácil | Cada opción se muestra como imagen y texto. |
| Solo imagen | Medio | Cada opción es solo una imagen (sin texto). |
| Solo texto | Difícil | Cada opción es solo texto (sin imágenes). |

Esta flexibilidad permite ajustar el test al grado de deterioro del paciente.

---

## 📊 ¿Qué métricas se obtienen?

Por cada ítem se registra:

- `acierto` (1 = correcto, 0 = error)
- `tiempo_reaccion_ms` (milisegundos desde que aparece la serie hasta la respuesta)

Al finalizar el test, se calcula:

- **Total de aciertos** (máximo 20)
- **Precisión** (aciertos/20)
- **Tiempo promedio, mediana, desviación estándar, mínimo y máximo**
- **Puntuación Z** comparada con controles sanos (media = 18.0, DE = 1.5) – valores propuestos, basados en literatura similar.
- **Interpretación clínica** según puntos de corte:
  - ≥ 17 aciertos → *Rendimiento dentro de lo normal*
  - 15‑16 aciertos → *Deterioro leve (seguimiento recomendado)*
  - < 15 aciertos → *Deterioro moderado a severo (derivar a especialista)*

Además se genera un **histograma de tiempos de reacción** y se muestra la **curva ROC** del test (estimada con sensibilidad 85% y especificidad 90% para el punto de corte 15/20).

---

## 📁 Formato de salida (JSON y TXT)

Al finalizar el test, se crea automáticamente la carpeta `/results` (si no existe) y dentro se guardan dos archivos con el nombre:

`{id_paciente}_{fecha_hora}.json` y `{id_paciente}_{fecha_hora}.txt`

### Estructura del JSON

```json
{
  "id_paciente": "PAC001",
  "edad": 65,
  "genero": "Masculino",
  "fecha": "2026-04-06T10:30:00",
  "modo_visual": "imagen_texto",
  "test": "Intruso Lógico (Razonamiento Abstracto)",
  "total_items": 20,
  "aciertos": 18,
  "precision": 0.9,
  "tiempo_respuesta_promedio_ms": 3450.2,
  "tiempo_respuesta_desviacion_ms": 450.1,
  "tiempo_respuesta_mediana_ms": 3300.0,
  "tiempo_respuesta_min_ms": 2100.0,
  "tiempo_respuesta_max_ms": 5200.0,
  "tiempos_individuales_ms": [3450, 3300, ...],
  "z_aciertos_control": 0.0,
  "interpretacion": "Rendimiento dentro de lo normal",
  "detalle_respuestas": [
    {
      "serie": 1,
      "categoria": "Animales",
      "opciones": ["perro", "gato", "mesa", "pájaro"],
      "respuesta_correcta": "mesa",
      "acierto": 1,
      "tiempo_reaccion_ms": 3450.2
    },
    ...
  ]
}
