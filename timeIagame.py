#!/usr/bin/env python3
"""
Prototipo Habitación del Tiempo 0.1
Sistema de RPG con IA - Entrena hasta volverte leyenda
Autor: Assistant
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Canvas, Frame
import json
import random
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import re
from dataclasses import dataclass, asdict
import openai
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Por favor configura OPENAI_API_KEY en tu archivo .env")

openai.api_key = OPENAI_API_KEY

# ============= SISTEMA DE JUEGO =============

@dataclass
class CharacterStats:
    """Estadísticas base del personaje"""
    vitalidad: int = 100
    mana: int = 10
    ataque: int = 10
    defensa: int = 8
    ataque_magico: int = 10
    defensa_magica: int = 8
    fortaleza: int = 0
    resistencia: int = 0
    
@dataclass
class Attributes:
    """Atributos base del personaje"""
    fuerza: int = 3
    destreza: int = 3
    constitucion: int = 3
    inteligencia: int = 3
    sabiduria: int = 3
    carisma: int = 3

class DiceSystem:
    """Sistema de dados del juego"""
    
    @staticmethod
    def roll(dice_str: str) -> Tuple[int, str]:
        """
        Realiza una tirada de dados
        Formato: XdY+Z donde X=cantidad, Y=caras, Z=bonus
        Retorna: (resultado, descripción)
        """
        pattern = r'(\d+)d(\d+)(?:\+(\d+))?'
        match = re.match(pattern, dice_str)
        
        if not match:
            return 0, "Formato inválido"
        
        cantidad = int(match.group(1))
        caras = int(match.group(2))
        bonus = int(match.group(3)) if match.group(3) else 0
        
        rolls = [random.randint(1, caras) for _ in range(cantidad)]
        total = sum(rolls) + bonus
        
        desc = f"{cantidad}d{caras}"
        if bonus > 0:
            desc += f"+{bonus}"
        desc += f" = {rolls}"
        if bonus > 0:
            desc += f" + {bonus}"
        desc += f" = {total}"
        
        return total, desc
    
    @staticmethod
    def roll_d100_with_bonus(bonus: int = 0) -> Tuple[int, str]:
        """Tirada d100 con bonus (sistema principal)"""
        roll = random.randint(1, 100)
        total = roll + bonus
        return total, f"1d100+{bonus} = {roll} + {bonus} = {total}"

class Character:
    """Clase que representa un personaje jugador"""
    
    RACES = {
        "Humano": {
            "stats": CharacterStats(vitalidad=100, mana=10, ataque=10, defensa=8, 
                                  ataque_magico=10, defensa_magica=8),
            "attr_bonus": {"fuerza": 1, "destreza": 1, "constitucion": 1, 
                          "inteligencia": 1, "sabiduria": 1, "carisma": 1},
            "description": "Versátiles y adaptables, dominan cualquier disciplina"
        },
        "Elfo": {
            "stats": CharacterStats(vitalidad=120, mana=15, ataque=12, defensa=10,
                                  ataque_magico=12, defensa_magica=10),
            "attr_bonus": {"destreza": 2, "sabiduria": 1},
            "description": "Ágiles y sabios, con afinidad natural por la magia"
        },
        "Enano": {
            "stats": CharacterStats(vitalidad=90, mana=8, ataque=16, defensa=13,
                                  ataque_magico=16, defensa_magica=16),
            "attr_bonus": {"constitucion": 2, "fuerza": 2},
            "description": "Robustos guerreros, resistentes como la roca"
        },
        "Orco": {
            "stats": CharacterStats(vitalidad=150, mana=10, ataque=18, defensa=14,
                                  ataque_magico=18, defensa_magica=14),
            "attr_bonus": {"fuerza": 2, "constitucion": 1},
            "description": "Guerreros feroces nacidos para el combate"
        }
    }
    
    CLASSES = {
        "Guerrero": {
            "attr_bonus": {"fuerza": 1, "constitucion": 1},
            "buff_weapons": ["Espada", "Hacha", "Lanza"],
            "buff_mult": 1.10,
            "description": "Maestro del combate cuerpo a cuerpo"
        },
        "Mago": {
            "attr_bonus": {"inteligencia": 1, "sabiduria": 1},
            "buff_weapons": ["Hechizo"],
            "buff_mult": 1.30,
            "description": "Manipulador de las fuerzas arcanas"
        },
        "Arquero": {
            "attr_bonus": {"destreza": 1, "sabiduria": 1},
            "buff_weapons": ["Arco"],
            "buff_mult": 1.15,
            "description": "Experto en combate a distancia"
        },
        "Asesino": {
            "attr_bonus": {"destreza": 1, "inteligencia": 1},
            "buff_weapons": ["Daga", "Veneno"],
            "buff_mult": 1.15,
            "description": "Maestro del sigilo y los golpes críticos"
        }
    }
    
    def __init__(self, name: str, race: str, char_class: str):
        self.name = name
        self.race = race
        self.char_class = char_class
        self.level = 1
        self.experience = 0
        self.exp_to_next = 100
        self.gold = 50
        self.hp_actual = 0
        self.mana_actual = 0
        
        # Inicializar stats base de la raza
        race_data = self.RACES[race]
        self.stats = CharacterStats(**asdict(race_data["stats"]))
        
        # Inicializar atributos
        self.attributes = Attributes()
        
        # Aplicar bonus de raza
        for attr, bonus in race_data["attr_bonus"].items():
            setattr(self.attributes, attr, getattr(self.attributes, attr) + bonus)
        
        # Aplicar bonus de clase
        class_data = self.CLASSES[char_class]
        for attr, bonus in class_data["attr_bonus"].items():
            setattr(self.attributes, attr, getattr(self.attributes, attr) + bonus)
        
        # Calcular HP y Mana máximos
        self.hp_max = self.stats.vitalidad
        self.hp_actual = self.hp_max
        self.mana_max = self.stats.mana
        self.mana_actual = self.mana_max
        
        # Inventario y equipo
        self.inventory = []
        self.equipment = {
            "arma": None,
            "armadura": None,
            "accesorio": None
        }
        
        # Estado
        self.in_combat = False
        self.status_effects = []
        self.kills = 0
        self.deaths = 0
        
    def get_attribute_bonus(self, attribute: str) -> int:
        """Obtiene el bonus de un atributo según las reglas"""
        value = getattr(self.attributes, attribute)
        if value >= 10:
            return 35
        elif value == 9:
            return 30
        elif value == 8:
            return 25
        elif value == 7:
            return 20
        elif value == 6:
            return 15
        else:
            return 0
    
    def get_attack_dice(self) -> str:
        """Obtiene los dados de ataque del personaje"""
        base = f"1d{self.stats.ataque}"
        if self.stats.fortaleza > 0:
            base += f"+{self.stats.fortaleza}"
        return base
    
    def get_defense_dice(self) -> str:
        """Obtiene los dados de defensa del personaje"""
        base = f"1d{self.stats.defensa}"
        if self.stats.resistencia > 0:
            base += f"+{self.stats.resistencia}"
        return base
    
    def take_damage(self, damage: int):
        """Recibe daño"""
        self.hp_actual = max(0, self.hp_actual - damage)
        
    def heal(self, amount: int):
        """Cura puntos de vida"""
        self.hp_actual = min(self.hp_max, self.hp_actual + amount)
        
    def spend_mana(self, amount: int) -> bool:
        """Gasta maná, retorna True si tiene suficiente"""
        if self.mana_actual >= amount:
            self.mana_actual -= amount
            return True
        return False
    
    def restore_mana(self, amount: int):
        """Restaura maná"""
        self.mana_actual = min(self.mana_max, self.mana_actual + amount)
        
    def add_experience(self, amount: int):
        """Añade experiencia y verifica subida de nivel"""
        self.experience += amount
        while self.experience >= self.exp_to_next:
            self.level_up()
    
    def level_up(self):
        """Sube de nivel"""
        self.level += 1
        self.experience -= self.exp_to_next
        self.exp_to_next = int(self.exp_to_next * 1.5)
        
        # Mejorar stats
        self.hp_max += 20
        self.hp_actual = self.hp_max
        self.mana_max += 5
        self.mana_actual = self.mana_max
        self.stats.fortaleza += 2
        self.stats.resistencia += 2
    
    def to_dict(self) -> dict:
        """Convierte el personaje a diccionario para guardar"""
        return {
            "name": self.name,
            "race": self.race,
            "class": self.char_class,
            "level": self.level,
            "experience": self.experience,
            "exp_to_next": self.exp_to_next,
            "gold": self.gold,
            "hp_actual": self.hp_actual,
            "mana_actual": self.mana_actual,
            "stats": asdict(self.stats),
            "attributes": asdict(self.attributes),
            "inventory": self.inventory,
            "equipment": self.equipment,
            "kills": self.kills,
            "deaths": self.deaths
        }

class Enemy:
    """Clase simple para enemigos"""
    
    ENEMY_TYPES = {
        "Lobo Sombrío": {
            "cr": 1,
            "hp": 150,
            "attack": "1d20+10",
            "defense": "1d15+10",
            "exp": 50,
            "gold_range": (10, 30),
            "description": "Un lobo con ojos rojos brillantes y colmillos como dagas"
        },
        "Goblin Salvaje": {
            "cr": 2,
            "hp": 350,
            "attack": "1d40+15",
            "defense": "1d25+15",
            "exp": 100,
            "gold_range": (20, 50),
            "description": "Un goblin cubierto de cicatrices que gruñe amenazante"
        },
        "Orco Berserker": {
            "cr": 3,
            "hp": 750,
            "attack": "1d60+30",
            "defense": "1d40+30",
            "exp": 200,
            "gold_range": (40, 100),
            "description": "Un orco masivo con músculos como rocas y un hacha gigante"
        },
        "Espectro Errante": {
            "cr": 4,
            "hp": 500,
            "attack": "1d80+40",
            "defense": "1d30+20",
            "exp": 300,
            "gold_range": (60, 150),
            "description": "Una figura etérea que flota, emanando frío mortal"
        }
    }
    
    def __init__(self, enemy_type: str):
        self.type = enemy_type
        data = self.ENEMY_TYPES[enemy_type]
        self.cr = data["cr"]
        self.hp_max = data["hp"]
        self.hp_current = self.hp_max
        self.attack_dice = data["attack"]
        self.defense_dice = data["defense"]
        self.description = data["description"]
        self.exp_reward = data["exp"]
        self.gold_range = data["gold_range"]
        self.is_alive = True
    
    def take_damage(self, damage: int):
        """Recibe daño"""
        self.hp_current = max(0, self.hp_current - damage)
        if self.hp_current <= 0:
            self.is_alive = False

class CombatSystem:
    """Sistema de combate del juego"""
    
    def __init__(self):
        self.dice = DiceSystem()
    
    def calculate_damage(self, attack_roll: int, defense_roll: int) -> int:
        """Calcula el daño según las reglas"""
        damage = attack_roll - defense_roll
        return max(0, damage)
    
    def player_attack(self, player: Character, enemy: Enemy) -> dict:
        """Ejecuta un ataque del jugador"""
        attack_roll, attack_desc = self.dice.roll(player.get_attack_dice())
        defense_roll, defense_desc = self.dice.roll(enemy.defense_dice)
        
        damage = self.calculate_damage(attack_roll, defense_roll)
        enemy.take_damage(damage)
        
        return {
            "attack_roll": attack_roll,
            "attack_desc": attack_desc,
            "defense_roll": defense_roll,
            "defense_desc": defense_desc,
            "damage": damage,
            "enemy_hp": enemy.hp_current,
            "enemy_defeated": not enemy.is_alive
        }
    
    def enemy_attack(self, enemy: Enemy, player: Character) -> dict:
        """Ejecuta un ataque del enemigo"""
        attack_roll, attack_desc = self.dice.roll(enemy.attack_dice)
        defense_roll, defense_desc = self.dice.roll(player.get_defense_dice())
        
        damage = self.calculate_damage(attack_roll, defense_roll)
        player.take_damage(damage)
        
        return {
            "attack_roll": attack_roll,
            "attack_desc": attack_desc,
            "defense_roll": defense_roll,
            "defense_desc": defense_desc,
            "damage": damage,
            "player_hp": player.hp_actual,
            "player_defeated": player.hp_actual <= 0
        }

# ============= SISTEMA DE IA NARRATIVA =============

class AIGameMaster:
    """IA que actúa como Game Master"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.conversation_history = []
        self.world_context = {
            "current_location": "",
            "explored_locations": [],
            "active_quests": [],
            "npcs_met": []
        }
        
        # Prompt del sistema
        self.system_prompt = """Eres el Narrador de la Habitación del Tiempo, una dimensión mística donde los guerreros entrenan.

REGLAS IMPORTANTES:
1. Siempre describe las escenas de forma inmersiva y atmosférica
2. La Habitación del Tiempo es un espacio infinito con diferentes zonas de entrenamiento
3. Cuando el jugador busque enemigos o explore, describe lo que encuentra
4. NO realices tiradas de dados - solo describe las situaciones
5. Cuando aparezca un enemigo, describe su apariencia y espera la acción del jugador
6. Las descripciones deben ser concisas pero evocativas (máximo 3 párrafos)
7. Siempre termina con una pregunta o situación que requiera decisión del jugador

CONTEXTO DEL MUNDO:
- La Habitación del Tiempo es una dimensión especial donde el tiempo fluye diferente
- Contiene diversas zonas: desiertos infinitos, montañas flotantes, bosques oscuros, etc.
- Los enemigos aparecen como manifestaciones de energía para entrenar
- El objetivo es volverse más fuerte enfrentando desafíos cada vez mayores

Responde SOLO con la narración, sin metadatos ni explicaciones."""
    
    def generate_narration(self, player_input: str, character: Character) -> str:
        """Genera narración basada en la entrada del jugador"""
        try:
            # Preparar contexto del personaje
            char_context = f"""
Personaje actual:
- Nombre: {character.name}
- Raza: {character.race}
- Clase: {character.char_class}
- Nivel: {character.level}
- HP: {character.hp_actual}/{character.hp_max}
- Maná: {character.mana_actual}/{character.mana_max}
- Ubicación actual: {self.world_context.get('current_location', 'Entrada de la Habitación del Tiempo')}
"""
            
            # Agregar entrada del usuario al historial
            self.conversation_history.append({
                "role": "user",
                "content": f"{char_context}\n\nAcción del jugador: {player_input}"
            })
            
            # Mantener historial manejable (últimos 10 mensajes)
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(self.conversation_history[-10:])
            
            # Generar respuesta
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=500,
                temperature=0.8
            )
            
            narration = response.choices[0].message.content
            
            # Agregar respuesta al historial
            self.conversation_history.append({
                "role": "assistant",
                "content": narration
            })
            
            return narration
            
        except Exception as e:
            return f"*Las energías dimensionales fluctúan... (Error: {str(e)})*"
    
    def generate_initial_scene(self, character: Character) -> str:
        """Genera la escena inicial para un nuevo personaje"""
        prompt = f"""
Un nuevo guerrero entra a la Habitación del Tiempo:
- Nombre: {character.name}
- Raza: {character.race}
- Clase: {character.char_class}

Describe su entrada a esta dimensión de entrenamiento, el ambiente que lo rodea y las primeras sensaciones que experimenta.
La entrada es un vasto espacio blanco infinito con una extraña gravedad. Menciona las diferentes zonas visibles a lo lejos.
Termina con opciones claras de qué puede hacer.
"""
        return self.generate_narration(prompt, character)
    
    def determine_encounter(self, action: str) -> Optional[str]:
        """Determina si una acción resulta en un encuentro"""
        encounter_keywords = ["buscar", "explorar", "cazar", "rastrear", "investigar", "entrenar", "pelear"]
        
        if any(keyword in action.lower() for keyword in encounter_keywords):
            if random.random() < 0.7:  # 70% de probabilidad de encuentro
                enemies = list(Enemy.ENEMY_TYPES.keys())
                # Peso por nivel del personaje
                weights = [4, 3, 2, 1]  # Favorece enemigos más débiles
                return random.choices(enemies, weights=weights)[0]
        return None

