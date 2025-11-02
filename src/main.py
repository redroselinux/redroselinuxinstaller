#!/usr/bin/env python3
import curses
import subprocess
import urllib.request

def run(cmd):
    subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def download_file(url, path):
    urllib.request.urlretrieve(url, path)

def ask_input(stdscr, prompt):
    curses.echo()
    stdscr.addstr(prompt)
    value = stdscr.getstr().decode().strip()
    curses.noecho()
    return value

def disk_selection(stdscr):
    curses.curs_set(1)
    stdscr.clear()
    stdscr.addstr(0, 0, "Redrose Installer - Disk Selection\n")
    stdscr.addstr(1, 0, "Available disks:\n")
    lsblk_output = subprocess.check_output("lsblk", shell=True).decode()
    stdscr.addstr(2, 0, lsblk_output + "\n")
    return ask_input(stdscr, "\nEnter the target disk (e.g., /dev/sda): ")

def get_user_info(stdscr):
    curses.curs_set(1)
    stdscr.clear()
    username = ask_input(stdscr, "Enter your username: ")
    hostname = ask_input(stdscr, "Enter your hostname: ")
    root_password = ask_input(stdscr, "Enter root password: ")
    user_password = ask_input(stdscr, f"Enter password for {username}: ")
    return username, hostname, root_password, user_password

def partition_and_format(disk):
    run(f"sgdisk -Z {disk}")
    run(f"sgdisk -n1:0:+512M -t1:EF00 {disk}")
    run(f"sgdisk -n2:0:0 -t2:8300 {disk}")
    run(f"mkfs.fat -F32 {disk}1")
    run(f"mkfs.ext4 {disk}2")
    run(f"mount {disk}2 /mnt")
    run("mkdir -p /mnt/boot")
    run(f"mount {disk}1 /mnt/boot")

def pacstrap_base_system():
    run("pacstrap /mnt base base-devel linux linux-firmware git wget curl")

def gen_fstab():
    run("genfstab -U /mnt >> /mnt/etc/fstab")

def chroot(cmd):
    run(f"arch-chroot /mnt /bin/bash -c \"{cmd}\"")

def setup_system(username, hostname, root_pw, user_pw):
    chroot(f"echo root:{root_pw} | chpasswd")
    chroot(f"echo {hostname} > /etc/hostname")
    chroot(f"useradd -m -G wheel {username}")
    chroot(f"echo '{username}:{user_pw}' | chpasswd")
    chroot(f"echo '{username} ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers")

def install_packages_and_config(username):
    chroot("pacman -S --noconfirm i3-wm i3status i3lock alacritty lightdm lightdm-gtk-greeter firefox feh python-pip nuitka")
    chroot("pip install --break-system-packages crust-shell")

    chroot(f"mkdir -p /home/{username}/.config/i3")
    download_file("https://raw.githubusercontent.com/redroselinux/i4/main/i3/config", f"/mnt/home/{username}/.config/i3/config")
    chroot(f"chown -R {username}:{username} /home/{username}/.config/i3")

    download_file("https://crust-project.w3spaces.com/redrose.png", f"/mnt/home/{username}/redrose.png")
    chroot(f"chown {username}:{username} /home/{username}/redrose.png")
    with open(f"/mnt/home/{username}/.config/i3/config", "a") as f:
        f.write(f"\nexec_always --no-startup-id feh --bg-scale /home/{username}/redrose.png\n")

    with open(f"/mnt/home/{username}/.bashrc", "a") as f:
        f.write("\ncrust\nexit\n")

def install_car(username):
    chroot(f"sudo -u {username} git clone https://github.com/redroselinux/car /home/{username}/car")
    chroot(f"cd /home/{username}/car/src && nuitka --onefile main.py")
    chroot(f"mv /home/{username}/car/src/main.bin /usr/bin/car && chmod +x /usr/bin/car")
    chroot(f"sudo -u {username} car init")

def enable_services():
    chroot("systemctl enable lightdm")

def show_beta_message(username):
    chroot(f"if [ ! -f /home/{username}/.redrose_beta_seen ]; then echo 'Welcome to Redrose Linux Beta build!' && touch /home/{username}/.redrose_beta_seen; fi")

def main(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    stdscr.addstr(0, 0, "Redrose Linux Installer (Beta) \nPress Enter to continue")
    stdscr.getch()

    disk = disk_selection(stdscr)
    username, hostname, root_pw, user_pw = get_user_info(stdscr)

    stdscr.addstr(15, 0, "Partitioning and formatting disk...")
    stdscr.refresh()
    partition_and_format(disk)

    stdscr.addstr(16, 0, "Installing base system...")
    stdscr.refresh()
    pacstrap_base_system()
    gen_fstab()

    stdscr.addstr(17, 0, "Configuring system...")
    stdscr.refresh()
    setup_system(username, hostname, root_pw, user_pw)

    stdscr.addstr(18, 0, "Installing packages and configuration...")
    stdscr.refresh()
    install_packages_and_config(username)

    stdscr.addstr(19, 0, "Installing Car...")
    stdscr.refresh()
    install_car(username)

    enable_services()
    show_beta_message(username)

    stdscr.addstr(20, 0, "Installation complete. Reboot to start Redrose.")
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)
