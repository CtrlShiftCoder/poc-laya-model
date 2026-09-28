# Resultados de Evaluación de Laya

**Fecha de ejecución:** 2026-09-27 / 2026-09-28  
**Entorno:** Cloud Agent VM (CPU)  
**Python:** 3.11.16  
**Laya:** versión 0.3.20  
**Checkpoint:** multilingual (mmBERT-base, 322M parámetros)

---

## Resumen Ejecutivo

Se ejecutaron dos pruebas de concepto (PoCs) end-to-end con modelos reales de Laya para evaluar su desempeño en tareas de clasificación en español.

**Hallazgos principales:**
- PoC 1 (XNLI): Desempeño sólido en benchmark estándar (82% accuracy)
- PoC 2 (Tickets): Desempeño débil en tarea de dominio específico (35% accuracy)
- Conclusión: Fine-tuning es necesario para casos de uso de producción

---

## PoC 1: Benchmark XNLI Español

### Configuración
- **Dataset:** XNLI Spanish (facebook/xnli, split de validación)
- **Tamaño de muestra:** 50 ejemplos
- **Tarea:** Clasificación de entailment en 3 clases (entailment, neutral, contradiction)
- **Modo:** Zero-shot (sin fine-tuning)

### Métricas de Calidad

| Métrica | Valor |
|---------|-------|
| **Accuracy** | 82.0% (IC 95%: 72.0%-92.0%) |
| **Macro F1** | 0.8202 (IC 95%: 0.698-0.922) |
| **Baseline aleatorio** | 33.3% (3 clases) |
| **Mejora sobre baseline** | +146% |

### Métricas de Calibración

| Métrica | Valor | Interpretación |
|---------|-------|----------------|
| **Brier Score** | 0.1136 | Buena calibración |
| **ECE** | 0.0763 | Calibración aceptable (<0.10) |

### Métricas de Rendimiento

| Métrica | Valor |
|---------|-------|
| **Latencia P50** | 65.9 ms |
| **Latencia P95** | 76.1 ms |
| **Latencia P99** | 79.8 ms |
| **Throughput** | 15.16 req/s |

### Métricas de Negocio

**Tasa de baja confianza (<0.7):** 28.0%

**Curva de cobertura de automatización:**

| Umbral | Cobertura | Precisión |
|--------|-----------|-----------|
| 0.75 | 68% | 94.1% |
| 0.80 | 66% | 93.9% |
| 0.90 | 56% | 96.4% |

### Análisis

- Accuracy de 82% en zero-shot indica que el checkpoint multilingual maneja español efectivamente
- ECE de 0.076 muestra calibración razonable (las probabilidades reflejan accuracy real)
- Latencia de ~66ms P50 es adecuada para aplicaciones interactivas en CPU
- Con umbral de confianza 0.75, se puede automatizar 68% de casos con 94% de precisión

---

## PoC 2: Triage de Tickets de Soporte

### Configuración
- **Dataset:** 20 tickets sintéticos en español
- **Categorías:** facturación, técnico, ventas, cancelación, otro
- **Tareas:** Clasificación de categoría + scoring de urgencia + detección de necesidad humana
- **Umbral de confianza:** 0.75
- **Modo:** Zero-shot (sin fine-tuning)

### Métricas de Clasificación de Categoría

| Métrica | Valor |
|---------|-------|
| **Accuracy** | 35.0% (IC 95%: 15.0%-55.0%) |
| **Macro F1** | 0.29 (IC 95%: 0.10-0.46) |
| **Brier Score** | 0.3244 |

### Métricas de Urgencia (Score Ordinal)

| Métrica | Valor |
|---------|-------|
| **MAE** | 0.70 niveles |
| **Exact Match** | 30.0% |

### Métricas de Detección de Necesidad Humana

| Métrica | Valor |
|---------|-------|
| **Accuracy** | 70.0% |

### Métricas de Rendimiento

| Métrica | Valor |
|---------|-------|
| **Latencia P50** | 213.1 ms |
| **Latencia P95** | 231.5 ms |
| **Throughput** | 4.77 tickets/s |

### Métricas de Automatización

| Métrica | Valor |
|---------|-------|
| **Total tickets** | 20 |
| **Automatizados** | 4 (20.0%) |
| **Cobertura ideal** | 10 (50.0%) |
| **Precisión de automatización** | 50.0% |
| **Errores críticos** | 2 tickets |
| **Gap de cobertura** | 30.0% |

### Distribución de Predicciones

- técnico: 9 tickets
- facturación: 4 tickets
- cancelación: 4 tickets
- ventas: 2 tickets
- otro: 1 ticket

### Análisis

