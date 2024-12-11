import asyncio
import platform

class MicrophoneInput:
    def __init__(self):
        """Initialize microphone input handler"""
        self._ffmpeg_process = None
        self._setup_device_name()

    def _setup_device_name(self):
        """Set up the audio input device name based on OS"""
        system = platform.system()
        if system == 'Darwin':  # macOS
            self.input_device = ':0'  # Default audio input device on macOS
        elif system == 'Windows':
            self.input_device = 'audio=@device_cm_{33D9A762-90C8-11D0-BD43-00A0C911CE86}'  # Default audio input
        else:  # Linux and others
            self.input_device = 'default'

    async def get_audio_stream(self):
        """
        Stream audio from microphone using ffmpeg.
        Returns audio in format required by Amazon Transcribe:
        - Sample rate: 16000 Hz
        - Channels: Mono
        - Format: 16-bit PCM
        """
        try:
            # Set up ffmpeg command for microphone capture
            command = [
                'ffmpeg',
                '-f', 'avfoundation' if platform.system() == 'Darwin' else 'dshow',  # Input format
                '-i', self.input_device,  # Input device
                '-acodec', 'pcm_s16le',   # Convert to 16-bit PCM
                '-ar', '16000',           # Set sample rate to 16000 Hz
                '-ac', '1',               # Convert to mono
                '-f', 's16le',           # Output format
                'pipe:1'                  # Output to pipe
            ]

            # Start ffmpeg process
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            self._ffmpeg_process = process

            print("Started microphone capture. Speaking into microphone...")

            # Read chunks from ffmpeg output
            chunk_size = 8 * 1024  # 8KB chunks
            while True:
                chunk = await process.stdout.read(chunk_size)
                if not chunk:
                    break
                yield chunk

        except Exception as e:
            print(f"Error in MicrophoneInput: {str(e)}")
            raise
        finally:
            if self._ffmpeg_process:
                self._ffmpeg_process.terminate()
                await self._ffmpeg_process.wait()

    async def close(self):
        """Clean up resources"""
        if self._ffmpeg_process:
            self._ffmpeg_process.terminate()
            await self._ffmpeg_process.wait()
