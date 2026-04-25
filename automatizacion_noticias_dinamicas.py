#!/usr/bin/env python3
"""
Automatización de Noticias Dinámicas
Obtiene noticias de NewsAPI y genera imágenes para redes sociales
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Configuración
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
OUTPUT_DIR = Path('posts')
URLS_FILE = Path('urls_noticias.json')

def obtener_noticias():
      """Obtiene noticias de NewsAPI"""
      try:
                url = f"https://newsapi.org/v2/top-headlines?country=es&pageSize=5&apiKey={NEWSAPI_KEY}"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                return response.json().get('articles', [])
except Exception as e:
        print(f"Error obteniendo noticias: {e}")
        return []

def generar_imagen_noticia(titulo, descripcion, indice):
      """Genera una imagen con la noticia"""
      width, height = 1200, 630
      bg_color = (13, 13, 47)
      text_color = (255, 255, 255)

    # Crear imagen
      img = Image.new('RGB', (width, height), color=bg_color)
      draw = ImageDraw.Draw(img)

    # Intentar usar una fuente mejor, si no está disponible usar la predeterminada
      try:
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
                text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
            except:
        title_font = ImageFont.load_default()
                      text_font = ImageFont.load_default()

                  # Escribir título
                  titulo_truncado = titulo[:100] if len(titulo) > 100 else titulo
                  draw.multiline_text((50, 100), titulo_truncado, fill=text_color, font=title_font)

                  # Escribir descripción
                  desc_truncado = descripcion[:150] if len(descripcion) > 150 else descripcion
                  draw.multiline_text((50, 300), desc_truncado, fill=text_color, font=text_font)

                  # Guardar imagen
                  output_path = OUTPUT_DIR / f"noticia_{indice}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                  img.save(output_path)
                  return str(output_path)

              def guardar_urls_noticias(noticias, imagenes):
                    """Guarda las URLs de noticias en formato JSON"""
                    urls_data = {
                        "noticias": [
                            {
                                "titulo": n.get('title', ''),
                                "descripcion": n.get('description', ''),
                                "url": n.get('url', ''),
                                "imagen_url": img,
                                "post": f"{n.get('title', '')} - {n.get('description', '')}"
                            }
                            for n, img in zip(noticias, imagenes)
                        ],
                        "fecha_generacion": datetime.now().isoformat()
                    }

    with open(URLS_FILE, 'w', encoding='utf-8') as f:
              json.dump(urls_data, f, ensure_ascii=False, indent=2)

    print(f"URLs guardadas en {URLS_FILE}")

def main():
      """Función principal"""
      print("Iniciando automatización de noticias...")

    # Crear directorio de salida
      OUTPUT_DIR.mkdir(exist_ok=True)

    # Obtener noticias
      noticias = obtener_noticias()
      if not noticias:
                print("No se obtuvieron noticias")
                return

      print(f"Se obtuvieron {len(noticias)} noticias")

    # Generar imágenes
      imagenes = []
      for indice, noticia in enumerate(noticias[:5], 1):
                print(f"Generando imagen para noticia {indice}...")
                imagen_path = generar_imagen_noticia(
                    noticia.get('title', ''),
                    noticia.get('description', ''),
                    indice
                )
                imagenes.append(imagen_path)

      # Guardar URLs
      guardar_urls_noticias(noticias[:len(imagenes)], imagenes)

    print("✅ Automatización completada exitosamente")

if __name__ == '__main__':
      main()
