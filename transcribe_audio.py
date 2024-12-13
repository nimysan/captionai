"""
Amazon Transcribe Streaming Client
This script provides real-time audio transcription using Amazon Transcribe Streaming service.
It supports PCM audio files and handles streaming with proper rate limiting for files longer than 5 minutes.
"""

import asyncio
import aiofile
import boto3
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
from amazon_transcribe.utils import apply_realtime_delay
import time

# Audio configuration constants
SAMPLE_RATE = 16000
BYTES_PER_SAMPLE = 2
CHANNEL_NUMS = 1
CHUNK_SIZE = 1024 * 4  # Reduced to match mic_input.py

# AWS and file path configuration
REGION = "us-west-2"
AUDIO_PATH = "/stream_caption/chinese.wav"


class TranscriptionHandler(TranscriptResultStreamHandler):
    """
    Custom handler for processing transcription results from Amazon Transcribe.
    Extends TranscriptResultStreamHandler to process real-time transcription events.
    """
    
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        """
        Process incoming transcription events and print the transcribed text.
        
        Args:
            transcript_event (TranscriptEvent): The transcription event containing results
        """
        results = transcript_event.transcript.results
        for result in results:
            for alt in result.alternatives:
                print(f"Transcription: {alt.transcript}")


async def check_aws_credentials():
    """Check if AWS credentials are properly configured"""
    try:
        boto3.client('sts').get_caller_identity()
        return True
    except Exception as e:
        print(f"AWS Credentials Error: {str(e)}")
        print("Please configure AWS credentials with appropriate permissions")
        return False


async def transcribe_audio_stream():
    """
    Main transcription function that sets up the streaming client and processes audio data.
    Handles both the audio streaming and transcription result processing.
    """
    if not await check_aws_credentials():
        return

    try:
        # Initialize the transcription client
        client = TranscribeStreamingClient(region=REGION)

        # Start the transcription stream
        stream = await client.start_stream_transcription(
            language_code="ar-SA",  # Changed to Arabic (Saudi Arabia)
            media_sample_rate_hz=SAMPLE_RATE,
            media_encoding="pcm",
        )

        async def stream_audio_chunks():
            """
            Stream audio data from file to Amazon Transcribe with proper rate limiting.
            """
            async with aiofile.AIOFile(AUDIO_PATH, "rb") as afp:
                reader = aiofile.Reader(afp, chunk_size=CHUNK_SIZE)
                await apply_realtime_delay(
                    stream, 
                    reader, 
                    BYTES_PER_SAMPLE, 
                    SAMPLE_RATE, 
                    CHANNEL_NUMS
                )
            await stream.input_stream.end_stream()

        # Set up handler and process events
        handler = TranscriptionHandler(stream.output_stream)
        await asyncio.gather(stream_audio_chunks(), handler.handle_events())

    except Exception as e:
        print(f"Transcription Error: {str(e)}")


async def transcribe_network_stream(audio_stream):
    """
    Transcribe audio from a network stream (e.g., ffmpeg output).
    
    Args:
        audio_stream: An async iterator that yields chunks of PCM audio data
                     (16000 Hz, 16-bit, mono)
    """
    if not await check_aws_credentials():
        return

    client = None
    stream = None
    stream_task = None
    handler_task = None

    try:
        print("Initializing transcription client...")
        client = TranscribeStreamingClient(region=REGION)
        
        print("Starting transcription stream...")
        stream = await client.start_stream_transcription(
            language_code="zh-CN",
            media_sample_rate_hz=SAMPLE_RATE,
            media_encoding="pcm",
        )

        async def stream_audio():
            """
            Stream audio data from network source to Amazon Transcribe with rate limiting.
            """
            bytes_per_second = SAMPLE_RATE * BYTES_PER_SAMPLE * CHANNEL_NUMS
            chunk_duration = CHUNK_SIZE / bytes_per_second
            
            try:
                print("Starting to stream audio chunks...")
                async for chunk in audio_stream:
                    if not chunk:
                        break
                    
                    try:
                        # Send chunk to transcribe
                        await stream.input_stream.send_audio_event(audio_chunk=chunk)
                        
                        # Rate limiting to maintain real-time pace
                        await asyncio.sleep(chunk_duration)
                    except asyncio.CancelledError:
                        break
                    except Exception as e:
                        print(f"Error sending audio chunk: {e}")
                        break
                    
            except GeneratorExit:
                print("Audio stream generator closed")
            except Exception as e:
                print(f"Error streaming audio: {e}")
            finally:
                if stream and stream.input_stream:
                    try:
                        print("Ending audio stream...")
                        await stream.input_stream.end_stream()
                    except Exception as e:
                        print(f"Error ending stream: {e}")

        print("Setting up transcription handler...")
        handler = TranscriptionHandler(stream.output_stream)
        
        # Create tasks for streaming and handling
        stream_task = asyncio.create_task(stream_audio())
        handler_task = asyncio.create_task(handler.handle_events())
        
        # Wait for both tasks to complete
        await asyncio.gather(stream_task, handler_task)

    except Exception as e:
        print(f"Transcription Error: {str(e)}")
    finally:
        # Clean up tasks
        if stream_task and not stream_task.done():
            stream_task.cancel()
            try:
                await stream_task
            except asyncio.CancelledError:
                pass
            
        if handler_task and not handler_task.done():
            handler_task.cancel()
            try:
                await handler_task
            except asyncio.CancelledError:
                pass


def main():
    """
    Entry point of the script. Sets up and runs the asyncio event loop.
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(transcribe_audio_stream())
    loop.close()


if __name__ == "__main__":
    main()
