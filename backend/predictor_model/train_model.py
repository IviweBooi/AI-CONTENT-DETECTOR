import json
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset

# Load combined dataset
with open("combined_dataset.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Map labels to integers
label_map = {"human": 0, "ai": 1}
for sample in data:
    sample["label"] = label_map[sample["label"]]

# Create Hugging Face Dataset and split
dataset = Dataset.from_list(data)
dataset = dataset.train_test_split(test_size=0.2)

# Tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("roberta-base")

def preprocess(examples):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=256)

dataset = dataset.map(preprocess, batched=True)

model = AutoModelForSequenceClassification.from_pretrained("roberta-base", num_labels=2)

training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    logging_dir="./logs",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
)

trainer.train()
