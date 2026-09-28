"""
Main entry point for PoC 2: Ticket triage.
"""
from src.backends import create_backend
from src.poc2_triage.runner import TicketTriageRunner
from src.poc2_triage.synthetic_data import SYNTHETIC_TICKETS


def main():
    """Run PoC 2: Ticket triage."""
    print("=" * 80)
    print("PoC 2: Triage de Tickets de Soporte en Shadow Mode")
    print("=" * 80)
    
    # Create backend
    print("\n📦 Inicializando backend Laya...")
    try:
        backend = create_backend(
            "laya_local",
            config={"model": "multilingual", "device": "cpu"}
        )
        print(f"✓ Backend '{backend.get_name()}' inicializado")
    except Exception as e:
        print(f"✗ Error al inicializar backend: {e}")
        return
    
    # Initialize runner
    print("\n🎫 Preparando triage...")
    runner = TicketTriageRunner(
        backend=backend,
        confidence_threshold=0.75,
        output_dir="reports/poc2"
    )
    
    # Load tickets
    tickets = SYNTHETIC_TICKETS
    print(f"✓ Cargados {len(tickets)} tickets sintéticos")
    
    # Run triage
    try:
        results = runner.run(tickets)
        
        # Generate report
        print("\n" + "=" * 80)
        print("Generando reporte...")
        print("=" * 80)
        runner.generate_report(results, tickets)
        
        # Summary
        automation = results["metrics"]["automation"]
        print("\n" + "=" * 80)
        print("✓ PoC 2 completado exitosamente")
        print("=" * 80)
        print(f"\n📊 Resumen:")
        print(f"  - Tickets procesados: {automation['total_tickets']}")
        print(f"  - Tickets automatizados: {automation['automated']} "
              f"({automation['automation_rate']:.1%})")
        print(f"  - Precisión de automatización: {automation['automation_precision']:.1%}")
        print(f"  - Errores de automatización: {automation['incorrectly_automated']}")
        print(f"\n📁 Resultados guardados en: {runner.output_dir}")
    
    except Exception as e:
        print(f"\n✗ Error durante triage: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
