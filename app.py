import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
import os
import base64
import requests
from bs4 import BeautifulSoup
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from datetime import datetime, date
import random

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Fetén Workspace", page_icon="🎬", layout="wide", initial_sidebar_state="collapsed")

# --- 2. DISEÑO UI/UX PREMIUM (SISTEMA "MIDNIGHT GLASS") ---
st.markdown("""
    <style>
    /* Tipografía súper limpia e industrial */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Ocultar elementos por defecto de Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Fondo Dark Mode Premium (Estilo Vercel/Linear) */
    .stApp {
        background-color: #09090b !important;
        background-image: radial-gradient(circle at 50% 0%, rgba(79, 70, 229, 0.15) 0%, transparent 60%) !important;
        color: #e2e8f0 !important;
    }

    /* Títulos con Gradientes */
    h1, h2 {
        background: -webkit-linear-gradient(0deg, #a5b4fc, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        letter-spacing: -1px !important;
    }
    h3, h4 { color: #f8fafc !important; font-weight: 600 !important; }
    p, span, div { color: #cbd5e1 !important; }

    /* Tarjetas tipo Cristal (Glassmorphism) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(24, 24, 27, 0.6) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        box-shadow: 0 10px 40px -10px rgba(0,0,0,0.5) !important;
        padding: 1.2rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: rgba(99, 102, 241, 0.4) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 40px -10px rgba(99, 102, 241, 0.2) !important;
    }
    
    /* Inputs y Formularios de Alta Gama */
    .stTextInput input, .stSelectbox select, .stNumberInput input, .stDateInput input, .stTimeInput input {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        transition: all 0.2s ease !important;
    }
    .stTextInput input:focus, .stSelectbox select:focus {
        border-color: #6366f1 !important;
        background-color: rgba(99, 102, 241, 0.05) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
    }
    
    /* Botones Neón/Glow */
    .stButton button {
        background: linear-gradient(180deg, #6366f1 0%, #4f46e5 100%) !important;
        border: 1px solid #4338ca !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4) !important;
    }
    .stButton button:hover {
        background: linear-gradient(180deg, #818cf8 0%, #6366f1 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(79, 70, 229, 0.6) !important;
        border-color: #818cf8 !important;
    }
    .stButton button p { color: white !important; font-weight: 600 !important; }

    /* Magia CSS: Convertir st.radio en un menú de navegación tipo Sidebar moderno */
    [data-testid="stRadio"] div[role="radiogroup"] {
        display: flex; flex-direction: column; gap: 4px;
    }
    [data-testid="stRadio"] div[role="radiogroup"] > label {
        padding: 12px 15px !important;
        border-radius: 10px !important;
        background: transparent !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        margin: 0 !important;
        border: 1px solid transparent;
    }
    [data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        background: rgba(255,255,255,0.05) !important;
    }
    [data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {
        display: none !important; /* Oculta el círculo del radio button */
    }
    [data-testid="stRadio"] div[role="radiogroup"] > label[data-baseweb="radio"][aria-checked="true"] {
        background: rgba(99, 102, 241, 0.15) !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        border-left: 4px solid #818cf8 !important;
    }
    [data-testid="stRadio"] div[role="radiogroup"] > label > div:last-child {
        font-weight: 500 !important; font-size: 14px !important; color: #f8fafc !important;
    }

    /* Avatares y Perfiles */
    .avatar-circle {
        border-radius: 50%; object-fit: cover;
        width: 50px; height: 50px;
        border: 2px solid #818cf8;
        box-shadow: 0 0 15px rgba(129, 140, 248, 0.4);
    }
    
    /* Credencial VIP Black Card */
    .credencial-feten {
        background: linear-gradient(135deg, #09090b 0%, #18181b 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-top: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 24px; padding: 40px 30px; width: 100%; max-width: 380px;
        margin: 20px auto; text-align: center;
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.8), inset 0 1px 1px rgba(255,255,255,0.1);
        position: relative; overflow: hidden;
    }
    .credencial-logo { font-size: 16px; font-weight: 800; letter-spacing: 5px; color: #818cf8; margin-bottom: 25px; text-transform: uppercase;}
    .credencial-img { width: 120px; height: 120px; border-radius: 50%; border: 3px solid #334155; margin-bottom: 20px; object-fit: cover; box-shadow: 0 10px 25px rgba(0,0,0,0.8);}
    .credencial-name { font-size: 26px; font-weight: 800; margin: 0; color: white !important;}
    .credencial-role { font-size: 13px; color: #94a3b8 !important; margin-top: 5px; margin-bottom: 30px; text-transform: uppercase; letter-spacing: 2px;}
    .credencial-id-box { background: rgba(0,0,0,0.5); padding: 12px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); }
    .credencial-id { font-family: 'Courier New', monospace; font-weight: bold; font-size: 18px; letter-spacing: 3px; color: #c7d2fe !important;}
    
    /* Métricas Dashboard */
    [data-testid="stMetricValue"] {
        color: #818cf8 !important; font-size: 2.5rem !important; font-weight: 800 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important; text-transform: uppercase !important; letter-spacing: 1px !important; font-size: 0.8rem !important;
    }
    </style>
""", unsafe_allow_html=True)

ARCHIVO_BD = "ftn_database.json"

# --- 3. MOTOR DE MEMORIA PERMANENTE ---
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
                                "foto": "", "credencial": "FTN-0001", "edad": "", "roles_fav": "Directora / Productora", "dieta": "Ninguna", "specs": "", "cv": "", "portfolio": ""
                            }
                        }, "recordatorios": []
                    }
                
                if "recordatorios" not in data_cargada["_CONFIG_"]: data_cargada["_CONFIG_"]["recordatorios"] = []
                
                claves_necesarias = [
                    "archivos_pendientes", "avisos", "equipos", "pedidos_equipos", "continuidad", 
                    "arte", "planos", "plan_rodaje", "plantas_luces", "sonido_log", "tomas_dir", 
                    "personajes", "locaciones", "crew", "catering", "links", "presupuesto", 
                    "casting", "desglose", "comparador_rentals", "carrito_rentals", "directorio_rentals"
                ]
                for nombre_proy, datos_proy in data_cargada.items():
                    if nombre_proy == "_CONFIG_": 
                        for email_u, info_u in datos_proy.get("usuarios", {}).items():
                            if "estado" not in info_u: info_u["estado"] = "Aprobado"
                            if "pass" not in info_u: info_u["pass"] = "1234"
                            if "foto" not in info_u: info_u["foto"] = ""
                            if "credencial" not in info_u: info_u["credencial"] = f"FTN-{random.randint(1000, 9999)}"
                            if "edad" not in info_u: info_u["edad"] = ""
                            if "roles_fav" not in info_u: info_u["roles_fav"] = ""
                            if "dieta" not in info_u: info_u["dieta"] = ""
                            if "specs" not in info_u: info_u["specs"] = ""
                            if "cv" not in info_u: info_u["cv"] = ""
                            if "portfolio" not in info_u: info_u["portfolio"] = ""
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
                            "foto": "", "credencial": "FTN-0001", "edad": "", "roles_fav": "Super Admin", "dieta": "", "specs": "", "cv": "", "portfolio": ""
                        }
                    }, "recordatorios": []
                },
                "Piloto Serie Web": {
                    "contexto_aprobado": "Comedia negra en una oficina.",
                    "archivos_pendientes": [], "avisos": [], "equipos": [], "pedidos_equipos": [], "continuidad": [], 
                    "arte": [], "planos": [], "plan_rodaje": [], "plantas_luces": [], "sonido_log": [], "tomas_dir": [], 
                    "personajes": [], "locaciones": [], "crew": [], "catering": [],
                    "links": [], "presupuesto": [], "casting": [], "desglose": [], "comparador_rentals": [], "carrito_rentals": [], "directorio_rentals": [] 
                }
            }

