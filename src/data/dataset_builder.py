import json
import pandas as pd
from datasets import Dataset
from pathlib import Path
import logging
import re
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AyitiDatasetBuilder:
    def __init__(self, raw_path="data/raw/", processed_path="data/processed/"):
        self.raw_path = Path(raw_path)
        self.processed_path = Path(processed_path)
        self.processed_path.mkdir(parents=True, exist_ok=True)
    
    def load_raw_files(self, pattern="*.jsonl") -> List[Dict]:
        data = []
        for file_path in self.raw_path.glob(pattern):
            logger.info(f"Chargement: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))
        return data
    
    def clean_text(self, text: str) -> str:
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def build_train_dataset(self) -> Dataset:
        raw_data = self.load_raw_files()
        for item in raw_data:
            if 'instruction' in item:
                item['instruction'] = self.clean_text(item['instruction'])
            if 'output' in item:
                item['output'] = self.clean_text(item['output'])
        df = pd.DataFrame(raw_data)
        dataset = Dataset.from_pandas(df)
        output_file = self.processed_path / "ayiti_train.parquet"
        dataset.to_parquet(str(output_file))
        logger.info(f"Sauvegardé: {output_file} ({len(dataset)} exemples)")
        return dataset
    
    def build_tokenizer_corpus(self) -> str:
        raw_data = self.load_raw_files()
        texts = []
        for item in raw_data:
            texts.append(item.get('instruction', ''))
            texts.append(item.get('output', ''))
        corpus_file = self.processed_path / "tokenizer_corpus.txt"
        with open(corpus_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(texts))
        logger.info(f"Corpus sauvegardé: {corpus_file}")
        return str(corpus_file)

if __name__ == "__main__":
    builder = AyitiDatasetBuilder()
    builder.build_train_dataset()
    builder.build_tokenizer_corpus()
