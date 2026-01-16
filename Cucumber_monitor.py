import psutil
import subprocess
import tkinter as tk
import os
import platform
from datetime import datetime

# --- ЛОКАЛІЗАЦІЯ ---
lang_data = {
    "UKR": {
        "cpu": "ПРОЦЕСОР", "gpu": "ВІДЕОКАРТА", "ram": "ОЗП", "disk": "ДИСК C", 
        "cores": "ЯДРА", "freq": "ЧАСТОТА", "os": "СИСТЕМА", "uptime": "ЧАС РОБОТИ",
        "swap": "ФАЙЛ ПІДКАЧКИ", "set": "Налаштування", "theme": "Тема", 
        "alpha": "Прозорість", "status": "Сингулярність досягнута!", "btn_close": "ЗАКРИТИ"
    },
    "ENG": {
        "cpu": "CPU", "gpu": "GPU", "ram": "RAM", "disk": "DISK C", 
        "cores": "CORES", "freq": "FREQ", "os": "OS VER", "uptime": "UPTIME",
        "swap": "SWAP FILE", "set": "Settings", "theme": "Theme", 
        "alpha": "Opacity", "status": "System Scan Complete!", "btn_close": "CLOSE"
    },
    "RUS": {
        "cpu": "ПРОЦЕССОР", "gpu": "ВИДЕОКАРТА", "ram": "ОЗУ", "disk": "ДИСК C", 
        "cores": "ЯДРА", "freq": "ЧАСТОТА", "os": "СИСТЕМА", "uptime": "ВРЕМЯ РАБОТЫ",
        "swap": "ФАЙЛ ПОДКАЧКИ", "set": "Настройки", "theme": "Тема", 
        "alpha": "Прозрачность", "status": "Все огурцы на месте!", "btn_close": "ЗАКРЫТЬ"
    }
}

config = {"bg": "#0a0a0a", "fg": "#00ffcc", "theme": "dark", "alpha": 0.95, "lang": "UKR"}

def get_info(cmd):
    try:
        out = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore')
        return out.split('\n')[1].strip()
    except: return "???"

def open_main_window():
    main_win = tk.Toplevel()
    main_win.title("Cucumber Monitor Pro")
    main_win.geometry("520x680")
    main_win.configure(bg=config["bg"])
    main_win.attributes('-topmost', True)
    main_win.attributes('-alpha', config["alpha"])

    # Щоб при закритті вікна монітора закривалася вся програма
    main_win.protocol("WM_DELETE_WINDOW", root.destroy)

    def update_styles():
        main_win.configure(bg=config["bg"])
        main_win.attributes('-alpha', config["alpha"])
        main_label.configure(bg=config["bg"], fg=config["fg"])
        header.configure(bg=config["bg"])
        btn_set.configure(bg=config["bg"], fg=config["fg"])

    def toggle_theme():
        if config["theme"] == "dark":
            config.update({"theme": "light", "bg": "#f0f0f0", "fg": "#222222"})
        else:
            config.update({"theme": "dark", "bg": "#0a0a0a", "fg": "#00ffcc"})
        update_styles()

    def change_alpha(val):
        config["alpha"] = float(val)
        main_win.attributes('-alpha', config["alpha"])

    def open_settings():
        set_win = tk.Toplevel(main_win)
        set_win.title("Settings")
        set_win.geometry("300x250")
        set_win.configure(bg=config["bg"])
        l = lang_data[config["lang"]]
        tk.Label(set_win, text=l["set"], fg=config["fg"], bg=config["bg"], font=("Arial", 12, "bold")).pack(pady=10)
        tk.Button(set_win, text=l["theme"], command=toggle_theme).pack(pady=5)
        tk.Label(set_win, text=l["alpha"], fg=config["fg"], bg=config["bg"]).pack()
        scale = tk.Scale(set_win, from_=0.4, to=1.0, resolution=0.1, orient="horizontal", 
                         command=change_alpha, bg=config["bg"], fg=config["fg"], highlightthickness=0)
        scale.set(config["alpha"])
        scale.pack(pady=5)

    # UI
    header = tk.Frame(main_win, bg=config["bg"])
    header.pack(fill="x", padx=10)
    btn_set = tk.Button(header, text="⚙", command=open_settings, bd=0, font=("Arial", 16), 
                        bg=config["bg"], fg=config["fg"], cursor="hand2")
    btn_set.pack(side="right")

    # Дані
    l = lang_data[config["lang"]]
    cpu_name = get_info("wmic cpu get name")
    gpu_name = get_info("wmic path win32_VideoController get name")
    cores = psutil.cpu_count(logical=True)
    cpu_freq = psutil.cpu_freq().max if psutil.cpu_freq() else "???"
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk = psutil.disk_usage('C:')
    uptime = str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())).split('.')[0]
    os_ver = f"{platform.system()} {platform.release()}"

    info_text = (
        f"--- [ HARDWARE ] ---\n"
        f"🖥 {l['cpu']}: {cpu_name}\n"
        f"🧵 {l['cores']}: {cores} | {l['freq']}: {cpu_freq} MHz\n"
        f"🎮 {l['gpu']}: {gpu_name}\n"
        f"\n--- [ MEMORY & STORAGE ] ---\n"
        f"💾 {l['ram']}: {round(mem.total / (1024**3), 2)} GB\n"
        f"📊 USED: {mem.percent}% | FREE: {round(mem.available / (1024**3), 2)} GB\n"
        f"🔄 {l['swap']}: {round(swap.total / (1024**3), 2)} GB\n"
        f"💽 {l['disk']}: {disk.percent}% USED\n"
        f"📂 FREE: {round(disk.free / (1024**3), 2)} GB\n"
        f"\n--- [ SYSTEM ] ---\n"
        f"💿 {l['os']}: {os_ver}\n"
        f"⏰ {l['uptime']}: {uptime}\n"
        f"👤 USER: {os.getlogin()}\n"
        f"----------------------------------------\n"
        f"✨ {l['status']}"
    )

    main_label = tk.Label(main_win, text=info_text, font=("Consolas", 10), 
                          bg=config["bg"], fg=config["fg"], justify="left")
    main_label.pack(pady=10, padx=20)
    
    tk.Button(main_win, text=l["btn_close"], command=root.destroy, bg="#333", fg="white", width=15).pack(pady=10)

def select_lang(choice):
    config["lang"] = choice
    lang_frame.pack_forget() # Ховаємо вибір мови
    open_main_window()

# --- ГОЛОВНИЙ ЗАПУСК ---
root = tk.Tk()
root.title("Lang Select")
root.geometry("300x250")
root.configure(bg="#1a1a1a")

lang_frame = tk.Frame(root, bg="#1a1a1a")
lang_frame.pack(expand=True)

tk.Label(lang_frame, text="SELECT INTERFACE", fg="white", bg="#1a1a1a", font=("Arial", 11, "bold")).pack(pady=15)
tk.Button(lang_frame, text="УКРАЇНСЬКА 🇺🇦", width=20, command=lambda: select_lang("UKR")).pack(pady=5)
tk.Button(lang_frame, text="ENGLISH 🇺🇸", width=20, command=lambda: select_lang("ENG")).pack(pady=5)
tk.Button(lang_frame, text="РУССКИЙ 🇷🇺", width=20, command=lambda: select_lang("RUS")).pack(pady=5)

root.mainloop()