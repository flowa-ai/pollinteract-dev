import io
import os
import re
import sys
import pytz
import shutil
import zipfile
import tarfile
import requests
import datetime
import contextlib

from ._core import DIRECTORY, main_model, code_model


class Functions:
    def get_date(timezone):
        try:
            tz = pytz.timezone(timezone)
            date = datetime.datetime.now(tz).strftime("%Y-%m-%d")
            return date
        except Exception as e:
            return False, str(e)

    def get_time(timezone):
        try:
            tz = pytz.timezone(timezone)
            time = datetime.datetime.now(tz).strftime("%H:%M:%S")
            return time
        except Exception as e:
            return False, str(e)

    def get_user():
        try:
            return os.getlogin()
        except Exception as e:
            return False, str(e)

    def create_directory(directory_name):
        try:
            os.makedirs(directory_name, exist_ok=True)
            return True, "Directory created"
        except Exception as e:
            return False, str(e)

    def delete_directory(directory_name):
        try:
            if os.path.isdir(directory_name):
                os.rmdir(directory_name)
                return True, "Directory deleted"
            else:
                return False, "Directory does not exist"
        except Exception as e:
            return False, str(e)

    def list_directory(directory_name):
        try:
            if os.path.isdir(directory_name):
                return os.listdir(directory_name)
            else:
                return False, "Directory does not exist"
        except Exception as e:
            return False, str(e)

    def append_file(filename, content):
        try:
            with open(filename, "a", encoding="utf-16") as file:
                file.write("\n" + content.replace("\\n", "\n"))
            return True, "Content appended successfully."
        except Exception as e:
            return False, str(e)

    def list_files():
        try:
            return os.listdir()
        except Exception as e:
            return False, str(e)

    def find_file(filename):

        try:
            if os.path.isfile(filename):
                return True, f"{DIRECTORY}\\{filename}"
            return False, "File does not exist."
        except Exception as e:
            return False, e

    def copy_file(source, destination):
        try:
            shutil.copy(source, destination)
            return True, "File copied"
        except Exception as e:
            return False, str(e)

    def move_file(source, destination):
        try:
            shutil.move(source, destination)
            return True, "File moved"
        except Exception as e:
            return False, str(e)

    def file_exists(filename):
        try:
            return os.path.isfile(filename)
        except Exception as e:
            return False, str(e)

    def get_file_size(filename):
        try:
            if Functions.file_exists(filename):
                return os.path.getsize(filename)
            return False, "File does not exist"
        except Exception as e:
            return False, str(e)

    def get_file_extension(filename):
        try:
            _, extension = os.path.splitext(filename)
            return extension if extension else "No extension"
        except Exception as e:
            return False, str(e)

    def get_file_metadata(filename):
        try:
            if Functions.file_exists(filename):
                metadata = os.stat(filename)
                return {
                    "size": metadata.st_size,
                    "created": datetime.datetime.fromtimestamp(
                        metadata.st_ctime
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "modified": datetime.datetime.fromtimestamp(
                        metadata.st_mtime
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "accessed": datetime.datetime.fromtimestamp(
                        metadata.st_atime
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                }
            return False, "File does not exist"
        except Exception as e:
            return False, str(e)

    def rename_file(old_name, new_name):
        try:
            if Functions.file_exists(old_name):
                os.rename(old_name, new_name)
                return True, "File renamed"
            return False, "File does not exist"
        except Exception as e:
            return False, str(e)

    def count_lines_in_file(filename):
        try:
            if Functions.file_exists(filename):
                with open(filename, "r") as file:
                    return sum(1 for _ in file)
            return False, "File does not exist"
        except Exception as e:
            return False, str(e)

    def read_file_head(filename, lines=10):
        try:
            if Functions.file_exists(filename):
                with open(filename, "r") as file:
                    return [next(file) for _ in range(lines)]
            return False, "File does not exist"
        except Exception as e:
            return False, str(e)

    def read_file_tail(filename, lines=10):
        try:
            if Functions.file_exists(filename):
                with open(filename, "r") as file:
                    return file.readlines()[-lines:]
            return False, "File does not exist"
        except Exception as e:
            return False, str(e)

    def read_file(filename):

        try:
            if Functions.find_file(filename)[0]:
                with open(filename, "r", encoding="utf-16") as file:
                    return file.read()
            else:
                return False, "File does not exist."
        except Exception as e:
            return False, e

    def make_file(filename):

        try:
            if not Functions.find_file(filename)[0]:
                with open(filename, "w") as file:
                    file.write("")
                return True, "File created."
            else:
                return False, "File exists already."
        except Exception as e:
            return False, e

    def write_file(filename, content):
        try:
            formatted_content = content
            with open(filename, "w", encoding="utf-16") as file:
                file.write(formatted_content)
            return True
        except Exception as e:
            return False, e

    def delete_file(filename):

        try:
            if Functions.find_file(filename)[0]:
                os.remove(filename)
                return True
            else:
                return False, "File does not exist."
        except Exception as e:
            return False, e

    def compress_to_zip(source, destination):
        try:
            with zipfile.ZipFile(destination, "w") as zipf:
                if os.path.isdir(source):
                    for root, dirs, files in os.walk(source):
                        for file in files:
                            zipf.write(os.path.join(root, file))
                else:
                    zipf.write(source)
            return True, "Files compressed to ZIP"
        except Exception as e:
            return False, str(e)

    def decompress_zip(source, destination):
        try:
            with zipfile.ZipFile(source, "r") as zipf:
                zipf.extractall(destination)
            return True, "Files decompressed from ZIP"
        except Exception as e:
            return False, str(e)

    def compress_to_tar(source, destination):
        try:
            with tarfile.open(destination, "w:gz") as tarf:
                tarf.add(source, arcname=os.path.basename(source))
            return True, "Files compressed to TAR"
        except Exception as e:
            return False, str(e)

    def decompress_tar(source, destination):
        try:
            with tarfile.open(source, "r:gz") as tarf:
                tarf.extractall(destination)
            return True, "Files decompressed from TAR"
        except Exception as e:
            return False, str(e)

    def search_files_by_extension(directory, extension):
        try:
            matches = []
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(extension):
                        matches.append(os.path.join(root, file))
            return matches if matches else "No matching files found"
        except Exception as e:
            return False, str(e)

    def search_files_by_name(directory, name):
        try:
            matches = []
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if name in file:
                        matches.append(os.path.join(root, file))
            return matches if matches else "No matching files found"
        except Exception as e:
            return False, str(e)

    def http_get(url):
        try:
            response = requests.get(url)
            return (
                response.status_code,
                response.text[:200],
            )  # Limiting response to first 200 chars
        except Exception as e:
            return False, str(e)

    def http_post(url, data):
        try:
            response = requests.post(url, data=data)
            return response.status_code, response.text[:200]
        except Exception as e:
            return False, str(e)

    def search_in_file(filename, search_string, use_regex=False):
        try:
            if not os.path.isfile(filename):
                return False, "File does not exist"

            with open(filename, "r") as file:
                content = file.read()

            if use_regex:
                matches = re.findall(search_string, content)
            else:
                matches = [
                    line for line in content.splitlines() if search_string in line
                ]

            return matches if matches else "No matches found"
        except Exception as e:
            return False, str(e)

    def get_directory_size(directory):
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(directory):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
            return total_size
        except Exception as e:
            return False, str(e)

    def iterative_code_self_prompt(filename, prompt):
        msgs = 0
        if Functions.find_file(filename)[0]:
            for _ in range(3):
                code = Functions.read_file(filename)
                main_model.messages.append(main_model.system_create(code))
                main_model.messages.append(
                    main_model.system_create(
                        "Take that code, study the prompt, think through exactly what needs to be done. Then fine-tune and improve the code. Provide completed code. If you need to add more code, do so. Make it much better. Wrap the full code in backticks, ```<code>```. Explain your full thought process and think through each problem. Make sure your message stops at the last 3 backticks. (```). Don’t include the language of the code at the beginning of backticks, even if it tries. If it's a Python file, it should still only be ```print(1)``` and NOT ```python\nprint(1)```."
                    )
                )

                new_code = main_model.generate(
                    f"Provide completed code. Provide the updated code that I sent, my original prompt was: ```{prompt}```. Remember, don't include the programming language after the first 3 backticks, that breaks my code."
                ).text

                if "```" in new_code:
                    code_sections = [
                        section for section in new_code.split("```") if section.strip()
                    ]
                    if len(code_sections) > 1:
                        new_code = code_sections[1]

                code_model.messages.append(code_model.system_create(new_code.strip()))
                Functions.write_file(filename, new_code.strip())

            return (
                True,
                "File was self-prompted and written to the best of your ability.",
                new_code,
            )
        return False, "File does not exist."

    def run_python(filename): # Fix, does not work, error
        try:
            if Functions.find_file(filename)[0]:
                with open(filename, "r", encoding="utf-16") as file:
                    code = file.read()

                def custom_input(prompt=""):

                    sys.stdout = sys.__stdout__
                    user_input = input(prompt)
                    sys.stdout = output
                    return user_input

                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    local_vars = {}

                    exec(code, {"input": custom_input}, local_vars)

                full_output = output.getvalue()
                fixed_output = (
                    (full_output[:200] + "...")
                    if len(full_output) > 200
                    else full_output
                )

                def_vars = {
                    key: value
                    for key, value in local_vars.items()
                    if not (
                        key.startswith("__")
                        or callable(value)
                        or isinstance(value, type(contextlib))
                    )
                }

                return (
                    "Output from you running file:",
                    fixed_output,
                    "Globals from you running file:",
                    dict(list(def_vars.items())[:15]),
                )
            else:
                return False, "File does not exist."
        except Exception as e:
            return False, str(e)
