"""
Character Creation Dialog - UI for creating new characters
"""

import tkinter as tk
from tkinter import ttk, messagebox, Canvas, Frame
from ..core.character import Character


class CharacterCreationDialog(tk.Toplevel):
    """Diálogo mejorado para crear un nuevo personaje"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Crear Personaje")
        self.geometry("500x700")
        self.resizable(False, False)
        self.configure(bg='#2a2a2a')
        
        self.result = None
        
        # Centrar ventana
        self.transient(parent)
        self.grab_set()
        
        # Crear frame con scroll
        self.create_widgets()
        
    def create_widgets(self):
        """Crea los widgets del diálogo con scroll"""
        # Canvas y scrollbar
        canvas = Canvas(self, bg='#2a2a2a', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas, bg='#2a2a2a')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Marco principal dentro del frame scrollable
        main_frame = Frame(scrollable_frame, bg='#2a2a2a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title = tk.Label(main_frame, text="Crear Nuevo Aventurero", 
                        font=('Arial', 18, 'bold'), bg='#2a2a2a', fg='white')
        title.pack(pady=(0, 20))
        
        # Nombre
        tk.Label(main_frame, text="Nombre:", bg='#2a2a2a', fg='white',
                font=('Arial', 12)).pack(anchor=tk.W, pady=(10, 5))
        self.name_var = tk.StringVar()
        name_entry = tk.Entry(main_frame, textvariable=self.name_var, 
                            bg='#3a3a3a', fg='white', insertbackground='white',
                            font=('Arial', 11), width=30)
        name_entry.pack(pady=(0, 15))
        name_entry.focus()
        
        # Raza
        tk.Label(main_frame, text="Raza:", bg='#2a2a2a', fg='white',
                font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        self.race_var = tk.StringVar(value="Humano")
        
        race_frame = Frame(main_frame, bg='#2a2a2a')
        race_frame.pack(fill=tk.X, pady=(5, 15))
        
        for race, data in Character.RACES.items():
            race_option_frame = Frame(race_frame, bg='#2a2a2a')
            race_option_frame.pack(anchor=tk.W, pady=2)
            
            rb = tk.Radiobutton(race_option_frame, text=race, variable=self.race_var,
                               value=race, bg='#2a2a2a', fg='white',
                               selectcolor='#2a2a2a', activebackground='#3a3a3a',
                               font=('Arial', 10, 'bold'))
            rb.pack(side=tk.LEFT)
            
            tk.Label(race_option_frame, text=f" - {data['description']}", 
                    bg='#2a2a2a', fg='#aaaaaa', font=('Arial', 9)).pack(side=tk.LEFT)
        
        # Clase
        tk.Label(main_frame, text="Clase:", bg='#2a2a2a', fg='white',
                font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        self.class_var = tk.StringVar(value="Guerrero")
        
        class_frame = Frame(main_frame, bg='#2a2a2a')
        class_frame.pack(fill=tk.X, pady=(5, 15))
        
        for char_class, data in Character.CLASSES.items():
            class_option_frame = Frame(class_frame, bg='#2a2a2a')
            class_option_frame.pack(anchor=tk.W, pady=2)
            
            rb = tk.Radiobutton(class_option_frame, text=char_class, 
                               variable=self.class_var, value=char_class,
                               bg='#2a2a2a', fg='white', selectcolor='#2a2a2a',
                               activebackground='#3a3a3a', font=('Arial', 10, 'bold'))
            rb.pack(side=tk.LEFT)
            
            tk.Label(class_option_frame, text=f" - {data['description']}", 
                    bg='#2a2a2a', fg='#aaaaaa', font=('Arial', 9)).pack(side=tk.LEFT)
        
        # Distribución de puntos de atributo
        tk.Label(main_frame, text="Puntos de Atributo (24 puntos):", 
                bg='#2a2a2a', fg='white', font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(15, 10))
        
        attr_frame = Frame(main_frame, bg='#2a2a2a')
        attr_frame.pack(pady=(5, 15))
        
        self.attr_vars = {}
        self.attr_labels = {}
        attributes = ["fuerza", "destreza", "constitucion", "inteligencia", "sabiduria", "carisma"]
        
        for i, attr in enumerate(attributes):
            attr_row = Frame(attr_frame, bg='#2a2a2a')
            attr_row.pack(fill=tk.X, pady=2)
            
            tk.Label(attr_row, text=f"{attr.capitalize()}:", width=12, anchor=tk.W,
                    bg='#2a2a2a', fg='white', font=('Arial', 10)).pack(side=tk.LEFT)
            
            var = tk.IntVar(value=3)
            self.attr_vars[attr] = var
            
            minus_btn = tk.Button(attr_row, text="-", width=3,
                                bg='#3a3a3a', fg='white',
                                command=lambda a=attr: self.adjust_attribute(a, -1))
            minus_btn.pack(side=tk.LEFT, padx=2)
            
            label = tk.Label(attr_row, text="3", width=4, bg='#2a2a2a', fg='white',
                           font=('Arial', 10, 'bold'))
            label.pack(side=tk.LEFT, padx=5)
            self.attr_labels[attr] = label
            
            plus_btn = tk.Button(attr_row, text="+", width=3,
                               bg='#3a3a3a', fg='white',
                               command=lambda a=attr: self.adjust_attribute(a, 1))
            plus_btn.pack(side=tk.LEFT, padx=2)
        
        # Puntos restantes
        self.points_label = tk.Label(main_frame, text="Puntos restantes: 6",
                                   bg='#2a2a2a', fg='#FFD700', font=('Arial', 11, 'bold'))
        self.points_label.pack(pady=10)
        
        # Botones
        button_frame = Frame(main_frame, bg='#2a2a2a')
        button_frame.pack(pady=20)
        
        create_btn = tk.Button(button_frame, text="Crear Personaje", 
                             command=self.create_character,
                             bg='#4a9eff', fg='white', font=('Arial', 11, 'bold'),
                             padx=20, pady=5)
        create_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancelar", 
                             command=self.destroy,
                             bg='#ff4444', fg='white', font=('Arial', 11, 'bold'),
                             padx=20, pady=5)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def adjust_attribute(self, attribute: str, delta: int):
        """Ajusta un atributo"""
        current = self.attr_vars[attribute].get()
        points_spent = sum(var.get() - 3 for var in self.attr_vars.values())
        points_remaining = 24 - points_spent
        
        # Verificar límites
        new_value = current + delta
        if new_value < 1 or new_value > 10:
            return
        
        if delta > 0 and points_remaining <= 0:
            return
        
        # Actualizar valor
        self.attr_vars[attribute].set(new_value)
        self.attr_labels[attribute].config(text=str(new_value))
        
        # Actualizar puntos restantes
        points_spent = sum(var.get() - 3 for var in self.attr_vars.values())
        points_remaining = 24 - points_spent
        self.points_label.config(text=f"Puntos restantes: {points_remaining}")
    
    def create_character(self):
        """Crea el personaje con los datos ingresados"""
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Por favor ingresa un nombre")
            return
        
        # Verificar puntos gastados
        points_spent = sum(var.get() - 3 for var in self.attr_vars.values())
        if points_spent != 24:
            messagebox.showerror("Error", "Debes usar exactamente 24 puntos de atributo")
            return
        
        self.result = {
            "name": name,
            "race": self.race_var.get(),
            "class": self.class_var.get(),
            "attributes": {attr: var.get() for attr, var in self.attr_vars.items()}
        }
        
        self.destroy()