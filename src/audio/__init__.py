"""
Windows-Native Audio Module
Pure Python audio I/O using sounddevice
"""
from .capture import AudioCapture
from .playback import AudioPlayback
from .vad import VoiceActivityDetector

__all__ = ['AudioCapture', 'AudioPlayback', 'VoiceActivityDetector']