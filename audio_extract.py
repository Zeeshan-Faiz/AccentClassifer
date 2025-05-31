import os
import tempfile
import requests
from urllib.parse import urlparse
from moviepy.editor import VideoFileClip
from pydub import AudioSegment


def download_video(url):
    tmp_dir = tempfile.gettempdir()
    filename = os.path.basename(urlparse(url).path)
    if not filename.endswith(".mp4"):
        filename += ".mp4"
    tmp_path = os.path.join(tmp_dir, filename)

    print(f"[INFO] Downloading video from URL: {url} to {tmp_path}")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(tmp_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return tmp_path


def extract_audio_from_video(video_path, output_audio_path=None):
    """
    Extract audio from a video file and save it as a .wav file in mono and 16kHz format.

    Args:
        video_path (str): Path to the local video file (.mp4).
        output_audio_path (str, optional): Path to save the extracted audio (.wav).
                                           If None, saves with same base name as video.

    Returns:
        str: Path to the processed audio file.
    """
    try:
        # Check if video_path is a URL
        is_temp_file = False
        if video_path.startswith("http://") or video_path.startswith("https://"):
            local_video_path = download_video(video_path)
            is_temp_file = True
        else:
            local_video_path = video_path

        try:
            print(f"[INFO] Loading video from: {local_video_path}")
            video_clip = VideoFileClip(local_video_path)

            if output_audio_path is None:
                base, _ = os.path.splitext(local_video_path)
                output_audio_path = base + ".wav"

            temp_audio_path = output_audio_path.replace(".wav", "_raw.wav")

            print(f"[INFO] Extracting audio to: {temp_audio_path}")
            video_clip.audio.write_audiofile(temp_audio_path, codec='pcm_s16le')
            video_clip.close()

            print(f"[INFO] Converting to mono and 16kHz: {output_audio_path}")
            convert_to_mono_16k(temp_audio_path, output_audio_path)

            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)

            print(f"[SUCCESS] Audio extracted and saved to: {output_audio_path}")
            return output_audio_path

        except Exception as e:
            raise RuntimeError(f"[ERROR] Failed to extract audio: {str(e)}")

        finally:
            # Clean up the temp downloaded file if applicable
            if is_temp_file and os.path.exists(local_video_path):
                os.remove(local_video_path)

    except Exception as e:
        raise RuntimeError(f"[ERROR] Failed to extract audio: {str(e)}")


def convert_to_mono_16k(input_wav_path, output_wav_path):
    """
    Convert WAV audio to mono channel and 16kHz sampling rate.

    Args:
        input_wav_path (str): Path to input WAV file.
        output_wav_path (str): Path to save the converted WAV file.
    """
    audio = AudioSegment.from_wav(input_wav_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(output_wav_path, format="wav")
