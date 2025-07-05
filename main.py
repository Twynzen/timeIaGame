#!/usr/bin/env python3
"""
Habitación del Tiempo RPG - Main Entry Point
Sistema de RPG con IA - Arquitectura modular v0.2.0
"""

import sys
import os
import logging
from tkinter import messagebox

# Añadir el directorio src al path para importaciones
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.ui.main_window import GameMainWindow
    from src.config.game_config import GameConfig
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all dependencies are installed and the src/ directory is present")
    sys.exit(1)


def setup_logging(config: GameConfig):
    """Configura el sistema de logging"""
    debug_config = config.get_debug_config()
    
    if debug_config["enable_logging"]:
        logging.basicConfig(
            level=getattr(logging, debug_config["log_level"]),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(debug_config["log_file"]),
                logging.StreamHandler()
            ]
        )
        
        # Crear logger para el juego
        logger = logging.getLogger("timeIaGame")
        logger.info("Sistema de logging inicializado")
        return logger
    
    return None


def check_dependencies():
    """Verifica que las dependencias necesarias estén instaladas"""
    required_packages = ['tkinter']
    optional_packages = ['openai', 'dotenv']
    
    missing_required = []
    missing_optional = []
    
    # Verificar tkinter (viene con Python pero puede fallar en algunas distribuciones)
    try:
        import tkinter
    except ImportError:
        missing_required.append('tkinter')
    
    # Verificar paquetes opcionales
    for package in optional_packages:
        try:
            __import__(package)
        except ImportError:
            missing_optional.append(package)
    
    if missing_required:
        error_msg = f"Error: Missing required packages: {', '.join(missing_required)}\n"
        error_msg += "Please install them using your system package manager."
        print(error_msg)
        return False
    
    if missing_optional:
        warning_msg = f"Warning: Missing optional packages: {', '.join(missing_optional)}\n"
        warning_msg += "Some features (like AI narration) may not be available.\n"
        warning_msg += "Install them with: pip install " + " ".join(missing_optional)
        print(warning_msg)
    
    return True


def check_configuration(config: GameConfig):
    """Verifica la configuración del juego"""
    logger = logging.getLogger("timeIaGame")
    
    # Verificar configuración de IA
    if not config.is_ai_enabled():
        warning_msg = "No se encontró OPENAI_API_KEY. El juego funcionará sin IA avanzada."
        if logger:
            logger.warning(warning_msg)
        print(f"Warning: {warning_msg}")
    
    # Verificar directorio de guardado
    save_config = config.get_save_config()
    save_dir = save_config["save_directory"]
    
    if not os.path.exists(save_dir):
        try:
            os.makedirs(save_dir)
            if logger:
                logger.info(f"Directorio de guardado creado: {save_dir}")
        except Exception as e:
            error_msg = f"No se pudo crear el directorio de guardado: {e}"
            if logger:
                logger.error(error_msg)
            print(f"Error: {error_msg}")
            return False
    
    return True


def main():
    """Función principal del juego"""
    print("Iniciando Habitación del Tiempo RPG v0.2.0...")
    
    # Verificar dependencias
    if not check_dependencies():
        input("Presiona Enter para salir...")
        return 1
    
    try:
        # Cargar configuración
        config = GameConfig()
        
        # Configurar logging
        logger = setup_logging(config)
        
        if logger:
            logger.info("Iniciando Habitación del Tiempo RPG v0.2.0")
        
        # Verificar configuración
        if not check_configuration(config):
            if logger:
                logger.error("Error en la configuración del juego")
            input("Presiona Enter para salir...")
            return 1
        
        # Inicializar y ejecutar la aplicación
        if logger:
            logger.info("Inicializando interfaz gráfica...")
        
        app = GameMainWindow()
        
        if logger:
            logger.info("Juego iniciado correctamente")
        
        # Ejecutar el loop principal
        app.mainloop()
        
        if logger:
            logger.info("Juego finalizado")
        
        return 0
        
    except KeyboardInterrupt:
        print("\nJuego interrumpido por el usuario")
        return 0
        
    except Exception as e:
        error_msg = f"Error fatal al iniciar el juego: {str(e)}"
        print(error_msg)
        
        # Intentar mostrar diálogo de error si tkinter está disponible
        try:
            messagebox.showerror("Error Fatal", error_msg)
        except:
            pass  # Si no se puede mostrar el diálogo, continuar
        
        # Log del error si está disponible
        logger = logging.getLogger("timeIaGame")
        if logger:
            logger.exception("Error fatal en main()")
        
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)