**Problemas identificados:**
1. **Accuracy muy baja (35%):** El modelo zero-shot no comprende el vocabulario de dominio
2. **Mala calibración (Brier 0.32):** Las probabilidades no reflejan accuracy real
3. **Errores críticos:** 2 de 4 tickets automatizados fueron incorrectos (50% error rate)
4. **Automatización conservadora:** Solo 20% automatizado vs 50% ideal

**Causa raíz:** Zero-shot es insuficiente para tareas de dominio específico

**Recomendación:** 
- Recolectar 500-1000 tickets etiquetados reales
- Fine-tunear checkpoint multilingual
- Mejora esperada: +40-50% accuracy (de 35% a 75-85%)

---

## Comparación Entre PoCs

| Métrica | PoC 1 (XNLI) | PoC 2 (Tickets) | Delta |
|---------|--------------|-----------------|-------|
| Accuracy | 82.0% | 35.0% | -47.0% |
| Macro F1 | 0.82 | 0.29 | -0.53 |
| Brier Score | 0.11 | 0.32 | +0.21 |
| ECE | 0.076 | N/A | - |
| Latencia P50 | 65.9 ms | 213.1 ms | +147 ms |
| Throughput | 15.16 /s | 4.77 /s | -10.4 /s |

**Observaciones:**
- Diferencia de 47% en accuracy refleja gap entre benchmark general y tarea de dominio
- Latencia 3.2x mayor en PoC 2 debido a preguntas múltiples (3 preguntas vs 1)
- Calibración significativamente peor en tarea de dominio

---

## Especificaciones Técnicas

### Entorno de Ejecución
- Sistema operativo: Linux x86_64
- Procesador: CPU (sin GPU)
- RAM: 16GB
- Python: 3.11.16
- Laya: 0.3.20
- Dependencias principales: PyTorch 2.14.0, transformers 5.17.0

### Datasets Cargados
- **XNLI Spanish:** facebook/xnli (50 muestras de validation split)
- **Tickets sintéticos:** 20 tickets en español (incluidos en repositorio)
- **MASSIVE Spanish:** No disponible (cambios en API de HuggingFace)
- **Emotion English:** No disponible (cambios en API de HuggingFace)

### Archivos Generados
```
reports/
├── poc1/
│   ├── xnli_results.csv    # 50 filas con predicciones reales
│   └── report.md            # Métricas medidas
└── poc2/
    ├── triage_results.csv   # 20 filas con predicciones reales
    ├── metrics.json         # Métricas en formato JSON
    └── report.md            # Métricas medidas
```

Todos los valores son **mediciones reales** de ejecuciones reales, no valores típicos o fabricados.

---

## Limitaciones del Estudio

1. **Tamaños de muestra pequeños:** PoC 1 solo 50 ejemplos (se requieren 500+ para validación de producción)
2. **Solo zero-shot:** No se aplicó fine-tuning
3. **Ejecución en CPU:** GPU sería 3-5x más rápida
4. **Tickets sintéticos:** No reflejan distribución real de soporte
5. **Datasets limitados:** Algunos datasets públicos no se pudieron cargar

---

## Conclusiones

### Fortalezas de Laya
1. Desempeño sólido en benchmarks estándar (82% en XNLI español)
2. Latencia razonable para CPU (66-213ms P50)
3. Calibración aceptable en tareas de benchmark (ECE 0.076)
4. Código funciona correctamente contra API real de Laya

### Debilidades Identificadas
1. Desempeño pobre en tareas de dominio específico sin fine-tuning (35%)
2. Calibración variable entre tareas (Brier 0.11 vs 0.32)
3. Requiere fine-tuning para uso productivo

### Recomendaciones

**Corto plazo:**
1. Recolectar datos etiquetados de dominio específico (mínimo 500 ejemplos)
2. Fine-tunear checkpoint multilingual en datos propios
3. Re-evaluar con muestras más grandes (500+ por dataset)

**Mediano plazo:**
4. Implementar monitoreo de calibración en producción
5. Actualizar data loaders para nueva API de HuggingFace
6. Comparar head-to-head con Jev si se dispone de API key

**Largo plazo:**
7. Establecer pipeline de fine-tuning continuo
8. Integrar human-in-the-loop para casos de baja confianza
9. Optimizar latencia con GPU o modelo distilled

---

## Validación del Código

**Tests unitarios:** 20/20 pasando  
**Linter:** ruff (sin errores)  
**Estructura:** src/ layout, production-ready  
**Documentación:** 8 documentos técnicos en español (95KB)

---

**Generado:** 2026-09-28  
**Repositorio:** https://github.com/CtrlShiftCoder/poc-laya-model
