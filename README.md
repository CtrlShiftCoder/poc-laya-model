# Evaluación de Laya

Repositorio de evaluación para **Laya**, el modelo de decisión no-autorregresivo open-source (Apache-2.0). Este proyecto proporciona herramientas completas para evaluar Laya en benchmarks y casos de uso reales, con soporte completo para español.

[![CI](https://github.com/tu-org/laya-eval/workflows/CI/badge.svg)](https://github.com/tu-org/laya-eval/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ¿Qué es Laya?

Laya es un modelo de decisión **System 1** no-autorregresivo que:
- Responde preguntas tipadas (choice, score, noul) sobre un estado en un solo forward pass (~33ms)
- Nunca genera texto, eliminando errores de parsing y alucinaciones
- Proporciona probabilidades matemáticamente calibradas mediante RLCD
- Soporta 100+ idiomas incluyendo español

**Características clave:**
- ⚡ Latencia ultra-baja: ~33ms por decisión
- 🎯 Probabilidades calibradas: entrenado con strictly proper scoring rules
- 🌍 Multilingüe: soporta español, inglés y 100+ idiomas
- 🔓 Open-source: Apache-2.0, alternativa a Jev (TypeSafe AI)
- 📦 Fácil integración: API Python y servidor HTTP

## Inicio Rápido

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/tu-org/laya-eval.git
cd laya-eval

# Setup completo (instala uv + dependencias)
make setup

# O manualmente con uv
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python 3.11
uv pip install -e ".[dev]"
```

### Uso Básico

```bash
# Ejecutar PoC 1: Benchmark offline
make poc1

# Ejecutar PoC 2: Triage de tickets
make poc2

# Ejecutar tests
make test

# Formatear código
make format
```

### Ejemplo en Python

```python
from src.backends import create_backend
from src.backends.base import DecisionRequest

# Crear backend Laya local
backend = create_backend("laya_local", config={"model": "multilingual"})

# Definir pregunta
state = {
    "subject": "Error al procesar pago",
    "body": "La transacción fue rechazada pero mi tarjeta está activa."
}

questions = {
    "category": {
        "type": "choice",
        "instructions": "¿A qué categoría pertenece este ticket?",
        "criteria": {
            "facturación": "Pagos, facturas, cobros",
            "técnico": "Bugs, errores del sistema",
            "ventas": "Consultas comerciales",
        }
    }
}

# Obtener predicción
request = DecisionRequest(state=state, questions=questions)
response = backend.predict(request)

print(f"Categoría: {response.answers['category']['choice']}")
print(f"Confianza: {response.answers['category']['confidence']:.2%}")
```

## Estructura del Proyecto

```
laya-eval/
├── src/
│   ├── backends/           # Abstracciones de backends (laya_local, laya_http, jev_http)
│   ├── metrics/            # Cálculo de métricas (accuracy, F1, ECE, Brier, etc.)
│   ├── poc1_benchmark/     # PoC 1: Benchmark offline con datasets públicos
│   ├── poc2_triage/        # PoC 2: Triage de tickets en shadow mode
│   ├── reporting/          # Generación de reportes
│   ├── utils/              # Utilidades compartidas
│   └── config.py           # Configuración centralizada
│
├── tests/
│   ├── unit/               # Tests unitarios (métricas, backends, config)
│   └── integration/        # Tests de integración
│
├── data/
│   ├── poc1_datasets/      # Datasets para benchmark (XNLI, MASSIVE, etc.)
│   └── poc2_tickets/       # Tickets sintéticos en español
│
├── config/
│   └── default.yaml        # Configuración por defecto
│
├── docs/                   # Documentación detallada en español
│   ├── 01-que-es-laya.md          # Arquitectura y conceptos
│   ├── 02-como-preguntar.md       # Guía de prompting
│   ├── 03-metricas.md             # Explicación de métricas
│   ├── 04-poc1-benchmark.md       # Documentación PoC 1
│   ├── 05-poc2-triage.md          # Documentación PoC 2
│   ├── 06-comparar-con-jev.md     # Comparación con Jev
│   └── 07-buenas-practicas.md     # Mejores prácticas
│
├── reports/                # Reportes generados
│   ├── poc1/               # Resultados de benchmark
│   └── poc2/               # Resultados de triage
│
├── pyproject.toml          # Configuración del proyecto y dependencias
├── Makefile                # Comandos comunes
├── docker-compose.yml      # Servicios Docker (laya-serve, runner)
└── README.md               # Este archivo
```

### Descripción de Carpetas

- **`src/backends/`**: Implementaciones de backends de decisión
  - `base.py`: Interfaces abstractas y utilidades (RateLimiter, CostLedger)
  - `laya_local.py`: Backend local usando Python API de Laya
  - `http.py`: Backends HTTP para laya-serve y Jev

- **`src/metrics/`**: Módulo de métricas de evaluación
  - `core.py`: Funciones de cálculo (accuracy, F1, Brier, ECE, MAE, etc.)
  - `aggregation.py`: Agregación y resumen de métricas

- **`src/poc1_benchmark/`**: Evaluación offline en datasets públicos
  - `data_loaders.py`: Cargadores para XNLI, MASSIVE, Emotion
  - `runner.py`: Orquestador de benchmarks
  - `run.py`: Punto de entrada

- **`src/poc2_triage/`**: Triage de tickets en shadow mode
  - `synthetic_data.py`: Dataset sintético de 20 tickets en español
  - `runner.py`: Lógica de triage y evaluación
  - `finetuning.py`: Guía y utilidades de fine-tuning
  - `run.py`: Punto de entrada

- **`docs/`**: Documentación técnica en español (ver sección Documentación)

## PoCs Implementados

### PoC 1: Benchmark Offline

Evaluación en datasets públicos:
- **XNLI Spanish**: Entailment en español (50 muestras)
- **MASSIVE Spanish**: Intent classification en español (30 muestras)
- **Emotion English**: Clasificación de emociones (50 muestras)

**Métricas evaluadas:**
- Calidad: Accuracy, Macro F1, baselines
- Calibración: Brier Score, ECE
- Consistencia: Paráfrasis y orden de opciones
- Rendimiento: Latencia (P50/P95/P99), throughput
- Negocio: Cobertura de automatización por umbral

```bash
make poc1
# Resultados en: reports/poc1/
```

### PoC 2: Triage de Tickets en Shadow Mode

Simulación de triage automático de tickets de soporte:
- **Dataset**: 20 tickets sintéticos en español
- **Tareas**: Categorización, scoring de urgencia, detección de necesidad humana
- **Routing**: Decisión automática de automatizar vs. escalar
- **Métricas**: Tasa de automatización, precisión, cobertura

**Categorías:**
- Facturación
- Técnico
- Ventas
- Cancelación
- Otro

```bash
make poc2
# Resultados en: reports/poc2/
```

## Backends Disponibles

| Backend | Descripción | Uso |
|---------|-------------|-----|
| `laya_local` | In-process Python | Desarrollo, CPU, gratis |
| `laya_http` | laya-serve HTTP | Producción, GPU opcional |
| `jev_http` | TypeSafe Jev API | Comparación (requiere API key) |

### Configuración de Backends

```yaml
# config/default.yaml
laya:
  default_model: "multilingual"  # Para español
  device: "cpu"  # o "cuda"
  cache_dir: ".cache/models"

laya_http:
  endpoint: "http://localhost:8000/v1/systemone"
  timeout: 30

jev_http:
  endpoint: "https://api.typesafe.ai/v1/systemone"
  enabled: false  # Requiere TYPESAFE_API_KEY
```

## Métricas Implementadas

### Métricas de Calidad
- **Accuracy**: Tasa de aciertos
- **Macro F1**: F1 promedio entre clases
- **MAE**: Error absoluto medio (para scores ordinales)
- **Baselines**: Mayoría y aleatorio

### Métricas de Calibración
- **Brier Score**: Error cuadrático medio de probabilidades
- **ECE**: Expected Calibration Error (10 bins)

### Métricas de Consistencia
- **Paraphrase consistency**: Consistencia bajo paráfrasis
- **Order consistency**: Consistencia bajo permutación de opciones

### Métricas de Rendimiento
- **Latencia**: P50, P95, P99 (separando cold start)
- **Throughput**: Decisiones por segundo
- **Costo**: USD por 1000 decisiones

### Métricas de Negocio
- **Automation coverage curve**: Cobertura vs. precisión por umbral
- **Low confidence rate**: Tasa de predicciones con baja confianza
- **Schema validity**: Cumplimiento de schema

Ver [`docs/03-metricas.md`](docs/03-metricas.md) para detalles.

## Docker

```bash
# Iniciar laya-serve (CPU)
docker compose up laya-serve

# Con GPU (requiere nvidia-docker)
docker compose --profile gpu up laya-serve-gpu

# Ejecutar benchmark en container
docker compose --profile benchmark up benchmark-runner
```

## Tests

```bash
# Todos los tests
make test

# Solo tests unitarios
pytest tests/unit/

# Con coverage
pytest --cov=src --cov-report=html
```

## Documentación

Documentación técnica completa en español en [`docs/`](docs/):

1. **[¿Qué es Laya?](docs/01-que-es-laya.md)** - Arquitectura, conceptos, diagramas
2. **[Cómo Preguntar](docs/02-como-preguntar.md)** - Guía de prompting y diseño de preguntas
3. **[Métricas](docs/03-metricas.md)** - Explicación detallada de cada métrica
4. **[PoC 1: Benchmark](docs/04-poc1-benchmark.md)** - Documentación del benchmark offline
5. **[PoC 2: Triage](docs/05-poc2-triage.md)** - Documentación del triage de tickets
6. **[Comparar con Jev](docs/06-comparar-con-jev.md)** - Cómo hacer comparaciones justas
7. **[Buenas Prácticas](docs/07-buenas-practicas.md)** - Recomendaciones y patterns

## Contribuir

```bash
# Setup
make setup

# Antes de commit
make format  # Formatea código
make lint    # Verifica estilo
make test    # Ejecuta tests
```

## Recursos

- **Laya GitHub**: https://github.com/NandhaKishorM/laya
- **Laya HuggingFace**: https://huggingface.co/convaiinnovations/laya
- **Laya PyPI**: https://pypi.org/project/laya/
- **Documentación Laya**: https://nandhakishorm.github.io/laya/
- **Jev (TypeSafe AI)**: https://typesafe.ai/ (comparación, cerrado)

## Licencia

MIT License - ver [LICENSE](LICENSE) para detalles.

Laya es Apache-2.0 (Convai Innovations).
