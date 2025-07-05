"""
Image Generator - DALL-E integration for visual storytelling
"""

import os
import base64
import hashlib
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import logging

try:
    import openai
    from PIL import Image, ImageTk
    import requests
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False


class ImageGenerator:
    """Generador de imágenes usando DALL-E para narrativa visual"""
    
    def __init__(self, api_key: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger("ImageGenerator")
        
        # Configuración por defecto
        default_config = {
            "dalle_model": "dall-e-3",
            "image_size": "1024x1024",
            "image_cache_dir": "generated_images",
            "enable_image_generation": True
        }
        
        self.config = {**default_config, **(config or {})}
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        # Verificar dependencias y disponibilidad
        self.enabled = (
            DEPENDENCIES_AVAILABLE and 
            self.api_key and 
            self.config["enable_image_generation"]
        )
        
        if self.enabled:
            try:
                self.client = openai.OpenAI(api_key=self.api_key)
                self._ensure_cache_directory()
                self.logger.info("ImageGenerator inicializado correctamente")
            except Exception as e:
                self.logger.error(f"Error inicializando OpenAI client: {e}")
                self.enabled = False
        else:
            self.client = None
            self.logger.warning("ImageGenerator deshabilitado: dependencias o API key no disponibles")
    
    def _ensure_cache_directory(self):
        """Asegura que existe el directorio de caché de imágenes"""
        cache_dir = self.config["image_cache_dir"]
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            self.logger.info(f"Directorio de caché creado: {cache_dir}")
    
    def _get_cache_path(self, prompt: str) -> str:
        """Genera una ruta de caché basada en el hash del prompt"""
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        filename = f"scene_{prompt_hash}.png"
        return os.path.join(self.config["image_cache_dir"], filename)
    
    def _download_image(self, url: str, filepath: str) -> bool:
        """Descarga una imagen desde URL y la guarda"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            self.logger.info(f"Imagen descargada: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Error descargando imagen: {e}")
            return False
    
    def generate_scene_image(self, location_description: str, character_context: str = "") -> Optional[str]:
        """
        Genera una imagen de un escenario/lugar basada en la descripción
        
        Args:
            location_description: Descripción del lugar/escenario
            character_context: Contexto del personaje (opcional)
        
        Returns:
            Ruta del archivo de imagen generada o None si falla
        """
        if not self.enabled:
            self.logger.warning("Generación de imágenes deshabilitada")
            return None
        
        # Crear prompt optimizado para escenarios
        scene_prompt = self._create_scene_prompt(location_description, character_context)
        
        # Verificar caché
        cache_path = self._get_cache_path(scene_prompt)
        if os.path.exists(cache_path):
            self.logger.info(f"Imagen encontrada en caché: {cache_path}")
            return cache_path
        
        try:
            self.logger.info(f"Generando imagen para: {location_description[:50]}...")
            
            # Llamar a DALL-E
            response = self.client.images.generate(
                model=self.config["dalle_model"],
                prompt=scene_prompt,
                size=self.config["image_size"],
                quality="standard",
                n=1
            )
            
            # Obtener URL de la imagen
            image_url = response.data[0].url
            
            # Descargar y guardar
            if self._download_image(image_url, cache_path):
                return cache_path
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error generando imagen: {e}")
            return None
    
    def _create_scene_prompt(self, location_description: str, character_context: str = "") -> str:
        """
        Crea un prompt optimizado para DALL-E basado en la descripción del lugar
        """
        # Prompt base optimizado para escenarios de fantasía
        base_prompt = f"""
        Una vista cinematográfica de un escenario de fantasía épica: {location_description}.
        
        Estilo: Arte conceptual digital de alta calidad, similar a videojuegos AAA de fantasía.
        Composición: Vista panorámica que muestre la grandeza y atmósfera del lugar.
        Iluminación: Dramática y evocativa, que realce el mood del escenario.
        Colores: Paleta rica y vibrante que transmita la magia del lugar.
        Detalles: Incluir elementos que sugieran la presencia de vida y actividad.
        
        El escenario debe verse como un lugar donde un aventurero podría explorar y vivir épicas aventuras.
        """
        
        # Añadir contexto del personaje si está disponible
        if character_context:
            base_prompt += f"\n\nContexto del aventurero: {character_context}"
        
        # Añadir restricciones técnicas
        base_prompt += """
        
        Restricciones técnicas:
        - Sin texto visible en la imagen
        - Evitar personajes prominentes en primer plano
        - Enfocar en el ambiente y la atmósfera del lugar
        - Calidad fotorrealista pero con toque fantástico
        """
        
        return base_prompt.strip()
    
    def load_image_for_display(self, image_path: str, max_size: Tuple[int, int] = (400, 300)) -> Optional[ImageTk.PhotoImage]:
        """
        Carga una imagen y la prepara para mostrar en Tkinter
        
        Args:
            image_path: Ruta de la imagen
            max_size: Tamaño máximo (ancho, alto)
        
        Returns:
            ImageTk.PhotoImage para usar en Tkinter o None si falla
        """
        if not DEPENDENCIES_AVAILABLE or not os.path.exists(image_path):
            return None
        
        try:
            # Cargar y redimensionar imagen
            image = Image.open(image_path)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convertir para Tkinter
            tk_image = ImageTk.PhotoImage(image)
            
            self.logger.info(f"Imagen cargada para display: {image_path}")
            return tk_image
            
        except Exception as e:
            self.logger.error(f"Error cargando imagen para display: {e}")
            return None
    
    def get_cached_images(self) -> list:
        """Obtiene lista de imágenes en caché"""
        cache_dir = self.config["image_cache_dir"]
        if not os.path.exists(cache_dir):
            return []
        
        images = []
        for filename in os.listdir(cache_dir):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                filepath = os.path.join(cache_dir, filename)
                stat = os.stat(filepath)
                images.append({
                    'filename': filename,
                    'filepath': filepath,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime)
                })
        
        return sorted(images, key=lambda x: x['modified'], reverse=True)
    
    def clear_cache(self, max_files: int = 50) -> int:
        """
        Limpia el caché manteniendo solo las imágenes más recientes
        
        Args:
            max_files: Número máximo de archivos a mantener
        
        Returns:
            Número de archivos eliminados
        """
        images = self.get_cached_images()
        
        if len(images) <= max_files:
            return 0
        
        # Eliminar imágenes más antiguas
        to_delete = images[max_files:]
        deleted_count = 0
        
        for image_info in to_delete:
            try:
                os.remove(image_info['filepath'])
                deleted_count += 1
            except Exception as e:
                self.logger.error(f"Error eliminando {image_info['filename']}: {e}")
        
        self.logger.info(f"Caché limpiado: {deleted_count} archivos eliminados")
        return deleted_count
    
    def is_available(self) -> bool:
        """Verifica si el generador de imágenes está disponible"""
        return self.enabled
    
    def get_status_info(self) -> Dict[str, Any]:
        """Obtiene información del estado del generador"""
        cached_images = self.get_cached_images()
        
        return {
            "enabled": self.enabled,
            "dependencies_available": DEPENDENCIES_AVAILABLE,
            "api_configured": bool(self.api_key),
            "cache_directory": self.config["image_cache_dir"],
            "cached_images_count": len(cached_images),
            "dalle_model": self.config["dalle_model"],
            "image_size": self.config["image_size"]
        }