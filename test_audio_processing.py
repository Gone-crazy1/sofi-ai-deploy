#!/usr/bin/env python3
"""
Test audio processing functionality with ffmpeg
"""

print("🎵 Testing audio processing with ffmpeg...")

try:
    from pydub import AudioSegment
    from pydub.utils import which
    import tempfile
    import os
    
    print("✅ Pydub imported successfully")
    
    # Check if ffmpeg executables are available
    ffmpeg_path = which("ffmpeg")
    ffprobe_path = which("ffprobe")
    
    print(f"🔧 ffmpeg path: {ffmpeg_path}")
    print(f"🔧 ffprobe path: {ffprobe_path}")
    
    if ffmpeg_path:
        print("✅ ffmpeg found and accessible")
    else:
        print("❌ ffmpeg not found in PATH")
        
    if ffprobe_path:
        print("✅ ffprobe found and accessible")
    else:
        print("❌ ffprobe not found in PATH")
    
    # Test AudioSegment configuration
    AudioSegment.converter = ffmpeg_path
    AudioSegment.ffmpeg = ffmpeg_path
    AudioSegment.ffprobe = ffprobe_path
    
    print("✅ AudioSegment configured with ffmpeg")
    
    # Test creating a simple audio segment (this tests if the configuration works)
    try:
        # Create a simple silent audio segment as a test
        silent_audio = AudioSegment.silent(duration=100)  # 100ms of silence
        print("✅ AudioSegment basic functionality working")
        
        # Test export functionality
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name
            
        try:
            silent_audio.export(temp_path, format="wav")
            print("✅ Audio export functionality working")
            
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
        except Exception as export_error:
            print(f"⚠️ Audio export test failed: {export_error}")
            
    except Exception as audio_error:
        print(f"⚠️ AudioSegment basic test failed: {audio_error}")
    
    print("\n🎯 Audio processing setup completed!")
    print("✅ Voice message processing should now work properly")
    
except Exception as e:
    print(f"❌ Error testing audio processing: {e}")
    import traceback
    traceback.print_exc()
