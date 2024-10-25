from openai import OpenAI
from typing import Any
import numpy as np

def determine_diagnosis_string(final_diagnosis_binary):
    # Ensure final_diagnosis_binary is a scalar
    if isinstance(final_diagnosis_binary, np.ndarray):
        if final_diagnosis_binary.size == 1:
            final_diagnosis_binary = final_diagnosis_binary.item()
        else:
            raise ValueError("final_diagnosis_binary should be a scalar or an array with a single element.")

    # Determine the diagnosis string based on the binary diagnosis
    string_output = "Not Depressed" if final_diagnosis_binary == 0 else "Depressed"
    return string_output

def gpt_summary(full_transcript: str, final_diagnosis_binary: int) -> str:
    """
    Generates a summary of a clinical interview transcript using GPT.

    Args:
        full_transcript (str): The full transcript of the clinical interview.
        final_diagnosis_binary (int): The binary diagnosis (0 for Not Depressed, 1 for Depressed).

    Returns:
        str: The generated summary of the clinical interview.
    """
    # Initialize the OpenAI client
    client = OpenAI()

    # Determine the diagnosis string based on the binary diagnosis
    print("final diagnosis binary: ", final_diagnosis_binary)
    string_output = determine_diagnosis_string(final_diagnosis_binary)

    # Generate the prompt for GPT
    prompt = (
        f"Given a clinical mental health conversation transcript, generate a summary of the conversation. "
        f"The summary will be used in a clinical report. The goal of this interview was to diagnose depression. "
        f"The patient was diagnosed as \"{string_output}\"."
    )

    # Generate the summary using GPT
    summary = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": full_transcript
            }
        ]
    )

    # Return the generated summary content
    return summary.choices[0].message.content