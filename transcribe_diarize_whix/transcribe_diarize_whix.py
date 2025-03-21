import os
import sys
import whisperx
import torch
import logging
import time
from pyannote.audio import Pipeline

# To activate the environment:
## Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
## .\whisperx-env\Scripts\Activate 

# To run the script:
## .\whisperx-env\Scripts\python.exe c:\Users\friem\OneDrive\Documenten\GitHub\whisper\whisper_x.py

# Enable TensorFloat-32 for matmul and cuDNN (if applicable)
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

# Configuration parameters
config = {
    "huggingface_api_token": "hf_lQeFqRFEzYlTMzPasRbxImhmegQceWaeVOoken",
    "task": "transcribe",
    "model_size": "small",
    "path": "G:/Mijn Drive/Audio/output_mp3",
    "diarize": False,
    "num_speakers": 4,  # Optional: number of speakers for diarization
    "speaker_names": ["Speaker 1", "Speaker 2", "Speaker 3", "Speaker 4"]  # Optional: list of speaker names
}

def check_virtual_environment(expected_env_name):
    """
    Check if the script is running inside the expected virtual environment.
    """
    # Method 1: Check VIRTUAL_ENV environment variable
    venv_path = os.environ.get('VIRTUAL_ENV')
    if venv_path and os.path.basename(venv_path) == expected_env_name:
        return True

    # Method 2: Compare sys.prefix with sys.base_prefix
    if hasattr(sys, 'base_prefix'):
        if sys.prefix != sys.base_prefix and expected_env_name in sys.prefix:
            return True

    return False

# Usage
if not check_virtual_environment('whisperx-env'):
    print("Error: This script must be run within the 'whisperx-env' virtual environment.")
    sys.exit(1)

# Set environment variable for Hugging Face API token
os.environ["HF_TOKEN"] = config["huggingface_api_token"]

def get_device():
    """
    Determine the appropriate device (GPU or CPU) for model inference.
    """
    if torch.cuda.is_available():
        return torch.device("cuda")
    else:
        logging.warning("No GPU detected. Using CPU.")
        return torch.device("cpu")

def load_whisperx_model(model_size, device):
    """
    Load the WhisperX model on the specified device.
    """
    logging.info(f"Loading WhisperX model '{model_size}' on {device} ...")
    model = whisperx.load_model(model_size, device, compute_type="float32")
    logging.info(f"Model '{model_size}' loaded successfully on {device}!")
    return model

def transcribe_and_diarize(model, audio_file, device, diarize, speaker_names=None):
    """
    Transcribe and optionally diarize the given audio file.
    """
    logging.info(f"Processing audio file: {audio_file} ...")
    audio = whisperx.load_audio(audio_file)
    result = model.transcribe(audio)

    if diarize:
        logging.info("Performing alignment and diarization...")
        model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
        result = whisperx.align(result["segments"], model_a, metadata, audio, device)

        try:
            logging.info("Loading diarization pipeline...")
            diarize_model = Pipeline.from_pretrained(
                "pyannote/speaker-diarization",
                use_auth_token=config["huggingface_api_token"]
            ).to(device)
            logging.info("Diarization pipeline loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading diarization pipeline: {e}", exc_info=True)
            raise

        try:
            logging.info("Running diarization...")
            diarize_segments = diarize_model(audio_file)
            logging.info("Diarization completed successfully.")
        except Exception as e:
            logging.error(f"Error during diarization: {e}", exc_info=True)
            raise

        result = whisperx.assign_word_speakers(diarize_segments, result)

        if speaker_names:
            for segment in result["segments"]:
                speaker_id = int(segment["speaker"].split('_')[-1])
                if speaker_id < len(speaker_names):
                    segment["speaker"] = speaker_names[speaker_id]

    return result

def save_transcription(output_path, transcription, max_lines=10):
    """
    Save the first 'max_lines' lines of the transcription to a text file.
    """
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(transcription["segments"]):
                if i >= max_lines:
                    break
                speaker = segment.get("speaker", "Speaker")
                text = segment["text"]
                f.write(f"[{speaker}] {text}\n")
        logging.info(f"Saved first {max_lines} lines of transcription to: {output_path}")
    except Exception as e:
        logging.error(f"Error saving file: {e}")

def process_audio_files(path, model, device, diarize, speaker_names=None):
    if os.path.isdir(path):
        audio_files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(('.mp3', '.wav', '.ogg'))]
        if not audio_files:
            logging.error(f"No audio files found in folder: {path}")
            return
        for audio_file in audio_files:
            try:
                result = transcribe_and_diarize(model, audio_file, device, diarize, speaker_names)
                base_name = os.path.splitext(os.path.basename(audio_file))[0]
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                output_file = f"{base_name}_whisperx_{config['model_size']}_{timestamp}.txt"
                save_transcription(os.path.join(os.path.dirname(audio_file), output_file), result)
            except Exception as e:
                logging.error(f"Error processing file {audio_file}: {e}", exc_info=True)
                continue  # Continue with the next file
    elif os.path.isfile(path):
        result = transcribe_and_diarize(model, path, device, diarize, speaker_names)
        base_name = os.path.splitext(os.path.basename(path))[0]
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = f"{base_name}_whisperx_{config['model_size']}_{timestamp}.txt"
        save_transcription(os.path.join(os.path.dirname(path), output_file), result, max_lines=10)
    else:
        logging.error(f"Invalid path: {path}")

def main():
    try:
        device = get_device()
        model = load_whisperx_model(config["model_size"], device)
        process_audio_files(config["path"], model, device, config["diarize"], config.get("speaker_names"))
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    main()
