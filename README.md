# Code Generation

A tool for collecting, analyzing, and generating Python code using machine learning models. This project scrapes functions from GitHub repositories, processes them into a structured dataset, and uses them to fine-tune language models for code generation.

## Overview

This project implements an end-to-end pipeline for:
1. Collecting Python functions from GitHub repositories
2. Processing and storing the code in a structured dataset
3. Fine-tuning language models on the collected code
4. Generating new code based on prompts

## Installation

```bash
# Clone the repository
git clone https://github.com/tejaskaher999/Code-Generation.git
cd Code-Generation

# Install required dependencies
pip install PyGithub datasets transformers torch
```

## Usage

### 1. Collecting Data

The [`collect_data.py`](collect_data.py) script collects Python functions from specified GitHub repositories.

```bash
python collect_data.py
```

Make sure to replace `"GITHUB_TOKEN"` with your actual GitHub token.

### 2. Fine-tuning Models

Use [`fine_tune.py`](fine_tune.py) to fine-tune a language model on the collected dataset.

```bash
python fine_tune.py
```

### 3. Generating Code

Generate code using the fine-tuned model with [`generatecode.py`](generatecode.py).

```bash
python generatecode.py
```

## Project Structure

```
├── collect_data.py      # Script to collect data from GitHub
├── fine_tune.py         # Script to fine-tune the model
├── generatecode.py      # Script to generate code using the model
├── code_generation_dataset/ # Dataset files
├── results/             # Generated code results
├── static/              # Static resources
└── README.md            # This file
```

## Dataset

The dataset is stored in Arrow format and contains code snippets along with their function names, extracted from the OpenAI Gym repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

This project was created in collaboration by:
- [Tejas Aher](https://github.com/tejaskaher999)
- [Komal Dhake](https://github.com/komal0001)

Under the guidance of:
- Prof. S. S. Shaikh