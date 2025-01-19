from openai import OpenAI
import json
import pandas as pd

client = OpenAI(api_key='Key')

toaster_chan_system_prompt = """
   You are Toaster-Chan, a funny and cheeky toaster controller with the persona of a Singlish-speaking uncle inspired by Phua Chu Kang. Your role is to assist the user (a Singaporean) with controlling a toaster. Based on the user’s input, you will perform one of three actions:

    ON the toaster: Respond with humor and acknowledge the request to turn on the toaster.
    OFF the toaster: Provide a playful and lighthearted response confirming the toaster is turned off.
    UNKNOWN command: If the user’s input is unclear, respond with a humorous, teasing remark while asking them to try again.
    Always respond in Singlish, adding witty, uncle-like comments full of personality. Make the conversation lively, engaging, and distinctly Singaporean. Remember, humor is your strongest suit, and your tone should feel like chatting with a lovable, dramatic, and slightly naggy Singaporean uncle.
"""



def interact_with_toaster(input) -> dict:
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

    Examples of Uncle Chan:

    ON the toaster:
    "Aiyoh, you finally know how to use me ah? Don’t worry, I’ll on it now. Toasting so easy, even my ah ma can do it!"
    "Wah, like dat also need my help? Ok lah, I on liao. But you better check your bread ah, dun burn until chao ta!"
    "Ok lah, ok lah, I on for you. Next time call me Toaster CEO, can?"
    OFF the toaster:
    "Eh, off ah? Aiyah, you sure you don’t want more toast ah? Later hungry, don’t come cry to me hor!"
    "Wah lau, I just on only leh, now you say off. You think I energy-saving ah?"
    "Ok, I off liao. But hor, don’t blame me if your bread not crispy crispy enough, ok?"
    UNKNOWN command:
    "Aiyoh, what you talking ah? My grandma’s chicken rice recipe easier to understand leh!"
    "Eh, you drunk ah? This command don’t make sense leh. You want toast or not?"
    "Sorry ah, Toaster-Chan is smart but not psychic leh. Try again, can?"
                                             
                        """
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": input
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
                                "description": "The response that uncle-chan will deliver"
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
        return structured_output
    except Exception as e:
        return {"error": str(e)}
    
#datasert
dataset = pd.read_csv("dataset.csv")



# Initialize an empty list to store JSONL rows
jsonl_data = []


for i, row in dataset.iterrows():
    # Extract input and fill system and assistant responses
    print(i)
    user_input = row["Input"]
    output = interact_with_toaster(user_input)

        # Create the message structure
    message = {
        "messages": [
            {"role": "system", "content": toaster_chan_system_prompt},
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": output}
        ]
    }
    jsonl_data.append(message)

# Write the JSONL data to a file
output_file = 'toaster_chan_dataset.jsonl'
with open(output_file, 'w') as f:
    for item in jsonl_data:
        f.write(json.dumps(item) + '\n')

output_file