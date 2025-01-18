from openai import OpenAI
import os
from dotenv import load_dotenv
import base64
import json

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPEN_AI_KEY"))

# Define the function
def interact_with_toaster(input_text, encoded_audio=None):
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
                    "text": input_text
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
            max_completion_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        # Parse the JSON response
        structured_output = response.choices[0].message.content
        return json.loads(structured_output)
    except Exception as e:
        return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    input_text = "Hey whats the time now"
    response = interact_with_toaster(input_text)
    #print(json.dumps(response, indent=4))
    print(response)
