import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from models import FileSystem, File

class FileSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File System GUI")
        self.fs = FileSystem()
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.frame = tk.Frame(root, padx=10, pady=10)
        self.frame.grid(row=0, column=0, sticky='nsew')
        
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(self.frame, selectmode="browse")
        self.tree.grid(row=0, column=0, sticky='nsew')
        
        self.tree.heading("#0", text="File System", anchor=tk.W)
        
        self.tree.insert('', 'end', '/', text='/', open=True)
        
        self.tree_menu = tk.Menu(self.tree, tearoff=0)
        self.tree_menu.add_command(label="Create File", command=self.create_file_in_tree)
        self.tree_menu.add_command(label="Create Directory", command=self.create_directory_in_tree)
        self.tree_menu.add_command(label="Delete", command=self.delete_in_tree)
        self.tree_menu.add_command(label="Search", command=self.search_in_tree)
        
        self.tree.bind("<Button-3>", self.show_tree_menu)
        self.tree.bind("<Button-1>", self.hide_tree_menu)
        
        self.tree_scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)
        self.tree_scrollbar.grid(row=0, column=1, sticky='ns')

        self.button_frame = tk.Frame(self.frame, pady=5)
        self.button_frame.grid(row=1, column=0, columnspan=2, sticky='ew')  # Adjusted padding here
        
        self.create_drive_button = tk.Button(self.button_frame, text="Create Drive", command=self.create_drive)
        #self.create_drive_button.pack(side=tk.LEFT, padx=5)
        
        self.copy_button = tk.Button(self.button_frame, text="Copy", command=self.copy)
        self.copy_button.pack(side=tk.LEFT, padx=5)
        
        self.move_button = tk.Button(self.button_frame, text="Move", command=self.move)
        self.move_button.pack(side=tk.LEFT, padx=5)
        
        self.rename_button = tk.Button(self.button_frame, text="Rename", command=self.rename)
        self.rename_button.pack(side=tk.LEFT, padx=5)
        
        self.stats_button = tk.Button(self.button_frame, text="Statistics", command=self.show_stats)
        self.stats_button.pack(side=tk.LEFT, padx=5)

        self.non_tree_button_frame = tk.Frame(self.frame, pady=5)
        self.non_tree_button_frame.grid(row=2, column=0, columnspan=2, sticky='ew')  # Adjusted padding here

        self.create_file_button = tk.Button(self.non_tree_button_frame, text="Create File", command=self.create_file)
        self.create_file_button.pack(side=tk.LEFT, padx=5)

        self.read_file_button = tk.Button(self.non_tree_button_frame, text="Read File", command=self.read_file)
        self.read_file_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_button = tk.Button(self.non_tree_button_frame, text="Delete", command=self.delete)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        self.search_button = tk.Button(self.non_tree_button_frame, text="Search", command=self.search)
        self.search_button.pack(side=tk.LEFT, padx=5)
        
        self.populate_tree(self.fs.root, '')

    def show_tree_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.tree_menu.post(event.x_root, event.y_root)

    def hide_tree_menu(self, event):
        self.tree_menu.unpost()

    def create_file_in_tree(self):
        item = self.tree.selection()[0]
        path = self.get_full_path(item)
        name = simpledialog.askstring("Input", "Enter the file name:")
        content = simpledialog.askstring("Input", "Enter the content (optional):")
        if name:
            self.fs.create_file(path, name, content or "")
            self.populate_tree(self.fs.root, '')

    def create_directory_in_tree(self):
        item = self.tree.selection()[0]
        path = self.get_full_path(item)
        name = simpledialog.askstring("Input", "Enter the directory name:")
        if name:
            self.fs._create_directory(f"{path}/{name}")
            self.populate_tree(self.fs.root, '')

    def delete_in_tree(self):
        item = self.tree.selection()[0]
        path = self.get_full_path(item)
        self.fs.delete(path)
        self.populate_tree(self.fs.root, '')

    def search_in_tree(self):
        item = self.tree.selection()[0]
        path = self.get_full_path(item)
        search_term = simpledialog.askstring("Input", "Enter the search term:")
        if search_term:
            results = self.fs.search(path, search_term)
            result_str = "\n".join([f"Name: {res.name}, Type: {'File' if isinstance(res, File) else 'Directory'}" for res in results])
            messagebox.showinfo("Search Results", f"Search results for '{search_term}':\n{result_str}")

    def create_drive(self):
        drive_name = simpledialog.askstring("Input", "Enter the drive name:")
        if drive_name:
            self.fs.create_virtual_drive(drive_name)
            self.fs.load_state(drive_name)
            self.populate_tree(self.fs.root, '')

    def copy(self):
        source = simpledialog.askstring("Input", "Enter the source path:")
        destination = simpledialog.askstring("Input", "Enter the destination path:")
        if source and destination:
            self.fs.copy(source, destination)
            self.populate_tree(self.fs.root, '')

    def move(self):
        source = simpledialog.askstring("Input", "Enter the source path:")
        destination = simpledialog.askstring("Input", "Enter the destination path:")
        if source and destination:
            self.fs.move(source, destination)
            self.populate_tree(self.fs.root, '')

    def rename(self):
        path = simpledialog.askstring("Input", "Enter the path to rename:")
        new_name = simpledialog.askstring("Input", "Enter the new name:")
        if path and new_name:
            self.fs.rename(path, new_name)
            self.populate_tree(self.fs.root, '')

    def show_stats(self):
        stats = self.fs.statistics()
        messagebox.showinfo("Statistics", f"Total Files: {stats['total_files']}\nTotal Directories: {stats['total_directories']}\nTotal Size: {stats['total_size']} bytes")

    def create_file(self):
        path = simpledialog.askstring("Input", "Enter the path to create file:")
        name = simpledialog.askstring("Input", "Enter the file name:")
        content = simpledialog.askstring("Input", "Enter the content (optional):")
        if path and name:
            self.fs.create_file(path, name, content or "")
            self.populate_tree(self.fs.root, '')

    def delete(self):
        path = simpledialog.askstring("Input", "Enter the path to delete:")
        if path:
            self.fs.delete(path)
            self.populate_tree(self.fs.root, '')

    def search(self):
        path = simpledialog.askstring("Input", "Enter the path to search in:")
        search_term = simpledialog.askstring("Input", "Enter the search term:")
        if path and search_term:
            results = self.fs.search(path, search_term)
            result_str = "\n".join([f"Name: {res.name}, Type: {'File' if isinstance(res, File) else 'Directory'}" for res in results])
            messagebox.showinfo("Search Results", f"Search results for '{search_term}':\n{result_str}")

    def read_file(self):
        path = simpledialog.askstring("Input", "Enter the path to the file to read:")
        if path:
            results = self.fs.read_file(path)
            if results:
                messagebox.showinfo("Read File", f"Content of '{path}':\n{results}")

    def get_full_path(self, item):
        path = ""
        while item != '':
            path = f"/{self.tree.item(item, 'text')}" + path
            item = self.tree.parent(item)
        return path

    def populate_tree(self, directory, parent):
        for item in self.tree.get_children(parent):
            self.tree.delete(item)
        
        self._populate_tree(directory, parent)

    def _populate_tree(self, directory, parent):
        for dir_name, dir in directory.directories.items():
            node_id = self.tree.insert(parent, 'end', text=dir_name, open=True)
            self._populate_tree(dir, node_id)
        
        for file_name in directory.files.keys():
            self.tree.insert(parent, 'end', text=file_name)

if __name__ == "__main__":
    root = tk.Tk()
    gui = FileSystemGUI(root)
    root.mainloop()
