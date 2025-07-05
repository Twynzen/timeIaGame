# Plan de Desarrollo - Habitación del Tiempo RPG

## Análisis del Estado Actual vs Manual MVP

### Estado Actual del Proyecto
El proyecto actual implementa un sistema RPG básico con:
- **Sistema de personajes**: 4 razas, 4 clases, atributos básicos
- **Sistema de combate**: Dados simples, 4 enemigos
- **IA narrativa**: Integración básica con OpenAI GPT-4o-mini
- **Interfaz**: Tkinter GUI completa con paneles de personaje
- **Persistencia**: Guardado/carga JSON

### Sistemas Faltantes del Manual MVP

Basado en el análisis del Manual MVP v1.2, el proyecto necesita implementar:

## 1. SISTEMA DE ATRIBUTOS Y STATS (Sección 2)

### ❌ Faltantes Críticos:
- **Sistema de 10 puntos de mejora por nivel**: Actualmente no implementado
- **Stats mejorables separados**: Vitalidad, Ataque, Defensa, Ataque Mágico, Defensa Mágica, Fortaleza, Resistencia, Maná
- **Costos específicos**: Cada stat tiene costos diferentes
- **Ascensión de nivel**: 30 puntos extra cada 10 niveles
- **Sistema de dados progresivo**: 1dY con conversión a XdY cuando Y > 999
- **Stat especial Apoyo/Curación (DS)**: Para clases específicas

### ✅ Implementado Parcialmente:
- Atributos base (6 atributos) ✅
- Bonos por atributo ✅ (pero valores diferentes al manual)
- Sistema de niveles básico ✅

## 2. RAZAS Y CLASES (Sección 3)

### ❌ Razas Faltantes:
- **Dragonesborn** (solo por sorteo)
- **Tieflings**
- **Genasi** (4 subtipos: Fuego, Agua, Aire, Tierra)
- **Aasimar**
- **Kalashtar**
- **Demonios**
- **Ángeles**
- **Thyria**

### ❌ Clases Faltantes:
- **Paladín**
- **Clérigo**
- **Bárbaro**
- **Artista Marcial**
- **Nigromante**
- **Bardo**
- **Ladrón** (vs Asesino actual)

### ❌ Sistema de Buffs/Debuffs:
- Multiplicadores por equipamiento
- Sistema de especialización por armas/armaduras

## 3. SISTEMA DE VOCACIONES (Sección 4)

### ❌ Completamente Faltante:
- **Conjurador/Invocador de Entidades**
- Prerequisitos de atributos
- Habilidades especiales de vocación
- Sistema de especialización adicional

## 4. SISTEMAS ADICIONALES IDENTIFICADOS

### Sistema de Magia y Hechizos
- Tipos de hechizos: Benditos, Malditos, Ofensivos, Defensivos
- Sistema de componentes mágicos
- Escuelas de magia

### Sistema de Equipamiento
- **Armas**: Espadas, Hachas, Lanzas, Arcos, Dagas, etc.
- **Armaduras**: Liviana, Mediana, Pesada
- **Escudos**: Liviano, Mediano, Grande
- **Sistema de calidad y rareza**

### Sistema de Combate Avanzado
- **Multiplicadores de clase**
- **Sistema de críticos**
- **Estados y efectos**
- **Combate por turnos estructurado**

## PLAN ALGORÍTMICO DE IMPLEMENTACIÓN

### FASE 1: REFACTORIZACIÓN DEL CORE
**Prioridad: CRÍTICA**

#### 1.1 Rediseño del Sistema de Stats
```python
# Implementar sistema de stats mejorables
class StatsMejorables:
    def __init__(self):
        self.vitalidad = 0  # +180 HP por punto
        self.ataque = 0     # +12 al dado por punto  
        self.defensa = 0    # +12 al dado por punto
        self.ataque_magico = 0   # +3 al dado por punto
        self.defensa_magica = 0  # +3 al dado por punto
        self.fortaleza = 0       # +3 bono fijo por punto
        self.resistencia = 0     # +3 bono fijo por punto
        self.mana = 0            # +3 maná por punto
        self.apoyo_curacion = 0  # Especial, +20 al dado

class Character:
    def level_up(self):
        self.improvement_points += 10
        if self.level % 10 == 0:  # Cada 10 niveles
            self.improvement_points += 30
```

#### 1.2 Sistema de Dados Progresivo
```python
class DiceSystem:
    def calculate_dice_progression(self, base_value: int) -> str:
        if base_value <= 999:
            return f"1d{base_value}"
        else:
            dice_count = math.ceil(base_value / 999)
            dice_count = min(dice_count, 20)  # Max 20 dados
            return f"{dice_count}d999"
```

### FASE 2: EXPANSIÓN DE RAZAS Y CLASES
**Prioridad: ALTA**

#### 2.1 Implementación de Razas Faltantes
```python
# Añadir al diccionario RACES
"Dragonesborn": {
    "stats": CharacterStats(vitalidad=400, mana=8, ataque=40, defensa=32, 
                          ataque_magico=30, defensa_magica=24),
    "attr_bonus": {"fuerza": 2, "carisma": 1},
    "weakness": "Sensibles a la Magia Caótica",
    "special": "solo_sorteo"
}
```

#### 2.2 Sistema de Buffs/Debuffs por Clase
```python
class ClassModifiers:
    def apply_equipment_modifier(self, character: Character, equipment: str) -> float:
        class_data = character.CLASSES[character.char_class]
        if equipment in class_data["buff_weapons"]:
            return class_data["buff_mult"]
        else:
            return class_data["desbuff_mult"]
```

