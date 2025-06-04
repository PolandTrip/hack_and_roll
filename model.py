import os
from dotenv import load_dotenv
import json
import logging
import requests
from openai import OpenAI
from pydub import AudioSegment
from pydub.playback import play
from elevenlabs import save, Voice, VoiceSettings
from elevenlabs.client import ElevenLabs

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPEN_AI_KEY"))

def transcribe_audio_whisper(audio_file: str) -> str:
     """
    Transcribe an audio file using OpenAI's Whisper model via the OpenAI Python SDK.
    
    Parameters:
        audio_file_path (str): Path to the audio file to transcribe.
    
    Returns:
        str: The transcribed text.
    """
     try:
         with open(audio_file, "rb") as audio_file:
             transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file, 
                response_format="text",
                prompt="Umm, let me think like, hmm... Okay, here's what I'm, like, thinking., errrr. All the possible filler words please detect")
             print(transcription)
             return transcription
     except Exception as e:
        logging.error(f"Failed to transcribe audio file: {e}")
        raise



# Define the function
def interact_with_toaster(audio_file:str) -> dict:
    """
    Interacts with OpenAI GPT-4 model to handle toaster commands.
    
    Args:
        input_text (str): User's command for the toaster.
        encoded_audio (str): Base64-encoded audio input (optional).

    Returns:
        dict: A structured JSON response containing an audio response and command.
    """
    # Set up the request messages
    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": 
                        """
                        You are Toaster-Chan, a funny and cheeky toaster controller with the persona of a Singlish-speaking uncle inspired by Phua Chu Kang. Your role is to assist the user (a Singaporean) with controlling a toaster. Based on the user’s input, you will perform one of three actions:

                        ON the toaster: Respond with humor and acknowledge the request to turn on the toaster.
                        OFF the toaster: Provide a playful and lighthearted response confirming the toaster is turned off.
                        UNKNOWN command: If the user’s input is unclear, respond with a humorous, teasing remark while asking them to try again.
                        Always respond in Singlish, adding witty, uncle-like comments full of personality. Make the conversation lively, engaging, and distinctly Singaporean. Remember, humor is your strongest suit, and your tone should feel like chatting with a lovable, dramatic, and slightly naggy Singaporean uncle.
                        
                        You should output the on command if they mention anything about turn on my toaster or on toaster
                        
                        Examples of Uncle Chan:

                        ON the toaster:
                        "Aiyoh, you finally know how to use me ah? Don’t worry, I’ll on it now. Toasting so easy, even my ah ma can do it!"
                        "Ok lah, ok lah, I on for you. Next time call me Toaster CEO, can?"
                        OFF the toaster:
                        "Eh, off ah? Aiyah, you sure you don’t want more toast ah? Later hungry, don’t come cry to me hor!"
                        "Wah lau, I just on only leh, now you say off. You think I energy-saving ah?"
                        "Ok, I off liao. But hor, don’t blame me if your bread not crispy crispy enough, ok?"
                        UNKNOWN command:
                        "Aiyoh, what you talking ah? My grandma’s chicken rice recipe easier to understand leh!"
                        "Eh, you drunk ah? This command don’t make sense leh. You want toast or not?"
                        "Sorry ah, Toaster-Chan is smart but not psychic leh. Try again, can?"
                        Dont use the same example more than once

                        """
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": transcribe_audio_whisper(audio_file=audio_file)
                }
            ]
        }
    ]

    try:
        response = client.chat.completions.create(
            model="ft:gpt-4o-mini-2024-07-18:chingu:hack-n-roll:Ar86apV1",
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "toaster_command",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "audio_response": {
                                "type": "string",
                                "description": "The response that uncle-chan will deliver"
                            },
                            "command": {
                                "type": "string",
                                "description": "The command to control the toaster.",
                                "enum": ["on", "off"]
                            }
                        },
                        "required": ["audio_response", "command"],
                        "additionalProperties": False
                    }
                }
            },
            temperature=1,
            top_p=1,
            frequency_penalty=1,
            presence_penalty=0
        )

        # Parse the JSON response
        structured_output = response.choices[0].message.content
        return json.loads(structured_output)
    except Exception as e:
        return {"error": str(e)}

def text_to_speech(text: str, filename: str, voice: str = 'Wing-Yi') -> None:
    """
    Convert text to speech using Narakeet API and save it as an audio file.
    
    Parameters:
        text (str): The text to be converted to speech.
        filename (str): The name of the file to save the audio.
        voice (str): The voice to use for the speech synthesis. Default is 'Seo-Yeon'.
    """
    url = f'https://api.narakeet.com/text-to-speech/m4a?voice={voice}'
    headers = {
        'Accept': 'application/octet-stream',
        'Content-Type': 'text/plain',
        'x-api-key': 'wkA2YLPyxy24vOiztNKOA26bOFgPyH91745BixBe',
    }
    
    try:
        logging.info(f"Converting text to speech with Narakeet: {text[:30]}...")  # Log first 30 characters of text
        response = requests.post(url, headers=headers, data=text.encode('utf8'))
        response.raise_for_status()  # Raise an error for bad status codes
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        logging.info(f"Audio file saved as {filename}")
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to convert text to speech: {e}")
        raise


def adjust_audio_pitch_and_speed(audio_file, output_file, pitch_semitones=0, speed_factor=1.0):
    """
    Adjust the pitch and speed of an audio file.

    Args:
        audio_file (str): Path to the input audio file.
        output_file (str): Path to save the modified audio.
        pitch_semitones (int): Number of semitones to adjust pitch (-12 to +12).
        speed_factor (float): Speed adjustment factor (>1.0 = faster, <1.0 = slower).
    """
    audio = AudioSegment.from_file(audio_file)

    # Adjust pitch by changing frame rate
    if pitch_semitones != 0:
        new_sample_rate = int(audio.frame_rate * (2 ** (pitch_semitones / 12)))
        audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_sample_rate}).set_frame_rate(audio.frame_rate)

    # Adjust speed
    if speed_factor != 1.0:
        audio = audio.speedup(playback_speed=speed_factor)

    # Export the modified audio
    audio.export(output_file, format="wav")
    print(f"Modified audio saved to {output_file}")

elev = ElevenLabs(
  api_key="sk_630352530c31cae8a37bc586889a3d99526c9207f550798c",
)

voice_settings = VoiceSettings(
    stability=0.5,          # Adjusts the emotional range; lower values introduce more emotion.
    similarity_boost=0.8,   # Determines adherence to the original voice; higher values mimic the original more closely.
    #style=0.5,              # Amplifies the style of the original speaker; consumes more computational resources.
    #use_speaker_boost=True, # Enhances similarity to the original speaker; may increase latency.
    speed=0.7               # Controls the speech speed; range is 0.7 (slower) to 1.2 (faster), with 1.0 being default.
)



def eleven_tts(text):
    """
    Generate speech from text and save the audio to a file.
    
    Args:
        text (str): The text to convert to speech.
        output_file (str): Path to save the audio file.
    """
    # Generate the audio using ElevenLabs API
    audio = elev.generate(
        text=text,
        voice=Voice(
            voice_id="x959FyxFeswkQQqFjoPb",
            settings=voice_settings
        ),
        model="eleven_turbo_v2_5",
    )
    save(audio, "output.wav")
    #adjust_audio_pitch_and_speed("temp_audio.wav", "output.wav", pitch_semitones=2, speed_factor=1)
