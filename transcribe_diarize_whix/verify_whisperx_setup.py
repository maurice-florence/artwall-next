import os
import subprocess
import sys
import importlib.util
from huggingface_hub import login, HfApi

def check_python_version():
    print(f"Python version: {sys.version}")
    if sys.version_info < (3, 8):
        print("Warning: Python 3.8 or higher is recommended for WhisperX.")

def check_module_installed(module_name):
    if importlib.util.find_spec(module_name) is not None:
        print(f"Module '{module_name}' is installed.")
        return True
    else:
        print(f"Module '{module_name}' is NOT installed.")
        return False

def check_pytorch():
    try:
        import torch
        print(f"PyTorch version: {torch.__version__}")
        if torch.cuda.is_available():
            print("CUDA is available. GPU device count:", torch.cuda.device_count())
            print("CUDA version:", torch.version.cuda)
            print("cuDNN version:", torch.backends.cudnn.version())
        else:
            print("CUDA is not available. PyTorch is running on CPU.")
    except ImportError:
        print("PyTorch is not installed.")

def check_cuda_installation():
    cuda_path = os.environ.get('CUDA_PATH')
    if cuda_path and os.path.isdir(cuda_path):
        print(f"CUDA installation found at: {cuda_path}")
        nvcc_path = os.path.join(cuda_path, 'bin', 'nvcc')
        if os.path.isfile(nvcc_path):
            try:
                result = subprocess.run([nvcc_path, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if result.returncode == 0:
                    print("CUDA nvcc version:")
                    print(result.stdout)
                else:
                    print("Unable to execute nvcc.")
            except Exception as e:
                print(f"Error running nvcc: {e}")
        else:
            print("nvcc not found in CUDA installation.")
    else:
        print("CUDA is not installed or 'CUDA_PATH' environment variable is not set correctly.")

def check_cudnn_installation():
    try:
        import torch
        if torch.cuda.is_available():
            print("cuDNN version:", torch.backends.cudnn.version())
        else:
            print("CUDA is not available; skipping cuDNN check.")
    except ImportError:
        print("PyTorch is not installed; skipping cuDNN check.")

def check_whisperx():
    if check_module_installed('whisperx'):
        try:
            import whisperx
            print(f"WhisperX version: {whisperx.__version__}")
        except AttributeError:
            print("WhisperX version information is not available.")
    else:
        print("WhisperX is not installed.")

def check_huggingface_token_and_model():
    token = os.environ.get('HF_TOKEN')
    if token:
        print("Hugging Face token is set.")
        try:
            # Log in using the token
            login(token=token)
            print("Successfully authenticated with Hugging Face.")
            
            # Attempt to access a model to verify terms acceptance
            api = HfApi()
            model_id = "pyannote/speaker-diarization-3.1"  # Example model that may require terms acceptance
            api.model_info(model_id)
            print(f"Access to model '{model_id}' is verified.")
        except Exception as e:  # Generic exception handling
            print(f"Error accessing model '{model_id}': {e}")
            print("Please ensure you have accepted the model's terms on the Hugging Face Hub.")
    else:
        print("Hugging Face token is NOT set. Please set the 'HF_TOKEN' environment variable.")



def main():
    print("Checking Python environment...")
    check_python_version()

    print("\nChecking PyTorch installation...")
    check_pytorch()

    print("\nChecking CUDA installation...")
    check_cuda_installation()

    print("\nChecking cuDNN installation...")
    check_cudnn_installation()

    print("\nChecking WhisperX installation...")
    check_whisperx()

    print("\nChecking Hugging Face token and model access...")
    check_huggingface_token_and_model()

if __name__ == "__main__":
    main()