inicializar_bd()

# --- ENRUTADOR PRINCIPAL ---
if "ruta" not in st.session_state: st.session_state["ruta"] = "Inicio"
if "proyecto_activo" not in st.session_state: st.session_state["proyecto_activo"] = None

# --- 4. VENTANAS EMERGENTES (MODALES) ---

@st.dialog("📅 Nuevo Recordatorio")
def ventana_recordatorio(es_admin, autor):
    titulo = st.text_input("Título / Tarea")
    fecha = st.date_input("Fecha")
    tipo = st.selectbox("Visibilidad", ["Solo para mí", "Global (Toda la productora)"]) if es_admin else "Solo para mí"
    if st.button("Guardar Tarea", use_container_width=True):
        if titulo:
            st.session_state["proyectos"]["_CONFIG_"]["recordatorios"].append({"autor": autor, "titulo": titulo, "fecha": str(fecha), "tipo": tipo})
            guardar_y_recargar()

@st.dialog("📢 Publicar en Tablón")
def ventana_aviso(proyecto, autor, locaciones_disponibles):
    tipo = st.radio("Tipo de Publicación:", ["Aviso General", "🚨 Citación Oficial"], horizontal=True)
    if tipo == "Aviso General":
        nuevo_aviso = st.text_area("Mensaje para el equipo:")
        if st.button("Publicar Aviso", use_container_width=True):
            if nuevo_aviso:
                st.session_state["proyectos"][proyecto]["avisos"].append({"tipo": "general", "autor": autor, "texto": nuevo_aviso})
                guardar_y_recargar()
    else:
        c1, c2 = st.columns(2)
        fecha = c1.date_input("Fecha de Rodaje")
        hora = c2.time_input("Hora de Citación")
        nombres_locs = [l['nombre'] for l in locaciones_disponibles]
        loc_elegida = st.selectbox("Locación", nombres_locs) if nombres_locs else st.text_input("Locación (No hay guardadas)")
        notas_citacion = st.text_area("Notas extras")
        if st.button("Publicar Citación", use_container_width=True):
            st.session_state["proyectos"][proyecto]["avisos"].append({
                "tipo": "citacion", "autor": autor, "fecha": str(fecha), "hora": str(hora), "locacion": loc_elegida, "notas": notas_citacion
            })
            guardar_y_recargar()

@st.dialog("📍 Agregar Locación")
def ventana_locacion(proyecto):
    nombre = st.text_input("Nombre de la Locación")
    direccion = st.text_input("Dirección Exacta")
    c1, c2 = st.columns(2)
    lat = c1.number_input("Latitud", format="%.6f", value=0.0)
    lon = c2.number_input("Longitud", format="%.6f", value=0.0)
    permisos = st.selectbox("Estado del Permiso", ["En gestión", "Aprobado", "No requiere"])
    if st.button("Guardar Locación", use_container_width=True):
        if nombre:
            st.session_state["proyectos"][proyecto]["locaciones"].append({"nombre": nombre, "direccion": direccion, "lat": lat, "lon": lon, "permisos": permisos})
            guardar_y_recargar()

@st.dialog("👥 Fichar Miembro (Crew/Elenco)")
def ventana_crew(proyecto):
    nombre = st.text_input("Nombre Completo")
    c1, c2 = st.columns(2)
    rol = c1.text_input("Rol en el set")
    telefono = c2.text_input("Teléfono de contacto")
    obra_social = st.text_input("Obra Social / ART")
    if st.button("Fichar en Proyecto", use_container_width=True):
        if nombre:
            st.session_state["proyectos"][proyecto]["crew"].append({"nombre": nombre, "rol": rol, "telefono": telefono, "obra_social": obra_social})
            guardar_y_recargar()

@st.dialog("🍽️ Cargar Restricciones (Catering)")
def ventana_catering(proyecto):
    nombre = st.text_input("Nombre Completo")
    dieta = st.selectbox("Preferencia / Restricción", ["Ninguna", "Vegetariano/a", "Vegano/a", "Celíaco/a (Sin TACC)", "Diabético/a"])
    alergias = st.text_area("Alergias específicas")
    if st.button("Guardar en Catering", use_container_width=True):
        if nombre:
            st.session_state["proyectos"][proyecto]["catering"].append({"nombre": nombre, "dieta": dieta, "alergias": alergias})
            guardar_y_recargar()

@st.dialog("🛒 Solicitar Equipo")
def ventana_pedido(proyecto, area):
    item_nombre = st.text_input("Equipo Solicitado")
    justificacion = st.text_area("Notas (Para qué escena o uso)")
    if st.button("Enviar Pedido", use_container_width=True):
        if item_nombre:
            st.session_state["proyectos"][proyecto]["pedidos_equipos"].append({"area": area, "item": item_nombre, "notas": justificacion, "estado": "Pendiente"})
            guardar_y_recargar()

@st.dialog("🎥 Cargar Equipo Directo")
def ventana_equipo(proyecto, area):
    col1, col2 = st.columns(2)
    item_nombre = col1.text_input("Equipo")
    cantidad = col2.number_input("Cantidad", min_value=1, value=1)
    tipo = col1.selectbox("Condición", ["Propio", "Alquilado"])
    rental = col2.text_input("Rental", disabled=(tipo=="Propio"))
    if st.button("Guardar Equipo", use_container_width=True):
        if item_nombre:
            st.session_state["proyectos"][proyecto]["equipos"].append({"area": area, "item": item_nombre, "cant": cantidad, "tipo": tipo, "rental": rental if tipo == "Alquilado" else "N/A"})
            guardar_y_recargar()

@st.dialog("📝 Nota de Continuidad")
def ventana_continuidad(proyecto):
    c1, c2 = st.columns(2)
    escena = c1.text_input("Escena N°")
    toma = c2.text_input("Toma N°")
    detalle = st.text_area("Detalle de raccord")
    if st.button("Guardar Registro", use_container_width=True):
        if escena and detalle:
            st.session_state["proyectos"][proyecto]["continuidad"].append({"escena": escena, "toma": toma, "detalle": detalle})
            guardar_y_recargar()

@st.dialog("🎨 Cargar Arte")
def ventana_arte(proyecto):
    categoria = st.radio("Categoría:", ["🪑 Utilería", "👗 Vestuario"], horizontal=True)
    objeto = st.text_input("Objeto o Prenda")
    responsable = st.text_input("Responsable")
    estado = st.selectbox("Estado", ["🔴 Pendiente", "🟢 Listo en Set"])
    foto_subida = st.file_uploader("Foto de referencia", type=["jpg", "png", "jpeg"])
    if st.button("Guardar Elemento", use_container_width=True):
        if objeto:
            foto_base64 = base64.b64encode(foto_subida.read()).decode('utf-8') if foto_subida else None
            st.session_state["proyectos"][proyecto]["arte"].append({"categoria": categoria, "objeto": objeto, "responsable": responsable, "estado": estado, "foto": foto_base64})
            guardar_y_recargar()

@st.dialog("🎬 Diseñar Plano")
def ventana_plano(proyecto):
    c1, c2 = st.columns(2)
    escena = c1.text_input("Escena")
    toma = c2.text_input("Plano N°")
    tamano = st.selectbox("Tamaño", ["PG", "PE", "PM", "PP", "PD"])
    movimiento = st.selectbox("Movimiento", ["Fijo", "Cámara en Mano", "Paneo", "Tilt", "Tracking", "Steady"])
    if st.button("Agregar Plano", use_container_width=True):
        if escena:
            st.session_state["proyectos"][proyecto]["planos"].append({"escena": escena, "toma": toma, "tamano": tamano, "movimiento": movimiento})
            guardar_y_recargar()

