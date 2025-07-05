"""
Combat system - Combat mechanics and resolution
"""

from typing import Dict, Any
from .dice_system import DiceSystem
from .character import Character
from ..entities.enemy import Enemy


class CombatSystem:
    """Sistema de combate del juego"""
    
    def __init__(self, dice_system: DiceSystem):
        self.dice_system = dice_system
        self.combat_log = []
    
    def calculate_damage(self, attack_roll: int, defense_roll: int) -> int:
        """Calcula el daño según las reglas"""
        damage = attack_roll - defense_roll
        return max(0, damage)
    
    def player_attack(self, player: Character, enemy: Enemy) -> Dict[str, Any]:
        """Ejecuta un ataque del jugador"""
        attack_roll, attack_desc = self.dice_system.roll(player.get_attack_dice())
        defense_roll, defense_desc = self.dice_system.roll(enemy.defense_dice)
        
        damage = self.calculate_damage(attack_roll, defense_roll)
        enemy.take_damage(damage)
        
        combat_result = {
            "action": "player_attack",
            "attack_roll": attack_roll,
            "attack_desc": attack_desc,
            "defense_roll": defense_roll,
            "defense_desc": defense_desc,
            "damage": damage,
            "enemy_hp": enemy.hp_current,
            "enemy_defeated": not enemy.is_alive
        }
        
        self.combat_log.append(combat_result)
        return combat_result
    
    def enemy_attack(self, enemy: Enemy, player: Character) -> Dict[str, Any]:
        """Ejecuta un ataque del enemigo"""
        attack_roll, attack_desc = self.dice_system.roll(enemy.attack_dice)
        defense_roll, defense_desc = self.dice_system.roll(player.get_defense_dice())
        
        damage = self.calculate_damage(attack_roll, defense_roll)
        player.take_damage(damage)
        
        combat_result = {
            "action": "enemy_attack",
            "attack_roll": attack_roll,
            "attack_desc": attack_desc,
            "defense_roll": defense_roll,
            "defense_desc": defense_desc,
            "damage": damage,
            "player_hp": player.hp_actual,
            "player_defeated": player.hp_actual <= 0
        }
        
        self.combat_log.append(combat_result)
        return combat_result
    
    def player_defend(self, player: Character, enemy: Enemy) -> Dict[str, Any]:
        """Ejecuta una acción defensiva del jugador"""
        # El jugador se defiende, lo que reduce el daño del próximo ataque
        enemy_result = self.enemy_attack(enemy, player)
        
        # Reducir daño a la mitad por defender
        if enemy_result["damage"] > 0:
            damage_reduction = enemy_result["damage"] // 2
            player.heal(damage_reduction)  # Restaurar la mitad del daño
            enemy_result["damage"] -= damage_reduction
            enemy_result["damage_reduced"] = damage_reduction
        
        enemy_result["action"] = "player_defend"
        return enemy_result
    
    def get_combat_log(self) -> list:
        """Obtiene el log completo del combate"""
        return self.combat_log.copy()
    
    def clear_combat_log(self):
        """Limpia el log de combate"""
        self.combat_log.clear()
    
    def get_last_action(self) -> Dict[str, Any]:
        """Obtiene la última acción de combate"""
        return self.combat_log[-1] if self.combat_log else {}