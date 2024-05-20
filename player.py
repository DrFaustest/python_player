import os
from pydub import AudioSegment
import pygame
import io
import time

# Set ffmpeg path
ffmpeg_path = os.path.join(os.environ['VIRTUAL_ENV'], 'Scripts' if os.name == 'nt' else 'bin', 'ffmpeg', 'bin')
AudioSegment.converter = os.path.join(ffmpeg_path, 'ffmpeg.exe' if os.name == 'nt' else 'ffmpeg')
AudioSegment.ffprobe = os.path.join(ffmpeg_path, 'ffprobe.exe' if os.name == 'nt' else 'ffprobe')

# Initialize Pygame mixer
pygame.mixer.init()

def load_audio_segment(file_path):
    """Loads the audio segment from the provided WAV file."""
    return AudioSegment.from_wav(file_path)

def get_segment(audio, start_ms, end_ms):
    """Extracts a segment from the audio from start_ms to end_ms."""
    return audio[start_ms:end_ms]

def play_segment(segment):
    """Plays the given audio segment."""
    mp3_io = io.BytesIO()
    segment.export(mp3_io, format="mp3")
    mp3_io.seek(0)
    pygame.mixer.music.load(mp3_io)
    pygame.mixer.music.play()

def fast_forward(audio, current_position, step_ms):
    """Fast forwards the audio by step_ms milliseconds."""
    new_position = current_position + step_ms
    if new_position >= len(audio):
        new_position = len(audio) - 1  # Ensure the position does not exceed the audio length
    return new_position

def rewind(audio, current_position, step_ms):
    """Rewinds the audio by step_ms milliseconds."""
    new_position = current_position - step_ms
    if new_position < 0:
        new_position = 0  # Ensure the position does not go below 0
    return new_position

# Load the whole song
song_file = "music\\test1.wav"
audio = load_audio_segment(song_file)
song_length = len(audio)

# Initial position
current_position = 0
step_ms = 5000  # 5000 milliseconds = 5 seconds

# Example usage to play initial segment
end_position = current_position + step_ms
segment = get_segment(audio, current_position, end_position)
play_segment(segment)

# Function to handle user inputs (simulate fast forward and rewind)
def handle_user_input(input_action):
    global current_position
    if input_action == 'fast_forward':
        current_position = fast_forward(audio, current_position, step_ms)
    elif input_action == 'rewind':
        current_position = rewind(audio, current_position, step_ms)
    elif input_action == 'pause':
        pygame.mixer.music.pause()
        return
    elif input_action == 'resume':
        pygame.mixer.music.unpause()
        return

    end_position = current_position + step_ms
    segment = get_segment(audio, current_position, end_position)
    play_segment(segment)

# Simulate user inputs for testing
def main():
    global current_position

    print("Press 'f' to fast forward, 'r' to rewind, 'p' to pause, 'u' to resume, 'q' to quit.")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_f]:
            handle_user_input('fast_forward')
            time.sleep(0.5)  # Delay to prevent rapid input processing
        elif keys[pygame.K_r]:
            handle_user_input('rewind')
            time.sleep(0.5)  # Delay to prevent rapid input processing
        elif keys[pygame.K_p]:
            handle_user_input('pause')
            time.sleep(0.5)  # Delay to prevent rapid input processing
        elif keys[pygame.K_u]:
            handle_user_input('resume')
            time.sleep(0.5)  # Delay to prevent rapid input processing
        elif keys[pygame.K_q]:
            running = False

    pygame.quit()

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_mode((640, 480))  # Necessary to capture keyboard input
    main()
