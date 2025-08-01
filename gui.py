import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import json
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import io
import base64
import queue
import os

# Import your existing modules
from client import call_ollama_model
from parser import parse_response
from playwright_actions import perform_action

class CarRentalAutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Car Rental Automation Testing Tool")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2c3e50')
        
        # Queue for thread communication
        self.result_queue = queue.Queue()
        
        # Variables
        self.is_running = False
        self.current_screenshot = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Natural Language Interface
        self.create_natural_language_tab(notebook)
        
        # Tab 2: Quick Actions
        self.create_quick_actions_tab(notebook)
        
        # Tab 3: Form Builder
        self.create_form_builder_tab(notebook)
        
        # Tab 4: Results & Screenshots
        self.create_results_tab(notebook)
        
        # Tab 5: Test History
        self.create_history_tab(notebook)
        
    def create_natural_language_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="🤖 Natural Language")
        
        # Title
        title_label = ttk.Label(frame, text="Car Rental Automation - Natural Language Interface", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Input section
        input_frame = ttk.LabelFrame(frame, text="Enter Your Command", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Sample commands
        samples_frame = ttk.Frame(input_frame)
        samples_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(samples_frame, text="Sample Commands:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        sample_commands = [
            "Search for BMW cars",
            "Fill booking form for John Doe",
            "Submit the booking",
            "Check pricing for Luxury cars",
            "Navigate to cars section",
            "Test contact links",
            "Reset the form",
            "Validate empty form"
        ]
        
        samples_text = ttk.Label(samples_frame, text=" • " + "\n • ".join(sample_commands), 
                                justify=tk.LEFT, foreground='#7f8c8d')
        samples_text.pack(anchor=tk.W)
        
        # Input text area
        self.natural_input = scrolledtext.ScrolledText(input_frame, height=4, width=80)
        self.natural_input.pack(fill=tk.X, pady=5)
        self.natural_input.insert(tk.END, "Search for BMW cars")
        
        # Button frame
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.execute_btn = ttk.Button(btn_frame, text="🚀 Execute Command", 
                                     command=self.execute_natural_command, style='Accent.TButton')
        self.execute_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(btn_frame, text="🗑️ Clear", command=self.clear_natural_input)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(input_frame, textvariable=self.progress_var)
        self.progress_label.pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(input_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Output section
        output_frame = ttk.LabelFrame(frame, text="Execution Log", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=15)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
    def create_quick_actions_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="⚡ Quick Actions")
        
        # Title
        title_label = ttk.Label(frame, text="Quick Actions - One-Click Automation", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Create grid of action buttons
        actions_frame = ttk.Frame(frame)
        actions_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Define quick actions
        quick_actions = [
            ("🔍 Search BMW", {"action": "search_car", "query": "BMW"}),
            ("🔍 Search Mercedes", {"action": "search_car", "query": "Mercedes"}),
            ("🏠 Go to Home", {"action": "navigate_to_section", "section": "#home"}),
            ("🚗 Go to Cars", {"action": "navigate_to_section", "section": "#cars"}),
            ("📋 Go to Booking", {"action": "navigate_to_section", "section": "#booking"}),
            ("💰 Go to Pricing", {"action": "navigate_to_section", "section": "#price"}),
            ("📞 Test Contact", {"action": "test_contact_links"}),
            ("💰 Check SUV Price", {"action": "check_pricing", "car_type": "SUV"}),
            ("💰 Check VAN Price", {"action": "check_pricing", "car_type": "VAN"}),
            ("💰 Check Luxury Price", {"action": "check_pricing", "car_type": "Luxury"}),
            ("🚗 SUV Details", {"action": "check_car_details", "car_type": "SUV"}),
            ("🚐 VAN Details", {"action": "check_car_details", "car_type": "VAN"}),
            ("🏎️ Luxury Details", {"action": "check_car_details", "car_type": "Luxury"}),
            ("📝 Submit Booking", {"action": "submit_booking"}),
            ("🔄 Reset Form", {"action": "reset_form"}),
            ("✅ Validate Empty Form", {"action": "validate_empty_form"})
        ]
        
        # Create buttons in grid
        for i, (text, action) in enumerate(quick_actions):
            row = i // 4
            col = i % 4
            
            btn = ttk.Button(actions_frame, text=text, width=20,
                           command=lambda a=action: self.execute_quick_action(a))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
        
        # Configure grid weights
        for i in range(4):
            actions_frame.columnconfigure(i, weight=1)
            
    def create_form_builder_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="📝 Form Builder")
        
        # Title
        title_label = ttk.Label(frame, text="Booking Form Builder", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Form fields
        form_frame = ttk.LabelFrame(frame, text="Booking Details", padding=15)
        form_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Name
        ttk.Label(form_frame, text="Full Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.form_name = ttk.Entry(form_frame, width=30)
        self.form_name.insert(0, "Keerthana")
        self.form_name.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Email
        ttk.Label(form_frame, text="Email:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.form_email = ttk.Entry(form_frame, width=30)
        self.form_email.insert(0, "keer@example.com")
        self.form_email.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Start Date
        ttk.Label(form_frame, text="Start Date:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.form_start_date = ttk.Entry(form_frame, width=30)
        self.form_start_date.insert(0, (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
        self.form_start_date.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)
        
        # End Date
        ttk.Label(form_frame, text="End Date:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.form_end_date = ttk.Entry(form_frame, width=30)
        self.form_end_date.insert(0, (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"))
        self.form_end_date.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Car Type
        ttk.Label(form_frame, text="Car Type:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.form_car_type = ttk.Combobox(form_frame, values=["SUV", "VAN", "Luxury"], width=27)
        self.form_car_type.set("VAN")
        self.form_car_type.grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Checkboxes
        self.form_cdw = tk.BooleanVar(value=True)
        self.form_terms = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(form_frame, text="Collision Damage Waiver (CDW)", 
                       variable=self.form_cdw).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)
        ttk.Checkbutton(form_frame, text="Accept Terms & Conditions", 
                       variable=self.form_terms).grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=15)
        
        ttk.Button(btn_frame, text="📝 Fill Form Only", 
                  command=self.fill_booking_form).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📝➡️📤 Fill & Submit", 
                  command=self.fill_and_submit_form).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Reset Fields", 
                  command=self.reset_form_fields).pack(side=tk.LEFT, padx=5)
        
    def create_results_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="📊 Results")
        
        # Title
        title_label = ttk.Label(frame, text="Execution Results & Screenshots", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Split pane
        paned = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left side - Results text
        left_frame = ttk.LabelFrame(paned, text="Execution Results", padding=10)
        paned.add(left_frame, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(left_frame, height=20)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Right side - Screenshots
        right_frame = ttk.LabelFrame(paned, text="Screenshots", padding=10)
        paned.add(right_frame, weight=1)
        
        # Screenshot controls
        screenshot_controls = ttk.Frame(right_frame)
        screenshot_controls.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(screenshot_controls, text="💾 Save Screenshot", 
                  command=self.save_screenshot).pack(side=tk.LEFT, padx=5)
        ttk.Button(screenshot_controls, text="🗑️ Clear Results", 
                  command=self.clear_results).pack(side=tk.LEFT, padx=5)
        
        # Screenshot display
        self.screenshot_frame = ttk.Frame(right_frame)
        self.screenshot_frame.pack(fill=tk.BOTH, expand=True)
        
        self.screenshot_label = ttk.Label(self.screenshot_frame, text="No screenshot available")
        self.screenshot_label.pack(expand=True)
        
    def create_history_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="📚 History")
        
        # Title
        title_label = ttk.Label(frame, text="Test Execution History", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # History table
        history_frame = ttk.LabelFrame(frame, text="Recent Tests", padding=10)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview for history
        columns = ('Time', 'Command', 'Action', 'Status', 'Result')
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=150)
        
        # Scrollbar for treeview
        history_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # History controls
        history_controls = ttk.Frame(frame)
        history_controls.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(history_controls, text="🗑️ Clear History", 
                  command=self.clear_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(history_controls, text="💾 Export History", 
                  command=self.export_history).pack(side=tk.LEFT, padx=5)
        
        # Initialize history list
        self.test_history = []
        
    def execute_natural_command(self):
        if self.is_running:
            return
            
        command = self.natural_input.get(1.0, tk.END).strip()
        if not command:
            messagebox.showwarning("Warning", "Please enter a command!")
            return
            
        self.start_execution()
        self.log_output(f"🤖 Processing command: {command}")
        
        # Run in separate thread
        thread = threading.Thread(target=self.run_automation, args=(command, "natural"))
        thread.daemon = True
        thread.start()
        
        # Start checking for results
        self.check_result()
        
    def execute_quick_action(self, action):
        if self.is_running:
            return
            
        self.start_execution()
        self.log_output(f"⚡ Executing quick action: {action}")
        
        # Run in separate thread
        thread = threading.Thread(target=self.run_automation_direct, args=(action, "quick"))
        thread.daemon = True
        thread.start()
        
        self.check_result()
        
    def fill_booking_form(self):
        form_data = self.get_form_data()
        action = {
            "action": "fill_booking_form",
            "form_data": form_data
        }
        self.execute_quick_action(action)
        
    def fill_and_submit_form(self):
        form_data = self.get_form_data()
        
        if self.is_running:
            return
            
        self.start_execution()
        self.log_output("📝➡️📤 Filling form and submitting...")
        
        # Run both actions in sequence
        thread = threading.Thread(target=self.run_form_sequence, args=(form_data,))
        thread.daemon = True
        thread.start()
        
        self.check_result()
        
    def get_form_data(self):
        return {
            "name": self.form_name.get(),
            "email": self.form_email.get(),
            "start_date": self.form_start_date.get(),
            "end_date": self.form_end_date.get(),
            "car_type": self.form_car_type.get(),
            "cdw": self.form_cdw.get(),
            "terms": self.form_terms.get()
        }
        
    def reset_form_fields(self):
        self.form_name.delete(0, tk.END)
        self.form_name.insert(0, "John Doe")
        self.form_email.delete(0, tk.END)
        self.form_email.insert(0, "john@example.com")
        self.form_start_date.delete(0, tk.END)
        self.form_start_date.insert(0, (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
        self.form_end_date.delete(0, tk.END)
        self.form_end_date.insert(0, (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"))
        self.form_car_type.set("SUV")
        self.form_cdw.set(True)
        self.form_terms.set(True)
        
    def run_automation(self, command, source):
        try:
            # Step 1: Call Ollama
            self.update_progress("Calling Ollama model...")
            ollama_output = call_ollama_model(command)
            
            if not ollama_output:
                self.result_queue.put(("error", "No response from Ollama model", None, source))
                return
                
            # Step 2: Parse response
            self.update_progress("Parsing response...")
            parsed_instruction = parse_response(ollama_output)
            
            if not parsed_instruction:
                self.result_queue.put(("error", "Could not parse instruction", None, source))
                return
                
            # Step 3: Execute action
            self.update_progress("Executing browser automation...")
            result_message, screenshot = perform_action(parsed_instruction)
            
            self.result_queue.put(("success", result_message, screenshot, source, command, parsed_instruction))
            
        except Exception as e:
            self.result_queue.put(("error", str(e), None, source))
            
    def run_automation_direct(self, action, source):
        try:
            self.update_progress("Executing browser automation...")
            result_message, screenshot = perform_action(action)
            self.result_queue.put(("success", result_message, screenshot, source, str(action), action))
        except Exception as e:
            self.result_queue.put(("error", str(e), None, source))
            
    def run_form_sequence(self, form_data):
        try:
            # Fill form first
            self.update_progress("Filling booking form...")
            fill_action = {"action": "fill_booking_form", "form_data": form_data}
            result1, screenshot1 = perform_action(fill_action)
            
            # Then submit
            self.update_progress("Submitting booking...")
            submit_action = {"action": "submit_booking"}
            result2, screenshot2 = perform_action(submit_action)
            
            combined_result = f"Fill Result: {result1}\nSubmit Result: {result2}"
            final_screenshot = screenshot2 if screenshot2 else screenshot1
            
            self.result_queue.put(("success", combined_result, final_screenshot, "form_sequence", 
                                 "Fill and Submit Form", submit_action))
            
        except Exception as e:
            self.result_queue.put(("error", str(e), None, "form_sequence"))
            
    def start_execution(self):
        self.is_running = True
        self.execute_btn.configure(state='disabled')
        self.progress_bar.start()
        self.progress_var.set("Executing...")
        
    def finish_execution(self):
        self.is_running = False
        self.execute_btn.configure(state='normal')
        self.progress_bar.stop()
        self.progress_var.set("Ready")
        
    def update_progress(self, message):
        self.root.after(0, lambda: self.progress_var.set(message))
        
    def check_result(self):
        try:
            result = self.result_queue.get_nowait()
            status, message, screenshot, source = result[:4]
            
            if status == "success":
                command = result[4] if len(result) > 4 else "Unknown"
                action = result[5] if len(result) > 5 else {}
                
                self.log_output(f"✅ SUCCESS: {message}")
                self.display_screenshot(screenshot)
                self.add_to_history(command, action.get('action', 'Unknown'), "Success", message)
                
            else:
                self.log_output(f"❌ ERROR: {message}")
                self.add_to_history("Error", "Error", "Failed", message)
                
            self.finish_execution()
            
        except queue.Empty:
            # Check again in 100ms
            self.root.after(100, self.check_result)
            
    def log_output(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.output_text.insert(tk.END, formatted_message)
        self.output_text.see(tk.END)
        
        # Also log to results tab
        self.results_text.insert(tk.END, formatted_message)
        self.results_text.see(tk.END)
        
    def display_screenshot(self, screenshot_bytes):
        if not screenshot_bytes:
            return
            
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(screenshot_bytes))
            
            # Resize to fit display
            display_size = (400, 300)
            image.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Update display
            self.screenshot_label.configure(image=photo, text="")
            self.screenshot_label.image = photo  # Keep reference
            
            # Store current screenshot
            self.current_screenshot = screenshot_bytes
            
        except Exception as e:
            self.log_output(f"Error displaying screenshot: {e}")
            
    def save_screenshot(self):
        if not self.current_screenshot:
            messagebox.showinfo("Info", "No screenshot to save!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialfile=f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        )
        
        if filename:
            try:
                with open(filename, 'wb') as f:
                    f.write(self.current_screenshot)
                messagebox.showinfo("Success", f"Screenshot saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save screenshot: {e}")
                
    def clear_results(self):
        self.results_text.delete(1.0, tk.END)
        self.screenshot_label.configure(image="", text="No screenshot available")
        self.screenshot_label.image = None
        self.current_screenshot = None
        
    def clear_natural_input(self):
        self.natural_input.delete(1.0, tk.END)
        
    def add_to_history(self, command, action, status, result):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Add to treeview
        self.history_tree.insert('', 0, values=(
            timestamp, 
            command[:50] + "..." if len(command) > 50 else command,
            action,
            status,
            result[:50] + "..." if len(result) > 50 else result
        ))
        
        # Add to history list
        self.test_history.insert(0, {
            'timestamp': timestamp,
            'command': command,
            'action': action,
            'status': status,
            'result': result
        })
        
        # Keep only last 100 entries
        if len(self.test_history) > 100:
            self.test_history.pop()
            
    def clear_history(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        self.test_history.clear()
        
    def export_history(self):
        if not self.test_history:
            messagebox.showinfo("Info", "No history to export!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"test_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.test_history, f, indent=2)
                messagebox.showinfo("Success", f"History exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export history: {e}")

def main():
    root = tk.Tk()
    app = CarRentalAutomationGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()