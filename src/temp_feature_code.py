    def extract_acoustic_features(self, audio_path):
        """
        Trích xuất các đặc trưng âm thanh (Acoustic Features)
        Dựa trên các tài liệu học thuật về Music Information Retrieval (MIR)
        
        Features:
        1. Zero Crossing Rate (ZCR): Độ ồn/sắc của âm thanh
        2. Spectral Centroid: Trọng tâm phổ (độ sáng)
        3. Spectral Bandwidth: Độ rộng băng tần
        4. RMS Energy: Năng lượng trung bình
        """
        # Load output
        try:
            y, sr = librosa.load(str(audio_path), sr=None, mono=True)
        except Exception:
            import soundfile as sf
            y, sr = sf.read(str(audio_path))
            if len(y.shape) > 1: y = np.mean(y, axis=1)
            y = y.astype(np.float32)

        if len(y) == 0:
            raise ValueError("Empty audio file")

        # 1. Zero Crossing Rate
        zcr = librosa.feature.zero_crossing_rate(y)
        zcr_mean = float(np.mean(zcr))
        zcr_var = float(np.var(zcr))

        # 2. Spectral Centroid (Brightness)
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        cent_mean = float(np.mean(centroid))
        
        # 3. Spectral Bandwidth
        bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        bw_mean = float(np.mean(bandwidth))
        
        # 4. RMS Energy
        rms = librosa.feature.rms(y=y)
        rms_mean = float(np.mean(rms))
        
        return {
            "zcr": {
                "mean": zcr_mean,
                "var": zcr_var,
                "desc": "Tỷ lệ qua điểm 0 (Độ sắc/ồn)"
            },
            "spectral_centroid": {
                "mean": cent_mean,
                "unit": "Hz",
                "desc": "Trọng tâm phổ (Độ sáng)"
            },
            "spectral_bandwidth": {
                "mean": bw_mean,
                "unit": "Hz",
                "desc": "Độ rộng băng tần hiệu dụng"
            },
            "rms_energy": {
                "mean": rms_mean,
                "desc": "Năng lượng trung bình (Âm lượng)"
            }
        }