@st.dialog("⏱️ Cargar Actividad (Cronograma)")
def ventana_cronograma(proyecto):
    hora = st.time_input("Hora")
    actividad = st.text_input("Actividad (Ej: Armado, Rodaje)")
    if st.button("Sumar al Cronograma", use_container_width=True):
        if actividad:
            st.session_state["proyectos"][proyecto]["plan_rodaje"].append({"hora": str(hora), "actividad": actividad})
            guardar_y_recargar()

@st.dialog("🎧 Reporte de Sonido")
def ventana_sonido(proyecto):
    c1, c2 = st.columns(2)
    escena = c1.text_input("Escena")
    toma = c2.text_input("Toma")
    pistas = st.text_area("Detalle de Pistas")
    obs = st.text_input("Observaciones")
    if st.button("Guardar Reporte", use_container_width=True):
        if escena:
            st.session_state["proyectos"][proyecto]["sonido_log"].append({"escena": escena, "toma": toma, "pistas": pistas, "obs": obs})
            guardar_y_recargar()

@st.dialog("📋 Registrar Toma (DIR)")
def ventana_toma_dir(proyecto):
    c1, c2 = st.columns(2)
    escena = c1.text_input("Escena")
    toma = c2.text_input("Toma")
    evaluacion = st.radio("Evaluación", ["⭕ BUENA", "❌ Mala", "⚠️ Regular"], horizontal=True)
    if st.button("Guardar Toma", use_container_width=True):
        if escena:
            st.session_state["proyectos"][proyecto]["tomas_dir"].append({"escena": escena, "toma": toma, "evaluacion": evaluacion})
            guardar_y_recargar()

@st.dialog("👤 Ficha de Personaje")
def ventana_personaje(proyecto):
    nombre = st.text_input("Nombre")
    rol = st.selectbox("Arquetipo", ["Protagonista", "Antagonista", "Secundario"])
    objetivo = st.text_input("Objetivo")
    conflicto = st.text_area("Conflicto")
    if st.button("Guardar", use_container_width=True):
        if nombre:
            st.session_state["proyectos"][proyecto]["personajes"].append({"nombre": nombre, "rol": rol, "objetivo": objetivo, "conflicto": conflicto})
            guardar_y_recargar()

@st.dialog("🔗 Agregar Link / Referencia")
def ventana_link(proyecto):
    titulo = st.text_input("Título (Ej: Corto Anterior)")
    url = st.text_input("URL (Link)")
    desc = st.text_input("Descripción rápida")
    if st.button("Guardar Link", use_container_width=True):
        if titulo and url:
            st.session_state["proyectos"][proyecto]["links"].append({"titulo": titulo, "url": url, "desc": desc})
            guardar_y_recargar()

@st.dialog("💸 Cargar Gasto")
def ventana_presupuesto(proyecto):
    item = st.text_input("Ítem")
    costo = st.number_input("Costo ($)", min_value=0.0)
    area = st.selectbox("Área", ["Técnica", "Arte", "Producción", "Catering", "Transporte"])
    estado = st.selectbox("Estado", ["Pendiente", "Pagado"])
    if st.button("Cargar Gasto", use_container_width=True):
        if item:
            st.session_state["proyectos"][proyecto]["presupuesto"].append({"item": item, "costo": costo, "area": area, "estado": estado})
            guardar_y_recargar()

@st.dialog("🎭 Ficha de Casting")
def ventana_casting(proyecto):
    actor = st.text_input("Nombre del Actor/Actriz")
    personaje = st.text_input("Personaje")
    reel = st.text_input("Link a Reel")
    foto = st.file_uploader("Foto (Headshot)", type=["jpg", "png", "jpeg"])
    if st.button("Guardar Casting", use_container_width=True):
        if actor:
            foto_base64 = base64.b64encode(foto.read()).decode('utf-8') if foto else None
            st.session_state["proyectos"][proyecto]["casting"].append({"actor": actor, "personaje": personaje, "reel": reel, "foto": foto_base64})
            guardar_y_recargar()

@st.dialog("📖 Desglosar Escena")
def ventana_desglose(proyecto):
    c1, c2, c3 = st.columns(3)
    escena = c1.text_input("Escena N°")
    intext = c2.selectbox("Ubicación", ["INT", "EXT", "INT/EXT"])
    dianoche = c3.selectbox("Tiempo", ["DÍA", "NOCHE", "ATARDECER"])
    desc = st.text_area("Descripción de la Acción")
    if st.button("Guardar Desglose", use_container_width=True):
        if escena:
            st.session_state["proyectos"][proyecto]["desglose"].append({"escena": escena, "intext": intext, "dianoche": dianoche, "desc": desc})
            guardar_y_recargar()

@st.dialog("🏬 Nuevo Rental (Directorio)")
def ventana_nuevo_rental(proyecto):
    nombre = st.text_input("Nombre del Rental")
    url = st.text_input("Link web, Instagram o WhatsApp")
    if st.button("Guardar en Directorio", use_container_width=True):
        if nombre:
            st.session_state["proyectos"][proyecto]["directorio_rentals"].append({"nombre": nombre, "url": url})
            guardar_y_recargar()

@st.dialog("🤖 Extraer Equipos (IA)")
def ventana_comparador_rental(proyecto):
    directorio = st.session_state["proyectos"][proyecto].get("directorio_rentals", [])
    if not directorio:
        st.warning("⚠️ Primero agregá un Rental desde 'Nuevo Rental'.")
        return
        
    nombres_rentals = [r["nombre"] for r in directorio]
    rental_elegido = st.selectbox("📌 ¿A qué rental pertenecen?", nombres_rentals)
    url_rental_elegido = next((r["url"] for r in directorio if r["nombre"] == rental_elegido), "#")

    tab_url, tab_excel, tab_img = st.tabs(["🔗 Link Web", "📊 Excel/CSV", "📸 Imagen"])
    
    with tab_url:
        url_producto = st.text_input("🔗 URL de los productos")
        if st.button("Escanear URL", use_container_width=True):
            if url_producto:
                with st.spinner("Navegando y analizando..."):
                    try:
                        headers = {'User-Agent': 'Mozilla/5.0'}
                        req = requests.get(url_producto, headers=headers, timeout=15)
                        soup = BeautifulSoup(req.text, 'html.parser')
                        texto_web = soup.get_text(separator=' ', strip=True)[:20000] 
                        
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        modelo = genai.GenerativeModel('gemini-3.5-flash')
                        prompt = f"Extrae datos a JSON. Regla: Precio solo numero. Formato: [{{\"nombre\": \"\", \"precio\": 0, \"estado\": \"Disponible\", \"url\": \"{url_producto}\", \"foto\": \"\"}}]\nTexto: {texto_web}"
                        respuesta = modelo.generate_content(prompt)
                        productos_extraidos = json.loads(respuesta.text.strip().replace("```json", "").replace("```", ""))
                        if productos_extraidos:
                            for prod in productos_extraidos:
                                prod.update({"rental": rental_elegido, "url_rental": url_rental_elegido})
                                st.session_state["proyectos"][proyecto]["comparador_rentals"].append(prod)
                            guardar_y_recargar()
                        else: st.warning("Sin resultados claros.")
                    except Exception as e: st.error(f"Error: {e}")

    with tab_excel:
        archivo_ex = st.file_uploader("Archivo (.xlsx o .csv)", type=["xlsx", "csv"])
        if st.button("Procesar Archivo", use_container_width=True):
            if archivo_ex:
                with st.spinner("Procesando datos..."):
                    try:
                        df = pd.read_csv(archivo_ex) if archivo_ex.name.endswith('.csv') else pd.read_excel(archivo_ex)
                        texto_datos = df.to_csv(index=False)[:20000]
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        modelo = genai.GenerativeModel('gemini-3.5-flash')
                        prompt = f"Extrae a JSON. Precio solo num. Formato: [{{\"nombre\": \"\", \"precio\": 0, \"estado\": \"Disponible\", \"url\": \"{url_rental_elegido}\", \"foto\": \"\"}}]\nDatos: {texto_datos}"
                        respuesta = modelo.generate_content(prompt)
                        productos_extraidos = json.loads(respuesta.text.strip().replace("```json", "").replace("```", ""))
                        if productos_extraidos:
                            for prod in productos_extraidos:
                                prod.update({"rental": rental_elegido, "url_rental": url_rental_elegido})
                                st.session_state["proyectos"][proyecto]["comparador_rentals"].append(prod)
                            guardar_y_recargar()
                    except Exception as e: st.error(f"Error: {e}")

    with tab_img:
        archivo_img = st.file_uploader("Subir Imagen de Lista", type=["jpg", "png", "jpeg"])
        if st.button("Analizar Foto", use_container_width=True):
            if archivo_img:
                with st.spinner("Visión IA analizando..."):
                    try:
                        img = Image.open(archivo_img)
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        modelo = genai.GenerativeModel('gemini-3.5-flash')
                        prompt = f"Extrae a JSON. Precio solo num. Formato: [{{\"nombre\": \"\", \"precio\": 0, \"estado\": \"Disponible\", \"url\": \"{url_rental_elegido}\", \"foto\": \"\"}}]"
                        respuesta = modelo.generate_content([prompt, img])
                        productos_extraidos = json.loads(respuesta.text.strip().replace("```json", "").replace("```", ""))
                        if productos_extraidos:
                            for prod in productos_extraidos:
                                prod.update({"rental": rental_elegido, "url_rental": url_rental_elegido})
                                st.session_state["proyectos"][proyecto]["comparador_rentals"].append(prod)
                            guardar_y_recargar()
                    except Exception as e: st.error(f"Error: {e}")

