import customtkinter as ctk
import json
import os
import winsound
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime, timedelta

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuration de la fenêtre
        self.title("Mon Hub Personnel")
        self.geometry("1000x750")
        
        ctk.set_appearance_mode("light")
        
        # Fichiers de sauvegarde
        self.db_file = "tasks.json"
        self.notes_dir = "pages_notes"
        self.stats_file = "stats.json"
        
        if not os.path.exists(self.notes_dir):
            os.makedirs(self.notes_dir)
        
        # Couleurs
        self.bg_color = "#F3EFFA"        
        self.card_color = "#FFFFFF"      
        self.accent_color = "#9D4EDD"    
        self.break_color = "#2A9D8F"     
        self.text_color = "#333333"      
        
        self.configure(fg_color=self.bg_color)

        # Grille principale
        self.grid_columnconfigure(0, weight=1) 
        self.grid_rowconfigure(0, weight=1)

        self.tasks_widgets = []
        self.note_buttons_widgets = {} 
        self.current_note = None       

        # --- VARIABLES DU TIMER & STATS ---
        self.timer_time_left = 25 * 60  
        self.timer_initial_duration = 25 * 60 
        self.timer_running = False
        self.timer_id = None            
        self.timer_mode = "Travail" 
        self.stats_data = {}        
        self.load_stats()

        # --- VARIABLES OPTIMISATION NOTES ---
        self.notes_modified = False
        self.start_notes_autosave_loop()

        # --- CONTENEUR PRINCIPAL ---
        self.left_container = ctk.CTkFrame(self, fg_color="transparent")
        self.left_container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.left_container.grid_columnconfigure(0, weight=1)
        self.left_container.grid_rowconfigure(1, weight=1)

        # Barre de navigation au-dessus
        self.nav_frame = ctk.CTkFrame(self.left_container, fg_color="transparent")
        self.nav_frame.grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.btn_tab_dashboard = ctk.CTkButton(self.nav_frame, text="Accueil", width=100, height=32, corner_radius=10, fg_color=self.accent_color, text_color="#FFFFFF", font=("Arial", 13, "bold"), command=lambda: self.switch_tab("Accueil"))
        self.btn_tab_dashboard.pack(side="left", padx=5)

        self.btn_tab_tasks = ctk.CTkButton(self.nav_frame, text="To do list", width=100, height=32, corner_radius=10, fg_color="#E0D6F2", text_color=self.text_color, font=("Arial", 13, "bold"), command=lambda: self.switch_tab("To do list"))
        self.btn_tab_tasks.pack(side="left", padx=5)

        self.btn_tab_notes = ctk.CTkButton(self.nav_frame, text="Notes", width=100, height=32, corner_radius=10, fg_color="#E0D6F2", text_color=self.text_color, font=("Arial", 13, "bold"), command=lambda: self.switch_tab("Notes"))
        self.btn_tab_notes.pack(side="left", padx=5)

        self.btn_tab_timer = ctk.CTkButton(self.nav_frame, text="Timer", width=100, height=32, corner_radius=10, fg_color="#E0D6F2", text_color=self.text_color, font=("Arial", 13, "bold"), command=lambda: self.switch_tab("Timer"))
        self.btn_tab_timer.pack(side="left", padx=5)

        # La carte blanche unique
        self.main_card = ctk.CTkFrame(self.left_container, fg_color=self.card_color, corner_radius=20)
        self.main_card.grid(row=1, column=0, sticky="nsew")

        # --- MODULE ACCUEIL / DASHBOARD ---
        self.dashboard_view = ctk.CTkFrame(self.main_card, fg_color="transparent")
        
        self.db_title = ctk.CTkLabel(self.dashboard_view, text="Tableau de bord", font=("Arial", 24, "bold"), text_color=self.text_color)
        self.db_title.pack(anchor="w", padx=25, pady=(20, 15))

        # Zone contenant les 3 widgets alignés horizontalement
        self.widgets_container = ctk.CTkFrame(self.dashboard_view, fg_color="transparent")
        self.widgets_container.pack(fill="both", expand=True, padx=25, pady=(0, 25))
        self.widgets_container.grid_columnconfigure((0, 1, 2), weight=1, uniform="equal")
        self.widgets_container.grid_rowconfigure(0, weight=1)

        # 1. Widget To do list
        self.widget_todo = ctk.CTkButton(self.widgets_container, text="", fg_color="#F8F6FC", hover_color="#E0D6F2", corner_radius=15, command=lambda: self.switch_tab("To do list"))
        self.widget_todo.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.setup_widget_todo_content()

        # 2. Widget Notes
        self.widget_notes = ctk.CTkButton(self.widgets_container, text="", fg_color="#F8F6FC", hover_color="#E0D6F2", corner_radius=15, command=lambda: self.switch_tab("Notes"))
        self.widget_notes.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.setup_widget_notes_content()

        # 3. Widget Timer / Focus
        self.widget_timer = ctk.CTkButton(self.widgets_container, text="", fg_color="#F8F6FC", hover_color="#E0D6F2", corner_radius=15, command=lambda: self.switch_tab("Timer"))
        self.widget_timer.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        self.setup_widget_timer_content()

        # --- MODULE TO DO LIST ---
        self.tasks_view = ctk.CTkFrame(self.main_card, fg_color="transparent")
        
        self.tasks_header = ctk.CTkFrame(self.tasks_view, fg_color="transparent")
        self.tasks_header.pack(fill="x", padx=25, pady=20)
        
        self.main_title = ctk.CTkLabel(self.tasks_header, text="Ma To do list (0/0 complétées)", font=("Arial", 22, "bold"), text_color=self.text_color)
        self.main_title.pack(side="left")
        
        self.clear_btn = ctk.CTkButton(self.tasks_header, text="Nettoyer", width=80, height=28, fg_color="#E63946", hover_color="#D62828", font=("Arial", 12, "bold"), corner_radius=8, command=self.clear_completed_tasks)
        self.clear_btn.pack(side="right", padx=(10, 0))

        self.task_entry = ctk.CTkEntry(self.tasks_header, placeholder_text="Ajouter une tâche...", width=220, height=28, corner_radius=8, border_color="#E0E0E0")
        self.task_entry.pack(side="right", padx=5)
        self.task_entry.bind("<Return>", lambda event: self.add_task())
        
        self.add_btn = ctk.CTkButton(self.tasks_header, text="+", width=30, height=28, fg_color=self.accent_color, hover_color="#7B2CBF", font=("Arial", 16, "bold"), corner_radius=8, command=self.add_task)
        self.add_btn.pack(side="right")

        self.tasks_container = ctk.CTkScrollableFrame(self.tasks_view, fg_color="transparent", label_text="")
        self.tasks_container.pack(fill="both", expand=True, padx=25, pady=(0, 25))

        self.task_context_menu = tk.Menu(self, tearoff=0, bg="#FFFFFF", fg=self.text_color, font=("Arial", 11))
        self.task_context_menu.add_command(label="Priorité Haute", command=lambda: self.set_task_priority(True))
        self.task_context_menu.add_command(label="Priorité Normale", command=lambda: self.set_task_priority(False))
        self.selected_task_widget = None

        # --- MODULE NOTES ---
        self.notes_view = ctk.CTkFrame(self.main_card, fg_color="transparent")
        self.notes_view.grid_columnconfigure(0, weight=1) 
        self.notes_view.grid_columnconfigure(1, weight=3) 
        self.notes_view.grid_rowconfigure(0, weight=1)

        self.notes_sidebar = ctk.CTkFrame(self.notes_view, fg_color="#F8F6FC", corner_radius=0)
        self.notes_sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        self.btn_create_note = ctk.CTkButton(self.notes_sidebar, text="+ Nouvelle Note", fg_color=self.accent_color, hover_color="#7B2CBF", text_color="#FFFFFF", font=("Arial", 12, "bold"), command=self.create_new_note)
        self.btn_create_note.pack(fill="x", padx=10, pady=15)

        self.notes_search_entry = ctk.CTkEntry(self.notes_sidebar, placeholder_text="Rechercher une note...", height=28, corner_radius=8, border_color="#E0E0E0")
        self.notes_search_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.notes_search_entry.bind("<KeyRelease>", lambda event: self.filter_notes_list())

        self.notes_list_container = ctk.CTkScrollableFrame(self.notes_sidebar, fg_color="transparent", label_text="")
        self.notes_list_container.pack(fill="both", expand=True, padx=5, pady=(0, 10))

        self.notes_content_frame = ctk.CTkFrame(self.notes_view, fg_color="transparent")
        self.notes_content_frame.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        
        self.notes_title = ctk.CTkLabel(self.notes_content_frame, text="Sélectionnez ou créez une note", font=("Arial", 20, "bold"), text_color=self.text_color)
        self.notes_title.pack(anchor="w", pady=(10, 5))

        self.format_bar = ctk.CTkFrame(self.notes_content_frame, fg_color="transparent")
        self.format_bar.pack(anchor="w", pady=(0, 10))

        self.btn_bold = ctk.CTkButton(self.format_bar, text="B", width=30, height=25, font=("Arial", 12, "bold"), fg_color="#E0D6F2", text_color=self.text_color, command=lambda: self.toggle_text_tag("bold"))
        self.btn_bold.pack(side="left", padx=2)
        self.btn_italic = ctk.CTkButton(self.format_bar, text="I", width=30, height=25, font=("Arial", 12, "italic"), fg_color="#E0D6F2", text_color=self.text_color, command=lambda: self.toggle_text_tag("italic"))
        self.btn_italic.pack(side="left", padx=2)
        self.btn_underline = ctk.CTkButton(self.format_bar, text="U", width=30, height=25, font=("Arial", 12, "underline"), fg_color="#E0D6F2", text_color=self.text_color, command=lambda: self.toggle_text_tag("underline"))
        self.btn_underline.pack(side="left", padx=2)
        self.btn_color = ctk.CTkButton(self.format_bar, text="Couleur", width=60, height=25, font=("Arial", 12), fg_color="#E0D6F2", text_color=self.text_color, command=self.change_text_color)
        self.btn_color.pack(side="left", padx=2)
        
        self.notes_box = ctk.CTkTextbox(self.notes_content_frame, fg_color="#F8F6FC", text_color=self.text_color, font=("Arial", 14), corner_radius=15, border_width=1, border_color="#E0D6F2")
        self.notes_box.pack(fill="both", expand=True)
        self.notes_box.bind("<KeyRelease>", self.mark_notes_as_changed)

        self.notes_box._textbox.tag_configure("bold", font=("Arial", 14, "bold"))
        self.notes_box._textbox.tag_configure("italic", font=("Arial", 14, "italic"))
        self.notes_box._textbox.tag_configure("underline", font=("Arial", 14, "underline"))
        self.notes_box._textbox.tag_configure("colored", foreground=self.accent_color)

        # --- MODULE TIMER & GRAPH_VIEW ---
        self.timer_view = ctk.CTkFrame(self.main_card, fg_color="transparent")
        self.timer_view.grid_columnconfigure(0, weight=1)
        self.timer_view.grid_columnconfigure(1, weight=1) 

        self.timer_left_sub = ctk.CTkFrame(self.timer_view, fg_color="transparent")
        self.timer_left_sub.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        self.timer_title = ctk.CTkLabel(self.timer_left_sub, text="Timer de Focus", font=("Arial", 24, "bold"), text_color=self.text_color)
        self.timer_title.pack(anchor="w", pady=(0, 20))

        self.custom_time_frame = ctk.CTkFrame(self.timer_left_sub, fg_color="transparent")
        self.custom_time_frame.pack(pady=10)
        self.entry_min = ctk.CTkEntry(self.custom_time_frame, width=50, placeholder_text="MM", justify="center")
        self.entry_min.pack(side="left", padx=2)
        self.entry_min.insert(0, "25")
        self.time_separator = ctk.CTkLabel(self.custom_time_frame, text=":", font=("Arial", 18, "bold"), text_color=self.text_color)
        self.time_separator.pack(side="left", padx=2)
        self.entry_sec = ctk.CTkEntry(self.custom_time_frame, width=50, placeholder_text="SS", justify="center")
        self.entry_sec.pack(side="left", padx=2)
        self.entry_sec.insert(0, "00")
        self.btn_set_time = ctk.CTkButton(self.custom_time_frame, text="Appliquer", width=80, fg_color=self.accent_color, hover_color="#7B2CBF", font=("Arial", 12, "bold"), command=self.apply_custom_time)
        self.btn_set_time.pack(side="left", padx=10)

        self.timer_label = ctk.CTkLabel(self.timer_left_sub, text="25:00", font=("Arial", 72, "bold"), text_color=self.accent_color)
        self.timer_label.pack(pady=20)

        self.timer_buttons_frame = ctk.CTkFrame(self.timer_left_sub, fg_color="transparent")
        self.timer_buttons_frame.pack(pady=10)
        self.btn_timer_start = ctk.CTkButton(self.timer_buttons_frame, text="Démarrer", width=90, height=36, corner_radius=10, fg_color=self.accent_color, hover_color="#7B2CBF", font=("Arial", 12, "bold"), command=self.start_timer)
        self.btn_timer_start.pack(side="left", padx=5)
        self.btn_timer_pause = ctk.CTkButton(self.timer_buttons_frame, text="Pause", width=90, height=36, corner_radius=10, fg_color="#E0D6F2", text_color=self.text_color, hover_color="#CDBCED", font=("Arial", 12, "bold"), command=self.pause_and_log_timer)
        self.btn_timer_pause.pack(side="left", padx=5)
        self.btn_timer_reset = ctk.CTkButton(self.timer_buttons_frame, text="Reset", width=90, height=36, corner_radius=10, fg_color="#E63946", hover_color="#D62828", font=("Arial", 12, "bold"), command=self.reset_and_log_timer)
        self.btn_timer_reset.pack(side="left", padx=5)

        self.timer_right_sub = ctk.CTkFrame(self.timer_view, fg_color="transparent")
        self.timer_right_sub.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.graph_title = ctk.CTkLabel(self.timer_right_sub, text="Temps d'activité (Minutes / Jour)", font=("Arial", 18, "bold"), text_color=self.text_color)
        self.graph_title.pack(anchor="w", pady=(0, 20))
        
        self.chart_frame = ctk.CTkFrame(self.timer_right_sub, fg_color="#F8F6FC", height=240, corner_radius=15)
        self.chart_frame.pack(fill="x", expand=True)

        # Initialisation de l'affichage sur l'Accueil
        self.dashboard_view.pack(fill="both", expand=True)

        self.load_tasks()
        self.refresh_notes_list()
        self.draw_stats_graph()
        self.update_dashboard_widgets()

        self.notes_context_menu = tk.Menu(self, tearoff=0, bg="#FFFFFF", fg=self.text_color, font=("Arial", 11))
        self.notes_context_menu.add_command(label="Renommer", command=self.prompt_rename_note)
        self.notes_context_menu.add_command(label="Exporter (.txt)", command=self.export_current_note)
        self.notes_context_menu.add_separator()
        self.notes_context_menu.add_command(label="Supprimer", command=self.delete_current_note, foreground="#E63946")

    # --- SETUP CONTENU DES WIDGETS DE L'ACCUEIL ---
    def setup_widget_todo_content(self):
        self.lbl_todo_title = ctk.CTkLabel(self.widget_todo, text="To do list", font=("Arial", 16, "bold"), text_color=self.accent_color)
        self.lbl_todo_title.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        
        self.lbl_todo_status = ctk.CTkLabel(self.widget_todo, text="0/0 tâches", font=("Arial", 12), text_color="gray")
        self.lbl_todo_status.grid(row=1, column=0, sticky="w", padx=15)
        
        self.lbl_todo_details = ctk.CTkLabel(self.widget_todo, text="Aucune tâche urgente", font=("Arial", 13), text_color=self.text_color, justify="left")
        self.lbl_todo_details.grid(row=2, column=0, sticky="w", padx=15, pady=15)

    def setup_widget_notes_content(self):
        self.lbl_notes_title = ctk.CTkLabel(self.widget_notes, text="Notes Récentes", font=("Arial", 16, "bold"), text_color=self.accent_color)
        self.lbl_notes_title.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        
        self.lbl_notes_details = ctk.CTkLabel(self.widget_notes, text="Pas de note récente", font=("Arial", 13), text_color=self.text_color, justify="left")
        self.lbl_notes_details.grid(row=1, column=0, sticky="w", padx=15, pady=15)

    def setup_widget_timer_content(self):
        self.widget_timer.grid_rowconfigure((0, 1), weight=1)
        self.widget_timer.grid_columnconfigure(0, weight=1)

        self.lbl_timer_title = ctk.CTkLabel(self.widget_timer, text="Temps de Focus", font=("Arial", 16, "bold"), text_color=self.accent_color)
        self.lbl_timer_title.grid(row=0, column=0, sticky="nw", padx=15, pady=(15, 5))
        
        self.lbl_timer_details = ctk.CTkLabel(self.widget_timer, text="0m travaillé aujourd'hui", font=("Arial", 14, "bold"), text_color=self.text_color)
        self.lbl_timer_details.grid(row=1, column=0, sticky="nsew", pady=30)

    def update_dashboard_widgets(self):
        """Met à jour dynamiquement les textes récapitulatifs sur l'écran d'accueil."""
        # 1. Mise à jour To do list
        total = len(self.tasks_widgets)
        completed = sum([1 for cb in self.tasks_widgets if cb.get() == 1])
        self.lbl_todo_status.configure(text=f"{completed}/{total} complétées")
        
        high_priority_tasks = []
        for cb in self.tasks_widgets:
            font_tuple = cb.cget("font")
            if cb.get() == 0 and len(font_tuple) > 2 and font_tuple[2] == "bold":
                high_priority_tasks.append(cb.cget("text"))
                
        if high_priority_tasks:
            details = "Urgences :\n" + "\n".join([f"• {t[:18]}..." if len(t) > 18 else f"• {t}" for t in high_priority_tasks[:3]])
        else:
            details = "Aucune tâche\nurgente en attente."
        self.lbl_todo_details.configure(text=details)

        # 2. Mise à jour Notes Récentes
        files = [f[:-4] for f in os.listdir(self.notes_dir) if f.endswith(".txt")]
        if files:
            self.lbl_notes_details.configure(text="Vos pages :\n" + "\n".join([f"• {f[:18]}" for f in files[:4]]))
        else:
            self.lbl_notes_details.configure(text="Aucune note\npour le moment.")

        # 3. Mise à jour Focus
        today_str = datetime.today().strftime("%Y-%m-%d")
        day_data = self.stats_data.get(today_str, {"work": 0, "break": 0})
        work_m = day_data.get("work", 0)
        self.lbl_timer_details.configure(text=f"{work_m} min\ntravaillées\naujourd'hui")

    def switch_tab(self, tab_name):
        self.dashboard_view.pack_forget()
        self.tasks_view.pack_forget()
        self.notes_view.pack_forget()
        self.timer_view.pack_forget()

        self.btn_tab_dashboard.configure(fg_color="#E0D6F2", text_color=self.text_color)
        self.btn_tab_tasks.configure(fg_color="#E0D6F2", text_color=self.text_color)
        self.btn_tab_notes.configure(fg_color="#E0D6F2", text_color=self.text_color)
        self.btn_tab_timer.configure(fg_color="#E0D6F2", text_color=self.text_color)

        if tab_name == "Accueil":
            self.update_dashboard_widgets()
            self.dashboard_view.pack(fill="both", expand=True)
            self.btn_tab_dashboard.configure(fg_color=self.accent_color, text_color="#FFFFFF")
        elif tab_name == "To do list":
            self.tasks_view.pack(fill="both", expand=True)
            self.btn_tab_tasks.configure(fg_color=self.accent_color, text_color="#FFFFFF")
        elif tab_name == "Notes":
            self.force_notes_save()
            self.notes_view.pack(fill="both", expand=True)
            self.btn_tab_notes.configure(fg_color=self.accent_color, text_color="#FFFFFF")
        elif tab_name == "Timer":
            self.timer_view.pack(fill="both", expand=True)
            self.btn_tab_timer.configure(fg_color=self.accent_color, text_color="#FFFFFF")
            self.draw_stats_graph()

    # --- LOGIQUE STATS & GRAPH ---
    def draw_stats_graph(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        today = datetime.today()
        days = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
        
        max_minutes = max([self.stats_data.get(day, {}).get("work", 0) + self.stats_data.get(day, {}).get("break", 0) for day in days] + [140])

        goal_minutes = 120
        goal_y = 175 - int((goal_minutes / max_minutes) * 150)

        canvas_line = tk.Canvas(self.chart_frame, height=2, bg="#E63946", highlightthickness=0)
        canvas_line.place(x=25, y=goal_y + 35, width=420)
        
        lbl_goal = ctk.CTkLabel(self.chart_frame, text="Cible : 2h", font=("Arial", 10, "bold"), text_color="#E63946")
        lbl_goal.place(x=450, y=goal_y + 25)

        for idx, day in enumerate(days):
            self.chart_frame.grid_columnconfigure(idx, weight=1)
            day_data = self.stats_data.get(day, {"work": 0, "break": 0})
            work_m = day_data.get("work", 0)
            break_m = day_data.get("break", 0)
            total = work_m + break_m

            h_work = int((work_m / max_minutes) * 150) if work_m > 0 else 0
            h_break = int((break_m / max_minutes) * 150) if break_m > 0 else 0

            date_obj = datetime.strptime(day, "%Y-%m-%d")
            date_str = date_obj.strftime("%d/%m")

            col_frame = ctk.CTkFrame(self.chart_frame, fg_color="transparent")
            col_frame.grid(row=0, column=idx, sticky="s", padx=5, pady=10)

            text_desc = f"{work_m}m" if work_m > 0 else ""
            if break_m > 0:
                text_desc += f"\n+{break_m}m"
            lbl_count = ctk.CTkLabel(col_frame, text=text_desc, font=("Arial", 9, "bold"), text_color=self.accent_color)
            lbl_count.pack(side="top")

            bar_container = ctk.CTkFrame(col_frame, fg_color="transparent", width=26)
            bar_container.pack(side="top", pady=2)

            if h_break > 0:
                b_break = ctk.CTkFrame(bar_container, width=26, height=h_break, fg_color=self.break_color, corner_radius=3)
                b_break.pack(side="top")
            if h_work > 0:
                b_work = ctk.CTkFrame(bar_container, width=26, height=h_work, fg_color=self.accent_color, corner_radius=3)
                b_work.pack(side="top")
            if total == 0:
                b_empty = ctk.CTkFrame(bar_container, width=26, height=2, fg_color="#E0D6F2")
                b_empty.pack(side="top")

            lbl_date = ctk.CTkLabel(col_frame, text=date_str, font=("Arial", 10), text_color="gray")
            lbl_date.pack(side="top")

    def apply_custom_time(self):
        try:
            minutes = int(self.entry_min.get().strip())
            seconds = int(self.entry_sec.get().strip())
            self.pause_timer()
            self.timer_time_left = (minutes * 60) + seconds
            self.timer_initial_duration = self.timer_time_left
            self.timer_label.configure(text=f"{minutes:02d}:{seconds:02d}")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des entiers valides.")

    def log_elapsed_time(self):
        elapsed_seconds = self.timer_initial_duration - self.timer_time_left
        if elapsed_seconds >= 10:
            elapsed_minutes = elapsed_seconds / 60
            today_str = datetime.today().strftime("%Y-%m-%d")
            
            if today_str not in self.stats_data:
                self.stats_data[today_str] = {"work": 0, "break": 0}
            
            mode_key = "work" if self.timer_mode == "Travail" else "break"
            self.stats_data[today_str][mode_key] = self.stats_data[today_str].get(mode_key, 0) + round(elapsed_minutes, 1)
            
            self.timer_initial_duration = self.timer_time_left
            self.save_stats()

    def update_timer(self):
        if self.timer_running and self.timer_time_left > 0:
            self.timer_time_left -= 1
            minutes = self.timer_time_left // 60
            seconds = self.timer_time_left % 60
            self.timer_label.configure(text=f"{minutes:02d}:{seconds:02d}")
            self.timer_id = self.after(1000, self.update_timer)
        elif self.timer_time_left == 0 and self.timer_running:
            self.timer_running = False
            self.log_elapsed_time()
            
            for _ in range(3):
                winsound.Beep(880, 300)
                self.after(100)
                
            if self.timer_mode == "Travail":
                self.timer_mode = "Pause"
                self.timer_title.configure(text="Pause - Détente", text_color=self.break_color)
                self.timer_time_left = 5 * 60 
                self.timer_initial_duration = 5 * 60
                self.timer_label.configure(text="05:00")
            else:
                self.timer_mode = "Travail"
                self.timer_title.configure(text="Timer de Focus", text_color=self.text_color)
                self.timer_time_left = 25 * 60
                self.timer_initial_duration = 25 * 60
                self.timer_label.configure(text="25:00")
                
            self.draw_stats_graph()

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def pause_timer(self):
        if self.timer_running:
            self.timer_running = False
            if self.timer_id:
                self.after_cancel(self.timer_id)

    def pause_and_log_timer(self):
        self.pause_timer()
        self.log_elapsed_time()
        self.draw_stats_graph()

    def reset_and_log_timer(self):
        self.pause_timer()
        self.log_elapsed_time()
        self.timer_mode = "Travail"
        self.timer_title.configure(text="Timer de Focus", text_color=self.text_color)
        self.apply_custom_time()
        self.draw_stats_graph()

    def load_stats(self):
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, "r") as f:
                    raw_data = json.load(f)
                    self.stats_data = {}
                    for k, v in raw_data.items():
                        if isinstance(v, dict):
                            self.stats_data[k] = {
                                "work": v.get("work", 0), 
                                "break": v.get("break", 0)
                            }
                        else:
                            self.stats_data[k] = {"work": float(v), "break": 0}
            except:
                self.stats_data = {}

    def save_stats(self):
        with open(self.stats_file, "w") as f:
            json.dump(self.stats_data, f, indent=4)

    # --- OPTIMISATION NOTES MULTI-PAGES & RECHERCHE ---
    def mark_notes_as_changed(self, event):
        self.notes_modified = True

    def start_notes_autosave_loop(self):
        if self.notes_modified and self.current_note:
            self.save_current_note_content()
            self.notes_modified = False
        self.after(5000, self.start_notes_autosave_loop)

    def force_notes_save(self):
        if self.notes_modified and self.current_note:
            self.save_current_note_content()
            self.notes_modified = False

    def filter_notes_list(self):
        search_query = self.notes_search_entry.get().strip().lower()
        for filename, btn in self.note_buttons_widgets.items():
            display_name = filename[:-4].lower()
            if search_query in display_name:
                btn.pack(fill="x", pady=2)
            else:
                btn.pack_forget()

    def refresh_notes_list(self):
        for btn in self.note_buttons_widgets.values():
            btn.destroy()
        self.note_buttons_widgets.clear()

        files = [f for f in os.listdir(self.notes_dir) if f.endswith(".txt")]
        for file in files:
            display_name = file[:-4]
            btn = ctk.CTkButton(self.notes_list_container, text=display_name, fg_color="transparent", text_color=self.text_color, hover_color="#E0D6F2", anchor="w", height=35)
            btn.pack(fill="x", pady=2)
            btn.bind("<Button-1>", lambda event, f=file: self.load_note_content(f))
            btn.bind("<Double-Button-1>", lambda event: self.prompt_rename_note())
            btn.bind("<Button-3>", lambda event, f=file: self.show_context_menu(event, f))
            self.note_buttons_widgets[file] = btn

        if self.current_note and self.current_note in self.note_buttons_widgets:
            self.highlight_active_note_button(self.current_note)
        else:
            self.notes_box.delete("1.0", "end")
            self.notes_title.configure(text="Sélectionnez ou créez une note")
            self.current_note = None

    def show_context_menu(self, event, filename):
        self.load_note_content(filename)
        self.notes_context_menu.post(event.x_root, event.y_root)

    def highlight_active_note_button(self, filename):
        for f, btn in self.note_buttons_widgets.items():
            if f == filename:
                btn.configure(fg_color="#E0D6F2", font=("Arial", 13, "bold"))
            else:
                btn.configure(fg_color="transparent", font=("Arial", 13))

    def load_note_content(self, filename):
        self.force_notes_save()
        self.current_note = filename
        self.notes_title.configure(text=filename[:-4])
        self.highlight_active_note_button(filename)
        path = os.path.join(self.notes_dir, filename)
        self.notes_box.delete("1.0", "end")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.notes_box.insert("1.0", f.read())

    def save_current_note_content(self):
        if self.current_note:
            path = os.path.join(self.notes_dir, self.current_note)
            content = self.notes_box.get("1.0", "end-1c")
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

    def create_new_note(self):
        self.force_notes_save()
        i = 1
        filename = f"Sans_titre_{i}.txt"
        while os.path.exists(os.path.join(self.notes_dir, filename)):
            i += 1
            filename = f"Sans_titre_{i}.txt"
        with open(os.path.join(self.notes_dir, filename), "w", encoding="utf-8") as f:
            f.write("")
        self.current_note = filename
        self.refresh_notes_list()
        self.load_note_content(filename)

    def prompt_rename_note(self):
        if not self.current_note:
            return
        dialog = ctk.CTkInputDialog(text="Entrez le nouveau nom de la note :", title="Renommer")
        new_name = dialog.get_input()
        if new_name and new_name.strip():
            new_name = new_name.strip()
            new_filename = new_name if new_name.endswith(".txt") else new_name + ".txt"
            old_path = os.path.join(self.notes_dir, self.current_note)
            new_path = os.path.join(self.notes_dir, new_filename)
            if os.path.exists(new_path):
                messagebox.showerror("Erreur", "Une note porte déjà ce nom.")
                return
            os.rename(old_path, new_path)
            self.current_note = new_filename
            self.refresh_notes_list()

    def delete_current_note(self):
        if not self.current_note:
            return
        if messagebox.askyesno("Confirmation", f"Supprimer la note '{self.current_note[:-4]}' ?"):
            path = os.path.join(self.notes_dir, self.current_note)
            if os.path.exists(path):
                os.remove(path)
                self.current_note = None
                self.refresh_notes_list()

    def export_current_note(self):
        if not self.current_note:
            return
        content = self.notes_box.get("1.0", "end-1c")
        export_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Fichiers texte", "*.txt")], initialfile=self.current_note)
        if export_path:
            with open(export_path, "w", encoding="utf-8") as f:
                f.write(content)

    def toggle_text_tag(self, tag_name):
        try:
            start = self.notes_box._textbox.index("sel.first")
            end = self.notes_box._textbox.index("sel.last")
            current_tags = self.notes_box._textbox.tag_names(start)
            if tag_name in current_tags:
                self.notes_box._textbox.tag_remove(tag_name, start, end)
            else:
                self.notes_box._textbox.tag_add(tag_name, start, end)
            self.notes_modified = True
        except tk.TclError:
            pass

    def change_text_color(self):
        try:
            start = self.notes_box._textbox.index("sel.first")
            end = self.notes_box._textbox.index("sel.last")
            self.notes_box._textbox.tag_add("colored", start, end)
            self.notes_modified = True
        except tk.TclError:
            pass

    # --- LOGIQUE TO DO LIST ---
    def update_tasks_header_count(self):
        total = len(self.tasks_widgets)
        completed = sum([1 for cb in self.tasks_widgets if cb.get() == 1])
        self.main_title.configure(text=f"Ma To do list ({completed}/{total} complétées)")

    def load_tasks(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r", encoding="utf-8") as f:
                    tasks_data = json.load(f)
                    for task in tasks_data:
                        self.create_task_widget(task["text"], task["completed"], task.get("priority", False))
                self.update_tasks_header_count()
            except Exception as e:
                print(f"Erreur chargement tâches : {e}")

    def save_tasks(self):
        tasks_data = []
        for checkbox in self.tasks_widgets:
            font_tuple = checkbox.cget("font")
            is_high = len(font_tuple) > 2 and font_tuple[2] == "bold" and checkbox.cget("text_color") == "#E63946"
            tasks_data.append({
                "text": checkbox.cget("text"),
                "completed": True if checkbox.get() == 1 else False,
                "priority": is_high
            })
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(tasks_data, f, ensure_ascii=False, indent=4)

    def create_task_widget(self, text, completed=False, priority=False):
        t_color = "#E63946" if priority else self.text_color
        t_font = ("Arial", 14, "bold") if priority else ("Arial", 14)

        task_checkbox = ctk.CTkCheckBox(
            self.tasks_container, text=text, font=t_font, 
            text_color="gray" if completed else t_color, 
            border_color=self.accent_color, checkmark_color="#FFFFFF", fg_color=self.accent_color, 
            command=self.toggle_task
        )
        if completed:
            task_checkbox.select()
        task_checkbox.pack(anchor="w", fill="x", padx=10, pady=10)
        
        task_checkbox.bind("<Button-3>", lambda event, cb=task_checkbox: self.show_task_context_menu(event, cb))
        self.tasks_widgets.append(task_checkbox)

    def show_task_context_menu(self, event, checkbox_widget):
        self.selected_task_widget = checkbox_widget
        self.task_context_menu.post(event.x_root, event.y_root)

    def set_task_priority(self, is_high):
        if self.selected_task_widget:
            if is_high:
                self.selected_task_widget.configure(text_color="#E63946", font=("Arial", 14, "bold"))
            else:
                self.selected_task_widget.configure(text_color=self.text_color, font=("Arial", 14))
            self.save_tasks()
            self.update_dashboard_widgets()

    def add_task(self):
        task_text = self.task_entry.get().strip()
        if task_text:
            self.create_task_widget(task_text, completed=False)
            self.task_entry.delete(0, 'end')
            self.save_tasks()
            self.update_tasks_header_count()
            self.update_dashboard_widgets()

    def toggle_task(self):
        for checkbox in self.tasks_widgets:
            if checkbox.get() == 1:
                checkbox.configure(text_color="gray")
            else:
                font_tuple = checkbox.cget("font")
                if len(font_tuple) > 2 and font_tuple[2] == "bold":
                    checkbox.configure(text_color="#E63946")
                else:
                    checkbox.configure(text_color=self.text_color)
        self.save_tasks()
        self.update_tasks_header_count()
        self.update_dashboard_widgets()

    def clear_completed_tasks(self):
        kept_widgets = []
        for checkbox in self.tasks_widgets:
            if checkbox.get() == 1:
                checkbox.destroy()
            else:
                kept_widgets.append(checkbox)
        self.tasks_widgets = kept_widgets
        self.save_tasks()
        self.update_tasks_header_count()
        self.update_dashboard_widgets()

if __name__ == "__main__":
    app = App()
    app.mainloop()