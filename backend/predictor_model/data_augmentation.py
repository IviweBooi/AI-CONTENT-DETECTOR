#!/usr/bin/env python3
"""
Data Augmentation and Preprocessing Pipeline for AI Text Detection
"""

import json
import random
import re
from typing import List, Dict, Any

class DataAugmentationPipeline:
    def __init__(self, augmentation_factor: float = 2.0):
        self.augmentation_factor = augmentation_factor
        self.min_text_length = 50
        self.max_text_length = 2000
        
        self.contractions = {
            "do not": "don't", "does not": "doesn't", "did not": "didn't",
            "will not": "won't", "cannot": "can't", "is not": "isn't",
            "are not": "aren't", "have not": "haven't"
        }
    
    def preprocess_dataset(self, dataset_path: str, output_path: str) -> Dict[str, Any]:
        print("Loading and preprocessing dataset...")
        
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        original_count = len(data)
        processed_data = []
        
        for item in data:
            text = item.get('text', '')
            label = item.get('label', 0)
            
            cleaned_text = self._clean_text(text)
            
            if self._is_valid_text(cleaned_text):
                processed_data.append({
                    'text': cleaned_text,
                    'label': label,
                    'original': True
                })
        
        balanced_data = self._balance_dataset(processed_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(balanced_data, f, indent=2, ensure_ascii=False)
        
        stats = {
            'original_samples': original_count,
            'valid_samples': len(processed_data),
            'balanced_samples': len(balanced_data),
            'ai_samples': sum(1 for item in balanced_data if item['label'] == 1),
            'human_samples': sum(1 for item in balanced_data if item['label'] == 0)
        }
        
        print(f"Preprocessing complete: {stats}")
        return stats
    
    def augment_dataset(self, dataset_path: str, output_path: str) -> Dict[str, Any]:
        print("Starting data augmentation...")
        
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        augmented_data = list(data)
        original_count = len(data)
        
        target_count = int(original_count * self.augmentation_factor)
        samples_to_create = target_count - original_count
        
        print(f"Creating {samples_to_create} augmented samples...")
        
        for i in range(samples_to_create):
            original_sample = random.choice(data)
            
            augmented_text = self._apply_augmentation(
                original_sample['text'], 
                original_sample['label']
            )
            
            if self._is_valid_text(augmented_text):
                augmented_data.append({
                    'text': augmented_text,
                    'label': original_sample['label'],
                    'original': False,
                    'augmentation_id': i
                })
        
        random.shuffle(augmented_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(augmented_data, f, indent=2, ensure_ascii=False)
        
        stats = {
            'original_samples': original_count,
            'augmented_samples': len(augmented_data),
            'augmentation_ratio': len(augmented_data) / original_count,
            'ai_samples': sum(1 for item in augmented_data if item['label'] == 1),
            'human_samples': sum(1 for item in augmented_data if item['label'] == 0)
        }
        
        print(f"Augmentation complete: {stats}")
        return stats
    
    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        
        return text.strip()
    
    def _is_valid_text(self, text: str) -> bool:
        if not text or len(text.strip()) < self.min_text_length:
            return False
        
        if len(text) > self.max_text_length:
            return False
        
        words = text.split()
        if len(words) < 10:
            return False
        
        alpha_ratio = sum(c.isalpha() for c in text) / len(text)
        if alpha_ratio < 0.6:
            return False
        
        return True
    
    def _balance_dataset(self, data: List[Dict]) -> List[Dict]:
        ai_samples = [item for item in data if item['label'] == 1]
        human_samples = [item for item in data if item['label'] == 0]
        
        target_count = min(len(ai_samples), len(human_samples))
        
        balanced_ai = random.sample(ai_samples, min(target_count, len(ai_samples)))
        balanced_human = random.sample(human_samples, min(target_count, len(human_samples)))
        
        balanced_data = balanced_ai + balanced_human
        random.shuffle(balanced_data)
        
        return balanced_data
    
    def _apply_augmentation(self, text: str, label: int) -> str:
        # Simple augmentation: add/remove contractions
        if label == 0 and random.random() < 0.5:  # Human text - add contractions
            for full_form, contraction in self.contractions.items():
                if random.random() < 0.3:
                    text = text.replace(full_form, contraction)
        elif label == 1 and random.random() < 0.5:  # AI text - remove contractions
            for full_form, contraction in self.contractions.items():
                if random.random() < 0.3:
                    text = text.replace(contraction, full_form)
        
        # Simple word shuffling for variety
        if random.random() < 0.2:
            sentences = text.split('. ')
            if len(sentences) > 2:
                random.shuffle(sentences)
                text = '. '.join(sentences)
        
        return text

def main():
    pipeline = DataAugmentationPipeline(augmentation_factor=2.5)
    
    original_dataset = "combined_dataset.json"
    preprocessed_dataset = "preprocessed_dataset.json"
    augmented_dataset = "augmented_dataset.json"
    
    print("Starting Data Augmentation Pipeline")
    print("=" * 50)
    
    try:
        preprocess_stats = pipeline.preprocess_dataset(original_dataset, preprocessed_dataset)
        print(f"Preprocessing Stats: {preprocess_stats}")
    except Exception as e:
        print(f"Preprocessing failed: {e}")
        return
    
    try:
        augment_stats = pipeline.augment_dataset(preprocessed_dataset, augmented_dataset)
        print(f"Augmentation Stats: {augment_stats}")
    except Exception as e:
        print(f"Augmentation failed: {e}")
        return
    
    print("\nData augmentation pipeline completed successfully!")
    print(f"Final dataset saved to: {augmented_dataset}")

if __name__ == "__main__":
    main()