@st.dialog("🚀 Checkout (Resumen)")
def ventana_checkout(proyecto):
    carrito = st.session_state["proyectos"][proyecto]["carrito_rentals"]
    directorio = st.session_state["proyectos"][proyecto].get("directorio_rentals", [])
    if not carrito: return st.warning("El carrito está vacío.")
        
    rentals_agrupados = {}
    for item in carrito:
        r_name = item.get("rental", "Desconocido")
        if r_name not in rentals_agrupados: rentals_agrupados[r_name] = []
        rentals_agrupados[r_name].append(item)
        
    for r_name, items in rentals_agrupados.items():
        with st.container(border=True):
            st.markdown(f"### 🏬 {r_name}")
            total_r = sum(i['precio'] for i in items)
            for i in items: st.write(f"- {i['nombre']} **(${i['precio']:,.2f})**")
            st.success(f"**Subtotal: ${total_r:,.2f} / día**")
            link_rental = next((d["url"] for d in directorio if d["nombre"] == r_name), None)
            if link_rental:
                st.markdown(f"<a href='{link_rental}' target='_blank' style='background-color:#6366f1; color:white; padding:10px 15px; text-decoration:none; border-radius:8px; font-weight:bold; display:inline-block; margin-top:10px;'>👉 CONTACTAR A {r_name.upper()}</a>", unsafe_allow_html=True)

@st.dialog("⚠️ Vaciar Comparador")
def ventana_vaciar_comparador(proyecto):
    st.warning("¿Seguro que querés borrar TODOS los equipos escaneados y vaciar el carrito?")
    if st.button("🚨 Sí, purgar datos", use_container_width=True):
        st.session_state["proyectos"][proyecto]["comparador_rentals"] = []
        st.session_state["proyectos"][proyecto]["carrito_rentals"] = []
        guardar_y_recargar()

# --- 5. GESTIÓN DE SESIÓN ---
if "usuario_logueado" not in st.session_state:
    st.session_state["usuario_logueado"] = None

