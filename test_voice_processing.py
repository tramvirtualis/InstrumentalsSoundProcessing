"""
Test script for Voice Processing module
Kiểm tra các tính năng xử lý âm thanh với kỹ thuật tiếng nói
"""

from src.voice_processing import InstrumentVoiceProcessor
from pathlib import Path

def test_voice_processing():
    """Test các tính năng voice processing"""
    
    # Khởi tạo processor
    processor = InstrumentVoiceProcessor()
    
    print("=" * 60)
    print("TESTING VOICE PROCESSING MODULE")
    print("=" * 60)
    
    # Kiểm tra xem có file test không
    test_file = Path("uploads") / "test.wav"
    
    if not test_file.exists():
        print("\n⚠️  Không tìm thấy file test.wav trong thư mục uploads/")
        print("Vui lòng upload một file âm thanh để test")
        return
    
    print(f"\n✓ Tìm thấy file test: {test_file}")
    
    # Test 1: LPC Analysis
    print("\n" + "-" * 60)
    print("TEST 1: LPC Analysis")
    print("-" * 60)
    try:
        lpc_results = processor.lpc_analysis(test_file)
        print(f"✓ LPC Order: {lpc_results['order']}")
        print(f"✓ LPC Coefficients: {len(lpc_results['lpc_coefficients'])} coefficients")
        print(f"✓ Cepstral Coefficients: {len(lpc_results['cepstral_coefficients'])} coefficients")
        print(f"✓ First 3 LPC coefficients: {lpc_results['lpc_coefficients'][:3]}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: Waveform Data
    print("\n" + "-" * 60)
    print("TEST 2: Waveform Visualization")
    print("-" * 60)
    try:
        waveform_data = processor.generate_waveform_data(test_file)
        print(f"✓ Total points: {len(waveform_data['points'])}")
        print(f"✓ Audio length: {waveform_data['length']} samples")
        print(f"✓ Sample rate: {waveform_data['sample_rate']} Hz")
        print(f"✓ Segments: {waveform_data['num_segments']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 3: Formant Analysis
    print("\n" + "-" * 60)
    print("TEST 3: Formant Analysis")
    print("-" * 60)
    try:
        formants = processor.analyze_formants(test_file)
        print(f"✓ Found {len(formants)} formants")
        for i, formant in enumerate(formants[:3]):  # Show first 3
            print(f"  Formant {i+1}: {formant['frequency']:.2f} Hz (magnitude: {formant['magnitude']:.2f})")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 4: Pitch Tracking
    print("\n" + "-" * 60)
    print("TEST 4: Pitch Tracking")
    print("-" * 60)
    try:
        pitch_data = processor.pitch_tracking(test_file)
        print(f"✓ Tracked {len(pitch_data)} pitch points")
        if len(pitch_data) > 0:
            print(f"  First pitch: {pitch_data[0]['frequency']:.2f} Hz ({pitch_data[0]['note']})")
            print(f"  Time: {pitch_data[0]['time']:.3f}s")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 5: Autocorrelation Plot
    print("\n" + "-" * 60)
    print("TEST 5: Autocorrelation Plot Generation")
    print("-" * 60)
    try:
        output_dir = Path("static/spectrograms")
        output_dir.mkdir(parents=True, exist_ok=True)
        autocorr_img = processor.generate_autocorrelation_plot(test_file, output_dir)
        print(f"✓ Generated autocorrelation plot: {autocorr_img}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 6: Detailed Spectrogram
    print("\n" + "-" * 60)
    print("TEST 6: Detailed Spectrogram Generation")
    print("-" * 60)
    try:
        output_dir = Path("static/spectrograms")
        spec_img = processor.generate_detailed_spectrogram(test_file, output_dir)
        print(f"✓ Generated detailed spectrogram: {spec_img}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_voice_processing()
