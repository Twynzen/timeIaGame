# Habitación del Tiempo - RPG Game

## Descripción del Proyecto
Un juego de rol (RPG) desarrollado en Python con interfaz gráfica Tkinter que simula una "Habitación del Tiempo" donde los jugadores entrenan para volverse más fuertes. El juego integra IA (OpenAI GPT-4) para generar narrativa dinámica.

**Versión Actual**: v0.2.0 - Arquitectura Modular Refactorizada

## Estructura del Proyecto
```
timeIaGame/
├── main.py                 # Punto de entrada principal (NUEVO)
├── timeIagame.py          # Archivo original (legacy, mantener para referencia)
├── save_garret.json       # Archivo de guardado de ejemplo
├── src/                   # Arquitectura modular (NUEVO)
│   ├── __init__.py
│   ├── config/            # Configuración centralizada
│   │   ├── __init__.py
│   │   └── game_config.py
│   ├── core/              # Sistemas centrales del juego
│   │   ├── __init__.py
│   │   ├── character.py   # Sistema de personajes
│   │   ├── dice_system.py # Sistema de dados
│   │   ├── combat_system.py # Sistema de combate
│   │   └── game_state.py  # Gestión de estado con patrón Observer
│   ├── entities/          # Entidades del juego
│   │   ├── __init__.py
│   │   └── enemy.py       # Sistema de enemigos
│   ├── ai/                # Sistemas de inteligencia artificial
│   │   ├── __init__.py
│   │   ├── game_master.py # Game Master con IA
│   │   └── narrative_manager.py # Gestión narrativa avanzada
│   ├── ui/                # Interfaz de usuario
│   │   ├── __init__.py
│   │   ├── main_window.py # Ventana principal
│   │   └── character_creation.py # Creación de personajes
│   └── data/              # Persistencia y datos
│       ├── __init__.py
│       └── persistence.py # Sistema de guardado/carga
├── documentacion_de_crecimiento/
│   ├── Manual MVP v1.2.txt
│   └── manualtecnicomcppython.txt
└── CLAUDE.md              # Este archivo
```

## Componentes Principales

### 1. Sistema de Personajes (Character)
- **Razas**: Humano, Elfo, Enano, Orco
- **Clases**: Guerrero, Mago, Arquero, Asesino
- **Atributos**: Fuerza, Destreza, Constitución, Inteligencia, Sabiduría, Carisma
- **Estadísticas**: HP, Maná, Ataque, Defensa, Experiencia, Oro

### 2. Sistema de Combate (CombatSystem)
- Sistema de dados personalizado
- Combate por turnos
- Tiradas de ataque vs defensa
- Diferentes tipos de enemigos con CR (Challenge Rating)

### 3. Sistema de IA (AIGameMaster)
- Integración con OpenAI GPT-4
- Generación de narrativa dinámica
- Contexto del mundo persistente
- Determinación de encuentros

### 4. Interfaz Gráfica (GameUI)
- Tkinter con estilo personalizado
- Panel de personaje con barras de progreso
- Área de narración con scroll
- Botones de acción rápida
- Sistema de menús

## Dependencias
```python
# Librerías estándar
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Canvas, Frame
import json
import random
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import re
from dataclasses import dataclass, asdict

# Dependencias externas
import openai
from dotenv import load_dotenv
```

## Configuración Requerida
- **OPENAI_API_KEY**: Token de API de OpenAI (requerido en archivo .env)
- **Modelo**: Usa GPT-4o-mini para la narrativa

## Funcionalidades Principales

### Creación de Personaje
- Diálogo interactivo con selección de raza/clase
- Distribución de 24 puntos de atributo
- Cálculo automático de bonificaciones

### Sistema de Combate
- Enemigos: Lobo Sombrío, Goblin Salvaje, Orco Berserker, Espectro Errante
- Tiradas de dados automáticas
- Recompensas por victoria (EXP y oro)
- Sistema de muerte/revivir

### Exploración
- Narrativa generada por IA
- Encuentros aleatorios basados en palabras clave
- Sistema de percepción
- Diferentes zonas de la Habitación del Tiempo

### Persistencia
- Guardado/carga de partidas en JSON
- Historial de conversación con IA
- Estado del mundo persistente

## Comandos de Desarrollo

### Ejecutar el juego (Versión Modular v0.2.0)
```bash
python main.py
```

### Ejecutar versión legacy (Solo para referencia)
```bash
python timeIagame.py
```

### Requisitos previos
```bash
pip install openai python-dotenv
```

### Archivo .env requerido
```
OPENAI_API_KEY=tu_clave_api_aqui
```

## Arquitectura Modular v0.2.0

### Beneficios del Refactor
- **Separación de responsabilidades**: Cada módulo tiene una función específica
- **Mantenibilidad mejorada**: Código más fácil de entender y modificar
- **Escalabilidad**: Estructura preparada para futuras expansiones
- **Patrón Observer**: Comunicación desacoplada entre componentes
- **Configuración centralizada**: Gestión unificada de settings
- **Mejor testing**: Componentes aislados permiten testing unitario

### Nuevas Características
- **GameStateManager**: Gestión centralizada del estado con eventos
- **NarrativeManager**: Sistema avanzado de tracking narrativo
- **GameConfig**: Configuración centralizada y modificable
- **SaveManager**: Sistema robusto de persistencia
- **Logging integrado**: Sistema de logs para debugging
- **Fallback de IA**: Narrativa offline cuando no hay API
- **Validación de dependencias**: Verificación automática al inicio

### Migración desde v0.1.0
El juego v0.2.0 es **completamente compatible** con partidas guardadas de la versión anterior. Simplemente ejecuta `python main.py` en lugar de `python timeIagame.py`.

## Mecánicas del Juego

### Sistema de Dados
- Formato: XdY+Z (ejemplo: 1d20+5)
- Tiradas d100 con bonificaciones de atributos
- Rangos de éxito: 50+ (básico), 70+ (bueno), 90+ (crítico)

### Progresión
- Experiencia requerida aumenta 1.5x por nivel
- Subida de nivel mejora HP (+20), Maná (+5), Fortaleza (+2), Resistencia (+2)
- Sistema de muertes/asesinatos rastreado

### Atributos y Bonificaciones
- Valores 1-10, bonificaciones de 0 a +35
- Escala: 6-7 (+15), 8 (+25), 9 (+30), 10+ (+35)

## Notas Técnicas
- El juego usa un sistema de canvas con scroll para manejar contenido largo
- La IA mantiene contexto de las últimas 10 interacciones
- Los archivos de guardado incluyen timestamp y estado completo del juego
- La interfaz usa un esquema de colores oscuro (#1a1a1a, #2a2a2a, #3a3a3a)