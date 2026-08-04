import streamlit as st
from streamlit_option_menu import option_menu
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import qrcode
from io import BytesIO
import json
import os
import base64
import requests
from bs4 import BeautifulSoup
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from datetime import datetime, timedelta
import pytz
import random
import time
import numpy as np
import matplotlib.pyplot as plt
import librosa
import scipy.signal
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Fetén Workspace Pro", page_icon="✦", layout="wide", initial_sidebar_state="collapsed")

LOGO_URL = "https://i.supaimg.com/4a90693e-1b41-4313-8203-f60c8b81825f/da7de7fd-3ded-4499-b3f4-790424f0dc5a.png"
TZ_AR = pytz.timezone('America/Argentina/Buenos_Aires')

def obtener_hora_actual():
    return datetime.now(TZ_AR).strftime("%Y-%m-%d %H:%M:%S")

# --- 2. DISEÑO UI/UX "SAAS OBSIDIAN PRO" ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    
    /* Fondo Obsidiana Premium */
    .stApp {
        background-color: #050505 !important;
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(251, 175, 59, 0.05), transparent 25%), 
            radial-gradient(circle at 90% 80%, rgba(180, 113, 63, 0.04), transparent 25%) !important;
        color: #EDEDED !important;
    }

    .logo-img { display: block; max-width: 100%; height: auto; filter: brightness(1.5) contrast(1.2); }

    /* Contenedores Base */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #0A0A0B !important;
        border: 1px solid #1C1C1F !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important;
        margin-bottom: 16px !important;
    }
    
    /* Títulos */
    .gradient-text {
        background: linear-gradient(135deg, #FFFFFF 0%, #FBAF3B 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800; letter-spacing: -0.03em;
    }
    h1, h2 { font-weight: 800 !important; letter-spacing: -0.02em !important; color: #FAFAFA !important; }
    h3, h4 { color: #D4D4D8 !important; font-weight: 600 !important; letter-spacing: -0.01em !important; }
    .section-title { color: #71717A; font-size: 12px; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 16px; }

    /* Inputs */
    .stTextInput input, .stSelectbox select, .stNumberInput input, .stDateInput input, .stTimeInput input, .stTextArea textarea, .stChatInput input {
        background-color: #0E0E11 !important; border: 1px solid #27272A !important; color: #FAFAFA !important;
        border-radius: 10px !important; padding: 12px 16px !important; font-weight: 400 !important;
    }
    .stTextInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus { border-color: #FBAF3B !important; box-shadow: 0 0 0 1px #FBAF3B !important; }
    
    /* Botones */
    .stButton button {
        background: linear-gradient(135deg, #FBAF3B 0%, #D97706 100%) !important; border: none !important; color: #050505 !important;
        border-radius: 10px !important; font-weight: 700 !important; padding: 0.6rem 1rem !important; transition: all 0.2s ease !important; width: 100% !important;
    }
    .stButton button:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 20px rgba(251, 175, 59, 0.3) !important; }
    .stButton button p { color: #050505 !important; font-weight: 700 !important; margin: 0; }
    
    [data-testid="stBaseButton-secondary"] { background: #0A0A0B !important; border: 1px solid #27272A !important; color: #A1A1AA !important; box-shadow: none !important; }
    [data-testid="stBaseButton-secondary"]:hover { border-color: #52525B !important; color: #FAFAFA !important; }

    /* Red Social UI */
    .tweet-card {
        background: #0A0A0B; border: 1px solid #1C1C1F; border-radius: 16px; padding: 20px; margin-bottom: 16px; transition: background 0.2s;
    }
    .tweet-card:hover { background: #0E0E11; }
    .tweet-header { display: flex; align-items: center; margin-bottom: 10px; }
    .tweet-avatar { width: 44px; height: 44px; border-radius: 50%; object-fit: cover; margin-right: 12px; border: 1px solid #27272A; }
    .tweet-name { font-weight: 700; color: #FAFAFA; font-size: 15px; margin: 0; }
    .tweet-handle { color: #71717A; font-size: 13px; margin: 0; }
    .tweet-body { font-size: 15px; color: #E2E8F0; margin-top: 4px; margin-bottom: 12px; line-height: 1.5; white-space: pre-wrap; }
    .tweet-img { width: 100%; border-radius: 12px; border: 1px solid #1C1C1F; margin-bottom: 12px; max-height: 400px; object-fit: cover; }
    .tweet-actions { display: flex; justify-content: space-between; max-width: 300px; color: #71717A; font-size: 13px; font-weight: 600; padding-top: 10px; border-top: 1px solid #1C1C1F; }

    .avatar-circle { border-radius: 50%; object-fit: cover; border: 2px solid #FBAF3B; box-shadow: 0 4px 10px rgba(180, 113, 63, 0.3); }
    
    /* Credencial */
    .credencial-feten {
        background-color: #0A0A0B; border: 1px solid #1C1C1F; border-radius: 16px; padding: 30px; width: 100%; max-width: 380px; margin: 0 auto; text-align: center; position: relative; overflow: hidden;
    }
    .credencial-feten::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #FBAF3B, #B4713F); }
    .credencial-img { width: 100px; height: 100px; border-radius: 50%; border: 2px solid #FBAF3B; margin-bottom: 15px; object-fit: cover;}
    .credencial-name { font-size: 20px; font-weight: 700; margin: 0; color: #FAFAFA !important;}
    .credencial-role { font-size: 12px; color: #FBAF3B !important; margin-top: 4px; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 1px;}

    [data-testid="stMetricValue"] { color: #FAFAFA !important; font-size: 2.2rem !important; font-weight: 800 !important; letter-spacing: -1px; }
    [data-testid="stMetricLabel"] { color: #A1A1AA !important; text-transform: uppercase !important; letter-spacing: 1px !important; font-size: 0.75rem !important; font-weight: 600 !important; }

    @media (max-width: 768px) {
        [data-testid="column"] { width: 100% !important; flex: 100% !important; min-width: 100% !important; margin-bottom: 10px !important; }
        .block-container { padding-left: 1rem !important; padding-right: 1rem !important; padding-top: 1.5rem !important; }
    }
    </style>
""", unsafe_allow_html=True)

ARCHIVO_BD = "ftn_database.json"

# --- 3. INICIALIZACIÓN PROFUNDA (CREACIÓN DE USUARIOS PRUEBA) ---
def generar_qr_base64(datos):
    qr = qrcode.QRCode(version=1, box_size=5, border=1)
    qr.add_data(datos)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def guardar_y_recargar():
    with open(ARCHIVO_BD, "w", encoding="utf-8") as f:
        json.dump(st.session_state["proyectos"], f, ensure_ascii=False, indent=4)
    st.rerun()

def inicializar_bd():
    if "proyectos" not in st.session_state:
        if os.path.exists(ARCHIVO_BD):
            with open(ARCHIVO_BD, "r", encoding="utf-8") as f:
                data_cargada = json.load(f)
        else:
            data_cargada = {}

        if "_CONFIG_" not in data_cargada:
            data_cargada["_CONFIG_"] = {"usuarios": {}}
            
        conf = data_cargada["_CONFIG_"]
        
        for lb in ["recordatorios", "notificaciones", "mensajes", "tickets_soporte", "social_posts", "social_stories"]:
            if lb not in conf: conf[lb] = []

        # Admin Default
        if "lau@admin.com" not in conf.get("usuarios", {}):
            conf["usuarios"]["lau@admin.com"] = {
                "nombre": "Lau (Admin)", "pass": "1234", "rol": "Super Admin", "nivel": "jefe_supremo", "estado": "Aprobado",
                "foto": "", "credencial": "FTN-0001", "edad": "", "roles_fav": "Directora", "dieta": "Ninguna", "specs": "", "cv": "", "portfolio": "", "spotify": "", "amigos": ["director@feten.com", "arte@feten.com"], "acceso_rapido": "Panel General", "alias": "lau_ok"
            }
            
        # Usuarios Dummy de Prueba
        if "director@feten.com" not in conf.get("usuarios", {}):
            conf["usuarios"]["director@feten.com"] = {
                "nombre": "Matias (Director)", "pass": "1234", "rol": "Dirección", "nivel": "jefe", "estado": "Aprobado",
                "foto": "", "credencial": "FTN-0002", "edad": "35", "roles_fav": "Cine publicitario", "dieta": "Ninguna", "specs": "", "cv": "", "portfolio": "", "spotify": "https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT", "amigos": [], "acceso_rapido": "Monitor DIR", "alias": "mati_dir"
            }
        if "arte@feten.com" not in conf.get("usuarios", {}):
            conf["usuarios"]["arte@feten.com"] = {
                "nombre": "Sofi (Arte)", "pass": "1234", "rol": "Dirección de Arte", "nivel": "jefe", "estado": "Aprobado",
                "foto": "", "credencial": "FTN-0003", "edad": "28", "roles_fav": "Escenografía", "dieta": "Vegana", "specs": "", "cv": "", "portfolio": "", "spotify": "https://open.spotify.com/track/11dFghVXANMlKmJXsNCbNl", "amigos": [], "acceso_rapido": "Arte & Vestuario", "alias": "sofi_arte"
            }

        # Posts Dummy
        if not conf["social_posts"]:
            conf["social_posts"] = [
                {"usuario": "arte@feten.com", "texto": "Armando el set de los años 80, una locura los detalles que estamos consiguiendo. Mañana subo fotos de la utilería.", "imagen": None, "timestamp": (datetime.now(TZ_AR) - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"), "likes": 12},
                {"usuario": "director@feten.com", "texto": "Recién terminamos el scouting técnico en San Telmo. ¡La luz de esa locación es increíble para la escena final! Listos para arrancar.", "imagen": None, "timestamp": (datetime.now(TZ_AR) - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"), "likes": 34}
            ]
            
        for em, info in conf["usuarios"].items():
            if "amigos" not in info: info["amigos"] = []
            if "spotify" not in info: info["spotify"] = ""
            if "estado" not in info: info["estado"] = "Aprobado"
            if "credencial" not in info: info["credencial"] = f"FTN-{random.randint(1000, 9999)}"
            if "acceso_rapido" not in info: info["acceso_rapido"] = "Panel General"
            if "alias" not in info: info["alias"] = em.split("@")[0]

        claves_proy = ["archivos_pendientes", "avisos", "equipos", "pedidos_equipos", "continuidad", "arte", "planos", "plan_rodaje", "plantas_luces", "sonido_log", "tomas_dir", "personajes", "locaciones", "crew", "catering", "links", "presupuesto", "casting", "desglose", "comparador_rentals", "carrito_rentals", "directorio_rentals", "kanban"]
        for nombre_proy, datos_proy in data_cargada.items():
            if nombre_proy != "_CONFIG_":
                if "contexto_aprobado" not in datos_proy: datos_proy["contexto_aprobado"] = "Proyecto actualizado."
                for clave in claves_proy:
                    if clave not in datos_proy: datos_proy[clave] = []
                    
        st.session_state["proyectos"] = data_cargada

inicializar_bd()

if "ruta" not in st.session_state: st.session_state["ruta"] = "Inicio"
if "proyecto_activo" not in st.session_state: st.session_state["proyecto_activo"] = None
if "menu_option" not in st.session_state: st.session_state["menu_option"] = "Panel General"

# --- 4. MODALES GLOBALES DE ACCIÓN ---
@st.dialog("◈ Reportar Problema")
def ventana_soporte(usuario):
    asunto = st.text_input("Asunto")
    desc = st.text_area("Descripción del bug o problema")
    if st.button("Enviar Ticket", use_container_width=True):
        if asunto and desc:
            st.session_state["proyectos"]["_CONFIG_"]["tickets_soporte"].append({
                "usuario": usuario, "fecha": obtener_hora_actual(), "asunto": asunto, "desc": desc, "estado": "Pendiente"
            })
            st.success("Ticket enviado al Administrador.")
            guardar_y_recargar()

@st.dialog("◈ Nueva Historia")
def ventana_historia(usuario):
    foto_hist = st.file_uploader("Subir foto", type=["jpg", "png", "jpeg"])
    if st.button("Publicar (24h)", use_container_width=True):
        if foto_hist:
            b64 = base64.b64encode(foto_hist.read()).decode('utf-8')
            st.session_state["proyectos"]["_CONFIG_"]["social_stories"].append({
                "usuario": usuario, "foto": b64, "timestamp": obtener_hora_actual()
            })
            guardar_y_recargar()

# Resto de Modales Base...
@st.dialog("◈ Nueva Tarea Kanban")
def ventana_kanban(proyecto, autor):
    tarea = st.text_input("Descripción de la Tarea")
    estado = st.selectbox("Estado Inicial", ["Pendiente", "En Proceso", "Completado"])
    if st.button("Agregar al Tablero", use_container_width=True):
        if tarea:
            st.session_state["proyectos"][proyecto]["kanban"].append({"tarea": tarea, "estado": estado, "autor": autor})
            guardar_y_recargar()

@st.dialog("◈ Recordatorio Global")
def ventana_recordatorio(es_admin, autor):
    titulo = st.text_input("Título")
    fecha = st.date_input("Fecha Límite")
    tipo = st.selectbox("Visibilidad", ["Privado", "Global"]) if es_admin else "Privado"
    if st.button("Guardar", use_container_width=True):
        if titulo:
            st.session_state["proyectos"]["_CONFIG_"]["recordatorios"].append({"autor": autor, "titulo": titulo, "fecha": str(fecha), "tipo": tipo})
            guardar_y_recargar()

@st.dialog("⟡ Emitir Comunicado")
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
        loc_elegida = st.selectbox("Locación", nombres_locs) if nombres_locs else st.text_input("Locación")
        notas_citacion = st.text_area("Notas extras")
        if st.button("Publicar Citación", use_container_width=True):
            st.session_state["proyectos"][proyecto]["avisos"].append({"tipo": "citacion", "autor": autor, "fecha": str(fecha), "hora": str(hora), "locacion": loc_elegida, "notas": notas_citacion})
            guardar_y_recargar()

@st.dialog("⌖ Registrar Locación")
def ventana_locacion(proyecto):
    nombre = st.text_input("Nombre")
    direccion = st.text_input("Dirección")
    c1, c2 = st.columns(2)
    lat = c1.number_input("Latitud", format="%.6f", value=0.0)
    lon = c2.number_input("Longitud", format="%.6f", value=0.0)
    permisos = st.selectbox("Permisos", ["En gestión", "Aprobado", "No requiere"])
    if st.button("Guardar", use_container_width=True):
        if nombre:
            st.session_state["proyectos"][proyecto]["locaciones"].append({"nombre": nombre, "direccion": direccion, "lat": lat, "lon": lon, "permisos": permisos})
            guardar_y_recargar()

@st.dialog("◈ Fichar Crew")
def ventana_crew(proyecto):
    nombre = st.text_input("Nombre")
    c1, c2 = st.columns(2)
    rol = c1.text_input("Rol")
    telefono = c2.text_input("Teléfono")
    obra_social = st.text_input("Seguro/ART")
    if st.button("Guardar", use_container_width=True):
        if nombre:
            st.session_state["proyectos"][proyecto]["crew"].append({"nombre": nombre, "rol": rol, "telefono": telefono, "obra_social": obra_social})
            guardar_y_recargar()

@st.dialog("◈ Planilla de Dietas")
def ventana_catering(proyecto):
    nombre = st.text_input("Nombre")
    dieta = st.selectbox("Restricción", ["Ninguna", "Vegetariano", "Vegano", "Celíaco", "Diabético"])
    alergias = st.text_area("Alergias")
    if st.button("Guardar", use_container_width=True):
        if nombre:
            st.session_state["proyectos"][proyecto]["catering"].append({"nombre": nombre, "dieta": dieta, "alergias": alergias})
            guardar_y_recargar()

@st.dialog("✉ Pedido de Equipamiento")
def ventana_pedido(proyecto, area):
    item_nombre = st.text_input("Equipo")
    justificacion = st.text_area("Notas")
    prioridad = st.selectbox("Urgencia", ["Baja", "Media", "Alta"])
    if st.button("Enviar", use_container_width=True):
        if item_nombre:
            st.session_state["proyectos"][proyecto]["pedidos_equipos"].append({"area": area, "item": item_nombre, "notas": justificacion, "prioridad": prioridad, "estado": "Pendiente"})
            guardar_y_recargar()

@st.dialog("⚙ Cargar Equipo al Inventario")
def ventana_equipo(proyecto, area):
    col1, col2 = st.columns(2)
    item_nombre = col1.text_input("Ítem")
    cantidad = col2.number_input("Cant", min_value=1, value=1)
    tipo = col1.selectbox("Condición", ["Propio", "Alquilado"])
    rental = col2.text_input("Rental", disabled=(tipo=="Propio"))
    if st.button("Registrar", use_container_width=True):
        if item_nombre:
            st.session_state["proyectos"][proyecto]["equipos"].append({"area": area, "item": item_nombre, "cant": cantidad, "tipo": tipo, "rental": rental if tipo == "Alquilado" else "N/A"})
            guardar_y_recargar()

@st.dialog("⟡ Nota de Raccord")
def ventana_continuidad(proyecto):
    c1, c2 = st.columns(2)
    escena = c1.text_input("ESC")
    toma = c2.text_input("TOMA")
    detalle = st.text_area("Detalle")
    if st.button("Guardar", use_container_width=True):
        if escena and detalle:
            st.session_state["proyectos"][proyecto]["continuidad"].append({"escena": escena, "toma": toma, "detalle": detalle})
            guardar_y_recargar()

@st.dialog("◈ Archivo de Arte")
def ventana_arte(proyecto):
    categoria = st.radio("Tipo:", ["Utilería", "Vestuario"], horizontal=True)
    objeto = st.text_input("Objeto")
    responsable = st.text_input("Responsable")
    estado = st.selectbox("Status", ["Pendiente", "Aprobado", "En Set"])
    foto_subida = st.file_uploader("Foto", type=["jpg", "png", "jpeg"])
    if st.button("Guardar", use_container_width=True):
        if objeto:
            foto_base64 = base64.b64encode(foto_subida.read()).decode('utf-8') if foto_subida else None
            st.session_state["proyectos"][proyecto]["arte"].append({"categoria": categoria, "objeto": objeto, "responsable": responsable, "estado": estado, "foto": foto_base64})
            guardar_y_recargar()

@st.dialog("◈ Diagramar Plano")
def ventana_plano(proyecto):
    c1, c2 = st.columns(2)
    escena = c1.text_input("ESC")
    toma = c2.text_input("PLANO")
    tamano = st.selectbox("Encuadre", ["PG", "PE", "PM", "PP", "PD"])
    movimiento = st.selectbox("Movimiento", ["Fijo", "Handheld", "Paneo", "Tilt", "Tracking", "Steady"])
    if st.button("Guardar", use_container_width=True):
        if escena:
            st.session_state["proyectos"][proyecto]["planos"].append({"escena": escena, "toma": toma, "tamano": tamano, "movimiento": movimiento})
            guardar_y_recargar()

@st.dialog("⏱ Registrar Bloque")
def ventana_cronograma(proyecto):
    hora = st.time_input("Hora")
    actividad = st.text_input("Actividad")
    if st.button("Fijar", use_container_width=True):
        if actividad:
            st.session_state["proyectos"][proyecto]["plan_rodaje"].append({"hora": str(hora), "actividad": actividad})
            guardar_y_recargar()

@st.dialog("◈ Log de Sonido")
def ventana_sonido(proyecto):
    c1, c2 = st.columns(2)
    escena = c1.text_input("ESC")
    toma = c2.text_input("TOMA")
    pistas = st.text_area("Pistas")
    obs = st.text_input("Notas")
    if st.button("Guardar", use_container_width=True):
        if escena:
            st.session_state["proyectos"][proyecto]["sonido_log"].append({"escena": escena, "toma": toma, "pistas": pistas, "obs": obs})
            guardar_y_recargar()

@st.dialog("🎬 Calificar Toma")
def ventana_toma_dir(proyecto):
    c1, c2 = st.columns(2)
    escena = c1.text_input("ESC")
    toma = c2.text_input("TOMA")
    evaluacion = st.radio("Evaluación", ["BUENA", "MALA", "REGULAR"], horizontal=True)
    if st.button("Guardar", use_container_width=True):
        if escena:
            st.session_state["proyectos"][proyecto]["tomas_dir"].append({"escena": escena, "toma": toma, "evaluacion": evaluacion})
            guardar_y_recargar()

@st.dialog("◈ Estructurar Personaje")
def ventana_personaje(proyecto):
    nombre = st.text_input("Nombre")
    rol = st.selectbox("Jerarquía", ["Protagonista", "Antagonista", "Secundario"])
    objetivo = st.text_input("Objetivo")
    conflicto = st.text_area("Conflicto")
    if st.button("Guardar", use_container_width=True):
        if nombre:
            st.session_state["proyectos"][proyecto]["personajes"].append({"nombre": nombre, "rol": rol, "objetivo": objetivo, "conflicto": conflicto})
            guardar_y_recargar()

@st.dialog("⧉ Referencia URL")
def ventana_link(proyecto):
    titulo = st.text_input("Título")
    url = st.text_input("URL")
    desc = st.text_input("Descripción")
    if st.button("Guardar", use_container_width=True):
        if titulo and url:
            st.session_state["proyectos"][proyecto]["links"].append({"titulo": titulo, "url": url, "desc": desc})
            guardar_y_recargar()

@st.dialog("◈ Registrar Gasto")
def ventana_presupuesto(proyecto):
    item = st.text_input("Concepto")
    costo = st.number_input("Costo Neto ($)", min_value=0.0)
    area = st.selectbox("Área", ["Técnica", "Arte", "Producción", "Catering", "Transporte"])
    estado = st.selectbox("Estado", ["Pendiente", "Abonado"])
    if st.button("Registrar", use_container_width=True):
        if item:
            st.session_state["proyectos"][proyecto]["presupuesto"].append({"item": item, "costo": costo, "area": area, "estado": estado})
            guardar_y_recargar()

@st.dialog("◒ Perfil de Casting")
def ventana_casting(proyecto):
    actor = st.text_input("Actor")
    personaje = st.text_input("Personaje")
    reel = st.text_input("Reel")
    foto = st.file_uploader("Foto", type=["jpg", "png", "jpeg"])
    if st.button("Archivar", use_container_width=True):
        if actor:
            foto_base64 = base64.b64encode(foto.read()).decode('utf-8') if foto else None
            st.session_state["proyectos"][proyecto]["casting"].append({"actor": actor, "personaje": personaje, "reel": reel, "foto": foto_base64})
            guardar_y_recargar()

@st.dialog("▤ Desglose Escénico")
def ventana_desglose(proyecto):
    c1, c2, c3 = st.columns(3)
    escena = c1.text_input("ESC")
    intext = c2.selectbox("Locación", ["INT", "EXT", "INT/EXT"])
    dianoche = c3.selectbox("Horario", ["DÍA", "NOCHE", "ATARDECER"])
    desc = st.text_area("Acción")
    if st.button("Guardar", use_container_width=True):
        if escena:
            st.session_state["proyectos"][proyecto]["desglose"].append({"escena": escena, "intext": intext, "dianoche": dianoche, "desc": desc})
            guardar_y_recargar()

@st.dialog("⌂ Agregar Rental")
def ventana_nuevo_rental(proyecto):
    nombre = st.text_input("Nombre")
    url = st.text_input("Sitio Web")
    if st.button("Guardar", use_container_width=True):
        if nombre:
            st.session_state["proyectos"][proyecto]["directorio_rentals"].append({"nombre": nombre, "url": url})
            guardar_y_recargar()

@st.dialog("✦ Análisis IA de Equipos")
def ventana_comparador_rental(proyecto):
    directorio = st.session_state["proyectos"][proyecto].get("directorio_rentals", [])
    if not directorio:
        st.warning("Registra un Rental primero.")
        return
    rental_elegido = st.selectbox("Asignar a:", [r["nombre"] for r in directorio])
    url_rental = next((r["url"] for r in directorio if r["nombre"] == rental_elegido), "#")

    tab_url, tab_excel, tab_img = st.tabs(["URL", "Documento", "Imagen"])
    with tab_url:
        url_p = st.text_input("URL del inventario")
        if st.button("Extraer Web", use_container_width=True):
            try:
                soup = BeautifulSoup(requests.get(url_p, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10).text, 'html.parser')
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                mod = genai.GenerativeModel('gemini-1.5-flash')
                resp = mod.generate_content(f"Extrae a JSON: [{{\"nombre\": \"\", \"precio\": 0, \"estado\": \"Disponible\", \"url\": \"{url_p}\", \"foto\": \"\"}}]. Texto: {soup.get_text()[:10000]}")
                for p in json.loads(resp.text.strip().replace("```json", "").replace("```", "")):
                    p.update({"rental": rental_elegido, "url_rental": url_rental})
                    st.session_state["proyectos"][proyecto]["comparador_rentals"].append(p)
                guardar_y_recargar()
            except Exception as e: st.error(str(e))
    with tab_excel:
        arch = st.file_uploader("Archivo (XLSX/CSV)", type=["xlsx", "csv"])
        if st.button("Leer Doc", use_container_width=True):
            try:
                df = pd.read_csv(arch) if arch.name.endswith('.csv') else pd.read_excel(arch)
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                resp = genai.GenerativeModel('gemini-1.5-flash').generate_content(f"Extrae a JSON: [{{\"nombre\": \"\", \"precio\": 0, \"estado\": \"Disponible\", \"url\": \"{url_rental}\", \"foto\": \"\"}}]. Datos: {df.to_csv(index=False)[:10000]}")
                for p in json.loads(resp.text.strip().replace("```json", "").replace("```", "")):
                    p.update({"rental": rental_elegido, "url_rental": url_rental})
                    st.session_state["proyectos"][proyecto]["comparador_rentals"].append(p)
                guardar_y_recargar()
            except: st.error("Error")
    with tab_img:
        img_arch = st.file_uploader("Foto", type=["jpg", "png", "jpeg"])
        if st.button("Visión IA", use_container_width=True):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                resp = genai.GenerativeModel('gemini-1.5-flash').generate_content([f"Extrae a JSON: [{{\"nombre\": \"\", \"precio\": 0, \"estado\": \"Disponible\", \"url\": \"{url_rental}\", \"foto\": \"\"}}]", Image.open(img_arch)])
                for p in json.loads(resp.text.strip().replace("```json", "").replace("```", "")):
                    p.update({"rental": rental_elegido, "url_rental": url_rental})
                    st.session_state["proyectos"][proyecto]["comparador_rentals"].append(p)
                guardar_y_recargar()
            except: st.error("Error")

@st.dialog("◈ Checkout")
def ventana_checkout(proyecto):
    carrito = st.session_state["proyectos"][proyecto]["carrito_rentals"]
    directorio = st.session_state["proyectos"][proyecto].get("directorio_rentals", [])
    if not carrito: return st.warning("Vacío.")
    agrupados = {}
    for i in carrito: agrupados.setdefault(i.get("rental", "Desconocido"), []).append(i)
    for rn, items in agrupados.items():
        with st.container(border=True):
            st.markdown(f"### {rn}")
            for i in items: st.write(f"✦ {i['nombre']} **(${i['precio']:,.2f})**")
            st.success(f"Total: ${sum(i['precio'] for i in items):,.2f}")

@st.dialog("Purga de Datos")
def ventana_vaciar_comparador(proyecto):
    st.warning("Borrará catálogo y carrito.")
    if st.button("Confirmar", use_container_width=True):
        st.session_state["proyectos"][proyecto]["comparador_rentals"] = []
        st.session_state["proyectos"][proyecto]["carrito_rentals"] = []
        guardar_y_recargar()

# --- 5. GESTIÓN DE SESIÓN ---
if "usuario_logueado" not in st.session_state:
    st.session_state["usuario_logueado"] = None

# --- 6. ACCESO (LOGIN) ---
if st.session_state["usuario_logueado"] is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown(f"<div style='text-align: center;'><img src='{LOGO_URL}' class='logo-img' style='max-width:200px; margin-bottom: 20px;'></div>", unsafe_allow_html=True)
        tab_log, tab_reg = st.tabs(["Acceder", "Solicitar Cuenta"])
        db = st.session_state["proyectos"]["_CONFIG_"]["usuarios"]
        with tab_log:
            with st.container(border=True):
                e_in = st.text_input("Usuario", placeholder="correo@productora.com").lower().strip()
                p_in = st.text_input("Clave", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Ingresar", use_container_width=True):
                    if e_in in db and db[e_in]["pass"] == p_in:
                        if db[e_in]["estado"] == "Aprobado":
                            st.session_state["usuario_logueado"] = e_in
                            st.rerun()
                        else: st.warning("Cuenta pendiente de aprobación.")
                    else: st.error("Datos incorrectos.")
        with tab_reg:
            with st.container(border=True):
                n_reg = st.text_input("Nombre")
                e_reg = st.text_input("Correo").lower().strip()
                p_reg = st.text_input("Clave", type="password")
                f_reg = st.file_uploader("Foto ID", type=["jpg", "png", "jpeg"])
                if st.button("Registrar", use_container_width=True):
                    if n_reg and e_reg and p_reg and f_reg:
                        db[e_reg] = {"nombre": n_reg, "pass": p_reg, "rol": "Invitado", "nivel": "lectura", "estado": "Pendiente", "foto": base64.b64encode(f_reg.read()).decode('utf-8'), "credencial": f"FTN-{random.randint(1000,9999)}", "edad": "", "roles_fav": "", "portfolio": "", "spotify": "", "amigos": [], "acceso_rapido": "Panel General", "alias": e_reg.split("@")[0]}
                        guardar_y_recargar()
                        st.success("Enviado al administrador.")

# --- 7. PLATAFORMA ---
else:
    us_act = st.session_state["usuario_logueado"]
    db_users = st.session_state["proyectos"]["_CONFIG_"]["usuarios"]
    mis_datos = db_users[us_act]
    rol_actual = mis_datos["rol"]
    nivel_actual = mis_datos["nivel"]
    
    # NAVBAR ALINEADA PERFECTA (Foto y Botón alineados al bottom con el mismo alto)
    c_nav1, c_nav2, c_nav3, c_nav4, c_nav5, c_nav6 = st.columns([1.5, 1.2, 1.2, 4, 1.2, 1.2], vertical_alignment="bottom")
    with c_nav1:
        st.markdown(f"<img src='{LOGO_URL}' class='logo-img' style='height:40px; margin-bottom:5px;'>", unsafe_allow_html=True)
    with c_nav2:
        if st.button("⌂ Dashboard", use_container_width=True, type="secondary"): st.session_state["ruta"] = "Inicio"; st.rerun()
    with c_nav3:
        if st.button("◈ Social", use_container_width=True, type="secondary"): st.session_state["ruta"] = "Social"; st.rerun()
    with c_nav4:
        pass
    with c_nav5:
        if st.button("✉ Mensajes", use_container_width=True, type="secondary"): st.session_state["ruta"] = "Mensajes"; st.rerun()
    with c_nav6:
        # Contenedor flex para alinear imagen (40px) y botón (aprox 40px) en la misma línea
        f_src = f"data:image/jpeg;base64,{mis_datos['foto']}" if mis_datos.get("foto") else "https://via.placeholder.com/150"
        st.markdown(f"""
            <div style="display:flex; justify-content: flex-end; align-items:flex-end; gap: 10px; height:40px; margin-bottom: 2px;">
                <img src='{f_src}' style='width: 36px; height: 36px; border-radius: 50%; border: 2px solid #FBAF3B; object-fit: cover;'>
            </div>
        """, unsafe_allow_html=True)
        if st.button("⚙ Perfil", use_container_width=True, type="secondary"): st.session_state["ruta"] = "Perfil"; st.rerun()
            
    st.markdown("<hr style='border-color: #1C1C1F; margin-top: 5px; margin-bottom: 20px;'>", unsafe_allow_html=True)

    # --- INICIO (DASHBOARD COMPLETO) ---
    if st.session_state["ruta"] == "Inicio":
        col_q1, col_q2, col_q3, col_q4 = st.columns(4)
        with col_q1:
            with st.container(border=True):
                st.markdown("<div class='section-title' style='margin-bottom:0;'>MI ROL</div>", unsafe_allow_html=True)
                st.markdown(f"<h3 class='gradient-text' style='margin:0; font-size:18px;'>{rol_actual}</h3>", unsafe_allow_html=True)
        with col_q2:
            with st.container(border=True):
                st.markdown("<div class='section-title' style='margin-bottom:0;'>PROYECTOS</div>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='margin:0;'>{len([p for p in st.session_state['proyectos'].keys() if p != '_CONFIG_'])} Activos</h3>", unsafe_allow_html=True)
        with col_q3:
            with st.container(border=True):
                st.markdown("<div class='section-title' style='margin-bottom:5px;'>ACCESO RÁPIDO</div>", unsafe_allow_html=True)
                h_list = ["Panel General", "Tablero Kanban", "Rentals IA", "Presupuesto", "Base Crew", "Laboratorio Guion", "Luces (Canvas)", "Arte & Vestuario"]
                acc = st.selectbox("Herramienta", h_list, index=h_list.index(mis_datos.get("acceso_rapido", "Panel General")), label_visibility="collapsed")
                if acc != mis_datos.get("acceso_rapido"):
                    db_users[us_act]["acceso_rapido"] = acc
                    guardar_y_recargar()
                if st.button(f"Ir a {acc}", type="secondary"):
                    if st.session_state.get("proyecto_activo"):
                        st.session_state["menu_option"] = acc
                        st.session_state["ruta"] = "Proyecto"
                        st.rerun()
                    else: st.warning("Selecciona un proyecto.")
        with col_q4:
            with st.container(border=True):
                st.markdown("<div class='section-title' style='margin-bottom:5px;'>SOPORTE</div>", unsafe_allow_html=True)
                if st.button("Reportar Problema", type="secondary"): ventana_soporte(us_act)

        c_main, c_side = st.columns([2.5, 1], gap="large")
        with c_main:
            st.markdown("<div class='section-title'>PROYECTOS EN DESARROLLO</div>", unsafe_allow_html=True)
            if nivel_actual in ["jefe", "jefe_supremo"]:
                with st.popover("Crear Workspace"):
                    np_n = st.text_input("Nombre de la Producción:")
                    if st.button("Inicializar DB"):
                        if np_n:
                            st.session_state["proyectos"][np_n] = {"contexto_aprobado": "Proyecto base.", "archivos_pendientes": [], "avisos": [], "equipos": [], "pedidos_equipos": [], "continuidad": [], "arte": [], "planos": [], "plan_rodaje": [], "plantas_luces": [], "sonido_log": [], "tomas_dir": [], "personajes": [], "locaciones": [], "crew": [], "catering": [], "links": [], "presupuesto": [], "casting": [], "desglose": [], "comparador_rentals": [], "carrito_rentals": [], "directorio_rentals": [], "kanban": []}
                            guardar_y_recargar()
            l_proy = [p for p in st.session_state["proyectos"].keys() if p != "_CONFIG_"]
            if not l_proy: st.info("No hay desarrollos activos.")
            cols_grid = st.columns(2)
            for idx, proy in enumerate(l_proy):
                with cols_grid[idx % 2]:
                    with st.container(border=True):
                        st.markdown(f"<h3 style='margin-bottom:4px;'>{proy}</h3>", unsafe_allow_html=True)
                        st.caption(f"Crew: {len(st.session_state['proyectos'][proy].get('crew',[]))} | Equipos: {len(st.session_state['proyectos'][proy].get('equipos',[]))}")
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("Entrar", key=f"e_{proy}", use_container_width=True):
                            st.session_state["proyecto_activo"] = proy
                            st.session_state["menu_option"] = "Panel General"
                            st.session_state["ruta"] = "Proyecto"
                            st.rerun()

        with c_side:
            st.markdown("<div class='section-title'>AGENDA</div>", unsafe_allow_html=True)
            if st.button("Nuevo Recordatorio", type="secondary"): ventana_recordatorio((nivel_actual in ["jefe_supremo", "jefe"]), mis_datos['nombre'])
            for rec in reversed(st.session_state["proyectos"]["_CONFIG_"]["recordatorios"]):
                if rec["tipo"] == "Global (Toda la Productora)" or rec["autor"] == mis_datos["nombre"]:
                    with st.container(border=True):
                        st.markdown(f"<span style='color:#FBAF3B; font-size:11px; font-weight:700;'>{rec['fecha']}</span>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-weight:600; font-size:14px;'>{rec['titulo']}</div>", unsafe_allow_html=True)

    # --- SOCIAL (RED NATIVA CERO ERRORES) ---
    elif st.session_state["ruta"] == "Social":
        st.markdown("<h2 class='gradient-text'>Workspace Social</h2>", unsafe_allow_html=True)
        col_izq, col_centro, col_der = st.columns([1, 2.5, 1], gap="large")
        
        with col_izq:
            with st.container(border=True):
                f_usr = f"data:image/jpeg;base64,{mis_datos['foto']}" if mis_datos.get("foto") else "https://via.placeholder.com/150"
                st.markdown(f"<img src='{f_usr}' class='avatar-circle' style='width:60px; height:60px; margin-bottom:10px;'>", unsafe_allow_html=True)
                st.markdown(f"#### {mis_datos['nombre']}")
                st.caption(f"@{mis_datos.get('alias', us_act.split('@')[0])}")
                st.markdown(f"**Siguiendo:** {len(mis_datos.get('amigos', []))}")
                
        with col_centro:
            # Historias Interactuables
            st.markdown("<div class='section-title'>Historias 24h</div>", unsafe_allow_html=True)
            ahora = datetime.now(TZ_AR)
            h_activas = [h for h in st.session_state["proyectos"]["_CONFIG_"]["social_stories"] if (ahora - datetime.strptime(h["timestamp"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=TZ_AR)).total_seconds() < 86400]
            
            cols_hist = st.columns(min(len(h_activas) + 1, 6))
            with cols_hist[0]:
                if st.button("➕", help="Subir Historia"): ventana_historia(us_act)
            
            for idx, h in enumerate(reversed(h_activas)):
                if idx + 1 < 6:
                    with cols_hist[idx + 1]:
                        n_c = db_users[h['usuario']]['nombre'].split()[0]
                        with st.popover(f"⟡ {n_c}"):
                            st.markdown(f"<img src='data:image/jpeg;base64,{h['foto']}' style='width:100%; border-radius:12px;'>", unsafe_allow_html=True)
                            st.caption(f"Subido a las: {h['timestamp'].split()[1]}")
            st.divider()
            
            # Muro / Publicar
            st.markdown("<div class='section-title'>Muro</div>", unsafe_allow_html=True)
            with st.container(border=True):
                txt_post = st.text_area("¿Qué está pasando?", label_visibility="collapsed")
                img_post = st.file_uploader("Adjuntar foto", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
                if st.button("Publicar en Muro"):
                    if txt_post or img_post:
                        img_b64 = base64.b64encode(img_post.read()).decode('utf-8') if img_post else None
                        st.session_state["proyectos"]["_CONFIG_"]["social_posts"].insert(0, {"usuario": us_act, "texto": txt_post, "imagen": img_b64, "timestamp": obtener_hora_actual(), "likes": 0})
                        guardar_y_recargar()

            # Feed Formateado HTML Puro (Sin Sangrías)
            posts = st.session_state["proyectos"]["_CONFIG_"]["social_posts"]
            for i, p in enumerate(posts):
                ui = db_users[p["usuario"]]
                fi = f"data:image/jpeg;base64,{ui['foto']}" if ui.get("foto") else "https://via.placeholder.com/150"
                alias_u = ui.get("alias", p['usuario'].split('@')[0])
                html_post = f"""<div class="tweet-card">
<div class="tweet-header">
<img src="{fi}" class="tweet-avatar">
<div>
<p class="tweet-name">{ui['nombre']}</p>
<p class="tweet-handle">@{alias_u} • {p['timestamp']}</p>
</div>
</div>
{f"<p class='tweet-body'>{p['texto']}</p>" if p.get('texto') else ""}
{f"<img src='data:image/jpeg;base64,{p['imagen']}' class='tweet-img'>" if p.get('imagen') else ""}
<div class="tweet-actions">
<span>♡ {p.get('likes', 0)} Me gusta</span>
</div>
</div>"""
                st.markdown(html_post.replace('\n', ''), unsafe_allow_html=True)

        with col_der:
            st.markdown("<div class='section-title'>A QUIÉN SEGUIR</div>", unsafe_allow_html=True)
            for em, info in db_users.items():
                if em != us_act and em not in mis_datos.get("amigos", []):
                    with st.container(border=True):
                        st.markdown(f"<p style='margin:0; font-weight:600;'>{info['nombre']}</p><p style='margin:0; font-size:11px; color:#A1A1AA;'>{info['rol']}</p>", unsafe_allow_html=True)
                        if st.button("Seguir", key=f"seg_{em}", type="secondary"):
                            st.session_state["proyectos"]["_CONFIG_"]["usuarios"][us_act]["amigos"].append(em)
                            guardar_y_recargar()
            
            st.markdown("<br><div class='section-title'>SINTONÍA (SPOTIFY)</div>", unsafe_allow_html=True)
            amigos_seguir = mis_datos.get("amigos", []) + [us_act]
            for em in amigos_seguir:
                if em in db_users:
                    info = db_users[em]
                    if info.get("spotify") and "track/" in info["spotify"]:
                        with st.container(border=True):
                            st.markdown(f"<p style='margin:0; font-size:12px; font-weight:700;'>{info['nombre']}</p>", unsafe_allow_html=True)
                            tid = info["spotify"].split("track/")[1].split("?")[0]
                            components.iframe(f"https://open.spotify.com/embed/track/{tid}?utm_source=generator&theme=0", height=80)

    # --- MENSAJES (CHAT PRIVADO) ---
    elif st.session_state["ruta"] == "Mensajes":
        st.markdown("<h2 class='gradient-text'>Mensajería</h2>", unsafe_allow_html=True)
        col_list, col_chat = st.columns([1, 2.5], gap="large")
        if "chat_con" not in st.session_state: st.session_state["chat_con"] = None
        
        with col_list:
            st.markdown("<div class='section-title'>Contactos</div>", unsafe_allow_html=True)
            for em, info in db_users.items():
                if em != us_act:
                    with st.container(border=True):
                        st.markdown(f"**{info['nombre']}**<br><span style='font-size:11px;color:#A1A1AA;'>{info['rol']}</span>", unsafe_allow_html=True)
                        if st.button("Abrir", key=f"c_{em}", type="secondary"):
                            st.session_state["chat_con"] = em
                            st.rerun()

        with col_chat:
            if st.session_state["chat_con"]:
                d_inf = db_users[st.session_state["chat_con"]]
                st.markdown(f"### Chat con {d_inf['nombre']}")
                st.divider()
                historial = [m for m in st.session_state["proyectos"]["_CONFIG_"]["mensajes"] if (m["de"] == us_act and m["para"] == st.session_state["chat_con"]) or (m["de"] == st.session_state["chat_con"] and m["para"] == us_act)]
                
                with st.container(height=400):
                    if not historial: st.info("Escribe tu primer mensaje.")
                    for msg in historial:
                        if msg["de"] == us_act:
                            st.markdown(f"<div style='text-align: right;'><span style='background:#FBAF3B; color:#000; padding:10px 14px; border-radius:14px; display:inline-block; margin-bottom:4px; font-weight:600;'>{msg['texto']}</span><br><span style='font-size:10px; color:#52525B;'>{msg['fecha']}</span></div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div style='text-align: left;'><span style='background:#111; border:1px solid #333; padding:10px 14px; border-radius:14px; display:inline-block; margin-bottom:4px;'>{msg['texto']}</span><br><span style='font-size:10px; color:#52525B;'>{msg['fecha']}</span></div>", unsafe_allow_html=True)
                
                nm = st.chat_input("Mensaje...")
                if nm:
                    st.session_state["proyectos"]["_CONFIG_"]["mensajes"].append({"de": us_act, "para": st.session_state["chat_con"], "texto": nm, "fecha": datetime.now(TZ_AR).strftime("%H:%M")})
                    guardar_y_recargar()
            else: st.info("Selecciona un contacto.")

    # --- PERFIL Y ADMIN ---
    elif st.session_state["ruta"] == "Perfil":
        st.markdown("<div class='section-title'>AJUSTES</div>", unsafe_allow_html=True)
        t_per, t_cred, t_dir, t_adm = st.tabs(["Mi Perfil", "Credencial", "Directorio", "Admin"])
        
        with t_per:
            c_img, c_form = st.columns([1, 2.5])
            with c_img:
                st.markdown("#### Avatar")
                f_s = f"data:image/jpeg;base64,{mis_datos['foto']}" if mis_datos.get("foto") else "https://via.placeholder.com/150"
                st.markdown(f"<img src='{f_s}' class='avatar-circle' style='width:120px;height:120px;'>", unsafe_allow_html=True)
                nf = st.file_uploader("Actualizar", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
                if nf and st.button("Guardar"): db_users[us_act]["foto"] = base64.b64encode(nf.read()).decode('utf-8'); guardar_y_recargar()
                st.markdown("---")
                st.metric("Nivel", mis_datos['nivel'].capitalize())

            with c_form:
                with st.form("f_p"):
                    c1, c2 = st.columns(2)
                    al = c1.text_input("Alias / Arroba (@)", value=mis_datos.get("alias", us_act.split("@")[0]))
                    e = c2.text_input("Edad", value=mis_datos.get("edad", ""))
                    rf = st.text_input("Especialidad", value=mis_datos.get("roles_fav", ""))
                    pf = st.text_input("Portfolio", value=mis_datos.get("portfolio", ""))
                    sp = st.text_input("Track Spotify (Pestaña Social)", value=mis_datos.get("spotify", ""), placeholder="https://open.spotify.com/track/...")
                    spc = st.text_area("Notas", value=mis_datos.get("specs", ""))
                    if st.form_submit_button("Sincronizar"):
                        db_users[us_act].update({"alias": al, "edad": e, "roles_fav": rf, "portfolio": pf, "spotify": sp, "specs": spc}); guardar_y_recargar()
            st.divider()
            if st.button("Cerrar Sesión", type="secondary"): st.session_state["usuario_logueado"] = None; st.session_state["ruta"] = "Inicio"; st.rerun()

        with t_cred:
            qr_b64 = generar_qr_base64(f"ID:{mis_datos.get('credencial')}|N:{mis_datos['nombre']}")
            st.markdown(f"""
                <div class="credencial-feten">
                    <img src="{LOGO_URL}" class="credencial-logo-img"><br>
                    <img src="{f_s}" class="credencial-img">
                    <h2 class="credencial-name">{mis_datos['nombre']}</h2>
                    <p class="credencial-role">{mis_datos['rol']}</p>
                    <div class="qr-box"><img src="data:image/png;base64,{qr_b64}" width="120"></div>
                    <div class="credencial-id-box"><span class="credencial-id">ID: {mis_datos.get('credencial')}</span></div>
                </div>
            """, unsafe_allow_html=True)

        with t_dir:
            bq = st.text_input("Buscar miembros...")
            for em, info in db_users.items():
                if info["estado"] == "Aprobado" and (bq.lower() in info["nombre"].lower() or bq.lower() in info["rol"].lower()):
                    with st.container(border=True):
                        colD1, colD2 = st.columns([1, 8])
                        with colD1: st.markdown(f"<img src='data:image/jpeg;base64,{info.get('foto','')}' class='avatar-circle' style='width:45px;height:45px;'>", unsafe_allow_html=True)
                        with colD2: st.markdown(f"<h4 style='margin:0;'>{info['nombre']} <span style='color:#FBAF3B;font-size:12px;'>({info['rol']})</span></h4>", unsafe_allow_html=True)

        with t_adm:
            if rol_actual == "Super Admin":
                mapa = {"Super Admin": "jefe_supremo", "Producción": "jefe", "Dirección": "jefe", "Dirección de Fotografía": "jefe", "Dirección de Arte": "jefe", "Director de Sonido": "jefe", "Asistente de Sonido": "asistente", "Guion": "jefe", "Continuidad": "jefe", "Invitado": "lectura"}
                for em_usr, dt_usr in db_users.items():
                    with st.container(border=True):
                        c1, c2, c3, c4 = st.columns([2, 1.5, 1.5, 1])
                        c1.markdown(f"**{dt_usr['nombre']}**<br><span style='font-size:12px;'>{em_usr}</span>", unsafe_allow_html=True)
                        est = c2.selectbox("Estado", ["Aprobado", "Pendiente"], index=0 if dt_usr.get("estado") == "Aprobado" else 1, key=f"e_{em_usr}")
                        rol = c3.selectbox("Rol", list(mapa.keys()), index=list(mapa.keys()).index(dt_usr["rol"]) if dt_usr["rol"] in mapa else 9, key=f"r_{em_usr}")
                        if c4.button("Aplicar", key=f"b_{em_usr}"): db_users[em_usr].update({"estado": est, "rol": rol, "nivel": mapa[rol]}); guardar_y_recargar()
                st.divider()
                st.markdown("### Tickets de Soporte")
                tks = st.session_state["proyectos"]["_CONFIG_"]["tickets_soporte"]
                for i, tk in enumerate(reversed(tks)):
                    with st.container(border=True):
                        st.markdown(f"**{tk['asunto']}** ({tk['fecha']}) - De: {tk['usuario']}")
                        st.write(tk['desc'])
                        if tk['estado'] == "Pendiente":
                            if st.button("Resuelto", key=f"tk_{i}"): st.session_state["proyectos"]["_CONFIG_"]["tickets_soporte"][len(tks)-1-i]["estado"] = "Resuelto"; guardar_y_recargar()
                        else: st.success("Resuelto")
            else: st.warning("Solo Super Admins.")

    # --- PROYECTO (HERRAMIENTAS INTACTAS) ---
    elif st.session_state["ruta"] == "Proyecto":
        pr = st.session_state["proyecto_activo"]
        pd_proy = st.session_state["proyectos"][pr]
        
        st.markdown(f"<h2 class='gradient-text' style='margin-bottom: 24px;'>{pr.upper()}</h2>", unsafe_allow_html=True)
        col_nav, col_content = st.columns([1, 3.5], gap="large")
        
        o_nav = ["Panel General", "Tablero Kanban", "Asistente IA"]
        i_nav = ["grid", "kanban", "lightning-charge"]
        if nivel_actual != "lectura": o_nav.append("Solicitar a Prod."); i_nav.append("send")
        o_nav.extend(["Bandeja Prod.", "Rentals IA", "Archivos", "Tablón", "Enlaces", "Permisos", "Presupuesto", "Scouting", "Base Crew", "Casting", "Catering", "Desglose", "Laboratorio Guion", "Inventario", "Plan Rodaje", "Monitor DIR", "Luces (Canvas)", "Ref. IA", "Arte & Vestuario", "Log Sonido", "Raccord", "IA: Moodboard Dinámico", "IA: Auditor Anacronismos", "IA: Utilería DIY", "IA: Analizador Espectral", "IA: Matriz de Ruido", "IA: Sugerente Foley"])
        i_nav.extend(["inbox", "shop", "folder2-open", "megaphone", "link-45deg", "shield-lock", "wallet2", "geo-alt", "people", "person-video", "cup-hot", "card-text", "pen", "box", "calendar-event", "camera-reels", "lightbulb", "cpu", "palette", "headphones", "film", "magic", "shield-check", "hammer", "soundwave", "volume-up", "mic"])
        
        nf, inf = [], []
        for o, i in zip(o_nav, i_nav):
            if rol_actual == "Super Admin": nf.append(o); inf.append(i)
            elif rol_actual == "Producción" and o in ["Panel General", "Tablero Kanban", "Asistente IA", "Solicitar a Prod.", "Presupuesto", "Bandeja Prod.", "Scouting", "Base Crew", "Casting", "Catering", "Rentals IA", "Archivos", "Tablón", "Enlaces"]: nf.append(o); inf.append(i)
            elif rol_actual == "Guion" and o in ["Panel General", "Tablero Kanban", "Asistente IA", "Solicitar a Prod.", "Desglose", "Laboratorio Guion", "Archivos", "Tablón", "Enlaces"]: nf.append(o); inf.append(i)
            elif "Dirección" in rol_actual and rol_actual not in ["Dirección de Arte", "Dirección de Fotografía"] and o in ["Panel General", "Tablero Kanban", "Asistente IA", "Solicitar a Prod.", "Casting", "Plan Rodaje", "Monitor DIR", "Archivos", "Tablón", "Enlaces", "Inventario"]: nf.append(o); inf.append(i)
            elif rol_actual == "Dirección de Fotografía" and o in ["Panel General", "Tablero Kanban", "Asistente IA", "Solicitar a Prod.", "Luces (Canvas)", "Ref. IA", "Inventario", "Archivos", "Tablón", "Enlaces"]: nf.append(o); inf.append(i)
            elif rol_actual == "Dirección de Arte" and o in ["Panel General", "Tablero Kanban", "Asistente IA", "Solicitar a Prod.", "Arte & Vestuario", "Inventario", "Archivos", "Tablón", "Enlaces", "IA: Moodboard Dinámico", "IA: Auditor Anacronismos", "IA: Utilería DIY"]: nf.append(o); inf.append(i)
            elif "Sonido" in rol_actual and o in ["Panel General", "Tablero Kanban", "Asistente IA", "Solicitar a Prod.", "Log Sonido", "Inventario", "Archivos", "Tablón", "Enlaces", "IA: Analizador Espectral", "IA: Matriz de Ruido", "IA: Sugerente Foley"]: nf.append(o); inf.append(i)
            elif rol_actual == "Continuidad" and o in ["Panel General", "Tablero Kanban", "Asistente IA", "Solicitar a Prod.", "Raccord", "Archivos", "Tablón", "Enlaces"]: nf.append(o); inf.append(i)
            elif nivel_actual == "lectura" and o in ["Panel General", "Tablero Kanban", "Asistente IA", "Archivos", "Tablón", "Enlaces"]: nf.append(o); inf.append(i)

        if not nf: nf = ["Panel General"]; inf = ["grid"]
        idx_def = nf.index(st.session_state["menu_option"]) if st.session_state.get("menu_option") in nf else 0
            
        with col_nav:
            s_e = option_menu(menu_title="HERRAMIENTAS", options=nf, icons=inf, default_index=idx_def, styles={"container": {"padding": "10px", "background-color": "#0A0A0B", "border-radius": "16px", "border": "1px solid #1C1C1F"}, "icon": {"color": "#888", "font-size": "15px"}, "menu-title": {"color": "#666", "font-size": "11px", "letter-spacing": "2px", "font-weight": "700"}, "nav-link": {"font-size": "13px", "text-align": "left", "margin": "4px 0", "color": "#CCC", "border-radius": "8px", "padding": "10px"}, "nav-link-selected": {"background-color": "#1A1A1A", "color": "#FAFAFA", "font-weight": "600", "border-left": "3px solid #FBAF3B"}})
            st.session_state["menu_option"] = s_e
        
        with col_content:
            if s_e == "Panel General":
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Nómina", len(pd_proy.get("crew", [])))
                c2.metric("Lugares", len(pd_proy.get("locaciones", [])))
                c3.metric("Fierros", len(pd_proy.get("equipos", [])))
                c4.metric("Tickets", len(pd_proy.get("pedidos_equipos", [])))
                st.divider()
                st.markdown("### Generador de Call Sheet (IA)")
                if st.button("Emitir Plan Maestro"):
                    try:
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        prompt = f"Proyecto: {pr}. Datos: Avisos {pd_proy.get('avisos',[])}, Locaciones {pd_proy.get('locaciones',[])}. Redactá un Call Sheet."
                        st.markdown(f"<div style='background:#111; padding:20px; border-radius:12px; border:1px solid #222;'>{genai.GenerativeModel('gemini-1.5-flash').generate_content(prompt).text}</div>", unsafe_allow_html=True)
                    except: st.error("Falta API Key Gemini.")

            elif s_e == "Tablero Kanban":
                c1, c2 = st.columns([2.5, 1])
                with c1: st.markdown("<h2>Gestor de Tareas</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("Crear Tarea"): ventana_kanban(pr, mis_datos['nombre'])
                st.divider()
                colP, colPr, colL = st.columns(3)
                with colP:
                    st.markdown("#### Pendiente")
                    for i, t in enumerate(pd_proy["kanban"]):
                        if t["estado"] == "Pendiente":
                            with st.container(border=True): 
                                st.write(f"**{t['tarea']}**")
                                if st.button("Mover ➔", key=f"k1_{i}", type="secondary"): pd_proy["kanban"][i]["estado"] = "En Proceso"; guardar_y_recargar()
                with colPr:
                    st.markdown("#### En Proceso")
                    for i, t in enumerate(pd_proy["kanban"]):
                        if t["estado"] == "En Proceso":
                            with st.container(border=True): 
                                st.write(f"**{t['tarea']}**")
                                if st.button("Finalizar", key=f"k2_{i}"): pd_proy["kanban"][i]["estado"] = "Completado"; guardar_y_recargar()
                with colL:
                    st.markdown("#### Listo")
                    for t in [t for t in pd_proy["kanban"] if t["estado"] == "Completado"]:
                        with st.container(border=True): st.write(f"~~{t['tarea']}~~")

            elif s_e == "Asistente IA":
                st.markdown("<h2>Comando de IA</h2>", unsafe_allow_html=True)
                try:
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    m = st.chat_input("Escribe una instrucción...")
                    if m:
                        st.chat_message("user").write(m)
                        st.chat_message("assistant").write(genai.GenerativeModel('gemini-1.5-flash').generate_content(f"Sos FTN AI. Hablás con: {mis_datos['nombre']}. Usuario: {m}").text)
                except: st.error("Falta API Key.")

            elif s_e == "Solicitar a Prod.":
                if st.button("Levantar Ticket"): ventana_pedido(pr, rol_actual)
                for ped in [p for p in pd_proy.get("pedidos_equipos", []) if p["area"] == rol_actual or rol_actual == "Super Admin"]:
                    with st.container(border=True): st.write(f"**{ped['item']}** — {ped['notas']} ({ped['estado']})")

            elif s_e == "Bandeja Prod.":
                for i, ped in enumerate(pd_proy["pedidos_equipos"]):
                    if ped['estado'] == "Pendiente":
                        with st.container(border=True):
                            st.write(f"**{ped['area']}:** {ped['item']}")
                            c1, c2 = st.columns(2)
                            if c1.button("Aprobar", key=f"ap_{i}"): pd_proy["equipos"].append({"area": ped['area'], "item": ped['item'], "cant": 1, "tipo": "A Confirmar", "rental": "A Definir"}); pd_proy["pedidos_equipos"][i]["estado"] = "Aprobado"; guardar_y_recargar()
                            if c2.button("Denegar", key=f"re_{i}", type="secondary"): pd_proy["pedidos_equipos"][i]["estado"] = "Rechazado"; guardar_y_recargar()

            elif s_e == "Rentals IA":
                c1, c2, c3 = st.columns(3)
                c1.button("Proveedor", on_click=lambda: ventana_nuevo_rental(pr))
                c2.button("Scanner IA", on_click=lambda: ventana_comparador_rental(pr))
                c3.button("Purga", on_click=lambda: ventana_vaciar_comparador(pr), type="secondary")
                st.divider()
                if pd_proy.get("carrito_rentals"):
                    if st.button("Checkout"): ventana_checkout(pr)
                    for i, item in enumerate(pd_proy["carrito_rentals"]):
                        with st.container(border=True):
                            st.write(f"{item['nombre']} - ${item['precio']}")
                            if st.button("Quitar", key=f"q_{i}"): pd_proy["carrito_rentals"].pop(i); guardar_y_recargar()
                st.markdown("### Base Analizada")
                for i, r in enumerate(pd_proy.get("comparador_rentals", [])):
                    with st.container(border=True):
                        st.write(f"{r['nombre']} - ${r['precio']}")
                        if st.button("Añadir", key=f"add_{i}"): pd_proy["carrito_rentals"].append(r); guardar_y_recargar()

            elif s_e == "Archivos":
                a = st.file_uploader("Documento (.txt)")
                if a and st.button("Subir"): pd_proy["archivos_pendientes"].append({"autor": mis_datos['nombre'], "nombre": a.name, "texto": a.getvalue().decode('utf-8')}); guardar_y_recargar()

            elif s_e == "Tablón":
                if st.button("Publicar"): ventana_aviso(pr, mis_datos['nombre'], pd_proy["locaciones"])
                for a in reversed(pd_proy["avisos"]): st.write(f"**{a['autor']}**: {a.get('texto', 'Citación')}")

            elif s_e == "Enlaces":
                if st.button("Cargar URL"): ventana_link(pr)
                for l in pd_proy["links"]: st.write(f"[{l['titulo']}]({l['url']})")

            elif s_e == "Permisos":
                st.info("Centralizado en Perfil > Admin")

            elif s_e == "Presupuesto":
                if st.button("Asentar Gasto"): ventana_presupuesto(pr)
                if pd_proy.get("presupuesto"):
                    df = pd.DataFrame(pd_proy["presupuesto"])
                    st.metric("Total", f"${df['costo'].sum():,.2f}")
                    st.plotly_chart(px.pie(df, values='costo', names='area', template="plotly_dark"))

            elif s_e == "Scouting":
                if st.button("Registrar Locación"): ventana_locacion(pr)
                for l in pd_proy.get("locaciones", []): st.write(f"**{l['nombre']}**: {l['direccion']}")

            elif s_e == "Base Crew":
                if st.button("Contratar"): ventana_crew(pr)
                if pd_proy.get("crew"): st.dataframe(pd.DataFrame(pd_proy["crew"]))

            elif s_e == "Casting":
                if st.button("Añadir Actor"): ventana_casting(pr)
                for a in pd_proy["casting"]: st.write(f"**{a['actor']}** ({a['personaje']})")

            elif s_e == "Catering":
                if st.button("Añadir Dieta"): ventana_catering(pr)
                for p in pd_proy["catering"]: st.write(f"**{p['nombre']}**: {p['dieta']}")

            elif s_e == "Desglose":
                if st.button("Extraer Escena"): ventana_desglose(pr)
                for d in pd_proy["desglose"]: st.write(f"**ESC {d['escena']}**: {d['desc']}")

            elif s_e == "Laboratorio Guion":
                if st.button("Crear Personaje"): ventana_personaje(pr)
                for p in pd_proy.get("personajes", []): st.write(f"**{p['nombre']}**: {p['rol']}")

            elif s_e == "Inventario":
                if st.button("Agregar a Base"): ventana_equipo(pr, rol_actual)
                for e in pd_proy["equipos"]: st.write(f"**{e['cant']}x {e['item']}**")

            elif s_e == "Plan Rodaje":
                if st.button("Nuevo Bloque"): ventana_cronograma(pr)
                for a in pd_proy["plan_rodaje"]: st.write(f"**{a['hora']}**: {a['actividad']}")

            elif s_e == "Monitor DIR":
                c1, c2 = st.columns(2)
                c1.button("Shot List", on_click=lambda: ventana_plano(pr))
                c2.button("Loguear Toma", on_click=lambda: ventana_toma_dir(pr))
                for t in pd_proy["tomas_dir"]: st.write(f"**ESC {t['escena']} T {t['toma']}**: {t['evaluacion']}")

            elif s_e == "Luces (Canvas)":
                modo = st.selectbox("Trazado", ["freedraw", "line", "rect", "circle", "transform"])
                st_canvas(stroke_color="#FFD700", background_color="#111", width=330, height=350, drawing_mode=modo, key="cv_l")

            elif s_e == "Ref. IA":
                try:
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    m = st.chat_input("Prompt visual...")
                    if m: st.info(genai.GenerativeModel('gemini-1.5-flash').generate_content(f"Sos DF: {m}").text)
                except: st.error("Falta API Key.")

            elif s_e == "Arte & Vestuario":
                if st.button("Añadir Objeto"): ventana_arte(pr)
                for i in pd_proy["arte"]: st.write(f"**{i['objeto']}** ({i['estado']})")

            elif s_e == "Log Sonido":
                if st.button("Registrar"): ventana_sonido(pr)
                for s in pd_proy["sonido_log"]: st.write(f"**ESC {s['escena']} T {s['toma']}**")

            elif s_e == "Raccord":
                if st.button("Asentar"): ventana_continuidad(pr)
                for n in pd_proy["continuidad"]: st.write(f"**ESC {n['escena']} T {n['toma']}**: {n['detalle']}")

            elif s_e == "IA: Moodboard Dinámico":
                im = st.file_uploader("Foto Ref", type=["jpg", "png"])
                if im and st.button("Generar"):
                    try:
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        st.info(genai.GenerativeModel('gemini-1.5-flash').generate_content(["Dame 4 colores HEX", Image.open(im)]).text)
                    except: pass

            elif s_e == "IA: Auditor Anacronismos":
                ep = st.text_input("Época")
                iu = st.file_uploader("Objeto", type=["jpg", "png"])
                if iu and st.button("Auditar"):
                    try:
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        st.info(genai.GenerativeModel('gemini-1.5-flash').generate_content([f"Es anacrónico para {ep}?", Image.open(iu)]).text)
                    except: pass

            elif s_e == "IA: Utilería DIY":
                od = st.text_input("Objeto a fabricar")
                if od and st.button("Guía"):
                    try:
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        st.info(genai.GenerativeModel('gemini-1.5-flash').generate_content(f"Guía para fabricar {od} barato").text)
                    except: pass

            elif s_e == "IA: Analizador Espectral":
                af = st.file_uploader("Audio", type=["wav", "mp3"])
                if af and st.button("Render"):
                    y, sr = librosa.load(af, sr=None)
                    D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
                    fig, ax = plt.subplots()
                    librosa.display.specshow(D, y_axis='log', ax=ax)
                    st.pyplot(fig)

            elif s_e == "IA: Matriz de Ruido":
                fr = st.selectbox("Fuente", ["Tráfico", "Aviones"])
                d = st.number_input("Distancia", value=20)
                if st.button("Plan"):
                    try:
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        st.info(genai.GenerativeModel('gemini-1.5-flash').generate_content(f"Aislamiento para {fr} a {d}m").text)
                    except: pass

            elif s_e == "IA: Sugerente Foley":
                ac = st.text_input("Acción")
                if ac and st.button("Lista"):
                    try:
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        st.info(genai.GenerativeModel('gemini-1.5-flash').generate_content(f"Foley para: {ac}").text)
                    except: pass
