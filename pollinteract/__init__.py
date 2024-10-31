"""
Interact with pollinations [https://pollinations.ai/] text models that interact with your computer.
Models come with preset functions to run, to add functions, use the pollinteract.define() method.

Example:

def my_custom_function(filename): 
    pollinteract.funcs.Functions.delete_file(filename)
    return True, "This is the output!"

pollinteract.define(my_custom_function, "filename", description="This is the description to my_custom_function. `description` is used to explain what you want the AI to do.")

-----------------------------------------------

Make sure you initialize pollinteract like so:

pollinteract.init()  # Optional: system

pollinteract.init("You are a friendly AI Assistant...")

Functions:
    init(system: str, *args, **kwargs) -> None:
        Initializes the assistant model with a system prompt to guide its behavior.

    reset(*args, **kwargs) -> tuple:
        Resets the assistant model to its initial state, clearing any accumulated 
        conversation history.

    logs(filename: str, *args, **kwargs) -> tuple[bool, str]:
        Creates or sets a log file to store the logs generated during interactions 
        with the assistant.

    define(function: object, *args, **kwargs) -> bool:
        Registers a new function within the assistant's system, allowing the assistant 
        to call and use it in response to user queries.

    generate(prompt: str, display: bool = False, verbose: bool = False, log: bool = True, responses: bool = False) -> str | tuple:
        Generates a response from the assistant based on the provided prompt. It can 
        display the response interactively, and optionally log the interaction and 
        output verbose information during the generation process. If responses
        argument is True, there will be a tuple of the main model and code model
        responses returned.


Example:

import pollinteract

pollinteract.init()
pollinteract.logs("logs.txt")

def my_custom_function(filename): 
    pollinteract.funcs.Functions.delete_file(filename)
    return True, "This is the output!"

pollinteract.define(my_custom_function, "filename")

while True:
    prompt = input("User:\n> "); print("\nPollInteract:\n> ", end="")
    pollinteract.generate(prompt=prompt, display=True, verbose=False, log=True, responses=False); print()
"""


import pollinteract._core as _core
import pollinteract._util as _util
import pollinteract.funcs as funcs

def init(system: str = "Website: https://pollinations.ai/\nYou are Polli, a friendly AI Assistant. Your role is to provide answers and perform tasks based on user queries. Do not show file content unless specifically requested to do so.", *args, **kwargs) -> None:
    """
    Initialize the assistant models with a system prompt.

    Args:
        system (str): The system prompt to set the assistant's behavior.
        *args: Additional arguments.
        **kwargs: Additional keyword arguments.
    """
    _core.model_init(system=system)

def reset(*args, **kwargs) -> tuple:
    """
    Reset the assistant model to its initial state.

    Args:
        *args: Additional arguments.
        **kwargs: Additional keyword arguments.

    Returns:
        tuple: A tuple indicating the reset result.
    """
    return _core.model_reset(*args, **kwargs)

def logs(filename: str, *args, **kwargs) -> tuple[bool, str]:
    """
    Set or create a log file to store logs from `pollinteract.generate(log=True)`

    Args:
        filename (str): The name of the log file.
        *args: Additional arguments.
        **kwargs: Additional keyword arguments.

    Returns:
        tuple[bool, str]: A tuple with a boolean indicating success and the filename.
    """
    def update() -> tuple[bool, str]:
        _core.logs_file = filename
        return True, filename
    
    if funcs.Functions.find_file(filename)[0]:
        return update()
    else:
        funcs.Functions.make_file(filename)
        if funcs.Functions.find_file(filename)[0]:
            return update()
    return False, filename

def define(function: object, *args, description: str=None, **kwargs) -> bool:
    """
    Define and register a new function within for the models to interact with and use.

    Args:
        function (object): The function object to define.
        *args: Arguments. Put all arguments that your function takes in, as well as the name. This will help guide the models.
        description (str): Describes what the funciton does.
        **kwargs: Additional keyword arguments.

    Returns:
        bool: True if the function was successfully defined.
    """
    f_name: str = function.__name__
    f_args: list[str] = []
    f_desc: str = f"  # {description}" if description is not None else ""
    for arg in args:
        f_args.append(f'"{arg}"')
        f_args.append(", ")
    f_args.pop()  # Remove last comma
    f_args_str: str = "".join(f_arg for f_arg in f_args)
    setattr(funcs.Functions, f_name, function)
    _core.code_prompt += f"- {f_name}({f_args_str})  !|end_<{f_name}>!{f_desc}\n"
    _util.function_keys[f_name] = function
    _core.code_model.system = _core.code_prompt
    return True

def generate(prompt: str, display: bool = False, verbose: bool = False, log: bool = True, responses: bool = False) -> str:
    """
    Generate a response from the assistant based on a prompt.

    Args:
        prompt (str): The user input or prompt to generate a response from.
        display (bool, optional): Whether to display the response like its being typed. Defaults to False.
        verbose (bool, optional): Whether to output additional information during generation. Defaults to False.
        log (bool, optional): Whether to log the interaction. Defaults to True.
        responses (bool, optional): Whether to send the response from the main model and code model. Defaults to False.

    Returns:
        str: The generated response from the assistant.
    """
    use_log: bool = False
    if _core.logs_file and log:
        use_log = True
        log_file = open(_core.logs_file, "a", encoding="utf-16")

    cmodel_r: str = _core.code_model.generate(prompt).text

    if verbose:
        print(f"Model successfully generated in generate({hex(id(generate))}): Prompt length({len(prompt)}) | Response length({len(cmodel_r)})")

    if use_log:
        log_file.write(f"\n{_core.logs_total} [{funcs.datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n| {repr(prompt)}\n")
        log_file.write(f"| {repr(cmodel_r)}\n")

    _util.model_append(_core.main_model, prompt, "user")
    _util.model_append(_core.main_model, cmodel_r, "assistant")
    cmodel_parse: list = _util.parser(cmodel_r)

    for index, tokenized_f in enumerate(cmodel_parse):
        try:
            f_name: str = tokenized_f[0]
            f_args: tuple = tokenized_f[1:]
            if len(f_args) > 2:
                raise Exception(f"Too many args passed in tokenized_f args. At `{index}` {f_name} with length({len(f_args)})")
            f_result: object = _util.function_keys[f_name](*f_args)
            _util.prompt_store += f"{index + 1} | {f_name} ({f_args}): ```{f_result}```\n"
        except Exception as e:
            if verbose:
                print(f"Error in generate({hex(id(generate))}): {e}")

    if verbose:
        print(_util.prompt_store)
    if use_log:
        log_file.write(f"| {repr(_util.prompt_store)}\n")

    _util.model_append(_core.code_model, _util.prompt_store, "system")
    _util.model_append(_core.main_model, _util.prompt_store, "system")

    mmodel_r: str = _core.main_model.generate(prompt, display).text

    if verbose:
        print(f"Model successfully generated in generate({hex(id(generate))}): Prompt length({len(prompt)}) | Response length({len(mmodel_r)})")
    if use_log:
        log_file.write(f"| {repr(mmodel_r)}\n")
        log_file.close()

    _util.model_append(_core.code_model, _core.SUCCESS_PROMPT.replace("<?mmodel_r!replace", mmodel_r), "assistant")
    _util.prompt_store = ""
    _core.logs_total += 1
    if responses:
        return mmodel_r, cmodel_r
    return mmodel_r