### FASE 3: SISTEMA DE VOCACIONES
**Prioridad: MEDIA**

#### 3.1 Base de Vocaciones
```python
class Vocation:
    def __init__(self, name: str, primary_attribute: str, prerequisite_value: int):
        self.name = name
        self.primary_attribute = primary_attribute
        self.prerequisite_value = prerequisite_value
        self.abilities = []

class ConjuradorVocation(Vocation):
    def __init__(self):
        super().__init__("Conjurador", "inteligencia", 6)
        self.summons = []
        self.summon_slots = 1
```

### FASE 4: SISTEMA DE EQUIPAMIENTO
**Prioridad: MEDIA**

#### 4.1 Base de Equipamiento
```python
class Equipment:
    def __init__(self, name: str, category: str, weight: str, rarity: str):
        self.name = name
        self.category = category  # "arma", "armadura", "escudo"
        self.weight = weight      # "liviana", "mediana", "pesada"
        self.rarity = rarity
        self.modifiers = {}

class WeaponSystem:
    WEAPONS = {
        "Espada": {"damage": "1d10", "weight": "mediana", "type": "cuerpo_a_cuerpo"},
        "Arco": {"damage": "1d8", "weight": "liviana", "type": "distancia"},
        # etc...
    }
```

### FASE 5: SISTEMA DE MAGIA
**Prioridad: BAJA**

#### 5.1 Escuelas de Magia
```python
class SpellSystem:
    SPELL_SCHOOLS = {
        "Benditos": {"modifier": 1.0, "mana_cost_mult": 1.0},
        "Malditos": {"modifier": 1.0, "mana_cost_mult": 1.2},
        "Ofensivos": {"modifier": 1.1, "mana_cost_mult": 1.0},
        "Defensivos": {"modifier": 0.9, "mana_cost_mult": 0.8}
    }
```

### FASE 6: INTEGRACIÓN TÉCNICA OPENAI
**Prioridad: BAJA**

#### 6.1 Implementar Recomendaciones del Manual Técnico
```python
# Mejorar gestión de tokens
import tiktoken

def count_tokens(messages: list, model: str = "gpt-4o-mini") -> int:
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = 0
    for message in messages:
        num_tokens += len(encoding.encode(message["content"]))
    return num_tokens

# Gestión de costos
class CostManager:
    def __init__(self):
        self.daily_budget = 5.0  # $5 USD diario
        self.current_cost = 0.0
    
    def can_make_request(self, estimated_tokens: int) -> bool:
        estimated_cost = (estimated_tokens / 1000) * 0.00015  # gpt-4o-mini
        return (self.current_cost + estimated_cost) <= self.daily_budget
```

## CRONOGRAMA DE IMPLEMENTACIÓN

### Sprint 1 (2-3 días): Core System Refactor
- [ ] Refactorizar sistema de stats mejorables
- [ ] Implementar puntos de mejora por nivel
- [ ] Sistema de dados progresivo
- [ ] Actualizar sistema de subida de nivel

### Sprint 2 (3-4 días): Razas y Clases
- [ ] Implementar 8 razas faltantes
- [ ] Implementar 7 clases faltantes  
- [ ] Sistema de buffs/debuffs por equipamiento
- [ ] Balanceo inicial

### Sprint 3 (2-3 días): Sistema de Vocaciones
- [ ] Base del sistema de vocaciones
- [ ] Implementar Conjurador como prototipo
- [ ] Prerequisites y validaciones

### Sprint 4 (3-4 días): Sistema de Equipamiento
- [ ] Base de datos de armas/armaduras
- [ ] Sistema de rareza y calidad
- [ ] Integración con modificadores de clase

### Sprint 5 (2-3 días): Sistema de Magia
- [ ] Escuelas de magia
- [ ] Hechizos básicos
- [ ] Sistema de componentes

### Sprint 6 (1-2 días): Optimización Técnica
- [ ] Implementar gestión de tokens
- [ ] Sistema de costos
- [ ] Mejoras de rendimiento

## MÉTRICAS DE ÉXITO

### Funcionalidad
- [ ] 100% de razas del manual implementadas
- [ ] 100% de clases del manual implementadas  
- [ ] Sistema de stats conforme al manual
- [ ] Sistema de vocaciones funcional

### Técnico
- [ ] Costo diario de IA < $2 USD
- [ ] Tiempo de respuesta < 3 segundos
- [ ] 0 errores críticos en producción

### Gameplay
- [ ] Balanceo de razas/clases validado
- [ ] Sistema de progresión coherente
- [ ] Experiencia de usuario fluida

## RIESGOS Y MITIGACIONES

### Riesgo: Complejidad del Sistema de Stats
**Mitigación**: Implementar incrementalmente, validar con tests unitarios

### Riesgo: Balanceo de Gameplay  
**Mitigación**: Implementar sistema de configuración fácil para ajustes

### Riesgo: Costos de IA
**Mitigación**: Implementar límites estrictos y caché de respuestas

### Riesgo: Rendimiento con Muchas Razas/Clases
**Mitigación**: Optimizar estructura de datos, lazy loading

## CONCLUSIÓN

El proyecto actual tiene una base sólida pero requiere una expansión significativa para cumplir con el Manual MVP. La implementación por fases permite mantener la funcionalidad actual mientras se expanden las características gradualmente.

**Estimación total**: 15-20 días de desarrollo
**Complejidad**: Media-Alta debido a la cantidad de sistemas interconectados
**ROI**: Alto, ya que el resultado será un RPG completo y balanceado conforme a especificaciones