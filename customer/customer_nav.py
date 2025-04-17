import customtkinter as ctk
from PIL import Image
import os
from utils import load_image

class CustomerNavigationFrame(ctk.CTkFrame):
    def __init__(self, master=None, signout_command=None):
        super().__init__(master, corner_radius=0, fg_color="#1a73e8")
        
        # Configure grid layout with weight to push sign-out button to the bottom
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Load icons for navigation buttons
        icon_path = os.path.join("images", "icons")
        
        # Try to load icons, use None if not found
        self.home_image = load_image(os.path.join(icon_path, "home_icon.png"))
        self.cart_image = load_image(os.path.join(icon_path, "cart_icon.png"))
        self.orders_image = load_image(os.path.join(icon_path, "order_icon.png"))
        
        # Dashboard label
        self.navigation_label = ctk.CTkLabel(
            self, 
            text="SuperMarket", 
            font=("Arial", 20, "bold"),
            text_color="white"
        )
        self.navigation_label.grid(row=0, column=0, padx=20, pady=20)
        
        # Navigation buttons
        self.home_button = ctk.CTkButton(
            self, 
            corner_radius=0, 
            height=40, 
            border_spacing=10, 
            text="Home",
            fg_color="transparent", 
            text_color="white", 
            hover_color="#005cb2",
            image=self.home_image, 
            anchor="w", 
            command=lambda: master.show_frame("home")
        )
        self.home_button.grid(row=1, column=0, sticky="ew")
        
        self.shopping_button = ctk.CTkButton(
            self, 
            corner_radius=0, 
            height=40, 
            border_spacing=10, 
            text="Shopping",
            fg_color="transparent", 
            text_color="white", 
            hover_color="#005cb2",
            image=self.home_image, 
            anchor="w", 
            command=lambda: master.show_frame("shopping")
        )
        self.shopping_button.grid(row=2, column=0, sticky="ew")
        
        self.cart_button = ctk.CTkButton(
            self, 
            corner_radius=0, 
            height=40, 
            border_spacing=10, 
            text="Cart",
            fg_color="transparent", 
            text_color="white", 
            hover_color="#005cb2",
            image=self.cart_image, 
            anchor="w", 
            command=lambda: master.show_frame("cart")
        )
        self.cart_button.grid(row=3, column=0, sticky="ew")
        
        self.orders_button = ctk.CTkButton(
            self, 
            corner_radius=0, 
            height=40, 
            border_spacing=10, 
            text="Previous Orders",
            fg_color="transparent", 
            text_color="white", 
            hover_color="#005cb2",
            image=self.orders_image, 
            anchor="w", 
            command=lambda: master.show_frame("orders")
        )
        self.orders_button.grid(row=4, column=0, sticky="ew")
        
        # Sign Out Button
        self.signout_button = ctk.CTkButton(
            self, 
            text="Sign Out", 
            command=signout_command,
            fg_color="#ff5252",
            hover_color="#ff1744", 
            corner_radius=8
        )
        self.signout_button.grid(row=6, column=0, padx=20, pady=20, sticky="s")