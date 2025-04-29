import requests
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from urllib.parse import urlparse
import random

API_KEY = "AIzaSyCAp1Dkr-WoJ2pocda1VEUe4JVEPric7DQ"
CX = "87eee66ce480a4da4"

class GhostSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ghost Search")
        self.root.geometry("800x600")
        
        # Window styling
        self.root.attributes('-alpha', 0.92)  # Semi-transparent
        self.is_fullscreen = False
        
        # Color scheme
        self.bg_color = '#282a36'
        self.fg_color = '#f8f8f2'
        self.accent_color = '#bd93f9'
        self.link_color = '#8be9fd'  # Bright blue for links
        self.hover_color = '#6272a4'
        
        self.root.configure(bg=self.bg_color)
        
        # Custom window controls
        self.create_title_bar()
        
        # Initialize variables
        self.links = []
        self.current_page = 1
        self.query = ""
        self.total_pages = 1
        
        # Create widgets
        self.create_widgets()
        self.bind_events()
        
    def create_title_bar(self):
        title_bar = tk.Frame(self.root, bg=self.bg_color, relief='raised', bd=0)
        title_bar.pack(fill=tk.X)
        
        # Title
        title_label = tk.Label(
            title_bar, text="Ghost Search", 
            bg=self.bg_color, fg=self.accent_color,
            font=('Segoe UI', 10, 'bold')
        )
        title_label.pack(side=tk.LEFT, padx=10)
        
        # Window controls
        controls_frame = tk.Frame(title_bar, bg=self.bg_color)
        controls_frame.pack(side=tk.RIGHT)
        
        # Minimize button
        minimize_btn = tk.Label(
            controls_frame, text='─', 
            bg=self.bg_color, fg=self.fg_color,
            font=('Segoe UI', 12), padx=15
        )
        minimize_btn.pack(side=tk.LEFT)
        minimize_btn.bind('<Button-1>', lambda e: self.root.iconify())
        minimize_btn.bind('<Enter>', lambda e: minimize_btn.config(bg=self.hover_color))
        minimize_btn.bind('<Leave>', lambda e: minimize_btn.config(bg=self.bg_color))
        
        # Fullscreen toggle button
        self.fullscreen_btn = tk.Label(
            controls_frame, text='□', 
            bg=self.bg_color, fg=self.fg_color,
            font=('Segoe UI', 10), padx=15
        )
        self.fullscreen_btn.pack(side=tk.LEFT)
        self.fullscreen_btn.bind('<Button-1>', self.toggle_fullscreen)
        self.fullscreen_btn.bind('<Enter>', lambda e: self.fullscreen_btn.config(bg=self.hover_color))
        self.fullscreen_btn.bind('<Leave>', lambda e: self.fullscreen_btn.config(bg=self.bg_color))
        
        # Close button
        close_btn = tk.Label(
            controls_frame, text='×', 
            bg=self.bg_color, fg=self.fg_color,
            font=('Segoe UI', 12), padx=15
        )
        close_btn.pack(side=tk.LEFT)
        close_btn.bind('<Button-1>', lambda e: self.root.destroy())
        close_btn.bind('<Enter>', lambda e: close_btn.config(bg='#ff5555'))
        close_btn.bind('<Leave>', lambda e: close_btn.config(bg=self.bg_color))
        
        # Move window
        title_bar.bind('<B1-Motion>', self.move_window)
        title_bar.bind('<Button-1>', self.get_pos)
        
    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)
        self.fullscreen_btn.config(text='❒' if self.is_fullscreen else '□')
        
    def move_window(self, event):
        if not self.is_fullscreen:
            x = self.root.winfo_pointerx() - self._x
            y = self.root.winfo_pointery() - self._y
            self.root.geometry(f'+{x}+{y}')
        
    def get_pos(self, event):
        self._x = event.x
        self._y = event.y
        
    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Search frame
        search_frame = tk.Frame(main_frame, bg=self.bg_color)
        search_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.entry = tk.Entry(
            search_frame, 
            font=('Segoe UI', 12),
            bg='#44475a',
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=self.hover_color,
            highlightcolor=self.accent_color
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.entry.bind('<Return>', lambda e: self.search())
        
        self.search_btn = tk.Button(
            search_frame, 
            text="Search", 
            command=self.search,
            bg=self.accent_color,
            fg='#282a36',
            activebackground=self.hover_color,
            activeforeground=self.fg_color,
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            bd=0,
            padx=20
        )
        self.search_btn.pack(side=tk.LEFT)
        
        # Results frame with Treeview
        results_frame = tk.Frame(main_frame, bg=self.bg_color)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Custom style for Treeview with blue links
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure(
            'BlueLink.Treeview',
            background='#44475a',
            foreground=self.link_color,  # Blue links
            fieldbackground='#44475a',
            rowheight=35,
            font=('Segoe UI', 10)
        )
        style.configure(
            'BlueLink.Treeview.Heading',
            background=self.hover_color,
            foreground=self.fg_color,
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT
        )
        style.map(
            'BlueLink.Treeview',
            background=[('selected', self.accent_color)],
            foreground=[('selected', '#282a36')]
        )
        
        self.tree = ttk.Treeview(
            results_frame,
            columns=('title', 'domain'),
            show='headings',
            style='BlueLink.Treeview'
        )
        
        self.tree.heading('title', text='Title')
        self.tree.heading('domain', text='Domain')
        self.tree.column('title', width=500, anchor='w')
        self.tree.column('domain', width=150, anchor='w')
        
        # Custom scrollbar
        scrollbar = ttk.Scrollbar(
            results_frame,
            orient='vertical',
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Pagination frame
        pagination_frame = tk.Frame(main_frame, bg=self.bg_color)
        pagination_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.prev_btn = tk.Button(
            pagination_frame,
            text="◀",
            command=self.prev_page,
            bg=self.hover_color,
            fg=self.fg_color,
            activebackground=self.accent_color,
            activeforeground='#282a36',
            font=('Segoe UI', 10),
            relief=tk.FLAT,
            bd=0,
            state=tk.DISABLED
        )
        self.prev_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.page_label = tk.Label(
            pagination_frame,
            text="Page 1",
            bg=self.bg_color,
            fg=self.fg_color,
            font=('Segoe UI', 10)
        )
        self.page_label.pack(side=tk.LEFT)
        
        self.next_btn = tk.Button(
            pagination_frame,
            text="▶",
            command=self.next_page,
            bg=self.hover_color,
            fg=self.fg_color,
            activebackground=self.accent_color,
            activeforeground='#282a36',
            font=('Segoe UI', 10),
            relief=tk.FLAT,
            bd=0,
            state=tk.DISABLED
        )
        self.next_btn.pack(side=tk.LEFT, padx=(5, 0))
        
    def bind_events(self):
        self.tree.bind('<Double-1>', self.open_link)
        # Escape key exits fullscreen
        self.root.bind('<Escape>', lambda e: self.toggle_fullscreen() if self.is_fullscreen else None)
    
    def activate_easter_egg(self):
        """Special Easter Egg for Shashank"""
        # Create a new top-level window
        easter_window = tk.Toplevel(self.root)
        easter_window.title("🎉 Ghost Mode Activated 👻")
        easter_window.geometry("600x400")
        easter_window.configure(bg="#1a1a2e")
        
        # Make window semi-transparent
        easter_window.attributes('-alpha', 0.95)
        
        # Greeting message
        greeting = tk.Label(
            easter_window,
            text="Hello Shashank!",
            font=('Segoe UI', 24, 'bold'),
            fg="#ff9d00",  # Orange text
            bg="#1a1a2e"
        )
        greeting.pack(pady=(40, 20))
        
        # Message
        message = tk.Label(
            easter_window,
            text="You've discovered the secret Ghost Mode!",
            font=('Segoe UI', 16),
            fg="#f8f8f2",
            bg="#1a1a2e",
            wraplength=500
        )
        message.pack(pady=10)
        
        # Changing colors randomly
        colors = ["#ff9d00", "#ff2e63", "#08d9d6", "#54e346", "#a742f5"]
        
        def change_color():
            greeting.config(fg=random.choice(colors))
            message.config(fg=random.choice(colors))
            easter_window.after(500, change_color)
        
        # Animation effect
        def animate_text():
            current_text = message.cget("text")
            if "!!!" in current_text:
                message.config(text="You've discovered the secret Ghost Mode!")
            else:
                message.config(text="You've discovered the secret Ghost Mode!!!")
            easter_window.after(1000, animate_text)
        
        # Add a cool ghost image (ASCII art)
        ghost_art = """
                   .-.
                  (o o)
                  | O |
                   \-/
                   /|\\
                  / | \\
        """
        
        ghost_label = tk.Label(
            easter_window,
            text=ghost_art,
            font=('Courier', 18, 'bold'),
            fg="#ffffff",
            bg="#1a1a2e",
            justify=tk.LEFT
        )
        ghost_label.pack(pady=20)
        
        # Add a close button
        close_btn = tk.Button(
            easter_window,
            text="Close Ghost Mode",
            command=easter_window.destroy,
            bg="#ff2e63",
            fg="#ffffff",
            activebackground="#ff9d00",
            activeforeground="#1a1a2e",
            font=('Segoe UI', 12, 'bold'),
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=10
        )
        close_btn.pack(pady=20)
        
        # Start animations
        change_color()
        animate_text()
        
        # Center the window
        easter_window.update_idletasks()
        width = easter_window.winfo_width()
        height = easter_window.winfo_height()
        x = (easter_window.winfo_screenwidth() // 2) - (width // 2)
        y = (easter_window.winfo_screenheight() // 2) - (height // 2)
        easter_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Bring to front
        easter_window.lift()
        easter_window.focus_force()
        
    def search(self, page=1):
        self.query = self.entry.get()
        
        # Check for Easter Egg
        if self.query == "(--Ghost_--shashank__)":
            self.activate_easter_egg()
            return
            
        if not self.query.strip():
            messagebox.showinfo("Input Required", "Please enter a search query.")
            return
            
        self.current_page = page
        self.tree.delete(*self.tree.get_children())
        self.links = []
        
        try:
            results = google_search(self.query, num_results=10, start=(page-1)*10 + 1)
            if not results:
                messagebox.showinfo("No Results", "No search results found.")
                return
                
            for item in results:
                title = item["title"]
                link = item["link"]
                domain = urlparse(link).netloc.replace("www.", "")
                
                self.tree.insert("", tk.END, values=(title, domain))
                self.links.append(link)
                
            self.total_pages = 5  # Google typically allows up to 5 pages (50 results)
            self.update_pagination_buttons()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def open_link(self, event):
        item = self.tree.selection()
        if item:
            index = self.tree.index(item[0])
            webbrowser.open(self.links[index])
    
    def next_page(self):
        if self.current_page < self.total_pages:
            self.search(self.current_page + 1)
    
    def prev_page(self):
        if self.current_page > 1:
            self.search(self.current_page - 1)
    
    def update_pagination_buttons(self):
        self.page_label.config(text=f"Page {self.current_page}")
        
        self.prev_btn.config(
            state=tk.NORMAL if self.current_page > 1 else tk.DISABLED,
            bg=self.hover_color if self.current_page > 1 else '#44475a'
        )
        self.next_btn.config(
            state=tk.NORMAL if self.current_page < self.total_pages else tk.DISABLED,
            bg=self.hover_color if self.current_page < self.total_pages else '#44475a'
        )

def google_search(query, num_results=10, start=1):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CX,
        "q": query,
        "num": num_results,
        "start": start
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        messagebox.showerror("API Error", f"{response.status_code}: {response.text}")
        return []

if __name__ == "__main__":
    root = tk.Tk()
    app = GhostSearchApp(root)
    root.mainloop()
    