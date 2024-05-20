import os
import threading
import time
from pydub import AudioSegment
import pygame
import io

# Set ffmpeg path
ffmpeg_path = os.path.join(os.environ['VIRTUAL_ENV'], 'Scripts' if os.name == 'nt' else 'bin', 'ffmpeg', 'bin')
AudioSegment.converter = os.path.join(ffmpeg_path, 'ffmpeg.exe' if os.name == 'nt' else 'ffmpeg')
AudioSegment.ffprobe = os.path.join(ffmpeg_path, 'ffprobe.exe' if os.name == 'nt' else 'ffprobe')

# Initialize Pygame mixer
pygame.mixer.init()

# Global variables
current_position = 0
step_ms = 5000  # 5000 milliseconds = 5 seconds
audio_length = 0
next_segment_io = None
stop_flag = False

def load_audio_segment(file_path):
    """Loads the audio segment from the provided WAV file."""
    return AudioSegment.from_wav(file_path)

def get_segment(audio, start_ms, end_ms):
    """Extracts a segment from the audio from start_ms to end_ms."""
    return audio[start_ms:end_ms]

def convert_to_mp3(segment):
    """Converts a segment to MP3 and returns it as a BytesIO object."""
    mp3_io = io.BytesIO()
    segment.export(mp3_io, format="mp3")
    mp3_io.seek(0)
    return mp3_io

def play_segment(segment_io):
    """Plays the given audio segment from a BytesIO object."""
    pygame.mixer.music.load(segment_io)
    pygame.mixer.music.play()

def pre_load_next_segment(audio, next_position, step_ms):
    """Pre-loads the next segment in a separate thread."""
    global next_segment_io, stop_flag
    if next_position < audio_length and not stop_flag:
        end_ms = min(next_position + step_ms, audio_length)
        next_segment = get_segment(audio, next_position, end_ms)
        next_segment_io = convert_to_mp3(next_segment)

# Load the whole song
song_file = "music\\test1.wav"
audio = load_audio_segment(song_file)
audio_length = len(audio)

# Load initial segments
current_segment_io = convert_to_mp3(get_segment(audio, current_position, current_position + step_ms))
next_position = current_position + step_ms
thread = threading.Thread(target=pre_load_next_segment, args=(audio, next_position, step_ms))
thread.start()

# Play the initial segment
play_segment(current_segment_io)

def main():
    global current_position, current_segment_io, next_segment_io, stop_flag

    print("Press 'f' to fast forward, 'r' to rewind, 'p' to pause, 'u' to resume, 'q' to quit.")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_f]:
            if next_segment_io:
                current_position += step_ms
                current_segment_io, next_segment_io = next_segment_io, None
                play_segment(current_segment_io)
                next_position = current_position + step_ms
                thread = threading.Thread(target=pre_load_next_segment, args=(audio, next_position, step_ms))
                thread.start()
            pygame.time.wait(500)  # Delay to prevent rapid input processing
        elif keys[pygame.K_r]:
            current_position = max(current_position - step_ms, 0)
            current_segment_io = convert_to_mp3(get_segment(audio, current_position, current_position + step_ms))
            play_segment(current_segment_io)
            next_position = current_position + step_ms
            thread = threading.Thread(target=pre_load_next_segment, args=(audio, next_position, step_ms))
            thread.start()
            pygame.time.wait(500)  # Delay to prevent rapid input processing
        elif keys[pygame.K_p]:
            pygame.mixer.music.pause()
            pygame.time.wait(500)  # Delay to prevent rapid input processing
        elif keys[pygame.K_u]:
            pygame.mixer.music.unpause()
            pygame.time.wait(500)  # Delay to prevent rapid input processing
        elif keys[pygame.K_q]:
            running = False
            stop_flag = True

        # Check if the current segment is about to end, and pre-load the next segment
        if not pygame.mixer.music.get_busy() and running:
            if next_segment_io:
                play_segment(next_segment_io)
                current_position += step_ms
                current_segment_io, next_segment_io = next_segment_io, None
                next_position = current_position + step_ms
                thread = threading.Thread(target=pre_load_next_segment, args=(audio, next_position, step_ms))
                thread.start()

    pygame.quit()

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_mode((640, 480))  # Necessary to capture keyboard input
    main()
