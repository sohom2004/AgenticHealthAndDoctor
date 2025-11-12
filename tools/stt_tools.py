import whisper
from config.settings import WHISPER_MODEL


def transcribe(audio_path: str) -> str:
    """
    Transcribes audio file to text using Whisper
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        Transcribed text
    """
    model = whisper.load_model(WHISPER_MODEL)
    result = model.transcribe(audio_path, fp16=False)
    return result['text']