import json
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification, 
    Trainer, 
    TrainingArguments,
    EarlyStoppingCallback
)
from datasets import Dataset
import torch
import logging
from datetime import datetime
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImprovedAIDetectorTrainer:
    def __init__(self, dataset_path="combined_dataset.json", model_name="roberta-base"):
        self.dataset_path = dataset_path
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.label_map = {"human": 0, "ai": 1}
        
        # Create output directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"./improved_model_{timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)
        
    def load_and_prepare_data(self):
        """Load dataset and prepare for training with better preprocessing"""
        logger.info(f"Loading dataset from {self.dataset_path}")
        
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Enhanced data preprocessing
        processed_data = []
        for sample in data:
            # Skip very short texts (less than 50 characters)
            if len(sample["text"]) < 50:
                continue
                
            # Clean and normalize text
            text = sample["text"].strip()
            text = ' '.join(text.split())  # Normalize whitespace
            
            processed_data.append({
                "text": text,
                "label": self.label_map[sample["label"]]
            })
        
        logger.info(f"Processed {len(processed_data)} samples from {len(data)} original samples")
        
        # Create dataset and split with stratification
        dataset = Dataset.from_list(processed_data)
        
        # Calculate class distribution
        labels = [sample["label"] for sample in processed_data]
        human_count = labels.count(0)
        ai_count = labels.count(1)
        logger.info(f"Class distribution - Human: {human_count}, AI: {ai_count}")
        
        # Split with stratification (80/10/10 train/val/test)
        dataset = dataset.train_test_split(test_size=0.2, stratify=labels, seed=42)
        val_test = dataset["test"].train_test_split(test_size=0.5, seed=42)
        
        return {
            "train": dataset["train"],
            "validation": val_test["train"],
            "test": val_test["test"]
        }
    
    def preprocess_function(self, examples):
        """Enhanced tokenization with dynamic padding"""
        return self.tokenizer(
            examples["text"],
            truncation=True,
            padding="max_length",
            max_length=512,  # Increased from 256 for better context
            return_attention_mask=True
        )
    
    def compute_metrics(self, eval_pred):
        """Comprehensive evaluation metrics"""
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        
        # Calculate metrics
        accuracy = accuracy_score(labels, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average='weighted')
        
        # Per-class metrics
        precision_per_class, recall_per_class, f1_per_class, _ = precision_recall_fscore_support(
            labels, predictions, average=None
        )
        
        # Confusion matrix
        cm = confusion_matrix(labels, predictions)
        
        metrics = {
            'accuracy': accuracy,
            'f1': f1,
            'precision': precision,
            'recall': recall,
            'human_precision': precision_per_class[0] if len(precision_per_class) > 0 else 0,
            'human_recall': recall_per_class[0] if len(recall_per_class) > 0 else 0,
            'human_f1': f1_per_class[0] if len(f1_per_class) > 0 else 0,
            'ai_precision': precision_per_class[1] if len(precision_per_class) > 1 else 0,
            'ai_recall': recall_per_class[1] if len(recall_per_class) > 1 else 0,
            'ai_f1': f1_per_class[1] if len(f1_per_class) > 1 else 0,
        }
        
        logger.info(f"Evaluation metrics: {metrics}")
        logger.info(f"Confusion Matrix:\n{cm}")
        
        return metrics
    
    def train_model(self):
        """Train the improved model with better hyperparameters"""
        # Load and prepare data
        datasets = self.load_and_prepare_data()
        
        # Tokenize datasets
        tokenized_datasets = {}
        for split_name, dataset in datasets.items():
            tokenized_datasets[split_name] = dataset.map(
                self.preprocess_function, 
                batched=True,
                remove_columns=dataset.column_names
            )
        
        # Load model
        model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name, 
            num_labels=2,
            problem_type="single_label_classification"
        )
        
        # Enhanced training arguments
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=10,  # Increased from 3
            per_device_train_batch_size=16,  # Increased from 8
            per_device_eval_batch_size=16,
            warmup_steps=500,  # Learning rate warmup
            weight_decay=0.01,  # L2 regularization
            logging_dir=f"{self.output_dir}/logs",
            logging_steps=50,
            evaluation_strategy="steps",
            eval_steps=200,
            save_strategy="steps",
            save_steps=200,
            save_total_limit=3,
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            greater_is_better=True,
            learning_rate=2e-5,  # Optimized learning rate
            lr_scheduler_type="cosine",  # Cosine learning rate schedule
            dataloader_num_workers=4,
            fp16=torch.cuda.is_available(),  # Mixed precision if GPU available
            gradient_checkpointing=True,  # Memory optimization
            report_to=None,  # Disable wandb/tensorboard
        )
        
        # Create trainer with early stopping
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_datasets["train"],
            eval_dataset=tokenized_datasets["validation"],
            compute_metrics=self.compute_metrics,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
        )
        
        # Train the model
        logger.info("Starting training...")
        trainer.train()
        
        # Evaluate on test set
        logger.info("Evaluating on test set...")
        test_results = trainer.evaluate(tokenized_datasets["test"])
        logger.info(f"Test results: {test_results}")
        
        # Save the final model
        final_model_path = f"{self.output_dir}/final_model"
        trainer.save_model(final_model_path)
        self.tokenizer.save_pretrained(final_model_path)
        
        logger.info(f"Model saved to {final_model_path}")
        
        # Save training summary
        summary = {
            "model_name": self.model_name,
            "training_args": training_args.to_dict(),
            "test_results": test_results,
            "model_path": final_model_path,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(f"{self.output_dir}/training_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        return final_model_path, test_results

if __name__ == "__main__":
    # Initialize trainer
    trainer = ImprovedAIDetectorTrainer()
    
    # Train the model
    try:
        model_path, results = trainer.train_model()
        print(f"\n=== Training Complete ===")
        print(f"Model saved to: {model_path}")
        print(f"Test Results: {results}")
        print("\nTo use this model, update the model_path in ai_text_classifier.py")
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise