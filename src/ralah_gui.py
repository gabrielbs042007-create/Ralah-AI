import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import ollama
from pypdf import PdfReader

# Configuration du thème de l'interface
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

MODEL_NAME = "qwen2.5:0.5b"

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    if ext == '.pdf':
        reader = PdfReader(file_path)
        for page in reader.pages:
            t = page.extract_text()
            if t: text += t + "\n"
    elif ext in ['.txt', '.py', '.md', '.json', '.c', '.cpp', '.sh', '.html', '.css']:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
    return text

class RalahApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("RALAH - Assistant Local (Jetson Orin Nano)")
        self.geometry("850x650")
        self.minsize(600, 500)

        self.history = []
        self.attached_file_path = None

        # --- Grille principale ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Sidebar (Panneau latéral) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="🛡️ RALAH AI", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.model_info = ctk.CTkLabel(self.sidebar_frame, text=f"Modèle:\n{MODEL_NAME}", text_color="gray", justify="left")
        self.model_info.grid(row=1, column=0, padx=20, pady=10)

        self.attach_btn = ctk.CTkButton(self.sidebar_frame, text="📎 Joindre un fichier", command=self.load_file)
        self.attach_btn.grid(row=2, column=0, padx=20, pady=10)

        self.file_label = ctk.CTkLabel(self.sidebar_frame, text="Aucun fichier", text_color="gray", wraplength=180)
        self.file_label.grid(row=3, column=0, padx=20, pady=5)

        self.clear_btn = ctk.CTkButton(self.sidebar_frame, text="Effacer l'historique", fg_color="#b91c1c", hover_color="#991b1b", command=self.clear_chat)
        self.clear_btn.grid(row=5, column=0, padx=20, pady=20)

        # --- Zone de Chat principale ---
        self.chat_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.chat_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_frame.grid_columnconfigure(0, weight=1)

        self.chat_textbox = ctk.CTkTextbox(self.chat_frame, wrap="word", font=ctk.CTkFont(size=14))
        self.chat_textbox.grid(row=0, column=0, sticky="nsew", padx=0, pady=(0, 10))
        self.chat_textbox.configure(state="disabled")

        # --- Barre de saisie en bas ---
        self.input_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        self.input_frame.grid(row=1, column=0, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.msg_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Écris ton message ici...", height=45, font=ctk.CTkFont(size=14))
        self.msg_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.msg_entry.bind("<Return>", lambda event: self.send_message())

        self.send_btn = ctk.CTkButton(self.input_frame, text="Envoyer", width=100, height=45, command=self.send_message)
        self.send_btn.grid(row=0, column=1)

        self.append_chat("RALAH", "Système initialisé. Je suis prêt à vous aider sur la Jetson.\n")

    def load_file(self):
        file_path = filedialog.askopenfilename(title="Sélectionner un fichier à analyser")
        if file_path:
            self.attached_file_path = file_path
            filename = os.path.basename(file_path)
            self.file_label.configure(text=f"📄 {filename}", text_color="#2ea043")

    def clear_chat(self):
        self.chat_textbox.configure(state="normal")
        self.chat_textbox.delete("1.0", tk.END)
        self.chat_textbox.configure(state="disabled")
        self.history.clear()
        self.attached_file_path = None
        self.file_label.configure(text="Aucun fichier", text_color="gray")

    def append_chat(self, sender, message):
        self.chat_textbox.configure(state="normal")
        if sender == "Vous":
            self.chat_textbox.insert(tk.END, f"\n[ Vous ] :\n{message}\n")
        elif sender == "RALAH":
            self.chat_textbox.insert(tk.END, f"\n[ RALAH ] :\n{message}\n")
        else:
            self.chat_textbox.insert(tk.END, f"\n{message}\n")
        self.chat_textbox.see(tk.END)
        self.chat_textbox.configure(state="disabled")

    def send_message(self):
        user_text = self.msg_entry.get().strip()
        if not user_text and not self.attached_file_path:
            return

        prompt = user_text
        display_text = user_text

        if self.attached_file_path:
            file_text = extract_text(self.attached_file_path)
            filename = os.path.basename(self.attached_file_path)
            if file_text:
                prompt = f"{user_text}\n\n[Contenu du fichier joint ({filename})] :\n{file_text[:4000]}"
                display_text += f" [Fichier joint: {filename}]"
            else:
                messagebox.showerror("Erreur", "Impossible de lire le fichier sélectionné.")
                return
            
            self.attached_file_path = None
            self.file_label.configure(text="Aucun fichier", text_color="gray")

        self.msg_entry.delete(0, tk.END)
        self.append_chat("Vous", display_text)
        self.history.append({'role': 'user', 'content': prompt})

        threading.Thread(target=self.generate_response, daemon=True).start()

    def generate_response(self):
        try:
            stream = ollama.chat(model=MODEL_NAME, messages=self.history, stream=True)
            
            self.chat_textbox.configure(state="normal")
            self.chat_textbox.insert(tk.END, "\n[ RALAH ] :\n")
            self.chat_textbox.configure(state="disabled")

            response_content = ""
            for chunk in stream:
                content = chunk['message']['content']
                response_content += content
                
                self.chat_textbox.configure(state="normal")
                self.chat_textbox.insert(tk.END, content)
                self.chat_textbox.see(tk.END)
                self.chat_textbox.configure(state="disabled")

            self.chat_textbox.configure(state="normal")
            self.chat_textbox.insert(tk.END, "\n")
            self.chat_textbox.configure(state="disabled")

            self.history.append({'role': 'assistant', 'content': response_content})

        except Exception as e:
            self.append_chat("Système", f"Erreur de communication : {e}")

if __name__ == "__main__":
    app = RalahApp()
    app.mainloop()
