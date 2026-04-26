#!/usr/bin/env python3
"""
SISTEMA DE AUTOMATIZACIÓN DINÁMICA - OFERTAS BESTIALES
Busca noticias en NewsAPI → Genera imágenes dinámicas → Sube a GitHub → Publica en Facebook
Sin templates fijos. Cada noticia = diseño único.
"""

import requests
import json
import os
from datetime import datetime, timedelta
import random
from PIL import Image, ImageDraw, ImageFont
import base64
import hashlib
from io import BytesIO

# ==================== CONFIG ====================
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "creativafactorykdp-cyber/ofertas-bestiales-images"
OWNER = "creativafactorykdp-cyber"
GITHUB_BASE = "https://raw.githubusercontent.com"

# Archivo histórico (relativo al repo en GitHub)
HISTORICO_FILE = "historias_publicadas.txt"

# Dimensiones imagen (Facebook)
IMG_WIDTH = 1200
IMG_HEIGHT = 630

# COLORES MARCA
COLOR_PRIMARY = "#00A651"   # Verde
COLOR_ACCENT = "#FF7F00"    # Naranja
COLOR_BG = "#FFFFFF"
COLOR_TEXT = "#1a1a1a"
COLOR_LIGHT = "#F5F5F5"

# ==================== UTILIDADES ====================

def crear_historico_si_no_existe():
    """Crea archivo histórico si no existe"""
    if not os.path.exists(HISTORICO_FILE):
        with open(HISTORICO_FILE, 'w') as f:
            f.write("")

def cargar_historias_publicadas():
    """Carga artículos ya publicados para no repetir"""
    crear_historico_si_no_existe()
    try:
        with open(HISTORICO_FILE, 'r') as f:
            lineas = f.readlines()
            urls = set()
            for linea in lineas:
                if "url:" in linea:
                    url = linea.split("url:")[1].strip()
                    urls.add(url)
            return urls
    except Exception as e:
        print(f"⚠️ Error cargando histórico: {e}")
        return set()

def guardar_historia_publicada(url, titulo):
    """Guarda artículo publicado en histórico"""
    try:
        with open(HISTORICO_FILE, 'a') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] url: {url} | titulo: {titulo}\n")
        return True
    except Exception as e:
        print(f"⚠️ Error guardando en histórico: {e}")
        return False

# ==================== NEWSAPI ====================

