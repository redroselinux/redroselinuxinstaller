import subprocess
import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf

# remove for production
debug = True

class Installer(Gtk.Window):
    def __init__(self):
        self.summary_box = None
        self.selected_locale = None
        self.step = 1
        super().__init__()
        self.set_default_size(800, 600)

        header = Gtk.HeaderBar()
        header.set_show_close_button(False)
        self.setup_header_buttons(header)

        header.set_has_subtitle(False)
        self.set_titlebar(header)

        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                "redroselinux.png", width=32, height=32, preserve_aspect_ratio=True
            )
            logo = Gtk.Image.new_from_pixbuf(pixbuf)
            header.pack_start(logo)
        except Exception as e:
            print("Could not load header image:", e)

        title_label = Gtk.Label()
        title_label.set_markup("<span size='large' weight='bold'>Redrose Linux Installer</span>")
        title_label.set_halign(Gtk.Align.START)
        header.pack_start(title_label)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(self.main_box)

        top_spacer = Gtk.Box()
        self.main_box.pack_start(top_spacer, True, True, 0)

        self.main_title = Gtk.Label()
        self.main_title.set_markup("<span size='xx-large' weight='bold'>Welcome to Redrose Linux</span>")
        self.main_box.pack_start(self.main_title, False, False, 0)

        self.description = Gtk.Label()
        self.description.set_markup(
            "<span size='medium'>Hello! We are glad you are installing Redrose Linux. "
            "This app will guide you on the process.</span>"
        )
        self.main_box.pack_start(self.description, False, False, 0)

        middle_spacer = Gtk.Box()
        self.main_box.pack_start(middle_spacer, True, True, 0)

        self.button = Gtk.Button(label="Continue")
        self.button.set_size_request(150, 50)
        self.button.connect("clicked", self.on_button_clicked)
        self.main_box.pack_start(self.button, False, False, 0)

    def on_button_clicked(self, widget):
        self.step += 1
        if self.step > 3:
            self.main_box.remove(self.combo)
        if self.step == 7:
            self.main_box.remove(self.input)
        if self.step == 9:
            self.main_box.remove(self.summary_box)

        if self.step == 2:
            self.main_title.set_markup("<span size='xx-large' weight='bold'>Choose your language</span>")
            self.description.set_text(
                "If you do not see your language, please report it to the maintainers."
            )

            self.combo = Gtk.ComboBoxText()
            for locale in self.get_locales():
                self.combo.append_text(locale)
            self.combo.set_active(20)

            self.main_box.pack_start(self.combo, False, False, 0)
            self.main_box.reorder_child(self.combo, 3)
            self.combo.show()
        elif self.step == 3:
            self.selected_locale = self.combo.get_active_text()
            self.main_title.set_markup("<span size='xx-large' weight='bold'>Choose your keyboard layout</span>")
            self.description.set_text(
                "If you do not see your keyboard layout, please report it to the maintainers."
            )
            for locale in self.get_keymaps():
                self.combo.append_text(locale)
        elif self.step == 4:
            self.selected_keymap = self.combo.get_active_text()
            self.main_title.set_markup("<span size='xx-large' weight='bold'>What username do you want to use?</span>")
            self.description.set_text(
                "You will set your password in the next step."
            )
            self.input = Gtk.Entry()
            self.main_box.pack_start(self.input, False, False, 0)
            self.main_box.reorder_child(self.input, 3)
            self.main_box.show_all()
        elif self.step == 5:
            self.username = self.input.get_text()
            self.main_title.set_markup("<span size='xx-large' weight='bold'>Choose a password</span>")
            self.description.set_text("Enter the user password.")
            self.input.set_text("")
            self.input.set_visibility(False)
        elif self.step == 6:
            self.user_password = self.input.get_text()
            self.main_title.set_markup("<span size='xx-large' weight='bold'>Set the root password</span>")
            self.description.set_text("Enter the root password.")
            self.input.set_text("")
            self.input.set_visibility(False)
        elif self.step == 7:
            self.combo = Gtk.ComboBoxText()
            for drive in self.get_drives():
                self.combo.append_text(drive)
            self.combo.set_active(0)
            self.main_title.set_markup("<span size='xx-large' weight='bold'>Select the target drive</span>")
            self.description.set_text("Select the drive where Redrose Linux will be installed.")
            self.main_box.pack_start(self.combo, False, False, 0)
            self.main_box.reorder_child(self.combo, 3)
            self.main_box.show_all()
        elif self.step == 8:
            self.target_drive = self.combo.get_active_text()
            self.root_password = self.input.get_text()
            self.input.set_visibility(True)
            self.input.set_text("")

            self.main_title.set_markup("<span size='xx-large' weight='bold'>Summary</span>")
            self.description.set_text(
                "Please review your selections before proceeding with the installation."
            )

            self.summary_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

            # Helper function to create a row with stock icon + label
            def summary_row(stock_icon_name, text):
                row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                icon = Gtk.Image.new_from_icon_name(stock_icon_name, Gtk.IconSize.MENU)
                label = Gtk.Label(label=text)
                label.set_xalign(0)
                row.pack_start(icon, False, False, 0)
                row.pack_start(label, True, True, 0)
                return row

            # Add summary rows with stock icons
            self.summary_box.pack_start(summary_row("preferences-desktop-locale", f"Locale: {self.selected_locale}"), False, False, 0)
            self.summary_box.pack_start(summary_row("preferences-desktop-keyboard", f"Keyboard: {self.selected_keymap}"), False, False, 0)
            self.summary_box.pack_start(summary_row("system-users", f"Username: {self.username} | Password: {'*' * len(self.user_password)}"), False, False, 0)
            self.summary_box.pack_start(summary_row("preferences-desktop-user-password", f"Root Password: {'*' * len(self.root_password)}"), False, False, 0)
            self.summary_box.pack_start(summary_row("drive-harddisk", f"Target Drive: {self.target_drive}"), False, False, 0)

            self.main_box.pack_start(self.summary_box, False, False, 0)
            self.main_box.reorder_child(self.summary_box, 3)
            self.main_box.show_all()
        else:
            self.main_title.set_markup("<span size='xx-large' weight='bold'>Installation was finished.</span>")
            self.description.set_text(
                "You can now reboot into your new installation of Redrose Linux or keep testing in the live enviroment. No changes done in the live enviroment are going to be saved. Please note that you are using the beta of Redrose Linux."
            )
            self.description.set_line_wrap(True)
            self.description.set_line_wrap_mode(Gtk.WrapMode.WORD)

            # Create a box for radio buttons
            radio_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            self.radio1 = Gtk.RadioButton.new_with_label_from_widget(None, "Reboot")
            self.radio1.set_valign(Gtk.Align.CENTER)
            self.radio1.set_halign(Gtk.Align.CENTER)
            self.radio2 = Gtk.RadioButton.new_with_label_from_widget(self.radio1, "Keep Testing")
            self.radio2.set_valign(Gtk.Align.CENTER)
            self.radio2.set_halign(Gtk.Align.CENTER)
            radio_box.pack_start(self.radio1, False, False, 0)
            radio_box.pack_start(self.radio2, False, False, 0)

            self.main_box.pack_start(radio_box, False, False, 0)
            self.main_box.reorder_child(radio_box, 3)

            self.main_box.show_all()

            # Disconnect the old signal handler
            self.button.disconnect_by_func(self.on_button_clicked)
            # Connect the new signal handler
            self.button.connect("clicked", self.finish)

    def finish(self, button):
        print("Radio1 active:", self.radio1.get_active())
        print("Radio2 active:", self.radio2.get_active())
        if self.radio1.get_active():
            if debug:
                self.destroy()
                exit()
            os.system("reboot")
        elif self.radio2.get_active():
            self.destroy()
        else:
            print("No option selected")

    def load_icon(self, filename):
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(filename, width=24, height=24, preserve_aspect_ratio=True)
            return Gtk.Image.new_from_pixbuf(pixbuf)
        except Exception as e:
            print(f"Could not load icon {filename}:", e)
            return Gtk.Image()  # Empty image fallback

    def setup_header_buttons(self, header):
        theme = "dark" if self.is_dark_theme() else "light"
        # Close
        btn_close = Gtk.Button()
        btn_close.add(self.load_icon(f"close-{theme}mode.png"))
        btn_close.connect("clicked", lambda w: self.destroy())
        header.pack_end(btn_close)
        # Maximize
        btn_max = Gtk.Button()
        btn_max.add(self.load_icon(f"maximize-{theme}mode.png"))
        btn_max.connect("clicked", lambda w: self.maximize() if not self.is_maximized() else self.unmaximize())
        header.pack_end(btn_max)
        # Minimize
        btn_min = Gtk.Button()
        btn_min.add(self.load_icon(f"minimize-{theme}mode.png"))
        btn_min.connect("clicked", lambda w: self.iconify())
        header.pack_end(btn_min)

    def is_dark_theme(self):
        # Create a temporary widget (not shown)
        templabel = Gtk.Button()
        style_context = templabel.get_style_context()
        bg_color = style_context.get_background_color(Gtk.StateFlags.NORMAL)
        r, g, b = bg_color.red, bg_color.green, bg_color.blue
        luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
        del templabel # Because 1 byte of memory is too much to waste :D
        return luminance < 0.5
    
    def get_drives(self):
        out = subprocess.check_output(["lsblk", "-dn", "-o", "NAME,SIZE,TYPE"], text=True)
        drives = []
        for line in out.splitlines():
            parts = line.split()
            if parts[2] == "disk":
                drives.append(f"{parts[0]} ({parts[1]})")
        return drives

    def get_locales(self):
        out = subprocess.check_output(["locale", "-a"], text=True)
        return out.split()
    
    def get_keymaps(self):
        keymaps = []
        try:
            with open("/usr/share/X11/xkb/rules/evdev.lst", "r") as f:
                section = None
                for line in f:
                    line = line.strip()
                    if line.startswith("!layout"):
                        section = "layout"
                        continue
                    if section == "layout" and line and not line.startswith("!"):
                        parts = line.split()
                        keymaps.append(parts[0])
            return keymaps
        except Exception as e:
            print("Error reading keymaps:", e)
            return []

if __name__ == "__main__":
    win = Installer()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
