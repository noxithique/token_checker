
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import requests
import os
import threading

OUTPUT_DIR = "output_gui"
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_PATHS = {
    "valid": os.path.join(OUTPUT_DIR, "valid.txt"),
    "invalid": os.path.join(OUTPUT_DIR, "invalid.txt"),
    "locked": os.path.join(OUTPUT_DIR, "locked.txt"),
    "nitro": os.path.join(OUTPUT_DIR, "nitro.txt"),
    "boosts_0": os.path.join(OUTPUT_DIR, "boosts_0.txt"),
    "boosts_1": os.path.join(OUTPUT_DIR, "boosts_1.txt"),
    "boosts_2": os.path.join(OUTPUT_DIR, "boosts_2plus.txt")
}

def save_token(token, category):
    with open(OUTPUT_PATHS[category], "a") as f:
        f.write(token + "\n")

def check_token(token, log_callback):
    headers = {"Authorization": token}
    try:
        r = requests.get("https://discord.com/api/v10/users/@me", headers=headers, timeout=10)
        if r.status_code == 200:
            user = r.json()
            premium = user.get("premium_type", 0)
            save_token(token, "valid")
            if premium != 0:
                save_token(token, "nitro")

            boost_headers = headers.copy()
            boost_headers["Content-Type"] = "application/json"
            b = requests.get("https://discord.com/api/v10/users/@me/guilds/premium/subscriptions", headers=boost_headers)
            if b.status_code == 200:
                boost_count = len(b.json())
                if boost_count >= 2:
                    save_token(token, "boosts_2")
                elif boost_count == 1:
                    save_token(token, "boosts_1")
                else:
                    save_token(token, "boosts_0")
            else:
                save_token(token, "boosts_0")

            log_callback(f"[+] ✅ Valide | Nitro: {'Oui' if premium else 'Non'} | Boosts: {boost_count if b.status_code == 200 else 'N/A'}")
        elif r.status_code == 401:
            save_token(token, "invalid")
            log_callback("[-] ❌ Token invalide")
        elif r.status_code == 403:
            save_token(token, "locked")
            log_callback("[!] 🔒 Token bloqué")
        else:
            log_callback(f"[?] Erreur inconnue: {r.status_code}")
    except Exception as e:
        log_callback(f"[!] Erreur réseau: {e}")

class TokenCheckerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Discord Token Checker - GUI Version")
        self.root.geometry("650x500")
        self.root.resizable(False, False)

        self.tokens = []

        style = ttk.Style()
        style.configure("TButton", padding=6)
        style.configure("TLabel", font=("Segoe UI", 11))

        self.label = ttk.Label(root, text="1. Charger un fichier de tokens (.txt)")
        self.label.pack(pady=10)

        self.load_button = ttk.Button(root, text="📂 Charger fichier", command=self.load_file)
        self.load_button.pack()

        self.check_button = ttk.Button(root, text="✅ Lancer le check", command=self.start_check, state="disabled")
        self.check_button.pack(pady=10)

        self.text_area = tk.Text(root, height=20, width=80, bg="#111", fg="#0f0", insertbackground="white")
        self.text_area.pack(pady=10)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Fichiers texte", "*.txt")])
        if file_path:
            with open(file_path, "r") as f:
                self.tokens = list(set([line.strip() for line in f if line.strip()]))
            self.log(f"📥 {len(self.tokens)} tokens chargés.")
            self.check_button.config(state="normal")

    def log(self, msg):
        self.text_area.insert(tk.END, msg + "\n")
        self.text_area.see(tk.END)
        self.root.update_idletasks()

    def start_check(self):
        self.check_button.config(state="disabled")
        self.text_area.delete("1.0", tk.END)
        threading.Thread(target=self.run_check, daemon=True).start()

    def run_check(self):
        for key in OUTPUT_PATHS:
            open(OUTPUT_PATHS[key], "w").close()
        self.log(f"🧪 Vérification de {len(self.tokens)} tokens...\n")
        for token in self.tokens:
            check_token(token, self.log)
        self.log("\n✅ Terminé. Résultats enregistrés dans le dossier 'output_gui'.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TokenCheckerGUI(root)
    root.mainloop()
