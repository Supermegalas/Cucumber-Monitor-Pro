import psutil
import subprocess
import tkinter as tk
import os
import platform
import wmi
from datetime import datetime
import urllib.request
import io

# Спроба імпортувати Pillow для іконок
try:
    from PIL import Image, ImageTk
    PILLOW_INSTALLED = True
except ImportError:
    PILLOW_INSTALLED = False

# --- ЛОКАЛІЗАЦІЯ ---
lang_data = {
    "UKR": {
        "cpu": "ПРОЦЕСОР", "gpu": "ВІДЕОКАРТА", "ram": "ОЗП", "disk": "ДИСК C", 
        "cores": "ЯДРА", "freq": "ЧАСТОТА", "os": "СИСТЕМА", "uptime": "ЧАС РОБОТИ",
        "swap": "ФАЙЛ ПІДКАЧКИ", "set": "Налаштування", "theme": "Тема", 
        "alpha": "Прозорість", "status": "Сканування системи завершено!", "btn_close": "ЗАКРИТИ",
        "rating": "РЕЙТИНГ ПК", "verdict": "ВЕРДИКТ", "health": "РЕСУРС ДИСКА"
    },
    "ENG": {
        "cpu": "CPU", "gpu": "GPU", "ram": "RAM", "disk": "DISK C", 
        "cores": "CORES", "freq": "FREQ", "os": "OS VER", "uptime": "UPTIME",
        "swap": "SWAP FILE", "set": "Settings", "theme": "Theme", 
        "alpha": "Opacity", "status": "System Scan Complete!", "btn_close": "CLOSE",
        "rating": "PC RATING", "verdict": "VERDICT", "health": "DISK LIFE"
    },
    "RUS": {
        "cpu": "ПРОЦЕССОР", "gpu": "ВИДЕОКАРТА", "ram": "ОЗУ", "disk": "ДИСК C", 
        "cores": "ЯДРА", "freq": "ЧАСТОТА", "os": "СИСТЕМА", "uptime": "ВРЕМЯ РАБОТЫ",
        "swap": "ФАЙЛ ПОДКАЧКИ", "set": "Настройки", "theme": "Тема", 
        "alpha": "Прозрачность", "status": "Все огурцы на месте!", "btn_close": "ЗАКРЫТЬ",
        "rating": "РЕЙТИНГ ПК", "verdict": "ВЕРДИКТ", "health": "ЖИЗНЬ ДИСКА"
    }
}

config = {"bg": "#0a0a0a", "fg": "#00ffcc", "theme": "dark", "alpha": 0.95, "lang": "UKR"}

def get_info(cmd):
    try:
        out = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore')
        return out.split('\n')[1].strip()
    except: return "???"

def get_disk_health():
    try:
        c = wmi.WMI(namespace="root\\wmi")
        items = c.MSStorageDriver_FailurePredictStatus()
        if items:
            return "100% (GOOD) ✅" if not items[0].PredictFailure else "WARNING ⚠️"
        out = subprocess.check_output("wmic diskdrive get status", shell=True).decode('utf-8')
        return "HEALTHY ✅" if "OK" in out else "UNKNOWN"
    except:
        return "HEALTHY ✅"

def get_pc_score(cpu_name, ram_gb, gpu_name, cores):
    cpu_n = cpu_name.upper()
    gpu_n = gpu_name.upper()
    cpu_p = 0
    if any(x in cpu_n for x in ["I9", "RYZEN 9", "THREADRIPPER", "7950", "14900"]): cpu_p = 10
    elif any(x in cpu_n for x in ["I7-12", "I7-13", "I7-14", "RYZEN 7 5", "RYZEN 7 7"]): cpu_p = 9
    elif any(x in cpu_n for x in ["I5-12", "I5-13", "I5-14", "RYZEN 5 5600", "RYZEN 5 7600"]): cpu_p = 8.5
    elif any(x in cpu_n for x in ["I5-10", "I5-11", "RYZEN 5 3600", "I7-10", "I7-11"]): cpu_p = 7.5
    elif any(x in cpu_n for x in ["I7-2", "I7-3", "I7-4", "FX-83", "FX-9"]): cpu_p = 4.0
    elif any(x in cpu_n for x in ["PENTIUM", "CELERON", "ATHLON", "CORE 2"]): cpu_p = 1.5
    else: cpu_p = 3.0

    gpu_p = 0
    if any(x in gpu_n for x in ["4090", "4080", "7900 XTX"]): gpu_p = 10
    elif any(x in gpu_n for x in ["4070", "3080", "3090", "6800 XT", "6900"]): gpu_p = 9
    elif any(x in gpu_n for x in ["4060 TI", "3070", "6700 XT"]): gpu_p = 8.2
    elif any(x in gpu_n for x in ["3060", "4060", "6600", "5700"]): gpu_p = 7.0
    elif any(x in gpu_n for x in ["1080", "1070", "VEGA 64", "GTX 980"]): gpu_p = 5.5
    elif any(x in gpu_n for x in ["HD 7", "HD 8", "RX 580", "RX 570", "GTX 1050", "GTX 960", "GTX 750"]): gpu_p = 2.5
    elif any(x in gpu_n for x in ["GT 7", "GT 1030", "HD 6", "HD 5"]): gpu_p = 1.2
    else: gpu_p = 1.5

    if ram_gb >= 64: ram_score = 10
    elif ram_gb >= 32: ram_score = 9
    elif ram_gb >= 16: ram_score = 7.5
    elif ram_gb >= 8: ram_score = 4
    else: ram_score = 1.5

    final = round((cpu_p * 0.35 + gpu_p * 0.5 + ram_score * 0.15), 1)
    if final >= 9.0: verd = "GODLIKE BEAST 🔥"
    elif final >= 7.5: verd = "MODERN GAMER 🎮"
    elif final >= 5.0: verd = "SOLID WORKHORSE 🐎"
    elif final >= 2.5: verd = "BRAVE SURVIVOR 🛡️"
    else: verd = "POTATO POWER 🥔"
    return final, verd

