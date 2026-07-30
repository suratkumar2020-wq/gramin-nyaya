try:
    import pyaudio
except ImportError:
    pyaudio = None
import wave
import math
import struct
import os
from faster_whisper import WhisperModel

_stt_model = None

def get_stt_model():
    global _stt_model
    if _stt_model is None:
        print("Loading Voice Model (Whisper)...")
        _stt_model = WhisperModel("base", device="cpu", compute_type="int8")
    return _stt_model 

def get_rms(data):
    count = len(data) // 2
    if count == 0:
        return 0
    format = "%dh" % (count)
    shorts = struct.unpack(format, data)
    sum_squares = sum([sample * sample for sample in shorts])
    return math.sqrt(sum_squares / count)

def record_and_transcribe():
    if pyaudio is None:
        print("\n[त्रुटि] PyAudio is not installed. Terminal voice recording is unavailable.")
        print("Please type your question instead or use the Web UI.")
        return ""

    CHUNK, FORMAT, CHANNELS, RATE = 1024, pyaudio.paInt16, 1, 16000
    WAVE_OUTPUT_FILENAME = "user_voice.wav"
    SILENCE_THRESHOLD = 150  # Lowered from 300 to better capture soft voices
    SILENCE_DURATION = 2.0   # Seconds of silence before stopping

    # Graceful handling for missing microphones or permission issues
    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    except Exception as e:
        print(f"\n[त्रुटि] माइक्रोफोन से जुड़ने में समस्या: {e}")
        print("कृपया सुनिश्चित करें कि माइक कनेक्टेड है। (Please ensure a microphone is connected.)")
        return ""

    print("\n🎤 बोलिए (Speak now)...")
    
    frames = []
    silent_chunks = 0
    max_silent_chunks = int(RATE / CHUNK * SILENCE_DURATION)
    has_spoken = False

    while True:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
            
            rms = get_rms(data)
            if rms > SILENCE_THRESHOLD:
                has_spoken = True
                silent_chunks = 0
            elif has_spoken:
                silent_chunks += 1
                
            if has_spoken and silent_chunks > max_silent_chunks:
                break
            
            # Hard limit just in case to prevent infinite loops (30 secs)
            if len(frames) > int(RATE / CHUNK * 30):
                break
        except Exception as e:
            print(f"Recording error: {e}")
            break

    print("🛑 रिकॉर्डिंग बंद।")
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save to WAV
    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    try:
        print("⏳ आवाज़ को समझा जा रहा है (Transcribing)...")
        # Transcribe with VAD filtering and anti-hallucination settings. 
        # (initial_prompt was removed because Whisper was echoing it instead of transcribing voice).
        segments, _ = get_stt_model().transcribe(
            WAVE_OUTPUT_FILENAME, 
            language="hi", 
            beam_size=5,
            vad_filter=True,
            condition_on_previous_text=False
        )
        
        transcription = "".join([segment.text for segment in segments]).strip()
        return transcription

    except Exception as e:
        print(f"\n[त्रुटि] Transcription Error: {e}")
        return ""
        
    finally:
        # File Cleanup: Delete the audio file so it doesn't clutter the disk
        if os.path.exists(WAVE_OUTPUT_FILENAME):
            os.remove(WAVE_OUTPUT_FILENAME)

def transcribe_audio_file(file_path):
    try:
        print(f"⏳ आवाज़ को समझा जा रहा है (Transcribing file: {file_path})...")
        segments, _ = get_stt_model().transcribe(
            file_path, 
            language="hi", 
            beam_size=5,
            vad_filter=True,
            condition_on_previous_text=False
        )
        
        transcription = "".join([segment.text for segment in segments]).strip()
        return transcription

    except Exception as e:
        print(f"\n[त्रुटि] Transcription Error: {e}")
        return ""