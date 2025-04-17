import customtkinter as ctk
from tkinter import ttk, messagebox
from utils import connect_to_database, center_window, format_currency
import mysql.connector
from PIL import Image
import os


class InventoryManagementFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.configure(fg_color="#f0f0f0")
        
        # Title and Controls Frame
        self.header_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self.header_frame.pack(fill="x", pady=(0, 20))
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Inventory Management",
            font=("Arial", 24, "bold"),
            text_color="#1a73e8"
        )
        self.title_label.pack(side="left", padx=30, pady=15)
        
        # Add Product Button
        self.add_product_button = ctk.CTkButton(
            self.header_frame,
            text="Add New Product",
            command=self.open_add_product_window,
            width=150,
            height=35,
            corner_radius=8,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        self.add_product_button.pack(side="right", padx=30, pady=15)
        
        # Main content frame
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create Treeview for displaying inventory
        self.create_inventory_table()
    
    def create_inventory_table(self):
        """Create the Treeview widget for displaying inventory."""
        # Style configuration for Treeview
        style = ttk.Style()
        style.configure("Treeview", 
                        background="#ffffff",
                        foreground="black",
                        rowheight=35,
                        fieldbackground="#ffffff",
                        borderwidth=0,
                        font=('Arial', 12))
        style.map('Treeview', background=[('selected', '#1a73e8')])
        
        # Create a frame to hold the Treeview and scrollbar
        tree_frame = ctk.CTkFrame(self.content_frame, fg_color="white", corner_radius=10)
        tree_frame.pack(fill="both", expand=True)
        
        # Create the Treeview
        self.inventory_tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Name", "Category", "Price", "Stock", "Added Date"),
            show="headings",
            height=15
        )
        
        # Define column headers
        self.inventory_tree.heading("ID", text="ID", anchor="center")
        self.inventory_tree.heading("Name", text="Product Name", anchor="center")
        self.inventory_tree.heading("Category", text="Category", anchor="center")
        self.inventory_tree.heading("Price", text="Price", anchor="center")
        self.inventory_tree.heading("Stock", text="Stock", anchor="center")
        self.inventory_tree.heading("Added Date", text="Added Date", anchor="center")
        
        # Adjust column widths
        self.inventory_tree.column("ID", width=50, anchor="center")
        self.inventory_tree.column("Name", width=200, anchor="w")
        self.inventory_tree.column("Category", width=150, anchor="center")
        self.inventory_tree.column("Price", width=100, anchor="center")
        self.inventory_tree.column("Stock", width=100, anchor="center")
        self.inventory_tree.column("Added Date", width=150, anchor="center")
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the Treeview and scrollbar
        self.inventory_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # Bind events
        self.inventory_tree.bind("<Button-3>", self.show_context_menu)  # Right-click
        self.inventory_tree.bind("<Double-1>", self.edit_selected_product)  # Double-click
        
        # Load inventory data
        self.load_inventory()
    
    def load_inventory(self):
        """Load inventory data from database and display it in the Treeview."""
        # Clear existing rows
        for row in self.inventory_tree.get_children():
            self.inventory_tree.delete(row)
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor(dictionary=True)
            
            # Get all products
            cursor.execute("""
                SELECT product_id, product_name, product_category, product_price, 
                       stock_quantity, added_at 
                FROM products 
                ORDER BY product_category, product_name
            """)
            products = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            # Add products to the Treeview
            for product in products:
                self.inventory_tree.insert(
                    "",
                    "end",
                    values=(
                        product["product_id"],
                        product["product_name"],
                        product["product_category"],
                        format_currency(product["product_price"]),
                        product["stock_quantity"],
                        product["added_at"].strftime("%Y-%m-%d") if product["added_at"] else ""
                    )
                )
            
            # Color rows based on stock level
            for item in self.inventory_tree.get_children():
                stock = int(self.inventory_tree.item(item, "values")[4])
                if stock < 10:  # Low stock
                    self.inventory_tree.item(item, tags=("low_stock",))
                elif stock < 20:  # Medium stock
                    self.inventory_tree.item(item, tags=("medium_stock",))
            
            # Configure tags
            self.inventory_tree.tag_configure("low_stock", background="#ffebee")  # Light red
            self.inventory_tree.tag_configure("medium_stock", background="#fff8e1")  # Light yellow
            
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            messagebox.showerror("Database Error", f"Failed to load inventory: {err}")
    
    def open_add_product_window(self):
        """Open a new window for adding a product."""
        add_window = ctk.CTkToplevel(self)
        add_window.title("Add New Product")
        add_window.geometry("450x600")
        add_window.resizable(False, False)
        center_window(add_window, width=450, height=600)
        
        # Set this window as modal
        add_window.grab_set()
        
        # Form container
        form_frame = ctk.CTkScrollableFrame(add_window, fg_color="white")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            form_frame,
            text="Add New Product",
            font=("Arial", 18, "bold"),
            text_color="#1a73e8"
        )
        title_label.pack(pady=(10, 20))
        
        # Product Image Preview (placeholder)
        self.image_frame = ctk.CTkFrame(form_frame, fg_color="#f5f5f5", width=200, height=150, corner_radius=5)
        self.image_frame.pack(pady=(0, 15))
        
        # Product Name
        name_label = ctk.CTkLabel(form_frame, text="Product Name:", font=("Arial", 14))
        name_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        name_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter product name",
            width=390,
            height=35,
            border_width=1,
            corner_radius=8
        )
        name_entry.pack(padx=20, pady=(0, 15))
        
        # Product Category
        category_label = ctk.CTkLabel(form_frame, text="Category:", font=("Arial", 14))
        category_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        categories = ["Fruits", "Vegetables", "Dairy", "Bakery", "Meat", "Beverages", "Snacks", "Other"]
        category_var = ctk.StringVar(value=categories[0])
        category_combobox = ctk.CTkOptionMenu(
            form_frame,
            variable=category_var,
            values=categories,
            width=390,
            height=35,
            fg_color="white",
            button_color="#1a73e8",
            button_hover_color="#005cb2",
            dropdown_fg_color="white",
            dropdown_hover_color="#f0f0f0",
            dropdown_text_color="black"
        )
        category_combobox.pack(padx=20, pady=(0, 15))
        
        # Price
        price_label = ctk.CTkLabel(form_frame, text="Price ($):", font=("Arial", 14))
        price_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        price_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter price",
            width=390,
            height=35,
            border_width=1,
            corner_radius=8
        )
        price_entry.pack(padx=20, pady=(0, 15))
        
        # Stock Quantity
        stock_label = ctk.CTkLabel(form_frame, text="Stock Quantity:", font=("Arial", 14))
        stock_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        stock_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter stock quantity",
            width=390,
            height=35,
            border_width=1,
            corner_radius=8
        )
        stock_entry.pack(padx=20, pady=(0, 15))
        
        # Description (optional)
        description_label = ctk.CTkLabel(form_frame, text="Description (optional):", font=("Arial", 14))
        description_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        description_entry = ctk.CTkTextbox(
            form_frame,
            width=390,
            height=100,
            corner_radius=8,
            border_width=1
        )
        description_entry.pack(padx=20, pady=(0, 15))