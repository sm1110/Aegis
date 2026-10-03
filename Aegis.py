import os
import re
import time
import base64
import sqlite3
import secrets
import string
import hashlib
import hmac
import tkinter as tk
from enum import nonmember
from tkinter import messagebox

from cryptography import fernet

from Crypt import *
from Database import *
import customtkinter as ctk
import pyperclip
from cryptography.fernet import Fernet, InvalidToken

APP_NAME = "Aegis"
AUTO_LOCK_SECONDS = 180
CLIPBOARD_CLEAR_SECONDS = 20
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class Aegis(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title = "Aegis"
        self.geometry("1920x1080")
        self.minsize(1000,650)
        self.db = Database()
        self.fernet = None
        self.selected_id = None
        self.last_activity = time.time()

        self.protocol("WM_DELETE_WINDOW", self.close_app)
        self.bind_all("<Any-KeyPress>", self.update_activity)
        self.bind_all("<Any-Button>", self.update_activity)
        self.after(1000, self.check_auto_lock)
        self.show_auth_screen()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def update_activity(self, event=None):
        self.last_activity = time.time()

    def encrypt(self, text):
        return self.fernet.encrypt(text.encode())

    def decrypt(self, encrypted_data):
        return self.fernet.decrypt(encrypted_data).decode()

    def copy_secure(self, value):
        pyperclip.copy(value)
        messagebox.showinfo(
            "Copied",
            f"Clipboard will clear in",
            f"{CLIPBOARD_CLEAR_SECONDS} seconds."
        )
        self.after(CLIPBOARD_CLEAR_SECONDS*1000, self.clear_clipboard)

    def clear_clipboard(self):
        try:
            pyperclip.copy("")
        except:
            pass

    def show_auth_screen(self):
        self.clear_window()
        self.fernet=None
        self.selected_id = None

        container=ctk.CTkFrame(
            self,
            width=460,
            height=530,
            corner_radius=20
        )
        container.place(
            relx=.5,
            rely=.5,
            anchor="center"
        )
        title=ctk.CTkLabel(
            container,
            text="AEGIS 🛡️",
            font=ctk.CTkFont(
                size=50,
                weight="bold"
            )
        )
        title.pack(pady=(55,10))

        subtitle=ctk.CTkLabel(
            container,
            text="Secure Password Storage",
            text_color="gray70",
            font=ctk.CTkFont(size=15)
        )
        subtitle.pack(pady=(0,35))

        self.master_entry=ctk.CTkEntry(
            container,
            width=340,
            height=48,
            placeholder_text="Enter Master Password",
            show="❍"
        )
        self.master_entry.pack(pady=10)

        self.confirm_entry=None

        if not self.db.master_exists():
            self.confirm_entry=ctk.CTkEntry(
                container,
                width=340,
                height=48,
                placeholder_text="Renter Master Password",
                show="❍"
            )
            self.confirm_entry.pack(pady=10)
            buttont="Create Aegis"
            command=self.setup_master

        else:
            buttont = "Unlock Aegis"
            command = self.login

        button = ctk.CTkButton(
            container,
            text=buttont,
            width=340,
            height=48,
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            ),
            command=command
        )
        button.pack(pady=25)

        info=ctk.CTkLabel(
            container,
            text=(
                "AES-based authenticated encryption\n"

                "PBKDF2 key derivation • Local database"
            ),
            text_color="gray55"
        )
        info.pack()

    def setup_master(self):
        password = self.master_entry.get()
        confirm = self.confirm_entry.get()

        if len(password) < 10:
            messagebox.showinfo(
                "Weak Master Password",
                "Use atleast 10 characters"
            )
            return

        if password != confirm:
            messagebox.showinfo(
                "Password Mismatch",
                "Passwords do not match. Please Try again."
            )
            return

        salt = os.urandom(16)
        key = Crypt.derive_key(password, salt)
        verifier = Crypt.create_verifier(key)

        self.db.create_master(salt,verifier)

        messagebox.showinfo(
            "Aegis Created",
            "Aegis Is Ready To Use"
        )
        self.show_auth_screen()

    def login(self):
        password= self.master_entry.get()
        if not password:
            return
        salt , stored_verifier= self.db.get_master()
        key=Crypt.derive_key(password, salt)

        if not Crypt.verify_master(key, stored_verifier):
            messagebox.showinfo(
                "Access Denied",
                "Wrong Master Password"
            )
            self.master_entry.delete(0, "end")
            return

        self.fernet=Fernet(key)
        self.last_activity=time.time()
        self.show_dashboard()

    def show_dashboard(self):
        print("Reached")





    def check_auto_lock(self):

        if (

                self.fernet is not None

                and time.time() - self.last_activity

                >= AUTO_LOCK_SECONDS

        ):
            self.lock_vault()

        self.after(

            1000,

            self.check_auto_lock

        )

    def lock_vault(self):

        self.clear_clipboard()

        self.fernet = None

        self.selected_id = None

        self.show_auth_screen()


    def close_app(self):

        self.clear_clipboard()

        self.db.conn.close()

        self.destroy()


#Run App
if __name__ == "__main__":
    app = Aegis()
    app.mainloop()