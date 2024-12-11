"""
Amazon Transcribe Streaming Client
This script provides real-time audio transcription using Amazon Transcribe Streaming service.
It supports PCM audio files and handles streaming with proper rate limiting for files longer than 5 minutes.
"""

import asyncio
import aiofile
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
from amazon_transcribe.utils import apply_realtime_delay

# Audio configuration constants
SAMPLE_RATE = 16000
BYTES_PER_SAMPLE = 2
CHANNEL_NUMS = 1
CHUNK_SIZE = 1024 * 8

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
                print(alt.transcript)


async def transcribe_audio_stream():
    """
    Main transcription function that sets up the streaming client and processes audio data.
    Handles both the audio streaming and transcription result processing.
    """
    # Initialize the transcription client
    client = TranscribeStreamingClient(region=REGION)

    # Start the transcription stream
    stream = await client.start_stream_transcription(
        language_code="en-US",
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


def main():
    """
    Entry point of the script. Sets up and runs the asyncio event loop.
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(transcribe_audio_stream())
    loop.close()


if __name__ == "__main__":
    main()
