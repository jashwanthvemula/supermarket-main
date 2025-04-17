import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
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
        
        # Add sort functionality
        for col in self.inventory_tree["columns"]:
            self.inventory_tree.heading(col, command=lambda _col=col: self.sort_treeview(_col, False))
        
        # Load inventory data
        self.load_inventory()
    
    def sort_treeview(self, col, reverse):
        """Sort the treeview when a column header is clicked."""
        # Get all rows with their values
        data = [(self.inventory_tree.set(item, col), item) for item in self.inventory_tree.get_children('')]
        
        # Sort the data
        data.sort(reverse=reverse)
        
        # Rearrange rows in the treeview
        for index, (_, item) in enumerate(data):
            self.inventory_tree.move(item, '', index)
        
        # Reverse the sort the next time this column is clicked
        self.inventory_tree.heading(col, command=lambda: self.sort_treeview(col, not reverse))
    
    def load_inventory(self):
        """Load inventory data from database and display it in the Treeview."""
        # Clear existing rows
        for row in self.inventory_tree.get_children():
            self.inventory_tree.delete(row)
        
        try:
            conn = connect_to_database()
            if not conn:
                messagebox.showerror("Database Error", "Failed to connect to database")
                return
                
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
            
            if not products:
                messagebox.showinfo("Inventory", "No products found in inventory.")
                return
            
            # Add products to the Treeview
            for product in products:
                # Format the date if it exists
                added_date = product["added_at"].strftime("%Y-%m-%d") if product["added_at"] else ""
                
                self.inventory_tree.insert(
                    "",
                    "end",
                    values=(
                        product["product_id"],
                        product["product_name"],
                        product["product_category"],
                        format_currency(product["product_price"]),
                        product["stock_quantity"],
                        added_date
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
        image_frame = ctk.CTkFrame(form_frame, fg_color="#f5f5f5", width=200, height=150, corner_radius=5)
        image_frame.pack(pady=(0, 15))
        
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
            border_width=1,
            corner_radius=8
        )
        description_entry.pack(padx=20, pady=(0, 15))
        
        # Error label
        error_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=("Arial", 12),
            text_color="red",
            wraplength=390
        )
        error_label.pack(pady=(0, 15))
        
        # Save button
        def save_product():
            # Validate fields
            name = name_entry.get().strip()
            category = category_var.get()
            price = price_entry.get().strip()
            stock = stock_entry.get().strip()
            description = description_entry.get("1.0", "end-1c").strip()
            
            if not name or not price or not stock:
                error_label.configure(text="Product name, price, and stock are required")
                return
            
            try:
                # Validate price as a number
                price = float(price)
                if price <= 0:
                    error_label.configure(text="Price must be greater than zero")
                    return
                
                # Validate stock as an integer
                stock = int(stock)
                if stock < 0:
                    error_label.configure(text="Stock cannot be negative")
                    return
                
                conn = connect_to_database()
                if not conn:
                    error_label.configure(text="Database connection failed")
                    return
                    
                cursor = conn.cursor()
                
                # Insert the new product
                cursor.execute(
                    """
                    INSERT INTO products 
                    (product_name, product_category, product_price, stock_quantity, added_at) 
                    VALUES (%s, %s, %s, %s, NOW())
                    """,
                    (name, category, price, stock)
                )
                
                # Get the new product ID
                product_id = cursor.lastrowid
                
                # Insert into inventory table
                cursor.execute(
                    "INSERT INTO inventory (product_id, stock_level, last_updated) VALUES (%s, %s, NOW())",
                    (product_id, stock)
                )
                
                conn.commit()
                cursor.close()
                conn.close()
                
                # Reload inventory
                self.load_inventory()
                
                # Close the window
                add_window.destroy()
                
                # Show success message
                messagebox.showinfo("Success", "Product added successfully")
                
            except ValueError:
                error_label.configure(text="Price and stock must be valid numbers")
            except mysql.connector.Error as err:
                print(f"Database error: {err}")
                error_label.configure(text=f"Error: {err}")
        
        save_button = ctk.CTkButton(
            form_frame,
            text="Save Product",
            command=save_product,
            width=390,
            height=40,
            corner_radius=8,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        save_button.pack(pady=(0, 20))
    
    def edit_selected_product(self, event=None):
        """Open a window to edit the selected product."""
        selected = self.inventory_tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a product to edit")
            return
        
        # Get the selected product's information
        product_id = self.inventory_tree.item(selected, "values")[0]
        
        try:
            conn = connect_to_database()
            if not conn:
                messagebox.showerror("Database Error", "Failed to connect to database")
                return
                
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
            product = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if not product:
                messagebox.showerror("Error", "Product not found")
                return
            
            # Create edit window
            edit_window = ctk.CTkToplevel(self)
            edit_window.title("Edit Product")
            edit_window.geometry("450x600")
            edit_window.resizable(False, False)
            center_window(edit_window, width=450, height=600)
            
            # Set this window as modal
            edit_window.grab_set()
            
            # Form container
            form_frame = ctk.CTkScrollableFrame(edit_window, fg_color="white")
            form_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Title
            title_label = ctk.CTkLabel(
                form_frame,
                text="Edit Product",
                font=("Arial", 18, "bold"),
                text_color="#1a73e8"
            )
            title_label.pack(pady=(10, 20))
            
            # Product Image Preview
            image_frame = ctk.CTkFrame(form_frame, fg_color="#f5f5f5", width=200, height=150, corner_radius=5)
            image_frame.pack(pady=(0, 15))
            
            # Try to load product image if it exists
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
            name_entry.insert(0, product["product_name"])
            name_entry.pack(padx=20, pady=(0, 15))
            
            # Product Category
            category_label = ctk.CTkLabel(form_frame, text="Category:", font=("Arial", 14))
            category_label.pack(anchor="w", padx=20, pady=(0, 5))
            
            categories = ["Fruits", "Vegetables", "Dairy", "Bakery", "Meat", "Beverages", "Snacks", "Other"]
            category_var = ctk.StringVar(value=product["product_category"])
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
            price_entry.insert(0, str(product["product_price"]))
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
            stock_entry.insert(0, str(product["stock_quantity"]))
            stock_entry.pack(padx=20, pady=(0, 15))
            
            # Error label
            error_label = ctk.CTkLabel(
                form_frame,
                text="",
                font=("Arial", 12),
                text_color="red",
                wraplength=390
            )
            error_label.pack(pady=(0, 15))
            
            # Save button
            def save_changes():
                # Validate fields
                name = name_entry.get().strip()
                category = category_var.get()
                price = price_entry.get().strip()
                stock = stock_entry.get().strip()
                
                if not name or not price or not stock:
                    error_label.configure(text="Product name, price, and stock are required")
                    return
                
                try:
                    # Validate price as a number
                    price = float(price)
                    if price <= 0:
                        error_label.configure(text="Price must be greater than zero")
                        return
                    
                    # Validate stock as an integer
                    stock = int(stock)
                    if stock < 0:
                        error_label.configure(text="Stock cannot be negative")
                        return
                    
                    conn = connect_to_database()
                    if not conn:
                        error_label.configure(text="Database connection failed")
                        return
                        
                    cursor = conn.cursor()
                    
                    # Update the product
                    cursor.execute(
                        """
                        UPDATE products 
                        SET product_name = %s, product_category = %s, product_price = %s, stock_quantity = %s
                        WHERE product_id = %s
                        """,
                        (name, category, price, stock, product_id)
                    )
                    
                    # Update inventory
                    cursor.execute(
                        "UPDATE inventory SET stock_level = %s, last_updated = NOW() WHERE product_id = %s",
                        (stock, product_id)
                    )
                    
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    # Reload inventory
                    self.load_inventory()
                    
                    # Close the window
                    edit_window.destroy()
                    
                    # Show success message
                    messagebox.showinfo("Success", "Product updated successfully")
                    
                except ValueError:
                    error_label.configure(text="Price and stock must be valid numbers")
                except mysql.connector.Error as err:
                    print(f"Database error: {err}")
                    error_label.configure(text=f"Error: {err}")
            
            save_button = ctk.CTkButton(
                form_frame,
                text="Save Changes",
                command=save_changes,
                width=390,
                height=40,
                corner_radius=8,
                fg_color="#4CAF50",
                hover_color="#388E3C"
            )
            save_button.pack(pady=(0, 20))
            
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            messagebox.showerror("Database Error", f"Error: {err}")
    
    def delete_selected_product(self):
        """Delete the selected product."""
        selected = self.inventory_tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a product to delete")
            return
        
        # Get the selected product's information
        product_id = self.inventory_tree.item(selected, "values")[0]
        product_name = self.inventory_tree.item(selected, "values")[1]
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to delete {product_name}?\n\nThis action cannot be undone."
        )
        if not confirm:
            return
        
        try:
            conn = connect_to_database()
            if not conn:
                messagebox.showerror("Database Error", "Failed to connect to database")
                return
                
            cursor = conn.cursor()
            
            try:
                # Start transaction
                conn.start_transaction()
                
                # Delete from inventory first (due to foreign key constraint)
                cursor.execute("DELETE FROM inventory WHERE product_id = %s", (product_id,))
                
                # Delete the product
                cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
                
                # Commit transaction
                conn.commit()
                
                # Reload inventory
                self.load_inventory()
                
                # Show success message
                messagebox.showinfo("Success", "Product deleted successfully")
                
            except mysql.connector.Error as err:
                # Rollback on error
                conn.rollback()
                raise err
            finally:
                cursor.close()
                conn.close()
            
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            messagebox.showerror("Database Error", f"Failed to delete product: {err}")
    
    def show_context_menu(self, event):
        """Show a context menu when right-clicking on a product."""
        selected = self.inventory_tree.selection()
        if not selected:
            return
        
        # Create context menu
        context_menu = tk.Menu(self, tearoff=0)
        
        # Edit option
        context_menu.add_command(label="Edit", command=self.edit_selected_product)
        
        # Delete option
        context_menu.add_command(label="Delete", command=self.delete_selected_product)
        
        # Display the menu at the pointer position
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            # Make sure to release the menu
            context_menu.grab_release()