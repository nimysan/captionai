import asyncio
import argparse
from transcribe_audio import transcribe_network_stream
from ts_player import TSPlayer
from mic_input import MicrophoneInput

async def transcribe_from_ts(url):
    """Transcribe from TS stream"""
    try:
        print("Starting transcription from TS stream...")
        player = TSPlayer(url)
        await transcribe_network_stream(player.get_audio_stream())
    finally:
        if 'player' in locals():
            await player.close()

async def transcribe_from_mic():
    """Transcribe from microphone input"""
    try:
        print("Starting transcription from microphone...")
        mic = MicrophoneInput()
        await transcribe_network_stream(mic.get_audio_stream())
    finally:
        if 'mic' in locals():
            await mic.close()

async def main():
    """Main function to run the test"""
    parser = argparse.ArgumentParser(description='Audio transcription from TS stream or microphone')
    parser.add_argument('--source', choices=['ts', 'mic'], default='mic',
                       help='Audio source: "ts" for TS stream or "mic" for microphone input')
    parser.add_argument('--url', default='http://example.com/stream.ts',
                       help='URL of the TS stream (only used if source is "ts")')
    
    args = parser.parse_args()
    
    try:
        if args.source == 'ts':
            await transcribe_from_ts(args.url)
        else:
            await transcribe_from_mic()
    except Exception as e:
        print(f"Error in main: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