# ============= INTERFAZ GRÁFICA =============

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

class GameUI(tk.Tk):
    """Interfaz principal del juego mejorada"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Prototipo Habitación del Tiempo 0.1")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        
        # Variables del juego
        self.character = None
        self.gm = AIGameMaster()
        self.combat_system = CombatSystem()
        self.dice_system = DiceSystem()
        self.current_enemy = None
        
        # Configurar estilo
        self.configure(bg='#1a1a1a')
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Crear interfaz
        self.create_widgets()
        self.create_menu()
        
        # Iniciar juego
        self.start_game()
    
    def create_widgets(self):
        """Crea todos los widgets de la interfaz mejorada"""
        # Frame principal con dos columnas
        main_frame = tk.Frame(self, bg='#1a1a1a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configurar grid weights
        main_frame.grid_columnconfigure(0, weight=3)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Columna izquierda - Área de juego
        left_frame = tk.Frame(main_frame, bg='#1a1a1a')
        left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
        
        # Área de narración
        narration_frame = tk.LabelFrame(left_frame, text="📜 Narración", 
                                       bg='#1a1a1a', fg='white', font=('Arial', 12, 'bold'))
        narration_frame.pack(fill=tk.BOTH, expand=True)
        
        self.narration_text = scrolledtext.ScrolledText(narration_frame, 
                                                        wrap=tk.WORD, 
                                                        bg='black', 
                                                        fg='white',
                                                        font=('Arial', 11),
                                                        height=25)
        self.narration_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame de acciones
        action_frame = tk.Frame(left_frame, bg='#1a1a1a')
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Entrada de texto
        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(action_frame, textvariable=self.input_var,
                                   bg='#2a2a2a', fg='white', insertbackground='white',
                                   font=('Arial', 12), relief=tk.FLAT)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.bind('<Return>', lambda e: self.process_input())
        
        self.send_button = tk.Button(action_frame, text="➤ Enviar", 
                                    command=self.process_input,
                                    bg='#4a9eff', fg='white', font=('Arial', 11, 'bold'),
                                    activebackground='#5aAeff', relief=tk.FLAT,
                                    padx=15)
        self.send_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Botones de acción rápida
        quick_actions_frame = tk.Frame(left_frame, bg='#1a1a1a')
        quick_actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.attack_button = tk.Button(quick_actions_frame, text="⚔️ Atacar",
                                      command=self.quick_attack,
                                      bg='#8B0000', fg='white', font=('Arial', 10, 'bold'),
                                      activebackground='#AA0000', relief=tk.FLAT,
                                      state=tk.DISABLED, padx=15, pady=5)
        self.attack_button.pack(side=tk.LEFT, padx=2)
        
        self.defend_button = tk.Button(quick_actions_frame, text="🛡️ Defender",
                                      command=self.quick_defend,
                                      bg='#00008B', fg='white', font=('Arial', 10, 'bold'),
                                      activebackground='#0000AA', relief=tk.FLAT,
                                      state=tk.DISABLED, padx=15, pady=5)
        self.defend_button.pack(side=tk.LEFT, padx=2)
        
        self.perception_button = tk.Button(quick_actions_frame, text="👁️ Percepción",
                                         command=self.roll_perception,
                                         bg='#4a4a4a', fg='white', font=('Arial', 10, 'bold'),
                                         activebackground='#5a5a5a', relief=tk.FLAT,
                                         padx=15, pady=5)
        self.perception_button.pack(side=tk.LEFT, padx=2)
        
        self.rest_button = tk.Button(quick_actions_frame, text="🏕️ Descansar",
                                    command=self.rest,
                                    bg='#2a6a2a', fg='white', font=('Arial', 10, 'bold'),
                                    activebackground='#3a7a3a', relief=tk.FLAT,
                                    padx=15, pady=5)
        self.rest_button.pack(side=tk.LEFT, padx=2)
        
        # Columna derecha - Panel del personaje con scroll
        right_frame = tk.Frame(main_frame, bg='#2a2a2a', width=400)
        right_frame.grid(row=0, column=1, sticky='nsew')
        right_frame.grid_propagate(False)
        
        # Canvas y scrollbar para el panel derecho
        self.char_canvas = Canvas(right_frame, bg='#2a2a2a', highlightthickness=0)
        char_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.char_canvas.yview)
        self.char_scrollable_frame = Frame(self.char_canvas, bg='#2a2a2a')
        
        self.char_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.char_canvas.configure(scrollregion=self.char_canvas.bbox("all"))
        )
        
        self.char_canvas.create_window((0, 0), window=self.char_scrollable_frame, anchor="nw")
        self.char_canvas.configure(yscrollcommand=char_scrollbar.set)
        
        # Crear contenido del panel de personaje
        self.create_character_panel()
        
        # Empaquetar canvas y scrollbar
        self.char_canvas.pack(side="left", fill="both", expand=True)
        char_scrollbar.pack(side="right", fill="y")
        
        # Configurar estilos de las barras
        self.style.configure('HP.Horizontal.TProgressbar', 
                           background='#8B0000',
                           troughcolor='#3a3a3a',
                           bordercolor='#2a2a2a',
                           lightcolor='#8B0000',
                           darkcolor='#8B0000')
        self.style.configure('Mana.Horizontal.TProgressbar',
                           background='#00008B',
                           troughcolor='#3a3a3a',
                           bordercolor='#2a2a2a',
                           lightcolor='#00008B',
                           darkcolor='#00008B')
        self.style.configure('EXP.Horizontal.TProgressbar',
                           background='#FFD700',
                           troughcolor='#3a3a3a',
                           bordercolor='#2a2a2a',
                           lightcolor='#FFD700',
                           darkcolor='#FFD700')
    
    def create_character_panel(self):
        """Crea el panel de personaje completo con toda la información"""
        # Título del personaje
        char_frame = tk.LabelFrame(self.char_scrollable_frame, text="👤 Personaje",
                                  bg='#2a2a2a', fg='white',
                                  font=('Arial', 14, 'bold'))
        char_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas para la imagen del personaje
        self.char_image_canvas = tk.Canvas(char_frame, width=180, height=180,
                                          bg='#3a3a3a', highlightthickness=2,
                                          highlightbackground='#4a4a4a')
        self.char_image_canvas.pack(pady=10)
        
        # Placeholder para imagen
        self.char_image_canvas.create_oval(40, 30, 140, 130, fill='#5a5a5a', outline='#6a6a6a', width=2)
        self.char_image_canvas.create_text(90, 80, text="Avatar", fill='gray', font=('Arial', 14))
        
        # Información básica
        self.char_info_frame = tk.Frame(char_frame, bg='#2a2a2a')
        self.char_info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Stats con barras
        self.stats_frame = tk.LabelFrame(char_frame, text="📊 Estadísticas",
                                        bg='#2a2a2a', fg='white', font=('Arial', 11, 'bold'))
        self.stats_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        # HP
        hp_frame = tk.Frame(self.stats_frame, bg='#2a2a2a')
        hp_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.hp_label = tk.Label(hp_frame, text="❤️ HP: 100/100",
                                bg='#2a2a2a', fg='white', font=('Arial', 10))
        self.hp_label.pack(anchor=tk.W)
        
        self.hp_var = tk.DoubleVar(value=100)
        self.hp_bar = ttk.Progressbar(hp_frame, variable=self.hp_var,
                                     maximum=100, length=280,
                                     style='HP.Horizontal.TProgressbar')
        self.hp_bar.pack(fill=tk.X, pady=(2, 0))
        
        # Maná
        mana_frame = tk.Frame(self.stats_frame, bg='#2a2a2a')
        mana_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.mana_label = tk.Label(mana_frame, text="💙 Maná: 10/10",
                                  bg='#2a2a2a', fg='white', font=('Arial', 10))
        self.mana_label.pack(anchor=tk.W)
        
        self.mana_var = tk.DoubleVar(value=100)
        self.mana_bar = ttk.Progressbar(mana_frame, variable=self.mana_var,
                                       maximum=100, length=280,
                                       style='Mana.Horizontal.TProgressbar')
        self.mana_bar.pack(fill=tk.X, pady=(2, 0))
        
        # Experiencia
        exp_frame = tk.Frame(self.stats_frame, bg='#2a2a2a')
        exp_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.exp_label = tk.Label(exp_frame, text="⭐ EXP: 0/100",
                                 bg='#2a2a2a', fg='white', font=('Arial', 10))
        self.exp_label.pack(anchor=tk.W)
        
        self.exp_var = tk.DoubleVar(value=0)
        self.exp_bar = ttk.Progressbar(exp_frame, variable=self.exp_var,
                                      maximum=100, length=280,
                                      style='EXP.Horizontal.TProgressbar')
        self.exp_bar.pack(fill=tk.X, pady=(2, 0))
        
        # Oro
        self.gold_label = tk.Label(self.stats_frame, text="💰 Oro: 50",
                                  bg='#2a2a2a', fg='#FFD700', font=('Arial', 10, 'bold'))
        self.gold_label.pack(anchor=tk.W, padx=5, pady=(5, 10))
        
        # Atributos
        self.attr_frame = tk.LabelFrame(char_frame, text="💪 Atributos",
                                       bg='#2a2a2a', fg='white', font=('Arial', 11, 'bold'))
        self.attr_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        # Stats de combate
        self.combat_frame = tk.LabelFrame(char_frame, text="⚔️ Combate",
                                         bg='#2a2a2a', fg='white', font=('Arial', 11, 'bold'))
        self.combat_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        # Estadísticas generales
        self.general_stats_frame = tk.LabelFrame(char_frame, text="📈 Estadísticas Generales",
                                                bg='#2a2a2a', fg='white', font=('Arial', 11, 'bold'))
        self.general_stats_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        # Equipamiento
        self.equipment_frame = tk.LabelFrame(char_frame, text="🎒 Equipamiento",
                                           bg='#2a2a2a', fg='white', font=('Arial', 11, 'bold'))
        self.equipment_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
    
    def create_menu(self):
        """Crea el menú del juego"""
        menubar = tk.Menu(self, bg='#2a2a2a', fg='white')
        self.config(menu=menubar)
        
        # Menú Juego
        game_menu = tk.Menu(menubar, tearoff=0, bg='#2a2a2a', fg='white')
        menubar.add_cascade(label="Juego", menu=game_menu)
        game_menu.add_command(label="Nuevo Personaje", command=self.new_character)
        game_menu.add_command(label="Guardar", command=self.save_game)
        game_menu.add_command(label="Cargar", command=self.load_game)
        game_menu.add_separator()
        game_menu.add_command(label="Salir", command=self.quit)
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0, bg='#2a2a2a', fg='white')
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Comandos", command=self.show_commands)
        help_menu.add_command(label="Acerca de", command=self.show_about)
    
    def start_game(self):
        """Inicia el juego"""
        self.add_narration("=== PROTOTIPO HABITACIÓN DEL TIEMPO 0.1 ===\n", "title")
        self.add_narration("Bienvenido a la dimensión de entrenamiento definitiva.\n", "system")
        self.add_narration("Aquí el tiempo fluye diferente. Un día aquí es un año afuera.", "system")
        self.add_narration("Tu objetivo: volverte más fuerte que nunca.\n", "system")
        
        # Crear personaje si no existe
        if not self.character:
            self.new_character()
    
    def new_character(self):
        """Crea un nuevo personaje"""
        dialog = CharacterCreationDialog(self)
        self.wait_window(dialog)
        
        if dialog.result:
            # Crear personaje
            self.character = Character(
                dialog.result["name"],
                dialog.result["race"],
                dialog.result["class"]
            )
            
            # Aplicar atributos personalizados
            for attr, value in dialog.result["attributes"].items():
                setattr(self.character.attributes, attr, value)
            
            # Actualizar UI
            self.update_character_panel()
            
            # Generar escena inicial
            self.add_narration("\n" + "="*50 + "\n", "system")
            initial_scene = self.gm.generate_initial_scene(self.character)
            self.add_narration(initial_scene, "narration")
    
    def update_character_panel(self):
        """Actualiza el panel del personaje con toda la información"""
        if not self.character:
            return
        
        # Limpiar frames
        for widget in self.char_info_frame.winfo_children():
            widget.destroy()
        for widget in self.attr_frame.winfo_children():
            widget.destroy()
        for widget in self.combat_frame.winfo_children():
            widget.destroy()
        for widget in self.general_stats_frame.winfo_children():
            widget.destroy()
        for widget in self.equipment_frame.winfo_children():
            widget.destroy()
        
        # Información básica
        info_grid = tk.Frame(self.char_info_frame, bg='#2a2a2a')
        info_grid.pack(fill=tk.X)
        
        labels = [
            ("Nombre:", self.character.name, '#FFD700'),
            ("Raza:", self.character.race, 'white'),
            ("Clase:", self.character.char_class, 'white'),
            ("Nivel:", str(self.character.level), '#00FF00')
        ]
        
        for i, (label, value, color) in enumerate(labels):
            tk.Label(info_grid, text=label, bg='#2a2a2a', fg='gray',
                    font=('Arial', 9)).grid(row=i, column=0, sticky=tk.W, padx=(0, 5))
            tk.Label(info_grid, text=value, bg='#2a2a2a', fg=color,
                    font=('Arial', 10, 'bold')).grid(row=i, column=1, sticky=tk.W)
        
        # Actualizar barras
        hp_percent = (self.character.hp_actual / self.character.hp_max) * 100
        self.hp_var.set(hp_percent)
        self.hp_label.config(text=f"❤️ HP: {self.character.hp_actual}/{self.character.hp_max}")
        
        mana_percent = (self.character.mana_actual / self.character.mana_max) * 100
        self.mana_var.set(mana_percent)
        self.mana_label.config(text=f"💙 Maná: {self.character.mana_actual}/{self.character.mana_max}")
        
        exp_percent = (self.character.experience / self.character.exp_to_next) * 100
        self.exp_var.set(exp_percent)
        self.exp_label.config(text=f"⭐ EXP: {self.character.experience}/{self.character.exp_to_next}")
        
        self.gold_label.config(text=f"💰 Oro: {self.character.gold}")
        
        # Atributos en grid
        attr_grid = tk.Frame(self.attr_frame, bg='#2a2a2a')
        attr_grid.pack(padx=10, pady=5)
        
        attrs = self.character.attributes
        attr_data = [
            ("FUE", attrs.fuerza, self.character.get_attribute_bonus('fuerza')),
            ("DES", attrs.destreza, self.character.get_attribute_bonus('destreza')),
            ("CON", attrs.constitucion, self.character.get_attribute_bonus('constitucion')),
            ("INT", attrs.inteligencia, self.character.get_attribute_bonus('inteligencia')),
            ("SAB", attrs.sabiduria, self.character.get_attribute_bonus('sabiduria')),
            ("CAR", attrs.carisma, self.character.get_attribute_bonus('carisma'))
        ]
        
        for i, (name, value, bonus) in enumerate(attr_data):
            row = i // 2
            col = (i % 2) * 3
            
            tk.Label(attr_grid, text=f"{name}:", bg='#2a2a2a', fg='gray',
                    font=('Arial', 9)).grid(row=row, column=col, sticky=tk.W, padx=(0, 5))
            tk.Label(attr_grid, text=str(value), bg='#2a2a2a', fg='white',
                    font=('Arial', 10, 'bold')).grid(row=row, column=col+1, padx=(0, 5))
            bonus_text = f"(+{bonus})" if bonus > 0 else ""
            tk.Label(attr_grid, text=bonus_text, bg='#2a2a2a', fg='#00FF00',
                    font=('Arial', 9)).grid(row=row, column=col+2, padx=(0, 10))
        
        # Stats de combate
        combat_grid = tk.Frame(self.combat_frame, bg='#2a2a2a')
        combat_grid.pack(padx=10, pady=5)
        
        combat_stats = [
            ("Ataque:", self.character.get_attack_dice()),
            ("Defensa:", self.character.get_defense_dice()),
            ("Atk Mágico:", f"1d{self.character.stats.ataque_magico}"),
            ("Def Mágica:", f"1d{self.character.stats.defensa_magica}"),
            ("Fortaleza:", f"+{self.character.stats.fortaleza}"),
            ("Resistencia:", f"+{self.character.stats.resistencia}")
        ]
        
        for i, (label, value) in enumerate(combat_stats):
            row = i // 2
            col = (i % 2) * 2
            
            tk.Label(combat_grid, text=label, bg='#2a2a2a', fg='gray',
                    font=('Arial', 9)).grid(row=row, column=col, sticky=tk.W, padx=(0, 5))
            tk.Label(combat_grid, text=value, bg='#2a2a2a', fg='white',
                    font=('Arial', 9, 'bold')).grid(row=row, column=col+1, sticky=tk.W, padx=(0, 15))
        
        # Estadísticas generales
        stats_text = f"Enemigos derrotados: {self.character.kills}\n"
        stats_text += f"Muertes: {self.character.deaths}\n"
        stats_text += f"Tiempo en la Habitación: {self.get_play_time()}"
        
        tk.Label(self.general_stats_frame, text=stats_text, bg='#2a2a2a', fg='white',
                justify=tk.LEFT, font=('Arial', 9)).pack(anchor=tk.W, padx=10, pady=5)
        
        # Equipamiento
        equip_text = "Arma: " + (self.character.equipment['arma'] or "Ninguna") + "\n"
        equip_text += "Armadura: " + (self.character.equipment['armadura'] or "Ninguna") + "\n"
        equip_text += "Accesorio: " + (self.character.equipment['accesorio'] or "Ninguno")
        
        tk.Label(self.equipment_frame, text=equip_text, bg='#2a2a2a', fg='white',
                justify=tk.LEFT, font=('Arial', 9)).pack(anchor=tk.W, padx=10, pady=5)
    
    def get_play_time(self):
        """Obtiene el tiempo de juego formateado"""
        # Por ahora retorna un placeholder
        return "0h 15m"
    
    def add_narration(self, text: str, tag: str = "normal"):
        """Agrega texto al área de narración"""
        self.narration_text.insert(tk.END, text + "\n")
        
        # Aplicar formato según el tag
        if tag == "title":
            start = self.narration_text.index(f"end-{len(text)+1}c")
            end = self.narration_text.index("end-1c")
            self.narration_text.tag_add("title", start, end)
            self.narration_text.tag_config("title", foreground="#FFD700", 
                                         font=('Arial', 14, 'bold'))
        elif tag == "system":
            start = self.narration_text.index(f"end-{len(text)+1}c")
            end = self.narration_text.index("end-1c")
            self.narration_text.tag_add("system", start, end)
            self.narration_text.tag_config("system", foreground="#00CED1")
        elif tag == "combat":
            start = self.narration_text.index(f"end-{len(text)+1}c")
            end = self.narration_text.index("end-1c")
            self.narration_text.tag_add("combat", start, end)
            self.narration_text.tag_config("combat", foreground="#FF6347")
        elif tag == "dice":
            start = self.narration_text.index(f"end-{len(text)+1}c")
            end = self.narration_text.index("end-1c")
            self.narration_text.tag_add("dice", start, end)
            self.narration_text.tag_config("dice", foreground="#32CD32")
        elif tag == "reward":
            start = self.narration_text.index(f"end-{len(text)+1}c")
            end = self.narration_text.index("end-1c")
            self.narration_text.tag_add("reward", start, end)
            self.narration_text.tag_config("reward", foreground="#FFD700")
        
        # Auto-scroll
        self.narration_text.see(tk.END)
    
    def process_input(self):
        """Procesa la entrada del jugador"""
        if not self.character:
            messagebox.showwarning("Advertencia", "Primero debes crear un personaje")
            return
        
        user_input = self.input_var.get().strip()
        if not user_input:
            return
        
        # Mostrar entrada del jugador
        self.add_narration(f"> {user_input}", "system")
        self.input_var.set("")
        
        # Si estamos en combate, manejar comandos de combate
        if self.current_enemy and self.current_enemy.is_alive:
            self.add_narration("¡Estás en combate! Usa los botones de acción o escribe 'huir'", "combat")
            if "huir" in user_input.lower():
                self.end_combat(fled=True)
            return
        
        # Verificar si la acción resulta en un encuentro
        enemy_type = self.gm.determine_encounter(user_input)
        if enemy_type:
            self.start_combat(enemy_type)
        else:
            # Generar narración normal
            narration = self.gm.generate_narration(user_input, self.character)
            self.add_narration(narration, "narration")
    
    def start_combat(self, enemy_type: str):
        """Inicia un combate"""
        self.current_enemy = Enemy(enemy_type)
        self.character.in_combat = True
        
        # Habilitar botones de combate
        self.attack_button.config(state=tk.NORMAL)
        self.defend_button.config(state=tk.NORMAL)
        self.rest_button.config(state=tk.DISABLED)
        
        # Narración de combate
        self.add_narration(f"\n⚔️ ¡COMBATE! ⚔️", "combat")
        self.add_narration(f"¡Un {enemy_type} aparece!", "combat")
        self.add_narration(self.current_enemy.description, "narration")
        self.add_narration(f"HP del enemigo: {self.current_enemy.hp_current}/{self.current_enemy.hp_max}", "combat")
    
    def quick_attack(self):
        """Ejecuta un ataque rápido"""
        if not self.current_enemy or not self.current_enemy.is_alive:
            return
        
        # Ataque del jugador
        self.add_narration(f"\n{self.character.name} ataca al {self.current_enemy.type}!", "combat")
        
        result = self.combat_system.player_attack(self.character, self.current_enemy)
        
        self.add_narration(f"Tirada de ataque: {result['attack_desc']}", "dice")
        self.add_narration(f"Defensa enemiga: {result['defense_desc']}", "dice")
        
        if result['damage'] > 0:
            self.add_narration(f"¡Infliges {result['damage']} puntos de daño!", "combat")
        else:
            self.add_narration("¡El enemigo esquiva tu ataque!", "combat")
        
        if result['enemy_defeated']:
            self.end_combat(victory=True)
            return
        
        # Contraataque del enemigo
        self.enemy_turn()
    
    def quick_defend(self):
        """Ejecuta una defensa (reduce daño del próximo ataque)"""
        if not self.current_enemy or not self.current_enemy.is_alive:
            return
        
        self.add_narration(f"\n{self.character.name} se prepara para defender...", "combat")
        self.add_narration("Tu defensa aumenta temporalmente.", "system")
        
        # Por simplicidad, el enemigo ataca pero con menos daño
        self.enemy_turn(defending=True)
    
    def enemy_turn(self, defending=False):
        """Turno del enemigo"""
        if not self.current_enemy or not self.current_enemy.is_alive:
            return
        
        self.add_narration(f"\n¡El {self.current_enemy.type} ataca!", "combat")
        
        result = self.combat_system.enemy_attack(self.current_enemy, self.character)
        
        self.add_narration(f"Ataque enemigo: {result['attack_desc']}", "dice")
        self.add_narration(f"Tu defensa: {result['defense_desc']}", "dice")
        
        damage = result['damage']
        if defending:
            damage = int(damage * 0.5)
            self.add_narration("¡Tu postura defensiva reduce el daño a la mitad!", "system")
        
        if damage > 0:
            self.character.take_damage(damage)
            self.add_narration(f"¡Recibes {damage} puntos de daño!", "combat")
        else:
            self.add_narration("¡Esquivas el ataque!", "combat")
        
        # Actualizar panel
        self.update_character_panel()
        
        if result['player_defeated']:
            self.game_over()
    
    def end_combat(self, victory: bool = False, fled: bool = False):
        """Termina el combate"""
        self.character.in_combat = False
        
        # Deshabilitar botones de combate
        self.attack_button.config(state=tk.DISABLED)
        self.defend_button.config(state=tk.DISABLED)
        self.rest_button.config(state=tk.NORMAL)
        
        if victory and self.current_enemy:
            self.add_narration(f"\n¡VICTORIA! Has derrotado al {self.current_enemy.type}.", "combat")
            
            # Calcular recompensas
            gold = random.randint(*self.current_enemy.gold_range)
            exp = self.current_enemy.exp_reward
            
            self.add_narration(f"\n🎉 Recompensas:", "reward")
            self.add_narration(f"   +{exp} puntos de experiencia", "reward")
            self.add_narration(f"   +{gold} monedas de oro", "reward")
            
            # Aplicar recompensas
            self.character.gold += gold
            old_level = self.character.level
            self.character.add_experience(exp)
            self.character.kills += 1
            
            if self.character.level > old_level:
                self.add_narration(f"\n¡SUBISTE DE NIVEL! Ahora eres nivel {self.character.level}", "reward")
                self.add_narration("Tus estadísticas han mejorado.", "system")
            
            self.update_character_panel()
            
        elif fled:
            self.add_narration(f"\n¡Huyes del combate!", "combat")
            self.add_narration("A veces la retirada es la mejor estrategia...", "system")
        
        self.current_enemy = None
    
    def roll_perception(self):
        """Realiza una tirada de percepción"""
        if not self.character:
            return
        
        if self.character.in_combat:
            self.add_narration("¡No puedes hacer eso en combate!", "system")
            return
        
        bonus = self.character.get_attribute_bonus('sabiduria')
        roll, desc = self.dice_system.roll_d100_with_bonus(bonus)
        
        self.add_narration(f"\nTirada de Percepción: {desc}", "dice")
        
        # Determinar resultado
        if roll >= 90:
            self.add_narration("¡Éxito crítico! Percibes cada detalle del entorno.", "system")
            self.add_narration("Notas una anomalía en el espacio... parece un portal a otra zona.", "narration")
        elif roll >= 70:
            self.add_narration("Éxito. Detectas movimiento en la distancia.", "system")
            self.add_narration("Parece que hay criaturas merodeando por aquí.", "narration")
        elif roll >= 50:
            self.add_narration("Éxito parcial. Percibes lo básico del entorno.", "system")
        else:
            self.add_narration("Fallo. No notas nada fuera de lo común.", "system")
    
    def rest(self):
        """Permite al personaje descansar y recuperarse"""
        if not self.character:
            return
        
        if self.character.in_combat:
            self.add_narration("¡No puedes descansar en combate!", "system")
            return
        
        self.add_narration("\n🏕️ Te tomas un momento para descansar...", "system")
        
        # Recuperar HP y Maná
        hp_recovered = int(self.character.hp_max * 0.3)
        mana_recovered = int(self.character.mana_max * 0.5)
        
        self.character.heal(hp_recovered)
        self.character.restore_mana(mana_recovered)
        
        self.add_narration(f"Recuperas {hp_recovered} puntos de vida.", "system")
        self.add_narration(f"Recuperas {mana_recovered} puntos de maná.", "system")
        
        # Pequeña penalización de tiempo
        if random.random() < 0.2:
            self.add_narration("\nMientras descansas, sientes que algo se acerca...", "narration")
        
        self.update_character_panel()
    
    def game_over(self):
        """Maneja el fin del juego"""
        self.add_narration("\n💀 HAS MUERTO 💀", "combat")
        self.add_narration("Tu entrenamiento termina aquí... por ahora.", "system")
        
        self.character.deaths += 1
        self.character.hp_actual = int(self.character.hp_max * 0.5)
        
        self.add_narration("\nLa Habitación del Tiempo te revive con la mitad de tu vitalidad.", "system")
        self.add_narration("Aprende de tus errores y hazte más fuerte.", "system")
        
        self.update_character_panel()
    
    def save_game(self):
        """Guarda el estado del juego"""
        if not self.character:
            messagebox.showwarning("Advertencia", "No hay personaje para guardar")
            return
        
        save_data = {
            "character": self.character.to_dict(),
            "gm_history": self.gm.conversation_history[-10:],
            "world_context": self.gm.world_context,
            "timestamp": datetime.now().isoformat()
        }
        
        filename = f"save_{self.character.name.lower().replace(' ', '_')}.json"
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        self.add_narration(f"\n💾 Juego guardado como: {filename}", "system")
    
    def load_game(self):
        """Carga un juego guardado"""
        from tkinter import filedialog
        
        filename = filedialog.askopenfilename(
            title="Cargar Partida",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, "r", encoding='utf-8') as f:
                    save_data = json.load(f)
                
                # Reconstruir personaje
                char_data = save_data["character"]
                self.character = Character(char_data["name"], char_data["race"], char_data["class"])
                
                # Restaurar stats
                for key, value in char_data["stats"].items():
                    setattr(self.character.stats, key, value)
                for key, value in char_data["attributes"].items():
                    setattr(self.character.attributes, key, value)
                
                # Restaurar otros datos
                self.character.level = char_data["level"]
                self.character.experience = char_data["experience"]
                self.character.exp_to_next = char_data["exp_to_next"]
                self.character.gold = char_data["gold"]
                self.character.hp_actual = char_data["hp_actual"]
                self.character.mana_actual = char_data["mana_actual"]
                self.character.kills = char_data.get("kills", 0)
                self.character.deaths = char_data.get("deaths", 0)
                
                # Restaurar contexto del GM
                self.gm.conversation_history = save_data.get("gm_history", [])
                self.gm.world_context = save_data.get("world_context", {})
                
                self.update_character_panel()
                self.add_narration(f"\n💾 Partida cargada: {self.character.name} - Nivel {self.character.level}", "system")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar: {str(e)}")
    
    def show_commands(self):
        """Muestra los comandos disponibles"""
        commands = """
