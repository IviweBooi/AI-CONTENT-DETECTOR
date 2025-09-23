import json
import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, classification_report
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification, 
    Trainer, 
    TrainingArguments,
    EarlyStoppingCallback,
    get_cosine_schedule_with_warmup
)
from datasets import Dataset
import logging
from datetime import datetime
import os
import random
from torch.utils.data import WeightedRandomSampler
import matplotlib.pyplot as plt
import seaborn as sns

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedAIDetectorTrainer:
    def __init__(self, dataset_path="trainingDataset.json", model_name="roberta-base"):
        self.dataset_path = dataset_path
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.label_map = {"human": 0, "ai": 1}
        
        # Create output directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"./enhanced_model_{timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Enhanced training parameters
        self.max_length = 512
        self.train_batch_size = 8  # Smaller batch for better gradient updates
        self.eval_batch_size = 16
        self.learning_rate = 1e-5  # Lower learning rate for fine-tuning
        self.num_epochs = 15
        self.warmup_ratio = 0.1
        self.weight_decay = 0.01
        
    def augment_text(self, text, augmentation_type="synonym"):
        """Simple text augmentation techniques"""
        if augmentation_type == "synonym" and len(text) > 100:
            # Simple word replacement for longer texts
            words = text.split()
            if len(words) > 10:
                # Replace some common words with synonyms
                replacements = {
                    "good": "excellent", "bad": "poor", "big": "large", 
                    "small": "tiny", "fast": "quick", "slow": "gradual",
                    "important": "crucial", "easy": "simple", "hard": "difficult"
                }
                for i, word in enumerate(words):
                    if word.lower() in replacements and random.random() < 0.1:
                        words[i] = replacements[word.lower()]
                return " ".join(words)
        elif augmentation_type == "punctuation":
            # Slight punctuation modifications
            if random.random() < 0.3:
                text = text.replace(".", " .")
            if random.random() < 0.3:
                text = text.replace(",", " ,")
        
        return text
    
    def load_and_prepare_data(self, augment_data=True):
        """Load dataset with enhanced preprocessing and optional augmentation"""
        logger.info(f"Loading dataset from {self.dataset_path}")
        
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Enhanced data preprocessing
        processed_data = []
        augmented_count = 0
        
        for sample in data:
            # Skip very short texts
            if len(sample["text"]) < 50:
                continue
                
            # Clean and normalize text
            text = sample["text"].strip()
            text = ' '.join(text.split())  # Normalize whitespace
            
            # Add original sample
            processed_data.append({
                "text": text,
                "label": self.label_map[sample["label"]],
                "original": True
            })
            
            # Add augmented samples for training diversity (only for human texts to balance)
            if augment_data and sample["label"] == "human" and len(text) > 200 and random.random() < 0.3:
                aug_text = self.augment_text(text, "synonym")
                if aug_text != text:
                    processed_data.append({
                        "text": aug_text,
                        "label": self.label_map[sample["label"]],
                        "original": False
                    })
                    augmented_count += 1
        
        logger.info(f"Processed {len(processed_data)} samples from {len(data)} original samples")
        logger.info(f"Added {augmented_count} augmented samples")
        
        # Create dataset and split with stratification
        dataset = Dataset.from_list(processed_data)
        
        # Calculate class distribution
        labels = [sample["label"] for sample in processed_data]
        human_count = labels.count(0)
        ai_count = labels.count(1)
        logger.info(f"Class distribution - Human: {human_count}, AI: {ai_count}")
        
        # Split dataset (80/10/10 train/val/test) with manual stratification
        dataset = dataset.train_test_split(test_size=0.2, seed=42)
        val_test = dataset["test"].train_test_split(test_size=0.5, seed=42)
        
        return {
            "train": dataset["train"],
            "validation": val_test["train"],
            "test": val_test["test"]
        }
    
    def preprocess_function(self, examples):
        """Enhanced tokenization with attention to special tokens"""
        return self.tokenizer(
            examples["text"],
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_attention_mask=True,
            return_token_type_ids=False
        )
    
    def compute_metrics(self, eval_pred):
        """Comprehensive evaluation metrics with focus on false positive reduction"""
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
        
        # Calculate false positive rate (important for our use case)
        tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)
        false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0
        false_negative_rate = fn / (fn + tp) if (fn + tp) > 0 else 0
        
        metrics = {
            'accuracy': accuracy,
            'f1': f1,
            'precision': precision,
            'recall': recall,
            'false_positive_rate': false_positive_rate,
            'false_negative_rate': false_negative_rate,
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
    
    def create_class_weighted_trainer(self, model, train_dataset, eval_dataset, original_train_dataset):
        """Create trainer with class weighting to handle imbalance"""
        
        # Calculate class weights from original dataset
        labels = [example["label"] for example in original_train_dataset]
        class_counts = np.bincount(labels)
        total_samples = len(labels)
        class_weights = total_samples / (len(class_counts) * class_counts)
        
        logger.info(f"Class weights: {class_weights}")
        
        # Enhanced training arguments with focus on reducing false positives
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=self.num_epochs,
            per_device_train_batch_size=self.train_batch_size,
            per_device_eval_batch_size=self.eval_batch_size,
            warmup_ratio=self.warmup_ratio,
            weight_decay=self.weight_decay,
            logging_dir=f"{self.output_dir}/logs",
            logging_steps=50,
            eval_strategy="steps",
            eval_steps=200,
            save_strategy="steps",
            save_steps=200,
            save_total_limit=5,
            load_best_model_at_end=True,
            metric_for_best_model="f1",  # Focus on F1 score
            greater_is_better=True,
            learning_rate=self.learning_rate,
            lr_scheduler_type="cosine_with_restarts",
            dataloader_num_workers=2,
            fp16=torch.cuda.is_available(),
            gradient_checkpointing=True,
            gradient_accumulation_steps=2,  # Effective batch size = 16
            report_to=None,
            seed=42,
            data_seed=42,
            remove_unused_columns=False,
        )
        
        # Custom trainer with class weighting
        class WeightedTrainer(Trainer):
            def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
                labels = inputs.get("labels")
                outputs = model(**inputs)
                logits = outputs.get('logits')
                
                # Apply class weights
                weight_tensor = torch.tensor(class_weights, dtype=torch.float).to(logits.device)
                loss_fct = nn.CrossEntropyLoss(weight=weight_tensor)
                loss = loss_fct(logits.view(-1, self.model.config.num_labels), labels.view(-1))
                
                return (loss, outputs) if return_outputs else loss
        
        trainer = WeightedTrainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            compute_metrics=self.compute_metrics,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=5)]
        )
        
        return trainer
    
    def train_enhanced_model(self):
        """Train the enhanced model with advanced techniques"""
        # Load and prepare data
        datasets = self.load_and_prepare_data(augment_data=True)
        
        # Tokenize datasets
        tokenized_datasets = {}
        for split_name, dataset in datasets.items():
            tokenized_datasets[split_name] = dataset.map(
                self.preprocess_function, 
                batched=True,
                remove_columns=[col for col in dataset.column_names if col not in ['label']]
            )
        
        # Load model with custom configuration
        model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name, 
            num_labels=2,
            problem_type="single_label_classification",
            hidden_dropout_prob=0.3,  # Increased dropout for regularization
            attention_probs_dropout_prob=0.3
        )
        
        # Create weighted trainer
        trainer = self.create_class_weighted_trainer(
            model, 
            tokenized_datasets["train"], 
            tokenized_datasets["validation"],
            datasets["train"]
        )
        
        # Train the model
        logger.info("Starting enhanced training...")
        trainer.train()
        
        # Evaluate on test set
        logger.info("Evaluating on test set...")
        test_results = trainer.evaluate(tokenized_datasets["test"])
        logger.info(f"Test results: {test_results}")
        
        # Generate detailed test predictions for analysis
        test_predictions = trainer.predict(tokenized_datasets["test"])
        self.analyze_predictions(test_predictions, datasets["test"])
        
        # Save the final model
        final_model_path = f"{self.output_dir}/final_model"
        trainer.save_model(final_model_path)
        self.tokenizer.save_pretrained(final_model_path)
        
        logger.info(f"Enhanced model saved to {final_model_path}")
        
        # Save comprehensive training summary
        summary = {
            "model_name": self.model_name,
            "training_args": trainer.args.to_dict(),
            "test_results": test_results,
            "model_path": final_model_path,
            "timestamp": datetime.now().isoformat(),
            "enhancements": [
                "Data augmentation for human texts",
                "Class weighting for balanced training",
                "Increased dropout for regularization",
                "Cosine learning rate schedule with restarts",
                "Early stopping with patience=5",
                "Focus on F1 score optimization"
            ]
        }
        
        with open(f"{self.output_dir}/enhanced_training_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        return final_model_path, test_results
    
    def analyze_predictions(self, predictions, test_dataset):
        """Analyze predictions to identify patterns in misclassifications"""
        pred_labels = np.argmax(predictions.predictions, axis=1)
        true_labels = predictions.label_ids
        
        # Find misclassified examples
        misclassified = []
        for i, (pred, true) in enumerate(zip(pred_labels, true_labels)):
            if pred != true:
                text = test_dataset[i]["text"]
                misclassified.append({
                    "text": text[:200] + "..." if len(text) > 200 else text,
                    "true_label": "Human" if true == 0 else "AI",
                    "predicted_label": "Human" if pred == 0 else "AI",
                    "confidence": float(np.max(predictions.predictions[i]))
                })
        
        # Save misclassified examples for analysis
        with open(f"{self.output_dir}/misclassified_examples.json", "w") as f:
            json.dump(misclassified, f, indent=2)
        
        logger.info(f"Found {len(misclassified)} misclassified examples out of {len(pred_labels)}")

if __name__ == "__main__":
    # Initialize enhanced trainer
    trainer = EnhancedAIDetectorTrainer()
    
    # Train the enhanced model
    try:
        model_path, results = trainer.train_enhanced_model()
        print(f"\n=== Enhanced Training Complete ===")
        print(f"Model saved to: {model_path}")
        print(f"Test Results: {results}")
        print(f"\nKey improvements:")
        print("- Data augmentation for better generalization")
        print("- Class weighting for balanced training")
        print("- Enhanced regularization to reduce overfitting")
        print("- Focus on reducing false positives")
        print("\nTo use this model, update the model_path in ai_text_classifier.py")
    except Exception as e:
        logger.error(f"Enhanced training failed: {e}")
        raise