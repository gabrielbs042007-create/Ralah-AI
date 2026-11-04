import os
import ollama
from pypdf import PdfReader

MODEL_NAME = "qwen2.5:0.5b"

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    if ext == '.pdf':
        reader = PdfReader(file_path)
        for page in reader.pages:
            t = page.extract_text()
            if t: text += t + "\n"
    elif ext in ['.txt', '.py', '.md', '.json', '.sh', '.c', '.cpp']:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
    return text

def main():
    print("=== RALAH CLI (Mode Terminal Jetson) ===")
    print(f"Modèle actif : {MODEL_NAME}")
    print("Tape ton message ou 'exit' pour quitter.\n")
    
    history = [
        {
            'role': 'system', 
            'content': 'Tu es RALAH, un assistant technique intelligent, concis et précis. Réponds toujours en français. Sois direct et évite les répétitions en boucle.'
        }
    ]

    while True:
        try:
            user_input = input("\033[1;34mVous > \033[0m")
        except (EOFError, KeyboardInterrupt):
            print("\nArrêt du script.")
            break

        if user_input.lower() in ['exit', 'quit', 'q']:
            break
        if not user_input.strip():
            continue

        prompt = user_input
        if os.path.exists(user_input) and os.path.isfile(user_input):
            file_text = extract_text(user_input)
            if file_text:
                prompt = f"Analyse ce fichier :\n{file_text[:4000]}"
                print(f"[*] Fichier {user_input} injecté.")

        history.append({'role': 'user', 'content': prompt})
        print("\033[1;32mRALAH > \033[0m", end="", flush=True)

        try:
            stream = ollama.chat(
                model=MODEL_NAME, 
                messages=history, 
                stream=True,
                options={
                    'temperature': 0.3,
                    'num_predict': 300
                }
            )

            response_content = ""
            for chunk in stream:
                content = chunk['message']['content']
                print(content, end="", flush=True)
                response_content += content
            print("\n")
            
            history.append({'role': 'assistant', 'content': response_content})
        except Exception as e:
            print(f"\nErreur de génération : {e}\n")

if __name__ == "__main__":
    main()
