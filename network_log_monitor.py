# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Network Log Monitor - Canlı İzleme Aracı

Bu uygulama, 'logs/server.log' dosyasını canlı olarak izler.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from datetime import datetime
import queue
import os


class NetworkLogMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Log Monitor")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2b2b2b')

        self.log_queue = queue.Queue()
        self.monitoring = False
        self.log_file_path = os.path.join('logs', 'server.log')

        self.setup_ui()
        self.setup_styles()

    def setup_styles(self):
        """UI stillerini ayarla"""
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('Main.TFrame', background='#2b2b2b')
        style.configure('Panel.TFrame', background='#3c3c3c', relief='raised', borderwidth=1)
        style.configure('Title.TLabel', background='#2b2b2b', foreground='#ffffff', font=('Arial', 12, 'bold'))
        style.configure('Status.TLabel', background='#3c3c3c', foreground='#ffffff', font=('Arial', 9, 'bold'))
        style.configure('Control.TButton', background='#4a4a4a', foreground='#ffffff', font=('Arial', 9, 'bold'))

    def setup_ui(self):
        """Kullanıcı arayüzünü oluştur"""
        main_frame = ttk.Frame(self.root, style='Main.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        title_label = ttk.Label(main_frame, text="Network Log Monitor", style='Title.TLabel')
        title_label.pack(pady=(0, 10))

        control_frame = ttk.Frame(main_frame, style='Panel.TFrame')
        control_frame.pack(fill=tk.X, pady=(0, 10), ipady=5)

        self.start_monitor_btn = ttk.Button(control_frame, text="İzlemeyi Başlat", command=self.start_monitoring, style='Control.TButton')
        self.start_monitor_btn.pack(side=tk.LEFT, padx=10)

        self.stop_monitor_btn = ttk.Button(control_frame, text="İzlemeyi Durdur", command=self.stop_monitoring, style='Control.TButton')
        self.stop_monitor_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(control_frame, text="Logları Temizle", command=self.clear_logs, style='Control.TButton')
        clear_btn.pack(side=tk.LEFT, padx=5)

        self.status_label = ttk.Label(control_frame, text="Hazır", style='Status.TLabel')
        self.status_label.pack(side=tk.RIGHT, padx=10)

        log_frame = ttk.Frame(main_frame, style='Panel.TFrame')
        log_frame.pack(fill=tk.BOTH, expand=True)

        log_title = ttk.Label(log_frame, text="Canlı Log Akışı", style='Title.TLabel')
        log_title.pack(pady=(10, 5))

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, bg='#1e1e1e', fg='#ffffff', font=('Consolas', 9), state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.stop_monitor_btn.config(state='disabled')

    def start_monitoring(self):
        """Log dosyasını izlemeyi başlat"""
        if not os.path.exists(self.log_file_path):
            messagebox.showerror("Hata", f"Log dosyası bulunamadı: {self.log_file_path}\nLütfen önce sunucuyu çalıştırın.")
            return

        self.monitoring = True
        self.start_monitor_btn.config(state='disabled')
        self.stop_monitor_btn.config(state='normal')
        self.status_label.config(text="İzleniyor...", foreground="#00ff00")

        threading.Thread(target=self.tail_log_file, daemon=True).start()
        threading.Thread(target=self.process_logs, daemon=True).start()

    def stop_monitoring(self):
        """Log izlemeyi durdur"""
        self.monitoring = False
        self.start_monitor_btn.config(state='normal')
        self.stop_monitor_btn.config(state='disabled')
        self.status_label.config(text="Durduruldu", foreground="#ffff00")

    def clear_logs(self):
        """Log görüntüleme alanını temizle"""
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')

    def tail_log_file(self):
        """Log dosyasının sonunu takip et"""
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as file:
                # Dosyanın sonuna git
                file.seek(0, 2)
                while self.monitoring:
                    line = file.readline()
                    if not line:
                        time.sleep(0.1)  # Yeni satır yoksa bekle
                        continue
                    self.log_queue.put(line.strip())
        except Exception as e:
            print(f"Log file monitoring error: {e}")
            self.root.after(0, self.stop_monitoring)
            self.root.after(0, lambda: self.status_label.config(text="Log Dosyası Hatası", foreground="#ff0000"))

    def process_logs(self):
        """Log kuyruğunu işle"""
        while self.monitoring:
            try:
                log_line = self.log_queue.get(timeout=0.2)
                self.root.after(0, self.update_log_display, log_line)
            except queue.Empty:
                continue

    def update_log_display(self, log_line: str):
        """Log görüntüleme alanını güncelle"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        # Log satırının kendisinde zaten zaman damgası var, biz sadece anlık olanı ekleyelim.
        formatted_line = f"[{timestamp}] {log_line}\n"

        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, formatted_line)
        self.log_text.config(state='disabled')
        self.log_text.see(tk.END)
        
        # Performans için log sınırlaması
        lines = int(self.log_text.index('end-1c').split('.')[0])
        if lines > 500:
            self.log_text.config(state='normal')
            self.log_text.delete('1.0', '101.0') # İlk 100 satırı sil
            self.log_text.config(state='disabled')


def main():
    """Ana fonksiyon"""
    root = tk.Tk()
    app = NetworkLogMonitor(root)
    root.mainloop()

if __name__ == "__main__":
    main() 