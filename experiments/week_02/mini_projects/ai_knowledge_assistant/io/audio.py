"""
Audio helpers: Whisper STT + TTS wrappers.

Provides speech-to-text (Whisper) and text-to-speech (OpenAI TTS) functionality.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional

import numpy as np
from openai import OpenAI

# Initialize OpenAI client for audio APIs
_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    """Get or create OpenAI client for audio APIs."""
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def transcribe(audio_input) -> str:
    """
    Transcribe audio to text using OpenAI Whisper.
    
    Handles both filepath strings and numpy tuple (sample_rate, audio_data) from Gradio.
    
    Args:
        audio_input: Either a filepath string or tuple (sample_rate, audio_data)
    
    Returns:
        Transcribed text, or error message if transcription fails
    """
    if audio_input is None:
        return "No audio file provided."
    
    client = _get_client()
    
    try:
        # Handle tuple (sample_rate, audio_data) from Gradio
        if isinstance(audio_input, tuple):
            import wave
            
            sample_rate, audio_data = audio_input
            
            # Validate sample rate
            if sample_rate is None or sample_rate < 8000:
                return f"Error: Invalid sample rate ({sample_rate}). Please try again."
            
            # Validate audio data
            if audio_data is None:
                return "Error: No audio data received. Please record again."
            
            audio_data = np.array(audio_data, dtype=np.float32)
            
            if len(audio_data) == 0:
                return "Error: Empty audio data. Please record again."
            
            # Check audio duration (should be at least 0.5 seconds)
            duration = len(audio_data) / sample_rate
            if duration < 0.5:
                return f"Error: Audio too short ({duration:.2f}s). Please record at least 1 second."
            
            # Resample if needed (Whisper works best with 16kHz, but accepts 8-48kHz)
            if sample_rate < 8000 or sample_rate > 48000:
                try:
                    from scipy import signal
                    target_rate = 16000
                    num_samples = int(len(audio_data) * target_rate / sample_rate)
                    audio_data = signal.resample(audio_data, num_samples)
                    sample_rate = target_rate
                except ImportError:
                    pass
            
            # Convert to 1D array if needed
            if len(audio_data.shape) > 1:
                audio_data = audio_data.flatten()
            
            # Check if audio is mostly silence
            max_amplitude = np.abs(audio_data).max()
            if max_amplitude < 0.01:
                return "Error: Audio appears to be silence. Please speak louder or check your microphone."
            
            # Normalize to [-1, 1] range if needed, then convert to int16
            if audio_data.dtype == np.float32 or audio_data.dtype == np.float64:
                audio_data = np.clip(audio_data, -1.0, 1.0)
                audio_data = (audio_data * 32767).astype(np.int16)
            elif audio_data.dtype != np.int16:
                if audio_data.dtype in [np.int32, np.int64]:
                    max_val = np.abs(audio_data).max()
                    if max_val > 32767:
                        audio_data = (audio_data / (max_val / 32767)).astype(np.int16)
                    else:
                        audio_data = audio_data.astype(np.int16)
                else:
                    audio_data = audio_data.astype(np.int16)
            
            # Save to temp WAV file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                with wave.open(tmp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(int(sample_rate))
                    wav_file.writeframes(audio_data.tobytes())
                audio_path = tmp_file.name
        else:
            # It's a filepath string
            audio_path = audio_input
            if not os.path.exists(audio_path):
                return "Error: Audio file not found. Please record again."
            if os.path.getsize(audio_path) == 0:
                return "Error: Audio file is empty. Please record again."
        
        # Transcribe with Whisper
        with open(audio_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="en"
            )
        
        result = transcript.text.strip()
        
        # Clean up temp file if we created one
        if isinstance(audio_input, tuple) and os.path.exists(audio_path):
            try:
                os.unlink(audio_path)
            except Exception:
                pass
        
        # Validate transcription result
        if not result or len(result) < 2:
            return "Error: Transcription returned empty or too short. Please try recording again with clearer audio."
        
        return result
        
    except Exception as e:
        return f"Error transcribing: {str(e)}"


def speak(text: str, voice: str = "nova", output_dir: Optional[str] = None) -> Optional[str]:
    """
    Convert text to speech using OpenAI TTS.
    
    Args:
        text: Text to convert to speech
        voice: Voice to use ("alloy", "echo", "fable", "onyx", "nova", "shimmer")
        output_dir: Directory to save audio file (defaults to data/audio/)
    
    Returns:
        Path to generated audio file, or None on error
    """
    if not text:
        return None
    
    client = _get_client()
    
    try:
        # Truncate to avoid TTS timeouts and costs
        if len(text) > 1000:
            text = text[:1000] + "... (truncated)"
        
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        # Determine output directory
        if output_dir is None:
            base_dir = Path(__file__).parent.parent / "data" / "audio"
            base_dir.mkdir(parents=True, exist_ok=True)
            output_dir = str(base_dir)
        else:
            os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        audio_path = os.path.join(output_dir, f"tts_{text_hash}.mp3")
        
        response.stream_to_file(audio_path)
        return audio_path
        
    except Exception as e:
        print(f"TTS Error: {str(e)}")
        return None
