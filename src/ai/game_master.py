"""
AI Game Master - OpenAI integration for enhanced narrative generation
"""

import os
import random
import logging
from typing import Optional, Dict, Any, Tuple
from ..core.character import Character
from ..entities.enemy import Enemy
from .divine_narrator import DivineNarrator, NarrativePhase
from .image_generator import ImageGenerator

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class AIGameMaster:
    """IA que actúa como Game Master con narrativa inmersiva y generación visual"""
    
    def __init__(self, api_key: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger("AIGameMaster")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        # Configuración
        default_config = {
            "max_history_length": 10,
            "max_tokens": 500,
            "temperature": 0.8,
            "model": "gpt-4o-mini"
        }
        self.config = {**default_config, **(config or {})}
        
        # Sistemas narrativos avanzados
        self.divine_narrator = DivineNarrator()
        self.image_generator = ImageGenerator(api_key, config)
        
        # Estado del juego y contexto
        self.conversation_history = []
        self.world_context = {
            "current_location": "",
            "explored_locations": [],
            "active_quests": [],
            "npcs_met": [],
            "environmental_features": [],
            "mood_atmosphere": "neutral"
        }
        
        # Cliente OpenAI
        if OPENAI_AVAILABLE and self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)
            self.enabled = True
            self.logger.info("AIGameMaster inicializado con IA habilitada")
        else:
            self.client = None
            self.enabled = False
            self.logger.warning("AIGameMaster inicializado sin IA")
        
        # Sistema de prompts mejorado
        self.base_system_prompt = """Eres un Narrador maestro de la Habitación del Tiempo, una dimensión mística donde las almas valientes entrenan para trascender sus límites.

IDENTIDAD NARRATIVA:
- Eres una voz omnisciente que observa y describe con maestría cinematográfica
- Tu narrativa debe ser inmersiva, evocativa y ricamen descriptiva
- Adaptas tu tono y estilo según el contexto emocional del momento
- Describes tanto lo visible como lo que se siente en el ambiente

REGLAS DE NARRACIÓN:
1. IMMERSIÓN TOTAL: Cada descripción debe transportar al jugador al escenario
2. DETALLES SENSORIALES: Incluye qué se ve, oye, huele, siente
3. ATMÓSFERA DINÁMICA: El mood debe coincidir con la situación y personalidad del jugador
4. CONSECUENCIAS NARRATIVAS: Las acciones del jugador tienen impacto en el mundo
5. PACING CINEMATOGRÁFICO: Varía entre momentos intensos y pausas contemplativas

MUNDO ADAPTATIVO:
- El mundo refleja la personalidad y elecciones del protagonista
- Los escenarios cambian según el tema dominante del jugador
- Cada zona tiene características únicas que desafían aspectos específicos
- Las descripciones incluyen detalles que invitan a la exploración

ESTRUCTURA DE RESPUESTA:
1. Descripción sensorial del entorno inmediato
2. Elementos dinámicos y detalles atmosféricos 
3. Reacción del mundo a la presencia/acción del jugador
4. Gancho narrativo que invite a la siguiente acción

IMPORTANTE: No hagas tiradas de dados. Tu función es describir y narrar.
Responde SOLO con narrativa inmersiva. Sin metadatos ni explicaciones técnicas."""
    
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
    
    def start_divine_narrative(self, character: Character) -> str:
        """Inicia el proceso narrativo divino con la primera pregunta"""
        self.divine_narrator.reset()
        awakening_message = self.divine_narrator.get_awakening_message(character)
        
        # Primera pregunta automáticamente
        first_question = self.divine_narrator.get_next_question()
        
        return f"{awakening_message}\n\n{first_question}"
    
    def process_divine_response(self, player_response: str) -> Tuple[str, bool, Optional[str]]:
        """
        Procesa una respuesta a las preguntas divinas
        
        Returns:
            (response_text, is_complete, next_question)
        """
        reaction = self.divine_narrator.process_player_response(player_response)
        
        if self.divine_narrator.is_questioning_complete():
            return reaction, True, None
        else:
            next_question = self.divine_narrator.get_next_question()
            return reaction, False, next_question
    
    def generate_world_creation(self, character: Character) -> Tuple[str, Optional[str]]:
        """
        Genera la narrativa de creación del mundo y opcionalmente una imagen
        
        Returns:
            (world_creation_narrative, image_path)
        """
        world_narrative = self.divine_narrator.generate_world_creation_narrative(character)
        
        # Intentar generar imagen del mundo creado
        image_path = None
        if self.image_generator.is_available():
            try:
                narrative_context = self.divine_narrator.get_enhanced_narrative_context()
                world_description = self._extract_world_description_for_image(narrative_context)
                character_context = f"{character.race} {character.char_class} llamado {character.name}"
                
                image_path = self.image_generator.generate_scene_image(
                    world_description, 
                    character_context
                )
                
                if image_path:
                    self.logger.info(f"Imagen del mundo generada: {image_path}")
                
            except Exception as e:
                self.logger.error(f"Error generando imagen del mundo: {e}")
        
        return world_narrative, image_path
    
    def generate_initial_scene(self, character: Character) -> str:
        """Genera la escena inicial para un nuevo personaje (método legacy)"""
        # Si el proceso divino no está completo, iniciarlo
        if self.divine_narrator.get_current_phase() == NarrativePhase.AWAKENING:
            return self.start_divine_narrative(character)
        
        # Si ya se completó el proceso divino, usar narrativa mejorada
        if self.divine_narrator.get_current_phase() == NarrativePhase.ACTIVE_PLAY:
            return self._generate_contextual_scene(character)
        
        # Fallback
        return self._generate_fallback_initial_scene(character)
    
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
    
    def _generate_contextual_scene(self, character: Character) -> str:
        """Genera una escena inicial contextual basada en el mundo creado"""
        if not self.enabled:
            return self._generate_fallback_initial_scene(character)
        
        narrative_context = self.divine_narrator.get_enhanced_narrative_context()
        theme = narrative_context.get("theme", "balance")
        tone = narrative_context.get("tone", "balanced")
        
        contextual_prompt = f"""
El personaje {character.name} ({character.race} {character.char_class}) se encuentra ahora 
en el mundo personalizado que ha sido creado según su esencia.

Contexto del mundo:
- Tema dominante: {theme}
- Tono general: {tone}
- Rasgos del personaje: {', '.join(narrative_context.get('traits', []))}

Describe la primera escena después de la creación del mundo. El personaje debe encontrarse
en un lugar específico que refleje su personalidad y ofrezca oportunidades de crecimiento.
Incluye detalles sensoriales ricos y elementos que inviten a la exploración.
"""
        
        return self.generate_narration(contextual_prompt, character)
    
    def _extract_world_description_for_image(self, narrative_context: Dict[str, Any]) -> str:
        """Extrae y formatea la descripción del mundo para generar imagen"""
        theme = narrative_context.get("theme", "balance")
        tone = narrative_context.get("tone", "balanced")
        
        world_descriptions = {
            "darkness": "Un reino crepuscular con bosques de árboles negros, torres de cristal emitiendo luz desafiante, y cielos de tormenta perpetua",
            "light": "Un reino resplandeciente con campos dorados, ciudades de mármol blanco, y montañas distantes donde habitan dragones antiguos",
            "power": "Un mundo épico con titanes de piedra caminando por valles, ciudades flotantes, volcanes escupiendo oro líquido y dragones soberanos",
            "wisdom": "Un plano místico con bibliotecas infinitas flotando en el vacío, conectadas por puentes de luz solidificada",
            "freedom": "Un mundo sin fronteras con continentes flotantes navegando por cielos infinitos y ciudades nómadas de aventureros",
            "justice": "Un mundo en equilibrio con ciudades resplandecientes de justicia contrastando con tierras salvajes"
        }
        
        return world_descriptions.get(theme, "Un mundo de equilibrio perfecto donde todas las fuerzas coexisten en armonía")
    
    def generate_enhanced_narration(self, player_input: str, character: Character) -> Tuple[str, Optional[str]]:
        """
        Genera narrativa mejorada con posible imagen de escenario
        
        Returns:
            (narration_text, image_path)
        """
        # Verificar si es una acción que merece imagen
        location_keywords = ["explorar", "ir", "caminar", "viajar", "buscar", "entrar", "llegar"]
        should_generate_image = any(keyword in player_input.lower() for keyword in location_keywords)
        
        # Generar narrativa principal
        narration = self.generate_narration(player_input, character)
        
        # Generar imagen si es apropiado
        image_path = None
        if should_generate_image and self.image_generator.is_available():
            try:
                # Extraer descripción del lugar de la narrativa
                location_description = self._extract_location_from_narration(narration)
                character_context = f"{character.race} {character.char_class} de nivel {character.level}"
                
                image_path = self.image_generator.generate_scene_image(
                    location_description,
                    character_context
                )
                
            except Exception as e:
                self.logger.error(f"Error generando imagen para narración: {e}")
        
        return narration, image_path
    
    def _extract_location_from_narration(self, narration: str) -> str:
        """Extrae descripción del lugar de la narrativa para generar imagen"""
        # Tomar las primeras 200 palabras que usualmente contienen la descripción del lugar
        words = narration.split()[:200]
        location_text = " ".join(words)
        
        # Limpiar marcado de narrativa
        import re
        location_text = re.sub(r'\*[^*]*\*', '', location_text)  # Remover *acciones*
        location_text = re.sub(r'\*\*[^*]*\*\*:', '', location_text)  # Remover **nombres**:
        
        return location_text.strip()
    
    def get_narrative_status(self) -> Dict[str, Any]:
        """Obtiene el estado del sistema narrativo"""
        return {
            "divine_phase": self.divine_narrator.get_current_phase().value,
            "questions_completed": self.divine_narrator.is_questioning_complete(),
            "image_generation_available": self.image_generator.is_available(),
            "ai_enabled": self.enabled,
            "world_context": self.world_context
        }
    
    def _generate_fallback_initial_scene(self, character: Character) -> str:
        """Genera escena inicial de respaldo"""
        return f"""*La luz se desvanece y te encuentras en un vasto espacio blanco infinito...*

{character.name}, el {character.race} {character.char_class}, da sus primeros pasos en la legendaria Habitación del Tiempo. El suelo bajo tus pies es sólido pero translúcido, como cristal perfecto. A lo lejos, puedes distinguir diferentes zonas de entrenamiento: montañas flotantes envueltas en niebla, desiertos dorados que brillan con energía mística, y bosques oscuros donde las sombras parecen moverse con vida propia.

El aire aquí se siente diferente, cargado de poder y posibilidades. Cada respiración te llena de una energía que no habías sentido antes. Sabes que el tiempo fluye de manera extraña en este lugar - un día aquí podría ser equivalente a un año en el mundo exterior.

¿Hacia dónde dirigirás tus primeros pasos en tu viaje hacia la grandeza?"""