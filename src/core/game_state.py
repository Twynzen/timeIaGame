"""
Game state management - Central game state and observer pattern
"""

from typing import List, Optional, Any, Callable
from .character import Character
from ..entities.enemy import Enemy


class GameStateManager:
    """Gestor central del estado del juego usando patrón Observer"""
    
    def __init__(self):
        self.character: Optional[Character] = None
        self.current_enemy: Optional[Enemy] = None
        self.combat_active: bool = False
        self.game_mode: str = "exploration"  # exploration, combat, character_creation
        self.observers: List[Callable] = []
        
        # Estado de la sesión
        self.session_data = {
            "start_time": None,
            "total_encounters": 0,
            "total_gold_earned": 0,
            "total_exp_earned": 0
        }
    
    def subscribe(self, observer: Callable):
        """Suscribe un observador a los cambios de estado"""
        if observer not in self.observers:
            self.observers.append(observer)
    
    def unsubscribe(self, observer: Callable):
        """Desuscribe un observador"""
        if observer in self.observers:
            self.observers.remove(observer)
    
    def notify_observers(self, event: str, data: Any = None):
        """Notifica a todos los observadores sobre un cambio"""
        for observer in self.observers:
            try:
                observer(event, data)
            except Exception as e:
                print(f"Error notificando observador: {e}")
    
    def set_character(self, character: Character):
        """Establece el personaje actual"""
        self.character = character
        self.notify_observers("character_set", character)
    
    def update_character(self):
        """Notifica que el personaje ha sido actualizado"""
        if self.character:
            self.notify_observers("character_updated", self.character)
    
    def start_combat(self, enemy: Enemy):
        """Inicia un combate"""
        self.current_enemy = enemy
        self.combat_active = True
        self.game_mode = "combat"
        if self.character:
            self.character.in_combat = True
        
        self.session_data["total_encounters"] += 1
        self.notify_observers("combat_started", {"enemy": enemy})
    
    def end_combat(self, victory: bool = False, fled: bool = False):
        """Termina el combate actual"""
        self.combat_active = False
        self.game_mode = "exploration"
        if self.character:
            self.character.in_combat = False
        
        combat_result = {
            "enemy": self.current_enemy,
            "victory": victory,
            "fled": fled
        }
        
        self.current_enemy = None
        self.notify_observers("combat_ended", combat_result)
    
    def add_experience(self, amount: int):
        """Añade experiencia al personaje"""
        if self.character:
            old_level = self.character.level
            self.character.add_experience(amount)
            self.session_data["total_exp_earned"] += amount
            
            if self.character.level > old_level:
                self.notify_observers("level_up", {
                    "old_level": old_level,
                    "new_level": self.character.level
                })
            
            self.update_character()
    
    def add_gold(self, amount: int):
        """Añade oro al personaje"""
        if self.character:
            self.character.gold += amount
            self.session_data["total_gold_earned"] += amount
            self.update_character()
    
    def take_damage(self, amount: int):
        """El personaje recibe daño"""
        if self.character:
            self.character.take_damage(amount)
            
            if self.character.hp_actual <= 0:
                self.character.deaths += 1
                self.notify_observers("character_died", {"damage": amount})
            
            self.update_character()
    
    def heal_character(self, amount: int):
        """Cura al personaje"""
        if self.character:
            self.character.heal(amount)
            self.update_character()
    
    def get_game_summary(self) -> dict:
        """Obtiene un resumen del estado actual del juego"""
        return {
            "character": self.character.to_dict() if self.character else None,
            "combat_active": self.combat_active,
            "current_enemy": self.current_enemy.type if self.current_enemy else None,
            "game_mode": self.game_mode,
            "session_data": self.session_data.copy()
        }
    
    def reset_game(self):
        """Reinicia el estado del juego"""
        self.character = None
        self.current_enemy = None
        self.combat_active = False
        self.game_mode = "exploration"
        self.session_data = {
            "start_time": None,
            "total_encounters": 0,
            "total_gold_earned": 0,
            "total_exp_earned": 0
        }
        self.notify_observers("game_reset", None)