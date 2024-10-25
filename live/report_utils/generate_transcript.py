from typing import Dict, List, Tuple

def generate_transcript(vtt_data: Dict[str, Dict[str, str]]) -> str:
    """
    Generates a full transcript from VTT data.

    Args:
        vtt_data (Dict[str, Dict[str, str]]): The VTT data containing speaker and text information.

    Returns:
        str: The full transcript as a single string.
    """
    # Initialize an empty list to store the transcript tuples
    transcript_list: List[Tuple[str, str]] = []

    # Process each entry in the VTT data
    for key in vtt_data:
        new_str = vtt_data[key]["text"].strip()
        speaker = vtt_data[key]["speaker"]

        # Capitalize the first letter of the string
        new_str = new_str[0].upper() + new_str[1:]

        # Append the speaker and text as a tuple to the transcript list
        transcript_list.append((speaker, new_str))

    # Initialize a new list to store the merged transcript
    new_transcript_list: List[Tuple[str, str]] = []

    # Merge adjacent utterances of the same speaker
    for i, (speaker, text) in enumerate(transcript_list):
        if i == 0:
            new_transcript_list.append(transcript_list[i])
        else:
            if speaker == new_transcript_list[-1][0]:
                new_transcript_list[-1] = (speaker, new_transcript_list[-1][1] + " " + text)
            else:
                new_transcript_list.append(transcript_list[i])

    # Add context for who is speaking
    for i, (speaker, text) in enumerate(new_transcript_list):
        new_transcript_list[i] = f"{speaker}: {text}"

    # Join all the entries into a single string separated by newlines
    full_transcript = "\n".join(new_transcript_list)

    return full_transcript