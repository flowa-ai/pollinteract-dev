import re

from .funcs import Functions

prompt_store: str = ""

def model_append(model: object, content: str, role: str) -> object:
    if role not in ["user", "assistant"]:
        role = "system"
    model.messages.append({"role": role, "content": content})
    return model

function_keys: dict[str, object] = {
    "get_user": Functions.get_user,
    "get_time": Functions.get_time,
    "get_date": Functions.get_date,

    "find_file": Functions.find_file,
    "file_exists": Functions.file_exists,
    
    "list_files": Functions.list_files,
    "list_directory": Functions.list_directory,
    
    "make_file": Functions.make_file,
    "read_file": Functions.read_file,
    "copy_file": Functions.copy_file,
    "move_file": Functions.move_file,
    "write_file": Functions.write_file,
    "rename_file": Functions.rename_file,
    "delete_file": Functions.delete_file,
    "append_file": Functions.append_file,
    
    "get_file_size": Functions.get_file_size,
    "get_file_metadata": Functions.get_file_metadata,
    "get_file_extension": Functions.get_file_extension,
    "get_directory_size": Functions.get_directory_size,
    
    
    "read_file_head": Functions.read_file_head,
    "read_file_tail": Functions.read_file_tail,
    
    "search_in_file": Functions.search_in_file,
    "count_lines_in_file": Functions.count_lines_in_file,
    
    "decompress_tar": Functions.decompress_tar,
    "decompress_zip": Functions.decompress_zip,
    "compress_to_tar": Functions.compress_to_tar,
    "compress_to_zip": Functions.compress_to_zip,
    
    "create_directory": Functions.create_directory,
    "delete_directory": Functions.delete_directory,
    
    "http_get": Functions.http_get,
    "http_post": Functions.http_post,
    
    "search_files_by_name": Functions.search_files_by_name,
    "search_files_by_extension": Functions.search_files_by_extension,
    
    "run_python": Functions.run_python,
    "iterative_code_self_prompt": Functions.iterative_code_self_prompt,
}

def parser(response):
    func_pattern = r"(\w+)\(([\s\S]*?)\)\s*!\|end_<\1>!"
    matches = re.findall(func_pattern, response)
    tokenized_functions = []
    for func, args in matches:
        arg_list = re.findall(
            r'"(.*?)(?<!\\)"|\'(.*?)(?<!\\)\'|([^\s,]+)', args, re.DOTALL
        )
        processed_args = [arg[0] or arg[1] or arg[2] for arg in arg_list]
        merged_args = []
        temp_arg = ""
        inside_string = False

        for arg in processed_args:
            if inside_string:

                temp_arg += "," + arg
                if not arg.endswith("\\") and (arg.endswith('"') or arg.endswith("'")):
                    merged_args.append(temp_arg)
                    inside_string = False
            else:
                if (arg.startswith('"') or arg.startswith("'")) and not (
                    arg.endswith('"') or arg.endswith("'")
                ):

                    temp_arg = arg
                    inside_string = True
                else:

                    merged_args.append(arg)

        unescaped_args = [
            arg.replace('\\"', '"').replace("\\'", "'") for arg in merged_args
        ]

        tokenized_functions.append([func] + unescaped_args)

    return tokenized_functions
