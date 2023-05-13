import os
import sys
from configparser import ConfigParser
from threading import Thread
from tkinter import filedialog, PhotoImage

import customtkinter as ctk
from PIL import Image
from playsound import playsound

config = ConfigParser()
ctk.set_appearance_mode("dark")
configfile = sys.path[0] + "/config.ini"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Digi-Tasbih")
        self.minsize(380, 336)
        self.wm_iconbitmap()
        self.iconphoto(True, PhotoImage(file=sys.path[0] + "/res/icon.png"))

        self.settings_window = None
        self.warn_window = None
        self.counts_window = None
        self.curr_accent_color = "DarkOliveGreen"
        self.counter = 0
        self.beep_interval = 33
        self.custom_beep_path = ""
        self.accent_colors = [
            "azure",
            "SlateBlue",
            "RoyalBlue",
            "DodgerBlue",
            "SteelBlue",
            "DeepSkyBlue",
            "SkyBlue",
            "LightSkyBlue",
            "SlateGray",
            "LightSteelBlue",
            "LightBlue",
            "LightCyan",
            "PaleTurquoise",
            "CadetBlue",
            "turquoise",
            "cyan",
            "DarkSlateGray",
            "aquamarine",
            "DarkSeaGreen",
            "SeaGreen",
            "PaleGreen",
            "SpringGreen",
            "green",
            "chartreuse",
            "OliveDrab",
            "DarkOliveGreen",
            "khaki",
            "LightGoldenrod",
            "LightYellow",
            "yellow",
            "gold",
            "goldenrod",
            "DarkGoldenrod",
            "RosyBrown",
            "IndianRed",
            "sienna",
            "burlywood",
            "wheat",
            "tan",
            "chocolate",
            "firebrick",
            "brown",
            "salmon",
            "LightSalmon",
            "orange",
            "DarkOrange",
            "coral",
            "tomato",
            "OrangeRed",
            "red",
            "DeepPink",
            "HotPink",
            "pink",
            "LightPink",
            "PaleVioletRed",
            "maroon",
            "VioletRed",
            "magenta",
            "orchid",
            "plum",
            "MediumOrchid",
            "DarkOrchid",
            "purple",
            "thistle",
        ]

        self.protocol(
            "WM_DELETE_WINDOW",
            lambda: [
                config.set("Counter", "counter", str(self.counter)),
                self.destroy(),
            ],
        )

        # Create .ini file ( if it was not created before ) to store app settings

        if not os.path.exists(configfile):
            print("Config file not found, creating new config file...")

            config.add_section("Appearance")
            config.set("Appearance", "appearance_mode", "Dark")
            config.set("Appearance", "accent_color", "DarkOliveGreen")

            config.add_section("Counter")
            config.set("Counter", "counter", "0")
            config.set("Counter", "beep_interval", "33")
            config.set("Counter", "custom_beep_path", sys.path[0] + "/res/beep.wav")

            with open(configfile, "w") as f:
                config.write(f)
                f.close()

        self.tasbih_frame = ctk.CTkFrame(
            self, fg_color=("#eeeeee", "#111111"), border_width=1
        )
        self.tasbih_frame.pack(padx=20, pady=20, expand=True)

        self.tasbih_screen = ctk.CTkButton(
            self.tasbih_frame,
            text="000000000",
            text_color=("black", "white"),
            border_width=1,
            width=300,
            font=ctk.CTkFont("Consolas", 52),
            command=self.change_counts,
        )
        self.tasbih_screen.pack(padx=20, pady=(20, 5))

        self.tasbih_count_label = ctk.CTkLabel(
            self.tasbih_frame,
            text=f"TARGET: {self.beep_interval}",
            text_color=("black", "white"),
            font=ctk.CTkFont(size=20),
        )
        self.tasbih_count_label.pack()

        self.tasbih_reset = ctk.CTkButton(
            self.tasbih_frame,
            text="↻",
            corner_radius=10,
            border_width=1,
            width=50,
            height=50,
            text_color=("black", "white"),
            font=ctk.CTkFont(size=25),
            command=self.reset_warn,
        )
        self.tasbih_reset.pack(padx=22, pady=(0, 100), side="left")

        self.tasbih_subtract = ctk.CTkButton(
            self.tasbih_frame,
            text="➖",
            corner_radius=10,
            border_width=1,
            width=50,
            height=50,
            text_color=("black", "white"),
            font=ctk.CTkFont(size=25),
            command=self.decrement,
        )
        self.tasbih_subtract.pack(padx=22, pady=(0, 100), side="right")

        self.tasbih_count = ctk.CTkButton(
            self.tasbih_frame,
            text="➕",
            corner_radius=25,
            border_width=1,
            width=150,
            height=150,
            text_color=("black", "white"),
            font=ctk.CTkFont(size=75),
            command=self.increment,
        )
        self.tasbih_count.pack(pady=(5, 20))

        self.settings_button = ctk.CTkButton(
            self.tasbih_frame,
            width=0,
            border_spacing=5,
            text="",
            command=self.open_settings,
            fg_color=("#eeeeee", "#111111"),
            hover_color=("#cccccc", "#333333"),
            image=ctk.CTkImage(
                light_image=Image.open(sys.path[0] + "/res/settings.png"),
                dark_image=Image.open(sys.path[0] + "/res/settingsdrk.png"),
                size=(20, 21),
            ),
        ).place(relx=1, rely=1, x=-37, y=-35)

        self.load_settings()

        self.counter = int(config.get("Counter", "counter"))
        self.tasbih_screen.configure(text=f"{self.counter:09}")

    def reset_warn(self):
        if self.warn_window is None or not self.warn_window.winfo_exists():
            self.warn_window = ctk.CTkToplevel(self)
            self.warn_window.attributes("-topmost", True)
            self.warn_window.geometry(
                f"300x164+{self.winfo_rootx()+10}+{self.winfo_rooty()+10}"
            )
            self.warn_window.resizable(False, False)
            self.warn_window.bind("<Escape>", lambda e: self.warn_window.destroy())

            self.warn_window.title("Warning")

            self.are_you_sure = ctk.CTkLabel(
                self.warn_window,
                text="Are you sure you want\nto reset the counter?",
                font=ctk.CTkFont(size=26),
            ).pack(padx=20, pady=20)

            self.yes_option = ctk.CTkButton(
                self.warn_window,
                text="Yes",
                height=50,
                font=ctk.CTkFont(size=26),
                command=lambda: [self.reset(), self.warn_window.destroy()],
            ).pack(side="right", padx=5, pady=5)

            self.no_option = ctk.CTkButton(
                self.warn_window,
                text="No",
                height=50,
                font=ctk.CTkFont(size=26),
                command=lambda: self.warn_window.destroy(),
            ).pack(side="left", padx=5, pady=5)

    def change_counts(self):
        if self.counts_window is None or not self.counts_window.winfo_exists():
            self.counts_window = ctk.CTkToplevel(self)
            self.counts_window.attributes("-topmost", True)
            self.counts_window.geometry(
                f"300x164+{self.winfo_rootx()+10}+{self.winfo_rooty()+10}"
            )
            self.counts_window.resizable(False, False)
            self.counts_window.bind("<Escape>", lambda e: self.counts_window.destroy())

            self.counts_window.title("Change the counter value")

            self.change_value = ctk.CTkLabel(
                self.counts_window,
                text="Change the\ncounter value",
                font=ctk.CTkFont(size=26),
            ).pack(padx=20, pady=5)

            self.confirm_option = ctk.CTkButton(
                self.counts_window,
                text="Confirm",
                height=50,
                font=ctk.CTkFont(size=26),
                command=lambda: [self.set_value(), self.counts_window.destroy()],
            )

            self.value_entry = ctk.CTkEntry(self.counts_window)
            self.value_entry.insert(0, self.counter)
            self.value_entry.pack(padx=5, pady=5, fill="x")
            self.value_entry.focus()
            self.value_entry.bind("<Return>", lambda e: self.confirm_option.invoke())

            self.confirm_option.pack(side="right", padx=5, pady=5)

            self.cancel_option = ctk.CTkButton(
                self.counts_window,
                text="Cancel",
                height=50,
                font=ctk.CTkFont(size=26),
                command=lambda: self.counts_window.destroy(),
            ).pack(side="left", padx=5, pady=5)

    def reset(self):
        self.counter = 0
        self.tasbih_screen.configure(text=f"{self.counter:09}")

    def set_value(self):
        try:
            self.counter = int(self.value_entry.get())
            self.tasbih_screen.configure(text=f"{self.counter:09}")
        except:
            print("Invalid integer.")

    def increment(self):
        self.counter += 1
        if self.counter % self.beep_interval == 0:
            Thread(target=self.play_sound).start()
        self.tasbih_screen.configure(text=f"{self.counter:09}")

    def decrement(self):
        self.counter -= 1
        if self.counter < 0:
            self.counter = 0
        self.tasbih_screen.configure(text=f"{self.counter:09}")

    def set_beep_interval(self, value):
        try:
            self.beep_interval = int(value)
            if self.beep_interval == 0:
                self.beep_interval = 33
            self.tasbih_count_label.configure(text=f"TARGET: {self.beep_interval}")
        except:
            print("Invalid integer.")

    def set_custom_beep_path(self, value):
        if os.path.isfile(value):
            self.custom_beep_path = value
        else:
            print("Not a valid file!")

    def play_sound(self):
        playsound(self.custom_beep_path)

    def open_settings(self):
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = ctk.CTkToplevel(self)

            self.settings_window.title("Settings")
            self.settings_window.resizable(False, False)
            self.settings_window.bind(
                "<Escape>", lambda e: self.settings_window.destroy()
            )

            # Apperance

            self.appearance_title = ctk.CTkLabel(
                self.settings_window, text="Appearance", font=ctk.CTkFont(size=32)
            ).pack(pady=5)

            def change_appearance_option():
                if self.appearance_setting.get():
                    ctk.set_appearance_mode("dark")
                else:
                    ctk.set_appearance_mode("light")

            self.appearance_setting = ctk.CTkSwitch(
                self.settings_window,
                text="Dim light",
                command=change_appearance_option,
            )
            if self._get_appearance_mode() == "dark":
                self.appearance_setting.toggle()
            self.appearance_setting.pack(padx=20, pady=5)

            self.colors_frame = ctk.CTkScrollableFrame(
                self.settings_window, width=280, height=280
            )
            self.colors_frame.pack(padx=5, pady=5)

            self.check_image = ctk.CTkImage(
                light_image=Image.open(sys.path[0] + "/res/checkmark.png"),
                size=(32, 32),
            )

            def create_color_option(i, color):
                self.color_setting = ctk.CTkButton(
                    self.colors_frame,
                    width=64,
                    height=64,
                    border_width=1,
                    border_color=(f"{color}3", f"{color}2"),
                    text="",
                    fg_color=(f"{color}1", f"{color}4"),
                    hover_color=(f"{color}2", f"{color}3"),
                    image=ctk.CTkImage(
                        light_image=Image.new("RGBA", (1, 1), (0, 0, 0, 0)),
                        size=(32, 32),
                    ),
                )
                self.color_setting.configure(
                    command=lambda b=self.color_setting: [
                        self.change_accent_color(color),
                        update_button(b),
                    ]
                )
                self.color_setting.grid(padx=3, pady=3, row=i >> 2, column=i % 4)

            def update_button(button):
                for i in self.colors_frame.winfo_children():
                    i.configure(
                        image=ctk.CTkImage(
                            light_image=Image.new("RGBA", (1, 1), (0, 0, 0, 0)),
                            size=(32, 32),
                        )
                    )
                button.configure(image=self.check_image)

            for i, color in enumerate(self.accent_colors):
                create_color_option(i, color)

            # Counter

            self.counter_title = ctk.CTkLabel(
                self.settings_window, text="Counter", font=ctk.CTkFont(size=32)
            ).pack(pady=5)

            self.beep_interval_label = ctk.CTkLabel(
                self.settings_window, text="Beep on intervals of:"
            ).pack()

            self.beep_interval_option = ctk.CTkComboBox(
                self.settings_window,
                values=[str(self.beep_interval), "33", "100", "1000"],
                command=self.set_beep_interval,
            )
            self.beep_interval_option.pack(pady=5)

            self.custom_beep_label = ctk.CTkLabel(
                self.settings_window, text="Beep sound:"
            ).pack()

            self.custom_beep_path_option = ctk.CTkEntry(self.settings_window)
            self.custom_beep_path_option.pack(padx=20, pady=5, fill="x")
            self.custom_beep_path_option.insert(0, self.custom_beep_path)

            self.custom_beep_path_browse = ctk.CTkButton(
                self.settings_window,
                text="Browse...",
                command=lambda: [
                    self.custom_beep_path_option.delete(0, "end"),
                    self.custom_beep_path_option.insert(
                        0,
                        filedialog.askopenfilename(
                            filetypes=[("Audio file", [".wav", ".mp3"])]
                        ),
                    ),
                    self.set_custom_beep_path(self.custom_beep_path_option.get()),
                ],
            ).pack(padx=20, pady=(0, 5), fill="x")

            self.save_settings_button = ctk.CTkButton(
                self.settings_window,
                text="Save settings",
                command=lambda: [
                    self.set_beep_interval(self.beep_interval_option.get()),
                    self.set_custom_beep_path(self.custom_beep_path_option.get()),
                    self.save_settings(),
                    self.settings_window.destroy(),
                ],
            ).pack(padx=5, pady=5, side="right")

            self.cancel_button = ctk.CTkButton(
                self.settings_window,
                text="Cancel",
                command=lambda: [
                    self.load_settings(),
                    self.settings_window.destroy(),
                ],
            ).pack(padx=5, pady=5, side="left")
        else:
            self.settings_window.focus()

    def change_accent_color(self, color):
        self.curr_accent_color = color

        self.tasbih_frame.configure(border_color=(f"{color}3", f"{color}2"))
        self.tasbih_screen.configure(
            hover_color=(f"{color}2", f"{color}3"),
            fg_color=(f"{color}1", f"{color}4"),
            border_color=(f"{color}3", f"{color}2"),
        )
        self.tasbih_reset.configure(
            hover_color=(f"{color}2", f"{color}3"),
            fg_color=(f"{color}1", f"{color}4"),
            border_color=(f"{color}3", f"{color}2"),
        )
        self.tasbih_subtract.configure(
            hover_color=(f"{color}2", f"{color}3"),
            fg_color=(f"{color}1", f"{color}4"),
            border_color=(f"{color}3", f"{color}2"),
        )
        self.tasbih_count.configure(
            hover_color=(f"{color}2", f"{color}3"),
            fg_color=(f"{color}1", f"{color}4"),
            border_color=(f"{color}3", f"{color}2"),
        )

    def load_settings(self):
        try:
            # First, read the config file
            config.read(configfile)

            # appearance_mode
            if config.get("Appearance", "appearance_mode") == "Dark":
                ctk.set_appearance_mode("dark")
            else:
                ctk.set_appearance_mode("light")
            # accent_color
            self.change_accent_color(config.get("Appearance", "accent_color"))
            # beep_interval
            self.beep_interval = int(config.get("Counter", "beep_interval"))
            self.tasbih_count_label.configure(text=f"TARGET: {self.beep_interval}")
            # custom_beep_path
            self.custom_beep_path = config.get("Counter", "custom_beep_path")

            print("Settings have been loaded.")
        except:
            print("Invalid config file!")

    def save_settings(self):
        try:
            # First, read the config file
            config.read(configfile)

            # appearance_mode
            if self._get_appearance_mode() == "dark":
                config.set("Appearance", "appearance_mode", "Dark")
            else:
                config.set("Appearance", "appearance_mode", "Light")
            # accent_color
            config.set("Appearance", "accent_color", self.curr_accent_color)
            # beep_interval
            config.set("Counter", "beep_interval", str(self.beep_interval))
            # custom_beep_path
            config.set("Counter", "custom_beep_path", self.custom_beep_path)

            # Save these changes
            with open(configfile, "w") as f:
                config.write(f)
                print("Settings saved to config file.")
                f.close()
        except:
            print("Invalid config file!")


if __name__ == "__main__":
    app = App()
    app.mainloop()

with open(configfile, "w") as f:
    config.write(f)
    print("Settings saved to config file.")
    f.close()
