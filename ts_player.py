import asyncio
import aiohttp
import subprocess
import io
from audio_processor import AudioProcessor

class TSPlayer:
    def __init__(self, url):
        """Initialize TSPlayer with stream URL"""
        self.url = url
        self._ffmpeg_process = None
        self.audio_processor = AudioProcessor()
        self._running = False
        self.chunk_size = 4 * 1024  # 4KB chunks to match other components

    async def get_audio_stream(self):
        """
        Stream audio from TS stream using ffmpeg.
        Converts to PCM format required by Amazon Transcribe:
        - Sample rate: 16000 Hz
        - Channels: Mono
        - Format: 16-bit PCM
        """
        try:
            self._running = True
            # Set up ffmpeg command with optimized parameters for streaming
            command = [
                'ffmpeg',
                '-i', self.url,           # Input from TS stream
                '-vn',                    # Disable video
                '-acodec', 'pcm_s16le',   # Convert to 16-bit PCM
                '-ar', '16000',           # Set sample rate to 16000 Hz
                '-ac', '1',               # Convert to mono
                '-f', 's16le',           # Output format
                '-bufsize', '4k',         # Match chunk size
                '-probesize', '32k',      # Smaller probe size for faster start
                '-analyzeduration', '0',  # Minimize analysis time
                '-thread_queue_size', '4096',  # Prevent buffer issues
                'pipe:1'                  # Output to pipe
            ]

            # Start ffmpeg process
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            self._ffmpeg_process = process

            print("Started TS stream capture...")
            print("Collecting noise profile (analyzing first second of audio)...")

            # Read chunks from ffmpeg output
            while self._running:
                try:
                    chunk = await process.stdout.read(self.chunk_size)
                    if not chunk:
                        break
                    
                    # Process chunk with noise reduction
                    processed_chunk = await self.audio_processor.process_chunk(chunk)
                    if processed_chunk is not None:
                        yield processed_chunk

                except asyncio.CancelledError:
                    print("TS stream reading cancelled")
                    break
                except Exception as e:
                    print(f"Error reading stream chunk: {str(e)}")
                    break

        except Exception as e:
            print(f"Error in TSPlayer: {str(e)}")
            raise
        finally:
            await self.close()

    async def close(self):
        """Clean up resources"""
        self._running = False
        
        if self._ffmpeg_process:
            try:
                # Try graceful termination first
                self._ffmpeg_process.terminate()
                try:
                    await asyncio.wait_for(self._ffmpeg_process.wait(), timeout=2.0)
                except asyncio.TimeoutError:
                    print("Forcing ffmpeg process to close...")
                    self._ffmpeg_process.kill()  # Force kill if termination takes too long
                    await self._ffmpeg_process.wait()
            except Exception as e:
                print(f"Error closing ffmpeg process: {str(e)}")
            finally:
                self._ffmpeg_process = None

        # Clean up audio processor
        if hasattr(self, 'audio_processor'):
            self.audio_processor.cleanup()
