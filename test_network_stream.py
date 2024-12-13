import asyncio
import argparse
import signal
from transcribe_audio import transcribe_network_stream
from ts_player import TSPlayer
from mic_input import MicrophoneInput

class StreamManager:
    def __init__(self):
        self.running = True
        self.current_task = None
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Set up handlers for graceful shutdown"""
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\nReceived shutdown signal, cleaning up...")
        self.running = False
        if self.current_task:
            self.current_task.cancel()

async def transcribe_from_ts(url, manager):
    """Transcribe from TS stream"""
    player = None
    try:
        print("Starting transcription from TS stream...")
        player = TSPlayer(url)
        manager.current_task = asyncio.current_task()
        await transcribe_network_stream(player.get_audio_stream())
    except asyncio.CancelledError:
        print("TS stream transcription cancelled")
    except Exception as e:
        print(f"Error in TS stream transcription: {str(e)}")
    finally:
        if player:
            try:
                await player.close()
            except Exception as e:
                print(f"Error closing TS player: {str(e)}")

async def transcribe_from_mic(manager):
    """Transcribe from microphone input"""
    mic = None
    try:
        print("Starting transcription from microphone...")
        mic = MicrophoneInput()
        manager.current_task = asyncio.current_task()
        await transcribe_network_stream(mic.get_audio_stream())
    except asyncio.CancelledError:
        print("Microphone transcription cancelled")
    except Exception as e:
        print(f"Error in microphone transcription: {str(e)}")
    finally:
        if mic:
            try:
                await mic.close()
            except Exception as e:
                print(f"Error closing microphone: {str(e)}")

async def cleanup(manager):
    """Cleanup function to handle graceful shutdown"""
    if manager.current_task and not manager.current_task.done():
        manager.current_task.cancel()
        try:
            await manager.current_task
        except asyncio.CancelledError:
            pass

async def main():
    """Main function to run the test"""
    parser = argparse.ArgumentParser(description='Audio transcription from TS stream or microphone')
    parser.add_argument('--source', choices=['ts', 'mic'], default='mic',
                       help='Audio source: "ts" for TS stream or "mic" for microphone input')
    parser.add_argument('--url', default='http://example.com/stream.ts',
                       help='URL of the TS stream (only used if source is "ts")')
    
    args = parser.parse_args()
    manager = StreamManager()
    
    try:
        if args.source == 'ts':
            await transcribe_from_ts(args.url, manager)
        else:
            await transcribe_from_mic(manager)
    except Exception as e:
        print(f"Error in main: {str(e)}")
    finally:
        await cleanup(manager)

def run():
    """Entry point with proper event loop handling"""
    try:
        if asyncio.get_event_loop().is_closed():
            asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except Exception as e:
        print(f"Fatal error: {str(e)}")
    finally:
        try:
            loop = asyncio.get_event_loop()
            if not loop.is_closed():
                loop.close()
        except Exception as e:
            print(f"Error closing event loop: {str(e)}")

if __name__ == "__main__":
    run()
