from datasets import load_from_disk
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("Salesforce/codegen-350M-mono")
model = AutoModelForCausalLM.from_pretrained("Salesforce/codegen-350M-mono")

# Set the pad_token to eos_token
tokenizer.pad_token = tokenizer.eos_token

# Load the dataset
dataset = load_from_disk("code_generation_dataset")

# Split the dataset into training and test sets
dataset = dataset.train_test_split(test_size=0.1)

# Preprocess the dataset
def preprocess_function(examples):
    return tokenizer(examples['code'], truncation=True, padding='max_length')

tokenized_datasets = dataset.map(preprocess_function, batched=True)

# Fine-tune the model
training_args = TrainingArguments(
    output_dir="./results",
    per_device_train_batch_size=2,
    num_train_epochs=1,
    save_steps=10_000,
    save_total_limit=2,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets['train'],
    eval_dataset=tokenized_datasets['test']
)

trainer.train()
