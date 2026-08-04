import streamlit as st
import streamlit.components.v1 as components
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
from datetime import datetime, date, timedelta
import random
import time
import numpy as np
import matplotlib.pyplot as plt
import librosa
import scipy.signal

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Fetén Workspace Pro", page_icon="✦", layout="wide", initial_sidebar_state="collapsed")

LOGO_URL = "https://i.supaimg.com/4a90693e-1b41-4313-8203-f60c8b81825f/da7de7fd-3ded-4499-b3f4-790424f0dc5a.png"

# --- 2. DISEÑO UI/UX "SAAS OBSIDIAN PRO" (LINEAR/VERCEL STYLE) ---
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

    /* Logo PNG sin distorsiones */
    .logo-img { display: block; max-width: 100%; height: auto; }

    /* Tarjetas Modulares SaaS */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #0A0A0B !important;
        border: 1px solid #1C1C1F !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important;
        transition: all 0.3s ease !important;
        margin-bottom: 16px !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: rgba(251, 175, 59, 0.3) !important;
        box-shadow: 0 8px 30px rgba(251, 175, 59, 0.08) !important;
    }
    
    /* Títulos con Gradiente Premium */
    .gradient-text {
        background: linear-gradient(135deg, #FFFFFF 0%, #FBAF3B 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: -0.03em;
    }
    h1, h2 { font-weight: 800 !important; letter-spacing: -0.02em !important; color: #FAFAFA !important; }
    h3, h4 { color: #D4D4D8 !important; font-weight: 600 !important; letter-spacing: -0.01em !important; }
    
    /* Títulos de Sección Pequeños */
    .section-title {
        color: #A1A1AA; font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 16px;
    }

    /* Inputs y Formularios Modernos */
    .stTextInput input, .stSelectbox select, .stNumberInput input, .stDateInput input, .stTimeInput input, .stTextArea textarea, .stChatInput input {
        background-color: #0E0E11 !important; 
        border: 1px solid #27272A !important; 
        color: #FAFAFA !important;
        border-radius: 10px !important; 
        padding: 12px 16px !important; 
        font-weight: 400 !important;
        transition: all 0.2s ease !important;
    }
    .stTextInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus { 
        border-color: #FBAF3B !important; 
        box-shadow: 0 0 0 1px #FBAF3B !important; 
    }
    
    /* Botones de Acción (Call to Action) */
    .stButton button {
        background: linear-gradient(135deg, #FBAF3B 0%, #D97706 100%) !important; 
        border: none !important; 
        color: #050505 !important;
        border-radius: 10px !important; 
        font-weight: 700 !important; 
        padding: 0.6rem 1rem !important; 
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    .stButton button:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 20px rgba(251, 175, 59, 0.3) !important; }
    .stButton button p { color: #050505 !important; font-weight: 700 !important; margin: 0; }
    
    /* Botones Secundarios */
    [data-testid="stBaseButton-secondary"] { 
        background: #0A0A0B !important; 
        border: 1px solid #27272A !important; 
        color: #A1A1AA !important; 
        box-shadow: none !important;
    }
    [data-testid="stBaseButton-secondary"]:hover { border-color: #52525B !important; color: #FAFAFA !important; }
    [data-testid="stBaseButton-secondary"] p { color: inherit !important; }

    /* Avatares */
    .avatar-circle { border-radius: 50%; object-fit: cover; border: 2px solid #FBAF3B; box-shadow: 0 4px 10px rgba(180, 113, 63, 0.3); }

    /* Historias de Red Social */
    .story-circle {
        border-radius: 50%; object-fit: cover; border: 3px solid #FBAF3B; padding: 2px;
        width: 64px; height: 64px; box-shadow: 0 4px 12px rgba(251, 175, 59, 0.2);
    }
    
    /* Credencial VIP rediseñada (Clean UI) */
    .credencial-feten {
        background-color: #0A0A0B;
        border: 1px solid #1C1C1F;
        border-radius: 16px; padding: 30px; width: 100%; max-width: 380px; margin: 0 auto; text-align: center;
        position: relative; overflow: hidden;
    }
    .credencial-feten::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px;
        background: linear-gradient(90deg, #FBAF3B, #B4713F);
    }
    .credencial-img { width: 100px; height: 100px; border-radius: 50%; border: 2px solid #FBAF3B; margin-bottom: 15px; object-fit: cover;}
    .credencial-name { font-size: 20px; font-weight: 700; margin: 0; color: #FAFAFA !important;}
    .credencial-role { font-size: 12px; color: #FBAF3B !important; margin-top: 4px; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 1px;}
    .qr-box { background: white; padding: 10px; border-radius: 8px; display: inline-block; margin-bottom: 15px;}
    .credencial-id-box { background: #111; padding: 10px; border-radius: 8px; border: 1px solid #222; }
    .credencial-id { font-family: 'Courier New', monospace; font-weight: bold; font-size: 14px; letter-spacing: 2px; color: #FBAF3B !important;}

    /* Métricas Dashboard */
    [data-testid="stMetricValue"] { color: #FAFAFA !important; font-size: 2.2rem !important; font-weight: 800 !important; letter-spacing: -1px; }
    [data-testid="stMetricLabel"] { color: #A1A1AA !important; text-transform: uppercase !important; letter-spacing: 1px !important; font-size: 0.75rem !important; font-weight: 600 !important; }

    /* Ocultar etiquetas de métricas */
    [data-testid="stMetricDelta"] { display: none; }

    /* Responsive */
    @media (max-width: 768px) {
        [data-testid="column"] { width: 100% !important; flex: 100% !important; min-width: 100% !important; margin-bottom: 10px !important; }
        .block-container { padding-left: 1rem !important; padding-right: 1rem !important; padding-top: 1.5rem !important; }
    }
    </style>
""", unsafe_allow_html=True)

ARCHIVO_BD = "ftn_database.json"

# --- 3. FUNCIONES AUXILIARES Y BASE DE DATOS ---
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
                if "_CONFIG_" not in data_cargada:
                    data_cargada["_CONFIG_"] = {
                        "usuarios": {
                            "lau@admin.com": {
                                "nombre": "Lau (Admin)", "pass": "1234", "rol": "Super Admin", "nivel": "jefe_supremo", "estado": "Aprobado",
                                "foto": "", "credencial": "FTN-0001", "edad": "", "roles_fav": "Directora / Productora", "dieta": "Ninguna", "specs": "", "cv": "", "portfolio": "", "acceso_rapido": "Panel General", "spotify": ""
                            }
                        }, "recordatorios": [], "notificaciones": [], "mensajes": [], "tickets_soporte": [], "social_posts": [], "social_stories": []
                    }
                # Asegurar que existan las nuevas bases
                if "mensajes" not in data_cargada["_CONFIG_"]: data_cargada["_CONFIG_"]["mensajes"] = []
                if "tickets_soporte" not in data_cargada["_CONFIG_"]: data_cargada["_CONFIG_"]["tickets_soporte"] = []
                if "social_posts" not in data_cargada["_CONFIG_"]: data_cargada["_CONFIG_"]["social_posts"] = []
                if "social_stories" not in data_cargada["_CONFIG_"]: data_cargada["_CONFIG_"]["social_stories"] = []
                if "notificaciones" not in data_cargada["_CONFIG_"]: data_cargada["_CONFIG_"]["notificaciones"] = []
                
                claves_necesarias = [
                    "archivos_pendientes", "avisos", "equipos", "pedidos_equipos", "continuidad", 
                    "arte", "planos", "plan_rodaje", "plantas_luces", "sonido_log", "tomas_dir", 
                    "personajes", "locaciones", "crew", "catering", "links", "presupuesto", 
                    "casting", "desglose", "comparador_rentals", "carrito_rentals", "directorio_rentals", "kanban"
                ]
                for nombre_proy, datos_proy in data_cargada.items():
                    if nombre_proy == "_CONFIG_": 
                        for email_u, info_u in datos_proy.get("usuarios", {}).items():
                            if "estado" not in info_u: info_u["estado"] = "Aprobado"
                            if "credencial" not in info_u: info_u["credencial"] = f"FTN-{random.randint(1000, 9999)}"
                            if "acceso_rapido" not in info_u: info_u["acceso_rapido"] = "Panel General"
                            if "spotify" not in info_u: info_u["spotify"] = ""
                        continue
                    if "contexto_aprobado" not in datos_proy: datos_proy["contexto_aprobado"] = "Proyecto actualizado."
                    for clave in claves_necesarias:
                        if clave not in datos_proy: datos_proy[clave] = []
                st.session_state["proyectos"] = data_cargada
        else:
            st.session_state["proyectos"] = {
                "_CONFIG_": {
                    "usuarios": {
                        "lau@admin.com": {
                            "nombre": "Lau (Admin)", "pass": "1234", "rol": "Super Admin", "nivel": "jefe_supremo", "estado": "Aprobado",
                            "foto": "", "credencial": "FTN-0001", "edad": "", "roles_fav": "Super Admin", "dieta": "", "specs": "", "cv": "", "portfolio": "", "acceso_rapido": "Panel General", "spotify": ""
                        }
                    }, "recordatorios": [], "notificaciones": [], "mensajes": [], "tickets_soporte": [], "social_posts": [], "social_stories": []
                }
            }

inicializar_bd()

if "ruta" not in st.session_state: st.session_state["ruta"] = "Inicio"
if "proyecto_activo" not in st.session_state: st.session_state["proyecto_activo"] = None
if "menu_option" not in st.session_state: st.session_state["menu_option"] = "Panel General"

# --- 4. MODALES DE GESTIÓN GLOBALES ---
@st.dialog("◈ Reportar un Problema (Soporte Técnico)")
def ventana_soporte(usuario):
    asunto = st.text_input("Asunto del reporte")
    desc = st.text_area("Descripción detallada del problema o bug")
    if st.button("Enviar Ticket a Soporte", use_container_width=True):
        if asunto and desc:
            # Solución del error de fecha
            st.session_state["proyectos"]["_CONFIG_"]["tickets_soporte"].append({
                "usuario": usuario, "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"), "asunto": asunto, "desc": desc, "estado": "Pendiente"
            })
            guardar_y_recargar()

@st.dialog("◈ Subir Historia (24h)")
def ventana_historia(usuario):
    foto_hist = st.file_uploader("Foto para tu historia", type=["jpg", "png", "jpeg"])
    if st.button("Publicar Historia", use_container_width=True):
        if foto_hist:
            b64 = base64.b64encode(foto_hist.read()).decode('utf-8')
            st.session_state["proyectos"]["_CONFIG_"]["social_stories"].append({
                "usuario": usuario, "foto": b64, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            guardar_y_recargar()

# --- MODALES DEL PROYECTO ---
@st.dialog("◈ Nueva Tarea Kanban")
def ventana_kanban(proyecto, autor):
    tarea = st.text_input("Descripción de la Tarea")
    estado = st.selectbox("Estado Inicial", ["Pendiente", "En Proceso", "Completado"])
    if st.button("Agregar al Tablero", use_container_width=True):
        if tarea:
            st.session_state["proyectos"][proyecto]["kanban"].append({"tarea": tarea, "estado": estado, "autor": autor})
            guardar_y_recargar()

@st.dialog("◈ Nuevo Recordatorio Global")
def ventana_recordatorio(es_admin, autor):
    titulo = st.text_input("Título de la Tarea")
    fecha = st.date_input("Fecha Límite")
    tipo = st.selectbox("Visibilidad", ["Privado", "Global (Toda la Productora)"]) if es_admin else "Privado"
    if st.button("Guardar Tarea", use_container_width=True):
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
        loc_elegida = st.selectbox("Locación", nombres_locs) if nombres_locs else st.text_input("Locación (Libre)")
        notas_citacion = st.text_area("Notas extras")
        if st.button("Publicar Citación", use_container_width=True):
            st.session_state["proyectos"][proyecto]["avisos"].append({
                "tipo": "citacion", "autor": autor, "fecha": str(fecha), "hora": str(hora), "locacion": loc_elegida, "notas": notas_citacion
            })
            guardar_y_recargar()

@st.dialog("⌖ Registrar Locación")
def ventana_locacion(proyecto):
    nombre = st.text_input("Nombre / Referencia")
    direccion = st.text_input("Dirección Exacta")
    c1, c2 = st.columns(2)
    lat = c1.number_input("Latitud", format="%.6f", value=0.0)
    lon = c2.number_input("Longitud", format="%.6f", value=0.0)
    permisos = st.selectbox("Permisos", ["En gestión", "Aprobado", "No requiere"])
    if st.button("Guardar Locación", use_container_width=True):
        if nombre:
            st.session_state["proyectos"][proyecto]["locaciones"].append({"nombre": nombre, "direccion": direccion, "lat": lat, "lon": lon, "permisos": permisos})
            guardar_y_recargar()

@st.dialog("◈ Fichar Miembro del Crew")
def ventana_crew(proyecto):
    nombre = st.text_input("Nombre Completo")
    c1, c2 = st.columns(2)
    rol = c1.text_input("Rol asignado")
    telefono = c2.text_input("Teléfono")
    obra_social = st.text_input("Seguro / ART")
    if st.button("Guardar Ficha", use_container_width=True):
        if nombre:
            st.session_state["proyectos"][proyecto]["crew"].append({"nombre": nombre, "rol": rol, "telefono": telefono, "obra_social": obra_social})
            guardar_y_recargar()

@st.dialog("◈ Planilla de Dietas")
def ventana_catering(proyecto):
    nombre = st.text_input("Nombre Completo")
    dieta = st.selectbox("Restricción", ["Ninguna", "Vegetariano", "Vegano", "Celíaco", "Diabético"])
    alergias = st.text_area("Alergias específicas (Opcional)")
    if st.button("Guardar Preferencia", use_container_width=True):
        if nombre:
            st.session_state["proyectos"][proyecto]["catering"].append({"nombre": nombre, "dieta": dieta, "alergias": alergias})
            guardar_y_recargar()

@st.dialog("✉ Pedido de Equipamiento")
def ventana_pedido(proyecto, area):
    item_nombre = st.text_input("Ítem / Equipo")
    justificacion = st.text_area("Justificación")
    prioridad = st.selectbox("Nivel de Urgencia", ["Baja", "Media", "Alta Prioridad"])
    if st.button("Enviar Ticket", use_container_width=True):
        if item_nombre:
            st.session_state["proyectos"][proyecto]["pedidos_equipos"].append({"area": area, "item": item_nombre, "notas": justificacion, "prioridad": prioridad, "estado": "Pendiente"})
            st.session_state["proyectos"]["_CONFIG_"]["notificaciones"].append(f"Ticket nuevo en {proyecto}: {item_nombre} ({prioridad})")
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

@st.dialog("⟡ Nota de Raccord")
def ventana_continuidad(proyecto):
    c1, c2 = st.columns(2)
    escena = c1.text_input("ESC N°")
    toma = c2.text_input("TOMA N°")
    detalle = st.text_area("Detalle Técnico de Continuidad")
    if st.button("Guardar Registro", use_container_width=True):
        if escena and detalle:
            st.session_state["proyectos"][proyecto]["continuidad"].append({"escena": escena, "toma": toma, "detalle": detalle})
            guardar_y_recargar()

@st.dialog("◈ Archivo de Arte")
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

@st.dialog("◈ Diagramar Plano")
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

@st.dialog("◈ Log de Sonido")
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

@st.dialog("◈ Calificar Toma")
def ventana_toma_dir(proyecto):
    c1, c2 = st.columns(2)
    escena = c1.text_input("ESC")
    toma = c2.text_input("TOMA")
    evaluacion = st.radio("Evaluación", ["BUENA", "MALA", "REGULAR"], horizontal=True)
    if st.button("Archivar Toma", use_container_width=True):
        if escena:
            st.session_state["proyectos"][proyecto]["tomas_dir"].append({"escena": escena, "toma": toma, "evaluacion": evaluacion})
            guardar_y_recargar()

@st.dialog("◈ Estructurar Personaje")
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

@st.dialog("◈ Registrar Gasto")
def ventana_presupuesto(proyecto):
    item = st.text_input("Concepto")
    costo = st.number_input("Costo Neto ($)", min_value=0.0)
    area = st.selectbox("Área", ["Técnica", "Arte", "Producción", "Catering", "Transporte"])
    estado = st.selectbox("Estado", ["Pendiente", "Abonado"])
    if st.button("Registrar Gasto", use_container_width=True):
        if item:
            st.session_state["proyectos"][proyecto]["presupuesto"].append({"item": item, "costo": costo, "area": area, "estado": estado})
            guardar_y_recargar()

@st.dialog("◈ Perfil de Casting")
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

@st.dialog("◈ Desglose Escénico")
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

@st.dialog("✦ Análisis IA de Equipos")
def ventana_comparador_rental(proyecto):
    directorio = st.session_state["proyectos"][proyecto].get("directorio_rentals", [])
    if not directorio:
        st.warning("Requiere registrar un Rental previamente.")
        return
        
    nombres_rentals = [r["nombre"] for r in directorio]
    rental_elegido = st.selectbox("Asignar a:", nombres_rentals)
    url_rental_elegido = next((r["url"] for r in directorio if r["nombre"] == rental_elegido), "#")

    tab_url, tab_excel, tab_img = st.tabs(["URL", "Documento", "Imagen"])
    
    with tab_url:
        url_producto = st.text_input("Enlace del inventario")
        if st.button("Extraer Datos", use_container_width=True):
            if url_producto:
                with st.spinner("Procesando estructura web..."):
                    try:
                        headers = {'User-Agent': 'Mozilla/5.0'}
                        req = requests.get(url_producto, headers=headers, timeout=15)
                        soup = BeautifulSoup(req.text, 'html.parser')
                        texto_web = soup.get_text(separator=' ', strip=True)[:20000] 
                        
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        modelo = genai.GenerativeModel('gemini-1.5-flash')
                        prompt = f"Extrae datos a JSON. Precio numérico puro. Formato: [{{\"nombre\": \"\", \"precio\": 0, \"estado\": \"Disponible\", \"url\": \"{url_producto}\", \"foto\": \"\"}}]\nTexto: {texto_web}"
                        respuesta = modelo.generate_content(prompt)
                        productos = json.loads(respuesta.text.strip().replace("```json", "").replace("```", ""))
                        if productos:
                            for prod in productos:
                                prod.update({"rental": rental_elegido, "url_rental": url_rental_elegido})
                                st.session_state["proyectos"][proyecto]["comparador_rentals"].append(prod)
                            guardar_y_recargar()
                        else: st.warning("Datos ilegibles.")
                    except Exception as e: st.error(f"Error sistémico: {e}")

    with tab_excel:
        archivo_ex = st.file_uploader("Archivo (XLSX/CSV)", type=["xlsx", "csv"])
        if st.button("Leer Documento", use_container_width=True):
            if archivo_ex:
                with st.spinner("Procesando celdas..."):
                    try:
                        df = pd.read_csv(archivo_ex) if archivo_ex.name.endswith('.csv') else pd.read_excel(archivo_ex)
                        texto_datos = df.to_csv(index=False)[:20000]
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        modelo = genai.GenerativeModel('gemini-1.5-flash')
                        prompt = f"Extrae a JSON. Formato: [{{\"nombre\": \"\", \"precio\": 0, \"estado\": \"Disponible\", \"url\": \"{url_rental_elegido}\", \"foto\": \"\"}}]\nDatos: {texto_datos}"
                        respuesta = modelo.generate_content(prompt)
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
                with st.spinner("Reconocimiento óptico..."):
                    try:
                        img = Image.open(archivo_img)
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        modelo = genai.GenerativeModel('gemini-1.5-flash')
                        prompt = f"Extrae a JSON. Precio numérico. Formato: [{{\"nombre\": \"\", \"precio\": 0, \"estado\": \"Disponible\", \"url\": \"{url_rental_elegido}\", \"foto\": \"\"}}]"
                        respuesta = modelo.generate_content([prompt, img])
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
            st.success(f"Subtotal: ${total_r:,.2f} / jornada")
            link_rental = next((d["url"] for d in directorio if d["nombre"] == r_name), None)
            if link_rental:
                st.markdown(f"<a href='{link_rental}' target='_blank' style='background: #FBAF3B; color:#0A0A0A; padding:8px 12px; text-decoration:none; border-radius:6px; font-weight:600; display:inline-block; margin-top:10px;'>Contactar Proveedor</a>", unsafe_allow_html=True)

@st.dialog("Purga de Base de Datos")
def ventana_vaciar_comparador(proyecto):
    st.warning("Esta acción es irreversible. Limpiará el catálogo y el carrito.")
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
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown(f"<div style='text-align: center;'><img src='{LOGO_URL}' class='logo-img logo-blend' style='max-width:240px; margin: 0 auto 10px auto;'></div>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; font-size: 1.4rem; color: #FAFAFA; margin-bottom: 24px; font-weight: 500;'>Ingresa a tu cuenta</h2>", unsafe_allow_html=True)
        
        tab_login, tab_registro = st.tabs(["Iniciar Sesión", "Registrarse"])
        db_users = st.session_state["proyectos"]["_CONFIG_"]["usuarios"]
        
        with tab_login:
            with st.container(border=True):
                email_ingreso = st.text_input("Email o usuario", placeholder="ejemplo@correo.com").lower().strip()
                pass_ingreso = st.text_input("Contraseña", type="password", placeholder="••••••••")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Iniciar sesión", use_container_width=True, type="primary"):
                    if email_ingreso in db_users and db_users[email_ingreso]["pass"] == pass_ingreso:
                        if db_users[email_ingreso].get("estado") == "Aprobado":
                            st.session_state["usuario_logueado"] = email_ingreso
                            st.session_state["ruta"] = "Inicio"
                            st.rerun()
                        else: st.warning("Cuenta en revisión por el Administrador.")
                    else: st.error("Credenciales inválidas.")
                        
        with tab_registro:
            with st.container(border=True):
                nombre_reg = st.text_input("Nombre Completo")
                email_reg = st.text_input("Correo").lower().strip()
                pass_reg = st.text_input("Crear Contraseña", type="password")
                foto_reg = st.file_uploader("Foto de Credencial", type=["jpg", "png", "jpeg"])
                if st.button("Solicitar Acceso", use_container_width=True, type="primary"):
                    if nombre_reg and email_reg and pass_reg and foto_reg:
                        foto_b64 = base64.b64encode(foto_reg.read()).decode('utf-8')
                        db_users[email_reg] = {
                            "nombre": nombre_reg, "pass": pass_reg, "rol": "Invitado", "nivel": "lectura", "estado": "Pendiente",
                            "foto": foto_b64, "credencial": f"FTN-{random.randint(1000, 9999)}", "edad": "", "roles_fav": "", "dieta": "", "specs": "", "cv": "", "portfolio": "", "acceso_rapido": "Panel General", "spotify": ""
                        }
                        guardar_y_recargar()
                        st.success("Solicitud enviada con éxito.")
                    else: st.error("Completar todos los campos y adjuntar foto.")

# --- 7. PLATAFORMA CENTRAL ---
else:
    usuario_actual = st.session_state["usuario_logueado"]
    db_users = st.session_state["proyectos"]["_CONFIG_"]["usuarios"]
    mis_datos = db_users[usuario_actual]
    rol_actual = mis_datos["rol"]
    nivel_actual = mis_datos["nivel"]
    
    # --- NAVBAR PROFESIONAL ALINEADA ---
    # Uso un contenedor y columnas ajustadas para que la foto de perfil y los botones queden en la misma línea
    col_logo, col_dash, col_soc, col_space, col_msg, col_prof_img, col_prof_btn = st.columns([0.6, 1.2, 1.2, 3.8, 1.2, 0.5, 1.2], vertical_alignment="bottom")
    
    with col_logo:
        st.markdown(f"<img src='{LOGO_URL}' class='logo-img logo-blend' style='max-height:45px; margin-bottom:5px;'>", unsafe_allow_html=True)
    with col_dash:
        if st.button("⌂ Dashboard", use_container_width=True, type="secondary"):
            st.session_state["ruta"] = "Inicio"
            st.rerun()
    with col_soc:
        if st.button("◈ Social", use_container_width=True, type="secondary"):
            st.session_state["ruta"] = "Social"
            st.rerun()
    with col_space:
        pass # Espacio central
    with col_msg:
        if st.button("✉ Mensajes", use_container_width=True, type="secondary"):
            st.session_state["ruta"] = "Mensajes"
            st.rerun()
    with col_prof_img:
        foto_src = f"data:image/jpeg;base64,{mis_datos['foto']}" if mis_datos.get("foto") else "https://via.placeholder.com/150"
        st.markdown(f"<img src='{foto_src}' class='avatar-circle' style='width:45px; height:45px; margin-bottom:4px; margin-left:10px;'>", unsafe_allow_html=True)
    with col_prof_btn:
        if st.button("⚙ Perfil", use_container_width=True, type="secondary"):
            st.session_state["ruta"] = "Perfil"
            st.rerun()
            
    st.markdown("<hr style='border-color: #1C1C1F; margin-top: 5px; margin-bottom: 20px;'>", unsafe_allow_html=True)

    # ==========================================
    # VISTA 1: DASHBOARD
    # ==========================================
    if st.session_state["ruta"] == "Inicio":
        
        # Accesos Rápidos Configurables
        col_q1, col_q2, col_q3, col_q4 = st.columns(4)
        with col_q1:
            with st.container(border=True):
                st.markdown("<p style='font-size:12px; color:#A1A1AA; font-weight:700; margin:0;'>MI ROL</p>", unsafe_allow_html=True)
                st.markdown(f"<h3 class='gradient-text' style='margin:0; font-size:18px;'>{rol_actual}</h3>", unsafe_allow_html=True)
        with col_q2:
            with st.container(border=True):
                st.markdown("<p style='font-size:12px; color:#A1A1AA; font-weight:700; margin:0;'>PROYECTOS</p>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='margin:0; color:#FAFAFA;'>{len([p for p in st.session_state['proyectos'].keys() if p != '_CONFIG_'])} Activos</h3>", unsafe_allow_html=True)
        with col_q3:
            with st.container(border=True):
                st.markdown("<p style='font-size:12px; color:#A1A1AA; font-weight:700; margin:0; margin-bottom: 5px;'>ACCESO RÁPIDO</p>", unsafe_allow_html=True)
                herramientas_list = ["Panel General", "Tablero Kanban", "Rentals IA", "Presupuesto", "Base Crew", "Laboratorio Guion", "Luces (Canvas)", "Arte & Vestuario"]
                acc_rapido = st.selectbox("Herramienta", herramientas_list, index=herramientas_list.index(mis_datos.get("acceso_rapido", "Panel General")), label_visibility="collapsed")
                if acc_rapido != mis_datos.get("acceso_rapido"):
                    db_users[usuario_actual]["acceso_rapido"] = acc_rapido
                    guardar_y_recargar()
                if st.button(f"Ir a {acc_rapido}", type="secondary"):
                    if st.session_state.get("proyecto_activo"):
                        st.session_state["menu_option"] = acc_rapido
                        st.session_state["ruta"] = "Proyecto"
                        st.rerun()
                    else: st.warning("Selecciona un proyecto abajo primero.")
        with col_q4:
            with st.container(border=True):
                st.markdown("<p style='font-size:12px; color:#A1A1AA; font-weight:700; margin:0; margin-bottom: 5px;'>SOPORTE</p>", unsafe_allow_html=True)
                if st.button("Reportar Problema", type="secondary"): ventana_soporte(usuario_actual)

        c_main, c_side = st.columns([2.5, 1], gap="large")
        
        with c_main:
            st.markdown("<div class='section-title'>PROYECTOS EN DESARROLLO</div>", unsafe_allow_html=True)
            if nivel_actual in ["jefe", "jefe_supremo"]:
                with st.popover("Crear Workspace"):
                    nuevo_proyecto = st.text_input("Nombre de la Producción:")
                    if st.button("Inicializar DB"):
                        if nuevo_proyecto:
                            st.session_state["proyectos"][nuevo_proyecto] = {
                                "contexto_aprobado": "Proyecto base.", "archivos_pendientes": [], "avisos": [], "equipos": [], "pedidos_equipos": [], "continuidad": [], 
                                "arte": [], "planos": [], "plan_rodaje": [], "plantas_luces": [], "sonido_log": [], "tomas_dir": [], "personajes": [], "locaciones": [], "crew": [], "catering": [], "links": [], "presupuesto": [], "casting": [], "desglose": [], "comparador_rentals": [], "carrito_rentals": [], "directorio_rentals": [], "kanban": []
                            }
                            guardar_y_recargar()
            
            lista_proyectos = [p for p in st.session_state["proyectos"].keys() if p != "_CONFIG_"]
            if not lista_proyectos: st.info("No hay desarrollos activos.")
            else:
                cols_grid = st.columns(2)
                for idx, proy in enumerate(lista_proyectos):
                    with cols_grid[idx % 2]:
                        with st.container(border=True):
                            st.markdown(f"<h3 style='margin-bottom: 4px; color:#FAFAFA;'>{proy}</h3>", unsafe_allow_html=True)
                            st.caption(f"Crew: {len(st.session_state['proyectos'][proy].get('crew',[]))} | Equipos: {len(st.session_state['proyectos'][proy].get('equipos',[]))}")
                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button("Entrar al Workspace", key=f"entrar_{proy}", use_container_width=True):
                                st.session_state["proyecto_activo"] = proy
                                st.session_state["menu_option"] = "Panel General"
                                st.session_state["ruta"] = "Proyecto"
                                st.rerun()

        with c_side:
            st.markdown("<div class='section-title'>AGENDA DE PRODUCCIÓN</div>", unsafe_allow_html=True)
            if st.button("Agregar Recordatorio", use_container_width=True, type="secondary"):
                ventana_recordatorio(es_admin=(nivel_actual in ["jefe_supremo", "jefe"]), autor=mis_datos['nombre'])
            recordatorios = st.session_state["proyectos"]["_CONFIG_"].get("recordatorios", [])
            for rec in reversed(recordatorios):
                if rec["tipo"] == "Global (Toda la Productora)" or rec["autor"] == mis_datos["nombre"]:
                    with st.container(border=True):
                        st.markdown(f"<span style='color:#FBAF3B; font-size:11px; font-weight:700;'>{rec['fecha']}</span>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-weight:600; font-size:15px; color:#E2E8F0;'>{rec['titulo']}</div>", unsafe_allow_html=True)

    # ==========================================
    # VISTA: RED SOCIAL (NUEVA)
    # ==========================================
    elif st.session_state["ruta"] == "Social":
        st.markdown("<h2 class='gradient-text' style='margin-bottom: 20px;'>Red Social del Estudio</h2>", unsafe_allow_html=True)
        
        # --- HISTORIAS ---
        st.markdown("<div class='section-title'>Historias 24h</div>", unsafe_allow_html=True)
        if st.button("✦ Subir Historia", type="secondary"): ventana_historia(usuario_actual)
        st.markdown("<br>", unsafe_allow_html=True)
        
        historias = st.session_state["proyectos"]["_CONFIG_"].get("social_stories", [])
        ahora = datetime.now()
        historias_activas = [h for h in historias if (ahora - datetime.strptime(h["timestamp"], "%Y-%m-%d %H:%M:%S")).total_seconds() < 86400]
        
        if historias_activas:
            cols_hist = st.columns(min(len(historias_activas), 8))
            for idx, hist in enumerate(historias_activas[:8]):
                with cols_hist[idx]:
                    st.markdown(f"<img src='data:image/jpeg;base64,{hist['foto']}' class='story-circle'>", unsafe_allow_html=True)
                    st.caption(db_users[hist['usuario']]['nombre'].split()[0])
        else:
            st.info("No hay historias nuevas.")
            
        st.divider()
        
        # --- FEED Y SPOTIFY ---
        c_feed, c_spot = st.columns([2.5, 1], gap="large")
        
        with c_feed:
            st.markdown("<div class='section-title'>Muro de Publicaciones</div>", unsafe_allow_html=True)
            
            with st.container(border=True):
                texto_post = st.text_area("¿Qué está pasando en el set?", placeholder="Comparte una actualización con el equipo...")
                img_post = st.file_uploader("Adjuntar imagen", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
                if st.button("Publicar en el Muro", type="primary"):
                    if texto_post or img_post:
                        img_b64 = base64.b64encode(img_post.read()).decode('utf-8') if img_post else None
                        st.session_state["proyectos"]["_CONFIG_"]["social_posts"].insert(0, {
                            "usuario": usuario_actual, "texto": texto_post, "imagen": img_b64, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "likes": 0
                        })
                        guardar_y_recargar()

            posts = st.session_state["proyectos"]["_CONFIG_"].get("social_posts", [])
            for p in posts:
                usr_info = db_users[p["usuario"]]
                with st.container(border=True):
                    colA, colB = st.columns([1, 10])
                    with colA:
                        f_src = f"data:image/jpeg;base64,{usr_info['foto']}" if usr_info.get("foto") else "https://via.placeholder.com/150"
                        st.markdown(f"<img src='{f_src}' style='width:45px; height:45px; border-radius:50%; border: 2px solid #333; object-fit:cover;'>", unsafe_allow_html=True)
                    with colB:
                        st.markdown(f"**{usr_info['nombre']}** <span style='font-size:12px; color:#71717A;'>• {p['timestamp']}</span>", unsafe_allow_html=True)
                        
                    if p.get("texto"):
                        st.write(p["texto"])
                    if p.get("imagen"):
                        st.markdown(f"<img src='data:image/jpeg;base64,{p['imagen']}' style='width:100%; border-radius:12px; margin-top:10px; border: 1px solid #1C1C1F;'>", unsafe_allow_html=True)
                    
                    st.markdown(f"<span style='color:#FBAF3B; font-weight:600; font-size:12px; margin-top:10px; display:block;'>✦ {p.get('likes',0)} Me gusta</span>", unsafe_allow_html=True)

        with c_spot:
            st.markdown("<div class='section-title'>EN SINTONÍA (SPOTIFY)</div>", unsafe_allow_html=True)
            st.caption("Lo que el equipo está escuchando.")
            for em, info in db_users.items():
                if info.get("spotify") and "track/" in info["spotify"]:
                    with st.container(border=True):
                        st.markdown(f"<p style='margin:0; font-size:12px; font-weight:700;'>{info['nombre']}</p>", unsafe_allow_html=True)
                        tid = info["spotify"].split("track/")[1].split("?")[0]
                        components.iframe(f"https://open.spotify.com/embed/track/{tid}?utm_source=generator&theme=0", height=80)

    # ==========================================
    # VISTA: MENSAJES (SISTEMA DE CHAT PRIVADO)
    # ==========================================
    elif st.session_state["ruta"] == "Mensajes":
        st.markdown("<div class='section-title'>MENSAJERÍA DIRECTA</div>", unsafe_allow_html=True)
        col_list, col_chat = st.columns([1, 2.5], gap="large")
        
        if "chat_con" not in st.session_state: st.session_state["chat_con"] = None
        
        with col_list:
            st.markdown("#### Directorio")
            for em, info in db_users.items():
                if em != usuario_actual and info.get("estado") == "Aprobado":
                    with st.container(border=True):
                        st.markdown(f"**{info['nombre']}**<br><span style='font-size:12px;color:#A1A1AA;'>{info['rol']}</span>", unsafe_allow_html=True)
                        if st.button("Chatear", key=f"chat_{em}", use_container_width=True, type="secondary"):
                            st.session_state["chat_con"] = em
                            st.rerun()

        with col_chat:
            if st.session_state["chat_con"]:
                dest_info = db_users[st.session_state["chat_con"]]
                st.markdown(f"### Conversación con {dest_info['nombre']}")
                st.divider()
                
                historial = [m for m in st.session_state["proyectos"]["_CONFIG_"]["mensajes"] if (m["de"] == usuario_actual and m["para"] == st.session_state["chat_con"]) or (m["de"] == st.session_state["chat_con"] and m["para"] == usuario_actual)]
                
                with st.container(height=400):
                    if not historial: st.info("No hay mensajes previos.")
                    for msg in historial:
                        if msg["de"] == usuario_actual:
                            st.markdown(f"<div style='text-align: right;'><span style='background:#FBAF3B; color:#0A0A0B; padding:10px 14px; border-radius:14px; display:inline-block; margin-bottom:4px; font-weight:500;'>{msg['texto']}</span><br><span style='font-size:10px; color:#52525B;'>{msg['fecha']}</span></div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div style='text-align: left;'><span style='background:#1C1C1F; border:1px solid #27272A; color:#FAFAFA; padding:10px 14px; border-radius:14px; display:inline-block; margin-bottom:4px; font-weight:500;'>{msg['texto']}</span><br><span style='font-size:10px; color:#52525B;'>{msg['fecha']}</span></div>", unsafe_allow_html=True)
                
                nuevo_msg = st.chat_input("Escribe un mensaje...")
                if nuevo_msg:
                    st.session_state["proyectos"]["_CONFIG_"]["mensajes"].append({
                        "de": usuario_actual, "para": st.session_state["chat_con"], "texto": nuevo_msg, "fecha": datetime.now().strftime("%H:%M")
                    })
                    guardar_y_recargar()
            else:
                st.info("Selecciona un usuario de la lista para chatear.")

    # ==========================================
    # VISTA: PERFIL Y CREDENCIAL VIP
    # ==========================================
    elif st.session_state["ruta"] == "Perfil":
        st.markdown("<div class='section-title'>CONFIGURACIÓN DE CUENTA Y ACCESOS</div>", unsafe_allow_html=True)
        tab_misdatos, tab_cred, tab_dir, tab_admin = st.tabs(["Mi Perfil", "Credencial Corporativa", "Directorio de Red", "Administración"])
        
        with tab_misdatos:
            with st.container(border=True):
                c_img, c_form = st.columns([1, 2.5])
                with c_img:
                    st.markdown("#### Avatar")
                    foto_src = f"data:image/jpeg;base64,{mis_datos['foto']}" if mis_datos.get("foto") else "https://via.placeholder.com/150"
                    st.markdown(f"<img src='{foto_src}' class='avatar-circle' style='width:120px;height:120px;'>", unsafe_allow_html=True)
                    nueva_foto = st.file_uploader("Actualizar Imagen", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
                    if nueva_foto and st.button("Guardar Foto", use_container_width=True):
                        db_users[usuario_actual]["foto"] = base64.b64encode(nueva_foto.read()).decode('utf-8')
                        guardar_y_recargar()
                    
                    st.markdown("---")
                    st.markdown("#### Estadísticas")
                    proyectos_count = len([p for p in st.session_state["proyectos"].keys() if p != "_CONFIG_"])
                    st.metric("Proyectos Involucrados", proyectos_count)
                    st.metric("Permiso Asignado", mis_datos['nivel'].capitalize())

                with c_form:
                    with st.form("form_perfil"):
                        c1, c2 = st.columns(2)
                        edad = c1.text_input("Edad", value=mis_datos.get("edad", ""))
                        roles_fav = c2.text_input("Especialidad Principal", value=mis_datos.get("roles_fav", ""))
                        portfolio = st.text_input("Enlace a Portfolio (Reel/CV)", value=mis_datos.get("portfolio", ""))
                        spotify_url = st.text_input("Canción de Perfil (Link de Track de Spotify)", value=mis_datos.get("spotify", ""), placeholder="https://open.spotify.com/track/...")
                        specs = st.text_area("Notas o Habilidades Especiales", value=mis_datos.get("specs", ""))
                        if st.form_submit_button("Sincronizar Perfil", use_container_width=True):
                            db_users[usuario_actual].update({"edad": edad, "roles_fav": roles_fav, "portfolio": portfolio, "spotify": spotify_url, "specs": specs})
                            guardar_y_recargar()
                            st.success("Perfil sincronizado.")
                
                st.divider()
                if st.button("Cerrar Sesión", type="secondary"):
                    st.session_state["usuario_logueado"] = None
                    st.session_state["ruta"] = "Inicio"
                    st.rerun()

        with tab_cred:
            qr_data = f"FETEN_ID:{mis_datos.get('credencial')}|NAME:{mis_datos['nombre']}|ROLE:{mis_datos['rol']}"
            qr_b64 = generar_qr_base64(qr_data)
            
            st.markdown(f"""
                <div class="credencial-feten">
                    <img src="{LOGO_URL}" class="credencial-logo-img">
                    <br>
                    <img src="{foto_src}" class="credencial-img">
                    <h2 class="credencial-name">{mis_datos['nombre']}</h2>
                    <p class="credencial-role">{mis_datos['rol']}</p>
                    <div class="qr-box">
                        <img src="data:image/png;base64,{qr_b64}" width="120">
                    </div>
                    <div class="credencial-id-box">
                        <span class="credencial-id">ID: {mis_datos.get('credencial', 'FTN-0000')}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.caption("Presentá el Código QR en controles de acceso, locaciones o casas de rental para verificación instantánea.")

        with tab_dir:
            st.markdown("### Directorio de Red")
            busqueda = st.text_input("Buscar miembros...", placeholder="Nombre o especialidad")
            st.markdown("<br>", unsafe_allow_html=True)
            for em, info in db_users.items():
                if info["estado"] == "Aprobado" and (busqueda.lower() in info["nombre"].lower() or busqueda.lower() in info["rol"].lower()):
                    with st.container(border=True):
                        colD1, colD2, colD3 = st.columns([1, 6, 2])
                        with colD1:
                            f_usr = f"data:image/jpeg;base64,{info['foto']}" if info.get("foto") else "https://via.placeholder.com/150"
                            st.markdown(f"<img src='{f_usr}' class='avatar-circle' style='width:45px;height:45px;'>", unsafe_allow_html=True)
                        with colD2:
                            st.markdown(f"<h4 style='margin:0; font-size:15px; color:#FAFAFA;'>{info['nombre']} <span style='color:#FBAF3B;font-size:12px;'>({info['rol']})</span></h4>", unsafe_allow_html=True)
                            st.caption(f"{em} | Especialidad: {info.get('roles_fav', 'No especificada')}")
                        with colD3:
                            if info.get('portfolio'):
                                st.markdown(f"<a href='{info['portfolio']}' target='_blank' style='font-size:12px; font-weight:bold; color:#FBAF3B; text-decoration:none;'>⧉ Ver Portfolio</a>", unsafe_allow_html=True)

        with tab_admin:
            if rol_actual == "Super Admin":
                st.markdown("### Control de Permisos")
                mapa_roles = {"Super Admin": "jefe_supremo", "Producción": "jefe", "Dirección": "jefe", "Dirección de Fotografía": "jefe", "Dirección de Arte": "jefe", "Director de Sonido": "jefe", "Asistente de Sonido": "asistente", "Guion": "jefe", "Continuidad": "jefe", "Invitado": "lectura"}
                
                for em_usr, dt_usr in db_users.items():
                    with st.container(border=True):
                        c1, c2, c3, c4 = st.columns([2, 1.5, 1.5, 1])
                        c1.markdown(f"**{dt_usr['nombre']}**<br><span style='font-size:12px; color:#888;'>{em_usr}</span>", unsafe_allow_html=True)
                        est = c2.selectbox("Estado", ["Aprobado", "Pendiente"], index=0 if dt_usr.get("estado") == "Aprobado" else 1, key=f"est_{em_usr}")
                        rol = c3.selectbox("Rol", list(mapa_roles.keys()), index=list(mapa_roles.keys()).index(dt_usr["rol"]) if dt_usr["rol"] in mapa_roles else 9, key=f"rol_{em_usr}")
                        if c4.button("Aplicar", key=f"btn_adm_{em_usr}", use_container_width=True):
                            db_users[em_usr].update({"estado": est, "rol": rol, "nivel": mapa_roles[rol]})
                            guardar_y_recargar()

                st.divider()
                st.markdown("### Tickets de Soporte (Recibidos)")
                tickets = st.session_state["proyectos"]["_CONFIG_"]["tickets_soporte"]
                if not tickets: st.info("No hay tickets nuevos.")
                for i, tk in enumerate(reversed(tickets)):
                    with st.container(border=True):
                        st.markdown(f"**{tk['asunto']}** ({tk['fecha']}) - De: {tk['usuario']}")
                        st.write(tk['desc'])
                        if tk['estado'] == "Pendiente":
                            if st.button("Marcar Resuelto", key=f"tk_{i}"):
                                idx_real = len(tickets) - 1 - i
                                st.session_state["proyectos"]["_CONFIG_"]["tickets_soporte"][idx_real]["estado"] = "Resuelto"
                                guardar_y_recargar()
                        else: st.success("Resuelto")
            else:
                st.warning("Solo los Super Admins pueden ver la configuración de red.")

    # ==========================================
    # VISTA 3: PROYECTO (TODOS LOS MÓDULOS INTACTOS)
    # ==========================================
    elif st.session_state["ruta"] == "Proyecto":
        proyecto_elegido = st.session_state["proyecto_activo"]
        p_data = st.session_state["proyectos"][proyecto_elegido]
        if "kanban" not in p_data: p_data["kanban"] = []
        
        st.markdown(f"<h2 class='gradient-text' style='margin-bottom: 24px;'>{proyecto_elegido.upper()}</h2>", unsafe_allow_html=True)
        
        col_nav, col_content = st.columns([1, 3.5], gap="large")
        
        opciones_nav = ["Panel General", "Tablero Kanban", "Asistente IA"]
        iconos_nav = ["grid", "kanban", "lightning-charge"]
        
        if nivel_actual != "lectura": 
            opciones_nav.append("Solicitar a Prod.")
            iconos_nav.append("send")
            
        opciones_nav.extend([
            "Bandeja Prod.", "Rentals IA", "Archivos", "Tablón", "Enlaces", "Permisos", "Presupuesto", "Scouting", 
            "Base Crew", "Casting", "Catering", "Desglose", "Laboratorio Guion", "Inventario", "Plan Rodaje", 
            "Monitor DIR", "Luces (Canvas)", "Ref. IA", "Arte & Vestuario", "Log Sonido", "Raccord",
            "IA: Moodboard Dinámico", "IA: Auditor Anacronismos", "IA: Utilería DIY",
            "IA: Analizador Espectral", "IA: Matriz de Ruido", "IA: Sugerente Foley"
        ])
        iconos_nav.extend([
            "inbox", "shop", "folder2-open", "megaphone", "link-45deg", "shield-lock", "wallet2", "geo-alt", 
            "people", "person-video", "cup-hot", "card-text", "pen", "box", "calendar-event", 
            "camera-reels", "lightbulb", "cpu", "palette", "headphones", "film",
            "magic", "shield-check", "hammer", "soundwave", "volume-up", "mic"
        ])
        
        nav_final = []
        iconos_final = []
        for op, ic in zip(opciones_nav, iconos_nav):
            if rol_actual == "Super Admin":
                nav_final.append(op); iconos_final.append(ic)
            elif rol_actual == "Producción" and op in ["Panel General", "Tablero Kanban", "Asistente IA", "Solicitar a Prod.", "Presupuesto", "Bandeja Prod.", "Scouting", "Base Crew", "Casting", "Catering", "Rentals IA", "Archivos", "Tablón", "Enlaces"]:
                nav_final.append(op); iconos_final.append(ic)
            elif rol_actual == "Guion" and op in ["Panel General", "Tablero Kanban", "Asistente IA", "Solicitar a Prod.", "Desglose", "Laboratorio Guion", "Archivos", "Tablón", "Enlaces"]:
                nav_final.append(op); iconos_final.append(ic)
            elif "Dirección" in rol_actual and rol_actual not in ["Dirección de Arte", "Dirección de Fotografía"] and op in ["Panel General", "Tablero Kanban", "Asistente IA", "Solicitar a Prod.", "Casting", "Plan Rodaje", "Monitor DIR", "Archivos", "Tablón", "Enlaces", "Inventario"]:
                nav_final.append(op); iconos_final.append(ic)
            elif rol_actual == "Dirección de Fotografía" and op in ["Panel General", "Tablero Kanban", "Asistente IA", "Solicitar a Prod.", "Luces (Canvas)", "Ref. IA", "Inventario", "Archivos", "Tablón", "Enlaces"]:
                nav_final.append(op); iconos_final.append(ic)
            elif rol_actual == "Dirección de Arte" and op in ["Panel General", "Tablero Kanban", "Asistente IA", "Solicitar a Prod.", "Arte & Vestuario", "Inventario", "Archivos", "Tablón", "Enlaces", "IA: Moodboard Dinámico", "IA: Auditor Anacronismos", "IA: Utilería DIY"]:
                nav_final.append(op); iconos_final.append(ic)
            elif "Sonido" in rol_actual and op in ["Panel General", "Tablero Kanban", "Asistente IA", "Solicitar a Prod.", "Log Sonido", "Inventario", "Archivos", "Tablón", "Enlaces", "IA: Analizador Espectral", "IA: Matriz de Ruido", "IA: Sugerente Foley"]:
                nav_final.append(op); iconos_final.append(ic)
            elif rol_actual == "Continuidad" and op in ["Panel General", "Tablero Kanban", "Asistente IA", "Solicitar a Prod.", "Raccord", "Archivos", "Tablón", "Enlaces"]:
                nav_final.append(op); iconos_final.append(ic)
            elif nivel_actual == "lectura" and op in ["Panel General", "Tablero Kanban", "Asistente IA", "Archivos", "Tablón", "Enlaces"]:
                nav_final.append(op); iconos_final.append(ic)

        if not nav_final:
            nav_final = ["Panel General", "Tablero Kanban", "Asistente IA", "Solicitar a Prod.", "Archivos", "Tablón", "Enlaces"]
            iconos_final = ["grid", "kanban", "lightning-charge", "send", "folder2-open", "megaphone", "link-45deg"]
        
        idx_defecto = 0
        if st.session_state.get("menu_option") in nav_final:
            idx_defecto = nav_final.index(st.session_state["menu_option"])
            
        with col_nav:
            seccion_elegida = option_menu(
                menu_title="WORKSPACE", options=nav_final, icons=iconos_final, menu_icon="command", default_index=idx_defecto,
                styles={
                    "container": {"padding": "10px", "background-color": "#0A0A0B", "border-radius": "16px", "border": "1px solid #1C1C1F"},
                    "icon": {"color": "#888", "font-size": "15px"},
                    "menu-title": {"color": "#666", "font-size": "11px", "letter-spacing": "2px", "font-weight": "700"},
                    "nav-link": {"font-size": "13px", "text-align": "left", "margin": "4px 0", "color": "#CCC", "border-radius": "8px", "padding": "10px"},
                    "nav-link-selected": {"background-color": "#1A1A1A", "color": "#FAFAFA", "font-weight": "600", "border-left": "3px solid #FBAF3B"},
                }
            )
            st.session_state["menu_option"] = seccion_elegida
        
        with col_content:
            if seccion_elegida == "Panel General":
                c1, c2, c3, c4 = st.columns(4)
                with c1: st.metric("Nómina", len(p_data.get("crew", [])))
                with c2: st.metric("Lugares", len(p_data.get("locaciones", [])))
                with c3: st.metric("Fierros", len(p_data.get("equipos", [])))
                with c4: st.metric("Tickets", len(p_data.get("pedidos_equipos", [])))
                st.divider()
                st.markdown("### Generador de Call Sheet (IA)")
                if st.button("Emitir Plan Maestro", use_container_width=True):
                    try:
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        modelo = genai.GenerativeModel('gemini-1.5-flash')
                        datos = f"Avisos: {p_data.get('avisos', [])} | Locaciones: {p_data.get('locaciones', [])}"
                        prompt = f"Sos Productor. Proyecto: {proyecto_elegido}. Datos: {datos}. Redactá un Call Sheet profesional en Markdown."
                        st.markdown(f"<div style='background:#111; padding:20px; border-radius:12px; border: 1px solid #222; overflow-x: auto;'>{modelo.generate_content(prompt).text}</div>", unsafe_allow_html=True)
                    except: st.error("Falta API Key Gemini.")

            elif seccion_elegida == "Tablero Kanban":
                c1, c2 = st.columns([2.5, 1])
                with c1: st.markdown("<h2>Gestor de Tareas</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("Crear Tarea", use_container_width=True): ventana_kanban(proyecto_elegido, mis_datos['nombre'])
                st.divider()
                k_list = [t for t in p_data["kanban"] if t["estado"] == "Completado"]
                
                colP, colPr, colL = st.columns(3)
                with colP:
                    st.markdown("#### Pendiente")
                    for i, t in enumerate(p_data["kanban"]):
                        if t["estado"] == "Pendiente":
                            with st.container(border=True): 
                                st.write(f"**{t['tarea']}**")
                                if st.button("Mover ➔", key=f"k1_{i}", use_container_width=True, type="secondary"):
                                    p_data["kanban"][i]["estado"] = "En Proceso"
                                    guardar_y_recargar()
                with colPr:
                    st.markdown("#### En Proceso")
                    for i, t in enumerate(p_data["kanban"]):
                        if t["estado"] == "En Proceso":
                            with st.container(border=True): 
                                st.write(f"**{t['tarea']}**")
                                if st.button("Finalizar", key=f"k2_{i}", use_container_width=True):
                                    p_data["kanban"][i]["estado"] = "Completado"
                                    guardar_y_recargar()
                with colL:
                    st.markdown("#### Listo")
                    for t in k_list:
                        with st.container(border=True): st.write(f"~~{t['tarea']}~~")

            elif seccion_elegida == "Asistente IA":
                st.markdown("<h2>Comando de IA (Copilot)</h2>", unsafe_allow_html=True)
                try:
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    modelo = genai.GenerativeModel('gemini-1.5-flash')
                    mensaje = st.chat_input("Escribe una instrucción al sistema...")
                    if mensaje:
                        st.chat_message("user").write(mensaje)
                        resp = modelo.generate_content(f"Sos FTN AI. Hablás con: {mis_datos['nombre']}. Contexto: {p_data['contexto_aprobado']}\nUsuario: {mensaje}")
                        st.chat_message("assistant").write(resp.text)
                except: st.error("Falta configurar la API Key.")

            elif seccion_elegida == "Solicitar a Prod.":
                colA, colB = st.columns([2.5, 1])
                with colA: st.markdown("<h2>Tickets de Necesidad</h2>", unsafe_allow_html=True)
                with colB: 
                    if st.button("Levantar Ticket", use_container_width=True): ventana_pedido(proyecto_elegido, rol_actual)
                st.divider()
                mis_pedidos = [p for p in p_data.get("pedidos_equipos", []) if p["area"] == rol_actual or rol_actual == "Super Admin"]
                for ped in mis_pedidos:
                    with st.container(border=True):
                        st.write(f"**{ped['item']}** — {ped['notas']}")
                        if ped.get('prioridad') == "URGENTE 🚨": st.error("Prioridad: URGENTE")
                        if ped['estado'] == "Pendiente": st.warning("En revisión")
                        elif ped['estado'] == "Aprobado": st.success("Aprobado")
                        else: st.error("Rechazado")

            elif seccion_elegida == "Bandeja Prod.":
                st.markdown("<h2>Control de Tickets</h2>", unsafe_allow_html=True)
                if not p_data["pedidos_equipos"]: st.info("Todo al día.")
                for i, ped in enumerate(p_data["pedidos_equipos"]):
                    if ped['estado'] == "Pendiente":
                        with st.container(border=True):
                            if ped.get('prioridad') == "URGENTE 🚨": st.error("Prioridad Máxima")
                            st.markdown(f"**Área:** {ped['area']} | **Ítem:** {ped['item']}")
                            st.caption(f"Justificación: {ped['notas']}")
                            c1, c2 = st.columns(2)
                            if c1.button("Aprobar", key=f"p_ap_{i}", use_container_width=True):
                                p_data["equipos"].append({"area": ped['area'], "item": ped['item'], "cant": 1, "tipo": "A Confirmar", "rental": "A Definir"})
                                p_data["pedidos_equipos"][i]["estado"] = "Aprobado"
                                guardar_y_recargar()
                            if c2.button("Denegar", key=f"p_re_{i}", use_container_width=True, type="secondary"):
                                p_data["pedidos_equipos"][i]["estado"] = "Rechazado"
                                guardar_y_recargar()

            elif seccion_elegida == "Rentals IA":
                colA, colB, colC = st.columns([2, 1, 1])
                with colA: st.markdown("<h2>Cotizador Central</h2>", unsafe_allow_html=True)
                with colB: 
                    if st.button("Proveedor", use_container_width=True, type="secondary"): ventana_nuevo_rental(proyecto_elegido)
                with colC: 
                    if st.button("Scanner IA", use_container_width=True): ventana_comparador_rental(proyecto_elegido)
                if rol_actual == "Super Admin" and st.button("Purga de Datos", type="secondary"): ventana_vaciar_comparador(proyecto_elegido)
                
                st.divider()
                carrito = p_data.get("carrito_rentals", [])
                if len(carrito) > 0:
                    with st.container(border=True):
                        c_txt, c_btn = st.columns([2, 1])
                        with c_txt: st.markdown("<h3 style='margin:0;'>Checkout</h3>", unsafe_allow_html=True)
                        with c_btn:
                            if st.button("GENERAR PEDIDO", use_container_width=True): ventana_checkout(proyecto_elegido)
                        
                        cols_cart = st.columns(2)
                        total_cart = 0
                        for i, item in enumerate(carrito):
                            total_cart += item["precio"]
                            with cols_cart[i % 2]:
                                with st.container(border=True):
                                    st.markdown(f"<p style='font-size:10px; font-weight:bold; color:#FBAF3B; margin:0;'>{item.get('rental', 'N/A')}</p>", unsafe_allow_html=True)
                                    st.markdown(f"<p style='font-weight:600; margin:0; font-size:13px; color:#E2E8F0;'>{item['nombre'][:25]}...</p>", unsafe_allow_html=True)
                                    st.markdown(f"**${item['precio']:,.2f}**")
                                    if st.button("Remover", key=f"quit_cart_{i}", use_container_width=True, type="secondary"):
                                        p_data["carrito_rentals"].pop(i)
                                        guardar_y_recargar()
                        st.markdown(f"<h4 style='text-align:right; color:#FBAF3B; font-size:1rem;'>Total: ${total_cart:,.2f} / Día</h4>", unsafe_allow_html=True)
                
                st.markdown("### Base Analizada")
                rentals_lista = p_data.get("comparador_rentals", [])
                if not rentals_lista: st.info("Base vacía. Ejecute el Scanner IA.")
                else:
                    texto_busqueda = st.text_input("Filtrar inventario...")
                    rentals_mostrar = [(idx, r) for idx, r in enumerate(rentals_lista) if texto_busqueda.lower() in r['nombre'].lower()]
                    if rentals_mostrar:
                        precios_validos = [r["precio"] for _, r in rentals_mostrar if r["precio"] > 0]
                        menor_precio = min(precios_validos) if precios_validos else 0

                        cols = st.columns(2)
                        for i, (idx_orig, r) in enumerate(rentals_mostrar):
                            with cols[i % 2]:
                                with st.container(border=True):
                                    if r["precio"] == menor_precio and r["precio"] > 0:
                                        st.markdown("<span style='background:rgba(251, 175, 59, 0.2); border: 1px solid #FBAF3B; color:#FBAF3B; padding:2px 8px; border-radius:6px; font-size:10px; font-weight:800;'>MÁS CONVENIENTE</span>", unsafe_allow_html=True)
                                    st.markdown(f"<p style='font-size:11px; font-weight:bold; color:#FBAF3B; margin:0; margin-top:5px;'>{r.get('rental', 'N/A')}</p>", unsafe_allow_html=True)
                                    st.markdown(f"<p style='margin:0; font-weight:500; font-size:13px; color:#E2E8F0;'>{r['nombre']}</p>", unsafe_allow_html=True)
                                    st.markdown(f"<h3 style='margin:0; color:#FBAF3B; font-size:18px;'>${r['precio']:,.2f}</h3>", unsafe_allow_html=True)
                                    c_add, c_del = st.columns(2)
                                    if c_add.button("Añadir", key=f"add_{idx_orig}", use_container_width=True):
                                        p_data["carrito_rentals"].append(r)
                                        guardar_y_recargar()
                                    if c_del.button("Borrar", key=f"del_{idx_orig}", use_container_width=True, type="secondary"):
                                        p_data["comparador_rentals"].pop(idx_orig)
                                        guardar_y_recargar()
                    else: st.warning("Sin coincidencias.")

            elif seccion_elegida == "Archivos":
                st.markdown("<h2>Documentos de Producción</h2>", unsafe_allow_html=True)
                archivo = st.file_uploader("Documento de texto (.txt)", type=["txt"])
                if archivo and st.button("Subir a Base", use_container_width=True):
                    if nivel_actual in ["jefe", "jefe_supremo"]:
                        p_data["contexto_aprobado"] += f"\n\n[Doc: {archivo.name}]:\n{archivo.getvalue().decode('utf-8')}"
                        guardar_y_recargar()
                    else:
                        p_data["archivos_pendientes"].append({"autor": mis_datos['nombre'], "nombre": archivo.name, "texto": archivo.getvalue().decode('utf-8')})
                        guardar_y_recargar()
                if nivel_actual in ["jefe", "jefe_supremo"] and len(p_data["archivos_pendientes"]) > 0:
                    st.divider()
                    st.markdown("### Pendientes de Aprobación")
                    for i, doc in enumerate(p_data["archivos_pendientes"]):
                        with st.container(border=True):
                            st.write(f"**{doc['nombre']}** ({doc['autor']})")
                            c1, c2 = st.columns(2)
                            if c1.button("Aprobar", key=f"ap_{i}", use_container_width=True):
                                p_data["contexto_aprobado"] += f"\n\n[Doc de {doc['autor']} - {doc['nombre']}]:\n{doc['texto']}"
                                p_data["archivos_pendientes"].pop(i)
                                guardar_y_recargar()
                            if c2.button("Rechazar", key=f"re_{i}", use_container_width=True, type="secondary"):
                                p_data["archivos_pendientes"].pop(i)
                                guardar_y_recargar()

            elif seccion_elegida == "Tablón":
                c1, c2 = st.columns([2.5, 1])
                with c1: st.markdown("<h2>Comunicaciones</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("Publicar", use_container_width=True): ventana_aviso(proyecto_elegido, mis_datos['nombre'], p_data["locaciones"])
                st.divider()
                for aviso in reversed(p_data["avisos"]):
                    with st.container(border=True): st.markdown(f"**{aviso['autor']}**: {aviso.get('texto', 'Citación cargada.')}")

            elif seccion_elegida == "Enlaces":
                c1, c2 = st.columns([2.5, 1])
                with c1: st.markdown("<h2>Directorio Web</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("Cargar URL", use_container_width=True): ventana_link(proyecto_elegido)
                st.divider()
                for lk in p_data["links"]:
                    with st.container(border=True): st.markdown(f"### [{lk['titulo']}]({lk['url']})\n{lk['desc']}")

            elif seccion_elegida == "Permisos":
                st.markdown("<h2>Control de Accesos</h2>", unsafe_allow_html=True)
                mapa = {"Super Admin": "jefe_supremo", "Producción": "jefe", "Dirección": "jefe", "Dirección de Fotografía": "jefe", "Dirección de Arte": "jefe", "Director de Sonido": "jefe", "Asistente de Sonido": "asistente", "Guion": "jefe", "Continuidad": "jefe", "Invitado": "lectura"}
                for em_usr, dt_usr in db_users.items():
                    with st.container(border=True):
                        st.markdown(f"**{dt_usr['nombre']}**<br><span style='font-size:12px; color:gray;'>{em_usr}</span>", unsafe_allow_html=True)
                        est = st.selectbox("Estado", ["Aprobado", "Pendiente"], index=0 if dt_usr.get("estado") == "Aprobado" else 1, key=f"e_{em_usr}")
                        rol = st.selectbox("Rol", list(mapa.keys()), index=list(mapa.keys()).index(dt_usr["rol"]) if dt_usr["rol"] in mapa else 9, key=f"r_{em_usr}")
                        if st.button("Aplicar cambios", key=f"b_{em_usr}", use_container_width=True):
                            db_users[em_usr].update({"estado": est, "rol": rol, "nivel": mapa[rol]})
                            guardar_y_recargar()

            elif seccion_elegida == "Presupuesto":
                c1, c2 = st.columns([2.5, 1])
                with c1: st.markdown("<h2>Flujo Financiero</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("Asentar Gasto", use_container_width=True): ventana_presupuesto(proyecto_elegido)
                st.divider()
                if p_data.get("presupuesto"):
                    df_presupuesto = pd.DataFrame(p_data["presupuesto"])
                    total = df_presupuesto['costo'].sum()
                    st.markdown(f"<h3 style='color:#FBAF3B; font-size: 1.2rem;'>Total: ${total:,.2f}</h3>", unsafe_allow_html=True)
                    fig = px.pie(df_presupuesto, values='costo', names='area', title='Distribución', color_discrete_sequence=px.colors.sequential.YlOrBr)
                    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig, use_container_width=True)
                    st.download_button("Exportar CSV", data=df_presupuesto.to_csv(index=False).encode('utf-8'), file_name="budget.csv", mime="text/csv", use_container_width=True)
                else: st.info("No hay gastos registrados.")

            elif seccion_elegida == "Scouting":
                c1, c2 = st.columns([2.5, 1])
                with c1: st.markdown("<h2>Locaciones y Clima</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("Registrar Locación", use_container_width=True): ventana_locacion(proyecto_elegido)
                st.divider()
                for loc in p_data.get("locaciones", []):
                    with st.container(border=True):
                        st.markdown(f"### ⌖ {loc['nombre']}")
                        st.write(f"**Dir:** {loc['direccion']} | **Estado:** {loc['permisos']}")
                        if loc.get('lat', 0.0) != 0.0: st.map(pd.DataFrame({'lat': [loc['lat']], 'lon': [loc['lon']]}), zoom=15, height=180)
                        st.info(f"**Clima estimado:** {random.choice(['Soleado', 'Nublado', 'Lluvias Aisladas'])}")

            elif seccion_elegida == "Base Crew":
                c1, c2 = st.columns([2.5, 1])
                with c1: st.markdown("<h2>Nómina Técnica</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("Contratar", use_container_width=True): ventana_crew(proyecto_elegido)
                st.divider()
                if p_data.get("crew"):
                    df_crew = pd.DataFrame(p_data["crew"])
                    st.dataframe(df_crew, use_container_width=True)
                    st.download_button("Descargar CSV", data=df_crew.to_csv(index=False).encode('utf-8'), file_name="crew.csv", mime="text/csv", use_container_width=True)

            elif seccion_elegida == "Casting":
                c1, c2 = st.columns([2.5, 1])
                with c1: st.markdown("<h2>Talentos</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("Añadir Actor", use_container_width=True): ventana_casting(proyecto_elegido)
                st.divider()
                cols = st.columns(2)
                for i, a in enumerate(p_data["casting"]):
                    with cols[i % 2]:
                        with st.container(border=True):
                            if a.get("foto"): st.image(base64.b64decode(a["foto"]), width=70)
                            st.markdown(f"**{a['actor']}**<br>Papel: {a['personaje']}", unsafe_allow_html=True)

            elif seccion_elegida == "Catering":
                c1, c2 = st.columns([2.5, 1])
                with c1: st.markdown("<h2>Dietética</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("Añadir Dieta", use_container_width=True): ventana_catering(proyecto_elegido)
                st.divider()
                for p in p_data["catering"]:
                    with st.container(border=True): st.markdown(f"**{p['nombre']}** | ⎔ {p['dieta']}")

            elif seccion_elegida == "Desglose":
                c1, c2 = st.columns([2.5, 1])
                with c1: st.markdown("<h2>Breakdown</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("Extraer Escena", use_container_width=True): ventana_desglose(proyecto_elegido)
                st.divider()
                for d in p_data["desglose"]:
                    with st.container(border=True): st.markdown(f"**ESC {d['escena']} | {d['intext']}**<br>{d['desc']}", unsafe_allow_html=True)

            elif seccion_elegida == "Laboratorio Guion":
                st.markdown("<h2>Escritura</h2>", unsafe_allow_html=True)
                with st.container(border=True):
                    st.markdown("### Pomodoro Writer")
                    if st.button("Iniciar 25 Minutos", use_container_width=True):
                        with st.spinner("Modo enfoque activado..."): time.sleep(2)
                        st.success("¡Tiempo cumplido!")
                st.divider()
                if st.button("Crear Personaje", use_container_width=True, type="secondary"): ventana_personaje(proyecto_elegido)
                for p in p_data.get("personajes", []):
                    with st.container(border=True): st.markdown(f"**{p['nombre']}** ({p['rol']})")

            elif seccion_elegida == "Inventario":
                c1, c2 = st.columns([2.5, 1])
                with c1: st.markdown("<h2>Activos</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("Agregar a Base", use_container_width=True): ventana_equipo(proyecto_elegido, rol_actual)
                st.divider()
                for eq in p_data["equipos"]:
                    with st.container(border=True): st.markdown(f"**{eq['cant']}x {eq['item']}** | {eq['area']}")

            elif seccion_elegida == "Plan Rodaje":
                c1, c2 = st.columns([2.5, 1])
                with c1: st.markdown("<h2>Cronograma</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("Nuevo Bloque", use_container_width=True): ventana_cronograma(proyecto_elegido)
                st.divider()
                for a in sorted(p_data["plan_rodaje"], key=lambda x: x.get('hora', '00:00')):
                    with st.container(border=True): st.markdown(f"**{a.get('hora', '')}** - {a['actividad']}")

            elif seccion_elegida == "Monitor DIR":
                c1, c2, c3 = st.columns([1.5, 1, 1])
                with c1: st.markdown("<h2>Director's Log</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("Shot List", use_container_width=True, type="secondary"): ventana_plano(proyecto_elegido)
                with c3: 
                    if st.button("Loguear Toma", use_container_width=True): ventana_toma_dir(proyecto_elegido)
                st.divider()
                for t in p_data["tomas_dir"]:
                    with st.container(border=True): st.markdown(f"{t['evaluacion']} | **ESC {t['escena']} - T {t['toma']}**")

            elif seccion_elegida == "Luces (Canvas)":
                st.markdown("<h2>Planta de Luz</h2>", unsafe_allow_html=True)
                modo = st.selectbox("Trazado", ["freedraw", "line", "rect", "circle", "transform"])
                color_mapping = {"Principal": "#FFD700", "Relleno": "#1E90FF", "Contraluz": "#8A2BE2", "Actor": "#FF4500", "Cámara": "#2D2926"}
                tipo = st.selectbox("Elemento", list(color_mapping.keys()))
                grosor = st.slider("Grosor", 1, 10, 3)
                st_canvas(fill_color="rgba(255,255,255,0)", stroke_width=grosor, stroke_color=color_mapping[tipo], background_color="#111", width=330, height=350, drawing_mode=modo, key="canvas_luces_pro")

            elif seccion_elegida == "Ref. IA":
                st.markdown("<h2>Lab Visual</h2>", unsafe_allow_html=True)
                try:
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    mod_foto = genai.GenerativeModel('gemini-1.5-flash')
                    msg_foto = st.chat_input("Prompt visual...")
                    if msg_foto:
                        st.markdown(f"**Dir:** {msg_foto}")
                        resp = mod_foto.generate_content(f"Sos DF. Da referencias: {msg_foto}")
                        st.info(resp.text)
                except: st.error("Falta API Key.")

            elif seccion_elegida == "Arte & Vestuario":
                c1, c2 = st.columns([2.5, 1])
                with c1: st.markdown("<h2>Dep. Arte</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("Añadir Objeto", use_container_width=True): ventana_arte(proyecto_elegido)
                st.divider()
                for item in p_data["arte"]:
                    with st.container(border=True):
                        st.markdown(f"**{item['estado']}** | {item['objeto']}")
                        if item.get("foto"): st.image(base64.b64decode(item["foto"]), width=100)

            elif seccion_elegida == "Log Sonido":
                c1, c2 = st.columns([2.5, 1])
                with c1: st.markdown("<h2>Audio Log</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("Registrar", use_container_width=True): ventana_sonido(proyecto_elegido)
                st.divider()
                for s in reversed(p_data["sonido_log"]):
                    with st.container(border=True): st.markdown(f"**ESC {s['escena']} | T {s['toma']}**")

            elif seccion_elegida == "Raccord":
                c1, c2 = st.columns([2.5, 1])
                with c1: st.markdown("<h2>Continuidad</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("Asentar Script", use_container_width=True): ventana_continuidad(proyecto_elegido)
                st.divider()
                for nota in reversed(p_data["continuidad"]):
                    with st.container(border=True): st.markdown(f"**ESC {nota['escena']} - T {nota['toma']}**<br>{nota['detalle']}", unsafe_allow_html=True)

            # ==========================================
            # FUNCIONES DE IA ARTE Y SONIDO
            # ==========================================
            elif seccion_elegida == "IA: Moodboard Dinámico":
                st.markdown("<h2>Moodboard Dinámico por IA</h2>", unsafe_allow_html=True)
                st.caption("Genera paletas de colores y texturas.")
                img_mb = st.file_uploader("Subir foto de referencia", type=["jpg", "png", "jpeg"], key="mb_upl")
                if img_mb and st.button("Generar Paleta", use_container_width=True):
                    with st.spinner("Analizando matices visuales..."):
                        try:
                            img = Image.open(img_mb)
                            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                            mod = genai.GenerativeModel('gemini-1.5-flash')
                            resp = mod.generate_content(["Analiza esta imagen y describe detalladamente 4 códigos de color HEX sugeridos para ambientación de set, texturas de paredes recomendadas y materialidad de los muebles en formato profesional.", img])
                            st.markdown(f"<div style='background:#111; padding:20px; border-radius:12px; border:1px solid #222;'>{resp.text}</div>", unsafe_allow_html=True)
                        except Exception as e: st.error(f"Error: {e}")

            elif seccion_elegida == "IA: Auditor Anacronismos":
                st.markdown("<h2>Auditor de Anacronismos</h2>", unsafe_allow_html=True)
                st.caption("Verifica historicidad de la utilería.")
                epoca_set = st.text_input("Época de ambientación")
                img_ut = st.file_uploader("Foto del objeto", type=["jpg", "png", "jpeg"], key="ut_upl")
                if img_ut and st.button("Auditar", use_container_width=True):
                    if epoca_set:
                        with st.spinner("Verificando registros..."):
                            try:
                                img = Image.open(img_ut)
                                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                                mod = genai.GenerativeModel('gemini-1.5-flash')
                                resp = mod.generate_content([f"Analiza si este objeto es anacrónico para una producción ambientada en '{epoca_set}'.", img])
                                st.markdown(f"<div style='background:#111; padding:20px; border-radius:12px; border:1px solid #222;'>{resp.text}</div>", unsafe_allow_html=True)
                            except Exception as e: st.error(f"Error: {e}")

            elif seccion_elegida == "IA: Utilería DIY":
                st.markdown("<h2>Guía de Utilería DIY</h2>", unsafe_allow_html=True)
                objeto_deseado = st.text_input("Elemento a fabricar")
                if st.button("Generar Instructivo", use_container_width=True):
                    if objeto_deseado:
                        with st.spinner("Diseñando..."):
                            try:
                                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                                mod = genai.GenerativeModel('gemini-1.5-flash')
                                resp = mod.generate_content(f"Crea una guía paso a paso para fabricar '{objeto_deseado}' con materiales económicos.")
                                st.markdown(f"<div style='background:#111; padding:20px; border-radius:12px; border:1px solid #222;'>{resp.text}</div>", unsafe_allow_html=True)
                            except Exception as e: st.error(f"Error: {e}")

            elif seccion_elegida == "IA: Analizador Espectral":
                st.markdown("<h2>Analizador Espectral</h2>", unsafe_allow_html=True)
                audio_file = st.file_uploader("Archivo de audio", type=["wav", "mp3"], key="aud_spec")
                if audio_file:
                    if st.button("Renderizar", use_container_width=True):
                        with st.spinner("Calculando..."):
                            try:
                                y, sr = librosa.load(audio_file, sr=None)
                                D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
                                fig, ax = plt.subplots(figsize=(10, 4))
                                img = librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log', ax=ax, cmap='magma')
                                fig.colorbar(img, ax=ax, format='%+2.0f dB')
                                st.pyplot(fig)
                            except Exception as e: st.error(f"Error: {e}")

            elif seccion_elegida == "IA: Matriz de Ruido":
                st.markdown("<h2>Matriz de Aislamiento Acústico</h2>", unsafe_allow_html=True)
                col_m1, col_m2 = st.columns(2)
                fuente_ruido = col_m1.selectbox("Fuente cercana", ["Tráfico", "Aviones", "Construcción", "Multitud"])
                distancia_mt = col_m2.number_input("Distancia (m)", min_value=1, value=20)
                if st.button("Calcular Plan", use_container_width=True):
                    with st.spinner("Evaluando..."):
                        try:
                            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                            mod = genai.GenerativeModel('gemini-1.5-flash')
                            resp = mod.generate_content(f"Una locación está a {distancia_mt}m de '{fuente_ruido}'. ¿Qué soluciones de insonorización debe aplicar sonido directo?")
                            st.markdown(f"<div style='background:#111; padding:20px; border-radius:12px; border:1px solid #222;'>{resp.text}</div>", unsafe_allow_html=True)
                        except Exception as e: st.error(f"Error: {e}")

            elif seccion_elegida == "IA: Sugerente Foley":
                st.markdown("<h2>Sugerente de Foley por IA</h2>", unsafe_allow_html=True)
                accion_escena = st.text_input("Acción visual")
                if st.button("Generar Lista", use_container_width=True):
                    if accion_escena:
                        with st.spinner("Diseñando plan..."):
                            try:
                                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                                mod = genai.GenerativeModel('gemini-1.5-flash')
                                resp = mod.generate_content(f"Para la acción: '{accion_escena}', enumera la lista exacta de efectos Foley necesarios.")
                                st.markdown(f"<div style='background:#111; padding:20px; border-radius:12px; border:1px solid #222;'>{resp.text}</div>", unsafe_allow_html=True)
                            except Exception as e: st.error(f"Error: {e}")
