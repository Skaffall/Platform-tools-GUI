#!/usr/bin/env python3
import os
import sys
import shutil
import platform
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

IS_WINDOWS = platform.system() == "Windows"


class ADBFastbootGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ADB & Fastboot Toolbox (Linux / Windows)")
        self.geometry("1000, 720")
        self.minsize(850, 600)

        self.custom_platform_tools_dir = ""

        self._init_layout()
        self._detect_binaries()

    def _init_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

      
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Platform Tools GUI",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.status_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="ADB: Checking...\nFastboot: Checking...",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            justify="center"
        )
        self.status_label.grid(row=1, column=0, padx=10, pady=5)

        self.btn_select_dir = ctk.CTkButton(
            self.sidebar_frame,
            text="Select folder bin",
            command=self._choose_platform_tools_dir,
            font=ctk.CTkFont(size=12)
        )
        self.btn_select_dir.grid(row=2, column=0, padx=20, pady=5)

        self.btn_refresh_devices = ctk.CTkButton(
            self.sidebar_frame,
            text="Update list devices",
            fg_color="#2b8a3e",
            hover_color="#237032",
            command=self.refresh_devices
        )
        self.btn_refresh_devices.grid(row=3, column=0, padx=20, pady=10)

        self.btn_kill_server = ctk.CTkButton(
            self.sidebar_frame,
            text="Restart ADB Servers",
            fg_color="#d6336c",
            hover_color="#a61e4d",
            command=self.restart_adb_server
        )
        self.btn_kill_server.grid(row=4, column=0, padx=20, pady=5)

        # Блок переключения тем
        self.theme_label = ctk.CTkLabel(self.sidebar_frame, text="Interface Theme:", anchor="w")
        self.theme_label.grid(row=8, column=0, padx=20, pady=(10, 0))
        self.theme_switch = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["Dark", "Light", "System"],
            command=self._change_appearance_mode
        )
        self.theme_switch.grid(row=9, column=0, padx=20, pady=(5, 20))

        # Основная рабочая область
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Вкладки действий
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

        self.tab_adb = self.tabview.add("Commands ADB")
        self.tab_fastboot = self.tabview.add("Commands Fastboot")
        self.tab_files = self.tabview.add("Files and Programms")
        self.tab_info = self.tabview.add("Device Info")
        self.tab_terminal = self.tabview.add("Direct Terminal")

        self._setup_adb_tab()
        self._setup_fastboot_tab()
        self._setup_files_tab()
        self._setup_info_tab()
        self._setup_terminal_tab()

        # Консоль вывода логов
        self.console_frame = ctk.CTkFrame(self.main_frame)
        self.console_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.console_frame.grid_rowconfigure(1, weight=1)
        self.console_frame.grid_columnconfigure(0, weight=1)

        self.console_header_frame = ctk.CTkFrame(self.console_frame, fg_color="transparent")
        self.console_header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        self.console_header_frame.grid_columnconfigure(0, weight=1)

        self.console_title = ctk.CTkLabel(
            self.console_header_frame,
            text="Logs (Console / Logs):",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.console_title.grid(row=0, column=0, sticky="w")

        self.clear_btn = ctk.CTkButton(
            self.console_header_frame,
            text="Clear Logs",
            width=90,
            height=24,
            command=self.clear_console
        )
        self.clear_btn.grid(row=0, column=1, padx=5)

        self.textbox = ctk.CTkTextbox(self.console_frame, wrap="char", font=ctk.CTkFont(family="Consolas", size=12))
        self.textbox.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    def _setup_adb_tab(self):
        frame = self.tab_adb
        frame.grid_columnconfigure((0, 1, 2), weight=1)

        lbl = ctk.CTkLabel(frame, text="Manage poweroff and Restart:", font=ctk.CTkFont(weight="bold"))
        lbl.grid(row=0, column=0, columnspan=3, pady=(5, 10), sticky="w")

        btn_reboot = ctk.CTkButton(frame, text="Restart (regular)", command=lambda: self.run_command(["adb", "reboot"]))
        btn_reboot.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        btn_recovery = ctk.CTkButton(frame, text="Reboot Recovery", command=lambda: self.run_command(["adb", "reboot", "recovery"]))
        btn_recovery.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        btn_bootloader = ctk.CTkButton(frame, text="Reboot Bootloader", command=lambda: self.run_command(["adb", "reboot", "bootloader"]))
        btn_bootloader.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

        btn_edl = ctk.CTkButton(frame, text="Reboot EDL (Qualcomm)", fg_color="#e03131", hover_color="#c92a2a", command=lambda: self.run_command(["adb", "reboot", "edl"]))
        btn_edl.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        btn_sideload = ctk.CTkButton(frame, text="Reboot Sideload", command=lambda: self.run_command(["adb", "reboot", "sideload"]))
        btn_sideload.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        btn_fastbootd = ctk.CTkButton(frame, text="Reboot Fastbootd", command=lambda: self.run_command(["adb", "reboot", "fastboot"]))
        btn_fastbootd.grid(row=2, column=2, padx=5, pady=5, sticky="ew")

        lbl_ops = ctk.CTkLabel(frame, text="Fast Actions ADB:", font=ctk.CTkFont(weight="bold"))
        lbl_ops.grid(row=3, column=0, columnspan=3, pady=(15, 10), sticky="w")

        btn_screenshot = ctk.CTkButton(frame, text="Screenshot PC", command=self.take_screenshot)
        btn_screenshot.grid(row=4, column=0, padx=5, pady=5, sticky="ew")

        btn_logcat = ctk.CTkButton(frame, text="See last 100 of logcat", command=lambda: self.run_command(["adb", "logcat", "-t", "100"]))
        btn_logcat.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        btn_root = ctk.CTkButton(frame, text="ADB Root (if supports)", command=lambda: self.run_command(["adb", "root"]))
        btn_root.grid(row=4, column=2, padx=5, pady=5, sticky="ew")

    def _setup_fastboot_tab(self):
        frame = self.tab_fastboot
        frame.grid_columnconfigure((0, 1, 2), weight=1)

        lbl = ctk.CTkLabel(frame, text="Manage mods of Fastboot:", font=ctk.CTkFont(weight="bold"))
        lbl.grid(row=0, column=0, columnspan=3, pady=(5, 10), sticky="w")

        btn_devices = ctk.CTkButton(frame, text="Fastboot Devices", command=lambda: self.run_command(["fastboot", "devices"]))
        btn_devices.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        btn_reboot_fb = ctk.CTkButton(frame, text="Restart into system", command=lambda: self.run_command(["fastboot", "reboot"]))
        btn_reboot_fb.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        btn_reboot_rec = ctk.CTkButton(frame, text="Reboot into Recovery", command=lambda: self.run_command(["fastboot", "reboot", "recovery"]))
        btn_reboot_rec.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

        lbl_unlock = ctk.CTkLabel(frame, text="Unlock Bootloader (Attention:All files are been destroyed!):", font=ctk.CTkFont(weight="bold"))
        lbl_unlock.grid(row=2, column=0, columnspan=3, pady=(15, 5), sticky="w")

        btn_unlock = ctk.CTkButton(frame, text="flashing unlock", fg_color="#c92a2a", hover_color="#a61e4d", command=lambda: self.confirm_action(["fastboot", "flashing", "unlock"], "Вы уверены, что хотите разблокировать загрузчик?"))
        btn_unlock.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

        btn_unlock_oem = ctk.CTkButton(frame, text="oem unlock (legacy)", fg_color="#c92a2a", hover_color="#a61e4d", command=lambda: self.confirm_action(["fastboot", "oem", "unlock"], "Вы уверены, что хотите разблокировать загрузчик?"))
        btn_unlock_oem.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        btn_lock = ctk.CTkButton(frame, text="flashing lock", fg_color="#862e9c", hover_color="#6f2282", command=lambda: self.confirm_action(["fastboot", "flashing", "lock"], "Вы уверены, что хотите заблокировать загрузчик?"))
        btn_lock.grid(row=3, column=2, padx=5, pady=5, sticky="ew")

        lbl_flash = ctk.CTkLabel(frame, text="Flash partitions (Flash image):", font=ctk.CTkFont(weight="bold"))
        lbl_flash.grid(row=4, column=0, columnspan=3, pady=(15, 5), sticky="w")

        self.partition_var = ctk.StringVar(value="boot")
        self.partition_menu = ctk.CTkOptionMenu(frame, values=["boot", "recovery", "system", "vendor", "vbmeta", "userdata"], variable=self.partition_var)
        self.partition_menu.grid(row=5, column=0, padx=5, pady=5, sticky="ew")

        btn_flash_img = ctk.CTkButton(frame, text="Select file of .img and flash", command=self.flash_partition)
        btn_flash_img.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

        btn_boot_img = ctk.CTkButton(frame, text="Boot .img (Download without Firmware)", command=self.fastboot_boot_image)
        btn_boot_img.grid(row=5, column=2, padx=5, pady=5, sticky="ew")

    def _setup_files_tab(self):
        frame = self.tab_files
        frame.grid_columnconfigure((0, 1), weight=1)

        lbl = ctk.CTkLabel(frame, text="Install Applications (APK):", font=ctk.CTkFont(weight="bold"))
        lbl.grid(row=0, column=0, columnspan=2, pady=(5, 10), sticky="w")

        btn_install_apk = ctk.CTkButton(frame, text="Install APK (adb install -r)", command=self.install_apk)
        btn_install_apk.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        btn_sideload_zip = ctk.CTkButton(frame, text="Set OTA/Update (adb sideload)", command=self.adb_sideload_file)
        btn_sideload_zip.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        lbl_transfer = ctk.CTkLabel(frame, text="Pull Files (Push / Pull):", font=ctk.CTkFont(weight="bold"))
        lbl_transfer.grid(row=2, column=0, columnspan=2, pady=(15, 10), sticky="w")

        btn_push = ctk.CTkButton(frame, text="Upload files to phone (/sdcard/Download/)", command=self.push_file)
        btn_push.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

        btn_pull = ctk.CTkButton(frame, text="Download File from phone (set path)", command=self.pull_file)
        btn_pull.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

    def _setup_info_tab(self):
        frame = self.tab_info
        frame.grid_columnconfigure((0, 1, 2), weight=1)

        lbl = ctk.CTkLabel(frame, text="Get Info abot Android device:", font=ctk.CTkFont(weight="bold"))
        lbl.grid(row=0, column=0, columnspan=3, pady=(5, 10), sticky="w")

        btn_props = ctk.CTkButton(frame, text="Model and specifications", command=lambda: self.run_command(["adb", "shell", "getprop", "ro.product.model"]))
        btn_props.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        btn_android_ver = ctk.CTkButton(frame, text="Version Android / SDK", command=lambda: self.run_command(["adb", "shell", "getprop", "ro.build.version.release"]))
        btn_android_ver.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        btn_battery = ctk.CTkButton(frame, text="Bataree Status", command=lambda: self.run_command(["adb", "shell", "dumpsys", "battery"]))
        btn_battery.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

        btn_wm_size = ctk.CTkButton(frame, text="Resolution and DPI", command=lambda: self.run_command(["adb", "shell", "wm", "size"]))
        btn_wm_size.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        btn_ip = ctk.CTkButton(frame, text="IP adresses (IP)", command=lambda: self.run_command(["adb", "shell", "ip", "addr", "show"]))
        btn_ip.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        btn_meminfo = ctk.CTkButton(frame, text="Memory (cat /proc/meminfo)", command=lambda: self.run_command(["adb", "shell", "cat", "/proc/meminfo"]))
        btn_meminfo.grid(row=2, column=2, padx=5, pady=5, sticky="ew")

    def _setup_terminal_tab(self):
        frame = self.tab_terminal
        frame.grid_columnconfigure(0, weight=1)

        lbl = ctk.CTkLabel(frame, text="Fast run command:", font=ctk.CTkFont(weight="bold"))
        lbl.grid(row=0, column=0, pady=(5, 5), sticky="w")

        self.custom_cmd_entry = ctk.CTkEntry(frame, placeholder_text="for example: adb shell pm list packages -3  ИЛИ  fastboot getvar all")
        self.custom_cmd_entry.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.custom_cmd_entry.bind("<Return>", lambda event: self._execute_custom_command())

        btn_run = ctk.CTkButton(frame, text="run command", command=self._execute_custom_command)
        btn_run.grid(row=2, column=0, sticky="e", padx=5, pady=5)

    def _detect_binaries(self):
        adb_found = self._resolve_binary("adb") is not None
        fastboot_found = self._resolve_binary("fastboot") is not None

        adb_status = "OK" if adb_found else "Not Found"
        fb_status = "OK" if fastboot_found else "Not Found"

        self.status_label.configure(
            text=f"ADB: {adb_status}\nFastboot: {fb_status}",
            text_color="#40c057" if (adb_found and fastboot_found) else "#fa5252"
        )

    def _resolve_binary(self, binary_name):
        exe_suffix = ".exe" if IS_WINDOWS else ""
        bin_with_ext = binary_name + exe_suffix

        if self.custom_platform_tools_dir:
            custom_path = os.path.join(self.custom_platform_tools_dir, bin_with_ext)
            if os.path.isfile(custom_path) and os.access(custom_path, os.X_OK):
                return custom_path

        local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "platform-tools", bin_with_ext)
        if os.path.isfile(local_path) and os.access(local_path, os.X_OK):
            return local_path

        path_in_sys = shutil.which(binary_name)
        return path_in_sys

    def _choose_platform_tools_dir(self):
        dir_path = filedialog.askdirectory(title="Select folder of  platform-tools")
        if dir_path:
            self.custom_platform_tools_dir = dir_path
            self._detect_binaries()
            self.log_message(f"Selected user folder platform-tools: {dir_path}")

    def _change_appearance_mode(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def log_message(self, text: str):
        self.textbox.insert(tk.END, text + "\n")
        self.textbox.see(tk.END)

    def clear_console(self):
        self.textbox.delete("1.0", tk.END)

    def run_command(self, cmd_args, callback_on_finish=None):
        binary = cmd_args[0]
        resolved = self._resolve_binary(binary)

        if not resolved:
            self.log_message(f"ERROR: File '{binary}' not found into PATH or selected folder!")
            messagebox.showerror("ERROR", f"File {binary} Not Found. select path to platform-tools.")
            return

        full_command = [resolved] + cmd_args[1:]

        def worker():
            display_cmd = " ".join(cmd_args)
            self.log_message(f"\n[RUN] > {display_cmd}")

            try:
                creation_flags = 0
                if IS_WINDOWS:
                    creation_flags = subprocess.CREATE_NO_WINDOW

                proc = subprocess.Popen(
                    full_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=creation_flags,
                    encoding="utf-8",
                    errors="replace"
                )

                stdout, stderr = proc.communicate()

                if stdout:
                    self.log_message(stdout.strip())
                if stderr:
                    self.log_message(f"[STDERR]: {stderr.strip()}")

                self.log_message(f"[DONE] Code finish: {proc.returncode}")

                if callback_on_finish:
                    self.after(0, lambda: callback_on_finish(proc.returncode, stdout, stderr))

            except Exception as e:
                self.log_message(f"[ERROR]: {str(e)}")

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def confirm_action(self, cmd, prompt):
        if messagebox.askyesno("Confirm", prompt):
            self.run_command(cmd)

    def refresh_devices(self):
        self.log_message("--- Scan devices ADB & Fastboot ---")
        self.run_command(["adb", "devices", "-l"])
        self.run_command(["fastboot", "devices"])

    def restart_adb_server(self):
        self.run_command(["adb", "kill-server"], callback_on_finish=lambda rc, o, e: self.run_command(["adb", "start-server"]))

    def take_screenshot(self):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png")],
            initialfile="screenshot.png"
        )
        if not save_path:
            return

        def on_screencap_done(rc, out, err):
            if rc == 0:
                self.run_command(["adb", "pull", "/sdcard/gui_screenshot.png", save_path],
                                 callback_on_finish=lambda r, o, e: self.run_command(["adb", "shell", "rm", "/sdcard/gui_screenshot.png"]))

        self.run_command(["adb", "shell", "screencap", "-p", "/sdcard/gui_screenshot.png"], callback_on_finish=on_screencap_done)

    def install_apk(self):
        apk_path = filedialog.askopenfilename(filetypes=[("Android Package", "*.apk")])
        if apk_path:
            self.run_command(["adb", "install", "-r", apk_path])

    def adb_sideload_file(self):
        zip_path = filedialog.askopenfilename(filetypes=[("ZIP archive", "*.zip")])
        if zip_path:
            self.run_command(["adb", "sideload", zip_path])

    def push_file(self):
        source = filedialog.askopenfilename(title="Select file to Send ")
        if source:
            dest = "/sdcard/Download/" + os.path.basename(source)
            self.run_command(["adb", "push", source, dest])

    def pull_file(self):
        dialog = ctk.CTkInputDialog(text="Type full Path to  files on device:", title="ADB Pull")
        device_path = dialog.get_input()
        if device_path:
            save_dest = filedialog.askdirectory(title="Select  Files to PC for save")
            if save_dest:
                self.run_command(["adb", "pull", device_path.strip(), save_dest])

    def flash_partition(self):
        partition = self.partition_var.get()
        img_path = filedialog.askopenfilename(filetypes=[("Image files", "*.img;*.bin")])
        if img_path:
            if messagebox.askyesno("Confirm firmware", f"Are you want flash:\nPartitions: {partition}\nFile: {img_path}?"):
                self.run_command(["fastboot", "flash", partition, img_path])

    def fastboot_boot_image(self):
        img_path = filedialog.askopenfilename(filetypes=[("Boot Image", "*.img")])
        if img_path:
            self.run_command(["fastboot", "boot", img_path])

    def _execute_custom_command(self):
        raw = self.custom_cmd_entry.get().strip()
        if not raw:
            return

        parts = raw.split()
        first = parts[0].lower()

        if first in ["adb", "fastboot"]:
            self.run_command(parts)
        else:
            self.run_command(["adb"] + parts)


if __name__ == "__main__":
    app = ADBFastbootGUI()
    app.mainloop()
