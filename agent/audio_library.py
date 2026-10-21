import os
import wave
import math
import random
import uuid
import subprocess
from pathlib import Path
import numpy as np
import imageio_ffmpeg
from .config import BASE_DIR, OUTPUT_DIR

AUDIO_DIR = BASE_DIR / "agent" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Top 10 Iconic Motivational & Mindset Music Tracks from the Instagram Library
INSTAGRAM_MOTIVATIONAL_TRACKS = [
    {
        "id": "experience",
        "title": "Experience",
        "artist": "Ludovico Einaudi",
        "audio_name": "Ludovico Einaudi • Experience",
        "genre": "Neoclassical / Emotional Piano",
        "vibe": "Transcendent emotional climax & awakening",
        "chords": [("F#", 3), ("D", 3), ("A", 2), ("C#", 3)],
        "tempo_scale": 1.25,
        "style": "arpeggio",
        "base_octave": 4
    },
    {
        "id": "cornfield_chase",
        "title": "Cornfield Chase",
        "artist": "Hans Zimmer",
        "audio_name": "Hans Zimmer • Cornfield Chase",
        "genre": "Cinematic Orchestral / Interstellar",
        "vibe": "Cosmic wonder, urgency & destiny",
        "chords": [("A", 2), ("F", 2), ("C", 3), ("G", 2)],
        "tempo_scale": 1.6,
        "style": "pulsing_ostinato",
        "base_octave": 4
    },
    {
        "id": "solitude",
        "title": "Solitude (Freats Slowed)",
        "artist": "M83",
        "audio_name": "M83 • Solitude (Freats Slowed)",
        "genre": "Slowed Atmospheric / Mindset",
        "vibe": "Unshakeable stoic presence & focus",
        "chords": [("C", 2), ("Ab", 1), ("F", 1), ("G", 1)],
        "tempo_scale": 0.75,
        "style": "deep_drone",
        "base_octave": 3
    },
    {
        "id": "reflections",
        "title": "Reflections",
        "artist": "Toshifumi Hinata",
        "audio_name": "Toshifumi Hinata • Reflections",
        "genre": "Introspective Piano & Strings",
        "vibe": "Deep nostalgic self-inquiry & truth",
        "chords": [("E", 2), ("C", 2), ("G", 2), ("D", 2)],
        "tempo_scale": 1.0,
        "style": "lyrical_piano",
        "base_octave": 4
    },
    {
        "id": "time",
        "title": "Time",
        "artist": "Hans Zimmer",
        "audio_name": "Hans Zimmer • Time",
        "genre": "Cinematic Orchestral / Inception",
        "vibe": "Relentless growth & undeniable triumph",
        "chords": [("D", 2), ("Bb", 1), ("F", 2), ("A", 1)],
        "tempo_scale": 0.85,
        "style": "orchestral_swell",
        "base_octave": 3
    },
    {
        "id": "snowfall",
        "title": "Snowfall",
        "artist": "Øneheart x reidenshi",
        "audio_name": "Øneheart x reidenshi • Snowfall",
        "genre": "Atmospheric Ambient / Lo-Fi",
        "vibe": "Pure stillness, clarity & manifestation",
        "chords": [("B", 2), ("G", 2), ("D", 2), ("A", 2)],
        "tempo_scale": 0.9,
        "style": "felt_ambient",
        "base_octave": 4
    },
    {
        "id": "idea22",
        "title": "Idea 22",
        "artist": "Gibran Alcocer",
        "audio_name": "Gibran Alcocer • Idea 22",
        "genre": "Virtuosic Piano / Viral Reel",
        "vibe": "Soulful longing, grace & realization",
        "chords": [("G", 2), ("Eb", 2), ("Bb", 2), ("F", 2)],
        "tempo_scale": 1.2,
        "style": "waltz_arpeggio",
        "base_octave": 4
    },
    {
        "id": "past_lives",
        "title": "Past Lives (Slowed)",
        "artist": "BØRNS",
        "audio_name": "BØRNS • Past Lives (Slowed)",
        "genre": "Dreamwave / Manifestation",
        "vibe": "Soul connections & quantum reality shift",
        "chords": [("A", 2), ("F#", 2), ("D", 2), ("E", 2)],
        "tempo_scale": 0.95,
        "style": "dreamwave_pad",
        "base_octave": 4
    },
    {
        "id": "the_long_dark",
        "title": "The Long Dark",
        "artist": "Scott Buckley",
        "audio_name": "Scott Buckley • The Long Dark",
        "genre": "Cinematic Resilient Piano",
        "vibe": "Rising through darkness into light",
        "chords": [("C#", 2), ("A", 1), ("E", 2), ("B", 1)],
        "tempo_scale": 1.0,
        "style": "cinematic_piano",
        "base_octave": 4
    },
    {
        "id": "a_new_man",
        "title": "A New Man (Slowed & Reverb)",
        "artist": "Aloboi",
        "audio_name": "Aloboi • A New Man (Slowed)",
        "genre": "Epic Awakening Electronic / Cinematic",
        "vibe": "Complete identity reinvention & power",
        "chords": [("F", 2), ("Db", 2), ("Ab", 1), ("Eb", 2)],
        "tempo_scale": 1.1,
        "style": "synth_awakening",
        "base_octave": 3
    }
]

