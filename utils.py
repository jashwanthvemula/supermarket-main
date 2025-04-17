# import mysql.connector
# from config import Config
# from PIL import Image, ImageTk
# import os
# import customtkinter as ctk

# # Connect to the database
# def connect_to_database():
#     """Establish and return a connection to the MySQL database"""
#     conn = mysql.connector.connect(
#         host=Config.db_host,
#         user=Config.user,
#         password=Config.password,
#         database=Config.database,
#         auth_plugin='mysql_native_password'  # Added for MySQL 8.0+ compatibility
#     )
#     return conn

# def center_window(window, width=900, height=600):
#     """Centers a given window on the screen."""
#     screen_width = window.winfo_screenwidth()
#     screen_height = window.winfo_screenheight()
#     x = (screen_width - width) // 2
#     y = (screen_height - height) // 2
#     window.geometry(f"{width}x{height}+{x}+{y}")

# def format_currency(amount):
#     """Formats a number as currency (USD)."""
#     return f"${amount:.2f}"

# def load_image(image_path, size=(20, 20)):
#     """Loads an image from the specified path and returns a CTkImage object."""
#     if os.path.exists(image_path):
#         return ctk.CTkImage(light_image=Image.open(image_path),
#                             dark_image=Image.open(image_path), size=size)
#     else:
#         print(f"Warning: Image not found at {image_path}")
#         return None
    

import mysql.connector
from config import Config
from PIL import Image
import os
import customtkinter as ctk

def connect_to_database():
    """Establishes and returns a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(
            host=Config.db_host,
            user=Config.user,
            password=Config.password,
            database=Config.database,
            auth_plugin='mysql_native_password'
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def center_window(window, width=900, height=600):
    """Centers a given window on the screen."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

def format_currency(amount):
    """Formats a number as currency (USD)."""
    return f"${amount:.2f}"

def load_image(image_path, size=(20, 20)):
    """Loads an image from the specified path and returns a CTkImage object."""
    if os.path.exists(image_path):
        return ctk.CTkImage(light_image=Image.open(image_path),
                            dark_image=Image.open(image_path), size=size)
    else:
        print(f"Warning: Image not found at {image_path}")
        return None

def load_ctk_image(image_path, size=(900, 600)):
    """Load an image and return a CTkImage object."""
    if os.path.exists(image_path):
        try:
            image = Image.open(image_path).resize(size, Image.LANCZOS)
            return ctk.CTkImage(light_image=image, size=size)
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None
    else:
        print(f"Image not found: {image_path}")
        return None