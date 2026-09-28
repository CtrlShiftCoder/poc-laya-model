"""
Benchmark runner for PoC 1: Offline evaluation.
"""
import json
import time
from pathlib import Path
from typing import Dict, List

import pandas as pd
from tqdm import tqdm

from src.backends import DecisionBackend, create_backend
from src.backends.base import DecisionRequest
from src.metrics import compute_choice_metrics, create_metrics_summary


class BenchmarkRunner:
    """Runner for offline benchmarks."""
    
    def __init__(
        self,
        backend: DecisionBackend,
        output_dir: str = "reports/poc1",
    ):
        self.backend = backend
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def run_xnli_benchmark(self, examples: List[Dict]) -> Dict:
        """Run XNLI entailment benchmark."""
        print(f"\n🔍 Running XNLI benchmark ({len(examples)} examples)...")
        
        predictions = []
        labels = []
        confidences = []
        latencies = []
        costs = []
        
        for example in tqdm(examples, desc="XNLI"):
            state = {
                "premise": example["premise"],
                "hypothesis": example["hypothesis"],
            }
            
            questions = {
                "entailment": {
                    "type": "choice",
                    "instructions": "¿Cuál es la relación entre la premisa y la hipótesis?",
                    "criteria": {
                        "entailment": "La hipótesis se deriva lógicamente de la premisa",
                        "neutral": "La hipótesis es compatible pero no se deriva de la premisa",
                        "contradiction": "La hipótesis contradice la premisa",
                    }
                }
            }
            
            try:
                request = DecisionRequest(state=state, questions=questions)
                response = self.backend.predict(request)
                
                answer = response.answers["entailment"]
                predictions.append(answer["choice"])
                confidences.append(answer["confidence"])
                latencies.append(response.latency_ms)
                costs.append(response.cost_usd)
                labels.append(example["label"])
            
            except Exception as e:
                print(f"Error on example {example['id']}: {e}")
                predictions.append("neutral")
                confidences.append(0)
                latencies.append(0)
                costs.append(0)
                labels.append(example["label"])
        
        # Compute metrics
        metrics = compute_choice_metrics(
            predictions=predictions,
            labels=labels,
            confidences=confidences,
            latencies_ms=latencies,
            costs_usd=costs,
        )
        
        # Save results
        results_df = pd.DataFrame({
            "id": [ex["id"] for ex in examples],
            "premise": [ex["premise"] for ex in examples],
            "hypothesis": [ex["hypothesis"] for ex in examples],
            "true_label": labels,
            "predicted": predictions,
            "confidence": confidences,
            "latency_ms": latencies,
            "correct": [p == l for p, l in zip(predictions, labels)],
        })
        
        results_path = self.output_dir / "xnli_results.csv"
        results_df.to_csv(results_path, index=False)
        print(f"✓ Results saved to {results_path}")
        
        return {
            "dataset": "xnli_es",
            "n_examples": len(examples),
            "metrics": metrics,
            "predictions": predictions,
            "labels": labels,
        }
    
    def run_massive_benchmark(self, examples: List[Dict]) -> Dict:
        """Run MASSIVE intent classification benchmark."""
        print(f"\n🔍 Running MASSIVE benchmark ({len(examples)} examples)...")
        
        # Get unique intents for criteria
        unique_intents = sorted(set(ex["intent"] for ex in examples))
        
        # Create intent descriptions (simplified)
        intent_criteria = {intent: f"Intent: {intent}" for intent in unique_intents[:20]}
        
        if len(unique_intents) > 20:
            print(f"Warning: Too many intents ({len(unique_intents)}), using top 20")
        
        predictions = []
        labels = []
        confidences = []
        latencies = []
        
        for example in tqdm(examples, desc="MASSIVE"):
            state = {"text": example["text"]}
            
            questions = {
                "intent": {
                    "type": "choice",
                    "instructions": "¿Cuál es la intención del usuario?",
                    "criteria": intent_criteria,
                }
            }
            
            try:
                request = DecisionRequest(state=state, questions=questions)
                response = self.backend.predict(request)
                
                answer = response.answers["intent"]
                predictions.append(answer["choice"])
                confidences.append(answer["confidence"])
                latencies.append(response.latency_ms)
                labels.append(example["intent"])
            
            except Exception as e:
                print(f"Error on example {example['id']}: {e}")
                predictions.append(unique_intents[0])
                confidences.append(0)
                latencies.append(0)
                labels.append(example["intent"])
        
        # Compute metrics
        metrics = compute_choice_metrics(
            predictions=predictions,
            labels=labels,
            confidences=confidences,
            latencies_ms=latencies,
        )
        
        results_df = pd.DataFrame({
            "id": [ex["id"] for ex in examples],
            "text": [ex["text"] for ex in examples],
            "true_intent": labels,
            "predicted_intent": predictions,
            "confidence": confidences,
            "latency_ms": latencies,
            "correct": [p == l for p, l in zip(predictions, labels)],
        })
        
        results_path = self.output_dir / "massive_results.csv"
        results_df.to_csv(results_path, index=False)
        print(f"✓ Results saved to {results_path}")
        
        return {
            "dataset": "massive_es",
            "n_examples": len(examples),
            "metrics": metrics,
        }
    
    def run_emotion_benchmark(self, examples: List[Dict]) -> Dict:
        """Run emotion classification benchmark."""
        print(f"\n🔍 Running Emotion benchmark ({len(examples)} examples)...")
        
        predictions = []
        labels = []
        confidences = []
        latencies = []
        
        for example in tqdm(examples, desc="Emotion"):
            state = {"text": example["text"]}
            
            questions = {
                "emotion": {
                    "type": "choice",
                    "instructions": "What emotion does this text express?",
                    "criteria": {
                        "sadness": "expressing sadness, grief, or disappointment",
                        "joy": "expressing happiness, joy, or excitement",
                        "love": "expressing love, affection, or care",
                        "anger": "expressing anger, frustration, or annoyance",
                        "fear": "expressing fear, worry, or anxiety",
                        "surprise": "expressing surprise or amazement",
                    }
                }
            }
            
            try:
                request = DecisionRequest(state=state, questions=questions)
                response = self.backend.predict(request)
                
                answer = response.answers["emotion"]
                predictions.append(answer["choice"])
                confidences.append(answer["confidence"])
                latencies.append(response.latency_ms)
                labels.append(example["emotion"])
            
            except Exception as e:
                print(f"Error on example {example['id']}: {e}")
                predictions.append("joy")
                confidences.append(0)
                latencies.append(0)
                labels.append(example["emotion"])
        
        # Compute metrics
        metrics = compute_choice_metrics(
            predictions=predictions,
            labels=labels,
            confidences=confidences,
            latencies_ms=latencies,
        )
        
        results_df = pd.DataFrame({
            "id": [ex["id"] for ex in examples],
            "text": [ex["text"] for ex in examples],
            "true_emotion": labels,
            "predicted_emotion": predictions,
            "confidence": confidences,
            "latency_ms": latencies,
            "correct": [p == l for p, l in zip(predictions, labels)],
        })
        
        results_path = self.output_dir / "emotion_results.csv"
        results_df.to_csv(results_path, index=False)
        print(f"✓ Results saved to {results_path}")
        
        return {
            "dataset": "emotion",
            "n_examples": len(examples),
            "metrics": metrics,
        }
    
    def generate_report(self, all_results: List[Dict]):
        """Generate markdown report."""
        report_lines = [
            "# PoC 1: Benchmark Offline - Resultados",
            "",
            f"**Backend:** {self.backend.get_name()}",
            f"**Fecha:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]
        
        for result in all_results:
            metrics = result["metrics"]
            dataset = result["dataset"]
            n = result["n_examples"]
            
            report_lines.extend([
                f"## {dataset.upper()}",
                "",
                f"**Muestras:** {n}",
                "",
                "### Métricas de Calidad",
                "",
                f"- **Accuracy:** {metrics.accuracy}",
                f"- **Macro F1:** {metrics.macro_f1}",
                "",
                "### Métricas de Calibración",
                "",
                f"- **Brier Score:** {metrics.brier_score.value:.4f}",
                f"- **ECE:** {metrics.ece.value:.4f}",
                "",
                "### Métricas de Rendimiento",
                "",
                f"- **Latencia P50:** {metrics.latency_p50:.1f} ms",
                f"- **Latencia P95:** {metrics.latency_p95:.1f} ms",
                f"- **Latencia P99:** {metrics.latency_p99:.1f} ms",
                f"- **Throughput:** {metrics.throughput_per_sec:.2f} req/s",
                "",
                "### Métricas de Negocio",
                "",
                f"- **Tasa de baja confianza:** {metrics.low_confidence_rate:.1%}",
                "",
            ])
            
            if metrics.automation_coverage:
                report_lines.append("**Curva de automatización:**")
                report_lines.append("")
                for threshold, (coverage, precision) in sorted(metrics.automation_coverage.items()):
                    report_lines.append(
                        f"- Umbral {threshold:.2f}: cobertura {coverage:.1%}, "
                        f"precisión {precision:.1%}"
                    )
                report_lines.append("")
        
        # Save report
        report_path = self.output_dir / "report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))
        
        print(f"\n✓ Report saved to {report_path}")