NOTE_SEMITONES = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
    "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
}

def note_to_freq(note_str: str, octave: int) -> float:
    """Calculates frequency in Hz for standard equal temperament A4=440Hz."""
    semi = NOTE_SEMITONES.get(note_str, 0)
    midi = 12 + octave * 12 + semi
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))

def synthesize_musical_track(track_info: dict, duration_sec: int = 7) -> str:
    """
    Synthesizes a lush, rich melodic musical soundscape matching the exact
    harmonic key, tempo, and style of the selected Instagram track.
    Saves and caches the generated MP3 in agent/audio/<id>.mp3.
    """
    track_id = track_info["id"]
    cached_mp3 = AUDIO_DIR / f"{track_id}.mp3"
    
    # If a custom MP3 is already placed in agent/audio/<id>.mp3, use it!
    if cached_mp3.exists() and cached_mp3.stat().st_size > 10000:
        return str(cached_mp3)

    sample_rate = 44100
    n_samples = int(sample_rate * duration_sec)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False)
    
    stereo_left = np.zeros(n_samples, dtype=np.float32)
    stereo_right = np.zeros(n_samples, dtype=np.float32)
    
    chords = track_info.get("chords", [("A", 2), ("F", 2), ("C", 3), ("G", 2)])
    chord_len = duration_sec / len(chords)
    
    style = track_info.get("style", "arpeggio")
    base_oct = track_info.get("base_octave", 4)
    
    for c_idx, (root_note, root_oct) in enumerate(chords):
        c_start = int(c_idx * chord_len * sample_rate)
        c_end = int((c_idx + 1) * chord_len * sample_rate)
        seg_t = t[c_start:c_end] - (c_idx * chord_len)
        seg_len = len(seg_t)
        if seg_len <= 0:
            continue
            
        f_root = note_to_freq(root_note, root_oct)
        f_fifth = f_root * 1.5
        f_third = f_root * (1.2 if "m" in track_info.get("genre", "").lower() or c_idx % 2 == 0 else 1.25)
        f_high_root = note_to_freq(root_note, base_oct)
        f_high_fifth = f_high_root * 1.5
        f_high_octave = f_high_root * 2.0
        
        # 1. Warm Sub-Bass drone with smooth envelope
        env_sub = np.sin(np.pi * (seg_t / chord_len)) ** 0.5
        sub_wave = 0.35 * np.sin(2 * np.pi * f_root * seg_t) * env_sub
        stereo_left[c_start:c_end] += sub_wave
        stereo_right[c_start:c_end] += sub_wave
        
        # 2. Lush warm string pad / fifth harmony (with gentle stereo chorus detune)
        pad_detune_l = 0.22 * np.sin(2 * np.pi * (f_fifth * 1.002) * seg_t)
        pad_detune_r = 0.22 * np.sin(2 * np.pi * (f_fifth * 0.998) * seg_t)
        pad_third = 0.16 * np.sin(2 * np.pi * f_third * seg_t)
        stereo_left[c_start:c_end] += (pad_detune_l + pad_third) * env_sub
        stereo_right[c_start:c_end] += (pad_detune_r + pad_third) * env_sub
        
        # 3. High Melodic Element depending on style
        if style in ["arpeggio", "waltz_arpeggio", "pulsing_ostinato"]:
            # Rapid 4-note melodic arpeggio cycling through high chord tones
            arp_freqs = [f_high_root, f_high_root * 1.2, f_high_fifth, f_high_octave]
            sub_step = chord_len / 4.0
            for step_i, note_f in enumerate(arp_freqs):
                n_start = int(step_i * sub_step * sample_rate)
                n_end = int((step_i + 1) * sub_step * sample_rate)
                n_len = n_end - n_start
                if n_len > 0 and (c_start + n_end) <= n_samples:
                    n_t = np.linspace(0, sub_step, n_len, endpoint=False)
                    # Piano-like exponential decay envelope
                    note_env = np.exp(-4.5 * (n_t / sub_step))
                    piano_tone = (
                        0.28 * np.sin(2 * np.pi * note_f * n_t) +
                        0.12 * np.sin(2 * np.pi * (note_f * 2) * n_t) +
                        0.05 * np.sin(2 * np.pi * (note_f * 3) * n_t)
                    ) * note_env
                    # Gentle stereo panning alternating per note
                    pan_l = 0.6 if step_i % 2 == 0 else 0.4
                    pan_r = 0.4 if step_i % 2 == 0 else 0.6
                    stereo_left[c_start + n_start : c_start + n_end] += piano_tone * pan_l
                    stereo_right[c_start + n_start : c_start + n_end] += piano_tone * pan_r
        else:
            # Slow expressive singing piano / cinematic lead melody
            lead_t = seg_t
            lead_env = np.sin(np.pi * (lead_t / chord_len)) ** 1.2
            lead_tone = (
                0.24 * np.sin(2 * np.pi * f_high_root * lead_t) +
                0.15 * np.sin(2 * np.pi * f_high_fifth * lead_t) +
                0.06 * np.sin(2 * np.pi * (f_high_root * 2) * lead_t)
            ) * lead_env
            stereo_left[c_start:c_end] += lead_tone * 0.5
            stereo_right[c_start:c_end] += lead_tone * 0.5

    # Master Fade In & Fade Out (1.0s in, 1.5s out) for clean seamless looping
    fade_in_len = int(1.0 * sample_rate)
    fade_out_len = int(1.5 * sample_rate)
    fade_in = np.linspace(0.0, 1.0, fade_in_len)
    fade_out = np.linspace(1.0, 0.0, fade_out_len)
    
    stereo_left[:fade_in_len] *= fade_in
    stereo_right[:fade_in_len] *= fade_in
    stereo_left[-fade_out_len:] *= fade_out
    stereo_right[-fade_out_len:] *= fade_out

    # Soft limiter / Normalization to -1 dB
    max_amp = max(np.max(np.abs(stereo_left)), np.max(np.abs(stereo_right)), 1e-6)
    target_amp = 0.88
    stereo_left = (stereo_left / max_amp) * target_amp
    stereo_right = (stereo_right / max_amp) * target_amp

    # Interleave to 16-bit PCM WAV
    int_l = (stereo_left * 32767).astype(np.int16)
    int_r = (stereo_right * 32767).astype(np.int16)
    interleaved = np.empty((n_samples * 2,), dtype=np.int16)
    interleaved[0::2] = int_l
    interleaved[1::2] = int_r
    
    temp_wav = AUDIO_DIR / f"temp_{uuid.uuid4().hex[:6]}.wav"
    with wave.open(str(temp_wav), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(interleaved.tobytes())
        
    # Convert WAV to high-fidelity MP3 with FFmpeg
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    mp3_cmd = [
        ffmpeg, "-y",
        "-i", str(temp_wav),
        "-codec:a", "libmp3lame",
        "-b:a", "192k",
        str(cached_mp3)
    ]
    subprocess.run(mp3_cmd, capture_output=True, text=True)
    
    try:
        temp_wav.unlink(missing_ok=True)
    except Exception:
        pass

    return str(cached_mp3)

def get_random_instagram_track(duration_sec: int = 7) -> tuple:
    """
    Picks a random motivational music track from the top 10 Instagram library
    and ensures its audio file is synthesized/ready.
    Returns: (audio_file_path, track_info)
    """
    track = random.choice(INSTAGRAM_MOTIVATIONAL_TRACKS)
    audio_path = synthesize_musical_track(track, duration_sec=duration_sec)
    return audio_path, track

def get_track_by_id(track_id: str, duration_sec: int = 7) -> tuple:
    """Retrieves a specific track by its ID."""
    for t in INSTAGRAM_MOTIVATIONAL_TRACKS:
        if t["id"] == track_id:
            audio_path = synthesize_musical_track(t, duration_sec=duration_sec)
            return audio_path, t
    return get_random_instagram_track(duration_sec=duration_sec)

def preload_all_tracks():
    """Generates and pre-renders all 10 tracks so they are instantly cached on disk."""
    for track in INSTAGRAM_MOTIVATIONAL_TRACKS:
        synthesize_musical_track(track, duration_sec=7)
