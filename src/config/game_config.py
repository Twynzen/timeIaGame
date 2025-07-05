"""
Game configuration - Settings and parameters
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class GameConfig:
    """Configuración central del juego"""
    
    def __init__(self):
        # Configuración de IA
        self.ai_config = {
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "model": "gpt-4o-mini",
            "max_tokens": 500,
            "temperature": 0.8,
            "max_history_length": 10
        }
        
        # Configuración de combate
        self.combat_config = {
            "encounter_chance": 0.7,
            "critical_threshold": 90,
            "fumble_threshold": 10,
            "rest_hp_recovery": 0.3,
            "rest_mana_recovery": 0.5
        }
        
        # Configuración de experiencia y progresión
        self.progression_config = {
            "base_exp_requirement": 100,
            "exp_multiplier": 1.5,
            "hp_per_level": 20,
            "mana_per_level": 5,
            "fortaleza_per_level": 2,
            "resistencia_per_level": 2
        }
        
        # Configuración de UI
        self.ui_config = {
            "window_width": 1400,
            "window_height": 900,
            "min_width": 1200,
            "min_height": 800,
            "theme": "dark",
            "font_family": "Arial",
            "font_size": 11
        }
        
        # Configuración de guardado
        self.save_config = {
            "save_directory": "saves",
            "auto_save_interval": 300,  # 5 minutos
            "max_save_files": 20
        }
        
        # Configuración de debug
        self.debug_config = {
            "enable_logging": True,
            "log_level": "INFO",
            "log_file": "game.log",
            "enable_ai_fallback": True
        }
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de IA"""
        return self.ai_config.copy()
    
    def get_combat_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de combate"""
        return self.combat_config.copy()
    
    def get_progression_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de progresión"""
        return self.progression_config.copy()
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de UI"""
        return self.ui_config.copy()
    
    def get_save_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de guardado"""
        return self.save_config.copy()
    
    def get_debug_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de debug"""
        return self.debug_config.copy()
    
    def is_ai_enabled(self) -> bool:
        """Verifica si la IA está habilitada"""
        return bool(self.ai_config["openai_api_key"])
    
    def update_config(self, section: str, key: str, value: Any):
        """Actualiza un valor de configuración"""
        config_sections = {
            "ai": self.ai_config,
            "combat": self.combat_config,
            "progression": self.progression_config,
            "ui": self.ui_config,
            "save": self.save_config,
            "debug": self.debug_config
        }
        
        if section in config_sections and key in config_sections[section]:
            config_sections[section][key] = value
        else:
            raise ValueError(f"Invalid config section '{section}' or key '{key}'")
    
    def get_all_config(self) -> Dict[str, Dict[str, Any]]:
        """Obtiene toda la configuración"""
        return {
            "ai": self.ai_config,
            "combat": self.combat_config,
            "progression": self.progression_config,
            "ui": self.ui_config,
            "save": self.save_config,
            "debug": self.debug_config
        }