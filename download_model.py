from sentence_transformers import SentenceTransformer
import os

# Define the path to save the model
model_name = 'all-MiniLM-L6-v2'
save_path = './model/'

# Create the directory if it doesn't exist
if not os.path.exists(save_path):
    os.makedirs(save_path)

print(f"Downloading model '{model_name}' to '{save_path}'...")

# Download and save the model to the specified path
model = SentenceTransformer(model_name)
model.save(save_path)

print("\nModel downloaded and saved successfully!")