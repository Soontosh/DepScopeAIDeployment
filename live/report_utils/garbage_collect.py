import os
from typing import List

def collect_garbages_dir(*dirs: str, rel: bool = True) -> None:
    """
    Removes all files and directories within the specified directories.

    Args:
        *dirs (str): The directories to clean up.
        rel (bool): If True, the directories are considered relative to the current file's directory.
    """
    if rel:
        # Get absolute directory of current file
        current_file_directory = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")

        # Append the relative directories to the current file directory
        dirs = [f"{current_file_directory}/{dir}" for dir in dirs]

    for dir in dirs:
        for root, subdirs, files in os.walk(dir):
            for file in files:
                os.remove(os.path.join(root, file))
        os.rmdir(dir)

def delete_temp() -> None:
    """
    Deletes temporary files and directories that are no longer needed.
    """
    # Get the current file directory
    current_file_directory = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")

    # Path to the temp_files directory
    temp_files = f"{current_file_directory}/temp_files"

    # Iterate over all root, dirs, files in the directory
    for root, dirs, files in os.walk(temp_files, topdown=False):
        for name in files:
            file_path = os.path.join(root, name)
            # If the file size is not greater than 500MB
            if os.path.getsize(file_path) <= 500 * 1024 * 1024:
                try: # If the file is not in use, otherwise, it will be deleted in the next run
                    os.remove(file_path)
                except:
                    pass
        for name in dirs:
            dir_path = os.path.join(root, name)
            # If the directory is empty
            if not os.listdir(dir_path):
                os.rmdir(dir_path)

def collect_garbages_file(*files: str, rel: bool = True) -> None:
    """
    Removes the specified files.

    Args:
        *files (str): The files to remove.
        rel (bool): If True, the files are considered relative to the current file's directory.
    """
    if rel:
        # Get absolute directory of current file
        current_file_directory = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")

        # Append the relative directories to the current file directory
        files = [f"{current_file_directory}/{file}" for file in files]

    for file in files:
        os.remove(file)