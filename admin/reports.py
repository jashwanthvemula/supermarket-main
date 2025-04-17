import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from utils import connect_to_database, format_currency, center_window
import mysql.connector
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os


class ReportsFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.configure(fg_color="#f0f0f0")
        
        # Title frame
        self.title_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self.title_frame.pack(fill="x", pady=(0, 20))
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text="Reports - Last 3 Months",
            font=("Arial", 24, "bold"),
            text_color="#1a73e8"
        )
        self.title_label.pack(side="left", padx=30, pady=15)
        
        # Main content frame with report types on left and display area on right
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Configure content frame layout
        self.content_frame.grid_columnconfigure(0, weight=1)  # Report types column
        self.content_frame.grid_columnconfigure(1, weight=4)  # Report display column
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Report types frame (left)
        self.report_types_frame = ctk.CTkFrame(self.content_frame, fg_color="white", corner_radius=10)
        self.report_types_frame.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")
        
        # Label for report types
        self.report_types_label = ctk.CTkLabel(
            self.report_types_frame,
            text="Report Types",
            font=("Arial", 16, "bold"),
            text_color="#333"
        )
        self.report_types_label.pack(padx=20, pady=(20, 15))
        
        # Report buttons
        self.sales_report_btn = ctk.CTkButton(
            self.report_types_frame,
            text="Sales Over Time",
            command=lambda: self.generate_report("sales"),
            width=180,
            height=40,
            corner_radius=8,
            fg_color="#f0f0f0",
            text_color="#333",
            hover_color="#e0e0e0"
        )
        self.sales_report_btn.pack(padx=20, pady=10)
        
        self.products_report_btn = ctk.CTkButton(
            self.report_types_frame,
            text="Top Products",
            command=lambda: self.generate_report("products"),
            width=180,
            height=40,
            corner_radius=8,
            fg_color="#f0f0f0",
            text_color="#333",
            hover_color="#e0e0e0"
        )
        self.products_report_btn.pack(padx=20, pady=10)
        
        self.revenue_report_btn = ctk.CTkButton(
            self.report_types_frame,
            text="Revenue Summary",
            command=lambda: self.generate_report("revenue"),
            width=180,
            height=40,
            corner_radius=8,
            fg_color="#f0f0f0",
            text_color="#333",
            hover_color="#e0e0e0"
        )
        self.revenue_report_btn.pack(padx=20, pady=10)
        
        self.stock_report_btn = ctk.CTkButton(
            self.report_types_frame,
            text="Low Stock Items",
            command=lambda: self.generate_report("stock"),
            width=180,
            height=40,
            corner_radius=8,
            fg_color="#f0f0f0",
            text_color="#333",
            hover_color="#e0e0e0"
        )
        self.stock_report_btn.pack(padx=20, pady=10)
        
        # Export button (to export the current report)
        self.export_btn = ctk.CTkButton(
            self.report_types_frame,
            text="Export Current Report",
            command=self.export_report,
            width=180,
            height=40,
            corner_radius=8,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        self.export_btn.pack(padx=20, pady=(30, 20))
        
        # Report display frame (right)
        self.report_display_frame = ctk.CTkFrame(self.content_frame, fg_color="white", corner_radius=10)
        self.report_display_frame.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")
        
        # Initial welcome message
        self.welcome_label = ctk.CTkLabel(
            self.report_display_frame,
            text="Welcome to Reports",
            font=("Arial", 18, "bold"),
            text_color="#333"
        )
        self.welcome_label.pack(pady=(100, 10))
        
        self.instruction_label = ctk.CTkLabel(
            self.report_display_frame,
            text="Select a report type from the left to generate a report.",
            font=("Arial", 14),
            text_color="#555"
        )
        self.instruction_label.pack(pady=(0, 100))
        
        # Instance variables
        self.current_report_type = None
        self.current_figure = None
        self.canvas = None
    
    def generate_report(self, report_type):
        """Generate and display the selected report type."""
        self.current_report_type = report_type
        
        # Clear current display
        for widget in self.report_display_frame.winfo_children():
            widget.destroy()
        
        # Generate the report based on type
        try:
            if report_type == "sales":
                self.generate_sales_report()
            elif report_type == "products":
                self.generate_products_report()
            elif report_type == "revenue":
                self.generate_revenue_report()
            elif report_type == "stock":
                self.generate_stock_report()
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            error_label = ctk.CTkLabel(
                self.report_display_frame,
                text=f"Error generating report: {err}",
                font=("Arial", 14),
                text_color="red",
                wraplength=500
            )
            error_label.pack(pady=100)
    
    def generate_sales_report(self):
        """Generate and display the sales over time report."""
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            
            # Date 3 months ago
            three_months_ago = datetime.now() - timedelta(days=90)
            
            # Query to get sales data grouped by month
            query = """
                SELECT 
                    DATE_FORMAT(order_date, '%Y-%m') AS month,
                    COUNT(order_id) AS order_count,
                    SUM(total_price) AS revenue
                FROM orders
                WHERE order_date >= %s
                GROUP BY month
                ORDER BY month
            """
            
            cursor.execute(query, (three_months_ago,))
            sales_data = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            if not sales_data:
                self.display_no_data_message("No sales data available for the last 3 months.")
                return
            
            # Create and display the plot
            self.create_sales_plot(sales_data)
            
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            self.display_error_message(f"Database error: {err}")
    
    def generate_products_report(self):
        """Generate and display the top products report."""
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            
            # Date 3 months ago
            three_months_ago = datetime.now() - timedelta(days=90)
            
            # Query to get top products by quantity sold
            query = """
                SELECT 
                    p.product_name,
                    SUM(od.quantity) AS total_quantity,
                    SUM(od.sub_total) AS total_revenue
                FROM order_details od
                JOIN products p ON od.product_id = p.product_id
                JOIN orders o ON od.order_id = o.order_id
                WHERE o.order_date >= %s
                GROUP BY p.product_id
                ORDER BY total_quantity DESC
                LIMIT 10
            """
            
            cursor.execute(query, (three_months_ago,))
            product_data = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            if not product_data:
                self.display_no_data_message("No product sales data available for the last 3 months.")
                return
            
            # Create and display the plot
            self.create_products_plot(product_data)
            
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            self.display_error_message(f"Database error: {err}")
    
    def generate_revenue_report(self):
        """Generate and display the revenue summary report."""
        try:
            conn = connect_to_database()
            cursor = conn.cursor(dictionary=True)
            
            # Date 3 months ago
            three_months_ago = datetime.now() - timedelta(days=90)
            
            # Query to get revenue stats
            query = """
                SELECT 
                    COUNT(order_id) AS total_orders,
                    SUM(total_price) AS total_revenue,
                    AVG(total_price) AS average_order_value,
                    MAX(total_price) AS highest_order,
                    MIN(total_price) AS lowest_order
                FROM orders
                WHERE order_date >= %s
            """
            
            cursor.execute(query, (three_months_ago,))
            revenue_data = cursor.fetchone()
            
            # Get revenue by category
            category_query = """
                SELECT 
                    p.product_category,
                    SUM(od.sub_total) AS category_revenue
                FROM order_details od
                JOIN products p ON od.product_id = p.product_id
                JOIN orders o ON od.order_id = o.order_id
                WHERE o.order_date >= %s
                GROUP BY p.product_category
                ORDER BY category_revenue DESC
            """
            
            cursor.execute(category_query, (three_months_ago,))
            category_data = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            if not revenue_data or revenue_data["total_orders"] == 0:
                self.display_no_data_message("No revenue data available for the last 3 months.")
                return
            
            # Display the revenue summary
            self.display_revenue_summary(revenue_data, category_data)
            
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            self.display_error_message(f"Database error: {err}")
    
    def generate_stock_report(self):
        """Generate and display the low stock items report."""
        try:
            conn = connect_to_database()
            cursor = conn.cursor(dictionary=True)
            
            # Query to get low stock items (less than 10 units)
            query = """
                SELECT 
                    product_id,
                    product_name,
                    product_category,
                    stock_quantity,
                    product_price
                FROM products
                WHERE stock_quantity < 10
                ORDER BY stock_quantity ASC
            """
            
            cursor.execute(query)
            stock_data = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            if not stock_data:
                self.display_no_data_message("No low stock items found.")
                return
            
            # Display the low stock items
            self.display_low_stock_items(stock_data)
            
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            self.display_error_message(f"Database error: {err}")
    
    def create_sales_plot(self, data):
        """Create and display a plot showing sales over time."""
        # Extract data
        months = [item[0] for item in data]
        order_counts = [item[1] for item in data]
        revenue = [float(item[2]) for item in data]
        
        # Create figure
        fig, ax1 = plt.subplots(figsize=(8, 5), dpi=100)
        
        # Plot order count
        ax1.set_xlabel('Month')
        ax1.set_ylabel('Order Count', color='tab:blue')
        ax1.bar(months, order_counts, color='tab:blue', alpha=0.7, label='Order Count')
        ax1.tick_params(axis='y', labelcolor='tab:blue')
        
        # Create second y-axis for revenue
        ax2 = ax1.twinx()
        ax2.set_ylabel('Revenue ($)', color='tab:red')
        ax2.plot(months, revenue, color='tab:red', marker='o', linestyle='-', linewidth=2, label='Revenue')
        ax2.tick_params(axis='y', labelcolor='tab:red')
        
        # Format x-axis labels for better readability
        plt.xticks(rotation=45)
        
        # Add title and grid
        plt.title('Sales and Revenue Over Time')
        ax1.grid(True, alpha=0.3)
        
        # Add legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        # Tight layout to ensure everything fits
        fig.tight_layout()
        
        # Display the plot
        self.display_matplotlib_figure(fig)
        
        # Store figure for exporting
        self.current_figure = fig
    
    def create_products_plot(self, data):
        """Create and display a plot showing top products."""
        # Extract data
        products = [item[0] for item in data]
        quantities = [item[1] for item in data]
        revenues = [float(item[2]) for item in data]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
        
        # Create horizontal bar chart
        y_pos = range(len(products))
        ax.barh(y_pos, quantities, align='center', color='tab:blue', alpha=0.7)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(products)
        ax.invert_yaxis()  # Labels read top-to-bottom
        
        # Add labels and title
        ax.set_xlabel('Quantity Sold')
        ax.set_title('Top Products by Quantity Sold')
        
        # Add quantity values at the end of each bar
        for i, v in enumerate(quantities):
            ax.text(v + 0.5, i, str(v), va='center')
        
        # Tight layout to ensure everything fits
        fig.tight_layout()
        
        # Display the plot
        self.display_matplotlib_figure(fig)
        
        # Store figure for exporting
        self.current_figure = fig
    
    def display_matplotlib_figure(self, figure):
        """Display a matplotlib figure in the report display frame."""
        # Clear any existing plot
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        
        # Create a canvas widget to display the figure
        canvas = FigureCanvasTkAgg(figure, master=self.report_display_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Store the canvas reference
        self.canvas = canvas
    
    def display_revenue_summary(self, revenue_data, category_data):
        """Display the revenue summary report."""
        # Create title
        title_label = ctk.CTkLabel(
            self.report_display_frame,
            text="Revenue Summary - Last 3 Months",
            font=("Arial", 18, "bold"),
            text_color="#1a73e8"
        )
        title_label.pack(pady=(20, 30))
        
        # Create summary frame
        summary_frame = ctk.CTkFrame(self.report_display_frame, fg_color="#f5f5f5", corner_radius=10)
        summary_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        # Add summary information
        total_orders = revenue_data["total_orders"]
        total_revenue = revenue_data["total_revenue"] or 0
        avg_order = revenue_data["average_order_value"] or 0
        highest_order = revenue_data["highest_order"] or 0
        lowest_order = revenue_data["lowest_order"] or 0
        
        # Create grid layout for summary
        summary_frame.grid_columnconfigure(0, weight=1)
        summary_frame.grid_columnconfigure(1, weight=1)
        
        # Total Orders
        total_orders_label = ctk.CTkLabel(
            summary_frame,
            text="Total Orders:",
            font=("Arial", 14, "bold"),
            text_color="#333"
        )
        total_orders_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        total_orders_value = ctk.CTkLabel(
            summary_frame,
            text=str(total_orders),
            font=("Arial", 14),
            text_color="#1a73e8"
        )
        total_orders_value.grid(row=0, column=1, padx=20, pady=10, sticky="w")
        
        # Total Revenue
        total_revenue_label = ctk.CTkLabel(
            summary_frame,
            text="Total Revenue:",
            font=("Arial", 14, "bold"),
            text_color="#333"
        )
        total_revenue_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        total_revenue_value = ctk.CTkLabel(
            summary_frame,
            text=format_currency(total_revenue),
            font=("Arial", 14),
            text_color="#1a73e8"
        )
        total_revenue_value.grid(row=1, column=1, padx=20, pady=10, sticky="w")
        
        # Average Order Value
        avg_order_label = ctk.CTkLabel(
            summary_frame,
            text="Average Order Value:",
            font=("Arial", 14, "bold"),
            text_color="#333"
        )
        avg_order_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        
        avg_order_value = ctk.CTkLabel(
            summary_frame,
            text=format_currency(avg_order),
            font=("Arial", 14),
            text_color="#1a73e8"
        )
        avg_order_value.grid(row=2, column=1, padx=20, pady=10, sticky="w")
        
        # Highest Order
        highest_order_label = ctk.CTkLabel(
            summary_frame,
            text="Highest Order Value:",
            font=("Arial", 14, "bold"),
            text_color="#333"
        )
        highest_order_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        
        highest_order_value = ctk.CTkLabel(
            summary_frame,
            text=format_currency(highest_order),
            font=("Arial", 14),
            text_color="#1a73e8"
        )
        highest_order_value.grid(row=3, column=1, padx=20, pady=10, sticky="w")
        
        # Lowest Order
        lowest_order_label = ctk.CTkLabel(
            summary_frame,
            text="Lowest Order Value:",
            font=("Arial", 14, "bold"),
            text_color="#333"
        )
        lowest_order_label.grid(row=4, column=0, padx=20, pady=10, sticky="w")
        
        lowest_order_value = ctk.CTkLabel(
            summary_frame,
            text=format_currency(lowest_order),
            font=("Arial", 14),
            text_color="#1a73e8"
        )
        lowest_order_value.grid(row=4, column=1, padx=20, pady=10, sticky="w")
        
        # If we have category data, create a pie chart
        if category_data:
            # Extract data
            categories = [item["product_category"] for item in category_data]
            revenues = [float(item["category_revenue"]) for item in category_data]
            
            # Create figure
            fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
            
            # Create pie chart
            wedges, texts, autotexts = ax.pie(
                revenues, 
                labels=categories, 
                autopct='%1.1f%%',
                startangle=90,
                shadow=False
            )
            
            # Equal aspect ratio ensures that pie is drawn as a circle
            ax.axis('equal')
            
            # Add title
            plt.title('Revenue by Category')
            
            # Display the plot
            self.display_matplotlib_figure(fig)
            
            # Store figure for exporting
            self.current_figure = fig
    
    def display_low_stock_items(self, stock_data):
        """Display the low stock items report."""
        # Create title
        title_label = ctk.CTkLabel(
            self.report_display_frame,
            text="Low Stock Items Report",
            font=("Arial", 18, "bold"),
            text_color="#1a73e8"
        )
        title_label.pack(pady=(20, 10))
        
        # Create subtitle
        subtitle_label = ctk.CTkLabel(
            self.report_display_frame,
            text=f"Items with stock quantity less than 10 ({len(stock_data)} items found)",
            font=("Arial", 14),
            text_color="#555"
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Create scrollable frame for items
        items_frame = ctk.CTkScrollableFrame(
            self.report_display_frame,
            width=600,
            height=400,
            fg_color="transparent"
        )
        items_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Header row
        header_frame = ctk.CTkFrame(items_frame, fg_color="#f0f0f0", corner_radius=0)
        header_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        # Configure header columns
        header_frame.grid_columnconfigure(0, weight=1)  # Product Name
        header_frame.grid_columnconfigure(1, weight=1)  # Category
        header_frame.grid_columnconfigure(2, weight=1)  # Stock
        header_frame.grid_columnconfigure(3, weight=1)  # Price
        
        # Header labels
        ctk.CTkLabel(
            header_frame, 
            text="Product Name", 
            font=("Arial", 14, "bold"),
            text_color="#333"
        ).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(
            header_frame, 
            text="Category", 
            font=("Arial", 14, "bold"),
            text_color="#333"
        ).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(
            header_frame, 
            text="Stock", 
            font=("Arial", 14, "bold"),
            text_color="#333"
        ).grid(row=0, column=2, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(
            header_frame, 
            text="Price", 
            font=("Arial", 14, "bold"),
            text_color="#333"
        ).grid(row=0, column=3, padx=10, pady=5, sticky="w")
        
        # Display each low stock item
        for i, item in enumerate(stock_data):
            item_frame = ctk.CTkFrame(items_frame, fg_color="white", corner_radius=5)
            item_frame.pack(fill="x", padx=5, pady=5)
            
            # Configure item columns
            item_frame.grid_columnconfigure(0, weight=1)  # Product Name
            item_frame.grid_columnconfigure(1, weight=1)  # Category
            item_frame.grid_columnconfigure(2, weight=1)  # Stock
            item_frame.grid_columnconfigure(3, weight=1)  # Price
            
            # Item data
            ctk.CTkLabel(
                item_frame, 
                text=item["product_name"], 
                font=("Arial", 12),
                text_color="#333"
            ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
            
            ctk.CTkLabel(
                item_frame, 
                text=item["product_category"], 
                font=("Arial", 12),
                text_color="#555"
            ).grid(row=0, column=1, padx=10, pady=10, sticky="w")
            
            # Stock level with color coding
            stock_color = "#f44336" if item["stock_quantity"] < 5 else "#ff9800"  # Red if < 5, Orange if < 10
            ctk.CTkLabel(
                item_frame, 
                text=str(item["stock_quantity"]), 
                font=("Arial", 12, "bold"),
                text_color=stock_color
            ).grid(row=0, column=2, padx=10, pady=10, sticky="w")
            
            ctk.CTkLabel(
                item_frame, 
                text=format_currency(item["product_price"]), 
                font=("Arial", 12),
                text_color="#1a73e8"
            ).grid(row=0, column=3, padx=10, pady=10, sticky="w")
        
        # Create a bar chart of low stock items
        self.create_low_stock_plot(stock_data)
    
    def create_low_stock_plot(self, data):
        """Create and display a bar chart of low stock items."""
        # Extract data (limit to top 10 lowest stock items)
        sorted_data = sorted(data, key=lambda x: x["stock_quantity"])[:10]
        products = [item["product_name"] for item in sorted_data]
        stock_levels = [item["stock_quantity"] for item in sorted_data]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
        
        # Create horizontal bar chart
        y_pos = range(len(products))
        bars = ax.barh(y_pos, stock_levels, align='center')
        
        # Color bars based on stock level
        for i, bar in enumerate(bars):
            if stock_levels[i] < 5:
                bar.set_color('#f44336')  # Red for very low stock
            else:
                bar.set_color('#ff9800')  # Orange for low stock
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(products)
        ax.invert_yaxis()  # Labels read top-to-bottom
        
        # Add labels and title
        ax.set_xlabel('Stock Quantity')
        ax.set_title('Lowest Stock Items')
        
        # Add stock values at the end of each bar
        for i, v in enumerate(stock_levels):
            ax.text(v + 0.1, i, str(v), va='center')
        
        # Set x-axis limit for better visibility
        ax.set_xlim(0, max(stock_levels) + 2)
        
        # Tight layout to ensure everything fits
        fig.tight_layout()
        
        # Display the plot
        self.display_matplotlib_figure(fig)
        
        # Store figure for exporting
        self.current_figure = fig
    
    def display_no_data_message(self, message):
        """Display a message when no data is available for the report."""
        no_data_label = ctk.CTkLabel(
            self.report_display_frame,
            text=message,
            font=("Arial", 16),
            text_color="#555"
        )
        no_data_label.pack(pady=(100, 10))
        
        suggestion_label = ctk.CTkLabel(
            self.report_display_frame,
            text="Try checking back later when more data is available.",
            font=("Arial", 14),
            text_color="#777"
        )
        suggestion_label.pack(pady=(0, 100))
    
    def display_error_message(self, message):
        """Display an error message."""
        error_label = ctk.CTkLabel(
            self.report_display_frame,
            text="Error Generating Report",
            font=("Arial", 16, "bold"),
            text_color="#f44336"
        )
        error_label.pack(pady=(100, 10))
        
        message_label = ctk.CTkLabel(
            self.report_display_frame,
            text=message,
            font=("Arial", 14),
            text_color="#555",
            wraplength=500
        )
        message_label.pack(pady=(0, 100))
    
    def export_report(self):
        """Export the current report to a file."""
        if not self.current_report_type:
            messagebox.showinfo("No Report", "Please generate a report first before exporting.")
            return
        
        if not self.current_figure:
            messagebox.showinfo("Cannot Export", "Current report does not have a figure to export.")
            return
        
        # Create reports directory if it doesn't exist
        os.makedirs("reports", exist_ok=True)
        
        # Generate a filename based on report type and date
        report_name = {
            "sales": "Sales_Report",
            "products": "Top_Products_Report",
            "revenue": "Revenue_Summary",
            "stock": "Low_Stock_Report"
        }.get(self.current_report_type, "Report")
        
        today = datetime.now().strftime("%Y-%m-%d")
        default_filename = f"{report_name}_{today}.png"
        
        # Ask user for save location
        file_path = filedialog.asksaveasfilename(
            initialdir="reports",
            initialfile=default_filename,
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Save the figure
            self.current_figure.savefig(file_path, dpi=300, bbox_inches='tight')
            messagebox.showinfo("Export Successful", f"Report exported to {file_path}")
            
            # Log the report in the database if needed
            self.log_report_export(file_path)
            
        except Exception as e:
            print(f"Error exporting report: {e}")
            messagebox.showerror("Export Error", f"Failed to export report: {e}")
    
    def log_report_export(self, file_path):
        """Log the report export in the database."""
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            
            # Insert the report record
            cursor.execute(
                "INSERT INTO admin_reports (user_id, date_generated, path_stored) VALUES (%s, NOW(), %s)",
                (self.master.user_id, file_path)
            )
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except mysql.connector.Error as err:
            print(f"Database error logging report: {err}")
            # Not showing this error to the user as it's not critical