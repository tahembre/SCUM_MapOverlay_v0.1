import tkinter as tk
from PIL import Image, ImageTk
import os

# Define images (Add more if needed)
IMAGES = {
    "GasStations": "./data/GasStations.png",
    "Abandoned Bunkers": "./data/AbandonedBunkers.png",
    "OldSchool Bunkers": "./data/BunkersOldSchool.png",
    "Points Of Interest": "./data/POI.png"
}
EYE_OPEN_SOLID_PATH = "eye_open_solid.png"
EYE_CLOSED_PATH = "eye_closed.png"
README_IMAGE_PATH = "ct-sys.png"  # Change to your actual image file

class OverlayApp:
    def __init__(self):
        self.overlay = None  # Stores overlay window
        self.overlay_images = []  # Stores references to images to prevent garbage collection

        # Create the always-on-top button window
        self.button_window = tk.Tk()
        self.button_window.overrideredirect(True)  # No borders
        self.button_window.geometry("+10+10")  # Position top-left
        self.button_window.attributes("-topmost", True)  # Always on top

        # Load the eye images
        self.eye_open_img = ImageTk.PhotoImage(Image.open(EYE_OPEN_SOLID_PATH).resize((30, 30)))
        self.eye_closed_img = ImageTk.PhotoImage(Image.open(EYE_CLOSED_PATH).resize((30, 30)))

        # Create button to toggle overlay
        self.button = tk.Button(self.button_window, image=self.eye_open_img, command=self.toggle_overlay, bg="gray")
        self.button.pack()

        # Create second button to show/hide the menu
        self.menu_button = tk.Button(self.button_window, text="Menu", command=self.toggle_menu, bg="green", fg="white")
        self.menu_button.pack(pady=5)

        # Create dropdown menu (hidden by default)
        self.menu_frame = tk.Frame(self.button_window, bg="white", borderwidth=2, relief="solid")
        self.check_vars = {name: tk.BooleanVar(value=False) for name in IMAGES}  # Checkbox states

        # Add checkboxes to menu
        for name in IMAGES:
            tk.Checkbutton(self.menu_frame, text=name, variable=self.check_vars[name], bg="white").pack(anchor="w")

        # Add apply button
        tk.Button(self.menu_frame, text="Apply", command=self.show_overlay, bg="green", fg="white").pack(fill="x")

        # Add "ReadMe / Instructions" button
        tk.Button(self.menu_frame, text="ReadMe / Instructions", command=self.show_readme, bg="gray", fg="white").pack(fill="x")

        # Add option to close the menu
        tk.Button(self.menu_frame, text="Close Menu", command=self.toggle_menu, bg="red", fg="white").pack(fill="x")

        # Allow dragging of the button window
        self.button.bind("<ButtonPress-1>", self.start_move)
        self.button.bind("<B1-Motion>", self.on_move)

    def show_readme(self):
        """ Show a dialog with an image and instructions. """
        readme_window = tk.Toplevel(self.button_window)
        readme_window.title("Instructions")
        readme_window.geometry("400x500")  # Adjust as needed
        readme_window.attributes("-topmost", True)  # Keep on top

        # Load the README image
        try:
            img = Image.open(README_IMAGE_PATH).resize((350, 150), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            img_label = tk.Label(readme_window, image=img_tk)
            img_label.image = img_tk  # Keep reference
            img_label.pack(pady=10)
        except Exception as e:
            tk.Label(readme_window, text="Image not found!", fg="red").pack()

        # Instructions text
        instructions = """
"Scum Map Overlay" by [CTsys]

IMPORTANT:
- This overlay ONLY works when the game is in borderless Fullscreen!
   - Esc-menu > Options > Video > DisplayMode > Borderless FullscreenClick

- Select map overlays to display in the menu.


- Feel free to report any errors and flaws in our discord.
--------------------------------
[𝐂𝐓ˢʸˢ]𝐓𝐡𝐞𝐁𝐥𝐮𝐞𝐎𝐧𝐞 & [𝐂𝐓ˢʸˢ]𝐭𝐢𝐤𝐫𝐞𝟗𝟏
Join our discord to stay updated on our OpenSource software:
https://discord.gg/byx88kMYdu
https://github.com/tahembre
https://github.com/tikre2910
        """

        # Add scrollable text box
        text_box = tk.Text(readme_window, wrap="word", height=10, width=80, padx=10, pady=10)
        text_box.insert("1.0", instructions)
        text_box.config(state="disabled")  # Make text read-only
        text_box.pack(padx=10, pady=5, expand=True, fill="both")

        # Close button
        tk.Button(readme_window, text="Close", command=readme_window.destroy, bg="red", fg="white").pack(pady=5)

    def toggle_menu(self):
        """ Show/hide the menu below the button. """
        if self.menu_frame.winfo_ismapped():
            self.menu_frame.pack_forget()
        else:
            self.menu_frame.pack(fill="both", expand=True)

    def toggle_overlay(self):
        """ Show/hide the overlay when the button is pressed. """
        if self.overlay and self.overlay.winfo_exists():
            self.overlay.destroy()  # Close overlay
            self.overlay = None
            self.button.config(image=self.eye_open_img)  # Change button icon back
        else:
            self.show_overlay()  # Create overlay if not already visible

    def show_overlay(self):
        """ Open the overlay and stack selected images. """
        selected_images = [IMAGES[name] for name, var in self.check_vars.items() if var.get()]

        if not selected_images:  # If no images are selected, return and do not create overlay
            print("No images selected. Overlay will not be created.")
            if self.overlay and self.overlay.winfo_exists():
                self.overlay.destroy()
            return

        # Destroy the previous overlay if it exists
        if self.overlay and self.overlay.winfo_exists():
            self.overlay.destroy()

        # Create the overlay window
        self.overlay = tk.Toplevel()
        self.overlay.overrideredirect(True)
        self.overlay.attributes("-topmost", True)

        # Transparent background
        if os.name == "nt":  # Windows
            self.overlay.wm_attributes("-transparentcolor", "black")
        else:  # Mac/Linux (partial transparency)
            self.overlay.wm_attributes("-alpha", 0.0)

        # Get screen size
        screen_width = self.overlay.winfo_screenwidth()
        screen_height = self.overlay.winfo_screenheight()
        size = min(screen_width, screen_height)  # Make it square

        # Create canvas to stack images
        canvas = tk.Canvas(self.overlay, width=size, height=size, bg="black", highlightthickness=0)
        canvas.pack()

        # Clear previous image references
        self.overlay_images.clear()

        # Stack images centered on canvas
        for img_path in selected_images:
            img = Image.open(img_path).convert("RGBA").resize((size, size), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            canvas.create_image(size // 2, size // 2, image=img_tk, anchor="center")
            self.overlay_images.append(img_tk)  # Keep reference to avoid garbage collection

        # Position overlay in the center
        x_position = (screen_width - size) // 2
        self.overlay.geometry(f"{size}x{size}+{x_position}+0")

        # Close on click
        self.overlay.bind("<Button-1>", lambda e: self.overlay.destroy())

        # Update button icon to "eye closed"
        self.button.config(image=self.eye_closed_img)

    def start_move(self, event):
        """ Store initial position for dragging. """
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        """ Move window while dragging. """
        x = self.button_window.winfo_x() + event.x - self.x
        y = self.button_window.winfo_y() + event.y - self.y
        self.button_window.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    app = OverlayApp()
    app.button_window.mainloop()
