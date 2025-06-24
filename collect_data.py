from github import Github
import re
from datasets import Dataset

# Initialize PyGithub with your GitHub token
g = Github("GITHUB_TOKEN")

# Specify the repository
repo = g.get_repo("openai/gym")

# Function to extract Python function names from code
def extract_functions_from_code(code):
    pattern = re.compile(r"def\s+(\w+)\s*\(.*\):")
    functions = pattern.findall(code)
    return functions

# Fetch Python files from the repository
python_files = []
contents = repo.get_contents("")
while contents:
    file_content = contents.pop(0)
    if file_content.type == "dir":
        contents.extend(repo.get_contents(file_content.path))
    elif file_content.path.endswith(".py"):
        python_files.append(file_content)

# Extract functions and create dataset
data = {"code": [], "function_name": []}
for file in python_files:
    code = file.decoded_content.decode("utf-8")
    functions = extract_functions_from_code(code)
    for function in functions:
        data["code"].append(code)
        data["function_name"].append(function)

# Create a Hugging Face dataset
dataset = Dataset.from_dict(data)

# Save the dataset to disk
dataset.save_to_disk("code_generation_dataset")

print("Dataset created and saved to disk.")
