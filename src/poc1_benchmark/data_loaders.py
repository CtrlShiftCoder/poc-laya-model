"""
Data loaders for benchmark datasets.
"""
import json
from pathlib import Path
from typing import Dict, List, Optional

from datasets import load_dataset


def load_xnli_spanish(sample_size: int = 100) -> List[Dict]:
    """
    Load Spanish XNLI dataset for entailment classification.
    
    Returns list of examples with:
    - premise: str
    - hypothesis: str
    - label: str (entailment, neutral, contradiction)
    """
    dataset = load_dataset("xnli", "es", split="validation")
    dataset = dataset.shuffle(seed=42).select(range(min(sample_size, len(dataset))))
    
    label_map = {0: "entailment", 1: "neutral", 2: "contradiction"}
    
    examples = []
    for item in dataset:
        examples.append({
            "premise": item["premise"],
            "hypothesis": item["hypothesis"],
            "label": label_map[item["label"]],
            "id": len(examples),
        })
    
    return examples


def load_massive_spanish(sample_size: int = 100) -> List[Dict]:
    """
    Load Spanish MASSIVE dataset for intent classification.
    
    Returns list of examples with:
    - text: str (user utterance)
    - intent: str
    """
    try:
        dataset = load_dataset("AmazonScience/massive", "es-ES", split="test")
        dataset = dataset.shuffle(seed=42).select(range(min(sample_size, len(dataset))))
        
        examples = []
        for item in dataset:
            examples.append({
                "text": item["utt"],
                "intent": item["intent"],
                "id": len(examples),
            })
        
        return examples
    except Exception as e:
        print(f"Warning: Could not load MASSIVE dataset: {e}")
        return []


def load_emotion_english(sample_size: int = 100) -> List[Dict]:
    """
    Load English emotion classification dataset.
    
    Returns list of examples with:
    - text: str
    - emotion: str (sadness, joy, love, anger, fear, surprise)
    """
    try:
        dataset = load_dataset("emotion", split="test")
        dataset = dataset.shuffle(seed=42).select(range(min(sample_size, len(dataset))))
        
        label_map = {0: "sadness", 1: "joy", 2: "love", 3: "anger", 4: "fear", 5: "surprise"}
        
        examples = []
        for item in dataset:
            examples.append({
                "text": item["text"],
                "emotion": label_map[item["label"]],
                "id": len(examples),
            })
        
        return examples
    except Exception as e:
        print(f"Warning: Could not load emotion dataset: {e}")
        return []


def load_custom_spanish_dataset(path: str) -> List[Dict]:
    """
    Load custom Spanish dataset from JSONL file.
    
    Expected format:
    {"text": "...", "label": "...", "metadata": {...}}
    """
    examples = []
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f):
            if line.strip():
                item = json.loads(line)
                item["id"] = line_num
                examples.append(item)
    
    return examples


def create_sample_spanish_dataset() -> List[Dict]:
    """Create a small sample Spanish dataset for testing."""
    return [
        {
            "text": "El producto llegó en perfectas condiciones y muy rápido",
            "category": "positivo",
            "sentiment_score": 2,
            "id": 0,
        },
        {
            "text": "Pésimo servicio, nunca más compraré aquí",
            "category": "negativo",
            "sentiment_score": 0,
            "id": 1,
        },
        {
            "text": "El precio es razonable pero la calidad es regular",
            "category": "neutral",
            "sentiment_score": 1,
            "id": 2,
        },
        {
            "text": "Excelente atención al cliente, resolvieron mi problema rápidamente",
            "category": "positivo",
            "sentiment_score": 2,
            "id": 3,
        },
        {
            "text": "El producto no coincide con la descripción",
            "category": "negativo",
            "sentiment_score": 0,
            "id": 4,
        },
    ]
