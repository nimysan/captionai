import asyncio
import aiohttp
import subprocess
import io

class TSPlayer:
    def __init__(self, url):
        """Initialize TSPlayer with stream URL"""
        self.url = url
        self._ffmpeg_process = None

    async def get_audio_stream(self):
        """
        Stream audio from TS stream using ffmpeg.
        Converts to PCM format required by Amazon Transcribe:
        - Sample rate: 16000 Hz
        - Channels: Mono
        - Format: 16-bit PCM
        """
        try:
            # Set up ffmpeg command to:
            # 1. Read from TS stream
            # 2. Extract audio
            # 3. Convert to required format for transcription
            command = [
                'ffmpeg',
                '-i', self.url,           # Input from TS stream
                '-vn',                    # Disable video
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

            # Read chunks from ffmpeg output
            chunk_size = 8 * 1024  # 8KB chunks
            while True:
                chunk = await process.stdout.read(chunk_size)
                if not chunk:
                    break
                yield chunk

        except Exception as e:
            print(f"Error in TSPlayer: {str(e)}")
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
