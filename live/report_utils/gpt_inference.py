""" TAKES IN TRANSCRIPT PATH, RETURNS BINARY GPT OUTPUTS """
from openai import OpenAI
from depscope.settings import GPT_MODEL
import json
from typing import Any

def gpt_inference(full_transcript: str) -> int:
    """
    Performs GPT inference on the full transcript to determine if the patient has depression.

    Args:
        full_transcript (str): The full transcript of the clinical interview.

    Returns:
        int: The binary diagnosis (0 for Not Depressed, 1 for Depressed).
    """
    # Initialize the OpenAI client
    client = OpenAI()

    # Format the input for GPT
    messages = [
        {
            "role": "system",
            "content": "Take on the role of an expert in psychiatric diagnosis using the DSM 5. Read the following transcript and determine if the patient has depression."
        },
        {
            "role": "user",
            "content": full_transcript
        }
    ]

    # Run GPT to get the binary output
    binary_gpt_output = client.chat.completions.create(
        model=GPT_MODEL,
        messages=messages
    )

    # Parse the GPT output
    gpt_output = json.loads(binary_gpt_output.choices[0].message.content)["diagnosis"]

    # Determine the final diagnosis string
    final_str_diagnosis = "Not Depressed" if gpt_output == "not depressed" else "Depressed"

    # Convert the final diagnosis string to a binary integer
    int_final = 0 if final_str_diagnosis == "Not Depressed" else 1

    return int_final