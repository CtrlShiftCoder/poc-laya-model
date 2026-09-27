"""
Ticket triage runner for PoC 2.
"""
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
from tqdm import tqdm

from src.backends import DecisionBackend
from src.backends.base import DecisionRequest
from src.metrics import compute_choice_metrics, compute_score_metrics


class TicketTriageRunner:
    """Runner for ticket triage simulation."""
    
    def __init__(
        self,
        backend: DecisionBackend,
        confidence_threshold: float = 0.75,
        output_dir: str = "reports/poc2",
    ):
        self.backend = backend
        self.confidence_threshold = confidence_threshold
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def triage_ticket(self, ticket: Dict) -> Dict:
        """
        Triage a single ticket.
        
        Returns:
            Dict with predictions and metadata
        """
        state = {
            "subject": ticket["subject"],
            "body": ticket["body"],
        }
        
        questions = {
            "category": {
                "type": "choice",
                "instructions": "¿A qué categoría pertenece este ticket?",
                "criteria": {
                    "facturación": "Pagos, facturas, cobros, reembolsos, métodos de pago",
                    "técnico": "Errores, bugs, problemas técnicos, integraciones, API",
                    "ventas": "Consultas comerciales, planes, precios, demos, contratos",
                    "cancelación": "Solicitudes de cancelación, quejas graves, insatisfacción",
                    "otro": "Cualquier otro tema: consultas generales, felicitaciones, cambios de cuenta",
                }
            },
            "urgency": {
                "type": "score",
                "instructions": "¿Qué tan urgente es este ticket?",
                "criteria": [
                    "No urgente - puede esperar varios días",
                    "Urgencia media - responder en 24-48 horas",
                    "Crítico - requiere atención inmediata",
                ]
            },
            "needs_human": {
                "type": "noul",
                "instructions": (
                    "¿Este ticket requiere intervención humana especializada? "
                    "Considera: amenaza de cancelación, problema crítico, solicitud compleja, "
                    "cliente muy insatisfecho, o situación que requiere juicio humano."
                )
            },
        }
        
        try:
            request = DecisionRequest(state=state, questions=questions)
            response = self.backend.predict(request)
            
            answers = response.answers
            
            # Extract predictions
            category_pred = answers["category"]["choice"]
            category_conf = answers["category"]["confidence"]
            
            urgency_pred = int(answers["urgency"]["score"])
            urgency_conf = answers["urgency"].get("confidence", 0.8)
            
            needs_human_prob = answers["needs_human"]["noul"]
            needs_human_pred = needs_human_prob >= 0.5
            
            # Routing decision
            automate = (
                category_conf >= self.confidence_threshold
                and not needs_human_pred
                and urgency_pred < 2
            )
            
            return {
                "ticket_id": ticket["id"],
                "category_pred": category_pred,
                "category_true": ticket["category"],
                "category_conf": category_conf,
                "category_correct": category_pred == ticket["category"],
                "urgency_pred": urgency_pred,
                "urgency_true": ticket["urgency"],
                "urgency_correct": urgency_pred == ticket["urgency"],
                "needs_human_prob": needs_human_prob,
                "needs_human_pred": needs_human_pred,
                "needs_human_true": ticket["needs_human"],
                "needs_human_correct": needs_human_pred == ticket["needs_human"],
                "automate": automate,
                "should_automate": not ticket["needs_human"] and ticket["urgency"] < 2,
                "latency_ms": response.latency_ms,
                "cost_usd": response.cost_usd,
            }
        
        except Exception as e:
            print(f"Error triaging ticket {ticket['id']}: {e}")
            return {
                "ticket_id": ticket["id"],
                "category_pred": "otro",
                "category_true": ticket["category"],
                "category_conf": 0,
                "category_correct": False,
                "urgency_pred": 1,
                "urgency_true": ticket["urgency"],
                "urgency_correct": False,
                "needs_human_prob": 0.5,
                "needs_human_pred": True,
                "needs_human_true": ticket["needs_human"],
                "needs_human_correct": False,
                "automate": False,
                "should_automate": False,
                "latency_ms": 0,
                "cost_usd": 0,
            }
    
    def run(self, tickets: List[Dict]) -> Dict:
        """Run triage on all tickets."""
        print(f"\n🎫 Triaging {len(tickets)} tickets...")
        print(f"📊 Umbral de confianza: {self.confidence_threshold}")
        
        results = []
        for ticket in tqdm(tickets, desc="Triage"):
            result = self.triage_ticket(ticket)
            results.append(result)
        
        # Create DataFrame
        df = pd.DataFrame(results)
        
        # Save detailed results
        results_path = self.output_dir / "triage_results.csv"
        df.to_csv(results_path, index=False)
        print(f"\n✓ Resultados guardados en {results_path}")
        
        # Compute metrics
        metrics_summary = self._compute_metrics(df)
        
        return {
            "results": results,
            "dataframe": df,
            "metrics": metrics_summary,
        }
    
    def _compute_metrics(self, df: pd.DataFrame) -> Dict:
        """Compute comprehensive metrics."""
        # Category classification metrics
        category_metrics = compute_choice_metrics(
            predictions=df["category_pred"].tolist(),
            labels=df["category_true"].tolist(),
            confidences=df["category_conf"].tolist(),
            latencies_ms=df["latency_ms"].tolist(),
            costs_usd=df["cost_usd"].tolist(),
        )
        
        # Urgency metrics
        urgency_metrics = compute_score_metrics(
            predictions=df["urgency_pred"].tolist(),
            labels=df["urgency_true"].tolist(),
            latencies_ms=df["latency_ms"].tolist(),
        )
        
        # Needs human metrics
        needs_human_acc = (df["needs_human_correct"]).mean()
        
        # Automation metrics
        total_tickets = len(df)
        automated = df["automate"].sum()
        should_automate = df["should_automate"].sum()
        
        # Safety metrics
        incorrectly_automated = df[df["automate"] & ~df["should_automate"]].shape[0]
        correctly_automated = df[df["automate"] & df["should_automate"]].shape[0]
        
        automation_precision = (
            correctly_automated / automated if automated > 0 else 0
        )
        automation_coverage = automated / total_tickets
        ideal_coverage = should_automate / total_tickets
        
        return {
            "category": category_metrics,
            "urgency": urgency_metrics,
            "needs_human_accuracy": needs_human_acc,
            "automation": {
                "total_tickets": total_tickets,
                "automated": automated,
                "should_automate": should_automate,
                "automation_rate": automation_coverage,
                "automation_precision": automation_precision,
                "ideal_coverage": ideal_coverage,
                "incorrectly_automated": incorrectly_automated,
                "coverage_gap": ideal_coverage - automation_coverage,
            }
        }
    
    def generate_report(self, results: Dict, tickets: List[Dict]):
        """Generate markdown report."""
        df = results["dataframe"]
        metrics = results["metrics"]
        
        report_lines = [
            "# PoC 2: Triage de Tickets en Shadow Mode - Resultados",
            "",
            f"**Backend:** {self.backend.get_name()}",
            f"**Fecha:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Umbral de confianza:** {self.confidence_threshold}",
            f"**Total de tickets:** {len(tickets)}",
            "",
            "## Resumen Ejecutivo",
            "",
            f"- **Tickets automatizados:** {metrics['automation']['automated']} "
            f"({metrics['automation']['automation_rate']:.1%})",
            f"- **Precisión de automatización:** {metrics['automation']['automation_precision']:.1%}",
            f"- **Cobertura ideal:** {metrics['automation']['ideal_coverage']:.1%}",
            f"- **Gap de cobertura:** {metrics['automation']['coverage_gap']:.1%}",
            f"- **Tickets incorrectamente automatizados:** {metrics['automation']['incorrectly_automated']}",
            "",
            "## Métricas de Clasificación de Categoría",
            "",
            f"- **Accuracy:** {metrics['category'].accuracy}",
            f"- **Macro F1:** {metrics['category'].macro_f1}",
            f"- **Brier Score:** {metrics['category'].brier_score.value:.4f}",
            "",
            "## Métricas de Urgencia",
            "",
            f"- **MAE (Mean Absolute Error):** {metrics['urgency']['ordinal_mae']:.3f}",
            f"- **Exact Match Accuracy:** {metrics['urgency']['exact_match_accuracy']:.1%}",
            "",
            "## Detección de Necesidad Humana",
            "",
            f"- **Accuracy:** {metrics['needs_human_accuracy']:.1%}",
            "",
            "## Métricas de Rendimiento",
            "",
            f"- **Latencia P50:** {metrics['category'].latency_p50:.1f} ms",
            f"- **Latencia P95:** {metrics['category'].latency_p95:.1f} ms",
            f"- **Throughput:** {metrics['category'].throughput_per_sec:.2f} tickets/s",
            "",
            "## Análisis de Automatización por Umbral",
            "",
        ]
        
        if metrics["category"].automation_coverage:
            report_lines.append("| Umbral | Cobertura | Precisión |")
            report_lines.append("|--------|-----------|-----------|")
            for threshold, (coverage, precision) in sorted(
                metrics["category"].automation_coverage.items()
            ):
                report_lines.append(
                    f"| {threshold:.2f} | {coverage:.1%} | {precision:.1%} |"
                )
            report_lines.append("")
        
        # Confusion matrix for categories
        report_lines.extend([
            "## Distribución de Categorías",
            "",
            "**Predicciones:**",
            ""
        ])
        
        for cat, count in df["category_pred"].value_counts().items():
            report_lines.append(f"- {cat}: {count}")
        
        report_lines.append("")
        
        # Save report
        report_path = self.output_dir / "report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))
        
        print(f"✓ Reporte guardado en {report_path}")
        
        # Save metrics as JSON
        metrics_path = self.output_dir / "metrics.json"
        # Convert metrics to serializable format
        metrics_json = {
            "automation": metrics["automation"],
            "needs_human_accuracy": float(metrics["needs_human_accuracy"]),
            "urgency": metrics["urgency"],
            "category": {
                "accuracy": float(metrics["category"].accuracy.value),
                "macro_f1": float(metrics["category"].macro_f1.value),
                "brier_score": float(metrics["category"].brier_score.value),
                "latency_p50": float(metrics["category"].latency_p50),
                "latency_p95": float(metrics["category"].latency_p95),
            }
        }
        
        with open(metrics_path, "w") as f:
            json.dump(metrics_json, f, indent=2)
        
        print(f"✓ Métricas guardadas en {metrics_path}")
