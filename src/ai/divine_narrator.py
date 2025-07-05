"""
Divine Narrator - Sistema narrativo inmersivo con voz divina
"""

from typing import Dict, List, Optional, Any
from enum import Enum
import random
from ..core.character import Character


class NarrativePhase(Enum):
    """Fases del proceso narrativo"""
    AWAKENING = "awakening"
    QUESTIONING = "questioning" 
    WORLD_CREATION = "world_creation"
    ACTIVE_PLAY = "active_play"


class DivineNarrator:
    """
    Narrador divino que guía al jugador a través de un proceso de 3 preguntas
    para crear un mundo personalizado basado en sus respuestas
    """
    
    def __init__(self):
        self.current_phase = NarrativePhase.AWAKENING
        self.questions_asked = 0
        self.player_responses = []
        self.world_seed = {}
        self.divine_personality = self._generate_divine_personality()
        
        # Banco de preguntas divinas organizadas por temas
        self.question_bank = {
            "essence": [
                "En las profundidades de tu ser, ¿qué es lo que más anhelas encontrar en este viaje? ¿Poder, sabiduría, redención, o algo que aún no has nombrado?",
                "Si pudieras cambiar algo fundamental de ti mismo, ¿qué sería? ¿Tu pasado, tu naturaleza, o tu destino?",
                "¿Qué te impulsa más: el deseo de proteger a otros, la búsqueda de la verdad, o la necesidad de superar tus propios límites?"
            ],
            "fear_and_courage": [
                "Háblame de aquello que más temes. ¿Es la soledad, el fracaso, la pérdida de control, o algo más profundo que acecha en las sombras de tu alma?",
                "¿Cuándo fue la última vez que sentiste verdadero miedo? ¿Fue ante un enemigo, una decisión, o al mirarte en el espejo?",
                "¿Prefieres enfrentar mil enemigos en batalla o enfrentar una verdad incómoda sobre ti mismo?"
            ],
            "values_and_morality": [
                "Si tuvieras que elegir entre salvar a un inocente o obtener el poder para salvar a miles, ¿qué harías? ¿Y si no pudieras estar seguro del resultado?",
                "¿Crees que el fin justifica los medios? ¿O hay líneas que nunca deberían cruzarse, sin importar las consecuencias?",
                "En un mundo donde la justicia a menudo falla, ¿te convertirías en juez, verdugo, o buscarías otra forma de equilibrar la balanza?"
            ],
            "ambition_and_dreams": [
                "Si pudieras remodelar el mundo según tu visión, ¿cómo sería? ¿Un lugar de orden perfecto, libertad absoluta, o algo entre ambos extremos?",
                "¿Qué legado quieres dejar? ¿Ser recordado como un héroe, un sabio, un revolucionario, o prefieres que tu influencia sea sutil pero duradera?",
                "¿Hay algo por lo que estarías dispuesto a sacrificar todo lo que eres? ¿Un ideal, una persona, un propósito mayor?"
            ]
        }
        
    def _generate_divine_personality(self) -> Dict[str, str]:
        """Genera una personalidad aleatoria para la voz divina"""
        personalities = [
            {
                "name": "El Observador Eterno",
                "voice": "Una presencia antigua y sabia que habla con la paciencia de milenios",
                "style": "formal pero benevolente",
                "approach": "Hace preguntas profundas con genuina curiosidad sobre la naturaleza humana"
            },
            {
                "name": "La Fuerza Primordial", 
                "voice": "Una energía pura y poderosa que resuena desde el núcleo mismo de la realidad",
                "style": "directo pero no carente de compasión",
                "approach": "Desafía al jugador a enfrentar verdades fundamentales"
            },
            {
                "name": "El Tejedor de Destinos",
                "voice": "Una entidad misteriosa que ve todos los posibles futuros",
                "style": "enigmático y poético",
                "approach": "Plantea dilemas que revelan el carácter verdadero"
            }
        ]
        
        return random.choice(personalities)
    
    def get_awakening_message(self, character: Character) -> str:
        """Mensaje inicial cuando el personaje 'despierta' en la Habitación del Tiempo"""
        divine_name = self.divine_personality["name"]
        
        awakening_messages = [
            f"""*Una presencia inmensa se manifiesta a tu alrededor, {character.name}. No la ves, pero la sientes en cada fibra de tu ser*

**{divine_name}**: "Despierta, {character.race} {character.char_class}. Has llegado a un lugar que existe más allá del tiempo y el espacio convencionales. Aquí, en esta Habitación del Tiempo, tu verdadero potencial puede ser forjado... pero primero, debo conocerte.

No soy tu enemigo ni tu salvador. Soy simplemente quien observa, quien pregunta, quien te dará la oportunidad de crear tu propio destino. Pero para ello, necesito entender quién eres realmente, más allá de tu raza y clase.

Respóndeme con honestidad, pues tus palabras darán forma al mundo que habitarás..."

*El espacio a tu alrededor aguarda, expectante*""",
            
            f"""*El vacío blanco que te rodea comienza a pulsar con una energía sutil. Una voz resuena no en tus oídos, sino directamente en tu conciencia*

**{divine_name}**: "{character.name}... sí, ese nombre resuena con posibilidades. Has cruzado el umbral hacia un reino donde el tiempo es maleable y la realidad responde a la voluntad.

Pero antes de que puedas dar forma a tu destino en este lugar, yo debo dar forma al escenario. Y para eso, necesito mirarte no con mis ojos, sino con tu propia comprensión de ti mismo.

Te haré preguntas. No busco respuestas correctas, pues no las hay. Busco la verdad de tu esencia, pues de ella brotará el mundo que merecerás enfrentar..."

*Una pausa cargada de expectación llena el aire*"""
        ]
        
        message = random.choice(awakening_messages)
        self.current_phase = NarrativePhase.QUESTIONING
        return message
    
    def get_next_question(self) -> Optional[str]:
        """Obtiene la siguiente pregunta en la secuencia de 3"""
        if self.questions_asked >= 3:
            return None
        
        # Seleccionar categoría para cada pregunta
        categories = list(self.question_bank.keys())
        category = categories[self.questions_asked]
        
        # Seleccionar pregunta aleatoria de la categoría
        questions = self.question_bank[category]
        question = random.choice(questions)
        
        divine_name = self.divine_personality["name"]
        
        # Envolver la pregunta con narración divina
        question_intro = [
            f"**{divine_name}**: \"",
            f"*La voz resuena con mayor intensidad*\n\n**{divine_name}**: \"",
            f"*Una pausa thoughtful antes de continuar*\n\n**{divine_name}**: \""
        ]
        
        intro = random.choice(question_intro)
        
        formatted_question = f"""{intro}{question}\"
        
*Puedes sentir que esta pregunta es importante. Tu respuesta ayudará a moldear el mundo que te espera*"""
        
        self.questions_asked += 1
        return formatted_question
    
    def process_player_response(self, response: str) -> str:
        """Procesa la respuesta del jugador y genera reacción divina"""
        self.player_responses.append(response)
        
        divine_name = self.divine_personality["name"]
        
        # Reacciones variadas basadas en el número de pregunta
        if len(self.player_responses) == 1:
            reactions = [
                f"**{divine_name}**: \"Interesante... veo profundidad en tu respuesta. Hay más que explorar...\"",
                f"**{divine_name}**: \"Tu alma habla con claridad. Esto revela mucho sobre el camino que debes recorrer...\"",
                f"**{divine_name}**: \"Hmm... sí, puedo ver los cimientos de tu carácter formándose...\""
            ]
        elif len(self.player_responses) == 2:
            reactions = [
                f"**{divine_name}**: \"El patrón se vuelve más claro. Tu esencia toma forma ante mis sentidos...\"",
                f"**{divine_name}**: \"Fascinante. Los elementos de tu personalidad comienzan a resonar con dimensiones específicas...\"",
                f"**{divine_name}**: \"Ya veo qué tipo de desafíos serán dignos de ti...\""
            ]
        else:  # Tercera respuesta
            reactions = [
                f"**{divine_name}**: \"Así es como debe ser. Ahora comprendo plenamente quién eres, {self.player_responses[0][:30]}...\"",
                f"**{divine_name}**: \"Perfecto. Las tres facetas de tu ser están claras. Es hora de crear tu mundo...\"",
                f"**{divine_name}**: \"Excelente. Con estas respuestas, puedo tejer una realidad digna de tu espíritu...\""
            ]
        
        reaction = random.choice(reactions)
        
        # Si hemos completado las 3 preguntas, cambiar fase
        if len(self.player_responses) == 3:
            self.current_phase = NarrativePhase.WORLD_CREATION
            self._analyze_responses()
        
        return reaction
    
    def _analyze_responses(self):
        """Analiza las respuestas del jugador para crear el mundo_seed"""
        responses = self.player_responses
        
        # Análisis básico de patrones en las respuestas
        combined_text = " ".join(responses).lower()
        
        # Detectar temas predominantes
        themes = {
            "darkness": ["sombra", "oscuridad", "miedo", "perdida", "soledad", "muerte"],
            "light": ["luz", "esperanza", "amor", "proteger", "salvar", "ayudar"],
            "power": ["poder", "fuerza", "control", "dominar", "liderar", "conquistar"],
            "wisdom": ["sabiduría", "conocimiento", "verdad", "entender", "aprender"],
            "freedom": ["libertad", "elegir", "independencia", "escapar", "libre"],
            "justice": ["justicia", "correcto", "equilibrio", "justo", "moral"]
        }
        
        theme_scores = {}
        for theme, keywords in themes.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            if score > 0:
                theme_scores[theme] = score
        
        # Determinar tema dominante
        dominant_theme = max(theme_scores.items(), key=lambda x: x[1])[0] if theme_scores else "balance"
        
        # Crear semilla del mundo basada en análisis
        self.world_seed = {
            "dominant_theme": dominant_theme,
            "responses": responses,
            "personality_traits": self._extract_personality_traits(combined_text),
            "preferred_challenges": self._determine_challenges(combined_text),
            "world_tone": self._determine_world_tone(dominant_theme)
        }
    
    def _extract_personality_traits(self, text: str) -> List[str]:
        """Extrae rasgos de personalidad del texto"""
        trait_patterns = {
            "valiente": ["enfrentar", "pelear", "luchar", "valor", "coraje"],
            "cauteloso": ["cuidado", "planear", "pensar", "evaluar", "considerar"],
            "altruista": ["otros", "ayudar", "sacrificar", "proteger", "servir"],
            "ambicioso": ["poder", "éxito", "lograr", "conquistar", "superar"],
            "sabio": ["conocimiento", "entender", "verdad", "sabiduría", "aprender"],
            "libre": ["libertad", "independencia", "elegir", "propio", "decidir"]
        }
        
        traits = []
        for trait, keywords in trait_patterns.items():
            if any(keyword in text for keyword in keywords):
                traits.append(trait)
        
        return traits[:3]  # Máximo 3 rasgos principales
    
    def _determine_challenges(self, text: str) -> str:
        """Determina qué tipo de desafíos prefiere el jugador"""
        if any(word in text for word in ["combate", "lucha", "pelear", "batalla"]):
            return "combat_focused"
        elif any(word in text for word in ["misterio", "enigma", "resolver", "descubrir"]):
            return "mystery_focused"
        elif any(word in text for word in ["social", "otros", "gente", "comunidad"]):
            return "social_focused"
        else:
            return "balanced"
    
    def _determine_world_tone(self, theme: str) -> str:
        """Determina el tono general del mundo"""
        tone_mapping = {
            "darkness": "grimdark",
            "light": "hopeful",
            "power": "epic",
            "wisdom": "mystical",
            "freedom": "adventure",
            "justice": "heroic",
            "balance": "balanced"
        }
        return tone_mapping.get(theme, "balanced")
    
    def generate_world_creation_narrative(self, character: Character) -> str:
        """Genera la narrativa de creación del mundo basada en las respuestas"""
        if self.current_phase != NarrativePhase.WORLD_CREATION:
            return "Error: No se han completado las preguntas necesarias."
        
        divine_name = self.divine_personality["name"]
        theme = self.world_seed["dominant_theme"]
        tone = self.world_seed["world_tone"]
        traits = self.world_seed["personality_traits"]
        
        # Crear narrativa personalizada basada en el análisis
        creation_narrative = f"""*El espacio a tu alrededor comienza a transformarse. La voz divina resuena con poder creativo*

**{divine_name}**: "Has hablado, y yo he escuchado, {character.name}. En tus palabras he visto el reflejo de tu alma: {', '.join(traits) if traits else 'un espíritu complejo y único'}.

*La realidad comienza a tomar forma alrededor tuyo*

Tu esencia resuena con fuerzas {self._get_theme_description(theme)}. Por ello, el mundo que habitarás será uno donde estas fuerzas tengan significado...

*El vacío blanco se disuelve, revelando...*"""
        
        # Descripción del mundo específica según el tema
        world_descriptions = {
            "darkness": """
Una vasta extensión de tierras crepusculares donde las sombras tienen vida propia. Aquí, las pruebas más duras forjan a los héroes más brillantes. Bosques de árboles negros se alzan bajo cielos de tormenta perpetua, pero en la distancia, torres de cristal emiten una luz desafiante contra la oscuridad.

En este reino, cada victoria contra las tinieblas es más valiosa que mil triunfos fáciles.""",
            
            "light": """
Un reino resplandeciente donde la esperanza toma forma física. Campos dorados se extienden hasta el horizonte, salpicados de ciudades de mármol blanco donde la gente vive en armonía. Pero incluso aquí, dragones antiguos duermen en montañas distantes, esperando que héroes valientes demuestren que la luz puede prevalecer.

Este es un mundo donde tus actos nobles resonarán a través de las eras.""",
            
            "power": """
Un mundo de contrastes épicos donde titanes de piedra caminan por valles profundos y ciudades flotantes desafían la gravedad. Aquí, el poder se gana a través de hazañas legendarias. Volcanes escupen oro líquido mientras dragones soberanos vigilan desde sus fortalezas en las nubes.

En este reino, solo aquellos con verdadera determinación pueden reclamar su destino.""",
            
            "wisdom": """
Un plano místico donde el conocimiento tiene poder físico. Bibliotecas infinitas flotan en el vacío, conectadas por puentes de luz solidificada. Aquí, cada secreto descubierto otorga nueva fuerza, y los sabios más ancianos pueden remodelar la realidad con una palabra bien elegida.

Este es un mundo donde la comprensión es la mayor arma.""",
            
            "freedom": """
Un mundo sin fronteras donde continentes flotantes navegan por cielos infinitos. Aquí, cada soul puede forjar su propio camino. Ciudades nómadas de aventureros cruzan océanos de nubes mientras exploradores valientes descubren nuevas islas que aparecen con cada amanecer.

En este reino, tu voluntad es la única ley que importa.""",
            
            "justice": """
Un mundo en equilibrio precario entre orden y caos. Ciudades resplandecientes de justicia contrastan con tierras salvajes donde la ley del más fuerte prevalece. Aquí, héroes verdaderos surgen para inclinar la balanza hacia la luz, enfrentando tiranos y protegiendo a los inocentes.

Este es un reino donde tus elecciones morales tienen consecuencias reales."""
        }
        
        world_desc = world_descriptions.get(theme, world_descriptions["balance"] if "balance" in world_descriptions else """
Un mundo de equilibrio perfecto donde todas las fuerzas coexisten. Aquí encontrarás desafíos variados que pondrán a prueba cada aspecto de tu carácter, desde tu valor en combate hasta tu sabiduría en la diplomacia.

Este es un reino donde puedes convertirte en cualquier tipo de héroe que elijas ser.""")
        
        full_narrative = creation_narrative + "\n\n" + world_desc + f"""

*La transformación se completa. Te encuentras de pie en este nuevo mundo, sintiendo cómo sus energías resuenan con las profundidades de tu ser*

**{divine_name}**: "Ahora comienza tu verdadero viaje, {character.name}. Este mundo ha sido moldeado por tu esencia. Lo que hagas aquí, cómo crezcas, qué elijas ser... eso depende únicamente de ti.

Yo observaré. Yo narraré. Pero el destino... el destino es tuyo para escribir."

*Con estas palabras, sientes que una nueva fase de tu existencia ha comenzado*"""
        
        self.current_phase = NarrativePhase.ACTIVE_PLAY
        return full_narrative
    
    def _get_theme_description(self, theme: str) -> str:
        """Obtiene descripción poética del tema"""
        descriptions = {
            "darkness": "de sombra y redención",
            "light": "de esperanza y pureza",
            "power": "de ambición y grandeza",
            "wisdom": "de conocimiento y misterio",
            "freedom": "de aventura y autodeterminación",
            "justice": "de honor y rectitud",
            "balance": "de equilibrio y armonía"
        }
        return descriptions.get(theme, "de complejidad y matiz")
    
    def get_enhanced_narrative_context(self) -> Dict[str, Any]:
        """Obtiene contexto para mejorar la narrativa futura"""
        if self.current_phase != NarrativePhase.ACTIVE_PLAY:
            return {}
        
        return {
            "world_seed": self.world_seed,
            "divine_personality": self.divine_personality,
            "theme": self.world_seed.get("dominant_theme", "balance"),
            "tone": self.world_seed.get("world_tone", "balanced"),
            "traits": self.world_seed.get("personality_traits", []),
            "challenge_preference": self.world_seed.get("preferred_challenges", "balanced")
        }
    
    def is_questioning_complete(self) -> bool:
        """Verifica si el proceso de preguntas está completo"""
        return self.questions_asked >= 3 and len(self.player_responses) >= 3
    
    def get_current_phase(self) -> NarrativePhase:
        """Obtiene la fase actual del proceso narrativo"""
        return self.current_phase
    
    def reset(self):
        """Reinicia el proceso narrativo para un nuevo personaje"""
        self.current_phase = NarrativePhase.AWAKENING
        self.questions_asked = 0
        self.player_responses = []
        self.world_seed = {}
        self.divine_personality = self._generate_divine_personality()