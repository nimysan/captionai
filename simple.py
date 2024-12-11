import asyncio

# This example uses aiofile for asynchronous file reads.
# It's not a dependency of the project but can be installed
# with `pip install aiofile`.
import aiofile
import datetime

from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent, TranscriptResultStream
from amazon_transcribe.utils import apply_realtime_delay

"""
Here's an example of a custom event handler you can extend to
process the returned transcription results as needed. This
handler will simply print the text out to your interpreter.
"""

SAMPLE_RATE = 44100 #16000
BYTES_PER_SAMPLE = 2
CHANNEL_NUMS = 1

# An example file can be found at tests/integration/assets/原版-带噪音-中文-男声.wav
AUDIO_PATH = "/Users/yexw/PycharmProjects/awsgists/stream_caption/right_test.wav"
CHUNK_SIZE = 1024 * 16
REGION = "us-west-2"
SRT_PATH = "match_test.srt"


def convert_to_srt_time(seconds):
    """
    将秒数转换为 SRT 时间格式 (HH:MM:SS,MS)
    """
    dt = datetime.datetime(1900, 1, 1) + datetime.timedelta(seconds=seconds)
    ms = dt.microsecond // 1000
    return f"{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d},{ms:03d}"

"""
ffmpeg -i 原版-带噪音-中文-男声.wav -af "highpass=f=200" -f wav - | sox -t wav - -t wav output_voice.wav noisered
"""
def write_srt(filename, text):
    """
    将字幕内容追加到 SRT 文件的末尾。
    :param filename: SRT 文件的路径和文件名
    :param text: 要写入的字幕文本
    """
    try:
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(text + '\n')
    except Exception as e:
        print(f"Error writing to SRT file: {e}")


class MyEventHandler(TranscriptResultStreamHandler):
    def __init__(self, transcript_result_stream: TranscriptResultStream):
        super(MyEventHandler, self).__init__(transcript_result_stream)
        self.previous_sentence = ''
        self.cc_fragments = []
        self.current_sentence_length = 0
        self.previous_time_range = None

    def calculate_start_to_end(self, items):
        start = None;
        end = None;
        for item in items:
            c_start = item.start_time
            c_end = item.end_time

            if start is None:
                start = c_start

            if end is None:
                end = c_end

            if c_end > end:
                end = c_end

        return {
            "s": start,
            "e": end
        }

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        # This handler can be implemented to handle transcriptions as needed.
        # Here's an example to get started.
        results = transcript_event.transcript.results
        # print(results)
        for result in results:
            for alt in result.alternatives:
                # print(alt.transcript)
                time_range = self.calculate_start_to_end(alt.items)
                # print(f"time range ---> {time_range}")
                current_sentence = alt.transcript
                current_sentence_length = len(current_sentence)
                # print(len(alt.items))
                previous_sentence_length = len(self.previous_sentence)
                if current_sentence_length < previous_sentence_length:
                    print(f"{self.previous_time_range}---{self.previous_sentence}")
                    write_srt(SRT_PATH,
                              f"{convert_to_srt_time(self.previous_time_range['s'])} --> {convert_to_srt_time(self.previous_time_range['e'])}")
                    write_srt(SRT_PATH, f"{self.previous_sentence}")
                    write_srt(SRT_PATH, "\n\n")

                self.previous_sentence = current_sentence
                self.previous_time_range = time_range


async def basic_transcribe():
    # Setup up our client with our chosen AWS region
    client = TranscribeStreamingClient(region=REGION)

    # Start transcription to generate our async stream
    stream = await client.start_stream_transcription(
        language_code="zh-CN",  # ar-SA
        media_sample_rate_hz=SAMPLE_RATE,
        media_encoding="pcm",
    )

    async def write_chunks():
        # NOTE: For pre-recorded files longer than 5 minutes, the sent audio
        # chunks should be rate limited to match the realtime bitrate of the
        # audio stream to avoid signing issues.
        async with aiofile.AIOFile(AUDIO_PATH, "rb") as afp:
            reader = aiofile.Reader(afp, chunk_size=CHUNK_SIZE)
            await apply_realtime_delay(
                stream, reader, BYTES_PER_SAMPLE, SAMPLE_RATE, CHANNEL_NUMS
            )
        await stream.input_stream.end_stream()

    # Instantiate our handler and start processing events
    handler = MyEventHandler(stream.output_stream)
    await asyncio.gather(write_chunks(), handler.handle_events())


loop = asyncio.get_event_loop()
loop.run_until_complete(basic_transcribe())
loop.close()
