"""Generates an HTML report using binary diagnosis, ChatGPT diagnosis, full transcript, recording ID, and date."""
import datapane as dp
from typing import Any

def generate_report_util(binary_diagnosis: int, chatgpt_diagnosis: Any, date: str, summary: str, patient_name: str) -> dp.Report:
    """
    Generates an HTML report for the patient using the provided data.

    Args:
        binary_diagnosis (int): The binary diagnosis (0 for Not Depressed, 1 for Depressed).
        chatgpt_diagnosis (Any): The diagnosis generated by ChatGPT.
        date (str): The date of the report.
        summary (str): The summary of the report.
        patient_name (str): The name of the patient.

    Returns:
        dp.Report: The generated HTML report.
    """
    # Define the CSS styles and initial HTML content
    title = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');
        h1 {
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            font-size: 2.5em;
            line-height: 1.2;
            color: #000;
            text-align: center;
            margin: 0;
            padding: 0;
        }
        h2 {
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            text-align: center;
            margin: 0;
            margin-top: 0.3em;
        }
        .bg-white.relative.z-40 {
            height: 5px;
        }
    </style>
    """

    # Determine the diagnosis string based on the binary diagnosis
    string_output = "Not Depressed" if binary_diagnosis == 0 else "Depressed"
    
    # Add the patient name, date, and summary to the HTML content
    title += f"<h1 style=\"padding: 0; margin: 0;\">{patient_name} Clinical Interview Report</h1>\n"
    title += f"<h2>{date}</h2>\n"
    title += f"<p style=\"text-align: center; max-width: 700px; margin:auto; margin-top: 1em; margin-bottom: 0.1em;\">{summary}</p>\n"

    # Create the report using Datapane
    report = dp.Report(
        dp.HTML(title),
        dp.Group(
            dp.BigNumber(heading="Audio-Visual-Textual Confidence", value="100%"),
            dp.BigNumber(heading="Textual Confidence", value=f"{int(chatgpt_diagnosis == binary_diagnosis) * 100}%"),
            columns=2,
        ),
        dp.BigNumber(heading="Diagnosis", value=string_output),
    )

    # Return the generated report
    return report