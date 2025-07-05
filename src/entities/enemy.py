"""
Enemy system - Enemy entities and their behaviors
"""

import random
from typing import Tuple


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
        if enemy_type not in self.ENEMY_TYPES:
            raise ValueError(f"Tipo de enemigo '{enemy_type}' no válido")
        
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
        
        # Estado del enemigo
        self.status_effects = []
    
    def take_damage(self, damage: int):
        """Recibe daño"""
        self.hp_current = max(0, self.hp_current - damage)
        if self.hp_current <= 0:
            self.is_alive = False
    
    def heal(self, amount: int):
        """Cura puntos de vida"""
        if self.is_alive:
            self.hp_current = min(self.hp_max, self.hp_current + amount)
    
    def get_reward_gold(self) -> int:
        """Calcula el oro que otorga al ser derrotado"""
        return random.randint(*self.gold_range)
    
    def get_hp_percentage(self) -> float:
        """Obtiene el porcentaje de vida actual"""
        return (self.hp_current / self.hp_max) * 100 if self.hp_max > 0 else 0
    
    def get_status_description(self) -> str:
        """Obtiene descripción del estado actual"""
        hp_percent = self.get_hp_percentage()
        
        if hp_percent <= 0:
            return "Derrotado"
        elif hp_percent <= 25:
            return "Gravemente herido"
        elif hp_percent <= 50:
            return "Herido"
        elif hp_percent <= 75:
            return "Ligeramente herido"
        else:
            return "Ileso"
    
    def to_dict(self) -> dict:
        """Convierte el enemigo a diccionario"""
        return {
            "type": self.type,
            "cr": self.cr,
            "hp_current": self.hp_current,
            "hp_max": self.hp_max,
            "is_alive": self.is_alive,
            "status_effects": self.status_effects
        }
    
    @classmethod
    def get_random_enemy(cls) -> 'Enemy':
        """Crea un enemigo aleatorio"""
        enemy_types = list(cls.ENEMY_TYPES.keys())
        weights = [4, 3, 2, 1]  # Favorece enemigos más débiles
        enemy_type = random.choices(enemy_types, weights=weights)[0]
        return cls(enemy_type)
    
    @classmethod
    def get_enemy_by_cr(cls, target_cr: int) -> 'Enemy':
        """Crea un enemigo basado en un CR objetivo"""
        suitable_enemies = [
            enemy_type for enemy_type, data in cls.ENEMY_TYPES.items()
            if data["cr"] <= target_cr + 1 and data["cr"] >= target_cr - 1
        ]
        
        if not suitable_enemies:
            return cls.get_random_enemy()
        
        enemy_type = random.choice(suitable_enemies)
        return cls(enemy_type)