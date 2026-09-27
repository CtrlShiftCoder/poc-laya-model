"""
Fine-tuning guide and utilities for Laya on custom ticket data.

This module provides guidance and utilities for fine-tuning Laya
on domain-specific ticket data to improve accuracy.
"""
from pathlib import Path
from typing import List, Dict
import json


def prepare_training_data(
    tickets: List[Dict],
    output_path: str = "data/poc2_tickets/training_data.jsonl"
) -> None:
    """
    Prepare ticket data for Laya fine-tuning.
    
    Laya fine-tuning expects JSONL format with:
    - state: The input context
    - questions: The question definitions
    - answers: The ground truth answers
    
    Args:
        tickets: List of labeled tickets
        output_path: Where to save training data
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    training_examples = []
    
    for ticket in tickets:
        # Convert ticket to Laya training format
        example = {
            "state": {
                "subject": ticket["subject"],
                "body": ticket["body"],
            },
            "questions": {
                "category": {
                    "type": "choice",
                    "instructions": "¿A qué categoría pertenece este ticket?",
                    "criteria": {
                        "facturación": "Pagos, facturas, cobros, reembolsos",
                        "técnico": "Errores, bugs, problemas técnicos",
                        "ventas": "Consultas comerciales, planes, precios",
                        "cancelación": "Solicitudes de cancelación, quejas",
                        "otro": "Cualquier otro tema",
                    }
                },
                "urgency": {
                    "type": "score",
                    "instructions": "¿Qué tan urgente es este ticket?",
                    "criteria": [
                        "No urgente",
                        "Urgencia media",
                        "Crítico",
                    ]
                },
            },
            "answers": {
                "category": {
                    "choice": ticket["category"],
                    "confidence": 1.0,
                },
                "urgency": {
                    "score": ticket["urgency"],
                }
            }
        }
        
        training_examples.append(example)
    
    # Save as JSONL
    with open(output_path, "w", encoding="utf-8") as f:
        for example in training_examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")
    
    print(f"✓ Training data saved to {output_path}")
    print(f"  Total examples: {len(training_examples)}")


def get_finetuning_instructions() -> str:
    """
    Get instructions for fine-tuning Laya.
    
    Returns:
        Markdown-formatted instructions
    """
    return """
# Fine-tuning Laya para Triage de Tickets

## Visión General

Laya puede ser fine-tuned en datos de dominio específico para mejorar
significativamente la precisión. El fine-tuning es especialmente útil para:

- Vocabulario de dominio específico
- Categorías o intents personalizados
- Calibración de confianza mejorada
- Mejor rendimiento en casos edge

## Preparación de Datos

1. **Formato de datos**: JSONL con state, questions y answers
2. **Tamaño mínimo**: ~1000 ejemplos etiquetados
3. **Balance**: Distribuir ejemplos uniformemente entre categorías
4. **Calidad**: Asegurar etiquetas correctas y consistentes

## Proceso de Fine-tuning

### Opción 1: Usando la API de Laya (recomendado)

```python
import laya

# Cargar modelo base
agent = laya.load("convaiinnovations/laya", subfolder="multilingual")

# Fine-tune en datos locales
agent.finetune(
    training_data="data/poc2_tickets/training_data.jsonl",
    validation_data="data/poc2_tickets/validation_data.jsonl",
    output_dir="models/laya-tickets-finetuned",
    epochs=3,
    learning_rate=2e-5,
    batch_size=16,
)
```

### Opción 2: Usando scripts de entrenamiento

```bash
# Instalar dependencias de entrenamiento
pip install laya[training]

# Ejecutar entrenamiento
laya-train \\
    --model convaiinnovations/laya \\
    --subfolder multilingual \\
    --train-data data/poc2_tickets/training_data.jsonl \\
    --val-data data/poc2_tickets/validation_data.jsonl \\
    --output-dir models/laya-tickets-finetuned \\
    --epochs 3 \\
    --learning-rate 2e-5 \\
    --batch-size 16
```

## Evaluación Post-Fine-tuning

Después del fine-tuning, evaluar el modelo usando:

```python
# Cargar modelo fine-tuned
finetuned_agent = laya.load("models/laya-tickets-finetuned")

# Evaluar en test set
from src.poc2_triage.runner import TicketTriageRunner

runner = TicketTriageRunner(
    backend=create_backend("laya_local", config={"agent": finetuned_agent})
)

results = runner.run(test_tickets)
```

## Métricas Esperadas

Mejoras típicas después de fine-tuning:

- **Accuracy**: +10-20% en categorización
- **Calibración**: Brier score mejora 0.05-0.10
- **Confianza**: Mayor confianza en predicciones correctas
- **Latencia**: Sin cambios (misma arquitectura)

## Mejores Prácticas

1. **Datos balanceados**: Igual número de ejemplos por categoría
2. **Validación separada**: 80% train, 10% val, 10% test
3. **Monitoreo**: Evaluar en val set cada época
4. **Early stopping**: Detener si val loss no mejora
5. **Augmentación**: Parafrasear ejemplos para más variedad

## Recursos

- [Documentación oficial de fine-tuning](https://nandhakishorm.github.io/laya/finetuning/)
- [Guía de preparación de datos](https://nandhakishorm.github.io/laya/data-prep/)
- [Ejemplos de fine-tuning](https://github.com/NandhaKishorM/laya/tree/main/examples/finetuning)
"""


if __name__ == "__main__":
    # Example: prepare training data from synthetic tickets
    from src.poc2_triage.synthetic_data import SYNTHETIC_TICKETS
    
    prepare_training_data(
        SYNTHETIC_TICKETS,
        output_path="data/poc2_tickets/training_data.jsonl"
    )
    
    # Print instructions
    print("\n" + "=" * 80)
    print(get_finetuning_instructions())
