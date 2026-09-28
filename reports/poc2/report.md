# PoC 2: Triage de Tickets en Shadow Mode - Resultados

**Backend:** laya_local
**Fecha:** 2026-09-27 18:17:39
**Umbral de confianza:** 0.75
**Total de tickets:** 20

## Resumen Ejecutivo

- **Tickets automatizados:** 4 (20.0%)
- **Precisión de automatización:** 50.0%
- **Cobertura ideal:** 50.0%
- **Gap de cobertura:** 30.0%
- **Tickets incorrectamente automatizados:** 2

## Métricas de Clasificación de Categoría

- **Accuracy:** 0.3500 (95% CI: 0.1500-0.5500)
- **Macro F1:** 0.2900 (95% CI: 0.1033-0.4614)
- **Brier Score:** 0.3244

## Métricas de Urgencia

- **MAE (Mean Absolute Error):** 0.700
- **Exact Match Accuracy:** 30.0%

## Detección de Necesidad Humana

- **Accuracy:** 70.0%

## Métricas de Rendimiento

- **Latencia P50:** 213.1 ms
- **Latencia P95:** 231.5 ms
- **Throughput:** 4.77 tickets/s

## Análisis de Automatización por Umbral

| Umbral | Cobertura | Precisión |
|--------|-----------|-----------|
| 0.50 | 70.0% | 42.9% |
| 0.60 | 55.0% | 45.5% |
| 0.70 | 45.0% | 33.3% |
| 0.75 | 40.0% | 37.5% |
| 0.80 | 35.0% | 42.9% |
| 0.85 | 30.0% | 50.0% |
| 0.90 | 25.0% | 40.0% |
| 0.95 | 20.0% | 50.0% |

## Distribución de Categorías

**Predicciones:**

- técnico: 9
- facturación: 4
- cancelación: 4
- ventas: 2
- otro: 1