def open_main_window():
    root.withdraw()
    
    main_win = tk.Toplevel()
    main_win.title("Cucumber Monitor Pro v1.3")
    main_win.geometry("520x960")
    main_win.configure(bg=config["bg"])
    main_win.attributes('-topmost', True)
    main_win.attributes('-alpha', config["alpha"])
    main_win.protocol("WM_DELETE_WINDOW", root.destroy)

    # --- ФУНКЦІЇ НАЛАШТУВАНЬ ---
    def update_styles():
        main_win.configure(bg=config["bg"])
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

    # --- ШЕСТЕРНЯ ТА ЛОГО ---
    header = tk.Frame(main_win, bg=config["bg"])
    header.pack(fill="x", padx=10)
    btn_set = tk.Button(header, text="⚙", command=open_settings, bd=0, font=("Arial", 18), 
                        bg=config["bg"], fg=config["fg"], cursor="hand2")
    btn_set.pack(side="right", pady=5)

    if PILLOW_INSTALLED:
        try:
            img_url = "https://cdn-icons-png.flaticon.com/512/2316/2316613.png"
            req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as u: raw_data = u.read()
            img_data = Image.open(io.BytesIO(raw_data))
            icon_small = ImageTk.PhotoImage(img_data.resize((32, 32)))
            main_win.iconphoto(False, icon_small)
            logo_img = ImageTk.PhotoImage(img_data.resize((100, 100)))
            logo_label = tk.Label(main_win, image=logo_img, bg=config["bg"])
            logo_label.image = logo_img 
            logo_label.pack(pady=5)
        except: pass

    # --- ДАНІ ---
    l = lang_data[config["lang"]]
    cpu_name = get_info("wmic cpu get name")
    gpu_name = get_info("wmic path win32_VideoController get name")
    cores = psutil.cpu_count(logical=True)
    cpu_freq = psutil.cpu_freq().max if psutil.cpu_freq() else "???"
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk = psutil.disk_usage('C:')
    d_health = get_disk_health()
    uptime = str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())).split('.')[0]

    rating, verdict = get_pc_score(cpu_name, round(mem.total / (1024**3)), gpu_name, cores)

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
        f"💓 {l['health']}: {d_health}\n"
        f"\n--- [ PERFORMANCE INDEX ] ---\n"
        f"⭐ {l['rating']}: {rating} / 10\n"
        f"📝 {l['verdict']}: {verdict}\n"
        f"\n--- [ SYSTEM ] ---\n"
        f"💿 {l['os']}: {platform.system()} {platform.release()}\n"
        f"⏰ {l['uptime']}: {uptime}\n"
        f"👤 USER: {os.getlogin()}\n"
        f"----------------------------------------\n"
        f"✨ {l['status']}"
    )

    main_label = tk.Label(main_win, text=info_text, font=("Consolas", 11), 
                          bg=config["bg"], fg=config["fg"], justify="left")
    main_label.pack(pady=10, padx=20)
    
    tk.Button(main_win, text=l["btn_close"], command=root.destroy, bg="#333", fg="white", width=15).pack(pady=15)

def select_lang(choice):
    config["lang"] = choice
    open_main_window()

root = tk.Tk()
root.title("Cucumber Monitor")
root.geometry("350x300")
root.configure(bg="#1a1a1a")

lang_frame = tk.Frame(root, bg="#1a1a1a")
lang_frame.pack(expand=True)

tk.Label(lang_frame, text="SELECT INTERFACE", fg="white", bg="#1a1a1a", font=("Arial", 12, "bold")).pack(pady=20)
tk.Button(lang_frame, text="УКРАЇНСЬКА 🇺🇦", width=25, command=lambda: select_lang("UKR")).pack(pady=5)
tk.Button(lang_frame, text="ENGLISH 🇺🇸", width=25, command=lambda: select_lang("ENG")).pack(pady=5)
tk.Button(lang_frame, text="РУССКИЙ 🇷🇺", width=25, command=lambda: select_lang("RUS")).pack(pady=5)

root.mainloop()