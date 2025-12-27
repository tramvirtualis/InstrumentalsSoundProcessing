import soundfile as sf

data, samplerate = sf.read('trial.wav')
print('Sample rate: ', samplerate)
print('Audio data shape: ', data.shape)
print('First 10 samples of audio data: ', data[:10])