"""
Main Game Window - Primary game interface
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Canvas, Frame
from datetime import datetime
from typing import Optional

from ..core.game_state import GameStateManager
from ..core.character import Character
from ..core.dice_system import DiceSystem
from ..core.combat_system import CombatSystem
from ..entities.enemy import Enemy
from ..ai.game_master import AIGameMaster
from ..ai.narrative_manager import NarrativeManager
from ..data.persistence import SaveManager
from .character_creation import CharacterCreationDialog


class GameMainWindow(tk.Tk):
    """Interfaz principal del juego"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Habitación del Tiempo RPG v0.2.0")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        self.configure(bg='#1a1a1a')
        
        # Inicializar sistemas de juego
        self.game_state = GameStateManager()
        self.dice_system = DiceSystem()
        self.combat_system = CombatSystem(self.dice_system)
        self.ai_gm = AIGameMaster()
        self.narrative_manager = NarrativeManager()
        self.save_manager = SaveManager()
        
        # Suscribirse a eventos del juego
        self.game_state.subscribe(self.on_game_event)
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.setup_styles()
        
        # Crear interfaz
        self.create_widgets()
        self.create_menu()
        
        # Inicializar juego
        self.start_game()
    
    def setup_styles(self):
        """Configura los estilos de la interfaz"""
        # Configurar estilos de las barras de progreso
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
    
    def create_widgets(self):
        """Crea la interfaz principal"""
        # Frame principal con dos columnas
        main_frame = tk.Frame(self, bg='#1a1a1a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configurar grid weights
        main_frame.grid_columnconfigure(0, weight=3)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Crear columna izquierda (área de juego)
        self.create_game_area(main_frame)
        
        # Crear columna derecha (panel de personaje)
        self.create_character_panel(main_frame)
    
    def create_game_area(self, parent):
        """Crea el área principal de juego"""
        left_frame = tk.Frame(parent, bg='#1a1a1a')
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
        self.create_quick_actions(left_frame)
    
    def create_quick_actions(self, parent):
        """Crea los botones de acción rápida"""
        quick_actions_frame = tk.Frame(parent, bg='#1a1a1a')
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
    
    def create_character_panel(self, parent):
        """Crea el panel del personaje"""
        right_frame = tk.Frame(parent, bg='#2a2a2a', width=400)
        right_frame.grid(row=0, column=1, sticky='nsew')
        right_frame.grid_propagate(False)
        
        # Canvas con scroll para el panel de personaje
        self.char_canvas = Canvas(right_frame, bg='#2a2a2a', highlightthickness=0)
        char_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.char_canvas.yview)
        self.char_scrollable_frame = Frame(self.char_canvas, bg='#2a2a2a')
        
        self.char_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.char_canvas.configure(scrollregion=self.char_canvas.bbox("all"))
        )
        
        self.char_canvas.create_window((0, 0), window=self.char_scrollable_frame, anchor="nw")
        self.char_canvas.configure(yscrollcommand=char_scrollbar.set)
        
        # Crear contenido del panel
        self.setup_character_panel()
        
        # Empaquetar canvas y scrollbar
        self.char_canvas.pack(side="left", fill="both", expand=True)
        char_scrollbar.pack(side="right", fill="y")
    
    def setup_character_panel(self):
        """Configura el panel de información del personaje"""
        # Título del personaje
        char_frame = tk.LabelFrame(self.char_scrollable_frame, text="👤 Personaje",
                                  bg='#2a2a2a', fg='white',
                                  font=('Arial', 14, 'bold'))
        char_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Información básica
        self.char_info_frame = tk.Frame(char_frame, bg='#2a2a2a')
        self.char_info_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        # Stats con barras
        self.create_stats_panel(char_frame)
        
        # Atributos
        self.create_attributes_panel(char_frame)
        
        # Combat stats
        self.create_combat_panel(char_frame)
        
        # Estadísticas generales
        self.create_general_stats_panel(char_frame)
    
    def create_stats_panel(self, parent):
        """Crea el panel de estadísticas con barras"""
        stats_frame = tk.LabelFrame(parent, text="📊 Estadísticas",
                                  bg='#2a2a2a', fg='white', font=('Arial', 11, 'bold'))
        stats_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        # HP
        hp_frame = tk.Frame(stats_frame, bg='#2a2a2a')
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
        mana_frame = tk.Frame(stats_frame, bg='#2a2a2a')
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
        exp_frame = tk.Frame(stats_frame, bg='#2a2a2a')
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
        self.gold_label = tk.Label(stats_frame, text="💰 Oro: 50",
                                  bg='#2a2a2a', fg='#FFD700', font=('Arial', 10, 'bold'))
        self.gold_label.pack(anchor=tk.W, padx=5, pady=(5, 10))
    
    def create_attributes_panel(self, parent):
        """Crea el panel de atributos"""
        self.attr_frame = tk.LabelFrame(parent, text="💪 Atributos",
                                       bg='#2a2a2a', fg='white', font=('Arial', 11, 'bold'))
        self.attr_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
    
    def create_combat_panel(self, parent):
        """Crea el panel de estadísticas de combate"""
        self.combat_frame = tk.LabelFrame(parent, text="⚔️ Combate",
                                         bg='#2a2a2a', fg='white', font=('Arial', 11, 'bold'))
        self.combat_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
    
    def create_general_stats_panel(self, parent):
        """Crea el panel de estadísticas generales"""
        self.general_stats_frame = tk.LabelFrame(parent, text="📈 Estadísticas",
                                                bg='#2a2a2a', fg='white', font=('Arial', 11, 'bold'))
        self.general_stats_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
    
    def create_menu(self):
        """Crea el menú principal"""
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
    
    def on_game_event(self, event: str, data):
        """Maneja eventos del sistema de juego"""
        if event == "character_set":
            self.update_character_display()
            
        elif event == "character_updated":
            self.update_character_display()
            
        elif event == "combat_started":
            self.enable_combat_ui()
            enemy = data["enemy"]
            self.add_narration(f"\n⚔️ ¡COMBATE! ⚔️", "combat")
            self.add_narration(f"¡Un {enemy.type} aparece!", "combat")
            self.add_narration(enemy.description, "narration")
            
        elif event == "combat_ended":
            self.disable_combat_ui()
            if data["victory"]:
                self.handle_victory(data["enemy"])
            elif data["fled"]:
                self.add_narration("¡Has huido del combate!", "combat")
                
        elif event == "level_up":
            self.add_narration(f"\n🎉 ¡SUBISTE DE NIVEL! Ahora eres nivel {data['new_level']}", "reward")
            
        elif event == "character_died":
            self.handle_character_death()
    
    def start_game(self):
        """Inicia el juego"""
        self.add_narration("=== HABITACIÓN DEL TIEMPO RPG v0.2.0 ===\n", "title")
        self.add_narration("Bienvenido a la dimensión de entrenamiento definitiva.\n", "system")
        self.add_narration("Aquí el tiempo fluye diferente. Un día aquí es un año afuera.", "system")
        self.add_narration("Tu objetivo: volverte más fuerte que nunca.\n", "system")
        
        # Crear personaje si no existe
        if not self.game_state.character:
            self.new_character()
    
    def new_character(self):
        """Inicia la creación de un nuevo personaje"""
        dialog = CharacterCreationDialog(self)
        self.wait_window(dialog)
        
        if dialog.result:
            # Crear personaje
            character = Character(
                dialog.result["name"],
                dialog.result["race"],
                dialog.result["class"]
            )
            
            # Aplicar atributos personalizados
            for attr, value in dialog.result["attributes"].items():
                setattr(character.attributes, attr, value)
            
            # Establecer en game state
            self.game_state.set_character(character)
            
            # Generar escena inicial
            self.add_narration("\n" + "="*50 + "\n", "system")
            initial_scene = self.ai_gm.generate_initial_scene(character)
            self.add_narration(initial_scene, "narration")
    
    def process_input(self):
        """Procesa la entrada del jugador"""
        if not self.game_state.character:
            messagebox.showwarning("Advertencia", "Primero debes crear un personaje")
            return
        
        user_input = self.input_var.get().strip()
        if not user_input:
            return
        
        # Mostrar entrada del jugador
        self.add_narration(f"> {user_input}", "system")
        self.input_var.set("")
        
        # Si estamos en combate, manejar comandos de combate
        if self.game_state.combat_active:
            if "huir" in user_input.lower():
                self.game_state.end_combat(fled=True)
            else:
                self.add_narration("¡Estás en combate! Usa los botones de acción o escribe 'huir'", "combat")
            return
        
        # Verificar si la acción resulta en un encuentro
        enemy_type = self.ai_gm.determine_encounter(user_input)
        if enemy_type:
            enemy = Enemy(enemy_type)
            self.game_state.start_combat(enemy)
        else:
            # Generar narración normal
            narration = self.ai_gm.generate_narration(user_input, self.game_state.character)
            self.add_narration(narration, "narration")
    
    def quick_attack(self):
        """Ejecuta un ataque rápido"""
        if not self.game_state.combat_active:
            return
        
        character = self.game_state.character
        enemy = self.game_state.current_enemy
        
        self.add_narration(f"\n{character.name} ataca al {enemy.type}!", "combat")
        
        result = self.combat_system.player_attack(character, enemy)
        
        self.add_narration(f"Tirada de ataque: {result['attack_desc']}", "dice")
        self.add_narration(f"Defensa enemiga: {result['defense_desc']}", "dice")
        
        if result['damage'] > 0:
            self.add_narration(f"¡Infliges {result['damage']} puntos de daño!", "combat")
        else:
            self.add_narration("¡El enemigo esquiva tu ataque!", "combat")
        
        if result['enemy_defeated']:
            self.game_state.end_combat(victory=True)
            return
        
        # Contraataque del enemigo
        self.enemy_turn()
    
    def quick_defend(self):
        """Ejecuta una defensa"""
        if not self.game_state.combat_active:
            return
        
        character = self.game_state.character
        enemy = self.game_state.current_enemy
        
        self.add_narration(f"\n{character.name} se prepara para defender...", "combat")
        
        result = self.combat_system.player_defend(character, enemy)
        
        self.add_narration(f"Defensa mejorada: {result['defense_desc']}", "dice")
        
        if result.get('damage_reduced', 0) > 0:
            self.add_narration(f"¡Tu defensa reduce {result['damage_reduced']} puntos de daño!", "system")
        
        self.game_state.update_character()
        
        if character.hp_actual <= 0:
            self.game_state.end_combat()
    
    def enemy_turn(self):
        """Turno del enemigo"""
        if not self.game_state.combat_active:
            return
        
        character = self.game_state.character
        enemy = self.game_state.current_enemy
        
        self.add_narration(f"\n¡El {enemy.type} ataca!", "combat")
        
        result = self.combat_system.enemy_attack(enemy, character)
        
        self.add_narration(f"Ataque enemigo: {result['attack_desc']}", "dice")
        self.add_narration(f"Tu defensa: {result['defense_desc']}", "dice")
        
        if result['damage'] > 0:
            self.add_narration(f"¡Recibes {result['damage']} puntos de daño!", "combat")
            self.game_state.take_damage(result['damage'])
        else:
            self.add_narration("¡Esquivas el ataque!", "combat")
        
        if result['player_defeated']:
            self.game_state.end_combat()
    
    def roll_perception(self):
        """Realiza una tirada de percepción"""
        if not self.game_state.character:
            return
        
        if self.game_state.combat_active:
            self.add_narration("¡No puedes hacer eso en combate!", "system")
            return
        
        character = self.game_state.character
        bonus = character.get_attribute_bonus('sabiduria')
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
        """Permite al personaje descansar"""
        if not self.game_state.character:
            return
        
        if self.game_state.combat_active:
            self.add_narration("¡No puedes descansar en combate!", "system")
            return
        
        character = self.game_state.character
        
        self.add_narration("\n🏕️ Te tomas un momento para descansar...", "system")
        
        # Recuperar HP y Maná
        hp_recovered = int(character.hp_max * 0.3)
        mana_recovered = int(character.mana_max * 0.5)
        
        character.heal(hp_recovered)
        character.restore_mana(mana_recovered)
        
        self.add_narration(f"Recuperas {hp_recovered} puntos de vida.", "system")
        self.add_narration(f"Recuperas {mana_recovered} puntos de maná.", "system")
        
        self.game_state.update_character()
    
    def enable_combat_ui(self):
        """Habilita la interfaz de combate"""
        self.attack_button.config(state=tk.NORMAL)
        self.defend_button.config(state=tk.NORMAL)
        self.rest_button.config(state=tk.DISABLED)
    
    def disable_combat_ui(self):
        """Deshabilita la interfaz de combate"""
        self.attack_button.config(state=tk.DISABLED)
        self.defend_button.config(state=tk.DISABLED)
        self.rest_button.config(state=tk.NORMAL)
    
    def handle_victory(self, enemy: Enemy):
        """Maneja la victoria en combate"""
        self.add_narration(f"\n¡VICTORIA! Has derrotado al {enemy.type}.", "combat")
        
        # Calcular recompensas
        gold = enemy.get_reward_gold()
        exp = enemy.exp_reward
        
        self.add_narration(f"\n🎉 Recompensas:", "reward")
        self.add_narration(f"   +{exp} puntos de experiencia", "reward")
        self.add_narration(f"   +{gold} monedas de oro", "reward")
        
        # Aplicar recompensas
        self.game_state.add_gold(gold)
        self.game_state.add_experience(exp)
        
        if self.game_state.character:
            self.game_state.character.kills += 1
            self.game_state.update_character()
    
    def handle_character_death(self):
        """Maneja la muerte del personaje"""
        self.add_narration("\n💀 HAS MUERTO 💀", "combat")
        self.add_narration("Tu entrenamiento termina aquí... por ahora.", "system")
        
        character = self.game_state.character
        if character:
            character.hp_actual = int(character.hp_max * 0.5)
            self.add_narration("\nLa Habitación del Tiempo te revive con la mitad de tu vitalidad.", "system")
            self.add_narration("Aprende de tus errores y hazte más fuerte.", "system")
            self.game_state.update_character()
    
    def update_character_display(self):
        """Actualiza la información del personaje en la UI"""
        character = self.game_state.character
        if not character:
            return
        
        # Limpiar frames de información
        for widget in self.char_info_frame.winfo_children():
            widget.destroy()
        for widget in self.attr_frame.winfo_children():
            widget.destroy()
        for widget in self.combat_frame.winfo_children():
            widget.destroy()
        for widget in self.general_stats_frame.winfo_children():
            widget.destroy()
        
        # Información básica
        info_data = [
            ("Nombre:", character.name, '#FFD700'),
            ("Raza:", character.race, 'white'),
            ("Clase:", character.char_class, 'white'),
            ("Nivel:", str(character.level), '#00FF00')
        ]
        
        for i, (label, value, color) in enumerate(info_data):
            row_frame = tk.Frame(self.char_info_frame, bg='#2a2a2a')
            row_frame.pack(fill=tk.X, pady=1)
            
            tk.Label(row_frame, text=label, bg='#2a2a2a', fg='gray',
                    font=('Arial', 9), width=8, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row_frame, text=value, bg='#2a2a2a', fg=color,
                    font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        
        # Actualizar barras de progreso
        hp_percent = (character.hp_actual / character.hp_max) * 100
        self.hp_var.set(hp_percent)
        self.hp_label.config(text=f"❤️ HP: {character.hp_actual}/{character.hp_max}")
        
        mana_percent = (character.mana_actual / character.mana_max) * 100
        self.mana_var.set(mana_percent)
        self.mana_label.config(text=f"💙 Maná: {character.mana_actual}/{character.mana_max}")
        
        exp_percent = (character.experience / character.exp_to_next) * 100
        self.exp_var.set(exp_percent)
        self.exp_label.config(text=f"⭐ EXP: {character.experience}/{character.exp_to_next}")
        
        self.gold_label.config(text=f"💰 Oro: {character.gold}")
        
        # Atributos
        attrs = character.attributes
        attr_data = [
            ("FUE", attrs.fuerza, character.get_attribute_bonus('fuerza')),
            ("DES", attrs.destreza, character.get_attribute_bonus('destreza')),
            ("CON", attrs.constitucion, character.get_attribute_bonus('constitucion')),
            ("INT", attrs.inteligencia, character.get_attribute_bonus('inteligencia')),
            ("SAB", attrs.sabiduria, character.get_attribute_bonus('sabiduria')),
            ("CAR", attrs.carisma, character.get_attribute_bonus('carisma'))
        ]
        
        attr_grid = tk.Frame(self.attr_frame, bg='#2a2a2a')
        attr_grid.pack(padx=10, pady=5)
        
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
        combat_stats = [
            ("Ataque:", character.get_attack_dice()),
            ("Defensa:", character.get_defense_dice()),
            ("Fortaleza:", f"+{character.stats.fortaleza}"),
            ("Resistencia:", f"+{character.stats.resistencia}")
        ]
        
        for label, value in combat_stats:
            stat_frame = tk.Frame(self.combat_frame, bg='#2a2a2a')
            stat_frame.pack(fill=tk.X, pady=1)
            
            tk.Label(stat_frame, text=label, bg='#2a2a2a', fg='gray',
                    font=('Arial', 9), width=12, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(stat_frame, text=value, bg='#2a2a2a', fg='white',
                    font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        
        # Estadísticas generales
        stats_text = f"Enemigos derrotados: {character.kills}\n"
        stats_text += f"Muertes: {character.deaths}"
        
        tk.Label(self.general_stats_frame, text=stats_text, bg='#2a2a2a', fg='white',
                justify=tk.LEFT, font=('Arial', 9)).pack(anchor=tk.W, padx=10, pady=5)
    
    def add_narration(self, text: str, tag: str = "normal"):
        """Agrega texto al área de narración"""
        self.narration_text.insert(tk.END, text + "\n")
        
        # Aplicar formato según el tag
        start_index = f"end-{len(text)+1}c"
        end_index = "end-1c"
        
        if tag == "title":
            self.narration_text.tag_add("title", start_index, end_index)
            self.narration_text.tag_config("title", foreground="#FFD700", 
                                         font=('Arial', 14, 'bold'))
        elif tag == "system":
            self.narration_text.tag_add("system", start_index, end_index)
            self.narration_text.tag_config("system", foreground="#00CED1")
        elif tag == "combat":
            self.narration_text.tag_add("combat", start_index, end_index)
            self.narration_text.tag_config("combat", foreground="#FF6347")
        elif tag == "dice":
            self.narration_text.tag_add("dice", start_index, end_index)
            self.narration_text.tag_config("dice", foreground="#32CD32")
        elif tag == "reward":
            self.narration_text.tag_add("reward", start_index, end_index)
            self.narration_text.tag_config("reward", foreground="#FFD700")
        
        # Auto-scroll
        self.narration_text.see(tk.END)
    
    def save_game(self):
        """Guarda el estado del juego"""
        if not self.game_state.character:
            messagebox.showwarning("Advertencia", "No hay personaje para guardar")
            return
        
        try:
            filename = self.save_manager.save_game(self.game_state, self.ai_gm, self.narrative_manager)
            self.add_narration(f"\n💾 Juego guardado como: {filename}", "system")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
    
    def load_game(self):
        """Carga un juego guardado"""
        try:
            game_data = self.save_manager.load_game()
            if game_data:
                # Restaurar estado del juego
                self.game_state = game_data["game_state"]
                self.ai_gm = game_data["ai_gm"]
                self.narrative_manager = game_data["narrative_manager"]
                
                # Reconectar observadores
                self.game_state.subscribe(self.on_game_event)
                
                self.add_narration(f"\n💾 Partida cargada: {self.game_state.character.name} - Nivel {self.game_state.character.level}", "system")
                self.update_character_display()
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
Habitación del Tiempo RPG v0.2.0

Un juego de rol con IA donde entrenas
en una dimensión especial para volverte
más fuerte que nunca.

El tiempo aquí fluye diferente...
Un día dentro es un año afuera.

¿Hasta dónde llegarás?

Arquitectura modular refactorizada
Creado con Python, Tkinter y OpenAI GPT-4
"""
        messagebox.showinfo("Acerca de", about)