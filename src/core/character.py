"""
Character system - Core character mechanics and data
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional


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