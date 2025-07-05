"""
Dice system - RNG and dice mechanics
"""

import random
import re
from typing import Tuple


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
    
    @staticmethod
    def roll_simple(dice_faces: int, count: int = 1, bonus: int = 0) -> Tuple[int, str]:
        """Tirada simple de dados"""
        rolls = [random.randint(1, dice_faces) for _ in range(count)]
        total = sum(rolls) + bonus
        
        if count == 1:
            desc = f"1d{dice_faces}"
        else:
            desc = f"{count}d{dice_faces}"
        
        if bonus > 0:
            desc += f"+{bonus}"
        
        desc += f" = {total}"
        return total, desc