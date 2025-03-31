import gradio as gr
import spaces
import subprocess
import os
from PIL import Image
import ffmpeg
from pydub import AudioSegment

import numpy as np
import soundfile as sf

def save_audio_mp3(audio_tuple, filename):
    sampling_rate, audio_data = audio_tuple
    audio_bytes = np.array(audio_data, dtype=np.int16).tobytes()
    audio_segment = AudioSegment(audio_bytes, sample_width=2, frame_rate=sampling_rate, channels=1)
    audio_segment.export(filename, format="mp3")
    
    return f"Audio saved successfully as {filename}"


def audio_video():
    input_video = ffmpeg.input('results/result_voice.mp4')
    input_audio = ffmpeg.input('sample_data/uploaded_audio.mp3')
    os.system(f"rm -rf results/final_output.mp4")
    ffmpeg.concat(input_video, input_audio, v=1, a=1).output('results/final_output.mp4').run()
    
    return "results/final_output.mp4"

@spaces.GPU
def run_infrence(input_image,input_audio):
    pil_image = Image.fromarray(input_image.astype(np.uint8))

    save_dir = "sample_data"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # Save input image 
    filename = os.path.join(save_dir, "uploaded_image.png")
    pil_image.save(filename)

    #Save input audio
    save_audio_mp3(input_audio, "sample_data/uploaded_audio.mp3")

    command = f'python3 inference.py --checkpoint_path checkpoints/wav2lip_gan.pth --face sample_data/uploaded_image.png --audio sample_data/uploaded_audio.mp3'
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()

    return audio_video()
    
def run():
    with gr.Blocks(css=".gradio-container {background-color: lightgray} #radio_div {background-color: #FFD8B4; font-size: 40px;} h3,h1,h2,p {color: black;}") as demo:
        gr.Markdown("<p style='text-align: left;font-size:18px'>"+ "Hey, check out our app! It's like having a magic tool for making videos. You put in a picture and audio, and it creates a video where the lips move perfectly with the audio. It's super easy – just upload your picture and audio, and click 'generate'! You've got a cool video where it looks like the person in the picture is speaking." + "</p>")
        with gr.Group():    
            with gr.Row():
                input_image = gr.Image(label="Input Image")
                input_audio = gr.Audio(label="Input Audio")
                video_out = gr.Video(show_label=True,label="Output")
            with gr.Row():
                btn = gr.Button("Generate")
        gr.Markdown("<h1 style='text-align: center;'>"+ "Demo Inputs and Output" + "</h1>")   
        with gr.Row():
            gr.Image("sample/spark.png",label="Input Image")
            gr.Audio("sample/spark_1.1.mp3",label="Input Audio")
            gr.Video("sample/final_output.mp4",label="Output")
        
        gr.Markdown("""<p style='text-align: center;'>Feel free to give us your thoughts on this demo and please contact us at 
                    <a href="mailto:letstalk@pragnakalp.com" target="_blank">letstalk@pragnakalp.com</a> 
                    </p><p style='text-align: center;'>Developed by: <a href="https://www.pragnakalp.com" target="_blank">Pragnakalp Techlabs</a></p>""")
    
        btn.click(run_infrence,inputs=[input_image,input_audio], outputs=[video_out])
        demo.queue()
        demo.launch(server_name="0.0.0.0", server_port=7860)

if __name__ == "__main__":
    run()