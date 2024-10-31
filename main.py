import tkinter as tk
import customtkinter as ctk
import matplotlib.pyplot as plt

import io
import time
import random
import string
import requests
import pyperclip
import threading
import matplotlib

from customtkinter import CTkImage
from PIL import Image, ImageDraw, ImageTk

import pollinteract
import pollinations

pollinteract.init(
    f"You have been equipped with resources to:\n Get realtime dates, time, website articles and basic website information. Interact, view, and edit directory's files, folders, and code. As well as generate images and graphs. Among other things. `Other things (If specifcally asked): {[_ if not _.startswith('__') else '' for _ in pollinteract.funcs.Functions.__dict__]}`"
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


def view_image_file(filename):
    return (
        True,
        "File name:",
        filename,
        "This function only displays images, polli-vision is currently not implemented.",
        "You successfully showed it to the user.",
        "Just tell the user like here you go or here is the image or file.",
    )


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
    view_image_file,
    "filename",
    description="This will display the image to the user in the chat. Only use to display images when requested.",
)

image_fs = ["generate_image_default", "generate_graph_or_plot", "view_image_file"]

# --------------------------------------------------- #
# --------------------------------------------------- #
# ----------- CREATE YOUR FUNCTIONS ABOVE ----------- #
# --------------------------------------------------- #
# --------------------------------------------------- #

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


def fetch_response(user_input):
    has_image = False
    mmodel_r, cmodel_r = pollinteract.generate(user_input, responses=True)
    parsed = pollinteract._util.parser(cmodel_r)
    files = []
    for p in parsed:
        if p[0] in image_fs:
            files.append(p[-1])
            has_image = True
    return (mmodel_r, has_image, files)


