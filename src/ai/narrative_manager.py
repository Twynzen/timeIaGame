"""
Narrative Manager - Story state and context management
"""

from typing import Dict, List, Any
import json
from datetime import datetime


class NarrativeManager:
    """Gestor del estado narrativo y contexto de la historia"""
    
    def __init__(self):
        self.story_state = {
            "current_location": "Entrada de la Habitación del Tiempo",
            "explored_locations": [],
            "important_events": [],
            "discovered_lore": [],
            "active_storylines": []
        }
        
        self.character_memories = {}
        self.world_state = {
            "time_spent": 0,
            "reality_shifts": 0,
            "power_level": 1
        }
        
        # Configuración de locaciones
        self.locations = {
            "Entrada de la Habitación del Tiempo": {
                "description": "Un vasto espacio blanco infinito donde comienza todo viaje",
                "first_visit": True,
                "encounters_available": ["tutorial"],
                "connections": ["Desierto Dorado", "Montañas Flotantes", "Bosque Sombrio"]
            },
            "Desierto Dorado": {
                "description": "Dunas infinitas que brillan con energía mística",
                "first_visit": True,
                "encounters_available": ["Lobo Sombrío", "Goblin Salvaje"],
                "connections": ["Entrada de la Habitación del Tiempo", "Oasis Temporal"]
            },
            "Montañas Flotantes": {
                "description": "Picos suspendidos en el aire envueltos en niebla etérea",
                "first_visit": True,
                "encounters_available": ["Orco Berserker", "Espectro Errante"],
                "connections": ["Entrada de la Habitación del Tiempo", "Cima del Tiempo"]
            },
            "Bosque Sombrio": {
                "description": "Árboles antiguos donde las sombras cobran vida",
                "first_visit": True,
                "encounters_available": ["Espectro Errante", "Goblin Salvaje"],
                "connections": ["Entrada de la Habitación del Tiempo", "Corazón del Bosque"]
            }
        }
    
    def update_location(self, new_location: str) -> Dict[str, Any]:
        """Actualiza la ubicación actual del personaje"""
        old_location = self.story_state["current_location"]
        
        if new_location in self.locations:
            self.story_state["current_location"] = new_location
            
            # Marcar como explorada si es primera visita
            if new_location not in self.story_state["explored_locations"]:
                self.story_state["explored_locations"].append(new_location)
                self.locations[new_location]["first_visit"] = False
                
                # Registrar evento importante
                self.add_important_event(f"Descubrió {new_location}")
            
            return {
                "old_location": old_location,
                "new_location": new_location,
                "first_visit": self.locations[new_location]["first_visit"],
                "description": self.locations[new_location]["description"],
                "available_connections": self.locations[new_location].get("connections", [])
            }
        
        return {"error": f"Ubicación '{new_location}' no existe"}
    
    def add_important_event(self, event: str):
        """Añade un evento importante al historial narrativo"""
        timestamp = datetime.now().isoformat()
        self.story_state["important_events"].append({
            "event": event,
            "timestamp": timestamp,
            "location": self.story_state["current_location"]
        })
        
        # Mantener solo los últimos 20 eventos
        if len(self.story_state["important_events"]) > 20:
            self.story_state["important_events"] = self.story_state["important_events"][-20:]
    
    def add_discovered_lore(self, lore_item: str):
        """Añade información de lore descubierta"""
        if lore_item not in self.story_state["discovered_lore"]:
            self.story_state["discovered_lore"].append(lore_item)
            self.add_important_event(f"Descubrió lore: {lore_item}")
    
    def update_character_memory(self, character_name: str, memory: str):
        """Actualiza las memorias de un personaje específico"""
        if character_name not in self.character_memories:
            self.character_memories[character_name] = []
        
        self.character_memories[character_name].append({
            "memory": memory,
            "timestamp": datetime.now().isoformat(),
            "location": self.story_state["current_location"]
        })
        
        # Mantener solo las últimas 10 memorias por personaje
        if len(self.character_memories[character_name]) > 10:
            self.character_memories[character_name] = self.character_memories[character_name][-10:]
    
    def get_location_context(self, location: str = None) -> Dict[str, Any]:
        """Obtiene el contexto de una ubicación específica"""
        target_location = location or self.story_state["current_location"]
        
        if target_location not in self.locations:
            return {"error": "Ubicación no encontrada"}
        
        location_data = self.locations[target_location].copy()
        
        # Añadir información de visitas
        visits = len([event for event in self.story_state["important_events"] 
                     if event.get("location") == target_location])
        
        location_data["visit_count"] = visits
        location_data["is_current"] = (target_location == self.story_state["current_location"])
        
        return location_data
    
    def get_narrative_summary(self) -> str:
        """Genera un resumen narrativo del progreso"""
        locations_count = len(self.story_state["explored_locations"])
        events_count = len(self.story_state["important_events"])
        lore_count = len(self.story_state["discovered_lore"])
        
        summary = f"Has explorado {locations_count} ubicaciones, "
        summary += f"vivido {events_count} eventos importantes, "
        summary += f"y descubierto {lore_count} fragmentos de conocimiento. "
        summary += f"Actualmente te encuentras en: {self.story_state['current_location']}."
        
        if self.story_state["important_events"]:
            last_event = self.story_state["important_events"][-1]
            summary += f" Tu último logro fue: {last_event['event']}."
        
        return summary
    
    def get_available_encounters(self) -> List[str]:
        """Obtiene los encuentros disponibles en la ubicación actual"""
        current_location = self.story_state["current_location"]
        if current_location in self.locations:
            return self.locations[current_location].get("encounters_available", [])
        return []
    
    def advance_time(self, time_units: int = 1):
        """Avanza el tiempo en la narrativa"""
        self.world_state["time_spent"] += time_units
        
        # Cada cierto tiempo, pueden ocurrir cambios en la realidad
        if self.world_state["time_spent"] % 10 == 0:
            self.world_state["reality_shifts"] += 1
            self.add_important_event("La realidad se reconfigura sutilmente")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el estado narrativo a diccionario"""
        return {
            "story_state": self.story_state,
            "character_memories": self.character_memories,
            "world_state": self.world_state,
            "locations": self.locations
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Carga el estado narrativo desde un diccionario"""
        self.story_state = data.get("story_state", self.story_state)
        self.character_memories = data.get("character_memories", {})
        self.world_state = data.get("world_state", self.world_state)
        if "locations" in data:
            self.locations.update(data["locations"])