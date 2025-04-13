from langchain_community.llms import LlamaCpp
import os
import os
import requests
from tqdm import tqdm


def download_model(url, save_path):
    """Download a file with progress bar."""
    if os.path.exists(save_path):
        print(f"Model file already exists at {save_path}")
        return

    print(f"Downloading model from {url} to {save_path}")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("content-length", 0))

    with open(save_path, "wb") as file, tqdm(
        total=total_size, unit="B", unit_scale=True
    ) as progress_bar:
        for data in response.iter_content(chunk_size=1024):
            file.write(data)
            progress_bar.update(len(data))

    print("Download complete!")


def load_local_model(model_path, max_tokens=256):
    """Load a local GGUF model using LlamaCpp.

    Args:
        model_path (str): Path to the GGUF model file
        temperature (float): Sampling temperature
        max_tokens (int): Maximum number of tokens to generate
        n_gpu_layers (int): Number of layers to offload to GPU (-1 for all)

    Returns:
        LlamaCpp: Initialized language model
    """
    # Check if model file exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")

    # Initialize LlamaCpp model
    model = LlamaCpp(
        model_path=model_path,
        max_tokens=max_tokens,
        n_ctx=2048,
        n_gpu_layers=-1,
        f16_kv=True,
        verbose=True
    )

    return model
