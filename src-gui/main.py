#!/usr/bin/env python3
import subprocess
import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf

# remove for production
debug = True

class Installer(Gtk.Window):
    def __init__(self):
        self.selected_locale = None
        self.step = 1
        super().__init__()
        self.set_default_size(800, 600)

        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
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
            "This installer will guide you on installing Redrose Linux.</span>"
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
            self.main_title.set_markup("<span size='xx-large' weight='bold'>What username do you want to use?</span>")
            self.description.set_text(
                "You will set your password in the next step."
            )
            self.input = Gtk.Entry()
            self.main_box.pack_start(self.input, False, False, 0)
            self.main_box.reorder_child(self.input, 3)
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
            self.radio2 = Gtk.RadioButton.new_with_label_from_widget(self.radio1, "Keep Testing")
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
