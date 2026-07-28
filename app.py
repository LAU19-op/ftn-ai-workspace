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

# --- 2. DISEÑO UI/UX PREMIUM (CSS) ---
st.markdown("""
    <style>
    /* Importar tipografía moderna */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Fondo general más limpio */
    .stApp {
        background-color: var(--background-color);
        background-image: radial-gradient(circle at 50% 0%, rgba(99, 102, 241, 0.05) 0%, transparent 70%);
    }

    /* Tarjetas y Contenedores (Glassmorphism sutil) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 20px !important;
        border: 1px solid rgba(150, 150, 150, 0.15) !important;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.08) !important;
        background: var(--background-color);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        padding: 10px;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 35px -10px rgba(99, 102, 241, 0.15) !important;
    }
    
    /* Inputs y Selects rediseñados */
    .stTextInput input, .stSelectbox select, .stNumberInput input, .stDateInput input, .stTimeInput input {
        border-radius: 14px !important;
        border: 1.5px solid rgba(150, 150, 150, 0.2) !important;
        padding: 12px 16px !important;
        transition: all 0.3s ease !important;
        background-color: rgba(255, 255, 255, 0.02) !important;
    }
    .stTextInput input:focus, .stSelectbox select:focus, .stNumberInput input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15) !important;
    }
    
    /* Botones Premium */
    .stButton button {
        border-radius: 14px !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px !important;
        border: none !important;
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        color: white !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
    }
    .stButton button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4) !important;
        background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%) !important;
    }
    
    /* Botones Secundarios (Streamlit los maneja con otro div, forzamos estilo base) */
    div[data-testid="stFormSubmitButton"] button {
        width: 100%;
        padding: 1rem !important;
        font-size: 1.1rem !important;
    }

    /* Métricas estilo Dashboard */
    [data-testid="stMetricValue"] {
        font-weight: 800 !important;
        font-size: 2.5rem !important;
        color: #6366f1 !important;
    }
    [data-testid="stMetricLabel"] {
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-size: 0.85rem !important;
        opacity: 0.7;
    }
    
    /* Perfil y Avatar Redondo */
    .avatar-circle {
        border-radius: 50%;
        object-fit: cover;
        width: 55px;
        height: 55px;
        border: 2px solid #6366f1;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        transition: transform 0.2s;
    }
    .avatar-circle:hover { transform: scale(1.05); }
    
    /* Credencial Fetén BLACK CARD */
    .credencial-feten {
        background: linear-gradient(145deg, #0f172a 0%, #1e1b4b 100%);
        color: white;
        border-radius: 24px;
        padding: 40px 30px;
        width: 100%;
        max-width: 380px;
        margin: 20px auto;
        text-align: center;
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5), inset 0 1px 1px rgba(255,255,255,0.1);
        position: relative;
        overflow: hidden;
    }
    .credencial-feten::before {
        content: ''; position: absolute; top: 0; left: -100%; width: 50%; height: 100%;
        background: linear-gradient(to right, transparent, rgba(255,255,255,0.1), transparent);
        transform: skewX(-25deg); animation: shine 6s infinite;
    }
    @keyframes shine { 0% {left: -100%;} 20% {left: 200%;} 100% {left: 200%;} }
    .credencial-logo { font-size: 18px; font-weight: 800; letter-spacing: 4px; color: #818cf8; margin-bottom: 25px; text-transform: uppercase;}
    .credencial-img { width: 130px; height: 130px; border-radius: 50%; border: 4px solid rgba(255,255,255,0.1); margin-bottom: 20px; object-fit: cover; box-shadow: 0 10px 25px rgba(0,0,0,0.5);}
    .credencial-name { font-size: 28px; font-weight: 800; margin: 0; letter-spacing: -0.5px; }
    .credencial-role { font-size: 14px; color: #94a3b8; margin-top: 5px; margin-bottom: 30px; text-transform: uppercase; letter-spacing: 2px; font-weight: 600;}
    .credencial-id-box { background: rgba(0,0,0,0.3); padding: 15px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.05); }
    .credencial-id { font-family: 'Courier New', monospace; font-weight: bold; font-size: 20px; letter-spacing: 4px; color: #c7d2fe;}
    .barcode { font-family: "Libre Barcode 39", cursive, monospace; font-size: 35px; margin-top: 10px; color: rgba(255,255,255,0.3); }
    
    /* Modificadores de texto Streamlit */
    h1, h2, h3 { font-weight: 700 !important; letter-spacing: -0.5px !important; }
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

# --- 4. VENTANAS EMERGENTES (MODALES) - (Lógica intacta, layout mejorado internamente) ---

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

# --- 6. PANTALLA DE ACCESO Y REGISTRO (DISEÑO CLEAN) ---
if st.session_state["usuario_logueado"] is None:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; font-weight: 800; color: #1e1b4b;'>🎬 FETÉN<br><span style='color: #6366f1; font-size: 20px; letter-spacing: 3px;'>WORKSPACE</span></h1>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        tab_login, tab_registro = st.tabs(["🔑 Ingresar", "📝 Crear Cuenta"])
        db_users = st.session_state["proyectos"]["_CONFIG_"]["usuarios"]
        
        with tab_login:
            with st.container(border=True):
                email_ingreso = st.text_input("Correo electrónico", placeholder="ejemplo@productora.com").lower().strip()
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
                st.info("📸 Sube una foto para tu Credencial oficial:")
                foto_reg = st.file_uploader("Foto de Perfil", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("SOLICITAR ACCESO", use_container_width=True, type="primary"):
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
                            st.success("¡Solicitud enviada al Administrador!")
                    else: st.error("Completá todos los campos.")

# --- 7. PLATAFORMA CENTRAL (REDESIGN) ---
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
    
    # --- HEADER SUPERIOR ELEGANTE ---
    c_head_left, c_head_space, c_head_right = st.columns([2, 5, 1])
    with c_head_left:
        if st.session_state["ruta"] != "Inicio":
            if st.button("⬅️ DASHBOARD", type="secondary"):
                st.session_state["ruta"] = "Inicio"
                st.rerun()
        else:
            st.markdown("<h3 style='margin:0; color:#1e1b4b; padding-top:10px;'>🎬 Fetén</h3>", unsafe_allow_html=True)
            
    with c_head_right:
        # Mini layout para foto y botón de perfil invisible
        foto_src = f"data:image/jpeg;base64,{mis_datos['foto']}" if mis_datos.get("foto") else "https://via.placeholder.com/150"
        st.markdown(f"<img src='{foto_src}' class='avatar-circle' style='float:right;'>", unsafe_allow_html=True)
        if st.button("Mi Perfil", key="btn_mi_perfil"):
            st.session_state["ruta"] = "Perfil"
            st.rerun()
    st.divider()

    # ==========================================
    # VISTA 1: DASHBOARD (HOME)
    # ==========================================
    if st.session_state["ruta"] == "Inicio":
        st.markdown(f"<h1 style='margin-bottom:5px; font-weight:800;'>Hola, {mis_datos['nombre']} 👋</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#6366f1; font-weight:600; font-size:1.2rem; margin-top:0;'>{rol_actual.upper()}</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        c_main, c_side = st.columns([2.5, 1])
        
        with c_main:
            c_title, c_btn_new = st.columns([3, 1])
            with c_title: st.markdown("<h3 style='margin-bottom:20px;'>📌 Proyectos Activos</h3>", unsafe_allow_html=True)
            with c_btn_new:
                if nivel_actual in ["jefe", "jefe_supremo"]:
                    with st.popover("➕ Nuevo Proyecto"):
                        nuevo_proyecto = st.text_input("Nombre del Film/Spot:")
                        if st.button("Inicializar Database"):
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
                # GRILLA DE PROYECTOS (Mejora visual: 2 columnas)
                cols_grid = st.columns(2)
                for idx, proy in enumerate(lista_proyectos):
                    with cols_grid[idx % 2]:
                        with st.container(border=True):
                            st.markdown(f"<h4 style='color:#1e1b4b; margin-bottom:5px;'>{proy}</h4>", unsafe_allow_html=True)
                            st.caption(f"👥 {len(st.session_state['proyectos'][proy]['crew'])} Crew | 🎥 {len(st.session_state['proyectos'][proy]['equipos'])} Equipos")
                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button("ABRIR WORKSPACE", key=f"entrar_{proy}", use_container_width=True, type="primary"):
                                st.session_state["proyecto_activo"] = proy
                                st.session_state["ruta"] = "Proyecto"
                                st.rerun()

        with c_side:
            st.markdown("### 📅 Agenda General")
            if st.button("➕ Agendar Tarea", use_container_width=True):
                ventana_recordatorio(es_admin=(nivel_actual in ["jefe_supremo", "jefe"]), autor=mis_datos['nombre'])
            
            recordatorios = st.session_state["proyectos"]["_CONFIG_"].get("recordatorios", [])
            if not recordatorios: st.caption("No hay recordatorios próximos.")
            for rec in reversed(recordatorios):
                if rec["tipo"] == "Global (Toda la productora)" or rec["autor"] == mis_datos["nombre"]:
                    with st.container(border=True):
                        color_t = "#6366f1" if "Global" in rec["tipo"] else "#475569"
                        st.markdown(f"<span style='color:{color_t}; font-size:12px; font-weight:bold;'>{rec['fecha']}</span>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-weight:600; font-size:15px;'>{rec['titulo']}</div>", unsafe_allow_html=True)
                        st.caption(f"De: {rec['autor']}")

    # ==========================================
    # VISTA 2: PERFIL PROFESIONAL
    # ==========================================
    elif st.session_state["ruta"] == "Perfil":
        st.markdown("<h2 style='font-weight:800;'>Tu Perfil Profesional</h2>", unsafe_allow_html=True)
        tab_misdatos, tab_cred, tab_dir = st.tabs(["👤 Mis Datos", "🪪 ID Corporativo", "👥 Directorio de Crew"])
        
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
                        st.success("Datos actualizados correctamente.")
                
                st.divider()
                if st.button("Cerrar Sesión Oficial", type="secondary"):
                    st.session_state["usuario_logueado"] = None
                    st.session_state["ruta"] = "Inicio"
                    st.rerun()

        with tab_cred:
            st.write("Presentá esta tarjeta para retirar equipos o acceder a locaciones.")
            foto_cred = f"data:image/jpeg;base64,{mis_datos['foto']}" if mis_datos.get("foto") else "https://via.placeholder.com/150"
            st.markdown(f"""
                <div class="credencial-feten">
                    <div class="credencial-logo">FETÉN PRODUCCIONES</div>
                    <img src="{foto_cred}" class="credencial-img">
                    <h2 class="credencial-name">{mis_datos['nombre']}</h2>
                    <p class="credencial-role">{mis_datos['rol']}</p>
                    <div class="credencial-id-box">
                        <span class="credencial-id">ID: {mis_datos.get('credencial', 'FTN-0000')}</span>
                    </div>
                    <div class="barcode">*{mis_datos.get('credencial', 'FTN-0000')}*</div>
                </div>
            """, unsafe_allow_html=True)

        with tab_dir:
            busqueda = st.text_input("🔎 Buscar talento por nombre o rol...", placeholder="Ej: Director, Sonido, Laura...")
            st.markdown("<br>", unsafe_allow_html=True)
            for em, info in db_users.items():
                if info["estado"] == "Aprobado" and (busqueda.lower() in info["nombre"].lower() or busqueda.lower() in info["rol"].lower()):
                    with st.container(border=True):
                        colD1, colD2 = st.columns([1, 6])
                        with colD1:
                            if info.get("foto"): st.markdown(f"<img src='data:image/jpeg;base64,{info['foto']}' class='avatar-circle' style='width:70px;height:70px;'>", unsafe_allow_html=True)
                        with colD2:
                            st.markdown(f"<h4 style='margin:0;'>{info['nombre']} <span style='color:#6366f1;font-size:14px;'>({info['rol']})</span></h4>", unsafe_allow_html=True)
                            st.caption(f"**Skills:** {info.get('specs', 'No especificado')} | **Dieta:** {info.get('dieta', 'Ninguna')}")
                            if info.get("portfolio"): st.markdown(f"[🔗 Ver Reel]({info['portfolio']})")

    # ==========================================
    # VISTA 3: PROYECTO (MÓDULOS)
    # ==========================================
    elif st.session_state["ruta"] == "Proyecto":
        proyecto_elegido = st.session_state["proyecto_activo"]
        p_data = st.session_state["proyectos"][proyecto_elegido]
        
        st.markdown(f"<h1 style='text-align:center; color:#1e1b4b; font-weight:900;'>{proyecto_elegido.upper()}</h1>", unsafe_allow_html=True)
        
        # --- NAVEGADOR DE DEPARTAMENTOS (Rediseño UX central) ---
        opciones_nav = ["⟡ Panel de Control", "⟡ Chat Central IA"]
        if nivel_actual != "lectura": opciones_nav.append("⟡ Solicitar Equipos a Prod.")
        opciones_nav.extend(["⟡ Comparador de Rentals", "⟡ Baúl y Archivos", "⟡ Tablón de Avisos", "⟡ Portfolio y Links"])
        
        if rol_actual == "Super Admin":
            opciones_nav.extend([
                "⟡ Gestión de Accesos", "⟡ Control de Presupuesto", "⟡ Bandeja de Pedidos (Prod)", "⟡ Locaciones y Scouting", "⟡ Registro de Crew", "⟡ Casting y Actores", "⟡ Planilla de Catering",
                "⟡ Desglose de Guion", "⟡ Laboratorio de Guion", "⟡ Inventario General", "⟡ Plan de Rodaje (AD)", "⟡ Planos y Dirección", "⟡ DF: Plantas de Luces y Lentes", "⟡ DF: Referencias Visuales IA",
                "⟡ Departamento de Arte", "⟡ Reportes de Sonido", "⟡ Notas de Continuidad"
            ])
        else:
            if rol_actual == "Producción": opciones_nav.extend(["⟡ Control de Presupuesto", "⟡ Bandeja de Pedidos (Prod)", "⟡ Locaciones y Scouting", "⟡ Registro de Crew", "⟡ Casting y Actores", "⟡ Planilla de Catering"])
            else:
                if nivel_actual != "lectura": opciones_nav.extend(["⟡ Inventario General"])
            if rol_actual == "Guion": opciones_nav.extend(["⟡ Desglose de Guion", "⟡ Laboratorio de Guion"])
            if "Dirección" in rol_actual and rol_actual not in ["Dirección de Arte", "Dirección de Fotografía"]: opciones_nav.extend(["⟡ Casting y Actores", "⟡ Plan de Rodaje (AD)", "⟡ Planos y Dirección"])
            if rol_actual == "Dirección de Fotografía": opciones_nav.extend(["⟡ DF: Plantas de Luces y Lentes", "⟡ DF: Referencias Visuales IA"])
            if rol_actual == "Dirección de Arte": opciones_nav.append("⟡ Departamento de Arte")
            if "Sonido" in rol_actual: opciones_nav.extend(["⟡ Reportes de Sonido"])
            if rol_actual == "Continuidad": opciones_nav.append("⟡ Notas de Continuidad")

        c_nav1, c_nav2, c_nav3 = st.columns([1, 2, 1])
        with c_nav2:
            st.markdown("<p style='text-align:center; font-weight:700; color:#6366f1; margin-bottom:5px;'>🛸 NAVEGADOR DE DEPARTAMENTOS</p>", unsafe_allow_html=True)
            seccion_elegida = st.selectbox("", opciones_nav, label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)

        # --- LÓGICA DE LOS MÓDULOS ---
        if seccion_elegida == "⟡ Panel de Control":
            # Dashboard de métricas del proyecto rediseñado
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Crew", len(p_data["crew"]))
            with col2: st.metric("Locaciones", len(p_data["locaciones"]))
            with col3: st.metric("Equipos", len(p_data["equipos"]))
            with col4: st.metric("Pedidos P.", len(p_data["pedidos_equipos"]))
            
            st.divider()
            st.markdown("<h3 style='text-align:center;'>⚡ Generador de Call Sheet (IA)</h3>", unsafe_allow_html=True)
            c_btn1, c_btn2, c_btn3 = st.columns([1, 2, 1])
            with c_btn2:
                if st.button("✨ Generar Call Sheet Automático", use_container_width=True):
                    try:
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        modelo = genai.GenerativeModel('gemini-3.5-flash')
                        datos = f"Avisos: {p_data['avisos']} | Equipo: {p_data['crew']} | Locaciones: {p_data['locaciones']}"
                        prompt = f"Sos FTN AI. Proyecto: {proyecto_elegido}. Datos: {datos}. Redactá un Call Sheet ultra profesional en markdown."
                        with st.spinner("Procesando la lógica del rodaje..."):
                            respuesta = modelo.generate_content(prompt)
                            st.success("Documento Generado:")
                            st.markdown(f"<div style='background:white; padding:20px; border-radius:15px; color:black;'>{respuesta.text}</div>", unsafe_allow_html=True)
                    except: st.error("Falta configurar la API Key de Gemini en Secrets.")

        elif seccion_elegida == "⟡ Solicitar Equipos a Prod.":
            colA, colB = st.columns([3, 1])
            with colA: st.markdown("<h2>📋 Mis Pedidos</h2>", unsafe_allow_html=True)
            with colB: 
                if st.button("➕ Enviar Solicitud", use_container_width=True): ventana_pedido(proyecto_elegido, rol_actual)
            st.divider()
            mis_pedidos = [p for p in p_data["pedidos_equipos"] if p["area"] == rol_actual or rol_actual == "Super Admin"]
            if not mis_pedidos: st.info("Bandeja vacía.")
            else:
                for ped in mis_pedidos:
                    with st.container(border=True):
                        st.write(f"**Ítem:** {ped['item']} | **Uso:** {ped['notas']}")
                        if ped['estado'] == "Pendiente": st.warning("🕒 Pendiente")
                        elif ped['estado'] == "Aprobado": st.success("✅ Aprobado")
                        else: st.error(f"❌ {ped['estado']}")

        elif seccion_elegida == "⟡ Bandeja de Pedidos (Prod)":
            st.markdown("<h2>Bandeja de Aprobaciones</h2>", unsafe_allow_html=True)
            if not p_data["pedidos_equipos"]: st.info("Todo al día.")
            for i, ped in enumerate(p_data["pedidos_equipos"]):
                if ped['estado'] == "Pendiente":
                    with st.container(border=True):
                        st.markdown(f"**De:** {ped['area']} | **Ítem:** {ped['item']}")
                        st.caption(f"Notas: {ped['notas']}")
                        c1, c2, c3 = st.columns(3)
                        if c1.button("✅ Aprobar", key=f"p_ap_{i}", use_container_width=True):
                            p_data["equipos"].append({"area": ped['area'], "item": ped['item'], "cant": 1, "tipo": "A Confirmar", "rental": "A Definir"})
                            p_data["pedidos_equipos"][i]["estado"] = "Aprobado"
                            guardar_y_recargar()
                        if c2.button("❌ Rechazar", key=f"p_re_{i}", use_container_width=True):
                            p_data["pedidos_equipos"][i]["estado"] = "Rechazado"
                            guardar_y_recargar()
                        if c3.button("🔍 Buscar Precio", key=f"p_bus_{i}", use_container_width=True):
                            st.info("Función conectada al comparador (Ir al Módulo de Rentals).")

        elif seccion_elegida == "⟡ Comparador de Rentals":
            colA, colB, colC = st.columns([2, 1, 1])
            with colA: st.markdown("<h2>🛒 Comparador Inteligente</h2>", unsafe_allow_html=True)
            with colB: 
                if st.button("🏬 Add Rental", use_container_width=True): ventana_nuevo_rental(proyecto_elegido)
            with colC: 
                if st.button("🤖 Escanear Equipos", use_container_width=True): ventana_comparador_rental(proyecto_elegido)
            if rol_actual == "Super Admin":
                if st.button("🗑️ Resetear Base de Rentals", type="secondary"): ventana_vaciar_comparador(proyecto_elegido)
            
            st.divider()
            carrito = p_data.get("carrito_rentals", [])
            if len(carrito) > 0:
                with st.container(border=True):
                    c_txt, c_btn = st.columns([3, 1])
                    with c_txt: st.markdown("<h3 style='margin:0; color:#4f46e5;'>CARRITO DE PRODUCCIÓN</h3>", unsafe_allow_html=True)
                    with c_btn:
                        if st.button("✅ FINALIZAR", use_container_width=True, type="primary"): ventana_checkout(proyecto_elegido)
                    
                    cols_cart = st.columns(4)
                    total_cart = 0
                    for i, item in enumerate(carrito):
                        total_cart += item["precio"]
                        with cols_cart[i % 4]:
                            with st.container(border=True):
                                st.markdown(f"<p style='font-size:12px; font-weight:bold; color:#6366f1; margin:0;'>{item.get('rental', 'N/A')}</p>", unsafe_allow_html=True)
                                st.markdown(f"<p style='font-weight:700; margin:0;'>{item['nombre'][:25]}...</p>", unsafe_allow_html=True)
                                st.markdown(f"**${item['precio']:,.2f}**")
                                if st.button("Quitar", key=f"quit_cart_{i}", use_container_width=True):
                                    p_data["carrito_rentals"].pop(i)
                                    guardar_y_recargar()
                    st.markdown(f"<h4 style='text-align:right;'>Total Día: ${total_cart:,.2f}</h4>", unsafe_allow_html=True)
            
            st.markdown("### 🔍 Catálogo de Equipos")
            rentals_lista = p_data.get("comparador_rentals", [])
            if not rentals_lista: st.info("Usá el botón 'Escanear Equipos' para agregar productos.")
            else:
                texto_busqueda = st.text_input("Buscar lentes, luces, cámaras...", placeholder="Ej: Arri Alexa...")
                rentals_mostrar = [(idx, r) for idx, r in enumerate(rentals_lista) if texto_busqueda.lower() in r['nombre'].lower()]
                if rentals_mostrar:
                    precios_validos = [r["precio"] for _, r in rentals_mostrar if r["precio"] > 0]
                    menor_precio = min(precios_validos) if precios_validos else 0

                    cols = st.columns(3)
                    for i, (idx_orig, r) in enumerate(rentals_mostrar):
                        with cols[i % 3]:
                            with st.container(border=True):
                                if r["precio"] == menor_precio and r["precio"] > 0:
                                    st.markdown("<span style='background:#10b981; color:white; padding:3px 10px; border-radius:10px; font-size:10px; font-weight:800;'>MÁS BARATO</span>", unsafe_allow_html=True)
                                st.markdown(f"<p style='font-size:12px; font-weight:bold; color:#6366f1; margin:0; margin-top:5px;'>{r.get('rental', 'N/A')}</p>", unsafe_allow_html=True)
                                st.markdown(f"#### {r['nombre']}")
                                st.markdown(f"<h3 style='margin:0;'>${r['precio']:,.2f}</h3>", unsafe_allow_html=True)
                                c_add, c_del = st.columns(2)
                                if c_add.button("Sumar", key=f"add_{idx_orig}", use_container_width=True, type="primary"):
                                    p_data["carrito_rentals"].append(r)
                                    guardar_y_recargar()
                                if c_del.button("Borrar", key=f"del_{idx_orig}", use_container_width=True):
                                    p_data["comparador_rentals"].pop(idx_orig)
                                    guardar_y_recargar()
                else: st.warning("Sin resultados.")

        elif seccion_elegida == "⟡ DF: Plantas de Luces y Lentes":
            st.markdown("<h2>📐 Blueprint: Planta de Luces</h2>", unsafe_allow_html=True)
            tab1, tab2 = st.tabs(["🗺️ Lienzo de Trazado", "🧮 Calculadora DOF"])
            with tab1:
                col_h, col_c, col_s = st.columns([1, 2.5, 1])
                with col_h:
                    st.markdown("**Herramientas**")
                    modo = st.selectbox("Trazado", ["freedraw", "line", "rect", "circle", "transform"])
                    color_mapping = {"🟡 Principal": "#FFD700", "🔵 Relleno": "#1E90FF", "🟣 Contraluz": "#8A2BE2", "🔴 Actor": "#FF4500", "🎥 Cámara": "#FFFFFF"}
                    tipo = st.radio("Elemento", list(color_mapping.keys()))
                    grosor = st.slider("Grosor", 1, 10, 3)
                with col_c:
                    st_canvas(fill_color="rgba(255,255,255,0)", stroke_width=grosor, stroke_color=color_mapping[tipo], background_color="#1b263b", width=500, height=450, drawing_mode=modo, key="canvas_luces_pro")
                with col_s:
                    st.markdown("**Metadata del Set**")
                    escena = st.text_input("Escena/Set")
                    hora = st.selectbox("Clima", ["Día", "Noche", "Atardecer"])
                    amps = st.number_input("Amperes Disp.", value=60)
                    if st.button("Guardar Ficha"): st.success("Guardado.")
            with tab2:
                c1, c2, c3 = st.columns(3)
                c1.number_input("Focal (mm)", value=50)
                c2.number_input("Apertura (f/)", value=2.8)
                c3.number_input("Distancia (m)", value=3.0)
                st.info("Datos hiperfocales listos para procesar.")

        elif seccion_elegida == "⟡ Gestión de Accesos":
            st.markdown("<h2>👑 Permisos y Niveles</h2>", unsafe_allow_html=True)
            mapa = {"Super Admin": "jefe_supremo", "Producción": "jefe", "Dirección": "jefe", "Dirección de Fotografía": "jefe", "Dirección de Arte": "jefe", "Director de Sonido": "jefe", "Asistente de Sonido": "asistente", "Guion": "jefe", "Continuidad": "jefe", "Invitado": "lectura"}
            for em_usr, dt_usr in st.session_state["proyectos"]["_CONFIG_"]["usuarios"].items():
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([2, 1.5, 1.5, 1])
                    c1.markdown(f"**{dt_usr['nombre']}**<br><span style='font-size:12px; color:gray;'>{em_usr}</span>", unsafe_allow_html=True)
                    est = c2.selectbox("Estado", ["Aprobado", "Pendiente"], index=0 if dt_usr.get("estado") == "Aprobado" else 1, key=f"e_{em_usr}")
                    rol = c3.selectbox("Rol", list(mapa.keys()), index=list(mapa.keys()).index(dt_usr["rol"]) if dt_usr["rol"] in mapa else 9, key=f"r_{em_usr}")
                    if c4.button("Guardar", key=f"b_{em_usr}"):
                        st.session_state["proyectos"]["_CONFIG_"]["usuarios"][em_usr].update({"estado": est, "rol": rol, "nivel": mapa[rol]})
                        guardar_y_recargar()

        # [Todos los demás módulos mantienen la MISMA lógica pero con st.markdown h2 para limpieza visual]
        elif seccion_elegida == "⟡ Portfolio y Links":
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown("<h2>Repositorio de Enlaces</h2>", unsafe_allow_html=True)
            with c2: 
                if st.button("➕ Link Nuevo", use_container_width=True): ventana_link(proyecto_elegido)
            st.divider()
            for lk in p_data["links"]:
                with st.container(border=True): st.markdown(f"### 🔗 [{lk['titulo']}]({lk['url']})\n{lk['desc']}")

        elif seccion_elegida == "⟡ Control de Presupuesto":
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1: st.markdown("<h2>Finanzas de Rodaje</h2>", unsafe_allow_html=True)
            with c2: 
                if st.button("➕ Asignar Gasto", use_container_width=True): ventana_presupuesto(proyecto_elegido)
            with c3:
                if p_data["presupuesto"]: st.download_button("⬇️ Excel", data=pd.DataFrame(p_data["presupuesto"]).to_csv(index=False).encode('utf-8'), file_name="budget.csv", mime="text/csv", use_container_width=True)
            st.divider()
            total = sum(i['costo'] for i in p_data["presupuesto"])
            st.success(f"**CAPITAL EJECUTADO: ${total:,.2f}**")
            for item in p_data["presupuesto"]:
                with st.container(border=True): st.markdown(f"**{item['estado']}** | ${item['costo']:,.2f} - {item['item']} ({item['area']})")

        elif seccion_elegida == "⟡ Casting y Actores":
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown("<h2>Talentos (Casting)</h2>", unsafe_allow_html=True)
            with c2: 
                if st.button("➕ Ingresar Talento", use_container_width=True): ventana_casting(proyecto_elegido)
            st.divider()
            for a in p_data["casting"]:
                with st.container(border=True):
                    st.markdown(f"### {a['actor']} ➔ {a['personaje']}")
                    st.write(f"[Ver Videobook]({a['reel']})")
                    if a.get("foto"): st.image(base64.b64decode(a["foto"]), width=150)

        elif seccion_elegida == "⟡ Desglose de Guion":
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown("<h2>Script Breakdown</h2>", unsafe_allow_html=True)
            with c2: 
                if st.button("➕ Desglosar", use_container_width=True): ventana_desglose(proyecto_elegido)
            st.divider()
            for d in p_data["desglose"]:
                with st.container(border=True): st.markdown(f"**ESC {d['escena']} | {d['intext']} | {d['dianoche']}**<br>{d['desc']}", unsafe_allow_html=True)

        elif seccion_elegida == "⟡ Plan de Rodaje (AD)":
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown("<h2>Tiempos (Cronograma)</h2>", unsafe_allow_html=True)
            with c2: 
                if st.button("➕ Agregar Bloque", use_container_width=True): ventana_cronograma(proyecto_elegido)
            st.divider()
            for a in sorted(p_data["plan_rodaje"], key=lambda x: x.get('hora', '00:00')):
                with st.container(border=True): st.markdown(f"<h4 style='margin:0; color:#6366f1;'>{a.get('hora', '')}</h4><p style='margin:0; font-size:18px;'>{a['actividad']}</p>", unsafe_allow_html=True)

        elif seccion_elegida == "⟡ DF: Referencias Visuales IA":
            st.markdown("<h2>🧠 Laboratorio Visual IA</h2>", unsafe_allow_html=True)
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                mod_foto = genai.GenerativeModel('gemini-3.5-flash')
                msg_foto = st.chat_input("Buscá referencias (Ej: Iluminación neon noir)...")
                if msg_foto:
                    st.markdown(f"**Vos:** {msg_foto}")
                    resp = mod_foto.generate_content(f"Sos un DF experto. Da referencias y poné link: [🖼️ Ver ESTO](https://www.google.com/search?tbm=isch&q=TERMINOS)\n\nConsulta: {msg_foto}")
                    st.info(f"**IA:** {resp.text}")
            except: st.error("Falta API Key.")

        elif seccion_elegida == "⟡ Locaciones y Scouting":
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown("<h2>Scouting</h2>", unsafe_allow_html=True)
            with c2: 
                if st.button("➕ Locación", use_container_width=True): ventana_locacion(proyecto_elegido)
            st.divider()
            for loc in p_data["locaciones"]:
                with st.container(border=True):
                    st.markdown(f"### 📍 {loc['nombre']}")
                    st.write(f"**Dir:** {loc['direccion']} | **Status:** {loc['permisos']}")
                    if loc['lat'] != 0.0: st.map(pd.DataFrame({'lat': [loc['lat']], 'lon': [loc['lon']]}), zoom=15, height=200)

        elif seccion_elegida == "⟡ Registro de Crew":
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown("<h2>Base de Crew</h2>", unsafe_allow_html=True)
            with c2: 
                if st.button("➕ Fichar", use_container_width=True): ventana_crew(proyecto_elegido)
            st.divider()
            for p in p_data["crew"]:
                with st.container(border=True): st.markdown(f"**{p['nombre']}** — {p['rol']}")

        elif seccion_elegida == "⟡ Planilla de Catering":
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown("<h2>Dietas Set</h2>", unsafe_allow_html=True)
            with c2: 
                if st.button("➕ Restricción", use_container_width=True): ventana_catering(proyecto_elegido)
            st.divider()
            for p in p_data["catering"]:
                with st.container(border=True): st.markdown(f"**{p['nombre']}** | 🍽️ {p['dieta']}")

        elif seccion_elegida == "⟡ Tablón de Avisos":
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown("<h2>Tablón Central</h2>", unsafe_allow_html=True)
            with c2: 
                if st.button("➕ Comunicar", use_container_width=True): ventana_aviso(proyecto_elegido, mis_datos['nombre'], p_data["locaciones"])
            st.divider()
            for aviso in reversed(p_data["avisos"]):
                with st.container(border=True): st.markdown(f"**{aviso['autor']}**: {aviso.get('texto', 'Citación cargada.')}")

        elif seccion_elegida == "⟡ Baúl y Archivos":
            st.markdown("<h2>Repositorio Documental</h2>", unsafe_allow_html=True)
            archivo = st.file_uploader("Documento de texto (.txt)", type=["txt"])
            if archivo and st.button("Procesar Doc"):
                p_data["archivos_pendientes"].append({"autor": mis_datos['nombre'], "nombre": archivo.name, "texto": archivo.getvalue().decode('utf-8')})
                guardar_y_recargar()
                
            if len(p_data["archivos_pendientes"]) > 0:
                st.markdown("### ⏳ Pendientes de Aprobación")
                for i, doc in enumerate(p_data["archivos_pendientes"]):
                    with st.container(border=True):
                        st.write(f"📄 {doc['nombre']} ({doc['autor']})")
                        c1, c2 = st.columns(2)
                        if c1.button("✅ Ok", key=f"ap_{i}"):
                            p_data["contexto_aprobado"] += f"\n\n[Doc]: {doc['texto']}"
                            p_data["archivos_pendientes"].pop(i)
                            guardar_y_recargar()
                        if c2.button("❌ No", key=f"re_{i}"):
                            p_data["archivos_pendientes"].pop(i)
                            guardar_y_recargar()

        elif seccion_elegida == "⟡ Inventario General":
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown("<h2>Inventario Activo</h2>", unsafe_allow_html=True)
            with c2: 
                if st.button("➕ Sumar Equipo", use_container_width=True): ventana_equipo(proyecto_elegido, rol_actual)
            st.divider()
            for eq in p_data["equipos"]:
                with st.container(border=True): st.markdown(f"**{eq['cant']}x {eq['item']}** | {eq['area']} | {eq['tipo']}")

        elif seccion_elegida == "⟡ Laboratorio de Guion":
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown("<h2>Diseño Narrativo</h2>", unsafe_allow_html=True)
            with c2: 
                if st.button("➕ Personaje", use_container_width=True): ventana_personaje(proyecto_elegido)
            st.divider()
            for p in p_data["personajes"]:
                with st.container(border=True): st.markdown(f"### {p['nombre']} ({p['rol']})")

        elif seccion_elegida == "⟡ Departamento de Arte":
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown("<h2>Arte y Utilería</h2>", unsafe_allow_html=True)
            with c2: 
                if st.button("➕ Elemento", use_container_width=True): ventana_arte(proyecto_elegido)
            st.divider()
            for item in p_data["arte"]:
                with st.container(border=True):
                    st.markdown(f"**{item['estado']}** | {item['objeto']}")
                    if item.get("foto"): st.image(base64.b64decode(item["foto"]), width=150)

        elif seccion_elegida == "⟡ Planos y Dirección":
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1: st.markdown("<h2>Shot List / Monitor</h2>", unsafe_allow_html=True)
            with c2: 
                if st.button("➕ Plano", use_container_width=True): ventana_plano(proyecto_elegido)
            with c3: 
                if st.button("➕ Toma (DIR)", use_container_width=True): ventana_toma_dir(proyecto_elegido)
            st.divider()
            for t in p_data["tomas_dir"]:
                with st.container(border=True): st.markdown(f"{t['evaluacion']} | **ESC {t['escena']} - TOMA {t['toma']}**")

        elif seccion_elegida == "⟡ Reportes de Sonido":
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown("<h2>Log de Sonido</h2>", unsafe_allow_html=True)
            with c2: 
                if st.button("➕ Track", use_container_width=True): ventana_sonido(proyecto_elegido)
            st.divider()
            for s in reversed(p_data["sonido_log"]):
                with st.container(border=True): st.markdown(f"🎧 **ESC {s['escena']} | T {s['toma']}**")

        elif seccion_elegida == "⟡ Notas de Continuidad":
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown("<h2>Raccord Central</h2>", unsafe_allow_html=True)
            with c2: 
                if st.button("➕ Raccord", use_container_width=True): ventana_continuidad(proyecto_elegido)
            st.divider()
            for nota in reversed(p_data["continuidad"]):
                with st.container(border=True): st.markdown(f"🎬 **ESC {nota['escena']} - T {nota['toma']}**<br>{nota['detalle']}", unsafe_allow_html=True)

        elif seccion_elegida == "⟡ Chat Central IA":
            st.markdown("<h2>⚡ Asistente Director (IA)</h2>", unsafe_allow_html=True)
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                modelo = genai.GenerativeModel('gemini-3.5-flash')
                mensaje = st.chat_input("Preguntá algo al contexto del guion...")
                if mensaje:
                    st.chat_message("user").write(mensaje)
                    resp = modelo.generate_content(f"Sos FTN AI. Hablás con: {mis_datos['nombre']}. Contexto: {p_data['contexto_aprobado']}\nUsuario: {mensaje}")
                    st.chat_message("assistant").write(resp.text)
            except: st.error("Falta API Key.")

    # --- WIDGET FLOTANTE (ESTÉTICA MEJORADA) ---
    st.markdown("""
        <style>
        .floating-chat-container { position: fixed; bottom: 30px; right: 30px; z-index: 99999; }
        .stPopover button { border-radius: 50% !important; width: 60px; height: 60px; font-size: 24px; box-shadow: 0 10px 25px rgba(99, 102, 241, 0.5) !important;}
        </style>
        <div class="floating-chat-container">
    """, unsafe_allow_html=True)

    with st.popover("💬"):
        st.markdown("<h4 style='margin:0;'>Soporte IA</h4>", unsafe_allow_html=True)
        if "chat_widget_mensajes" not in st.session_state: st.session_state["chat_widget_mensajes"] = [{"role": "assistant", "content": "Hola, ¿Dudas con los rentals?"}]
        for msg in st.session_state["chat_widget_mensajes"]:
            if msg["role"] == "assistant": st.info(msg["content"])
            else: st.success(msg["content"])
                
        pregunta = st.text_input("Escribe...", key="input_widget")
        if st.button("Enviar", key="btn_widget", use_container_width=True):
            if pregunta:
                st.session_state["chat_widget_mensajes"].append({"role": "user", "content": pregunta})
                try:
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    mod_w = genai.GenerativeModel('gemini-3.5-flash')
                    st.session_state["chat_widget_mensajes"].append({"role": "assistant", "content": mod_w.generate_content(f"Sos experto en cine: {pregunta}").text})
                except: st.session_state["chat_widget_mensajes"].append({"role": "assistant", "content": "Error de API."})
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
