import customtkinter as ctk
from PIL import Image, ImageTk
from utils import connect_to_database, format_currency
import mysql.connector
import os
from tkinter import messagebox


class ShoppingFrame(ctk.CTkFrame):
    def __init__(self, master, user_id):
        super().__init__(master)
        self.master = master
        self.user_id = user_id
        self.configure(fg_color="#f0f0f0")
        self.product_frames = []  # Store references to product frames
        
        # Header frame
        self.header_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0, height=60)
        self.header_frame.pack(fill="x", pady=(0, 20))
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Available Items",
            font=("Arial", 24, "bold"),
            text_color="#1a73e8"
        )
        self.title_label.pack(side="left", padx=30, pady=10)
        
        # Search frame
        self.search_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.search_frame.pack(side="right", padx=30, pady=10)
        
        # Search entry
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Search...",
            textvariable=self.search_var,
            width=200,
            height=36,
            border_width=1,
            corner_radius=8
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        
        # Search button
        self.search_button = ctk.CTkButton(
            self.search_frame,
            text="Search",
            command=self.search_products,
            width=80,
            height=36,
            corner_radius=8,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        self.search_button.pack(side="right")
        
        # Create a scrollable frame for products
        self.products_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            width=800
        )
        self.products_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Load products
        self.load_products()
    
    def load_products(self, search_term=None):
        """Load products from the database and display them."""
        # Clear existing product frames
        for frame in self.product_frames:
            frame.destroy()
        self.product_frames = []
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor(dictionary=True)
            
            if search_term:
                query = """
                    SELECT * FROM products 
                    WHERE product_name LIKE %s OR product_category LIKE %s
                    ORDER BY product_category, product_name
                """
                search_pattern = f"%{search_term}%"
                cursor.execute(query, (search_pattern, search_pattern))
            else:
                query = "SELECT * FROM products ORDER BY product_category, product_name"
                cursor.execute(query)
            
            products = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if not products:
                # No products found
                no_products_label = ctk.CTkLabel(
                    self.products_container,
                    text="No products found",
                    font=("Arial", 16),
                    text_color="#555"
                )
                no_products_label.pack(pady=50)
                self.product_frames.append(no_products_label)
                return
            
            # Create product rows (3 products per row)
            products_per_row = 3
            current_row_frame = None
            current_row_items = 0
            
            for product in products:
                # Create a new row frame if needed
                if current_row_items % products_per_row == 0:
                    current_row_frame = ctk.CTkFrame(self.products_container, fg_color="transparent")
                    current_row_frame.pack(fill="x", pady=10)
                    self.product_frames.append(current_row_frame)
                    current_row_items = 0
                
                # Create a product frame
                product_frame = self.create_product_card(current_row_frame, product)
                product_frame.grid(row=0, column=current_row_items, padx=10, pady=10)
                
                current_row_items += 1
            
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            error_label = ctk.CTkLabel(
                self.products_container,
                text=f"Error loading products: {err}",
                font=("Arial", 14),
                text_color="red"
            )
            error_label.pack(pady=50)
            self.product_frames.append(error_label)
    
    def create_product_card(self, parent, product):
        """Create a product card widget."""
        product_id = product["product_id"]
        product_name = product["product_name"]
        product_price = product["product_price"]
        product_stock = product["stock_quantity"]
        
        # Product card frame
        product_card = ctk.CTkFrame(parent, width=240, height=320, fg_color="white", corner_radius=10)
        
        # Try to load product image
        image_frame = ctk.CTkFrame(product_card, fg_color="#f5f5f5", width=200, height=150, corner_radius=5)
        image_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")
        
        # Check if product image exists
        image_path = os.path.join("images", "products", f"{product_id}.png")
        if os.path.exists(image_path):
            try:
                product_image = Image.open(image_path)
                product_image = product_image.resize((180, 140))
                photo = ctk.CTkImage(light_image=product_image, size=(180, 140))
                image_label = ctk.CTkLabel(image_frame, image=photo, text="")
                image_label.image = photo  # Keep a reference
                image_label.place(relx=0.5, rely=0.5, anchor="center")
            except Exception as e:
                print(f"Error loading image {image_path}: {e}")
                # If image fails to load, show the product name instead
                fallback_label = ctk.CTkLabel(
                    image_frame, 
                    text=product_name,
                    font=("Arial", 14, "bold"),
                    text_color="#555"
                )
                fallback_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            # If no image exists, display text with product name
            fallback_label = ctk.CTkLabel(
                image_frame, 
                text=product_name,
                font=("Arial", 14, "bold"),
                text_color="#555"
            )
            fallback_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Product name
        name_label = ctk.CTkLabel(
            product_card,
            text=product_name,
            font=("Arial", 16, "bold"),
            text_color="#333"
        )
        name_label.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w")
        
        # Product price
        price_label = ctk.CTkLabel(
            product_card,
            text=format_currency(product_price),
            font=("Arial", 14),
            text_color="#1a73e8"
        )
        price_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        
        # Product stock
        stock_text = f"In Stock: {product_stock}" if product_stock > 0 else "Out of Stock"
        stock_color = "#4CAF50" if product_stock > 0 else "#f44336"
        
        stock_label = ctk.CTkLabel(
            product_card,
            text=stock_text,
            font=("Arial", 12),
            text_color=stock_color
        )
        stock_label.grid(row=3, column=0, padx=20, pady=5, sticky="w")
        
        # Add to cart button - disabled if out of stock
        add_to_cart_button = ctk.CTkButton(
            product_card,
            text="Add to Cart",
            command=lambda p=product: self.add_to_cart(p),
            width=200,
            height=35,
            corner_radius=8,
            fg_color="#4CAF50",
            hover_color="#388E3C",
            state="normal" if product_stock > 0 else "disabled"
        )
        add_to_cart_button.grid(row=4, column=0, padx=20, pady=(10, 20))
        
        return product_card
    
    def add_to_cart(self, product):
        """Add a product to the cart."""
        # Get quantity from user - could be enhanced with a dropdown or entry field
        quantity = 1  # Default quantity
        
        # Check if product is in stock
        if product["stock_quantity"] < quantity:
            messagebox.showerror("Out of Stock", "This product is out of stock.")
            return
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            
            # Check if the user has an active shopping cart
            cursor.execute("SELECT cart_id FROM shopping_carts WHERE user_id = %s AND status = 'active'", (self.user_id,))
            cart_result = cursor.fetchone()
            
            if cart_result:
                cart_id = cart_result[0]
            else:
                # Create a new cart
                cursor.execute(
                    "INSERT INTO shopping_carts (user_id, status, created_at) VALUES (%s, 'active', NOW())",
                    (self.user_id,)
                )
                cart_id = cursor.lastrowid
            
            # Check if the product is already in the cart
            cursor.execute(
                "SELECT quantity FROM cart_items WHERE cart_id = %s AND product_id = %s",
                (cart_id, product["product_id"])
            )
            existing_item = cursor.fetchone()
            
            if existing_item:
                # Update quantity of existing item
                new_quantity = existing_item[0] + quantity
                cursor.execute(
                    "UPDATE cart_items SET quantity = %s WHERE cart_id = %s AND product_id = %s",
                    (new_quantity, cart_id, product["product_id"])
                )
            else:
                # Add new item to cart
                cursor.execute(
                    "INSERT INTO cart_items (cart_id, product_id, quantity, added_at) VALUES (%s, %s, %s, NOW())",
                    (cart_id, product["product_id"], quantity)
                )
            
            conn.commit()
            cursor.close()
            conn.close()
            
            messagebox.showinfo("Added to Cart", f"{product['product_name']} has been added to your cart.")
            
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            messagebox.showerror("Error", f"Could not add item to cart: {err}")
    
    def search_products(self):
        """Search for products based on the search term."""
        search_term = self.search_var.get().strip()
        if search_term:
            self.load_products(search_term)
        else:
            self.load_products()  # If search is empty, load all products