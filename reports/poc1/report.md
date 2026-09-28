# PoC 1: Benchmark Offline - Resultados

**Backend:** laya_local
**Fecha:** 2026-09-28 13:50:05

## EMOTION

**Muestras:** 50

### Métricas de Calidad

- **Accuracy:** 0.5800 (95% CI: 0.4400-0.7005)
- **Macro F1:** 0.4035 (95% CI: 0.2611-0.5698)

### Métricas de Calibración

- **Brier Score:** 0.2982
- **ECE:** 0.3135

### Métricas de Rendimiento

- **Latencia P50:** 61.4 ms
- **Latencia P95:** 76.9 ms
- **Latencia P99:** 105.5 ms
- **Throughput:** 15.63 req/s

### Métricas de Negocio

- **Tasa de baja confianza:** 22.0%

**Curva de automatización:**

- Umbral 0.50: cobertura 86.0%, precisión 60.5%
- Umbral 0.60: cobertura 86.0%, precisión 60.5%
- Umbral 0.70: cobertura 78.0%, precisión 59.0%
- Umbral 0.75: cobertura 66.0%, precisión 60.6%
- Umbral 0.80: cobertura 62.0%, precisión 58.1%
- Umbral 0.85: cobertura 56.0%, precisión 64.3%
- Umbral 0.90: cobertura 48.0%, precisión 70.8%
- Umbral 0.95: cobertura 38.0%, precisión 73.7%

## XNLI_ES

**Muestras:** 50

### Métricas de Calidad

- **Accuracy:** 0.8200 (95% CI: 0.7000-0.9200)
- **Macro F1:** 0.8202 (95% CI: 0.7001-0.9168)

### Métricas de Calibración

- **Brier Score:** 0.1136
- **ECE:** 0.0725

### Métricas de Rendimiento

- **Latencia P50:** 66.9 ms
- **Latencia P95:** 80.7 ms
- **Latencia P99:** 85.0 ms
- **Throughput:** 14.79 req/s

### Métricas de Negocio

- **Tasa de baja confianza:** 28.0%

**Curva de automatización:**

- Umbral 0.50: cobertura 78.0%, precisión 92.3%
- Umbral 0.60: cobertura 74.0%, precisión 94.6%
- Umbral 0.70: cobertura 72.0%, precisión 94.4%
- Umbral 0.75: cobertura 68.0%, precisión 94.1%
- Umbral 0.80: cobertura 66.0%, precisión 93.9%
- Umbral 0.85: cobertura 64.0%, precisión 93.8%
- Umbral 0.90: cobertura 56.0%, precisión 96.4%
- Umbral 0.95: cobertura 42.0%, precisión 95.2%
