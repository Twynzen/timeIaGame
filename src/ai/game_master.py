"""
AI Game Master - OpenAI integration for narrative generation
"""

import os
import random
from typing import Optional, Dict, Any
from ..core.character import Character
from ..entities.enemy import Enemy

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class AIGameMaster:
    """IA que actúa como Game Master"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.conversation_history = []
        self.world_context = {
            "current_location": "",
            "explored_locations": [],
            "active_quests": [],
            "npcs_met": []
        }
        
        # Configuración
        self.max_history_length = 10
        self.max_tokens = 500
        self.temperature = 0.8
        
        # Cliente OpenAI
        if OPENAI_AVAILABLE and self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)
            self.enabled = True
        else:
            self.client = None
            self.enabled = False
        
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
        if not self.enabled:
            return self._generate_fallback_narration(player_input, character)
        
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
            
            # Mantener historial manejable
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(self.conversation_history[-self.max_history_length:])
            
            # Generar respuesta
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            narration = response.choices[0].message.content
            
            # Agregar respuesta al historial
            self.conversation_history.append({
                "role": "assistant",
                "content": narration
            })
            
            return narration
            
        except Exception as e:
            print(f"Error en AI GameMaster: {e}")
            return self._generate_fallback_narration(player_input, character)
    
    def generate_initial_scene(self, character: Character) -> str:
        """Genera la escena inicial para un nuevo personaje"""
        if not self.enabled:
            return self._generate_fallback_initial_scene(character)
        
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
                return Enemy.get_random_enemy().type
        return None
    
    def update_world_context(self, key: str, value: Any):
        """Actualiza el contexto del mundo"""
        if key in self.world_context:
            if isinstance(self.world_context[key], list):
                if value not in self.world_context[key]:
                    self.world_context[key].append(value)
            else:
                self.world_context[key] = value
    
    def get_context_summary(self) -> str:
        """Obtiene un resumen del contexto actual"""
        return f"Ubicación: {self.world_context.get('current_location', 'Desconocida')}, Lugares explorados: {len(self.world_context.get('explored_locations', []))}"
    
    def _generate_fallback_narration(self, player_input: str, character: Character) -> str:
        """Genera narración de respaldo cuando OpenAI no está disponible"""
        templates = [
            f"*Las energías de la Habitación del Tiempo responden a tu acción...*\n\n{character.name} {player_input.lower()}. El espacio infinito a tu alrededor parece reaccionar, creando nuevas oportunidades y desafíos. ¿Qué harás a continuación?",
            f"*El tiempo fluye diferente aquí...*\n\nMientras {character.name} {player_input.lower()}, las dimensiones se reconfiguran sutilmente. Sientes que cada acción te hace más fuerte en este lugar mágico.",
            f"*La Habitación del Tiempo observa tu progreso...*\n\nTu acción resuena por el espacio infinito. Como {character.race} {character.char_class}, sientes una conexión especial con las energías de entrenamiento que te rodean."
        ]
        return random.choice(templates)
    
    def _generate_fallback_initial_scene(self, character: Character) -> str:
        """Genera escena inicial de respaldo"""
        return f"""*La luz se desvanece y te encuentras en un vasto espacio blanco infinito...*

{character.name}, el {character.race} {character.char_class}, da sus primeros pasos en la legendaria Habitación del Tiempo. El suelo bajo tus pies es sólido pero translúcido, como cristal perfecto. A lo lejos, puedes distinguir diferentes zonas de entrenamiento: montañas flotantes envueltas en niebla, desiertos dorados que brillan con energía mística, y bosques oscuros donde las sombras parecen moverse con vida propia.

El aire aquí se siente diferente, cargado de poder y posibilidades. Cada respiración te llena de una energía que no habías sentido antes. Sabes que el tiempo fluye de manera extraña en este lugar - un día aquí podría ser equivalente a un año en el mundo exterior.

¿Hacia dónde dirigirás tus primeros pasos en tu viaje hacia la grandeza?"""