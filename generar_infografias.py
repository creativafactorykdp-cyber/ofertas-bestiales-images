#!/usr/bin/env python3
"""
Script para generar 3 infografías profesionales con Matplotlib/Seaborn
y subirlas automáticamente a GitHub usando un token seguro.
"""

import os
import json
import base64
from datetime import datetime
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# CONFIGURACIÓN
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Token desde variable de entorno
GITHUB_USER = "creativafactorykdp-cyber"
REPO_NAME = "ofertas-bestiales-images"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/contents"

# Configurar estilo de Seaborn
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 12

def generar_infografia_1():
      """Infografía 1: Análisis de Ofertas por Categoría"""
      fig, ax = plt.subplots(figsize=(14, 10))

    # Datos de ejemplo
      categorias = ['Electrónica', 'Ropa', 'Hogar', 'Deportes', 'Libros', 'Belleza']
      ofertas = np.random.randint(50, 200, len(categorias))
      colores = sns.color_palette("husl", len(categorias))

    # Gráfico de barras
      barras = ax.barh(categorias, ofertas, color=colores, edgecolor='black', linewidth=2)

    # Añadir valores en las barras
      for i, (barra, valor) in enumerate(zip(barras, ofertas)):
                ax.text(valor + 2, i, f'{valor}', va='center', fontweight='bold', fontsize=11)

      ax.set_xlabel('Número de Ofertas', fontsize=13, fontweight='bold')
      ax.set_title('Análisis de Ofertas por Categoría - 2026', fontsize=16, fontweight='bold', pad=20)
      ax.set_xlim(0, max(ofertas) + 20)

    plt.tight_layout()
    return fig, 'infografia_ofertas_categoria.png'

def generar_infografia_2():
      """Infografía 2: Tendencia de Descuentos"""
      fig, ax = plt.subplots(figsize=(14, 10))

    # Datos de tendencia
      meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio']
      descuentos = np.array([15, 18, 22, 25, 28, 32])

    # Gráfico de línea con área
      ax.fill_between(range(len(meses)), descuentos, alpha=0.3, color='#FF6B6B')
      ax.plot(meses, descuentos, marker='o', linewidth=3, markersize=10, 
              color='#FF6B6B', markerfacecolor='#FFE66D', markeredgewidth=2)

    # Añadir valores en puntos
      for x, y in enumerate(descuentos):
                ax.text(x, y + 0.5, f'{y}%', ha='center', fontweight='bold', fontsize=11)

      ax.set_ylabel('Descuento Promedio (%)', fontsize=13, fontweight='bold')
      ax.set_xlabel('Mes', fontsize=13, fontweight='bold')
      ax.set_title('Tendencia de Descuentos a lo Largo del Año', fontsize=16, fontweight='bold', pad=20)
      ax.grid(True, alpha=0.3)
      ax.set_ylim(10, 35)

    plt.tight_layout()
    return fig, 'infografia_tendencia_descuentos.png'

def generar_infografia_3():
      """Infografía 3: Distribución de Compras por Hora"""
      fig, ax = plt.subplots(figsize=(14, 10))

    # Datos de distribución
      horas = [f'{h:02d}:00' for h in range(24)]
      compras = np.random.randint(10, 100, 24)
      compras[18:22] = np.random.randint(150, 250, 4)  # Pico en la tarde

    # Gráfico de barras con gradiente
      colores_gradiente = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(compras)))
      barras = ax.bar(range(len(horas)), compras, color=colores_gradiente, edgecolor='black', linewidth=1)

    # Cada 3 horas mostrar etiqueta
      ax.set_xticks(range(0, len(horas), 3))
      ax.set_xticklabels([horas[i] for i in range(0, len(horas), 3)], rotation=45)

    ax.set_ylabel('Número de Compras', fontsize=13, fontweight='bold')
    ax.set_xlabel('Hora del Día', fontsize=13, fontweight='bold')
    ax.set_title('Distribución de Compras por Hora del Día', fontsize=16, fontweight='bold', pad=20)

    plt.tight_layout()
    return fig, 'infografia_compras_hora.png'

def subir_a_github(imagen_path, imagen_nombre):
      """Sube una imagen a GitHub y retorna la URL raw"""
      if not GITHUB_TOKEN:
                print("❌ Error: GITHUB_TOKEN no configurado. Usa: export GITHUB_TOKEN='tu_token'")
                return None

      with open(imagen_path, 'rb') as f:
        contenido = base64.b64encode(f.read()).decode('utf-8')

            url = f"{GITHUB_API_URL}/{imagen_nombre}"
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Content-Type": "application/json"
            }

            datos = {
                "message": f"Actualizar infografía: {imagen_nombre}",
                "content": contenido,
                "branch": "main"
            }

            try:
                      response = requests.put(url, headers=headers, json=datos)
                      if response.status_code in [201, 200]:
                                    print(f"✅ {imagen_nombre} subido exitosamente")
                                    # URL raw de GitHub
                                    url_raw = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main/{imagen_nombre}"
                          return url_raw
            else:
            print(f"❌ Error subiendo {imagen_nombre}: {response.status_code}")
                          print(response.json())
                          return None
except Exception as e:
        print(f"❌ Excepción: {e}")
        return None

def main():
      """Función principal"""
      print("🎨 Generando infografías profesionales...")
      print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    infografias_urls = {}

    # Generar Infografía 1
    print("📊 Generando Infografía 1: Ofertas por Categoría...")
    fig1, nombre1 = generar_infografia_1()
    fig1.savefig(nombre1, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig1)
    url1 = subir_a_github(nombre1, nombre1)
    if url1:
              infografias_urls['infografia_1'] = url1

    # Generar Infografía 2
    print("📈 Generando Infografía 2: Tendencia de Descuentos...")
    fig2, nombre2 = generar_infografia_2()
    fig2.savefig(nombre2, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig2)
    url2 = subir_a_github(nombre2, nombre2)
    if url2:
              infografias_urls['infografia_2'] = url2

    # Generar Infografía 3
    print("📉 Generando Infografía 3: Compras por Hora...")
    fig3, nombre3 = generar_infografia_3()
    fig3.savefig(nombre3, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig3)
    url3 = subir_a_github(nombre3, nombre3)
    if url3:
              infografias_urls['infografia_3'] = url3

    # Guardar URLs en archivo JSON
    config_file = 'urls_infografias.json'
    config_data = {
              'timestamp': datetime.now().isoformat(),
              'urls': infografias_urls
    }

    with open(config_file, 'w') as f:
              json.dump(config_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Proceso completado!")
    print(f"📁 URLs guardadas en: {config_file}")
    print(f"\n🔗 URLs de las infografías:")
    for key, url in infografias_urls.items():
              print(f"  {key}: {url}")

    # Limpiar archivos locales
    for nombre in [nombre1, nombre2, nombre3]:
              if os.path.exists(nombre):
                            os.remove(nombre)

          return infografias_urls

if __name__ == '__main__':
      main()
