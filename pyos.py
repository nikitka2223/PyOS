import tkinter as tk
import os, sys, importlib.util, hashlib, json

class PyOS:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PyOS Kernel")
        self.root.geometry("1000x600")
        self.root.configure(bg="#1e1f29")
        
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.pkg_dir = os.path.join(self.base_dir, "packages")
        self.sys_dir = os.path.join(self.base_dir, "system")
        self.db_path = os.path.join(self.sys_dir, "users.db")
        
        self.current_user = None
        self.is_admin = False
        self.login_step = "user" 
        self.temp_user = ""
        self.command_history = []
        self.history_index = -1

        self.txt = tk.Text(self.root, bg="#1e1f29", fg="#f8f8f2", font=("monospace", 12), 
                           insertbackground="white", relief=tk.FLAT, padx=10, pady=10)
        self.txt.pack(expand=True, fill=tk.BOTH)
        
        self.init_system()
        self.boot_system()
        
        self.txt.bind("<Return>", self.handle)
        self.txt.bind("<Up>", self.history_up)
        self.txt.bind("<Down>", self.history_down)
        self.txt.bind("<BackSpace>", self.prevent_erase)
        self.root.mainloop()

    def init_system(self):
        os.makedirs(self.pkg_dir, exist_ok=True)
        os.makedirs(self.sys_dir, exist_ok=True)
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w") as f: json.dump({}, f)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def boot_system(self):
        self.current_user = None
        self.txt.delete("1.0", "end")
        with open(self.db_path, "r") as f: db = json.load(f)
        if not db:
            self.txt.insert("end", "First boot: Create ROOT account\nPassword: ")
            self.login_step = "create_root"
        else:
            self.txt.insert("end", "PyOS Kernel v4.5.1\nLogin: ")
            self.login_step = "user"
        self.mark_input()

    def mark_input(self):
        self.txt.mark_set("input_start", "insert-1c")
        self.txt.see("end")

    def prevent_erase(self, event):
        if self.txt.compare("insert", "<=", "input_start + 1c"):
            return "break"

    def history_up(self, event):
        if self.current_user and self.command_history:
            if self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                self._replace_input_with_history()
        return "break"

    def history_down(self, event):
        if self.current_user and self.history_index >= 0:
            self.history_index -= 1
            self._replace_input_with_history()
        return "break"

    def _replace_input_with_history(self):
        self.txt.delete("input_start + 1c", "end")
        if self.history_index >= 0:
            cmd = self.command_history[-(self.history_index + 1)]
            self.txt.insert("end", cmd)
        self.txt.mark_set("insert", "end")

    def handle(self, event):
        raw = self.txt.get("input_start + 1c", "end").strip()
        self.txt.insert("end", "\n")
        if self.current_user is None:
            self.process_login(raw)
            return "break"
        if raw:
            self.command_history.append(raw)
            self.history_index = -1
            parts = raw.split()
            cmd, args = parts[0].lower(), parts[1:]
            if cmd == "newuser": self.cmd_newuser(args)
            elif cmd == "su": self.boot_system()
            elif cmd == "help": self.show_help()
            elif cmd == "clear": self.txt.delete("1.0", "end")
            elif cmd == "exit": self.root.destroy(); sys.exit()
            else: self.run_module(cmd, args)
        if self.current_user:
            self.draw_prompt()
        return "break"

    def process_login(self, val):
        if self.login_step == "create_root":
            db = {"root": {"pass": self.hash_password(val), "admin": True}}
            with open(self.db_path, "w") as f: json.dump(db, f)
            self.boot_system()
        elif self.login_step == "user":
            self.temp_user = val
            self.login_step = "pass"
            self.txt.insert("end", "Password: ")
            self.mark_input()
        elif self.login_step == "pass":
            with open(self.db_path, "r") as f: db = json.load(f)
            if self.temp_user in db and db[self.temp_user]["pass"] == self.hash_password(val):
                self.current_user = self.temp_user
                self.is_admin = db[self.temp_user]["admin"]
                self.txt.insert("end", f"Logged in as {self.current_user}\n")
                self.run_module("pyfetch", [])
                self.draw_prompt()
            else:
                self.txt.insert("end", "Denied.\nLogin: ")
                self.login_step = "user"
                self.mark_input()

    def draw_prompt(self):
        prefix = "#" if self.is_admin else "$"
        self.txt.insert("end", f"[{self.current_user}@pyos]:~{prefix} ")
        self.txt.mark_set("input_start", "insert-1c")
        self.txt.see("end")

    def show_help(self):
        pkgs = [f[:-3] for f in os.listdir(self.pkg_dir) if f.endswith('.py') and f != "__init__.py"]
        self.txt.insert("end", f"Built-in: newuser, su, clear, exit, help\nModules: {', '.join(pkgs)}\n")

    def cmd_newuser(self, args):
        if not self.is_admin:
            self.txt.insert("end", "Access denied.\n")
            return
        if len(args) < 3:
            self.txt.insert("end", "Usage: newuser <name> <pass> <admin:true/false>\n")
            return
        with open(self.db_path, "r") as f: db = json.load(f)
        db[args[0]] = {"pass": self.hash_password(args[1]), "admin": args[2].lower() == "true"}
        with open(self.db_path, "w") as f: json.dump(db, f)
        self.txt.insert("end", f"User {args[0]} created.\n")

    def run_module(self, name, args):
        path = os.path.join(self.pkg_dir, f"{name}.py")
        if os.path.exists(path):
            try:
                spec = importlib.util.spec_from_file_location(name, path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                mod.run(self.root, args, self.txt)
            except Exception as e:
                self.txt.insert("end", f"Error: {e}\n")
        else:
            self.txt.insert("end", f"pyos: {name}: command not found\n")

if __name__ == "__main__":
    PyOS()