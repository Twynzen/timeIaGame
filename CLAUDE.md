# Habitación del Tiempo - RPG Game

## Descripción del Proyecto
Un juego de rol (RPG) desarrollado en Python con interfaz gráfica Tkinter que simula una "Habitación del Tiempo" donde los jugadores entrenan para volverse más fuertes. El juego integra IA (OpenAI GPT-4) para generar narrativa dinámica.

## Estructura del Proyecto
```
timeIaGame/
├── timeIagame.py           # Archivo principal del juego
├── save_garret.json        # Archivo de guardado de ejemplo
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

### Ejecutar el juego
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