COMANDOS Y ACCIONES:

🗺️ Exploración:
- Escribe cualquier acción para interactuar con el mundo
- Usa el botón Percepción para examinar el entorno
- Palabras clave: buscar, explorar, investigar, entrenar

⚔️ Combate:
- Botón Atacar: Realiza un ataque básico
- Botón Defender: Reduce el daño del próximo ataque
- Escribe 'huir' para escapar del combate

🏕️ General:
- Botón Descansar: Recupera HP y Maná (no disponible en combate)
- Las tiradas de dados son automáticas
- Tu personaje sube de nivel con la experiencia

💡 Consejos:
- La Habitación del Tiempo tiene zonas infinitas por explorar
- Cada enemigo derrotado te hace más fuerte
- Si mueres, revives con la mitad de HP
- Guarda tu progreso frecuentemente
"""
        messagebox.showinfo("Comandos", commands)
    
    def show_about(self):
        """Muestra información sobre el juego"""
        about = """
Prototipo Habitación del Tiempo 0.1

Un juego de rol con IA donde entrenas
en una dimensión especial para volverte
más fuerte que nunca.

El tiempo aquí fluye diferente...
Un día dentro es un año afuera.

¿Hasta dónde llegarás?

Creado con Python, Tkinter y OpenAI GPT-4
"""
        messagebox.showinfo("Acerca de", about)

# ============= PUNTO DE ENTRADA =============

def main():
    """Función principal"""
    try:
        app = GameUI()
        app.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error Fatal", f"Error al iniciar el juego:\n{str(e)}")

if __name__ == "__main__":
    main()