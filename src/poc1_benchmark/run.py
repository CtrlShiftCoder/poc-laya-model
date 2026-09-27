"""
Main entry point for PoC 1: Offline benchmark.
"""
from src.backends import create_backend
from src.poc1_benchmark.data_loaders import (
    create_sample_spanish_dataset,
    load_emotion_english,
    load_massive_spanish,
    load_xnli_spanish,
)
from src.poc1_benchmark.runner import BenchmarkRunner


def main():
    """Run PoC 1 benchmark."""
    print("=" * 80)
    print("PoC 1: Benchmark Offline de Laya")
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
        print("\nIntentando con dataset de muestra...")
        # Use sample data if Laya fails to load
        backend = None
    
    # Initialize runner
    runner = BenchmarkRunner(backend=backend, output_dir="reports/poc1")
    
    all_results = []
    
    # Run benchmarks
    try:
        # 1. English emotion dataset
        print("\n" + "=" * 80)
        print("Dataset 1: Emotion (English)")
        print("=" * 80)
        emotion_data = load_emotion_english(sample_size=50)
        if emotion_data and backend:
            emotion_results = runner.run_emotion_benchmark(emotion_data)
            all_results.append(emotion_results)
        else:
            print("Skipping emotion dataset (no data or backend)")
        
        # 2. Spanish XNLI
        print("\n" + "=" * 80)
        print("Dataset 2: XNLI (Spanish)")
        print("=" * 80)
        xnli_data = load_xnli_spanish(sample_size=50)
        if xnli_data and backend:
            xnli_results = runner.run_xnli_benchmark(xnli_data)
            all_results.append(xnli_results)
        else:
            print("Skipping XNLI dataset (no data or backend)")
        
        # 3. Spanish MASSIVE (optional, may fail)
        print("\n" + "=" * 80)
        print("Dataset 3: MASSIVE (Spanish) - opcional")
        print("=" * 80)
        massive_data = load_massive_spanish(sample_size=30)
        if massive_data and backend:
            massive_results = runner.run_massive_benchmark(massive_data)
            all_results.append(massive_results)
        else:
            print("Skipping MASSIVE dataset")
    
    except Exception as e:
        print(f"\n✗ Error durante benchmark: {e}")
        import traceback
        traceback.print_exc()
    
    # Generate report
    if all_results:
        print("\n" + "=" * 80)
        print("Generando reporte final...")
        print("=" * 80)
        runner.generate_report(all_results)
        
        print("\n" + "=" * 80)
        print("✓ PoC 1 completado exitosamente")
        print("=" * 80)
        print(f"\nResultados guardados en: {runner.output_dir}")
    else:
        print("\n⚠ No se generaron resultados")


if __name__ == "__main__":
    main()
