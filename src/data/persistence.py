"""
Save/Load functionality - Game state persistence
"""

import json
import os
from datetime import datetime
from tkinter import filedialog
from typing import Optional, Dict, Any

from ..core.game_state import GameStateManager
from ..core.character import Character
from ..ai.game_master import AIGameMaster
from ..ai.narrative_manager import NarrativeManager


class SaveManager:
    """Gestor de guardado y carga de partidas"""
    
    def __init__(self):
        self.save_directory = "saves"
        self.ensure_save_directory()
    
    def ensure_save_directory(self):
        """Asegura que existe el directorio de guardado"""
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
    
    def save_game(self, game_state: GameStateManager, ai_gm: AIGameMaster, 
                  narrative_manager: NarrativeManager, filename: Optional[str] = None) -> str:
        """
        Guarda el estado completo del juego
        
        Args:
            game_state: Estado actual del juego
            ai_gm: Game Master con historial de IA
            narrative_manager: Gestor narrativo
            filename: Nombre del archivo (opcional)
        
        Returns:
            Nombre del archivo guardado
        """
        if not game_state.character:
            raise ValueError("No hay personaje para guardar")
        
        # Generar nombre de archivo si no se proporciona
        if not filename:
            character_name = game_state.character.name.lower().replace(' ', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"save_{character_name}_{timestamp}.json"
        
        # Preparar datos para guardar
        save_data = {
            "version": "0.2.0",
            "timestamp": datetime.now().isoformat(),
            "character": game_state.character.to_dict(),
            "game_state": {
                "combat_active": game_state.combat_active,
                "game_mode": game_state.game_mode,
                "session_data": game_state.session_data,
                "current_enemy": game_state.current_enemy.to_dict() if game_state.current_enemy else None
            },
            "ai_gm": {
                "conversation_history": ai_gm.conversation_history[-10:],  # Últimas 10 conversaciones
                "world_context": ai_gm.world_context
            },
            "narrative": narrative_manager.to_dict()
        }
        
        # Guardar archivo
        filepath = os.path.join(self.save_directory, filename)
        with open(filepath, "w", encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def load_game(self, filename: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Carga un juego guardado
        
        Args:
            filename: Nombre del archivo a cargar (si no se proporciona, abre diálogo)
        
        Returns:
            Diccionario con los datos del juego o None si se cancela
        """
        if not filename:
            filename = filedialog.askopenfilename(
                title="Cargar Partida",
                initialdir=self.save_directory,
                filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
            )
        
        if not filename:
            return None
        
        # Cargar archivo
        with open(filename, "r", encoding='utf-8') as f:
            save_data = json.load(f)
        
        # Reconstruir objetos del juego
        game_state = self._reconstruct_game_state(save_data)
        ai_gm = self._reconstruct_ai_gm(save_data)
        narrative_manager = self._reconstruct_narrative_manager(save_data)
        
        return {
            "game_state": game_state,
            "ai_gm": ai_gm,
            "narrative_manager": narrative_manager,
            "save_data": save_data
        }
    
    def _reconstruct_game_state(self, save_data: Dict[str, Any]) -> GameStateManager:
        """Reconstruye el GameStateManager desde los datos guardados"""
        game_state = GameStateManager()
        
        # Reconstruir personaje
        char_data = save_data["character"]
        character = Character(char_data["name"], char_data["race"], char_data["class"])
        
        # Restaurar stats del personaje
        for key, value in char_data["stats"].items():
            setattr(character.stats, key, value)
        for key, value in char_data["attributes"].items():
            setattr(character.attributes, key, value)
        
        # Restaurar otros datos del personaje
        character.level = char_data["level"]
        character.experience = char_data["experience"]
        character.exp_to_next = char_data["exp_to_next"]
        character.gold = char_data["gold"]
        character.hp_actual = char_data["hp_actual"]
        character.mana_actual = char_data["mana_actual"]
        character.kills = char_data.get("kills", 0)
        character.deaths = char_data.get("deaths", 0)
        character.inventory = char_data.get("inventory", [])
        character.equipment = char_data.get("equipment", {})
        
        # Establecer personaje en game state
        game_state.set_character(character)
        
        # Restaurar estado del juego
        gs_data = save_data["game_state"]
        game_state.combat_active = gs_data["combat_active"]
        game_state.game_mode = gs_data["game_mode"]
        game_state.session_data = gs_data["session_data"]
        
        # Restaurar enemigo actual si existe
        if gs_data["current_enemy"]:
            from ..entities.enemy import Enemy
            enemy_data = gs_data["current_enemy"]
            enemy = Enemy(enemy_data["type"])
            enemy.hp_current = enemy_data["hp_current"]
            enemy.is_alive = enemy_data["is_alive"]
            game_state.current_enemy = enemy
        
        return game_state
    
    def _reconstruct_ai_gm(self, save_data: Dict[str, Any]) -> AIGameMaster:
        """Reconstruye el AIGameMaster desde los datos guardados"""
        ai_gm = AIGameMaster()
        
        ai_data = save_data.get("ai_gm", {})
        ai_gm.conversation_history = ai_data.get("conversation_history", [])
        ai_gm.world_context = ai_data.get("world_context", {})
        
        return ai_gm
    
    def _reconstruct_narrative_manager(self, save_data: Dict[str, Any]) -> NarrativeManager:
        """Reconstruye el NarrativeManager desde los datos guardados"""
        narrative_manager = NarrativeManager()
        
        narrative_data = save_data.get("narrative", {})
        if narrative_data:
            narrative_manager.from_dict(narrative_data)
        
        return narrative_manager
    
    def get_save_files(self) -> list:
        """Obtiene la lista de archivos de guardado disponibles"""
        if not os.path.exists(self.save_directory):
            return []
        
        save_files = []
        for filename in os.listdir(self.save_directory):
            if filename.endswith('.json'):
                filepath = os.path.join(self.save_directory, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    save_files.append({
                        "filename": filename,
                        "character_name": data.get("character", {}).get("name", "Unknown"),
                        "level": data.get("character", {}).get("level", 1),
                        "timestamp": data.get("timestamp", "Unknown"),
                        "version": data.get("version", "Unknown")
                    })
                except Exception:
                    continue  # Saltar archivos corruptos
        
        # Ordenar por timestamp descendente
        save_files.sort(key=lambda x: x["timestamp"], reverse=True)
        return save_files
    
    def delete_save_file(self, filename: str) -> bool:
        """
        Elimina un archivo de guardado
        
        Args:
            filename: Nombre del archivo a eliminar
        
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        filepath = os.path.join(self.save_directory, filename)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
        except Exception:
            pass
        return False