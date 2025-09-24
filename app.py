import streamlit as st
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips, ImageClip
import tempfile
import os

st.title("Video Looper to Match Audio")

# User uploads
video_file = st.file_uploader("Upload a video (.mp4), gif, or image", type=["mp4", "gif", "png", "jpg", "jpeg"])
audio_file = st.file_uploader("Upload an audio track (.mp3)", type=["mp3", "wav", "ogg"])

if video_file and audio_file:
    # Save the uploaded files to a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = os.path.join(tmpdir, video_file.name)
        audio_path = os.path.join(tmpdir, audio_file.name)
        
        # Write files to temp dir
        with open(video_path, "wb") as f:
            f.write(video_file.read())
        with open(audio_path, "wb") as f:
            f.write(audio_file.read())
        
        # Determine if it's an image or video/gif by extension
        if video_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Convert image to video with the same duration as audio
            audio_clip = AudioFileClip(audio_path)
            video_clip = (ImageClip(video_path)
                        .with_duration(audio_clip.duration)
                        .with_audio(audio_clip))
            output_path = os.path.join(tmpdir, "output.mp4")
            video_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
            video_clip.close()
            audio_clip.close()
        else:
            # Process as video/gif
            video_clip = VideoFileClip(video_path)
            audio_clip = AudioFileClip(audio_path)
            num_loops = int(audio_clip.duration // video_clip.duration) + 1
            video_loops = [video_clip.copy() for _ in range(num_loops)]
            looped_video = concatenate_videoclips(video_loops)
            final_clip = looped_video.subclipped(0, audio_clip.duration).with_audio(audio_clip)
            output_path = os.path.join(tmpdir, "output.mp4")
            final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
            video_clip.close()
            audio_clip.close()
            final_clip.close()
        
        # Present for download
        with open(output_path, "rb") as f:
            st.success("Video created! Download below.")
            st.download_button('Download video', f, file_name="output_video.mp4", mime='video/mp4')
