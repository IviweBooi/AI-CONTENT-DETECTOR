#!/usr/bin/env python3
"""
Simplified Incremental Fine-tuning Script for AI Content Detector
Trains the model in smaller chunks for manageable daily training sessions.
"""

import os
import json
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import numpy as np
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer, EarlyStoppingCallback
)
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IncrementalAIDetectorTrainer:
    def __init__(self, 
                 model_name: str = "roberta-base",
                 max_length: int = 512,
                 chunk_size: int = 2000,
                 checkpoint_dir: str = "incremental_checkpoints"):
        """Initialize the incremental trainer."""
        self.model_name = model_name
        self.max_length = max_length
        self.chunk_size = chunk_size
        self.checkpoint_dir = checkpoint_dir
        
        # Create checkpoint directory
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        # Initialize tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Training state
        self.current_chunk = 0
        self.total_chunks = 0
        self.training_history = []
        
        logger.info(f"Initialized incremental trainer with chunk size: {chunk_size}")

    def load_and_prepare_data(self, data_file: str = "trainingDataset.json") -> List[Dict]:
        """Load and prepare the dataset."""
        logger.info("Loading dataset...")
        
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Loaded {len(data)} samples")
        return data

    def create_data_chunks(self, data: List[Dict]) -> List[List[Dict]]:
        """Split dataset into manageable chunks."""
        total_samples = len(data)
        self.total_chunks = (total_samples + self.chunk_size - 1) // self.chunk_size
        
        chunks = []
        for i in range(0, total_samples, self.chunk_size):
            end_idx = min(i + self.chunk_size, total_samples)
            chunk = data[i:end_idx]
            chunks.append(chunk)
        
        logger.info(f"Created {len(chunks)} chunks of ~{self.chunk_size} samples each")
        return chunks

    def preprocess_function(self, examples):
        """Tokenize the texts."""
        return self.tokenizer(
            examples['text'],
            truncation=True,
            padding=True,
            max_length=self.max_length
        )

    def load_or_create_model(self) -> AutoModelForSequenceClassification:
        """Load existing checkpoint or create new model."""
        latest_checkpoint = self.get_latest_checkpoint()
        
        if latest_checkpoint:
            logger.info(f"Loading model from checkpoint: {latest_checkpoint}")
            model = AutoModelForSequenceClassification.from_pretrained(latest_checkpoint)
        else:
            logger.info(f"Creating new model from: {self.model_name}")
            model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                num_labels=2,
                id2label={0: "human", 1: "ai"},
                label2id={"human": 0, "ai": 1}
            )
        
        return model

    def get_latest_checkpoint(self) -> Optional[str]:
        """Get the latest checkpoint directory."""
        if not os.path.exists(self.checkpoint_dir):
            return None
        
        model_dirs = [d for d in os.listdir(self.checkpoint_dir) 
                     if d.startswith("model_after_chunk_")]
        
        if not model_dirs:
            return None
        
        # Sort by chunk number
        model_dirs.sort(key=lambda x: int(x.split("_")[-1]))
        latest = os.path.join(self.checkpoint_dir, model_dirs[-1])
        
        if os.path.exists(latest):
            return latest
        return None

    def compute_class_weights(self, labels: List[int]) -> torch.Tensor:
        """Compute class weights for balanced training."""
        unique_labels = np.unique(labels)
        class_weights = compute_class_weight(
            'balanced',
            classes=unique_labels,
            y=labels
        )
        return torch.tensor(class_weights, dtype=torch.float32)

    def compute_metrics(self, eval_pred):
        """Compute evaluation metrics."""
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        
        precision, recall, f1, _ = precision_recall_fscore_support(
            labels, predictions, average='weighted'
        )
        accuracy = accuracy_score(labels, predictions)
        
        return {
            'accuracy': accuracy,
            'f1': f1,
            'precision': precision,
            'recall': recall
        }

    def train_chunk(self, chunk: List[Dict], chunk_idx: int) -> Dict:
        """Train on a single chunk of data."""
        logger.info(f"Training chunk {chunk_idx + 1}/{self.total_chunks}")
        
        # Extract texts and labels
        texts = [item['text'] for item in chunk]
        labels = [1 if item['label'] == 'ai' else 0 for item in chunk]
        
        # Split chunk into train/val
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            texts, labels,
            test_size=0.2,
            random_state=42,
            stratify=labels
        )
        
        # Create datasets
        train_dataset = Dataset.from_dict({
            'text': train_texts,
            'labels': train_labels  # Use 'labels' for transformers
        })
        val_dataset = Dataset.from_dict({
            'text': val_texts,
            'labels': val_labels
        })
        
        # Tokenize
        train_dataset = train_dataset.map(
            self.preprocess_function,
            batched=True,
            remove_columns=['text']
        )
        val_dataset = val_dataset.map(
            self.preprocess_function,
            batched=True,
            remove_columns=['text']
        )
        
        # Load model
        model = self.load_or_create_model()
        
        # Compute class weights
        class_weights = self.compute_class_weights(train_labels)
        logger.info(f"Class weights: {class_weights}")
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=f"{self.checkpoint_dir}/chunk_{chunk_idx}",
            num_train_epochs=2,  # Fewer epochs per chunk
            per_device_train_batch_size=8,
            per_device_eval_batch_size=16,
            warmup_steps=50,
            weight_decay=0.01,
            logging_dir=f"{self.checkpoint_dir}/logs",
            logging_steps=25,
            eval_strategy="steps",
            eval_steps=50,
            save_strategy="steps",
            save_steps=100,
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            greater_is_better=True,
            report_to=None,
            save_total_limit=2,
        )
        
        # Create trainer with class weights
        class WeightedTrainer(Trainer):
            def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
                labels = inputs.get("labels")
                outputs = model(**inputs)
                logits = outputs.get("logits")
                
                # Apply class weights
                loss_fct = torch.nn.CrossEntropyLoss(weight=class_weights.to(logits.device))
                loss = loss_fct(logits.view(-1, self.model.config.num_labels), labels.view(-1))
                
                return (loss, outputs) if return_outputs else loss
        
        trainer = WeightedTrainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            compute_metrics=self.compute_metrics,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
        )
        
        # Train
        logger.info("Starting training...")
        train_result = trainer.train()
        
        # Evaluate
        eval_result = trainer.evaluate()
        
        # Save final model for this chunk
        final_model_path = f"{self.checkpoint_dir}/model_after_chunk_{chunk_idx}"
        trainer.save_model(final_model_path)
        
        # Record training history
        chunk_history = {
            'chunk': chunk_idx,
            'train_samples': len(train_dataset),
            'val_samples': len(val_dataset),
            'train_loss': train_result.training_loss,
            'eval_metrics': eval_result,
            'timestamp': datetime.now().isoformat()
        }
        
        self.training_history.append(chunk_history)
        
        # Save training history
        with open(f"{self.checkpoint_dir}/training_history.json", 'w') as f:
            json.dump(self.training_history, f, indent=2)
        
        logger.info(f"Chunk {chunk_idx + 1} completed. Eval metrics: {eval_result}")
        return chunk_history

    def train_incremental(self, data_file: str = "trainingDataset.json", 
                         start_chunk: int = 0, max_chunks: Optional[int] = None):
        """Train incrementally on data chunks."""
        # Load data
        data = self.load_and_prepare_data(data_file)
        
        # Create chunks
        chunks = self.create_data_chunks(data)
        
        # Determine chunks to train
        end_chunk = min(len(chunks), start_chunk + (max_chunks or len(chunks)))
        
        logger.info(f"Training chunks {start_chunk} to {end_chunk - 1}")
        
        # Train each chunk
        for i in range(start_chunk, end_chunk):
            try:
                chunk_result = self.train_chunk(chunks[i], i)
                logger.info(f"Completed chunk {i + 1}/{len(chunks)}")
                
                # Save progress
                self.current_chunk = i + 1
                
            except Exception as e:
                logger.error(f"Error training chunk {i}: {e}")
                break
        
        logger.info("Incremental training session completed!")
        self.print_training_summary()

    def print_training_summary(self):
        """Print a summary of training progress."""
        if not self.training_history:
            logger.info("No training history available.")
            return
        
        logger.info("\n" + "="*50)
        logger.info("TRAINING SUMMARY")
        logger.info("="*50)
        
        total_samples = sum(h['train_samples'] for h in self.training_history)
        latest_metrics = self.training_history[-1]['eval_metrics']
        
        logger.info(f"Total chunks trained: {len(self.training_history)}")
        logger.info(f"Total samples processed: {total_samples}")
        logger.info(f"Latest evaluation metrics:")
        for metric, value in latest_metrics.items():
            logger.info(f"  {metric}: {value:.4f}")
        
        logger.info("="*50)

def main():
    parser = argparse.ArgumentParser(description="Incremental AI Content Detector Training")
    parser.add_argument("--chunk-size", type=int, default=2000, 
                       help="Number of samples per training chunk")
    parser.add_argument("--max-chunks", type=int, default=1,
                       help="Maximum number of chunks to train in this session")
    parser.add_argument("--continue-training", action="store_true",
                       help="Continue from previous checkpoint")
    parser.add_argument("--data-file", type=str, default="trainingDataset.json",
                       help="Path to training data file")
    
    args = parser.parse_args()
    
    # Initialize trainer
    trainer = IncrementalAIDetectorTrainer(chunk_size=args.chunk_size)
    
    trainer.train_incremental(
        data_file=args.data_file,
        max_chunks=args.max_chunks
    )

if __name__ == "__main__":
    main()