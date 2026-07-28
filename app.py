import streamlit as st
from streamlit_option_menu import option_menu
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
st.set_page_config(page_title="Fetén Workspace", page_icon="☀", layout="wide", initial_sidebar_state="collapsed")

LOGO_URL = "https://i.supaimg.com/4a90693e-1b41-4313-8203-f60c8b81825f/da7de7fd-3ded-4499-b3f4-790424f0dc5a.png"

# --- 2. DISEÑO UI/UX "STUDIO IVORY" (ADAPTADO AL LOGO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Animación de entrada general */
    @keyframes fadeUp {
        0% { opacity: 0; transform: translateY(15px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    .block-container {
        animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    /* Fondo Studio Ivory (Claro, cálido, orgánico) */
    .stApp {
        background-color: #FDFCF8 !important;
        background-image: radial-gradient(circle at 50% 0%, rgba(251, 175, 59, 0.05) 0%, transparent 60%) !important;
        color: #332F2C !important;
    }

    /* Títulos Orgánicos */
    h1, h2 {
        color: #B4713F !important; /* Marrón del logo */
        font-weight: 800 !important;
        letter-spacing: -1px !important;
    }
    h3, h4 { color: #2D2926 !important; font-weight: 700 !important; }
    p, span, div { color: #4A4541 !important; } /* Texto base gris cálido */

    /* Tarjetas Modulares (Blancas con sombras suaves cálidas) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border: 1px solid #EBE8E0 !important;
        border-radius: 20px !important;
        padding: 1.5rem !important;
        box-shadow: 0 10px 30px -15px rgba(180, 113, 63, 0.15) !important;
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #FBAF3B !important; /* Amarillo del logo */
        transform: translateY(-4px) !important;
        box-shadow: 0 15px 40px -10px rgba(251, 175, 59, 0.25) !important;
    }
    
    /* Inputs minimalistas claros */
    .stTextInput input, .stSelectbox select, .stNumberInput input, .stDateInput input, .stTimeInput input {
        background-color: #F9F8F4 !important;
        border: 1px solid #EBE8E0 !important;
        color: #332F2C !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        transition: all 0.3s ease !important;
    }
    .stTextInput input:focus, .stSelectbox select:focus {
        border-color: #B4713F !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 0 0 3px rgba(180, 113, 63, 0.15) !important;
    }
    
    /* Botones de alta conversión (Estilo Sol/Tierra) */
    .stButton button {
        background: linear-gradient(135deg, #FBAF3B 0%, #B4713F 100%) !important;
        border: none !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 6px 15px rgba(180, 113, 63, 0.3) !important;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #FFC15E 0%, #C7824E 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(251, 175, 59, 0.4) !important;
    }
    .stButton button p { color: white !important; font-weight: 600 !important; }

    /* Botones Secundarios (Outline) */
    [data-testid="stBaseButton-secondary"] {
        background: transparent !important;
        border: 2px solid #EBE8E0 !important;
        color: #B4713F !important;
        box-shadow: none !important;
    }
    [data-testid="stBaseButton-secondary"]:hover {
        border-color: #B4713F !important;
        background: rgba(180, 113, 63, 0.05) !important;
    }
    [data-testid="stBaseButton-secondary"] p { color: #B4713F !important; }

    /* Avatares */
    .avatar-circle {
        border-radius: 50%; object-fit: cover;
        width: 55px; height: 55px;
        border: 3px solid #FBAF3B;
        box-shadow: 0 4px 10px rgba(180, 113, 63, 0.2);
        transition: transform 0.3s ease;
    }
    .avatar-circle:hover { transform: scale(1.08) rotate(3deg); }
    
    /* Credencial VIP (Contraste oscuro para que resalte) */
    @keyframes cardFloat {
        0%, 100% { transform: translateY(0) rotateX(0); }
        50% { transform: translateY(-8px) rotateX(2deg); }
    }
    .credencial-feten {
        background: linear-gradient(135deg, #2D2926 0%, #1A1816 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px; padding: 40px 30px; width: 100%; max-width: 380px;
        margin: 20px auto; text-align: center;
        box-shadow: 0 25px 50px -15px rgba(0,0,0,0.4);
        position: relative; overflow: hidden;
        animation: cardFloat 6s ease-in-out infinite;
    }
    .credencial-logo-img { width: 100px; margin-bottom: 20px; filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.5));}
    .credencial-img { width: 120px; height: 120px; border-radius: 50%; border: 3px solid #FBAF3B; margin-bottom: 20px; object-fit: cover; box-shadow: 0 8px 20px rgba(0,0,0,0.5);}
    .credencial-name { font-size: 26px; font-weight: 800; margin: 0; color: #FDFCF8 !important;}
    .credencial-role { font-size: 12px; color: #FBAF3B !important; margin-top: 5px; margin-bottom: 30px; text-transform: uppercase; letter-spacing: 3px;}
    .credencial-id-box { background: rgba(255,255,255,0.05); padding: 12px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); }
    .credencial-id { font-family: 'Courier New', monospace; font-weight: bold; font-size: 18px; letter-spacing: 4px; color: #FFFFFF !important;}
    
    /* Métricas Dashboard */
    [data-testid="stMetricValue"] { color: #B4713F !important; font-size: 2.8rem !important; font-weight: 800 !important; }
    [data-testid="stMetricLabel"] { color: #8A8179 !important; text-transform: uppercase !important; letter-spacing: 1px !important; font-size: 0.8rem !important; }
    
    /* Dialogs/Modales */
    div[data-testid="stDialog"] > div {
        background-color: #FDFCF8 !important;
        border-radius: 20px;
        border: 1px solid #EBE8E0;
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

if "ruta" not in st.session_state: st.session_state["ruta"] = "Inicio"
if "proyecto_activo" not in st.session_state: st.session_state["proyecto_activo"] = None

# --- 4. VENTANAS EMERGENTES (MODALES CON ICONOS MINIMALISTAS) ---

@st.dialog("✦ Nuevo Recordatorio")
def ventana_recordatorio(es_admin, autor):
    titulo = st.text_input("Título de la Tarea")
    fecha = st.date_input("Fecha Límite")
    tipo = st.selectbox("Visibilidad", ["Privado", "Global (Toda la Productora)"]) if es_admin else "Privado"
    if st.button("Guardar Tarea", use_container_width=True):
        if titulo:
            st.session_state["proyectos"]["_CONFIG_"]["recordatorios"].append({"autor": autor, "titulo": titulo, "fecha": str(fecha), "tipo": tipo})
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

@st.dialog("☖ Fichar Miembro del Crew")
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

@st.dialog("⎔ Planilla de Dietas")
def ventana_catering(proyecto):
    nombre = st.text_input("Nombre Completo")
    dieta = st.selectbox("Restricción", ["Ninguna", "Vegetariano", "Vegano", "Celíaco", "Diabético"])
    alergias = st.text_area("Alergias específicas (Opcional)")
    if st.button("Guardar Preferencia", use_container_width=True):
        if nombre:
            st.session_state["proyectos"][proyecto]["catering"].append({"nombre": nombre, "dieta": dieta, "alergias": alergias})
            guardar_y_recargar()

@st.dialog("⊞ Pedido de Equipamiento")
def ventana_pedido(proyecto, area):
    item_nombre = st.text_input("Ítem / Equipo")
    justificacion = st.text_area("Justificación Técnica")
    if st.button("Enviar a Producción", use_container_width=True):
        if item_nombre:
            st.session_state["proyectos"][proyecto]["pedidos_equipos"].append({"area": area, "item": item_nombre, "notas": justificacion, "estado": "Pendiente"})
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

@st.dialog("◈ Registrar Gasto")
def ventana_presupuesto(proyecto):
    item = st.text_input("Concepto")
    costo = st.number_input("Costo Neto ($)", min_value=0.0)
    area = st.selectbox("Área", ["Técnica", "Arte", "Producción", "Catering", "Transporte"])
    estado = st.selectbox("Estado", ["A Pagar", "Abonado"])
    if st.button("Registrar Movimiento", use_container_width=True):
        if item:
            st.session_state["proyectos"][proyecto]["presupuesto"].append({"item": item, "costo": costo, "area": area, "estado": estado})
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
    if not directorio:
        st.warning("⚠️ Requiere registrar un Rental previamente.")
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
                        modelo = genai.GenerativeModel('gemini-3.5-flash')
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
                        modelo = genai.GenerativeModel('gemini-3.5-flash')
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
                        modelo = genai.GenerativeModel('gemini-3.5-flash')
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
            st.success(f"**Subtotal: ${total_r:,.2f} / jornada**")
            link_rental = next((d["url"] for d in directorio if d["nombre"] == r_name), None)
            if link_rental:
                st.markdown(f"<a href='{link_rental}' target='_blank' style='background: linear-gradient(135deg, #FBAF3B 0%, #B4713F 100%); color:white; padding:10px 15px; text-decoration:none; border-radius:8px; font-weight:bold; display:inline-block; margin-top:10px;'>Contactar Proveedor</a>", unsafe_allow_html=True)

@st.dialog("⚠️ Purga de Base de Datos")
def ventana_vaciar_comparador(proyecto):
    st.warning("Esta acción es irreversible. Limpiará el catálogo y el carrito.")
    if st.button("Confirmar Purga", use_container_width=True):
        st.session_state["proyectos"][proyecto]["comparador_rentals"] = []
        st.session_state["proyectos"][proyecto]["carrito_rentals"] = []
        guardar_y_recargar()

# --- 5. GESTIÓN DE SESIÓN ---
if "usuario_logueado" not in st.session_state:
    st.session_state["usuario_logueado"] = None

# --- 6. PANTALLA DE ACCESO Y REGISTRO (CON LOGO OFICIAL) ---
if st.session_state["usuario_logueado"] is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown(f"<div style='text-align: center;'><img src='{LOGO_URL}' width='250' style='margin-bottom: 20px; drop-shadow(0px 4px 10px rgba(0,0,0,0.1));'></div>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: #8A8179 !important; letter-spacing: 3px; font-weight: 500; margin-top: -15px;'>WORKSPACE</h4>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        tab_login, tab_registro = st.tabs(["Autenticación", "Solicitar Acceso"])
        db_users = st.session_state["proyectos"]["_CONFIG_"]["usuarios"]
        
        with tab_login:
            with st.container(border=True):
                email_ingreso = st.text_input("Correo corporativo", placeholder="nombre@productora.com").lower().strip()
                pass_ingreso = st.text_input("Contraseña", type="password", placeholder="••••••••")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("INICIAR SESIÓN", use_container_width=True, type="primary"):
                    if email_ingreso in db_users:
                        if db_users[email_ingreso]["pass"] == pass_ingreso:
                            if db_users[email_ingreso].get("estado") == "Aprobado":
                                st.session_state["usuario_logueado"] = email_ingreso
                                st.session_state["ruta"] = "Inicio"
                                st.rerun()
                            else: st.warning("Cuenta pendiente de validación.")
                        else: st.error("Credenciales inválidas.")
                    else: st.error("Usuario no registrado.")
                        
        with tab_registro:
            with st.container(border=True):
                nombre_reg = st.text_input("Nombre Completo")
                email_reg = st.text_input("Correo").lower().strip()
                pass_reg = st.text_input("Crear Contraseña", type="password")
                foto_reg = st.file_uploader("Foto de Credencial", type=["jpg", "png", "jpeg"])
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("ENVIAR SOLICITUD", use_container_width=True, type="primary"):
                    if nombre_reg and email_reg and pass_reg and foto_reg:
                        if "@" not in email_reg or "." not in email_reg:
                            st.error("Formato de correo inválido.")
                        elif email_reg in db_users:
                            st.error("El correo ya existe en la base.")
                        else:
                            foto_b64 = base64.b64encode(foto_reg.read()).decode('utf-8')
                            db_users[email_reg] = {
                                "nombre": nombre_reg, "pass": pass_reg, "rol": "Invitado", "nivel": "lectura", "estado": "Pendiente",
                                "foto": foto_b64, "credencial": f"FTN-{random.randint(1000, 9999)}", "edad": "", "roles_fav": "", "dieta": "", "specs": "", "cv": "", "portfolio": ""
                            }
                            guardar_y_recargar()
                            st.success("Solicitud enviada a la administración.")
                    else: st.error("Se requieren todos los campos.")

# --- 7. PLATAFORMA CENTRAL (DASHBOARD) ---
else:
    usuario_actual = st.session_state["usuario_logueado"]
    db_users = st.session_state["proyectos"]["_CONFIG_"]["usuarios"]
    
    if usuario_actual not in db_users or db_users[usuario_actual].get("estado") != "Aprobado":
        st.error("Acceso denegado. Contacte a soporte.")
        if st.button("Salir"):
            st.session_state["usuario_logueado"] = None
            st.rerun()
        st.stop()

    mis_datos = db_users[usuario_actual]
    rol_actual = mis_datos["rol"]
    nivel_actual = mis_datos["nivel"]
    
    # --- NAVBAR CON LOGO ---
    c_head_left, c_head_space, c_head_right = st.columns([2, 5, 1])
    with c_head_left:
        if st.session_state["ruta"] != "Inicio":
            if st.button("⌂ Dashboard", type="secondary"):
                st.session_state["ruta"] = "Inicio"
                st.rerun()
        else:
            st.markdown(f"<img src='{LOGO_URL}' height='50' style='margin-top:5px;'>", unsafe_allow_html=True)
            
    with c_head_right:
        foto_src = f"data:image/jpeg;base64,{mis_datos['foto']}" if mis_datos.get("foto") else "https://via.placeholder.com/150"
        st.markdown(f"<img src='{foto_src}' class='avatar-circle' style='float:right;'>", unsafe_allow_html=True)
        if st.button("Perfil", key="btn_mi_perfil"):
            st.session_state["ruta"] = "Perfil"
            st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # VISTA 1: DASHBOARD
    # ==========================================
    if st.session_state["ruta"] == "Inicio":
        st.markdown(f"<h1 style='margin-bottom:0px;'>{mis_datos['nombre']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#B4713F !important; font-weight:600; font-size:1.1rem;'>{rol_actual.upper()}</p>", unsafe_allow_html=True)
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        c_main, c_side = st.columns([2.5, 1])
        
        with c_main:
            c_title, c_btn_new = st.columns([3, 1])
            with c_title: st.markdown("### Proyectos Activos")
            with c_btn_new:
                if nivel_actual in ["jefe", "jefe_supremo"]:
                    with st.popover("❖ Nuevo Workspace"):
                        nuevo_proyecto = st.text_input("Nombre de la Producción:")
                        if st.button("Inicializar DB"):
                            if nuevo_proyecto and nuevo_proyecto not in st.session_state["proyectos"]:
                                st.session_state["proyectos"][nuevo_proyecto] = {
                                    "contexto_aprobado": "Proyecto base.", "archivos_pendientes": [], "avisos": [], "equipos": [], "pedidos_equipos": [], "continuidad": [], 
                                    "arte": [], "planos": [], "plan_rodaje": [], "plantas_luces": [], "sonido_log": [], "tomas_dir": [], "personajes": [], "locaciones": [], "crew": [], "catering": [], "links": [], "presupuesto": [], "casting": [], "desglose": [], "comparador_rentals": [], "carrito_rentals": [], "directorio_rentals": []
                                }
                                guardar_y_recargar()
            
            lista_proyectos = [p for p in st.session_state["proyectos"].keys() if p != "_CONFIG_"]
            if not lista_proyectos: st.info("No hay desarrollos activos.")
            else:
                cols_grid = st.columns(2)
                for idx, proy in enumerate(lista_proyectos):
                    with cols_grid[idx % 2]:
                        with st.container(border=True):
                            st.markdown(f"<h2>{proy}</h2>", unsafe_allow_html=True)
                            st.caption(f"☖ {len(st.session_state['proyectos'][proy]['crew'])} Personas | ⚙ {len(st.session_state['proyectos'][proy]['equipos'])} Equipos")
                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button("ENTRAR", key=f"entrar_{proy}", use_container_width=True, type="primary"):
                                st.session_state["proyecto_activo"] = proy
                                st.session_state["ruta"] = "Proyecto"
                                st.rerun()

        with c_side:
            st.markdown("### Agenda Global")
            if st.button("✦ Nueva Tarea", use_container_width=True):
                ventana_recordatorio(es_admin=(nivel_actual in ["jefe_supremo", "jefe"]), autor=mis_datos['nombre'])
            
            recordatorios = st.session_state["proyectos"]["_CONFIG_"].get("recordatorios", [])
            for rec in reversed(recordatorios):
                if rec["tipo"] == "Global (Toda la Productora)" or rec["autor"] == mis_datos["nombre"]:
                    with st.container(border=True):
                        color_t = "#FBAF3B" if "Global" in rec["tipo"] else "#8A8179"
                        st.markdown(f"<span style='color:{color_t}; font-size:12px; font-weight:bold;'>{rec['fecha']}</span>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-weight:600; font-size:15px; color:#332F2C;'>{rec['titulo']}</div>", unsafe_allow_html=True)
                        st.caption(f"Asignado por: {rec['autor']}")

    # ==========================================
    # VISTA 2: PERFIL Y CREDENCIAL
    # ==========================================
    elif st.session_state["ruta"] == "Perfil":
        st.markdown("<h1>Configuración de Cuenta</h1>", unsafe_allow_html=True)
        tab_misdatos, tab_cred, tab_dir = st.tabs(["Preferencias", "Credencial Corporativa", "Directorio"])
        
        with tab_misdatos:
            with st.container(border=True):
                c_img, c_form = st.columns([1, 3])
                with c_img:
                    st.markdown("#### Avatar")
                    foto_src = f"data:image/jpeg;base64,{mis_datos['foto']}" if mis_datos.get("foto") else "https://via.placeholder.com/150"
                    st.markdown(f"<img src='{foto_src}' class='avatar-circle' style='width:120px;height:120px; border-width:4px;'>", unsafe_allow_html=True)
                    nueva_foto = st.file_uploader("Cambiar Imagen", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
                    if nueva_foto and st.button("Subir Nueva Foto", use_container_width=True):
                        db_users[usuario_actual]["foto"] = base64.b64encode(nueva_foto.read()).decode('utf-8')
                        guardar_y_recargar()

                with c_form:
                    with st.form("form_perfil"):
                        c1, c2 = st.columns(2)
                        edad = c1.text_input("Edad", value=mis_datos.get("edad", ""))
                        roles_fav = c2.text_input("Área de Especialidad", value=mis_datos.get("roles_fav", ""))
                        dieta_opciones = ["Ninguna", "Vegetariano", "Vegano", "Celíaco", "Diabético"]
                        idx_dieta = dieta_opciones.index(mis_datos.get("dieta", "Ninguna")) if mis_datos.get("dieta") in dieta_opciones else 0
                        dieta = c1.selectbox("Catering", dieta_opciones, index=idx_dieta)
                        portfolio = c2.text_input("Enlace Profesional (Reel/CV)", value=mis_datos.get("portfolio", ""))
                        specs = st.text_area("Notas / Manejo de Equipos", value=mis_datos.get("specs", ""))
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.form_submit_button("Guardar Cambios", use_container_width=True):
                            db_users[usuario_actual].update({"edad": edad, "roles_fav": roles_fav, "dieta": dieta, "portfolio": portfolio, "specs": specs})
                            guardar_y_recargar()
                            st.success("Perfil sincronizado.")
                
                st.divider()
                if st.button("Desconectar Cuenta", type="secondary"):
                    st.session_state["usuario_logueado"] = None
                    st.session_state["ruta"] = "Inicio"
                    st.rerun()

        with tab_cred:
            foto_cred = f"data:image/jpeg;base64,{mis_datos['foto']}" if mis_datos.get("foto") else "https://via.placeholder.com/150"
            st.markdown(f"""
                <div class="credencial-feten">
                    <img src="{LOGO_URL}" class="credencial-logo-img">
                    <br>
                    <img src="{foto_cred}" class="credencial-img">
                    <h2 class="credencial-name">{mis_datos['nombre']}</h2>
                    <p class="credencial-role">{mis_datos['rol']}</p>
                    <div class="credencial-id-box">
                        <span class="credencial-id">ID: {mis_datos.get('credencial', 'FTN-0000')}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with tab_dir:
            busqueda = st.text_input("Buscador de Talentos...", placeholder="Ej: Director...")
            st.markdown("<br>", unsafe_allow_html=True)
            for em, info in db_users.items():
                if info["estado"] == "Aprobado" and (busqueda.lower() in info["nombre"].lower() or busqueda.lower() in info["rol"].lower()):
                    with st.container(border=True):
                        colD1, colD2 = st.columns([1, 8])
                        with colD1:
                            if info.get("foto"): st.markdown(f"<img src='data:image/jpeg;base64,{info['foto']}' class='avatar-circle' style='width:60px;height:60px;'>", unsafe_allow_html=True)
                        with colD2:
                            st.markdown(f"<h4 style='margin:0;'>{info['nombre']} <span style='color:#B4713F;font-size:14px;'>({info['rol']})</span></h4>", unsafe_allow_html=True)
                            st.caption(f"**Notas:** {info.get('specs', 'N/A')}")
                            if info.get("portfolio"): st.markdown(f"[⧉ Ver Trabajos]({info['portfolio']})")

    # ==========================================
    # VISTA 3: PROYECTO (USANDO OPTION_MENU)
    # ==========================================
    elif st.session_state["ruta"] == "Proyecto":
        proyecto_elegido = st.session_state["proyecto_activo"]
        p_data = st.session_state["proyectos"][proyecto_elegido]
        
        st.markdown(f"<h1 style='margin-bottom:30px;'>{proyecto_elegido}</h1>", unsafe_allow_html=True)
        
        col_nav, col_content = st.columns([1, 3.5], gap="large")
        
        # --- ESTRUCTURACIÓN DEL MENÚ CON ÍCONOS ---
        opciones_nav = ["Panel General", "Asistente IA"]
        iconos_nav = ["grid", "lightning-charge"]
        
        if nivel_actual != "lectura": 
            opciones_nav.append("Solicitar a Prod.")
            iconos_nav.append("send")
            
        opciones_nav.extend(["Rentals IA", "Archivos", "Tablón", "Enlaces"])
        iconos_nav.extend(["shop", "folder2-open", "megaphone", "link-45deg"])
        
        if rol_actual == "Super Admin":
            opciones_nav.extend([
                "Permisos", "Presupuesto", "Bandeja Prod.", "Scouting", "Base Crew", "Casting", "Catering",
                "Desglose", "Guion", "Inventario", "Plan Rodaje", "Monitor DIR", "Luces (Canvas)", "Ref. IA",
                "Arte & Vestuario", "Log Sonido", "Raccord"
            ])
            iconos_nav.extend([
                "shield-lock", "wallet2", "inbox", "geo-alt", "people", "person-video", "cup-hot",
                "card-text", "pen", "box", "calendar-event", "camera-reels", "lightbulb", "cpu",
                "palette", "headphones", "film"
            ])
        else:
            if rol_actual == "Producción": 
                opciones_nav.extend(["Presupuesto", "Bandeja Prod.", "Scouting", "Base Crew", "Casting", "Catering"])
                iconos_nav.extend(["wallet2", "inbox", "geo-alt", "people", "person-video", "cup-hot"])
            else:
                if nivel_actual != "lectura": 
                    opciones_nav.extend(["Inventario"])
                    iconos_nav.extend(["box"])
            if rol_actual == "Guion": 
                opciones_nav.extend(["Desglose", "Guion"])
                iconos_nav.extend(["card-text", "pen"])
            if "Dirección" in rol_actual and rol_actual not in ["Dirección de Arte", "Dirección de Fotografía"]: 
                opciones_nav.extend(["Casting", "Plan Rodaje", "Monitor DIR"])
                iconos_nav.extend(["person-video", "calendar-event", "camera-reels"])
            if rol_actual == "Dirección de Fotografía": 
                opciones_nav.extend(["Luces (Canvas)", "Ref. IA"])
                iconos_nav.extend(["lightbulb", "cpu"])
            if rol_actual == "Dirección de Arte": 
                opciones_nav.append("Arte & Vestuario")
                iconos_nav.append("palette")
            if "Sonido" in rol_actual: 
                opciones_nav.extend(["Log Sonido"])
                iconos_nav.extend(["headphones"])
            if rol_actual == "Continuidad": 
                opciones_nav.append("Raccord")
                iconos_nav.append("film")

        with col_nav:
            seccion_elegida = option_menu(
                menu_title="DEPARTAMENTOS",
                options=opciones_nav,
                icons=iconos_nav,
                menu_icon="cast",
                default_index=0,
                styles={
                    "container": {"padding": "10px", "background-color": "#FFFFFF", "border-radius": "16px", "border": "1px solid #EBE8E0"},
                    "icon": {"color": "#FBAF3B", "font-size": "16px"},
                    "menu-title": {"color": "#8A8179", "font-size": "12px", "letter-spacing": "2px", "font-weight": "800"},
                    "nav-link": {"font-size": "14px", "text-align": "left", "margin": "2px 0", "color": "#4A4541", "border-radius": "8px", "padding": "10px"},
                    "nav-link-selected": {"background-color": "rgba(251, 175, 59, 0.15)", "color": "#B4713F", "font-weight": "700", "border-left": "4px solid #FBAF3B"},
                }
            )
        
        with col_content:
            # --- LÓGICA DE LOS MÓDULOS ---
            if seccion_elegida == "Panel General":
                c1, c2, c3, c4 = st.columns(4)
                with c1: st.metric("Nómina", len(p_data["crew"]))
                with c2: st.metric("Lugares", len(p_data["locaciones"]))
                with c3: st.metric("Fierros", len(p_data["equipos"]))
                with c4: st.metric("Tickets", len(p_data["pedidos_equipos"]))
                
                st.divider()
                st.markdown("### ⚡ Generador de Call Sheet")
                c_btn1, c_btn2, c_btn3 = st.columns([1, 2, 1])
                with c_btn2:
                    if st.button("Emitir Plan (IA)", use_container_width=True):
                        try:
                            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                            modelo = genai.GenerativeModel('gemini-3.5-flash')
                            datos = f"Avisos: {p_data['avisos']} | Equipo: {p_data['crew']} | Locaciones: {p_data['locaciones']}"
                            prompt = f"Sos FTN AI. Proyecto: {proyecto_elegido}. Datos: {datos}. Redactá un Call Sheet profesional."
                            with st.spinner("Compilando variables..."):
                                st.markdown(f"<div style='background:#F9F8F4; padding:20px; border-radius:15px; border: 1px solid #EBE8E0;'>{modelo.generate_content(prompt).text}</div>", unsafe_allow_html=True)
                        except: st.error("Falta API Key Gemini.")

            elif seccion_elegida == "Solicitar a Prod.":
                colA, colB = st.columns([3, 1])
                with colA: st.markdown("<h2>Tickets de Necesidad</h2>", unsafe_allow_html=True)
                with colB: 
                    if st.button("✦ Levantar Ticket", use_container_width=True): ventana_pedido(proyecto_elegido, rol_actual)
                st.divider()
                mis_pedidos = [p for p in p_data["pedidos_equipos"] if p["area"] == rol_actual or rol_actual == "Super Admin"]
                if not mis_pedidos: st.info("Bandeja limpia.")
                for ped in mis_pedidos:
                    with st.container(border=True):
                        st.write(f"**{ped['item']}** — {ped['notas']}")
                        if ped['estado'] == "Pendiente": st.warning("En revisión")
                        elif ped['estado'] == "Aprobado": st.success("Aprobado")
                        else: st.error("Rechazado")

            elif seccion_elegida == "Bandeja Prod.":
                st.markdown("<h2>Control de Tickets</h2>", unsafe_allow_html=True)
                if not p_data["pedidos_equipos"]: st.info("Todo al día.")
                for i, ped in enumerate(p_data["pedidos_equipos"]):
                    if ped['estado'] == "Pendiente":
                        with st.container(border=True):
                            st.markdown(f"**{ped['area']}** solicita: {ped['item']}")
                            st.caption(f"Justificación: {ped['notas']}")
                            c1, c2 = st.columns(2)
                            if c1.button("Aprobar", key=f"p_ap_{i}", use_container_width=True):
                                p_data["equipos"].append({"area": ped['area'], "item": ped['item'], "cant": 1, "tipo": "A Confirmar", "rental": "A Definir"})
                                p_data["pedidos_equipos"][i]["estado"] = "Aprobado"
                                guardar_y_recargar()
                            if c2.button("Denegar", key=f"p_re_{i}", use_container_width=True):
                                p_data["pedidos_equipos"][i]["estado"] = "Rechazado"
                                guardar_y_recargar()

            elif seccion_elegida == "Rentals IA":
                colA, colB, colC = st.columns([2, 1, 1])
                with colA: st.markdown("<h2>Cotizador Central</h2>", unsafe_allow_html=True)
                with colB: 
                    if st.button("⌂ Sumar Proveedor", use_container_width=True): ventana_nuevo_rental(proyecto_elegido)
                with colC: 
                    if st.button("✧ Scanner IA", use_container_width=True): ventana_comparador_rental(proyecto_elegido)
                if rol_actual == "Super Admin" and st.button("Purga de Datos", type="secondary"): ventana_vaciar_comparador(proyecto_elegido)
                
                st.divider()
                carrito = p_data.get("carrito_rentals", [])
                if len(carrito) > 0:
                    with st.container(border=True):
                        c_txt, c_btn = st.columns([3, 1])
                        with c_txt: st.markdown("<h3 style='margin:0;'>Lista de Checkout</h3>", unsafe_allow_html=True)
                        with c_btn:
                            if st.button("PROCEDER", use_container_width=True, type="primary"): ventana_checkout(proyecto_elegido)
                        
                        cols_cart = st.columns(3)
                        total_cart = 0
                        for i, item in enumerate(carrito):
                            total_cart += item["precio"]
                            with cols_cart[i % 3]:
                                with st.container(border=True):
                                    st.markdown(f"<p style='font-size:10px; font-weight:bold; color:#B4713F; margin:0;'>{item.get('rental', 'N/A')}</p>", unsafe_allow_html=True)
                                    st.markdown(f"<p style='font-weight:700; margin:0; font-size:14px; color:#2D2926;'>{item['nombre'][:30]}...</p>", unsafe_allow_html=True)
                                    st.markdown(f"**${item['precio']:,.2f}**")
                                    if st.button("Remover", key=f"quit_cart_{i}", use_container_width=True):
                                        p_data["carrito_rentals"].pop(i)
                                        guardar_y_recargar()
                        st.markdown(f"<h4 style='text-align:right; color:#B4713F;'>Total Estimado: ${total_cart:,.2f} / Día</h4>", unsafe_allow_html=True)
                
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
                                        st.markdown("<span style='background:rgba(251,175,59,0.2); border: 1px solid #FBAF3B; color:#B4713F; padding:2px 8px; border-radius:6px; font-size:10px; font-weight:800;'>MÁS CONVENIENTE</span>", unsafe_allow_html=True)
                                    st.markdown(f"<p style='font-size:11px; font-weight:bold; color:#B4713F; margin:0; margin-top:5px;'>{r.get('rental', 'N/A')}</p>", unsafe_allow_html=True)
                                    st.markdown(f"<p style='margin:0; font-weight:600; font-size:14px; color:#2D2926;'>{r['nombre']}</p>", unsafe_allow_html=True)
                                    st.markdown(f"<h3 style='margin:0; color:#B4713F; font-size:20px;'>${r['precio']:,.2f}</h3>", unsafe_allow_html=True)
                                    c_add, c_del = st.columns(2)
                                    if c_add.button("Añadir", key=f"add_{idx_orig}", use_container_width=True, type="primary"):
                                        p_data["carrito_rentals"].append(r)
                                        guardar_y_recargar()
                                    if c_del.button("Borrar", key=f"del_{idx_orig}", use_container_width=True):
                                        p_data["comparador_rentals"].pop(idx_orig)
                                        guardar_y_recargar()
                    else: st.warning("Sin coincidencias.")

            elif seccion_elegida == "Luces (Canvas)":
                st.markdown("<h2>Planta de Iluminación</h2>", unsafe_allow_html=True)
                col_h, col_c = st.columns([1, 2.5])
                with col_h:
                    st.markdown("**Panel de Herramientas**")
                    modo = st.selectbox("Trazado", ["freedraw", "line", "rect", "circle", "transform"])
                    color_mapping = {"Principal": "#FFD700", "Relleno": "#1E90FF", "Contraluz": "#8A2BE2", "Actor": "#FF4500", "Cámara": "#FFFFFF"}
                    tipo = st.radio("Elemento", list(color_mapping.keys()))
                    grosor = st.slider("Grosor", 1, 10, 3)
                    if st.button("Guardar Diseño"): st.success("Registrado.")
                with col_c:
                    st_canvas(fill_color="rgba(255,255,255,0)", stroke_width=grosor, stroke_color=color_mapping[tipo], background_color="#2D2926", width=500, height=450, drawing_mode=modo, key="canvas_luces_pro")

            elif seccion_elegida == "Permisos":
                st.markdown("<h2>Control de Accesos</h2>", unsafe_allow_html=True)
                mapa = {"Super Admin": "jefe_supremo", "Producción": "jefe", "Dirección": "jefe", "Dirección de Fotografía": "jefe", "Dirección de Arte": "jefe", "Director de Sonido": "jefe", "Asistente de Sonido": "asistente", "Guion": "jefe", "Continuidad": "jefe", "Invitado": "lectura"}
                for em_usr, dt_usr in st.session_state["proyectos"]["_CONFIG_"]["usuarios"].items():
                    with st.container(border=True):
                        c1, c2, c3, c4 = st.columns([2, 1.5, 1.5, 1])
                        c1.markdown(f"**{dt_usr['nombre']}**<br><span style='font-size:12px; color:gray;'>{em_usr}</span>", unsafe_allow_html=True)
                        est = c2.selectbox("Estado", ["Aprobado", "Pendiente"], index=0 if dt_usr.get("estado") == "Aprobado" else 1, key=f"e_{em_usr}")
                        rol = c3.selectbox("Rol", list(mapa.keys()), index=list(mapa.keys()).index(dt_usr["rol"]) if dt_usr["rol"] in mapa else 9, key=f"r_{em_usr}")
                        if c4.button("Aplicar", key=f"b_{em_usr}", use_container_width=True):
                            st.session_state["proyectos"]["_CONFIG_"]["usuarios"][em_usr].update({"estado": est, "rol": rol, "nivel": mapa[rol]})
                            guardar_y_recargar()

            elif seccion_elegida == "Enlaces":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Directorio Web</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("✦ Cargar URL", use_container_width=True): ventana_link(proyecto_elegido)
                st.divider()
                for lk in p_data["links"]:
                    with st.container(border=True): st.markdown(f"### [⧉ {lk['titulo']}]({lk['url']})\n{lk['desc']}")

            elif seccion_elegida == "Presupuesto":
                c1, c2, c3 = st.columns([2, 1, 1])
                with c1: st.markdown("<h2>Flujo Financiero</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("✦ Asentar Gasto", use_container_width=True): ventana_presupuesto(proyecto_elegido)
                with c3:
                    if p_data["presupuesto"]: st.download_button("Exportar CSV", data=pd.DataFrame(p_data["presupuesto"]).to_csv(index=False).encode('utf-8'), file_name="budget.csv", mime="text/csv", use_container_width=True)
                st.divider()
                total = sum(i['costo'] for i in p_data["presupuesto"])
                st.markdown(f"<h3 style='color:#B4713F;'>Total Comprometido: ${total:,.2f}</h3>", unsafe_allow_html=True)
                for item in p_data["presupuesto"]:
                    with st.container(border=True): st.markdown(f"**{item['estado']}** | ${item['costo']:,.2f} - {item['item']} ({item['area']})")

            elif seccion_elegida == "Casting":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Base de Talentos</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("✦ Ingresar Actor", use_container_width=True): ventana_casting(proyecto_elegido)
                st.divider()
                cols = st.columns(2)
                for i, a in enumerate(p_data["casting"]):
                    with cols[i % 2]:
                        with st.container(border=True):
                            if a.get("foto"): st.image(base64.b64decode(a["foto"]), width=90)
                            st.markdown(f"#### {a['actor']}\n**Papel:** {a['personaje']}\n[Ver Demo]({a['reel']})")

            elif seccion_elegida == "Desglose":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Script Breakdown</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("✦ Extraer", use_container_width=True): ventana_desglose(proyecto_elegido)
                st.divider()
                for d in p_data["desglose"]:
                    with st.container(border=True): st.markdown(f"**ESC {d['escena']} | {d['intext']} | {d['dianoche']}**<br>{d['desc']}", unsafe_allow_html=True)

            elif seccion_elegida == "Plan Rodaje":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Shooting Schedule</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("✦ Add Slot", use_container_width=True): ventana_cronograma(proyecto_elegido)
                st.divider()
                for a in sorted(p_data["plan_rodaje"], key=lambda x: x.get('hora', '00:00')):
                    with st.container(border=True): st.markdown(f"<h3 style='margin:0; color:#B4713F;'>{a.get('hora', '')}</h3><p style='margin:0; font-size:16px;'>{a['actividad']}</p>", unsafe_allow_html=True)

            elif seccion_elegida == "Ref. IA":
                st.markdown("<h2>Laboratorio Visual</h2>", unsafe_allow_html=True)
                try:
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    mod_foto = genai.GenerativeModel('gemini-3.5-flash')
                    msg_foto = st.chat_input("Prompt visual...")
                    if msg_foto:
                        st.markdown(f"**Dir:** {msg_foto}")
                        resp = mod_foto.generate_content(f"Sos DF. Da referencias: {msg_foto}")
                        st.info(f"**Visión IA:** {resp.text}")
                except: st.error("Falta API Key.")

            elif seccion_elegida == "Scouting":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Locations</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("✦ Registrar", use_container_width=True): ventana_locacion(proyecto_elegido)
                st.divider()
                for loc in p_data["locaciones"]:
                    with st.container(border=True):
                        st.markdown(f"### ⌖ {loc['nombre']}")
                        st.write(f"**Dir:** {loc['direccion']} | **Estado:** {loc['permisos']}")

            elif seccion_elegida == "Base Crew":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Nómina</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("✦ Contratar", use_container_width=True): ventana_crew(proyecto_elegido)
                st.divider()
                for p in p_data["crew"]:
                    with st.container(border=True): st.markdown(f"**{p['nombre']}** — {p['rol']}")

            elif seccion_elegida == "Catering":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Dietética</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("✦ Añadir Dieta", use_container_width=True): ventana_catering(proyecto_elegido)
                st.divider()
                for p in p_data["catering"]:
                    with st.container(border=True): st.markdown(f"**{p['nombre']}** | ⎔ {p['dieta']}")

            elif seccion_elegida == "Tablón":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Comunicaciones</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("✦ Publicar", use_container_width=True): ventana_aviso(proyecto_elegido, mis_datos['nombre'], p_data["locaciones"])
                st.divider()
                for aviso in reversed(p_data["avisos"]):
                    with st.container(border=True): st.markdown(f"**{aviso['autor']}**: {aviso.get('texto', 'Citación.')}")

            elif seccion_elegida == "Archivos":
                st.markdown("<h2>Documentos Root</h2>", unsafe_allow_html=True)
                archivo = st.file_uploader("Documento (.txt)", type=["txt"])
                if archivo and st.button("Subir al Sistema Central"):
                    p_data["archivos_pendientes"].append({"autor": mis_datos['nombre'], "nombre": archivo.name, "texto": archivo.getvalue().decode('utf-8')})
                    guardar_y_recargar()
                    
                if len(p_data["archivos_pendientes"]) > 0:
                    st.markdown("### En Cola")
                    for i, doc in enumerate(p_data["archivos_pendientes"]):
                        with st.container(border=True):
                            st.write(f"📄 {doc['nombre']} ({doc['autor']})")
                            c1, c2 = st.columns(2)
                            if c1.button("Validar", key=f"ap_{i}"):
                                p_data["contexto_aprobado"] += f"\n\n[Doc]: {doc['texto']}"
                                p_data["archivos_pendientes"].pop(i)
                                guardar_y_recargar()
                            if c2.button("Descartar", key=f"re_{i}"):
                                p_data["archivos_pendientes"].pop(i)
                                guardar_y_recargar()

            elif seccion_elegida == "Inventario":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Activos en Uso</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("✦ Agregar", use_container_width=True): ventana_equipo(proyecto_elegido, rol_actual)
                st.divider()
                for eq in p_data["equipos"]:
                    with st.container(border=True): st.markdown(f"**{eq['cant']}x {eq['item']}** | {eq['area']} | {eq['tipo']}")

            elif seccion_elegida == "Guion":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Diseño Narrativo</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("✦ Add Personaje", use_container_width=True): ventana_personaje(proyecto_elegido)
                st.divider()
                for p in p_data["personajes"]:
                    with st.container(border=True): st.markdown(f"#### {p['nombre']} ({p['rol']})")

            elif seccion_elegida == "Arte & Vestuario":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Dep. Arte</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("✦ Objeto Nuevo", use_container_width=True): ventana_arte(proyecto_elegido)
                st.divider()
                cols = st.columns(3)
                for i, item in enumerate(p_data["arte"]):
                    with cols[i % 3]:
                        with st.container(border=True):
                            st.markdown(f"**{item['estado']}** | {item['objeto']}")
                            if item.get("foto"): st.image(base64.b64decode(item["foto"]), use_container_width=True)

            elif seccion_elegida == "Monitor DIR":
                c1, c2, c3 = st.columns([2, 1, 1])
                with c1: st.markdown("<h2>Director's Log</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("✦ Shot List", use_container_width=True): ventana_plano(proyecto_elegido)
                with c3: 
                    if st.button("✦ Loguear Toma", use_container_width=True): ventana_toma_dir(proyecto_elegido)
                st.divider()
                for t in p_data["tomas_dir"]:
                    with st.container(border=True): st.markdown(f"{t['evaluacion']} | **ESC {t['escena']} - TOMA {t['toma']}**")

            elif seccion_elegida == "Log Sonido":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Reportes de Audio</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("✦ Registrar", use_container_width=True): ventana_sonido(proyecto_elegido)
                st.divider()
                for s in reversed(p_data["sonido_log"]):
                    with st.container(border=True): st.markdown(f"**ESC {s['escena']} | T {s['toma']}**")

            elif seccion_elegida == "Raccord":
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown("<h2>Notas Continuidad</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("✦ Asentar", use_container_width=True): ventana_continuidad(proyecto_elegido)
                st.divider()
                for nota in reversed(p_data["continuidad"]):
                    with st.container(border=True): st.markdown(f"**ESC {nota['escena']} - T {nota['toma']}**<br>{nota['detalle']}", unsafe_allow_html=True)

            elif seccion_elegida == "Asistente IA":
                st.markdown("<h2>Comando de IA (Copilot)</h2>", unsafe_allow_html=True)
                try:
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    modelo = genai.GenerativeModel('gemini-3.5-flash')
                    mensaje = st.chat_input("Escribe una instrucción al sistema...")
                    if mensaje:
                        st.chat_message("user").write(mensaje)
                        resp = modelo.generate_content(f"Sos FTN AI. Hablás con: {mis_datos['nombre']}. Contexto: {p_data['contexto_aprobado']}\nUsuario: {mensaje}")
                        st.chat_message("assistant").write(resp.text)
                except: st.error("Falta configurar la API Key.")