# --- 6. PANTALLA DE ACCESO Y REGISTRO (REDESIGN PREMIUM) ---
if st.session_state["usuario_logueado"] is None:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; font-size: 3rem;'>Fetén<br><span style='font-size: 1.2rem; letter-spacing: 4px; color: #94a3b8;'>WORKSPACE</span></h1>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        tab_login, tab_registro = st.tabs(["🔑 Autenticación", "📝 Solicitar Acceso"])
        db_users = st.session_state["proyectos"]["_CONFIG_"]["usuarios"]
        
        with tab_login:
            with st.container(border=True):
                email_ingreso = st.text_input("Correo corporativo", placeholder="ejemplo@productora.com").lower().strip()
                pass_ingreso = st.text_input("Contraseña", type="password", placeholder="••••••••")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("INICIAR SESIÓN", use_container_width=True, type="primary"):
                    if email_ingreso in db_users:
                        if db_users[email_ingreso]["pass"] == pass_ingreso:
                            if db_users[email_ingreso].get("estado") == "Aprobado":
                                st.session_state["usuario_logueado"] = email_ingreso
                                st.session_state["ruta"] = "Inicio"
                                st.rerun()
                            else: st.warning("⏳ Cuenta en revisión por el Administrador.")
                        else: st.error("Contraseña incorrecta.")
                    else: st.error("Usuario no encontrado.")
                        
        with tab_registro:
            with st.container(border=True):
                nombre_reg = st.text_input("Nombre Completo")
                email_reg = st.text_input("Correo (Real)").lower().strip()
                pass_reg = st.text_input("Crear Contraseña", type="password")
                st.info("📸 Foto de Perfil (Obligatoria para la credencial):")
                foto_reg = st.file_uploader("Foto de Perfil", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("ENVIAR SOLICITUD", use_container_width=True, type="primary"):
                    if nombre_reg and email_reg and pass_reg and foto_reg:
                        if "@" not in email_reg or "." not in email_reg:
                            st.error("⚠️ Correo inválido.")
                        elif email_reg in db_users:
                            st.error("Correo ya registrado.")
                        else:
                            foto_b64 = base64.b64encode(foto_reg.read()).decode('utf-8')
                            db_users[email_reg] = {
                                "nombre": nombre_reg, "pass": pass_reg, "rol": "Invitado", "nivel": "lectura", "estado": "Pendiente",
                                "foto": foto_b64, "credencial": f"FTN-{random.randint(1000, 9999)}", "edad": "", "roles_fav": "", "dieta": "", "specs": "", "cv": "", "portfolio": ""
                            }
                            guardar_y_recargar()
                            st.success("¡Solicitud enviada! Espera la aprobación.")
                    else: st.error("Completá todos los campos.")

# --- 7. PLATAFORMA CENTRAL (MODO DASHBOARD) ---
else:
    usuario_actual = st.session_state["usuario_logueado"]
    db_users = st.session_state["proyectos"]["_CONFIG_"]["usuarios"]
    
    if usuario_actual not in db_users or db_users[usuario_actual].get("estado") != "Aprobado":
        st.error("⚠️ Tu cuenta fue bloqueada o no está aprobada.")
        if st.button("Salir"):
            st.session_state["usuario_logueado"] = None
            st.rerun()
        st.stop()

    mis_datos = db_users[usuario_actual]
    rol_actual = mis_datos["rol"]
    nivel_actual = mis_datos["nivel"]
    
    # --- NAVBAR SUPERIOR ---
    c_head_left, c_head_space, c_head_right = st.columns([2, 5, 1])
    with c_head_left:
        if st.session_state["ruta"] != "Inicio":
            if st.button("⬅️ VOLVER AL DASHBOARD", type="secondary"):
                st.session_state["ruta"] = "Inicio"
                st.rerun()
        else:
            st.markdown("<h2 style='margin:0; padding-top:10px;'>Fetén.</h2>", unsafe_allow_html=True)
            
    with c_head_right:
        foto_src = f"data:image/jpeg;base64,{mis_datos['foto']}" if mis_datos.get("foto") else "https://via.placeholder.com/150"
        st.markdown(f"<img src='{foto_src}' class='avatar-circle' style='float:right;'>", unsafe_allow_html=True)
        if st.button("Mi Perfil", key="btn_mi_perfil"):
            st.session_state["ruta"] = "Perfil"
            st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # VISTA 1: DASHBOARD (HOME)
    # ==========================================
    if st.session_state["ruta"] == "Inicio":
        st.markdown(f"<h1 style='margin-bottom:0px;'>Bienvenido, {mis_datos['nombre']}.</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#818cf8 !important; font-weight:600; font-size:1.1rem;'>{rol_actual.upper()}</p>", unsafe_allow_html=True)
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        c_main, c_side = st.columns([2.5, 1])
        
        with c_main:
            c_title, c_btn_new = st.columns([3, 1])
            with c_title: st.markdown("### Proyectos Activos")
            with c_btn_new:
                if nivel_actual in ["jefe", "jefe_supremo"]:
                    with st.popover("➕ Nuevo Proyecto"):
                        nuevo_proyecto = st.text_input("Nombre del Film/Spot:")
                        if st.button("Crear Workspace"):
                            if nuevo_proyecto and nuevo_proyecto not in st.session_state["proyectos"]:
                                st.session_state["proyectos"][nuevo_proyecto] = {
                                    "contexto_aprobado": "Proyecto nuevo.", "archivos_pendientes": [], "avisos": [], "equipos": [], "pedidos_equipos": [], "continuidad": [], 
                                    "arte": [], "planos": [], "plan_rodaje": [], "plantas_luces": [], "sonido_log": [], "tomas_dir": [], "personajes": [], "locaciones": [], "crew": [], "catering": [], "links": [], "presupuesto": [], "casting": [], "desglose": [], "comparador_rentals": [], "carrito_rentals": [], "directorio_rentals": []
                                }
                                guardar_y_recargar()
            
            lista_proyectos = [p for p in st.session_state["proyectos"].keys() if p != "_CONFIG_"]
            if not lista_proyectos:
                st.info("No hay proyectos en curso.")
            else:
                cols_grid = st.columns(2)
                for idx, proy in enumerate(lista_proyectos):
                    with cols_grid[idx % 2]:
                        with st.container(border=True):
                            st.markdown(f"<h2>{proy}</h2>", unsafe_allow_html=True)
                            st.caption(f"👥 {len(st.session_state['proyectos'][proy]['crew'])} Crew | 🎥 {len(st.session_state['proyectos'][proy]['equipos'])} Equipos")
                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button("INGRESAR", key=f"entrar_{proy}", use_container_width=True, type="primary"):
                                st.session_state["proyecto_activo"] = proy
                                st.session_state["ruta"] = "Proyecto"
                                st.rerun()

        with c_side:
            st.markdown("### Agenda Central")
            if st.button("➕ Agendar Tarea", use_container_width=True):
                ventana_recordatorio(es_admin=(nivel_actual in ["jefe_supremo", "jefe"]), autor=mis_datos['nombre'])
            
            recordatorios = st.session_state["proyectos"]["_CONFIG_"].get("recordatorios", [])
            for rec in reversed(recordatorios):
                if rec["tipo"] == "Global (Toda la productora)" or rec["autor"] == mis_datos["nombre"]:
                    with st.container(border=True):
                        color_t = "#818cf8" if "Global" in rec["tipo"] else "#94a3b8"
                        st.markdown(f"<span style='color:{color_t}; font-size:12px; font-weight:bold;'>{rec['fecha']}</span>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-weight:600; font-size:15px; color:white;'>{rec['titulo']}</div>", unsafe_allow_html=True)
                        st.caption(f"Por: {rec['autor']}")

    # ==========================================
    # VISTA 2: PERFIL Y CREDENCIAL
    # ==========================================
    elif st.session_state["ruta"] == "Perfil":
        st.markdown("<h1>Centro de Usuario</h1>", unsafe_allow_html=True)
        tab_misdatos, tab_cred, tab_dir = st.tabs(["⚙️ Ajustes", "🪪 Black Card (ID)", "👥 Directorio Corporativo"])
        
        with tab_misdatos:
            with st.container(border=True):
                with st.form("form_perfil"):
                    c1, c2 = st.columns(2)
                    edad = c1.text_input("Edad", value=mis_datos.get("edad", ""))
                    roles_fav = c2.text_input("Especialidad principal", value=mis_datos.get("roles_fav", ""))
                    dieta_opciones = ["Ninguna", "Vegetariano/a", "Vegano/a", "Celíaco/a", "Diabético/a"]
                    idx_dieta = dieta_opciones.index(mis_datos.get("dieta", "Ninguna")) if mis_datos.get("dieta") in dieta_opciones else 0
                    dieta = c1.selectbox("Dieta / Catering", dieta_opciones, index=idx_dieta)
                    portfolio = c2.text_input("Link a Reel / Portfolio", value=mis_datos.get("portfolio", ""))
                    specs = st.text_area("Habilidades técnicas detalladas", value=mis_datos.get("specs", ""))
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button("Guardar Cambios", use_container_width=True):
                        db_users[usuario_actual].update({"edad": edad, "roles_fav": roles_fav, "dieta": dieta, "portfolio": portfolio, "specs": specs})
                        guardar_y_recargar()
                        st.success("Datos sincronizados.")
                
                st.divider()
                if st.button("Cerrar Sesión Oficial", type="secondary"):
                    st.session_state["usuario_logueado"] = None
                    st.session_state["ruta"] = "Inicio"
                    st.rerun()

        with tab_cred:
            foto_cred = f"data:image/jpeg;base64,{mis_datos['foto']}" if mis_datos.get("foto") else "https://via.placeholder.com/150"
            st.markdown(f"""
                <div class="credencial-feten">
                    <div class="credencial-logo">FETÉN STUDIOS</div>
                    <img src="{foto_cred}" class="credencial-img">
                    <h2 class="credencial-name">{mis_datos['nombre']}</h2>
                    <p class="credencial-role">{mis_datos['rol']}</p>
                    <div class="credencial-id-box">
                        <span class="credencial-id">ID: {mis_datos.get('credencial', 'FTN-0000')}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with tab_dir:
            busqueda = st.text_input("🔎 Buscar talento...", placeholder="Director, Sonido, Laura...")
            st.markdown("<br>", unsafe_allow_html=True)
            for em, info in db_users.items():
                if info["estado"] == "Aprobado" and (busqueda.lower() in info["nombre"].lower() or busqueda.lower() in info["rol"].lower()):
                    with st.container(border=True):
                        colD1, colD2 = st.columns([1, 8])
                        with colD1:
                            if info.get("foto"): st.markdown(f"<img src='data:image/jpeg;base64,{info['foto']}' class='avatar-circle' style='width:60px;height:60px;'>", unsafe_allow_html=True)
                        with colD2:
                            st.markdown(f"<h4 style='margin:0;'>{info['nombre']} <span style='color:#818cf8;font-size:14px;'>({info['rol']})</span></h4>", unsafe_allow_html=True)
                            st.caption(f"**Specs:** {info.get('specs', 'No especificado')}")
                            if info.get("portfolio"): st.markdown(f"[🔗 Ver Reel]({info['portfolio']})")

    # ==========================================
    # VISTA 3: PROYECTO (LAYOUT DE PANELES)
    # ==========================================
    elif st.session_state["ruta"] == "Proyecto":
        proyecto_elegido = st.session_state["proyecto_activo"]
        p_data = st.session_state["proyectos"][proyecto_elegido]
        
        st.markdown(f"<h1 style='margin-bottom:20px;'>{proyecto_elegido}</h1>", unsafe_allow_html=True)
        
        # --- NUEVO DISEÑO: MENÚ LATERAL IZQUIERDO vs CONTENIDO (Estilo Notion/Linear) ---
        col_nav, col_content = st.columns([1, 3.5], gap="large")
        
        opciones_nav = ["📊 Panel General", "⚡ Asistente IA"]
        if nivel_actual != "lectura": opciones_nav.append("🛒 Solicitar a Prod.")
        opciones_nav.extend(["🛍️ Rentals Automáticos", "📁 Archivos (Baúl)", "📢 Tablón", "🔗 Enlaces"])
        
        if rol_actual == "Super Admin":
            opciones_nav.extend([
                "⚙️ Permisos", "💰 Presupuesto", "📥 Bandeja Producción", "📍 Scouting", "👥 Base Crew", "🎭 Casting", "🍽️ Catering",
                "📖 Script Breakdown", "🧪 Guion", "📦 Inventario", "⏱️ Plan Rodaje", "🎬 Monitor Director", "📐 Luces (Canvas)", "🧠 Ref. IA",
                "🎨 Arte & Vestuario", "🎧 Sonido", "📝 Raccord"
            ])
        else:
            if rol_actual == "Producción": opciones_nav.extend(["💰 Presupuesto", "📥 Bandeja Producción", "📍 Scouting", "👥 Base Crew", "🎭 Casting", "🍽️ Catering"])
            else:
                if nivel_actual != "lectura": opciones_nav.extend(["📦 Inventario"])
            if rol_actual == "Guion": opciones_nav.extend(["📖 Script Breakdown", "🧪 Guion"])
            if "Dirección" in rol_actual and rol_actual not in ["Dirección de Arte", "Dirección de Fotografía"]: opciones_nav.extend(["🎭 Casting", "⏱️ Plan Rodaje", "🎬 Monitor Director"])
            if rol_actual == "Dirección de Fotografía": opciones_nav.extend(["📐 Luces (Canvas)", "🧠 Ref. IA"])
            if rol_actual == "Dirección de Arte": opciones_nav.append("🎨 Arte & Vestuario")
            if "Sonido" in rol_actual: opciones_nav.extend(["🎧 Sonido"])
            if rol_actual == "Continuidad": opciones_nav.append("📝 Raccord")

        with col_nav:
            st.markdown("<p style='font-size:11px; font-weight:700; letter-spacing:1px; color:#64748b;'>DEPARTAMENTOS</p>", unsafe_allow_html=True)
            # Acá ocurre la magia CSS: st.radio se ve como un menú de botones elegantes
            seccion_elegida = st.radio("", opciones_nav, label_visibility="collapsed")
        
        with col_content:
            # --- LÓGICA DE LOS MÓDULOS ---
            if seccion_elegida == "📊 Panel General":
                c1, c2, c3, c4 = st.columns(4)
                with c1: st.metric("Miembros", len(p_data["crew"]))
                with c2: st.metric("Lugares", len(p_data["locaciones"]))
                with c3: st.metric("Fierros", len(p_data["equipos"]))
                with c4: st.metric("Pedidos", len(p_data["pedidos_equipos"]))
                
                st.divider()
                st.markdown("### ⚡ Call Sheet Generator")
                c_btn1, c_btn2, c_btn3 = st.columns([1, 2, 1])
                with c_btn2:
                    if st.button("Generar Plan del Día (IA)", use_container_width=True):
                        try:
                            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                            modelo = genai.GenerativeModel('gemini-3.5-flash')
                            datos = f"Avisos: {p_data['avisos']} | Equipo: {p_data['crew']} | Locaciones: {p_data['locaciones']}"
                            prompt = f"Sos FTN AI. Proyecto: {proyecto_elegido}. Datos: {datos}. Redactá un Call Sheet ultra profesional en markdown."
                            with st.spinner("Procesando la lógica del rodaje..."):
                                respuesta = modelo.generate_content(prompt)
                                st.success("Documento Generado:")
                                st.markdown(f"<div style='background:rgba(255,255,255,0.05); padding:20px; border-radius:15px;'>{respuesta.text}</div>", unsafe_allow_html=True)
                        except: st.error("Falta configurar la API Key de Gemini en Secrets.")

            elif seccion_elegida == "🛒 Solicitar a Prod.":
                colA, colB = st.columns([3, 1])
                with colA: st.markdown("<h2>Mis Solicitudes</h2>", unsafe_allow_html=True)
                with colB: 
                    if st.button("➕ Nuevo Pedido", use_container_width=True): ventana_pedido(proyecto_elegido, rol_actual)
                st.divider()
                mis_pedidos = [p for p in p_data["pedidos_equipos"] if p["area"] == rol_actual or rol_actual == "Super Admin"]
                if not mis_pedidos: st.info("Bandeja vacía.")
                for ped in mis_pedidos:
                    with st.container(border=True):
                        st.write(f"**{ped['item']}** — {ped['notas']}")
                        if ped['estado'] == "Pendiente": st.warning("🕒 Pendiente")
                        elif ped['estado'] == "Aprobado": st.success("✅ Aprobado")
                        else: st.error(f"❌ {ped['estado']}")

            elif seccion_elegida == "📥 Bandeja Producción":
                st.markdown("<h2>Control de Aprobaciones</h2>", unsafe_allow_html=True)
                if not p_data["pedidos_equipos"]: st.info("Todo al día.")
                for i, ped in enumerate(p_data["pedidos_equipos"]):
                    if ped['estado'] == "Pendiente":
                        with st.container(border=True):
                            st.markdown(f"**Área:** {ped['area']} | **Ítem:** {ped['item']}")
                            st.caption(f"Razón: {ped['notas']}")
                            c1, c2 = st.columns(2)
                            if c1.button("✅ Aprobar e Inventariar", key=f"p_ap_{i}", use_container_width=True):
                                p_data["equipos"].append({"area": ped['area'], "item": ped['item'], "cant": 1, "tipo": "A Confirmar", "rental": "A Definir"})
                                p_data["pedidos_equipos"][i]["estado"] = "Aprobado"
                                guardar_y_recargar()
                            if c2.button("❌ Denegar", key=f"p_re_{i}", use_container_width=True):
                                p_data["pedidos_equipos"][i]["estado"] = "Rechazado"
                                guardar_y_recargar()

            elif seccion_elegida == "🛍️ Rentals Automáticos":
                colA, colB, colC = st.columns([2, 1, 1])
                with colA: st.markdown("<h2>Comparador IA</h2>", unsafe_allow_html=True)
                with colB: 
                    if st.button("🏬 Add Casa", use_container_width=True): ventana_nuevo_rental(proyecto_elegido)
                with colC: 
                    if st.button("🤖 Escanear Web", use_container_width=True): ventana_comparador_rental(proyecto_elegido)
                if rol_actual == "Super Admin" and st.button("🗑️ Resetear BD Rentals", type="secondary"): ventana_vaciar_comparador(proyecto_elegido)
                
                st.divider()
                carrito = p_data.get("carrito_rentals", [])
                if len(carrito) > 0:
                    with st.container(border=True):
                        c_txt, c_btn = st.columns([3, 1])
                        with c_txt: st.markdown("<h3 style='margin:0;'>🛒 Carrito Master</h3>", unsafe_allow_html=True)
                        with c_btn:
                            if st.button("✅ CHECKOUT", use_container_width=True, type="primary"): ventana_checkout(proyecto_elegido)
                        
                        cols_cart = st.columns(3)
                        total_cart = 0
                        for i, item in enumerate(carrito):
                            total_cart += item["precio"]
                            with cols_cart[i % 3]:
                                with st.container(border=True):
                                    st.markdown(f"<p style='font-size:10px; font-weight:bold; color:#818cf8; margin:0;'>{item.get('rental', 'N/A')}</p>", unsafe_allow_html=True)
                                    st.markdown(f"<p style='font-weight:700; margin:0;'>{item['nombre'][:30]}...</p>", unsafe_allow_html=True)
                                    st.markdown(f"**${item['precio']:,.2f}**")
                                    if st.button("Quitar", key=f"quit_cart_{i}", use_container_width=True):
                                        p_data["carrito_rentals"].pop(i)
                                        guardar_y_recargar()
                        st.markdown(f"<h3 style='text-align:right; color:#a5b4fc;'>Subtotal Día: ${total_cart:,.2f}</h3>", unsafe_allow_html=True)
                
                st.markdown("### 🔍 Catálogo Analizado")
                rentals_lista = p_data.get("comparador_rentals", [])
                if not rentals_lista: st.info("Usá el botón 'Escanear Web' para cargar precios usando IA.")
                else:
                    texto_busqueda = st.text_input("Buscador rápido (Ej: Alexa, Skypanel)...")
                    rentals_mostrar = [(idx, r) for idx, r in enumerate(rentals_lista) if texto_busqueda.lower() in r['nombre'].lower()]
                    if rentals_mostrar:
                        precios_validos = [r["precio"] for _, r in rentals_mostrar if r["precio"] > 0]
                        menor_precio = min(precios_validos) if precios_validos else 0

                        cols = st.columns(2)
                        for i, (idx_orig, r) in enumerate(rentals_mostrar):
                            with cols[i % 2]:
                                with st.container(border=True):
                                    if r["precio"] == menor_precio and r["precio"] > 0:
                                        st.markdown("<span style='background:#10b981; color:white; padding:3px 10px; border-radius:8px; font-size:10px; font-weight:800;'>MÁS BARATO</span>", unsafe_allow_html=True)
                                    st.markdown(f"<p style='font-size:11px; font-weight:bold; color:#818cf8; margin:0; margin-top:5px;'>{r.get('rental', 'N/A')}</p>", unsafe_allow_html=True)
                                    st.markdown(f"<h4 style='margin:0;'>{r['nombre']}</h4>", unsafe_allow_html=True)
                                    st.markdown(f"<h3 style='margin:0; color:#f8fafc;'>${r['precio']:,.2f}</h3>", unsafe_allow_html=True)
                                    c_add, c_del = st.columns(2)
                                    if c_add.button("Sumar al carrito", key=f"add_{idx_orig}", use_container_width=True, type="primary"):
                                        p_data["carrito_rentals"].append(r)
                                        guardar_y_recargar()
                                    if c_del.button("Eliminar", key=f"del_{idx_orig}", use_container_width=True):
                                        p_data["comparador_rentals"].pop(idx_orig)
                                        guardar_y_recargar()
                    else: st.warning("Sin resultados.")

            elif seccion_elegida == "📐 Luces (Canvas)":
                st.markdown("<h2>Mesa de Diseño DF</h2>", unsafe_allow_html=True)
                col_h, col_c = st.columns([1, 2.5])
                with col_h:
                    st.markdown("**Tools**")
                    modo = st.selectbox("Trazado", ["freedraw", "line", "rect", "circle", "transform"])
                    color_mapping = {"🟡 Principal": "#FFD700", "🔵 Relleno": "#1E90FF", "🟣 Contraluz": "#8A2BE2", "🔴 Actor": "#FF4500", "🎥 Cámara": "#FFFFFF"}
                    tipo = st.radio("Elemento", list(color_mapping.keys()))
                    grosor = st.slider("Grosor", 1, 10, 3)
                    if st.button("Guardar Ficha"): st.success("Capturado en BD.")
                with col_c:
                    st_canvas(fill_color="rgba(255,255,255,0)", stroke_width=grosor, stroke_color=color_mapping[tipo], background_color="#18181b", width=500, height=450, drawing_mode=modo, key="canvas_luces_pro")

            elif seccion_elegida == "⚙️ Permisos":
                st.markdown("<h2>Gestión de Usuarios</h2>", unsafe_allow_html=True)
                mapa = {"Super Admin": "jefe_supremo", "Producción": "jefe", "Dirección": "jefe", "Dirección de Fotografía": "jefe", "Dirección de Arte": "jefe", "Director de Sonido": "jefe", "Asistente de Sonido": "asistente", "Guion": "jefe", "Continuidad": "jefe", "Invitado": "lectura"}
                for em_usr, dt_usr in st.session_state["proyectos"]["_CONFIG_"]["usuarios"].items():
                    with st.container(border=True):
                        c1, c2, c3, c4 = st.columns([2, 1.5, 1.5, 1])
                        c1.markdown(f"**{dt_usr['nombre']}**<br><span style='font-size:12px; color:gray;'>{em_usr}</span>", unsafe_allow_html=True)
                        est = c2.selectbox("Estado", ["Aprobado", "Pendiente"], index=0 if dt_usr.get("estado") == "Aprobado" else 1, key=f"e_{em_usr}")
                        rol = c3.selectbox("Rol", list(mapa.keys()), index=list(mapa.keys()).index(dt_usr["rol"]) if dt_usr["rol"] in mapa else 9, key=f"r_{em_usr}")
                        if c4.button("Update", key=f"b_{em_usr}", use_container_width=True):
                            st.session_state["proyectos"]["_CONFIG_"]["usuarios"][em_usr].update({"estado": est, "rol": rol, "nivel": mapa[rol]})
                            guardar_y_recargar()

            elif seccion_elegida == "🔗 Enlaces":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Repositorio URL</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("➕ Add Link", use_container_width=True): ventana_link(proyecto_elegido)
                st.divider()
                for lk in p_data["links"]:
                    with st.container(border=True): st.markdown(f"### 🔗 [{lk['titulo']}]({lk['url']})\n{lk['desc']}")

            elif seccion_elegida == "💰 Presupuesto":
                c1, c2, c3 = st.columns([2, 1, 1])
                with c1: st.markdown("<h2>Flujo de Caja</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("➕ Add Gasto", use_container_width=True): ventana_presupuesto(proyecto_elegido)
                with c3:
                    if p_data["presupuesto"]: st.download_button("⬇️ Excel", data=pd.DataFrame(p_data["presupuesto"]).to_csv(index=False).encode('utf-8'), file_name="budget.csv", mime="text/csv", use_container_width=True)
                st.divider()
                total = sum(i['costo'] for i in p_data["presupuesto"])
                st.markdown(f"<h3 style='color:#10b981;'>Total Ejecutado: ${total:,.2f}</h3>", unsafe_allow_html=True)
                for item in p_data["presupuesto"]:
                    with st.container(border=True): st.markdown(f"**{item['estado']}** | ${item['costo']:,.2f} - {item['item']} ({item['area']})")

            elif seccion_elegida == "🎭 Casting":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Talentos</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("➕ Fichar", use_container_width=True): ventana_casting(proyecto_elegido)
                st.divider()
                cols = st.columns(2)
                for i, a in enumerate(p_data["casting"]):
                    with cols[i % 2]:
                        with st.container(border=True):
                            if a.get("foto"): st.image(base64.b64decode(a["foto"]), width=100)
                            st.markdown(f"### {a['actor']}\n**Rol:** {a['personaje']}\n[Ver Videobook]({a['reel']})")

            elif seccion_elegida == "📖 Script Breakdown":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Desglose Técnico</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("➕ Desglosar", use_container_width=True): ventana_desglose(proyecto_elegido)
                st.divider()
                for d in p_data["desglose"]:
                    with st.container(border=True): st.markdown(f"**ESC {d['escena']} | {d['intext']} | {d['dianoche']}**<br>{d['desc']}", unsafe_allow_html=True)

            elif seccion_elegida == "⏱️ Plan Rodaje":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Cronograma (AD)</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("➕ Bloque", use_container_width=True): ventana_cronograma(proyecto_elegido)
                st.divider()
                for a in sorted(p_data["plan_rodaje"], key=lambda x: x.get('hora', '00:00')):
                    with st.container(border=True): st.markdown(f"<h3 style='margin:0; color:#818cf8;'>{a.get('hora', '')}</h3><p style='margin:0; font-size:18px;'>{a['actividad']}</p>", unsafe_allow_html=True)

            elif seccion_elegida == "🧠 Ref. IA":
                st.markdown("<h2>Laboratorio Visual (Gemini)</h2>", unsafe_allow_html=True)
                try:
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    mod_foto = genai.GenerativeModel('gemini-3.5-flash')
                    msg_foto = st.chat_input("Prompt: Iluminación cyberpunk, Deakins...")
                    if msg_foto:
                        st.markdown(f"**Vos:** {msg_foto}")
                        resp = mod_foto.generate_content(f"Sos DF. Da referencias de: {msg_foto}")
                        st.info(f"**IA:** {resp.text}")
                except: st.error("Falta API Key de Gemini.")

            elif seccion_elegida == "📍 Scouting":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Locaciones</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("➕ Add", use_container_width=True): ventana_locacion(proyecto_elegido)
                st.divider()
                for loc in p_data["locaciones"]:
                    with st.container(border=True):
                        st.markdown(f"### 📍 {loc['nombre']}")
                        st.write(f"**Dir:** {loc['direccion']} | **Status:** {loc['permisos']}")
                        if loc['lat'] != 0.0: st.map(pd.DataFrame({'lat': [loc['lat']], 'lon': [loc['lon']]}), zoom=15, height=200)

            elif seccion_elegida == "👥 Base Crew":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Nómina Técnica</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("➕ Fichar", use_container_width=True): ventana_crew(proyecto_elegido)
                st.divider()
                for p in p_data["crew"]:
                    with st.container(border=True): st.markdown(f"**{p['nombre']}** — {p['rol']}")

            elif seccion_elegida == "🍽️ Catering":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Dietas</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("➕ Dieta", use_container_width=True): ventana_catering(proyecto_elegido)
                st.divider()
                for p in p_data["catering"]:
                    with st.container(border=True): st.markdown(f"**{p['nombre']}** | 🍽️ {p['dieta']}")

            elif seccion_elegida == "📢 Tablón":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Comunicados</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("➕ Avisar", use_container_width=True): ventana_aviso(proyecto_elegido, mis_datos['nombre'], p_data["locaciones"])
                st.divider()
                for aviso in reversed(p_data["avisos"]):
                    with st.container(border=True): st.markdown(f"**{aviso['autor']}**: {aviso.get('texto', 'Citación cargada.')}")

            elif seccion_elegida == "📁 Archivos (Baúl)":
                st.markdown("<h2>Documentos de Producción</h2>", unsafe_allow_html=True)
                archivo = st.file_uploader("Documento de texto (.txt)", type=["txt"])
                if archivo and st.button("Subir al Core IA"):
                    p_data["archivos_pendientes"].append({"autor": mis_datos['nombre'], "nombre": archivo.name, "texto": archivo.getvalue().decode('utf-8')})
                    guardar_y_recargar()
                    
                if len(p_data["archivos_pendientes"]) > 0:
                    st.markdown("### ⏳ Pendientes")
                    for i, doc in enumerate(p_data["archivos_pendientes"]):
                        with st.container(border=True):
                            st.write(f"📄 {doc['nombre']} ({doc['autor']})")
                            c1, c2 = st.columns(2)
                            if c1.button("✅ Aprobar", key=f"ap_{i}"):
                                p_data["contexto_aprobado"] += f"\n\n[Doc]: {doc['texto']}"
                                p_data["archivos_pendientes"].pop(i)
                                guardar_y_recargar()
                            if c2.button("❌ Borrar", key=f"re_{i}"):
                                p_data["archivos_pendientes"].pop(i)
                                guardar_y_recargar()

            elif seccion_elegida == "📦 Inventario":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Activos en Set</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("➕ Add Directo", use_container_width=True): ventana_equipo(proyecto_elegido, rol_actual)
                st.divider()
                for eq in p_data["equipos"]:
                    with st.container(border=True): st.markdown(f"**{eq['cant']}x {eq['item']}** | {eq['area']} | {eq['tipo']}")

            elif seccion_elegida == "🧪 Guion":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Personajes</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("➕ Arco Nuevo", use_container_width=True): ventana_personaje(proyecto_elegido)
                st.divider()
                for p in p_data["personajes"]:
                    with st.container(border=True): st.markdown(f"### {p['nombre']} ({p['rol']})")

            elif seccion_elegida == "🎨 Arte & Vestuario":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Departamento de Arte</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("➕ Prop/Prenda", use_container_width=True): ventana_arte(proyecto_elegido)
                st.divider()
                cols = st.columns(3)
                for i, item in enumerate(p_data["arte"]):
                    with cols[i % 3]:
                        with st.container(border=True):
                            st.markdown(f"**{item['estado']}** | {item['objeto']}")
                            if item.get("foto"): st.image(base64.b64decode(item["foto"]), use_container_width=True)

            elif seccion_elegida == "🎬 Monitor Director":
                c1, c2, c3 = st.columns([2, 1, 1])
                with c1: st.markdown("<h2>Log de Tomas</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("➕ Dis. Plano", use_container_width=True): ventana_plano(proyecto_elegido)
                with c3: 
                    if st.button("➕ Eval. Toma", use_container_width=True): ventana_toma_dir(proyecto_elegido)
                st.divider()
                for t in p_data["tomas_dir"]:
                    with st.container(border=True): st.markdown(f"{t['evaluacion']} | **ESC {t['escena']} - TOMA {t['toma']}**")

            elif seccion_elegida == "🎧 Sonido":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Planilla de Sonido</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("➕ Track", use_container_width=True): ventana_sonido(proyecto_elegido)
                st.divider()
                for s in reversed(p_data["sonido_log"]):
                    with st.container(border=True): st.markdown(f"🎧 **ESC {s['escena']} | T {s['toma']}**")

            elif seccion_elegida == "📝 Raccord":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Continuidad</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("➕ Nota", use_container_width=True): ventana_continuidad(proyecto_elegido)
                st.divider()
                for nota in reversed(p_data["continuidad"]):
                    with st.container(border=True): st.markdown(f"🎬 **ESC {nota['escena']} - T {nota['toma']}**<br>{nota['detalle']}", unsafe_allow_html=True)

            elif seccion_elegida == "⚡ Asistente IA":
                st.markdown("<h2>Chat de Producción (Gemini)</h2>", unsafe_allow_html=True)
                try:
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    modelo = genai.GenerativeModel('gemini-3.5-flash')
                    mensaje = st.chat_input("Consultar base de datos del guion o cronograma...")
                    if mensaje:
                        st.chat_message("user").write(mensaje)
                        resp = modelo.generate_content(f"Sos FTN AI. Hablás con: {mis_datos['nombre']}. Contexto: {p_data['contexto_aprobado']}\nUsuario: {mensaje}")
                        st.chat_message("assistant").write(resp.text)
                except: st.error("Falta configurar la API Key.")
