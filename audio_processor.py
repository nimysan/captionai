import numpy as np
import noisereduce as nr
import librosa
import io
import soundfile as sf
import gc

class AudioProcessor:
    def __init__(self, sample_rate=16000):
        """
        Initialize audio processor with given sample rate
        """
        self.sample_rate = sample_rate
        self.noise_sample = None
        self.noise_collected = False
        self.initial_chunks = []
        self.initial_chunks_duration = 0
        self.target_noise_duration = 1  # 1 second of noise for profile
        self.max_chunk_size = 32768  # Maximum chunk size to process (32KB)

    def _bytes_to_float_array(self, audio_bytes):
        """Convert raw audio bytes to float array"""
        try:
            # Convert bytes to numpy array (16-bit PCM)
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
            # Convert to float32 and normalize to [-1, 1]
            return audio_array.astype(np.float32) / 32768.0
        except Exception as e:
            print(f"Error converting bytes to float array: {e}")
            return None

    def _float_array_to_bytes(self, audio_array):
        """Convert float array back to bytes"""
        try:
            # Ensure the array is within [-1, 1]
            audio_array = np.clip(audio_array, -1, 1)
            # Convert to 16-bit PCM
            audio_int = (audio_array * 32768).astype(np.int16)
            return audio_int.tobytes()
        except Exception as e:
            print(f"Error converting float array to bytes: {e}")
            return None

    async def process_chunk(self, chunk):
        """
        Process an audio chunk with noise reduction
        Returns processed audio chunk or None if still collecting noise profile
        """
        if not chunk:
            return None

        try:
            # Check chunk size
            if len(chunk) > self.max_chunk_size:
                print(f"Chunk size too large ({len(chunk)} bytes), truncating...")
                chunk = chunk[:self.max_chunk_size]

            # Convert input chunk to float array
            audio_array = self._bytes_to_float_array(chunk)
            if audio_array is None:
                return None

            if not self.noise_collected:
                # Collect initial audio for noise profile
                self.initial_chunks.append(audio_array)
                chunk_duration = len(audio_array) / self.sample_rate
                self.initial_chunks_duration += chunk_duration

                if self.initial_chunks_duration >= self.target_noise_duration:
                    # We have enough audio for noise profile
                    try:
                        self.noise_sample = np.concatenate(self.initial_chunks)
                        self.noise_collected = True
                        print("Noise profile collected")
                        # Process and return the collected audio
                        processed_audio = self._process_with_noise_reduction(
                            np.concatenate(self.initial_chunks)
                        )
                        self.initial_chunks = []  # Clear the buffer
                        gc.collect()  # Force garbage collection
                        return self._float_array_to_bytes(processed_audio)
                    except Exception as e:
                        print(f"Error processing noise profile: {e}")
                        self.cleanup()
                        return None
                return None

            # Process chunk with noise reduction
            processed_audio = self._process_with_noise_reduction(audio_array)
            return self._float_array_to_bytes(processed_audio)

        except Exception as e:
            print(f"Error processing audio chunk: {e}")
            return None

    def _process_with_noise_reduction(self, audio_array):
        """Apply noise reduction to audio array"""
        if self.noise_sample is None:
            return audio_array

        try:
            # Apply noise reduction with optimized parameters for streaming
            reduced_noise = nr.reduce_noise(
                y=audio_array,
                sr=self.sample_rate,
                y_noise=self.noise_sample,
                prop_decrease=0.75,
                n_fft=1024,  # Reduced from 2048 for faster processing
                win_length=1024,  # Reduced from 2048 for faster processing
                hop_length=256,   # Reduced from 512 for faster processing
                n_jobs=1  # Single thread to prevent threading issues
            )

            return reduced_noise
        except Exception as e:
            print(f"Error in noise reduction: {e}")
            return audio_array  # Return original audio if noise reduction fails

    def cleanup(self):
        """Clean up resources and reset state"""
        self.noise_sample = None
        self.noise_collected = False
        self.initial_chunks = []
        self.initial_chunks_duration = 0
        gc.collect()  # Force garbage collection
