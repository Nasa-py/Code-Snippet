import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
from datetime import datetime
import re

class CodeSnippetManager:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Code Snippet Manager")
        self.root.geometry("1200x700")
        
        # Dark mode colors
        self.bg_dark = "#1e1e2e"
        self.bg_secondary = "#2b2b3c"
        self.bg_tertiary = "#363650"
        self.accent = "#89b4fa"
        self.accent_hover = "#b4befe"
        self.text_primary = "#cdd6f4"
        self.text_secondary = "#a6adc8"
        self.success = "#a6e3a1"
        self.warning = "#f9e2af"
        self.error = "#f38ba8"
        
        self.root.configure(bg=self.bg_dark)
        
        # File extensions mapping
        self.language_extensions = {
            "Python": ".py",
            "JavaScript": ".js",
            "Java": ".java",
            "C++": ".cpp",
            "HTML": ".html",
            "CSS": ".css",
            "SQL": ".sql",
            "Ruby": ".rb",
            "Go": ".go",
            "Rust": ".rs",
            "TypeScript": ".ts",
            "PHP": ".php",
            "C": ".c",
            "C#": ".cs",
            "Swift": ".swift",
            "Kotlin": ".kt",
            "Other": ".txt"
        }
        
        # Create base directory for snippets
        self.base_dir = "Code_Snippets"
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
        
        # Metadata file
        self.metadata_file = os.path.join(self.base_dir, "snippets_metadata.json")
        self.snippets = self.load_snippets()
        self.current_snippet = None
        
        # Container for switching views
        self.container = tk.Frame(self.root, bg=self.bg_dark)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        self.show_home_page()
        
    def load_snippets(self):
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_metadata(self):
        with open(self.metadata_file, 'w') as f:
            json.dump(self.snippets, f, indent=2)
    
    def get_language_folder(self, language):
        """Get or create folder for specific language"""
        folder = os.path.join(self.base_dir, language)
        if not os.path.exists(folder):
            os.makedirs(folder)
        return folder
    
    def sanitize_filename(self, title):
        """Convert title to valid filename"""
        # Remove invalid characters
        valid = re.sub(r'[<>:"/\\|?*]', '', title)
        # Replace spaces with underscores
        valid = valid.replace(' ', '_')
        return valid if valid else "untitled"
    
    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()
    
    def show_home_page(self):
        self.clear_container()
        self.current_snippet = None
        
        # Reload snippets from file to get latest
        self.snippets = self.load_snippets()
        print(f"📊 Loading home page with {len(self.snippets)} snippets")  # Debug
        
        # Main home container
        home_frame = tk.Frame(self.container, bg=self.bg_dark)
        home_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header section
        header_frame = tk.Frame(home_frame, bg=self.bg_dark)
        header_frame.pack(fill=tk.X, pady=(40, 30))
        
        title = tk.Label(header_frame, text="📝 Code Snippets", 
                        font=("Segoe UI", 48, "bold"),
                        bg=self.bg_dark, fg=self.accent)
        title.pack()
        
        subtitle = tk.Label(header_frame, text="Your personal code library saved as real files",
                           font=("Segoe UI", 14),
                           bg=self.bg_dark, fg=self.text_secondary)
        subtitle.pack(pady=(10, 0))
        
        # Search and New Snippet section
        search_frame = tk.Frame(home_frame, bg=self.bg_dark)
        search_frame.pack(pady=30)
        
        # Search container
        search_container = tk.Frame(search_frame, bg=self.bg_secondary, height=50)
        search_container.pack(side=tk.LEFT, padx=(0, 15))
        
        search_icon = tk.Label(search_container, text="🔍", bg=self.bg_secondary,
                              fg=self.text_secondary, font=("Segoe UI", 16))
        search_icon.pack(side=tk.LEFT, padx=(15, 10))
        
        self.home_search_var = tk.StringVar()
        self.home_search_var.trace('w', lambda *args: self.filter_home_snippets())
        search_entry = tk.Entry(search_container, textvariable=self.home_search_var,
                               bg=self.bg_secondary, fg=self.text_primary,
                               relief=tk.FLAT, font=("Segoe UI", 14),
                               insertbackground=self.accent, width=40,
                               bd=0)
        search_entry.pack(side=tk.LEFT, padx=(0, 15), ipady=10)
        
        # New Snippet button
        new_btn = tk.Button(search_frame, text="✨ New Snippet",
                           command=self.show_editor_page,
                           bg=self.accent, fg=self.bg_dark,
                           relief=tk.FLAT, font=("Segoe UI", 14, "bold"),
                           cursor="hand2", padx=30, pady=12,
                           activebackground=self.accent_hover,
                           activeforeground=self.bg_dark)
        new_btn.pack(side=tk.LEFT)
        
        # Snippets grid container
        snippets_container = tk.Frame(home_frame, bg=self.bg_dark)
        snippets_container.pack(fill=tk.BOTH, expand=True, padx=60, pady=(0, 40))
        
        # Canvas for scrolling
        canvas = tk.Canvas(snippets_container, bg=self.bg_dark, highlightthickness=0)
        scrollbar = tk.Scrollbar(snippets_container, orient=tk.VERTICAL, command=canvas.yview,
                                bg=self.bg_tertiary)
        
        self.snippets_grid_frame = tk.Frame(canvas, bg=self.bg_dark)
        
        canvas.create_window((0, 0), window=self.snippets_grid_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.snippets_grid_frame.bind('<Configure>', 
                                     lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Mouse wheel binding - fix for when switching pages
        def on_mousewheel(event):
            try:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except:
                pass
        
        canvas.bind("<MouseWheel>", on_mousewheel)
        self.snippets_grid_frame.bind("<MouseWheel>", on_mousewheel)
        
        self.display_snippet_cards()
    
    def display_snippet_cards(self, filtered_snippets=None):
        for widget in self.snippets_grid_frame.winfo_children():
            widget.destroy()
        
        snippets_to_show = filtered_snippets if filtered_snippets is not None else self.snippets
        
        print(f"🎨 Displaying {len(snippets_to_show)} snippet cards")  # Debug
        
        if not snippets_to_show:
            empty_frame = tk.Frame(self.snippets_grid_frame, bg=self.bg_dark)
            empty_frame.pack(expand=True, pady=150)
            
            # Big emoji
            emoji_label = tk.Label(empty_frame, text="📂", 
                                  font=("Segoe UI", 80),
                                  bg=self.bg_dark, fg=self.text_secondary)
            emoji_label.pack()
            
            empty_label = tk.Label(empty_frame, 
                                  text="No snippets yet!",
                                  font=("Segoe UI", 24, "bold"),
                                  bg=self.bg_dark, fg=self.text_primary)
            empty_label.pack(pady=(20, 10))
            
            empty_sub = tk.Label(empty_frame, 
                                text="Click '✨ New Snippet' above to create your first code file",
                                font=("Segoe UI", 14),
                                bg=self.bg_dark, fg=self.text_secondary)
            empty_sub.pack()
            return
        
        # Create grid of cards (3 columns)
        for idx, snippet in enumerate(snippets_to_show):
            row = idx // 3
            col = idx % 3
            
            card = self.create_snippet_card(self.snippets_grid_frame, snippet)
            card.grid(row=row, column=col, padx=15, pady=15, sticky=tk.NSEW)
        
        # Configure grid weights
        for i in range(3):
            self.snippets_grid_frame.columnconfigure(i, weight=1, minsize=300)
    
    def create_snippet_card(self, parent, snippet):
        print(f"🎴 Creating card for: {snippet.get('title', 'Unknown')}")  # Debug
        
        card = tk.Frame(parent, bg=self.bg_secondary, cursor="hand2", width=350, height=250)
        card.grid_propagate(False)
        
        # Header with language badge and file extension
        header = tk.Frame(card, bg=self.bg_secondary)
        header.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        lang_badge = tk.Label(header, text=snippet.get('language', 'Unknown'),
                             bg=self.accent, fg=self.bg_dark,
                             font=("Segoe UI", 9, "bold"),
                             padx=10, pady=3)
        lang_badge.pack(side=tk.LEFT)
        
        # Show file extension
        ext_label = tk.Label(header, text=snippet.get('extension', ''),
                            bg=self.bg_tertiary, fg=self.success,
                            font=("Consolas", 9, "bold"),
                            padx=8, pady=3)
        ext_label.pack(side=tk.LEFT, padx=(5, 0))
        
        date_label = tk.Label(header, text=snippet.get('created', '').split()[0],
                             bg=self.bg_secondary, fg=self.text_secondary,
                             font=("Segoe UI", 8))
        date_label.pack(side=tk.RIGHT)
        
        # Title with filename
        title = tk.Label(card, text=snippet.get('title', 'Untitled'),
                        bg=self.bg_secondary, fg=self.text_primary,
                        font=("Segoe UI", 16, "bold"),
                        anchor=tk.W, wraplength=250)
        title.pack(fill=tk.X, padx=20, pady=(5, 5))
        
        # Show actual filename
        filename_label = tk.Label(card, text=f"📄 {snippet.get('filename', 'N/A')}",
                                 bg=self.bg_secondary, fg=self.text_secondary,
                                 font=("Consolas", 9),
                                 anchor=tk.W)
        filename_label.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Code preview
        code_preview = snippet.get('code_preview', 'No preview')
        code_label = tk.Label(card, text=code_preview,
                             bg=self.bg_tertiary, fg=self.text_secondary,
                             font=("Consolas", 9),
                             anchor=tk.W, justify=tk.LEFT,
                             wraplength=250, height=4)
        code_label.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Tags preview
        if snippet.get('tags'):
            tags_text = " ".join([f"#{tag}" for tag in snippet['tags'][:3]])
            if len(snippet['tags']) > 3:
                tags_text += f" +{len(snippet['tags']) - 3}"
            
            tags_label = tk.Label(card, text=tags_text,
                                 bg=self.bg_secondary, fg=self.accent,
                                 font=("Segoe UI", 9),
                                 anchor=tk.W)
            tags_label.pack(fill=tk.X, padx=20, pady=(0, 15))
        else:
            tags_label = None
        
        # Hover effect
        def on_enter(e):
            card.config(bg=self.bg_tertiary)
            header.config(bg=self.bg_tertiary)
            title.config(bg=self.bg_tertiary)
            filename_label.config(bg=self.bg_tertiary)
            if tags_label:
                tags_label.config(bg=self.bg_tertiary)
            date_label.config(bg=self.bg_tertiary)
        
        def on_leave(e):
            card.config(bg=self.bg_secondary)
            header.config(bg=self.bg_secondary)
            title.config(bg=self.bg_secondary)
            filename_label.config(bg=self.bg_secondary)
            if tags_label:
                tags_label.config(bg=self.bg_secondary)
            date_label.config(bg=self.bg_secondary)
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        card.bind("<Button-1>", lambda e, s=snippet: self.show_editor_page(s))
        
        # Bind all children too
        for child in [header, title, filename_label, code_label, lang_badge, ext_label, date_label]:
            child.bind("<Enter>", on_enter)
            child.bind("<Leave>", on_leave)
            child.bind("<Button-1>", lambda e, s=snippet: self.show_editor_page(s))
        
        if tags_label:
            tags_label.bind("<Enter>", on_enter)
            tags_label.bind("<Leave>", on_leave)
            tags_label.bind("<Button-1>", lambda e, s=snippet: self.show_editor_page(s))
        
        return card
    
    def filter_home_snippets(self):
        search_term = self.home_search_var.get().lower()
        if not search_term:
            self.display_snippet_cards()
            return
        
        filtered = [s for s in self.snippets if 
                   search_term in s['title'].lower() or 
                   search_term in s['language'].lower() or
                   search_term in s.get('filename', '').lower() or
                   any(search_term in tag for tag in s.get('tags', []))]
        self.display_snippet_cards(filtered)
    
    def show_editor_page(self, snippet=None):
        self.clear_container()
        self.current_snippet = snippet
        
        editor_frame = tk.Frame(self.container, bg=self.bg_dark)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with back button
        header = tk.Frame(editor_frame, bg=self.bg_secondary, height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Back button
        back_btn = tk.Button(header, text="← Back",
                            command=self.show_home_page,
                            bg=self.bg_tertiary, fg=self.text_primary,
                            relief=tk.FLAT, font=("Segoe UI", 12, "bold"),
                            cursor="hand2", padx=20, pady=10,
                            activebackground=self.bg_dark)
        back_btn.pack(side=tk.LEFT, padx=20, pady=15)
        
        title_text = "✏️ Edit Snippet" if snippet else "✨ Create New Snippet"
        title_label = tk.Label(header, text=title_text,
                              font=("Segoe UI", 18, "bold"),
                              bg=self.bg_secondary, fg=self.accent)
        title_label.pack(side=tk.LEFT, padx=20)
        
        # Main content
        content_frame = tk.Frame(editor_frame, bg=self.bg_dark)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # Input fields
        input_frame = tk.Frame(content_frame, bg=self.bg_dark)
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(input_frame, text="Snippet Title (Filename)", bg=self.bg_dark,
                fg=self.text_secondary, font=("Segoe UI", 10)).grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        
        self.title_entry = tk.Entry(input_frame, bg=self.bg_secondary,
                                    fg=self.text_primary, relief=tk.FLAT,
                                    font=("Segoe UI", 12),
                                    insertbackground=self.accent)
        self.title_entry.grid(row=1, column=0, sticky=tk.EW, ipady=12, padx=(0, 20))
        
        tk.Label(input_frame, text="Language", bg=self.bg_dark,
                fg=self.text_secondary, font=("Segoe UI", 10)).grid(row=0, column=1, sticky=tk.W, pady=(0, 8))
        
        self.lang_var = tk.StringVar(value="Python")
        lang_combo = ttk.Combobox(input_frame, textvariable=self.lang_var,
                                 values=list(self.language_extensions.keys()),
                                 state="readonly", font=("Segoe UI", 11))
        lang_combo.grid(row=1, column=1, sticky=tk.EW)
        
        # Show preview of filename
        self.filename_preview = tk.Label(input_frame, text="",
                                        bg=self.bg_dark, fg=self.success,
                                        font=("Consolas", 10, "bold"))
        self.filename_preview.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(8, 0))
        
        # Update filename preview on change
        def update_preview(*args):
            title = self.title_entry.get().strip()
            lang = self.lang_var.get()
            if title and lang:
                filename = self.sanitize_filename(title) + self.language_extensions[lang]
                self.filename_preview.config(text=f"💾 Will save as: {filename}")
            else:
                self.filename_preview.config(text="")
        
        self.title_entry.bind('<KeyRelease>', update_preview)
        self.lang_var.trace('w', update_preview)
        
        input_frame.columnconfigure(0, weight=3)
        input_frame.columnconfigure(1, weight=1)
        
        # Code editor
        tk.Label(content_frame, text="Code", bg=self.bg_dark,
                fg=self.text_secondary, font=("Segoe UI", 10)).pack(anchor=tk.W, pady=(10, 8))
        
        editor_container = tk.Frame(content_frame, bg=self.bg_secondary)
        editor_container.pack(fill=tk.BOTH, expand=False, pady=(0, 15))
        
        self.code_text = scrolledtext.ScrolledText(editor_container, bg=self.bg_tertiary,
                                                   fg=self.text_primary, relief=tk.FLAT,
                                                   font=("Consolas", 11),
                                                   insertbackground=self.accent,
                                                   wrap=tk.NONE, padx=10, pady=10,
                                                   height=12)
        self.code_text.pack(fill=tk.BOTH, expand=False)
        
        # Tags section
        tk.Label(content_frame, text="AI-Generated Tags", bg=self.bg_dark,
                fg=self.text_secondary, font=("Segoe UI", 10)).pack(anchor=tk.W, pady=(10, 8))
        
        tags_container = tk.Frame(content_frame, bg=self.bg_secondary, height=65)
        tags_container.pack(fill=tk.X, pady=(0, 15))
        tags_container.pack_propagate(False)
        
        self.tags_canvas = tk.Canvas(tags_container, bg=self.bg_secondary,
                                     height=65, highlightthickness=0)
        self.tags_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        tags_scrollbar = tk.Scrollbar(tags_container, orient=tk.HORIZONTAL,
                                     command=self.tags_canvas.xview,
                                     bg=self.bg_tertiary)
        tags_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.tags_canvas.configure(xscrollcommand=tags_scrollbar.set)
        
        self.tags_frame = tk.Frame(self.tags_canvas, bg=self.bg_secondary)
        self.tags_canvas.create_window((0, 0), window=self.tags_frame, anchor=tk.NW)
        
        self.tags_canvas.bind('<MouseWheel>', self._on_mousewheel)
        self.tags_frame.bind('<Configure>', lambda e: self.tags_canvas.configure(
            scrollregion=self.tags_canvas.bbox("all")))
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg=self.bg_dark)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        save_btn = tk.Button(button_frame, text="💾 Save as File",
                            command=self.save_snippet,
                            bg=self.accent, fg=self.bg_dark,
                            relief=tk.FLAT, font=("Segoe UI", 14, "bold"),
                            cursor="hand2", padx=35, pady=15,
                            activebackground=self.accent_hover)
        save_btn.pack(side=tk.LEFT, padx=(0, 20))
        
        gen_btn = tk.Button(button_frame, text="🤖 Generate Tags",
                           command=self.generate_tags,
                           bg=self.success, fg=self.bg_dark,
                           relief=tk.FLAT, font=("Segoe UI", 14, "bold"),
                           cursor="hand2", padx=35, pady=15)
        gen_btn.pack(side=tk.LEFT, padx=(0, 20))
        
        if snippet:
            delete_btn = tk.Button(button_frame, text="🗑️ Delete File",
                                  command=self.delete_snippet,
                                  bg=self.error, fg=self.bg_dark,
                                  relief=tk.FLAT, font=("Segoe UI", 14, "bold"),
                                  cursor="hand2", padx=35, pady=15)
            delete_btn.pack(side=tk.LEFT)
        
        # Load snippet data if editing
        if snippet:
            self.title_entry.insert(0, snippet['title'])
            self.lang_var.set(snippet['language'])
            # Load code from file
            filepath = snippet.get('filepath')
            if filepath and os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.code_text.insert("1.0", f.read())
            if snippet.get('tags'):
                self.display_tags(snippet['tags'])
            update_preview()
    
    def generate_tags(self):
        code = self.code_text.get("1.0", tk.END).strip()
        title = self.title_entry.get().strip()
        language = self.lang_var.get()
        
        if not code:
            messagebox.showwarning("Warning", "Please enter some code first!")
            return
        
        tags = set()
        
        # Detect patterns
        if "def " in code or "function " in code:
            tags.add("function")
        if "class " in code:
            tags.add("class")
        if "import " in code or "#include" in code:
            tags.add("imports")
        if any(kw in code for kw in ["if", "else", "switch"]):
            tags.add("conditional")
        if any(kw in code for kw in ["for", "while", "loop"]):
            tags.add("loop")
        if any(kw in code for kw in ["try", "except", "catch"]):
            tags.add("error-handling")
        if any(kw in code for kw in ["async", "await", "Promise"]):
            tags.add("async")
        if "API" in code or "api" in code or "fetch" in code or "request" in code:
            tags.add("api")
        if "file" in code.lower() or "open(" in code:
            tags.add("file-io")
        if any(kw in code.lower() for kw in ["sort", "filter", "map"]):
            tags.add("data-processing")
        
        tags.add(language.lower())
        
        if title:
            title_words = re.findall(r'\w+', title.lower())
            for word in title_words:
                if len(word) > 3:
                    tags.add(word)
        
        self.display_tags(list(tags))
        messagebox.showinfo("Success", f"✨ Generated {len(tags)} AI-powered tags!")
    
    def display_tags(self, tags):
        for widget in self.tags_frame.winfo_children():
            widget.destroy()
        
        tag_colors = {
            'python': '#3776ab', 'javascript': '#f7df1e', 'java': '#007396',
            'c++': '#00599c', 'function': '#a6e3a1', 'class': '#89dceb',
            'loop': '#f9e2af', 'conditional': '#fab387', 'async': '#cba6f7',
            'api': '#f38ba8', 'error-handling': '#eba0ac',
        }
        
        for tag in tags:
            tag_color = tag_colors.get(tag.lower(), self.accent)
            
            tag_container = tk.Frame(self.tags_frame, bg=self.bg_secondary)
            tag_container.pack(side=tk.LEFT, padx=4, pady=10)
            
            tag_label = tk.Label(tag_container, text=f"#{tag}",
                               bg=tag_color, fg=self.bg_dark,
                               font=("Segoe UI", 10, "bold"),
                               padx=12, pady=6, cursor="hand2")
            tag_label.pack(side=tk.LEFT)
            
            remove_btn = tk.Label(tag_container, text="✕",
                                bg=tag_color, fg=self.bg_dark,
                                font=("Segoe UI", 9, "bold"),
                                padx=8, pady=6, cursor="hand2")
            remove_btn.pack(side=tk.LEFT)
            remove_btn.bind("<Button-1>", lambda e, t=tag: self.remove_tag(t))
        
        self.tags_frame.update_idletasks()
        self.tags_canvas.configure(scrollregion=self.tags_canvas.bbox("all"))
    
    def remove_tag(self, tag):
        current_tags = [child.winfo_children()[0].cget("text").replace("#", "") 
                       for child in self.tags_frame.winfo_children()]
        current_tags.remove(tag)
        self.display_tags(current_tags)
    
    def _on_mousewheel(self, event):
        if event.num == 5 or event.delta < 0:
            self.tags_canvas.xview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.tags_canvas.xview_scroll(-1, "units")
    
    def save_snippet(self):
        title = self.title_entry.get().strip()
        code = self.code_text.get("1.0", tk.END).strip()
        language = self.lang_var.get()
        
        if not title or not code:
            messagebox.showwarning("Warning", "Please fill in title and code!")
            return
        
        # Get tags
        tags = []
        try:
            tags = [child.winfo_children()[0].cget("text").replace("#", "") 
                    for child in self.tags_frame.winfo_children() if child.winfo_children()]
        except:
            tags = []
        
        # Create filename and filepath
        filename = self.sanitize_filename(title) + self.language_extensions[language]
        folder = self.get_language_folder(language)
        filepath = os.path.join(folder, filename)
        
        # Check if file exists (for new snippets)
        if not self.current_snippet and os.path.exists(filepath):
            overwrite = messagebox.askyesno("File Exists", 
                                           f"File '{filename}' already exists. Overwrite?")
            if not overwrite:
                return
        
        try:
            # Save the actual code file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Create code preview
            code_preview = code[:100] + "..." if len(code) > 100 else code
            
            # Update or create metadata
            if self.current_snippet:
                # Update existing
                for snippet in self.snippets:
                    if snippet.get('id') == self.current_snippet.get('id'):
                        # Delete old file if name/language changed
                        old_filepath = snippet.get('filepath')
                        if old_filepath and old_filepath != filepath and os.path.exists(old_filepath):
                            os.remove(old_filepath)
                        
                        snippet['title'] = title
                        snippet['language'] = language
                        snippet['filename'] = filename
                        snippet['filepath'] = filepath
                        snippet['extension'] = self.language_extensions[language]
                        snippet['tags'] = tags
                        snippet['code_preview'] = code_preview
                        break
            else:
                # Create new
                new_snippet = {
                    "id": max([s.get('id', 0) for s in self.snippets], default=0) + 1,
                    "title": title,
                    "language": language,
                    "filename": filename,
                    "filepath": filepath,
                    "extension": self.language_extensions[language],
                    "tags": tags,
                    "code_preview": code_preview,
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                self.snippets.append(new_snippet)
            
            # Save metadata
            self.save_metadata()
            
            print(f"✅ Saved snippet: {filename}")  # Debug
            print(f"📁 File location: {filepath}")  # Debug
            print(f"📊 Total snippets now: {len(self.snippets)}")  # Debug
            
            messagebox.showinfo("Success", 
                              f"✨ Code saved as:\n{filename}\n\nLocation:\n{filepath}")
            self.show_home_page()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def delete_snippet(self):
        if not self.current_snippet:
            return
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Delete this snippet and its file?\n\n{self.current_snippet.get('filename', '')}"):
            try:
                # Delete the actual file
                filepath = self.current_snippet.get('filepath')
                if filepath and os.path.exists(filepath):
                    os.remove(filepath)
                
                # Remove from metadata
                self.snippets.remove(self.current_snippet)
                self.save_metadata()
                
                messagebox.showinfo("Deleted", "✅ Snippet and file deleted successfully!")
                self.show_home_page()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeSnippetManager(root)
    root.mainloop()