def buscar_noticias(cantidad=10):
    """Busca noticias sobre mascotas en NewsAPI"""
    if not NEWSAPI_KEY:
        print("❌ ERROR: NEWSAPI_KEY no configurada en variables de entorno")
        return []

    url = "https://newsapi.org/v2/everything"

    # Keywords para mascotas
    queries = ["perros", "gatos", "mascotas", "animales domésticos"]

    todas_noticias = []

    for query in queries:
        params = {
            "q": query,
            "sortBy": "publishedAt",
            "language": "es",
            "pageSize": 5,
            "apiKey": NEWSAPI_KEY
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                todas_noticias.extend(data.get("articles", []))
            else:
                print(f"⚠️ NewsAPI error: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Error buscando en NewsAPI: {e}")

    # Deduplicar y ordenar por fecha
    noticias_unicas = {n['url']: n for n in todas_noticias}
    noticias = sorted(
        noticias_unicas.values(),
        key=lambda x: x.get('publishedAt', ''),
        reverse=True
    )

    return noticias[:cantidad]

def filtrar_noticias_nuevas(noticias):
    """Filtra noticias que NO han sido publicadas"""
    publicadas = cargar_historias_publicadas()
    nuevas = [n for n in noticias if n['url'] not in publicadas]
    return nuevas

# ==================== GENERACIÓN DE CONTENIDO ====================

def generar_post(noticia):
    """Genera post único basado en la noticia"""
    titulo = noticia.get('title', 'Sin título')
    descripcion = noticia.get('description', '')[:100]
    enlace = noticia.get('url', '')

    # Tipos de mascotas detectadas
    es_perro = any(p in titulo.lower() for p in ['perro', 'canino', 'cachorro'])
    es_gato = any(g in titulo.lower() for g in ['gato', 'felino', 'gatito'])
    es_mascota = 'mascota' in titulo.lower()

    # Emojis según tipo
    emoji = "🐕" if es_perro else "🐱" if es_gato else "🐾"

    # Generar enlace corto simulado (en producción usar is.gd API)
    enlace_corto = f"https://is.gd/pet_{hash(enlace) % 10000}"

    post = f"""{emoji} {titulo.upper()}

{descripcion}...

📚 Fuente: Noticia relevante sobre mascotas
🔗 Descubre más sobre tu mascota:
👉 {enlace_corto}

#Mascotas #Perros #Gatos #CienciaAnimal #OertasBestiales"""

    return {
        "titulo": titulo,
        "descripcion": descripcion,
        "post": post,
        "enlace": enlace_corto,
        "emoji": emoji,
        "url_original": enlace
    }

# ==================== GENERACIÓN DE IMÁGENES ====================

def generar_imagen_dinamica(contenido):
    """Genera imagen profesional dinámicamente"""
    # Crear imagen
    img = Image.new('RGB', (IMG_WIDTH, IMG_HEIGHT), COLOR_BG)
    draw = ImageDraw.Draw(img)

    # Fondo degradado simulado con rectángulos
    draw.rectangle([(0, 0), (IMG_WIDTH//2, IMG_HEIGHT)], fill='#F0F8F4')
    draw.rectangle([(IMG_WIDTH//2, 0), (IMG_WIDTH, IMG_HEIGHT)], fill='#FFF5E6')

    # Emoji grande
    emoji = contenido['emoji']
    try:
        # Intentar con fuente grande del sistema
        titulo_font = ImageFont.truetype("arial.ttf", 72)
        descripcion_font = ImageFont.truetype("arial.ttf", 24)
        cta_font = ImageFont.truetype("arial.ttf", 32)
    except:
        titulo_font = ImageFont.load_default()
        descripcion_font = ImageFont.load_default()
        cta_font = ImageFont.load_default()

    # Emoji
    draw.text((60, 60), emoji, fill=COLOR_TEXT, font=titulo_font)

    # Título (con palabra wrapping)
    titulo = contenido['titulo']
    if len(titulo) > 60:
        titulo = titulo[:57] + "..."

    draw.text((60, 160), titulo, fill=COLOR_PRIMARY, font=descripcion_font)

    # Descripción
    desc = contenido['descripcion']
    if len(desc) > 80:
        desc = desc[:77] + "..."

    draw.text((60, 350), desc, fill=COLOR_TEXT, font=descripcion_font)

    # CTA
    draw.rectangle([(750, 450), (1150, 550)], fill=COLOR_PRIMARY)
    draw.text((950, 485), "Descubre más", fill=COLOR_BG, font=cta_font, anchor="mm")

    # Logo
    draw.text((IMG_WIDTH - 100, IMG_HEIGHT - 50), "Ofertas\nBestiales",
              fill=COLOR_PRIMARY, font=descripcion_font, anchor="rb")

    # Guardar en BytesIO
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    return img_bytes.getvalue()

# ==================== GITHUB ====================

def subir_imagen_github(imagen_bytes, nombre_archivo, mensaje_commit):
    """Sube imagen a GitHub"""
    if not GITHUB_TOKEN:
        print("❌ ERROR: GITHUB_TOKEN no configurada")
        return None

    # Preparar URL
    url = f"https://api.github.com/repos/{REPO}/contents/posts/{nombre_archivo}"

    # Encodesr base64
    contenido_b64 = base64.b64encode(imagen_bytes).decode('utf-8')

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Obtener SHA actual si existe
    sha = None
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            sha = response.json()['sha']
    except:
        pass

    # Preparar payload
    payload = {
        "message": mensaje_commit,
        "content": contenido_b64
    }

    if sha:
        payload["sha"] = sha

    # Subir
    try:
        response = requests.put(url, json=payload, headers=headers, timeout=30)

        if response.status_code in [200, 201]:
            # Retornar URL raw
            url_raw = f"{GITHUB_BASE}/{REPO}/main/posts/{nombre_archivo}"
            return url_raw
        else:
            print(f"❌ Error subiendo a GitHub: {response.status_code}")
            print(f"   {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ Error en GitHub: {str(e)}")
        return None

# ==================== MAIN ====================

def main():
    print("\n" + "="*70)
    print("🚀 AUTOMATIZACIÓN OFERTAS BESTIALES - BÚSQUEDA DINÁMICA")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")

    # 1. Buscar noticias
    print("📡 Buscando noticias sobre mascotas...")
    noticias = buscar_noticias(10)

    if not noticias:
        print("❌ No se encontraron noticias")
        return

    print(f"✅ Encontradas {len(noticias)} noticias")

    # 2. Filtrar nuevas
    print("\n🔍 Filtrando historias ya publicadas...")
    noticias_nuevas = filtrar_noticias_nuevas(noticias)

    if not noticias_nuevas:
        print("⚠️ Todas las noticias ya fueron publicadas")
        noticias_nuevas = noticias[:1]  # Usar la más reciente como fallback

    print(f"✅ {len(noticias_nuevas)} historias nuevas para publicar")

    # 3. Generar y subir
    urls_generadas = []

    for idx, noticia in enumerate(noticias_nuevas[:2], 1):  # Máximo 2 por ejecución
        print(f"\n--- Noticia {idx} ---")

        try:
            # Generar contenido
            contenido = generar_post(noticia)
            print(f"📝 Título: {contenido['titulo'][:50]}...")

            # Generar imagen
            print("🎨 Generando imagen...")
            imagen = generar_imagen_dinamica(contenido)

            # Subir a GitHub
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f"noticia_{timestamp}_{idx}.png"
            mensaje = f"Nueva noticia: {contenido['titulo'][:50]}"

            print(f"📤 Subiendo a GitHub: {nombre_archivo}")
            url_github = subir_imagen_github(imagen, nombre_archivo, mensaje)

            if url_github:
                urls_generadas.append({
                    "id": f"noticia_{timestamp}_{idx}",
                    "titulo": contenido['titulo'],
                    "post": contenido['post'],
                    "imagen_url": url_github,
                    "enlace_afiliado": contenido['enlace'],
                    "timestamp": timestamp
                })
                print(f"✅ Publicada: {nombre_archivo}")

                # Guardar en histórico
                guardar_historia_publicada(noticia['url'], contenido['titulo'])
            else:
                print(f"❌ Error subiendo imagen")

        except Exception as e:
            print(f"❌ Error procesando noticia: {str(e)}")

    # 4. Generar JSON para Make
    if urls_generadas:
        output_json = {
            "timestamp": datetime.now().isoformat(),
            "cantidad": len(urls_generadas),
            "noticias": urls_generadas
        }

        # Guardar en raíz del repo (GitHub subirá automáticamente)
        with open('urls_noticias.json', 'w') as f:
            json.dump(output_json, f, indent=2, ensure_ascii=False)

        print(f"\n✅ JSON generado: urls_noticias.json")
        print(f"✅ Listo para Make.com")

    print("\n" + "="*70)
    print("✅ PROCESO COMPLETADO")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
