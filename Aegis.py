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

from Crypt import *
from Database import *
import customtkinter as ctk
import pyperclip
from cryptography.fernet import Fernet, InvalidToken

APP_NAME = "Aegis"
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
        self.bind_all("<Any-KeyPress", self.update_activity)
        self.bind_all("<Any-Button", self.update_activity)
        self.after(1000, self.check_auto_lock)
        self.show_auth_screen()

