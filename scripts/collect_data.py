#!/usr/bin/env python3
"""
Script de collecte et structuration de données seed pour Ayiti-AI.

Ce script aide à :
1. Valider des fichiers JSONL existants (format instruction/output).
2. Afficher des statistiques sur les datasets.
3. Fusionner plusieurs fichiers JSONL en un seul.
4. Convertir un CSV en JSONL (format instruction/output).

Utilisation:
    python scripts/collect_data.py --action validate --file data/raw/seed_ht.jsonl
    python scripts/collect_data.py --action stats --file data/raw/seed_ht.jsonl
    python scripts/collect_data.py --action merge --input data/raw/ --output data/raw/merged.jsonl
    python scripts/collect_data.py --action from_csv --file data/external/data.csv --out data/raw/out.jsonl
"""
import argparse
import json
import sys
import csv
from pathlib import Path
from typing import List, Dict
from collections import Counter

# Reconfigure stdout and stderr to handle UTF-8 / emojis on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')



# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

REQUIRED_KEYS = {"instruction", "output"}
OPTIONAL_KEYS = {"input", "language", "source", "domain"}


def validate_jsonl(filepath: str) -> bool:
    """Valide qu'un fichier JSONL respecte le format attendu."""
    path = Path(filepath)
    if not path.exists():
        print(f"❌ Fichier introuvable: {filepath}")
        return False

    errors = 0
    warnings = 0
    total = 0

    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            total += 1
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"  ❌ Ligne {i}: JSON invalide — {e}")
                errors += 1
                continue

            missing = REQUIRED_KEYS - set(obj.keys())
            if missing:
                print(f"  ❌ Ligne {i}: Clés manquantes — {missing}")
                errors += 1
                continue

            # Vérifications de contenu
            if not obj["instruction"].strip():
                print(f"  ⚠️  Ligne {i}: 'instruction' vide")
                warnings += 1
            if not obj["output"].strip():
                print(f"  ⚠️  Ligne {i}: 'output' vide")
                warnings += 1

            unknown = set(obj.keys()) - REQUIRED_KEYS - OPTIONAL_KEYS
            if unknown:
                print(f"  ⚠️  Ligne {i}: Clés inconnues — {unknown}")
                warnings += 1

    print(f"\n📊 Validation de {path.name}:")
    print(f"   Total lignes   : {total}")
    print(f"   Erreurs        : {errors}")
    print(f"   Avertissements : {warnings}")

    if errors == 0:
        print("   ✅ Fichier valide!")
        return True
    else:
        print("   ❌ Fichier invalide — corrigez les erreurs ci-dessus.")
        return False


# ---------------------------------------------------------------------------
# Statistiques
# ---------------------------------------------------------------------------

def print_stats(filepath: str):
    """Affiche des statistiques sur un fichier JSONL."""
    path = Path(filepath)
    records = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

    if not records:
        print("Aucun enregistrement valide trouvé.")
        return

    inst_lens = [len(r.get("instruction", "").split()) for r in records]
    out_lens = [len(r.get("output", "").split()) for r in records]
    langs = Counter(r.get("language", "unknown") for r in records)
    domains = Counter(r.get("domain", "unknown") for r in records)

    print(f"\n📊 Statistiques: {path.name}")
    print(f"   Exemples          : {len(records)}")
    print(f"   Instruction (mots): min={min(inst_lens)}, max={max(inst_lens)}, moy={sum(inst_lens)//len(inst_lens)}")
    print(f"   Output (mots)     : min={min(out_lens)}, max={max(out_lens)}, moy={sum(out_lens)//len(out_lens)}")
    print(f"   Langues           : {dict(langs)}")
    print(f"   Domaines          : {dict(domains)}")


# ---------------------------------------------------------------------------
# Fusion
# ---------------------------------------------------------------------------

def merge_jsonl(input_dir: str, output_file: str):
    """Fusionne tous les fichiers JSONL d'un répertoire."""
    input_path = Path(input_dir)
    files = list(input_path.glob("*.jsonl"))

    if not files:
        print(f"❌ Aucun fichier JSONL trouvé dans: {input_dir}")
        return

    total = 0
    with open(output_file, "w", encoding="utf-8") as out_f:
        for file_path in sorted(files):
            if file_path.resolve() == Path(output_file).resolve():
                continue
            count = 0
            with open(file_path, "r", encoding="utf-8") as in_f:
                for line in in_f:
                    if line.strip():
                        out_f.write(line if line.endswith("\n") else line + "\n")
                        count += 1
            print(f"  ✅ {file_path.name}: {count} exemples")
            total += count

    print(f"\n📦 Fusionné: {total} exemples → {output_file}")


# ---------------------------------------------------------------------------
# Conversion CSV → JSONL
# ---------------------------------------------------------------------------

def csv_to_jsonl(
    csv_file: str,
    output_file: str,
    instruction_col: str = "instruction",
    output_col: str = "output",
    language_col: str = None,
    language: str = "ht",
):
    """Convertit un fichier CSV en format JSONL instruction/output."""
    total = 0
    skipped = 0

    with open(csv_file, "r", encoding="utf-8") as in_f, \
         open(output_file, "w", encoding="utf-8") as out_f:

        reader = csv.DictReader(in_f)
        for row in reader:
            inst = row.get(instruction_col, "").strip()
            out = row.get(output_col, "").strip()

            if not inst or not out:
                skipped += 1
                continue

            record = {
                "instruction": inst,
                "output": out,
                "language": row.get(language_col, language) if language_col else language,
            }
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
            total += 1

    print(f"\n✅ Converti: {total} exemples → {output_file}")
    if skipped:
        print(f"   ⚠️  {skipped} lignes ignorées (vides)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Ayiti-AI — Utilitaire de données")
    parser.add_argument(
        "--action",
        required=True,
        choices=["validate", "stats", "merge", "from_csv"],
    )
    parser.add_argument("--file", type=str, default=None)
    parser.add_argument("--input", type=str, default="data/raw/")
    parser.add_argument("--output", type=str, default="data/raw/merged.jsonl")
    parser.add_argument("--instruction_col", type=str, default="instruction")
    parser.add_argument("--output_col", type=str, default="output")
    parser.add_argument("--language", type=str, default="ht")
    args = parser.parse_args()

    if args.action == "validate":
        if not args.file:
            print("❌ --file requis pour l'action 'validate'")
            sys.exit(1)
        validate_jsonl(args.file)

    elif args.action == "stats":
        if not args.file:
            print("❌ --file requis pour l'action 'stats'")
            sys.exit(1)
        print_stats(args.file)

    elif args.action == "merge":
        merge_jsonl(args.input, args.output)

    elif args.action == "from_csv":
        if not args.file:
            print("❌ --file requis pour l'action 'from_csv'")
            sys.exit(1)
        csv_to_jsonl(
            args.file,
            args.output,
            instruction_col=args.instruction_col,
            output_col=args.output_col,
            language=args.language,
        )


if __name__ == "__main__":
    main()
