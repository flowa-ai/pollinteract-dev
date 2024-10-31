import matplotlib
import matplotlib.pyplot as plt

import io
import os
import base64
import requests

import pollinteract
import pollinations

pollinteract.init(
    f"You have been equipped with resources to:\n Get realtime dates, time, website articles and basic website information. Interact, view, and edit directory's files, folders, and code. As well as generate and display (in chat) images and graphs. Among other things. `Other things (If specifcally asked): {[_ if not _.startswith('__') else '' for _ in pollinteract.funcs.Functions.__dict__]}`"
)
pollinteract.logs("logs.txt")

matplotlib.use("Agg")

# --------------------------------------------------- #
# --------------------------------------------------- #
# ----------- CREATE YOUR FUNCTIONS BELOW ----------- #
# --------------------------------------------------- #
# --------------------------------------------------- #

model = pollinations.image(model=pollinations.flux, private=True, nologo=True)


def generate_image_default(prompt, filename):
    model.generate(prompt, save=True, file=filename)
    return (
        True,
        "Generated an image and it was saved to:",
        filename,
        "Prompt used: ",
        prompt,
    )


def generate_graph_or_plot(code, filename):
    buffer = io.BytesIO()
    try:
        exec(code, {"plt": plt})
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        return (
            True,
            "Generated an graph or plot was saved to:",
            filename,
            "Code used:",
            code,
        )
    except Exception:
        return (
            False,
            "Error occured in saving the file:",
            filename,
            "Code that was attempted:",
            code,
        )
    finally:
        plt.close()
        return (
            True,
            "Generated an graph or plot was saved to:",
            filename,
            "Code used:",
            code,
        )


def view_image_file_or_url(filename_or_url):
    if filename_or_url.startswith("http://") or filename_or_url.startswith("https://"):
        image_content = {
            "type": "image_url",
            "image_url": {
                "url": filename_or_url
            }
        }
    elif os.path.isfile(filename_or_url):
        with open(filename_or_url, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        image_content = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image}"
            }
        }

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image in detail that will allow general understanding for people without having to see the image."},
                image_content,
            ]
        }
    ]
    params = {
        "system": "You are an AI designed to describe images in detail so that another model can later be questioned about the image and understand what the image is. Only provide the description for the image.",
        "messages": messages
    }

    response = requests.post(f"https://{pollinations.TEXT_API}/", json=params, headers=pollinations.HEADER, timeout=30)
    if response.status_code == 200:
        try:
            response_json = response.json()
            return True, f"Image of ({filename_or_url}) description:", response_json
        except requests.exceptions.JSONDecodeError:
            return True, f"Image of ({filename_or_url}) description:", response.text
    else:
        return False, f"Failed to view/open the image ({filename_or_url})"


pollinteract.define(
    generate_image_default,
    "prompt",
    "filename",
    description="Don't use for graphs. Use context to make the prompt better.",
)
pollinteract.define(
    generate_graph_or_plot,
    "code",
    "filename",
    description="No backticks. Libs you can use: matplotlib, numpy, math, etc and builtin libraries. Provide the python code for how you could achieve what the user is trying to graph or plot. Only provide the code, nothing else. Use message context if needed. You must save it to a file instead of a pop-up. File names in the code need to relate to what you made or be exactly what the user specified. Also provide the contextual file name in the generate function. Use for all graphing and plotting requests. Don't use for images.",
)
pollinteract.define(
    view_image_file_or_url,
    "filename_or_url",
    description="This will display the image to the user in the chat as well as use a vision model to describe the image to you. That way you can understand and maintain context with images. Use for images, image files, and image urls, or if requested.",
)

image_functions = [  # Functions that will display image files in the chat when called.
    "generate_image_default",
    "generate_graph_or_plot",
    "view_image_file_or_url",
]

#  Function objects at pollinteract.funcs.Functions
#  List of functions found at pollinteract._core.code_prompt

# --------------------------------------------------- #
# --------------------------------------------------- #
# ----------- CREATE YOUR FUNCTIONS ABOVE ----------- #
# --------------------------------------------------- #
# --------------------------------------------------- #
