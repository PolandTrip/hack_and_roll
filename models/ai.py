from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import logging

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
                    "text": (
                        "As an AI-powered funny toaster, respond to users who interact with you to control the toasting functions.\n\n"
                        "Use humor and playful language to entertain while assisting the user with various toasting commands.\n\n"
                        "# Steps\n\n"
                        "1. **Greeting**: Start with a friendly and humorous greeting.\n"
                        "2. **Understand the Command**: Identify and understand the user's request regarding toasting settings or functions.\n"
                        "3. **Respond**: Use humor or a funny analogy while confirming the action or providing information.\n"
                        "4. **Provide Options**: If applicable, offer additional settings or options in a light-hearted manner.\n"
                        "5. **Confirm**: Reassure the user that their command has been or will be executed.\n\n"
                        "# Output Format\n\n"
                        "- Use a conversational format.\n"
                        "- Responses should be a few sentences long, maintaining a balance between humor and clarity.\n"
                        "- Conclude with a confirmation of the action.\n"
                    )
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

    # Call the OpenAI API
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
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
                                "description": "The audio response associated with the toaster command."
                            },
                            "command": {
                                "type": "string",
                                "description": "The command to control the toaster.",
                                "enum": ["on", "off", "unknown"]
                            }
                        },
                        "required": ["audio_response", "command"],
                        "additionalProperties": False
                    }
                }
            },
            temperature=1,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        # Parse the JSON response
        structured_output = response.choices[0].message.content
        return json.loads(structured_output)
    except Exception as e:
        return {"error": str(e)}

# print(interact_with_toaster("test5.wav"))