class PolliWindow:
    def __init__(self, root: ctk.CTk):
        self.window_type = "Chat"
        self.root = root
        self.root.title("pollinations.ai")
        self.root.geometry("600x700")
        self.root.configure(bg="#000000")
        self.font = ctk.CTkFont(family="Helvetica", size=14)
        self.header_font = ctk.CTkFont(family="Helvetica", size=18, weight="bold")
        self.user_color = "#FFE801"
        self.ai_color = "#424242"
        self.text_color = "#F7F8F8"
        self.bg_color = "#000000"
        self.last_regen = None
        self.header_frame = ctk.CTkFrame(self.root, fg_color=self.bg_color)
        self.header_frame.pack(fill=tk.X, pady=(0, 0))
        try:
            logo_img = Image.open("polli_logo.png")
            logo_img.thumbnail((100, 100))
            logo_img = ImageTk.PhotoImage(logo_img)
            self.logo_label = tk.Label(
                self.header_frame, image=logo_img, bg=self.bg_color
            )
            self.logo_label.image = logo_img
            self.logo_label.pack(pady=10)
        except Exception:
            pass
        self.header_text = ctk.CTkLabel(
            self.header_frame,
            text=f"Pollinations AI {self.window_type} 🤖",
            font=self.header_font,
            text_color=self.text_color,
            fg_color=self.bg_color,
        )
        self.header_text.pack()
        self.reset_button = ctk.CTkButton(
            self.header_frame,
            text="Reset 🔄",
            font=self.font,
            fg_color="#FFE801",
            hover_color="#D4B800",
            text_color="black",
            command=self.reset_polli,
        )
        self.reset_button.pack(pady=10)
        self.main_frame = ctk.CTkFrame(self.root, fg_color=self.bg_color)
        self.main_frame.pack(fill=ctk.BOTH, expand=True)
        self.canvas = ctk.CTkCanvas(
            self.main_frame, bg=self.bg_color, highlightthickness=0
        )
        self.scrollbar = ctk.CTkScrollbar(
            self.main_frame, orientation="vertical", command=self.canvas.yview
        )
        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color=self.bg_color)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.entry_frame = ctk.CTkFrame(self.root, fg_color="#2c2c2c")
        self.entry_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.entry = ctk.CTkTextbox(
            self.entry_frame,
            font=self.font,
            fg_color="#3c3c3c",
            text_color=self.text_color,
            border_width=0,
            height=1,
            wrap="word",
        )
        self.entry.pack(fill=tk.X, padx=10, pady=10, ipady=10)
        self.entry.bind("<Return>", self.send_message)
        self.entry.bind("<Shift-Return>", self.newline)
        self.canvas.bind(
            "<Enter>",
            lambda e: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel),
        )
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))
        self.entry.bind("<Enter>", lambda e: self.canvas.unbind_all("<MouseWheel>"))
        self.entry.bind(
            "<Leave>",
            lambda e: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel),
        )
        self.messages = []
        self.was_image = False
        self.root.bind("<Configure>", self.on_resize)
        self.scroll_speed = 0

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

    def on_resize(self, event):

        self.canvas.itemconfig("all", width=self.canvas.winfo_width())

    def reset_polli(self):
        pollinteract.reset()

        self.clear_chat_history()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(0.0)

    def clear_chat_history(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.messages = []

    def send_message(self, event):

        self.root.after(1, lambda: self.entry.focus_set())

        if event.state & 0x0001:
            self.newline(event)
            return

        if self.last_regen:
            self.last_regen.destroy()
            self.last_regen = None

        user_text = self.entry.get("1.0", tk.END).strip()
        if user_text:
            self.new_message(user_text, sender="user")
            self.entry.delete("1.0", tk.END)
            threading.Thread(
                target=self.new_response, args=(user_text,), daemon=True
            ).start()

    def newline(self, event):
        self.entry.insert(tk.END, "\n")
        return "break"

    def new_response(self, user_text):
        ai_text, has_image, image_url = fetch_response(user_text)
        if has_image:
            self.was_image = True
        else:
            self.was_image = False
        self.new_message(
            ai_text,
            sender="ai",
            typing=False,
            image_url=image_url if has_image else None,
        )

    def new_message(self, text, sender="ai", typing=False, image_url=None):

        message = {"sender": sender, "text": text, "image_url": image_url}
        self.messages.append(message)

        message_frame = ctk.CTkFrame(self.scrollable_frame, fg_color=self.bg_color)
        if sender == "user":
            message_frame.pack(anchor="e", padx=10, pady=5, fill=ctk.BOTH, expand=True)
            bubble_color = self.user_color
            text_color = "#000000"
            align = "e"
        else:
            message_frame.pack(anchor="w", padx=10, pady=5, fill=ctk.BOTH, expand=True)
            bubble_color = self.ai_color
            text_color = self.text_color
            align = "w"

        bubble = ctk.CTkLabel(
            message_frame,
            text=text if text else "",
            font=self.font,
            fg_color=bubble_color,
            text_color=text_color,
            corner_radius=20,
            padx=15,
            pady=10,
            wraplength=self.root.winfo_width() // 2,
            justify=ctk.LEFT if sender == "ai" else ctk.LEFT,
        )
        bubble.pack(anchor=align, padx=5)

        if sender == "ai":
            self.typing_display(bubble, text)

        if image_url:
            self.new_image(message_frame, image_url, sender)

        regen_btn = self.reaction_buttons(message_frame, message)

        if sender == "ai" and regen_btn:
            self.last_regen = regen_btn

        self.root.after(100, lambda: self.canvas.yview_moveto(1.0))

    def new_image(self, parent_frame, image_urls, sender):
        if not isinstance(image_urls, list):
            image_urls = [image_urls]

        for image_url in image_urls:
            try:
                response = requests.get(image_url)
                img_data = response.content
                img = Image.open(io.BytesIO(img_data))
            except Exception:
                try:
                    img = Image.open(image_url)
                except Exception:
                    continue

            img.thumbnail((self.root.winfo_width() // 2, 300))
            rounded_img = self.roundify(img)

            ctk_image = CTkImage(
                light_image=rounded_img,
                dark_image=rounded_img,
                size=(rounded_img.width, rounded_img.height),
            )

            image_frame = ctk.CTkFrame(parent_frame, fg_color=self.bg_color)
            image_frame.pack(anchor="w" if sender == "ai" else "e", padx=5, pady=5)

            img_label = ctk.CTkLabel(image_frame, image=ctk_image, text="")
            img_label.image = ctk_image
            img_label.pack()

    def roundify(self, img, corner_radius=50):

        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)

        draw.rounded_rectangle(
            [0, 0, img.size[0], img.size[1]], radius=corner_radius, fill=255
        )

        rounded_img = Image.new("RGBA", img.size)
        rounded_img.paste(img, (0, 0), mask=mask)

        return rounded_img

    def typing_display(self, widget, text, delay=0.015):
        widget.configure(text="")
        words = text.split(" ")

        def animate():
            for word in words:
                if not widget.winfo_exists():
                    break

                full_text = widget.cget("text") + word + " "
                widget.configure(text=full_text)

                if any(
                    char not in set(string.ascii_letters + string.digits + " \t\n")
                    for char in word
                ):
                    delay = random.uniform(0.1, 0.2)
                else:
                    delay = random.uniform(0.01, 0.015)

                time.sleep(delay)
                self.root.update_idletasks()
                self.root.after(1, lambda: self.canvas.yview_moveto(1.0))

        threading.Thread(target=animate, daemon=True).start()

    def reaction_buttons(self, parent_frame, message):

        button_frame = ctk.CTkFrame(parent_frame, fg_color=self.bg_color)
        button_frame.pack(
            anchor="e" if message["sender"] == "user" else "w",
            padx=5,
            pady=(0, 5),
            fill="x",
        )

        button_width = 15
        button_height = 15
        button_radius = button_width // 2
        button_padding = 8

        regen_btn = None

        if message["sender"] == "ai":

            regenerate_btn = ctk.CTkButton(
                button_frame,
                text="🔄",
                width=button_width,
                height=button_height,
                corner_radius=button_radius,
                fg_color=self.bg_color,
                text_color=self.text_color,
                hover_color="#4b4b4b",
                font=ctk.CTkFont(size=16),
                command=lambda m=message: self.regenerate_response(m),
            )
            regenerate_btn.pack(side="left", padx=button_padding, pady=5)
            regen_btn = regenerate_btn

        copy_btn = ctk.CTkButton(
            button_frame,
            text="📋",
            width=button_width,
            height=button_height,
            corner_radius=button_radius,
            fg_color=self.bg_color,
            text_color=self.text_color,
            hover_color="#4b4b4b",
            font=ctk.CTkFont(size=16),
            command=lambda m=message: self.copy_response(m),
        )
        copy_btn.pack(
            side="right" if message["sender"] == "user" else "left",
            padx=button_padding,
            pady=5,
        )

        if message["sender"] == "ai":

            like_btn = ctk.CTkButton(
                button_frame,
                text="👍",
                width=button_width,
                height=button_height,
                corner_radius=button_radius,
                fg_color=self.bg_color,
                text_color=self.text_color,
                hover_color="#4b4b4b",
                font=ctk.CTkFont(size=16),
                command=lambda: self.reaction_update(like_btn, dislike_btn, "like"),
            )
            like_btn.pack(side="left", padx=button_padding, pady=5)

            dislike_btn = ctk.CTkButton(
                button_frame,
                text="👎",
                width=button_width,
                height=button_height,
                corner_radius=button_radius,
                fg_color=self.bg_color,
                text_color=self.text_color,
                hover_color="#4b4b4b",
                font=ctk.CTkFont(size=16),
                command=lambda: self.reaction_update(like_btn, dislike_btn, "dislike"),
            )
            dislike_btn.pack(side="left", padx=button_padding, pady=5)

        return regen_btn

    def reaction_update(self, like_btn, dislike_btn, current_reaction):
        color = "green" if current_reaction == "like" else "red"
        button = like_btn if current_reaction == "like" else dislike_btn
        opposite_button = like_btn if button == dislike_btn else dislike_btn

        if button.cget("text_color") == color:
            button.configure(text_color=self.text_color)
        else:
            button.configure(text_color=color)
            opposite_button.configure(text_color=self.text_color)

    def copy_response(self, message):
        if message["sender"] == "user":
            pyperclip.copy(message["text"])
        elif message["sender"] == "ai":
            if message["image_url"]:
                pyperclip.copy(message["image_url"])
            else:
                pyperclip.copy(message["text"])

    def regenerate_response(self, message):
        if message["sender"] == "ai":

            index = self.messages.index(message)

            if index > 0 and self.messages[index - 1]["sender"] == "user":

                self.remove_response(message)

                user_message = self.messages[index - 1]["text"]
                self.new_message(user_message, sender="user")
                threading.Thread(
                    target=self.new_response, args=(user_message,), daemon=True
                ).start()

    def remove_response(self, ai_message):
        if ai_message["sender"] == "ai":

            if (
                len(self.messages) >= 2
                and self.messages[-1]["sender"] == "ai"
                and self.messages[-2]["sender"] == "user"
            ):

                self.messages.pop()

                for widget in self.scrollable_frame.winfo_children()[-2:]:
                    widget.destroy()

            try:
                for _ in range(5):
                    pollinteract._core.main_model.messages.pop()
            except Exception:
                pass
            try:
                for _ in range(4):
                    pollinteract._core.code_model.messages.pop()
            except Exception:
                pass


root = ctk.CTk()
PolliWindow(root)
root.mainloop()
