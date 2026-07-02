#!/usr/bin/env python3
"""
Script CLI pour lancer l'entraînement SFT d'Ayiti-AI depuis la ligne de commande.

Utilisation:
    python scripts/run_training.py --train_file data/raw/seed_ht.jsonl
    python scripts/run_training.py --train_file data/raw/seed_ht.jsonl --val_file data/raw/val_ht.jsonl
    python scripts/run_training.py --config config/training_config.yaml --train_file data/raw/seed_ht.jsonl
"""
import argparse
import sys
import yaml
from pathlib import Path

# Reconfigure stdout and stderr to handle UTF-8 / emojis on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Permettre les imports depuis la racine du projet
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.training.trainer import train_sft


def load_yaml_config(path: str) -> dict:
    """Charge un fichier YAML de configuration."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def main():
    parser = argparse.ArgumentParser(
        description="Ayiti-AI — Lancement de l'entraînement SFT",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Fichier de config YAML (optionnel — les args CLI ont priorité)
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Chemin vers le fichier YAML de configuration (config/training_config.yaml)",
    )

    # Modèle
    parser.add_argument(
        "--model",
        type=str,
        default="Qwen/Qwen2.5-1.5B-Instruct",
        help="Identifiant HuggingFace du modèle de base",
    )

    # Données
    parser.add_argument(
        "--train_file",
        type=str,
        required=True,
        help="Chemin vers le fichier d'entraînement JSONL",
    )
    parser.add_argument(
        "--val_file",
        type=str,
        default=None,
        help="Chemin vers le fichier de validation JSONL (optionnel)",
    )

    # Sortie
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./results/ayiti_lora",
        help="Répertoire de sortie pour les checkpoints",
    )

    # Hyperparamètres (surchargent le YAML si fournis)
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--batch_size", type=int, default=None)
    parser.add_argument("--learning_rate", type=float, default=None)
    parser.add_argument("--lora_r", type=int, default=None)
    parser.add_argument("--lora_alpha", type=int, default=None)
    parser.add_argument("--max_seq_length", type=int, default=None)
    parser.add_argument(
        "--no_quantize",
        action="store_true",
        help="Désactiver la quantification 4-bit (pour CPU / test)",
    )

    args = parser.parse_args()

    # Charger les valeurs par défaut depuis le YAML si fourni
    yaml_config = {}
    if args.config:
        print(f"Chargement de la config: {args.config}")
        yaml_config = load_yaml_config(args.config)

    # Fusionner YAML + CLI (CLI a priorité)
    epochs = args.epochs or yaml_config.get("num_train_epochs", 3)
    batch_size = args.batch_size or yaml_config.get("per_device_train_batch_size", 1)
    learning_rate = args.learning_rate or float(yaml_config.get("learning_rate", 2e-4))
    lora_r = args.lora_r or 16
    lora_alpha = args.lora_alpha or 32
    max_seq_length = args.max_seq_length or yaml_config.get("max_seq_length", 512)

    print("\n" + "=" * 60)
    print("  🇭🇹  Ayiti-AI — Démarrage de l'entraînement")
    print("=" * 60)
    print(f"  Modèle       : {args.model}")
    print(f"  Train file   : {args.train_file}")
    print(f"  Val file     : {args.val_file or 'None'}")
    print(f"  Output dir   : {args.output_dir}")
    print(f"  Epochs       : {epochs}")
    print(f"  Batch size   : {batch_size}")
    print(f"  LR           : {learning_rate}")
    print(f"  LoRA r       : {lora_r}, alpha: {lora_alpha}")
    print(f"  Max seq len  : {max_seq_length}")
    print(f"  Quantization : {'Non' if args.no_quantize else 'Oui (4-bit)'}")
    print("=" * 60 + "\n")

    # Vérifier que le fichier d'entraînement existe
    if not Path(args.train_file).exists():
        print(f"❌ Fichier introuvable: {args.train_file}")
        sys.exit(1)

    train_sft(
        model_name_or_path=args.model,
        train_file_path=args.train_file,
        val_file_path=args.val_file,
        output_dir=args.output_dir,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        lora_r=lora_r,
        lora_alpha=lora_alpha,
        max_seq_length=max_seq_length,
    )

    print(f"\n✅ Entraînement terminé. Adapter sauvegardé dans: {args.output_dir}")


if __name__ == "__main__":
    main()
