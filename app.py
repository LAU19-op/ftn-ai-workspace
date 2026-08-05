import streamlit as st
import re
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
from datetime import datetime, timedelta, timezone
import random
import time
import streamlit.components.v1 as components

# Importación de Spotify para la conexión en tiempo real
try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
    SPOTIPY_INSTALLED = True
except ImportError:
    SPOTIPY_INSTALLED = False

# --- 1. CONFIGURACIÓN INICIAL Y ESTADO ---
st.set_page_config(page_title="Fetén Workspace Pro", page_icon="✦", layout="wide", initial_sidebar_state="collapsed")

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

LOGO_URL = "https://i.supaimg.com/4a90693e-1b41-4313-8203-f60c8b81825f/da7de7fd-3ded-4499-b3f4-790424f0dc5a.png"
TZ_AR = timezone(timedelta(hours=-3))

def obtener_hora_actual():
    return datetime.now(TZ_AR).strftime("%Y-%m-%d %H:%M:%S")

# --- 2. SVGS UNIVERSALES (Minimalismo Puro) ---
SVG_LIKE = '<svg class="icon-svg" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>'
SVG_LIKE_FILLED = '<svg class="icon-svg" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="#FBAF3B" stroke="#FBAF3B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>'
SVG_COMMENT = '<svg class="icon-svg" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>'
SVG_REPOST = '<svg class="icon-svg" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="17 1 21 5 17 9"></polyline><path d="M3 11V9a4 4 0 0 1 4-4h14"></path><polyline points="7 23 3 19 7 15"></polyline><path d="M21 13v2a4 4 0 0 1-4 4H3"></path></svg>'
SVG_REPOST_FILLED = '<svg class="icon-svg" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#22C55E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="17 1 21 5 17 9"></polyline><path d="M3 11V9a4 4 0 0 1 4-4h14"></path><polyline points="7 23 3 19 7 15"></polyline><path d="M21 13v2a4 4 0 0 1-4 4H3"></path></svg>'
SVG_SAVE = '<svg class="icon-svg" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg>'
SVG_SAVE_FILLED = '<svg class="icon-svg" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="#3B82F6" stroke="#3B82F6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg>'

# --- 3. MOTOR DE ESTILOS (LINEAR/VERCEL VIBE) ---
def get_css():
    if st.session_state.theme == "dark":
        return """
        :root { --bg-base: #000000; --bg-card: #0A0A0C; --bg-hover: #121216; --border-color: #1A1A1E; --border-hover: #3F3F46; --text-main: #FAFAFA; --text-muted: #71717A; --accent: #FBAF3B; --accent-glow: rgba(251, 175, 59, 0.1); }
        .logo-img { filter: brightness(1.2) contrast(1.2); }
        """
    else:
        return """
        :root { --bg-base: #F4F4F5; --bg-card: #FFFFFF; --bg-hover: #FAFAFA; --border-color: #E4E4E7; --border-hover: #A1A1AA; --text-main: #09090B; --text-muted: #52525B; --accent: #D97706; --accent-glow: rgba(217, 119, 6, 0.1); }
        .logo-img { filter: brightness(0.2) contrast(1.2); }
        """

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    {get_css()}
    
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif !important; }}
    #MainMenu {{visibility: hidden;}} header {{visibility: hidden;}} footer {{visibility: hidden;}}
    
    .stApp {{ background-color: var(--bg-base) !important; color: var(--text-main) !important; transition: all 0.3s ease; }}
    .logo-img {{ display: block; max-width: 100%; height: auto; transition: filter 0.3s; }}

    /* Tarjetas Modulares - Efecto Glass y Borde Limpio */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: var(--bg-card) !important; border: 1px solid var(--border-color) !important; 
        border-radius: 12px !important; padding: 1.5rem !important; 
        box-shadow: 0 4px 24px rgba(0,0,0,0.04) !important; margin-bottom: 16px !important; transition: all 0.3s ease !important;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
        border-color: var(--border-hover) !important; transform: translateY(-2px); box-shadow: 0 8px 32px var(--accent-glow) !important;
    }}
    
    /* Tipografía Premium */
    h1, h2, h3 {{ font-weight: 800 !important; letter-spacing: -0.03em !important; color: var(--text-main) !important; }}
    .gradient-text {{ background: linear-gradient(135deg, var(--text-main) 0%, var(--text-muted) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }}
    .section-title {{ color: var(--text-muted); font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 12px; display:block; }}

    /* Inputs Limpios */
    .stTextInput input, .stSelectbox select, .stNumberInput input, .stDateInput input, .stTimeInput input, .stTextArea textarea, .stChatInput input {{
        background-color: var(--bg-base) !important; border: 1px solid var(--border-color) !important; color: var(--text-main) !important;
        border-radius: 8px !important; padding: 12px 16px !important; font-weight: 400 !important; transition: all 0.2s;
    }}
    .stTextInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {{ border-color: var(--accent) !important; box-shadow: 0 0 0 1px var(--accent) !important; }}
    
    /* Botones Genéricos */
    .stButton button {{
        background: var(--bg-card) !important; border: 1px solid var(--border-color) !important; color: var(--text-main) !important;
        border-radius: 8px !important; font-weight: 600 !important; transition: all 0.2s ease !important;
    }}
    .stButton button:hover {{ background: var(--bg-hover) !important; border-color: var(--accent) !important; color: var(--accent) !important; }}
    .stButton button p {{ font-weight: 600 !important; color: inherit !important; margin: 0; }}
    
    /* Botón Primario Custom */
    button[kind="primary"] {{ background: var(--text-main) !important; border: none !important; color: var(--bg-base) !important; }}
    button[kind="primary"]:hover {{ transform: scale(1.02); color: var(--bg-base) !important; opacity: 0.9; }}
    button[kind="primary"] p {{ color: var(--bg-base) !important; }}

    /* Botones Secundarios Aesthetic (Translucidos, sin fondo) */
    [data-testid="stBaseButton-secondary"] {{ background: transparent !important; border: 1px solid var(--border-color) !important; color: var(--text-muted) !important; box-shadow: none !important; }}
    [data-testid="stBaseButton-secondary"]:hover {{ background: rgba(255,255,255,0.03) !important; border-color: var(--text-muted) !important; color: var(--text-main) !important; }}

    /* Botones de Navegación Superiores (Totalmente invisibles hasta el hover) */
    .nav-btn-top button {{ border: none !important; background: transparent !important; font-weight: 600 !important; }}
    .nav-btn-top button:hover {{ background: var(--bg-hover) !important; color: var(--text-main) !important; border-radius: 8px !important; }}

    /* RED SOCIAL UI */
    .post-header {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }}
    .post-avatar {{ width: 44px; height: 44px; border-radius: 50%; object-fit: cover; margin-right: 12px; border: 1px solid var(--border-color); }}
    .post-name {{ font-weight: 700; color: var(--text-main); font-size: 15px; margin: 0; display: flex; align-items: center; gap: 4px; }}
    .post-handle {{ color: var(--text-muted); font-size: 13px; font-weight: 400; }}
    .post-body {{ font-size: 15px; color: var(--text-main); margin-top: 4px; margin-bottom: 16px; line-height: 1.5; white-space: pre-wrap; }}
    .post-img {{ width: 100%; border-radius: 12px; border: 1px solid var(--border-color); margin-bottom: 16px; max-height: 500px; object-fit: cover; }}
    
    .badge-verified {{ color: #3B82F6; font-size: 14px; margin-top: 2px; }}
    .repost-badge {{ font-size: 12px; color: var(--text-muted); font-weight: 600; margin-bottom: 8px; display: flex; align-items:center; gap:6px; }}
    
    /* Historias Verticales (Snippets) */
    .snippets-tray {{ display: flex; gap: 12px; overflow-x: auto; padding-bottom: 10px; margin-bottom: 20px; }}
    .snippets-tray::-webkit-scrollbar {{ height: 0px; }}
    .snippet-card {{ min-width: 100px; height: 150px; border-radius: 12px; position: relative; overflow: hidden; border: 1px solid var(--border-color); cursor: pointer; transition: transform 0.2s; background-size: cover; background-position: center; }}
    .snippet-card:hover {{ transform: scale(1.03); border-color: var(--accent); }}
    .snippet-overlay {{ position: absolute; bottom: 0; left: 0; right: 0; padding: 12px 8px 8px 8px; background: linear-gradient(to top, rgba(0,0,0,0.8), transparent); display: flex; flex-direction: column; align-items: flex-start; }}
    .snippet-avatar {{ width: 24px; height: 24px; border-radius: 50%; border: 2px solid var(--accent); margin-bottom: 4px; object-fit: cover;}}
    .snippet-name {{ font-size: 11px; color: #FFF; font-weight: 600; text-shadow: 0 1px 2px #000; }}

    /* Misc */
    .online-indicator {{ display: inline-block; width: 8px; height: 8px; background-color: #22C55E; border-radius: 50%; margin-right: 6px; box-shadow: 0 0 8px rgba(34, 197, 94, 0.4); }}
    .icon-svg {{ vertical-align: middle; margin-right: 6px; margin-bottom: 2px; }}
    .hashtag {{ color: var(--accent); font-weight: 500; cursor: pointer; }}
    .mention {{ color: #3B82F6; font-weight: 500; cursor: pointer; }}

    [data-testid="stMetricValue"] {{ color: var(--text-main) !important; font-size: 2.2rem !important; font-weight: 800 !important; letter-spacing: -1px; }}
    [data-testid="stMetricLabel"] {{ color: var(--text-muted) !important; text-transform: uppercase !important; letter-spacing: 1px !important; font-size: 0.75rem !important; font-weight: 600 !important; }}

    @media (max-width: 768px) {
        [data-testid="column"] { width: 100% !important; flex: 100% !important; min-width: 100% !important; margin-bottom: 10px !important; }
        .block-container { padding: 1rem !important; }
    }
    </style>
""", unsafe_allow_html=True)

def format_text(texto):
    texto = re.sub(r'(#\w+)', r'<span class="hashtag">\1</span>', texto)
    texto = re.sub(r'(@\w+)', r'<span class="mention">\1</span>', texto)
    return texto

ARCHIVO_BD = "ftn_database.json"

# --- 4. BASE DE DATOS Y MIGRACIÓN ---
def guardar_y_recargar():
    with open(ARCHIVO_BD, "w", encoding="utf-8") as f:
        json.dump(st.session_state["proyectos"], f, ensure_ascii=False, indent=4)
    st.rerun()

def inicializar_bd():
    if "proyectos" not in st.session_state:
        if os.path.exists(ARCHIVO_BD):
            with open(ARCHIVO_BD, "r", encoding="utf-8") as f: data_cargada = json.load(f)
        else: data_cargada = {}

        if "_CONFIG_" not in data_cargada: data_cargada["_CONFIG_"] = {"usuarios": {}}
        conf = data_cargada["_CONFIG_"]
        
        for lb in ["recordatorios", "notificaciones", "mensajes", "tickets_soporte", "social_posts", "social_stories"]:
            if lb not in conf: conf[lb] = []

        if "lau@admin.com" not in conf.get("usuarios", {}):
            conf["usuarios"]["lau@admin.com"] = {"nombre": "Lau", "pass": "1234", "rol": "Super Admin", "nivel": "jefe_supremo", "estado": "Aprobado", "foto": "", "credencial": "FTN-0001", "edad": "", "roles_fav": "Directora", "specs": "Amo el cine oscuro.", "portfolio": "", "spotify_token": None, "spotify_track_id": None, "amigos": ["director@feten.com", "arte@feten.com"], "acceso_rapido": "Panel General", "alias": "lau_ok", "estado_txt": "Editando", "guardados": []}
        if "director@feten.com" not in conf.get("usuarios", {}):
            conf["usuarios"]["director@feten.com"] = {"nombre": "Matias", "pass": "1234", "rol": "Dirección", "nivel": "jefe", "estado": "Aprobado", "foto": "", "credencial": "FTN-0002", "edad": "35", "roles_fav": "Cine", "specs": "Ópticas anamórficas.", "portfolio": "", "spotify_token": None, "spotify_track_id": "4cOdK2wGLETKBW3PvgPWqT", "amigos": [], "acceso_rapido": "Monitor DIR", "alias": "mati_dir", "estado_txt": "En Set", "guardados": []}
        if "arte@feten.com" not in conf.get("usuarios", {}):
            conf["usuarios"]["arte@feten.com"] = {"nombre": "Sofi", "pass": "1234", "rol": "Dirección de Arte", "nivel": "jefe", "estado": "Aprobado", "foto": "", "credencial": "FTN-0003", "edad": "28", "roles_fav": "Escenografía", "specs": "Paletas de color.", "portfolio": "", "spotify_token": None, "spotify_track_id": "11dFghVXANMlKmJXsNCbNl", "amigos": [], "acceso_rapido": "Arte & Vestuario", "alias": "sofi_arte", "estado_txt": "Descanso", "guardados": []}

        if not conf["social_posts"]:
            conf["social_posts"] = [
                {"id": "p1", "usuario": "arte@feten.com", "texto": "Armando el set de los 80 #Scenography #Arte.", "imagen": None, "timestamp": (datetime.now(TZ_AR) - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"), "liked_by": ["lau@admin.com"], "comentarios": [], "reposted_by": [], "es_repost": False},
                {"id": "p2", "usuario": "director@feten.com", "texto": "Scouting terminado en San Telmo. ¡Luz increíble! @sofi_arte prepará paleta.", "imagen": None, "timestamp": (datetime.now(TZ_AR) - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"), "liked_by": [], "comentarios": [], "reposted_by": [], "es_repost": False}
            ]
            
        for em, info in conf["usuarios"].items():
            for key, val in [("amigos", []), ("spotify_token", None), ("spotify_track_id", None), ("estado", "Aprobado"), ("credencial", f"FTN-{random.randint(1000, 9999)}"), ("acceso_rapido", "Panel General"), ("alias", em.split("@")[0]), ("estado_txt", "Online"), ("guardados", [])]:
                if key not in info: info[key] = val

        for p in conf["social_posts"]:
            if "id" not in p: p["id"] = str(random.randint(100000, 999999))
            if "comentarios" not in p: p["comentarios"] = []
            if "liked_by" not in p: p["liked_by"] = []
            if "reposted_by" not in p: p["reposted_by"] = []
            if "es_repost" not in p: p["es_repost"] = False

        claves_proy = ["archivos_pendientes", "avisos", "equipos", "pedidos_equipos", "continuidad", "arte", "planos", "plan_rodaje", "plantas_luces", "sonido_log", "tomas_dir", "personajes", "locaciones", "crew", "catering", "links", "presupuesto", "casting", "desglose", "comparador_rentals", "carrito_rentals", "directorio_rentals", "kanban"]
        for nombre_proy, datos_proy in data_cargada.items():
            if nombre_proy != "_CONFIG_":
                datos_proy.setdefault("contexto_aprobado", "Proyecto base.")
                for clave in claves_proy: datos_proy.setdefault(clave, [])
                    
        st.session_state["proyectos"] = data_cargada

inicializar_bd()

if "ruta" not in st.session_state: st.session_state["ruta"] = "Inicio"
if "proyecto_activo" not in st.session_state: st.session_state["proyecto_activo"] = None
if "menu_option" not in st.session_state: st.session_state["menu_option"] = "Panel General"

# OAUTH SPOTIFY HANDLER
if SPOTIPY_INSTALLED and "code" in st.query_params and st.session_state.get("usuario_logueado"):
    try:
        if "SPOTIFY_CLIENT_ID" in st.secrets:
            sp_oauth = SpotifyOAuth(client_id=st.secrets["SPOTIFY_CLIENT_ID"], client_secret=st.secrets["SPOTIFY_CLIENT_SECRET"], redirect_uri=st.secrets["SPOTIFY_REDIRECT_URI"], scope="user-read-currently-playing")
            token_info = sp_oauth.get_access_token(st.query_params["code"])
            st.session_state["proyectos"]["_CONFIG_"]["usuarios"][st.session_state["usuario_logueado"]]["spotify_token"] = token_info
            st.query_params.clear()
            guardar_y_recargar()
    except Exception as e: st.error(f"Error OAuth Spotify: {e}")

# --- 5. MODALES (VENTANAS EMERGENTES) ---
@st.dialog("Responder")
def dialog_comentar(post_id, usuario):
    txt = st.text_area("Tu comentario", label_visibility="collapsed", placeholder="Escribe tu respuesta...", key=f"dlg_txt_{post_id}")
    if st.button("Publicar", use_container_width=True, type="primary", key=f"dlg_btn_{post_id}"):
        if txt:
            for p in st.session_state["proyectos"]["_CONFIG_"]["social_posts"]:
                if p["id"] == post_id:
                    p["comentarios"].append({"usuario": usuario, "texto": txt, "timestamp": obtener_hora_actual()})
                    guardar_y_recargar()

@st.dialog("Visualizador")
def ver_historia_dialog(b64_foto, usuario_nombre, f_avatar, tiempo):
    st.markdown(f"""
        <div style="display:flex; align-items:center; margin-bottom:12px;">
            <img src="{f_avatar}" style="width:28px; height:28px; border-radius:50%; object-fit:cover; margin-right:8px; border:1px solid var(--border-color);">
            <span style="font-weight:600; font-size:13px; color:var(--text-main);">{usuario_nombre}</span>
            <span style="color:var(--text-muted); font-size:11px; margin-left:6px;">{tiempo}</span>
        </div>
        <img src="data:image/jpeg;base64,{b64_foto}" style="width:100%; border-radius:12px; object-fit:contain; background:#000; border:1px solid var(--border-color);">
    """, unsafe_allow_html=True)

@st.dialog("Nuevo Snippet")
def ventana_historia(usuario):
    foto_hist = st.file_uploader("Subir foto vertical", type=["jpg", "png", "jpeg"], key="dlg_hist_up")
    if st.button("Subir Historia", use_container_width=True, type="primary", key="dlg_hist_btn"):
        if foto_hist:
            b64 = base64.b64encode(foto_hist.read()).decode('utf-8')
            st.session_state["proyectos"]["_CONFIG_"]["social_stories"].append({"usuario": usuario, "foto": b64, "timestamp": obtener_hora_actual()})
            guardar_y_recargar()

@st.dialog("Perfil de Creador")
def ver_perfil(em_usuario):
    u_info = st.session_state["proyectos"]["_CONFIG_"]["usuarios"][em_usuario]
    f_usr = f"data:image/jpeg;base64,{u_info['foto']}" if u_info.get("foto") else "https://via.placeholder.com/150"
    
    colA, colB = st.columns([1, 2.5])
    with colA: st.markdown(f"<img src='{f_usr}' style='width:90px; height:90px; border-radius:50%; object-fit:cover; border:1px solid var(--border-color);'>", unsafe_allow_html=True)
    with colB:
        verificado = "<span class='badge-verified'>✔</span>" if u_info['nivel'] in ["jefe", "jefe_supremo"] else ""
        st.markdown(f"<h3 style='margin:0; font-size:20px;'>{u_info['nombre']} {verificado}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:var(--text-muted); font-size:13px; margin:0;'>@{u_info['alias']} • {u_info['rol']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:13px; color:var(--text-main); margin-top:8px;'>{u_info.get('specs', '')}</p>", unsafe_allow_html=True)
    
    st.divider()
    if u_info.get("spotify_track_id"):
        st.markdown("<p style='font-size:10px; font-weight:700; color:var(--text-muted); letter-spacing:1px; margin-bottom:8px;'>SOUNDTRACK ANCLADO</p>", unsafe_allow_html=True)
        components.iframe(f"https://open.spotify.com/embed/track/{u_info['spotify_track_id']}?utm_source=generator&theme=0", height=80)
        
    st.markdown("<br><span class='section-title'>Timeline</span>", unsafe_allow_html=True)
    posts_user = [p for p in st.session_state["proyectos"]["_CONFIG_"]["social_posts"] if p["usuario"] == em_usuario]
    if not posts_user: st.info("Sin publicaciones.")
    for p in posts_user:
        with st.container(border=True):
            st.caption(p['timestamp'].split()[1])
            if p.get("texto"): st.markdown(f"<p class='post-body'>{format_text(p['texto'])}</p>", unsafe_allow_html=True)
            if p.get("imagen"): st.markdown(f"<img src='data:image/jpeg;base64,{p['imagen']}' class='post-img'>", unsafe_allow_html=True)

# Resto de modales (Funciones)
@st.dialog("Nueva Tarea")
def ventana_kanban(proyecto, autor):
    t = st.text_input("Tarea", key="dlg_kb_t")
    e = st.selectbox("Estado", ["Pendiente", "En Proceso", "Completado"], key="dlg_kb_s")
    if st.button("Guardar", key="dlg_kb_b"):
        if t: st.session_state["proyectos"][proyecto]["kanban"].append({"tarea": t, "estado": e, "autor": autor}); guardar_y_recargar()

@st.dialog("Reportar Problema")
def ventana_soporte(usuario):
    a = st.text_input("Asunto", key="dlg_sop_a")
    d = st.text_area("Descripción", key="dlg_sop_d")
    if st.button("Enviar Ticket", key="dlg_sop_b"):
        if a and d: st.session_state["proyectos"]["_CONFIG_"]["tickets_soporte"].append({"usuario": usuario, "fecha": obtener_hora_actual(), "asunto": a, "desc": d, "estado": "Pendiente"}); guardar_y_recargar()


# --- 6. ACCESO (LOGIN) ---
if st.session_state.get("usuario_logueado") is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown(f"<div style='text-align: center;'><img src='{LOGO_URL}' class='logo-img' style='max-width:200px; margin: 0 auto 20px auto;'></div>", unsafe_allow_html=True)
        tab_log, tab_reg = st.tabs(["Acceder", "Crear Cuenta"])
        db = st.session_state["proyectos"]["_CONFIG_"]["usuarios"]
        with tab_log:
            with st.container(border=True):
                e_in = st.text_input("Usuario", placeholder="correo@productora.com", key="l_u").lower().strip()
                p_in = st.text_input("Clave", type="password", key="l_p")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Ingresar", use_container_width=True, key="l_btn", type="primary"):
                    if e_in in db and db[e_in]["pass"] == p_in:
                        if db[e_in]["estado"] == "Aprobado":
                            st.session_state["usuario_logueado"] = e_in
                            st.rerun()
                        else: st.warning("Pendiente de aprobación.")
                    else: st.error("Datos incorrectos.")
        with tab_reg:
            with st.container(border=True):
                n_reg = st.text_input("Nombre", key="r_n")
                e_reg = st.text_input("Correo", key="r_c").lower().strip()
                p_reg = st.text_input("Clave", type="password", key="r_p")
                f_reg = st.file_uploader("Foto ID", type=["jpg", "png", "jpeg"], key="r_f")
                if st.button("Registrar", use_container_width=True, key="r_btn", type="primary"):
                    if n_reg and e_reg and p_reg and f_reg:
                        db[e_reg] = {"nombre": n_reg, "pass": p_reg, "rol": "Invitado", "nivel": "lectura", "estado": "Pendiente", "foto": base64.b64encode(f_reg.read()).decode('utf-8'), "credencial": f"FTN-{random.randint(1000,9999)}", "edad": "", "roles_fav": "", "portfolio": "", "spotify_token": None, "spotify_track_id": None, "amigos": [], "acceso_rapido": "Panel General", "alias": e_reg.split("@")[0], "specs": "", "estado_txt": "Online", "guardados": []}
                        guardar_y_recargar()
                        st.success("Enviado al administrador.")

# --- 7. PLATAFORMA ---
else:
    us_act = st.session_state["usuario_logueado"]
    db_users = st.session_state["proyectos"]["_CONFIG_"]["usuarios"]
    mis_datos = db_users[us_act]
    rol_actual = mis_datos["rol"]
    nivel_actual = mis_datos["nivel"]
    
    # NAVBAR ALINEADA PERFECTA Y ESTÉTICA (Botones transparentes)
    c_nav1, c_nav2, c_nav3, c_nav4, c_nav_space, c_nav_th, c_nav_img, c_nav_btn = st.columns([1.5, 1.2, 1.2, 1.2, 3, 0.5, 0.5, 1.2], vertical_alignment="center")
    
    with c_nav1: st.markdown(f"<img src='{LOGO_URL}' class='logo-img' style='height:38px;'>", unsafe_allow_html=True)
    with c_nav2: 
        st.markdown("<div class='nav-btn-top'>", unsafe_allow_html=True)
        if st.button("Dashboard", use_container_width=True, key="nv_d"): st.session_state["ruta"] = "Inicio"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with c_nav3:
        st.markdown("<div class='nav-btn-top'>", unsafe_allow_html=True)
        if st.button("Social", use_container_width=True, key="nv_s"): st.session_state["ruta"] = "Social"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with c_nav4:
        st.markdown("<div class='nav-btn-top'>", unsafe_allow_html=True)
        if st.button("Mensajes", use_container_width=True, key="nv_m"): st.session_state["ruta"] = "Mensajes"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with c_nav_space: pass
    with c_nav_th:
        st.markdown("<div class='nav-btn-top'>", unsafe_allow_html=True)
        if st.button("🌓", key="btn_th"):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with c_nav_img:
        # Foto nativa, se centra automático con la columna
        f_src = f"data:image/jpeg;base64,{mis_datos['foto']}" if mis_datos.get("foto") else "https://via.placeholder.com/150"
        st.markdown(f"<img src='{f_src}' style='width:36px; height:36px; border-radius:50%; object-fit:cover; border:1px solid var(--border-color);'>", unsafe_allow_html=True)
    with c_nav_btn:
        st.markdown("<div class='nav-btn-top'>", unsafe_allow_html=True)
        if st.button("Perfil", use_container_width=True, key="nv_p"): st.session_state["ruta"] = "Perfil"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
            
    st.markdown("<hr style='border-color: var(--border-color); margin-top: 5px; margin-bottom: 24px;'>", unsafe_allow_html=True)

    # --- RUTA: INICIO (DASHBOARD AESTHETIC) ---
    if st.session_state["ruta"] == "Inicio":
        st.markdown(f"<h2>Welcome back, <span class='gradient-text'>{mis_datos['nombre']}</span>.</h2>", unsafe_allow_html=True)
        
        # Métricas Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Proyectos Activos", len([p for p in st.session_state['proyectos'].keys() if p != '_CONFIG_']))
        total_crew = sum(len(pd_proy.get("crew", [])) for p, pd_proy in st.session_state['proyectos'].items() if p != '_CONFIG_')
        m2.metric("Nómina Total", total_crew)
        total_tareas = sum(len(pd_proy.get("kanban", [])) for p, pd_proy in st.session_state['proyectos'].items() if p != '_CONFIG_')
        m3.metric("Tareas Activas", total_tareas)
        m4.metric("Nivel de Acceso", mis_datos['nivel'].capitalize())
        st.markdown("<br>", unsafe_allow_html=True)

        c_izq, c_der = st.columns([2.5, 1.2], gap="large")
        
        with c_izq:
            st.markdown("<span class='section-title'>Mis Workspaces</span>", unsafe_allow_html=True)
            l_proy = [p for p in st.session_state["proyectos"].keys() if p != "_CONFIG_"]
            if not l_proy: st.info("No hay desarrollos activos.")
            
            # Grilla de Proyectos
            cols_grid = st.columns(2)
            for idx, proy in enumerate(l_proy):
                with cols_grid[idx % 2]:
                    with st.container(border=True):
                        st.markdown(f"<h3 style='margin:0; font-size:18px;'>{proy}</h3>", unsafe_allow_html=True)
                        st.caption(f"Última act: Hace 2h")
                        
                        pd_proy = st.session_state['proyectos'][proy]
                        k_tot = len(pd_proy.get("kanban", []))
                        k_don = len([t for t in pd_proy.get("kanban", []) if t["estado"] == "Completado"])
                        prog = (k_don / k_tot) * 100 if k_tot > 0 else 0
                        st.progress(int(prog))
                        
                        if st.button("Abrir Workspace", key=f"d_e_{proy}", use_container_width=True, type="primary"):
                            st.session_state["proyecto_activo"] = proy
                            st.session_state["menu_option"] = "Panel General"
                            st.session_state["ruta"] = "Proyecto"
                            st.rerun()
            
            st.markdown("<br><span class='section-title'>Análisis de Producción</span>", unsafe_allow_html=True)
            # Gráfico de tareas global si hay data
            df_data = []
            for p, pd_proy in st.session_state['proyectos'].items():
                if p != '_CONFIG_':
                    for t in pd_proy.get("kanban", []):
                        df_data.append({"Proyecto": p, "Estado": t["estado"]})
            if df_data:
                df = pd.DataFrame(df_data)
                fig = px.pie(df, names='Estado', hole=0.7, color_discrete_sequence=['#FBAF3B', '#3B82F6', '#22C55E'])
                fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else: st.info("No hay tareas para graficar.")

        with c_der:
            st.markdown("<span class='section-title'>App Drawer (Centro de Control)</span>", unsafe_allow_html=True)
            if nivel_actual in ["jefe", "jefe_supremo"]:
                with st.popover("➕ Crear Producción", use_container_width=True):
                    np_n = st.text_input("Nombre", key="d_np")
                    if st.button("Inicializar DB", key="d_bnp", type="primary"):
                        if np_n: st.session_state["proyectos"][np_n] = {"contexto_aprobado": "Proyecto base.", "archivos_pendientes": [], "avisos": [], "equipos": [], "pedidos_equipos": [], "continuidad": [], "arte": [], "planos": [], "plan_rodaje": [], "plantas_luces": [], "sonido_log": [], "tomas_dir": [], "personajes": [], "locaciones": [], "crew": [], "catering": [], "links": [], "presupuesto": [], "casting": [], "desglose": [], "comparador_rentals": [], "carrito_rentals": [], "directorio_rentals": [], "kanban": []}; guardar_y_recargar()
            
            st.markdown("<br>", unsafe_allow_html=True)
            # Botonera de acceso rápido (Grid 2x2)
            c_dr1, c_dr2 = st.columns(2)
            if c_dr1.button("Kanban", use_container_width=True, key="dr_1"): st.session_state["menu_option"] = "Tablero Kanban"; st.session_state["ruta"] = "Proyecto" if st.session_state.get("proyecto_activo") else "Inicio"; st.rerun()
            if c_dr2.button("Presupuesto", use_container_width=True, key="dr_2"): st.session_state["menu_option"] = "Presupuesto"; st.session_state["ruta"] = "Proyecto" if st.session_state.get("proyecto_activo") else "Inicio"; st.rerun()
            if c_dr1.button("Rentals IA", use_container_width=True, key="dr_3"): st.session_state["menu_option"] = "Rentals IA"; st.session_state["ruta"] = "Proyecto" if st.session_state.get("proyecto_activo") else "Inicio"; st.rerun()
            if c_dr2.button("Guiones", use_container_width=True, key="dr_4"): st.session_state["menu_option"] = "Laboratorio Guion"; st.session_state["ruta"] = "Proyecto" if st.session_state.get("proyecto_activo") else "Inicio"; st.rerun()
            
            if not st.session_state.get("proyecto_activo"): st.caption("Abrí un proyecto primero para usar las herramientas.")

            st.markdown("<br><span class='section-title'>Agenda / Call Sheets</span>", unsafe_allow_html=True)
            if st.button("Nuevo Recordatorio", type="secondary", use_container_width=True, key="d_rec"): ventana_recordatorio((nivel_actual in ["jefe_supremo", "jefe"]), mis_datos['nombre'])
            for rec in reversed(st.session_state["proyectos"]["_CONFIG_"]["recordatorios"]):
                if rec["tipo"] == "Global (Toda la Productora)" or rec["autor"] == mis_datos["nombre"]:
                    with st.container(border=True):
                        st.markdown(f"<span style='color:var(--accent); font-size:11px; font-weight:700;'>{rec['fecha']}</span>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-weight:600; font-size:14px;'>{rec['titulo']}</div>", unsafe_allow_html=True)

    # --- RUTA: SOCIAL (LÓGICA TWITTER/IG EXTREMA) ---
    elif st.session_state["ruta"] == "Social":
        col_izq, col_centro, col_der = st.columns([1, 2.5, 1.2], gap="large")
        
        with col_izq:
            with st.container(border=True):
                f_usr = f"data:image/jpeg;base64,{mis_datos['foto']}" if mis_datos.get("foto") else "https://via.placeholder.com/150"
                verif = "<span class='badge-verified'>✔</span>" if nivel_actual in ["jefe", "jefe_supremo"] else ""
                st.markdown(f"<img src='{f_usr}' class='avatar-circle' style='width:80px; height:80px; margin-bottom:12px;'>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='margin:0; font-size:18px;'>{mis_datos['nombre']} {verif}</h3>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:var(--text-muted); font-size:13px; margin:0;'>@{mis_datos.get('alias', us_act.split('@')[0])}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:var(--text-main); font-size:12px; margin-top:8px;'><span class='online-indicator'></span>{mis_datos.get('estado_txt', 'Online')}</p>", unsafe_allow_html=True)
                st.divider()
                seguidores = sum(1 for info in db_users.values() if us_act in info.get("amigos", []))
                st.markdown(f"**{seguidores}** <span style='color:var(--text-muted); font-size:13px;'>Seguidores</span>", unsafe_allow_html=True)
                st.markdown(f"**{len(mis_datos.get('amigos', []))}** <span style='color:var(--text-muted); font-size:13px;'>Siguiendo</span>", unsafe_allow_html=True)
                
        with col_centro:
            # Snippets Estéticos (IG Web Mode)
            st.markdown("<span class='section-title'>Snippets</span>", unsafe_allow_html=True)
            ahora = datetime.now(TZ_AR)
            h_activas = [h for h in st.session_state["proyectos"]["_CONFIG_"]["social_stories"] if (ahora - datetime.strptime(h["timestamp"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=TZ_AR)).total_seconds() < 86400]
            
            c_hist = st.columns(6)
            with c_hist[0]:
                st.markdown(f"<div style='min-width: 90px; height: 120px; border-radius: 12px; border: 1px dashed var(--border-color); display:flex; flex-direction:column; align-items:center; justify-content:center; background:var(--bg-card);'><span style='font-size:24px; color:var(--text-muted);'>+</span></div>", unsafe_allow_html=True)
                if st.button("New", help="Subir", type="secondary", key="s_n_btn"): ventana_historia(us_act)
            
            for idx, h in enumerate(reversed(h_activas)):
                if idx + 1 < 6:
                    with c_hist[idx + 1]:
                        ui_h = db_users[h['usuario']]
                        f_h = f"data:image/jpeg;base64,{ui_h['foto']}" if ui_h.get("foto") else "https://via.placeholder.com/150"
                        n_c = ui_h['nombre'].split()[0]
                        st.markdown(f"""
                        <div class='snippet-card' style='background-image: url("data:image/jpeg;base64,{h['foto']}");'>
                            <div class='snippet-overlay'>
                                <img src='{f_h}' class='snippet-avatar'>
                                <span class='snippet-name'>{n_c}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("Ver", key=f"s_v_{idx}", type="secondary"): ver_historia_dialog(h['foto'], ui_h['nombre'], f_h, h['timestamp'].split()[1])
            st.divider()
            
            # Post Creator
            st.markdown("<span class='section-title'>Update Status</span>", unsafe_allow_html=True)
            with st.container(border=True):
                txt_post = st.text_area("Whats on your mind?", label_visibility="collapsed", placeholder="What's happening on set?", key="s_ta")
                img_post = st.file_uploader("Attach media", type=["jpg", "png", "jpeg"], label_visibility="collapsed", key="s_fu")
                c_sub1, c_sub2 = st.columns([3,1])
                with c_sub2:
                    if st.button("Post", type="primary", key="s_bp"):
                        if txt_post or img_post:
                            img_b64 = base64.b64encode(img_post.read()).decode('utf-8') if img_post else None
                            st.session_state["proyectos"]["_CONFIG_"]["social_posts"].insert(0, {
                                "id": str(random.randint(100000, 999999)), "usuario": us_act, "texto": txt_post, "imagen": img_b64, 
                                "timestamp": obtener_hora_actual(), "liked_by": [], "comentarios": [], "reposted_by": [], "es_repost": False
                            })
                            guardar_y_recargar()

            # Feed
            posts = st.session_state["proyectos"]["_CONFIG_"]["social_posts"]
            for i, p in enumerate(posts):
                ui = db_users[p["usuario"]]
                fi = f"data:image/jpeg;base64,{ui['foto']}" if ui.get("foto") else "https://via.placeholder.com/150"
                alias_u = ui.get("alias", p['usuario'].split('@')[0])
                verif_p = "<span class='badge-verified'>✔</span>" if ui['nivel'] in ["jefe", "jefe_supremo"] else ""
                
                with st.container(border=True):
                    if p.get("es_repost"):
                        st.markdown(f"<span class='repost-badge'>{SVG_REPOST} Reposted</span>", unsafe_allow_html=True)
                    
                    st.markdown(f"""
                        <div class='post-header'>
                            <div style='display:flex; align-items:center;'>
                                <img src='{fi}' class='post-avatar'>
                                <div>
                                    <p class='post-name'>{ui['nombre']} {verif_p}</p>
                                    <p class='post-handle'>@{alias_u} • {p['timestamp'].split()[1]}</p>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if p.get("texto"): st.markdown(f"<div class='post-body'>{format_text(p['texto'])}</div>", unsafe_allow_html=True)
                    if p.get("imagen"): st.markdown(f"<img src='data:image/jpeg;base64,{p['imagen']}' class='post-img'>", unsafe_allow_html=True)
                    
                    # Interacciones Reales SVG
                    st.markdown("<div class='social-action-group'>", unsafe_allow_html=True)
                    c_lik, c_com, c_rep, c_sav = st.columns(4)
                    
                    is_liked = us_act in p.get("liked_by", [])
                    ico_like = SVG_LIKE_FILLED if is_liked else SVG_LIKE
                    if c_lik.button(f"{ico_like} {len(p.get('liked_by', []))}", key=f"sl_{p['id']}_{i}", type="secondary"):
                        if is_liked: p["liked_by"].remove(us_act)
                        else: p["liked_by"].append(us_act)
                        guardar_y_recargar()
                        
                    if c_com.button(f"{SVG_COMMENT} {len(p.get('comentarios', []))}", key=f"sc_{p['id']}_{i}", type="secondary"):
                        dialog_comentar(p['id'], us_act)
                        
                    is_reposted = us_act in p.get("reposted_by", [])
                    ico_rep = SVG_REPOST_FILLED if is_reposted else SVG_REPOST
                    if c_rep.button(f"{ico_rep} {len(p.get('reposted_by', []))}", key=f"sr_{p['id']}_{i}", type="secondary"):
                        if not is_reposted:
                            p["reposted_by"].append(us_act)
                            st.session_state["proyectos"]["_CONFIG_"]["social_posts"].insert(0, {
                                "id": str(random.randint(100000, 999999)), "usuario": p['usuario'], "texto": p.get('texto'), "imagen": p.get('imagen'), 
                                "timestamp": obtener_hora_actual(), "liked_by": [], "comentarios": [], "reposted_by": [], "es_repost": True
                            })
                            guardar_y_recargar()
                        else: # Undo repost
                            p["reposted_by"].remove(us_act)
                            # Hard to delete the exact repost item without a distinct ID trace, but we remove the badge count.
                            guardar_y_recargar()
                            
                    is_saved = p['id'] in mis_datos.get("guardados", [])
                    ico_sav = SVG_SAVE_FILLED if is_saved else SVG_SAVE
                    if c_sav.button(f"{ico_sav}", key=f"ss_{p['id']}_{i}", type="secondary"):
                        if not is_saved: st.session_state["proyectos"]["_CONFIG_"]["usuarios"][us_act]["guardados"].append(p['id'])
                        else: st.session_state["proyectos"]["_CONFIG_"]["usuarios"][us_act]["guardados"].remove(p['id'])
                        guardar_y_recargar()
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    for com in p.get("comentarios", []):
                        nm_c = db_users[com['usuario']]['nombre']
                        st.markdown(f"<div class='comment-box'><strong style='color:var(--text-main);'>{nm_c}</strong> <span style='font-size:11px;color:var(--text-muted);'>• {com['timestamp'].split()[1]}</span><br><span style='color:var(--text-main); font-size:13px;'>{com['texto']}</span></div>", unsafe_allow_html=True)

        with col_der:
            st.markdown("<span class='section-title'>Trending Tags</span>", unsafe_allow_html=True)
            textos_feed = " ".join([p.get('texto', '') for p in posts if p.get('texto')])
            hashtags = re.findall(r"#(\w+)", textos_feed)
            if hashtags:
                top_tags = pd.Series(hashtags).value_counts().head(5)
                with st.container(border=True):
                    for tag, count in top_tags.items():
                        st.markdown(f"**#{tag}** <span style='font-size:11px;color:var(--text-muted); float:right;'>{count} posts</span>", unsafe_allow_html=True)
            else: st.info("No active trends.")

            st.markdown("<br><span class='section-title'>Network</span>", unsafe_allow_html=True)
            for em, info in db_users.items():
                if em != us_act and em not in mis_datos.get("amigos", []):
                    with st.container(border=True):
                        st.markdown(f"<p style='margin:0; font-weight:600; color:var(--text-main);'>{info['nombre']}</p><p style='margin:0; font-size:11px; color:var(--text-muted);'>@{info['alias']}</p>", unsafe_allow_html=True)
                        c_vp, c_sg = st.columns(2)
                        if c_vp.button("Profile", key=f"sp_{em}", type="secondary"): ver_perfil(em)
                        if c_sg.button("Follow", key=f"ss_{em}", type="secondary"): st.session_state["proyectos"]["_CONFIG_"]["usuarios"][us_act]["amigos"].append(em); guardar_y_recargar()
            
            st.markdown("<br><span class='section-title'>Live Activity (Spotify)</span>", unsafe_allow_html=True)
            amigos_seguir = mis_datos.get("amigos", []) + [us_act]
            for em in amigos_seguir:
                if em in db_users:
                    info = db_users[em]
                    if SPOTIPY_INSTALLED and info.get("spotify_token"):
                        try:
                            sp = spotipy.Spotify(auth=info["spotify_token"]["access_token"])
                            current = sp.current_user_playing_track()
                            if current and current.get("is_playing"):
                                tid = current["item"]["id"]
                                with st.container(border=True):
                                    st.markdown(f"<p style='margin:0; font-size:12px; font-weight:700;'><span class='online-indicator'></span>{info['nombre']}</p>", unsafe_allow_html=True)
                                    components.iframe(f"https://open.spotify.com/embed/track/{tid}?utm_source=generator&theme=0", height=80)
                                continue
                        except: pass

    # --- RUTA: MENSAJES ---
    elif st.session_state["ruta"] == "Mensajes":
        st.markdown("<h2 class='gradient-text'>Direct Messages</h2>", unsafe_allow_html=True)
        col_list, col_chat = st.columns([1, 2.5], gap="large")
        if "chat_con" not in st.session_state: st.session_state["chat_con"] = None
        
        with col_list:
            st.markdown("<span class='section-title'>Inbox</span>", unsafe_allow_html=True)
            for em, info in db_users.items():
                if em != us_act:
                    with st.container(border=True):
                        st.markdown(f"**{info['nombre']}**<br><span style='font-size:11px;color:var(--text-muted);'>@{info['alias']}</span>", unsafe_allow_html=True)
                        if st.button("Chat", key=f"m_c_{em}", type="secondary"): st.session_state["chat_con"] = em; st.rerun()

        with col_chat:
            if st.session_state["chat_con"]:
                d_inf = db_users[st.session_state["chat_con"]]
                st.markdown(f"### Chatting with {d_inf['nombre']}")
                st.divider()
                historial = [m for m in st.session_state["proyectos"]["_CONFIG_"]["mensajes"] if (m["de"] == us_act and m["para"] == st.session_state["chat_con"]) or (m["de"] == st.session_state["chat_con"] and m["para"] == us_act)]
                
                with st.container(height=400):
                    if not historial: st.info("Say hi.")
                    for msg in historial:
                        if msg["de"] == us_act:
                            st.markdown(f"<div style='text-align: right;'><span style='background:var(--accent); color:#000; padding:10px 14px; border-radius:14px; display:inline-block; margin-bottom:4px; font-weight:600;'>{msg['texto']}</span><br><span style='font-size:10px; color:var(--text-muted);'>{msg['fecha'].split()[1]}</span></div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div style='text-align: left;'><span style='background:var(--bg-hover); border:1px solid var(--border-color); padding:10px 14px; border-radius:14px; display:inline-block; margin-bottom:4px;'>{msg['texto']}</span><br><span style='font-size:10px; color:var(--text-muted);'>{msg['fecha'].split()[1]}</span></div>", unsafe_allow_html=True)
                
                nm = st.chat_input("Message...", key="m_in")
                if nm:
                    st.session_state["proyectos"]["_CONFIG_"]["mensajes"].append({"de": us_act, "para": st.session_state["chat_con"], "texto": nm, "fecha": obtener_hora_actual()})
                    guardar_y_recargar()
            else: st.info("Select a contact.")

    # --- RUTA: PERFIL Y ADMIN ---
    elif st.session_state["ruta"] == "Perfil":
        st.markdown("<span class='section-title'>ACCOUNT SETTINGS</span>", unsafe_allow_html=True)
        t_per, t_g, t_cred, t_dir, t_adm = st.tabs(["Profile", "Saved", "ID Card", "Directory", "Admin"])
        
        with t_per:
            c_img, c_form = st.columns([1, 2.5])
            with c_img:
                st.markdown("#### Avatar")
                f_s = f"data:image/jpeg;base64,{mis_datos['foto']}" if mis_datos.get("foto") else "https://via.placeholder.com/150"
                st.markdown(f"<img src='{f_s}' class='avatar-circle' style='width:120px;height:120px;'>", unsafe_allow_html=True)
                nf = st.file_uploader("Update", type=["jpg", "png", "jpeg"], label_visibility="collapsed", key="p_up")
                if nf and st.button("Save Image", key="p_sb"): db_users[us_act]["foto"] = base64.b64encode(nf.read()).decode('utf-8'); guardar_y_recargar()
                st.markdown("---")
                st.metric("Access Level", mis_datos['nivel'].capitalize())

            with c_form:
                with st.form("p_f"):
                    st.markdown("#### Personal Data")
                    c1, c2 = st.columns(2)
                    al = c1.text_input("Username (@)", value=mis_datos.get("alias", us_act.split("@")[0]))
                    es = c2.text_input("Status", value=mis_datos.get("estado_txt", "Online"))
                    rf = st.text_input("Role Specialization", value=mis_datos.get("roles_fav", ""))
                    spc = st.text_area("Bio / Notes", value=mis_datos.get("specs", ""))
                    
                    st.markdown("#### Soundtrack")
                    sp_p = st.text_input("Pinned Track (Profile view)", value=mis_datos.get("spotify_track_id", ""), placeholder="https://open.spotify.com/track/...")
                    
                    if SPOTIPY_INSTALLED:
                        try:
                            sp_oauth = SpotifyOAuth(client_id=st.secrets["SPOTIFY_CLIENT_ID"], client_secret=st.secrets["SPOTIFY_CLIENT_SECRET"], redirect_uri=st.secrets["SPOTIFY_REDIRECT_URI"], scope="user-read-currently-playing")
                            auth_url = sp_oauth.get_authorize_url()
                            st.markdown(f"[🔗 **Link Spotify Account (Live Status)**]({auth_url})")
                        except: st.info("Requires Spotify keys in st.secrets.")

                    if st.form_submit_button("Sync Profile"):
                        t_id = sp_p.split("track/")[1].split("?")[0] if "track/" in sp_p else sp_p
                        db_users[us_act].update({"alias": al, "estado_txt": es, "roles_fav": rf, "specs": spc, "spotify_track_id": t_id})
                        guardar_y_recargar()
                        st.success("Synced.")
            st.divider()
            if st.button("Log Out", type="secondary", key="p_lo"): st.session_state["usuario_logueado"] = None; st.session_state["ruta"] = "Inicio"; st.rerun()

        with t_g:
            st.markdown("### Saved Posts 🔖")
            mis_g = mis_datos.get("guardados", [])
            if not mis_g: st.info("Nothing saved yet.")
            for pid in mis_g:
                post = next((p for p in st.session_state["proyectos"]["_CONFIG_"]["social_posts"] if p["id"] == pid), None)
                if post:
                    with st.container(border=True):
                        st.write(f"**@{db_users[post['usuario']]['alias']}** - {post['timestamp']}")
                        if post.get("texto"): st.write(post["texto"])
                        if post.get("imagen"): st.markdown(f"<img src='data:image/jpeg;base64,{post['imagen']}' style='height:150px;border-radius:8px;'>", unsafe_allow_html=True)
                        if st.button("Remove", key=f"p_rem_{pid}", type="secondary"):
                            st.session_state["proyectos"]["_CONFIG_"]["usuarios"][us_act]["guardados"].remove(pid)
                            guardar_y_recargar()

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
            bq = st.text_input("Search members...", key="p_bq")
            for em, info in db_users.items():
                if info["estado"] == "Aprobado" and (bq.lower() in info["nombre"].lower() or bq.lower() in info["rol"].lower()):
                    with st.container(border=True):
                        colD1, colD2 = st.columns([1, 8])
                        with colD1: st.markdown(f"<img src='data:image/jpeg;base64,{info.get('foto','')}' class='avatar-circle' style='width:45px;height:45px;'>", unsafe_allow_html=True)
                        with colD2: st.markdown(f"<h4 style='margin:0;'>{info['nombre']} <span style='color:var(--accent);font-size:12px;'>({info['rol']})</span></h4>", unsafe_allow_html=True)

        with t_adm:
            if rol_actual == "Super Admin":
                mapa = {"Super Admin": "jefe_supremo", "Producción": "jefe", "Dirección": "jefe", "Dirección de Fotografía": "jefe", "Dirección de Arte": "jefe", "Director de Sonido": "jefe", "Asistente de Sonido": "asistente", "Guion": "jefe", "Continuidad": "jefe", "Invitado": "lectura"}
                for em_usr, dt_usr in db_users.items():
                    with st.container(border=True):
                        c1, c2, c3, c4 = st.columns([2, 1.5, 1.5, 1])
                        c1.markdown(f"**{dt_usr['nombre']}**<br><span style='font-size:12px;'>{em_usr}</span>", unsafe_allow_html=True)
                        est = c2.selectbox("Status", ["Aprobado", "Pendiente"], index=0 if dt_usr.get("estado") == "Aprobado" else 1, key=f"p_e_{em_usr}")
                        rol = c3.selectbox("Role", list(mapa.keys()), index=list(mapa.keys()).index(dt_usr["rol"]) if dt_usr["rol"] in mapa else 9, key=f"p_r_{em_usr}")
                        if c4.button("Apply", key=f"p_b_{em_usr}"): db_users[em_usr].update({"estado": est, "rol": rol, "nivel": mapa[rol]}); guardar_y_recargar()
                st.divider()
                st.markdown("### Support Tickets")
                tks = st.session_state["proyectos"]["_CONFIG_"]["tickets_soporte"]
                for i, tk in enumerate(reversed(tks)):
                    with st.container(border=True):
                        st.markdown(f"**{tk['asunto']}** ({tk['fecha']}) - From: {tk['usuario']}")
                        st.write(tk['desc'])
                        if tk['estado'] == "Pendiente":
                            if st.button("Resolve", key=f"p_tk_{i}"): st.session_state["proyectos"]["_CONFIG_"]["tickets_soporte"][len(tks)-1-i]["estado"] = "Resuelto"; guardar_y_recargar()
                        else: st.success("Resolved")
            else: st.warning("Super Admins only.")

    # --- RUTA: PROYECTO (HERRAMIENTAS INTACTAS) ---
    elif st.session_state["ruta"] == "Proyecto":
        pr = st.session_state["proyecto_activo"]
        pd_proy = st.session_state["proyectos"][pr]
        
        st.markdown(f"<h2 class='gradient-text' style='margin-bottom: 24px;'>{pr.upper()}</h2>", unsafe_allow_html=True)
        col_nav, col_content = st.columns([1, 3.5], gap="large")
        
        o_nav = ["Panel General", "Tablero Kanban", "Asistente IA"]
        i_nav = ["grid", "kanban", "lightning-charge"]
        if nivel_actual != "lectura": o_nav.append("Solicitar a Prod."); i_nav.append("send")
        o_nav.extend(["Bandeja Prod.", "Rentals IA", "Archivos", "Tablón", "Enlaces", "Presupuesto", "Scouting", "Base Crew", "Casting", "Catering", "Desglose", "Laboratorio Guion", "Inventario", "Plan Rodaje", "Monitor DIR", "Luces (Canvas)", "Ref. IA", "Arte & Vestuario", "Log Sonido", "Raccord"])
        i_nav.extend(["inbox", "shop", "folder2-open", "megaphone", "link-45deg", "wallet2", "geo-alt", "people", "person-video", "cup-hot", "card-text", "pen", "box", "calendar-event", "camera-reels", "lightbulb", "cpu", "palette", "headphones", "film"])
        
        nf, inf = [], []
        for o, i in zip(o_nav, i_nav):
            if rol_actual == "Super Admin": nf.append(o); inf.append(i)
            elif rol_actual == "Producción" and o in ["Panel General", "Tablero Kanban", "Asistente IA", "Solicitar a Prod.", "Presupuesto", "Bandeja Prod.", "Scouting", "Base Crew", "Casting", "Catering", "Rentals IA", "Archivos", "Tablón", "Enlaces"]: nf.append(o); inf.append(i)
            elif rol_actual == "Guion" and o in ["Panel General", "Tablero Kanban", "Asistente IA", "Solicitar a Prod.", "Desglose", "Laboratorio Guion", "Archivos", "Tablón", "Enlaces"]: nf.append(o); inf.append(i)
            elif "Dirección" in rol_actual and rol_actual not in ["Dirección de Arte", "Dirección de Fotografía"] and o in ["Panel General", "Tablero Kanban", "Asistente IA", "Solicitar a Prod.", "Casting", "Plan Rodaje", "Monitor DIR", "Archivos", "Tablón", "Enlaces", "Inventario"]: nf.append(o); inf.append(i)
            elif rol_actual == "Dirección de Fotografía" and o in ["Panel General", "Tablero Kanban", "Asistente IA", "Solicitar a Prod.", "Luces (Canvas)", "Ref. IA", "Inventario", "Archivos", "Tablón", "Enlaces"]: nf.append(o); inf.append(i)
            elif rol_actual == "Dirección de Arte" and o in ["Panel General", "Tablero Kanban", "Asistente IA", "Solicitar a Prod.", "Arte & Vestuario", "Inventario", "Archivos", "Tablón", "Enlaces"]: nf.append(o); inf.append(i)
            elif "Sonido" in rol_actual and o in ["Panel General", "Tablero Kanban", "Asistente IA", "Solicitar a Prod.", "Log Sonido", "Inventario", "Archivos", "Tablón", "Enlaces"]: nf.append(o); inf.append(i)
            elif rol_actual == "Continuidad" and o in ["Panel General", "Tablero Kanban", "Asistente IA", "Solicitar a Prod.", "Raccord", "Archivos", "Tablón", "Enlaces"]: nf.append(o); inf.append(i)
            elif nivel_actual == "lectura" and o in ["Panel General", "Tablero Kanban", "Asistente IA", "Archivos", "Tablón", "Enlaces"]: nf.append(o); inf.append(i)

        if not nf: nf = ["Panel General"]; inf = ["grid"]
        idx_def = nf.index(st.session_state["menu_option"]) if st.session_state.get("menu_option") in nf else 0
            
        with col_nav:
            s_e = option_menu(menu_title="WORKSPACE", options=nf, icons=inf, default_index=idx_def, styles={"container": {"padding": "10px", "background-color": "var(--bg-card)", "border-radius": "12px", "border": "1px solid var(--border-color)"}, "icon": {"color": "var(--text-muted)", "font-size": "15px"}, "menu-title": {"color": "var(--text-muted)", "font-size": "11px", "letter-spacing": "2px", "font-weight": "700"}, "nav-link": {"font-size": "13px", "text-align": "left", "margin": "4px 0", "color": "var(--text-main)", "border-radius": "8px", "padding": "10px"}, "nav-link-selected": {"background-color": "var(--bg-hover)", "color": "var(--text-main)", "font-weight": "600", "border-left": "3px solid var(--accent)"}})
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
                if st.button("Emitir Plan Maestro", key="w_csh"):
                    try:
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        prompt = f"Proyecto: {pr}. Datos: Avisos {pd_proy.get('avisos',[])}, Locaciones {pd_proy.get('locaciones',[])}. Redactá un Call Sheet."
                        st.markdown(f"<div style='background:var(--bg-hover); padding:20px; border-radius:12px; border:1px solid var(--border-color);'>{genai.GenerativeModel('gemini-1.5-flash').generate_content(prompt).text}</div>", unsafe_allow_html=True)
                    except: st.error("Falta API Key Gemini.")

            elif s_e == "Tablero Kanban":
                c1, c2 = st.columns([2.5, 1])
                with c1: st.markdown("<h2>Gestor de Tareas</h2>", unsafe_allow_html=True)
                with c2: 
                    if st.button("Crear Tarea", key="w_kb"): ventana_kanban(pr, mis_datos['nombre'])
                st.divider()
                colP, colPr, colL = st.columns(3)
                with colP:
                    st.markdown("#### Pendiente")
                    for i, t in enumerate(pd_proy["kanban"]):
                        if t["estado"] == "Pendiente":
                            with st.container(border=True): 
                                st.write(f"**{t['tarea']}**")
                                if st.button("Mover ➔", key=f"w_k1_{i}", type="secondary"): pd_proy["kanban"][i]["estado"] = "En Proceso"; guardar_y_recargar()
                with colPr:
                    st.markdown("#### En Proceso")
                    for i, t in enumerate(pd_proy["kanban"]):
                        if t["estado"] == "En Proceso":
                            with st.container(border=True): 
                                st.write(f"**{t['tarea']}**")
                                if st.button("Finalizar", key=f"w_k2_{i}", type="secondary"): pd_proy["kanban"][i]["estado"] = "Completado"; guardar_y_recargar()
                with colL:
                    st.markdown("#### Listo")
                    for t in [t for t in pd_proy["kanban"] if t["estado"] == "Completado"]:
                        with st.container(border=True): st.write(f"~~{t['tarea']}~~")

            elif s_e == "Asistente IA":
                st.markdown("<h2>Comando de IA</h2>", unsafe_allow_html=True)
                try:
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    m = st.chat_input("Instrucción...", key="w_ia")
                    if m:
                        st.chat_message("user").write(m)
                        st.chat_message("assistant").write(genai.GenerativeModel('gemini-1.5-flash').generate_content(f"Sos FTN AI. Hablás con: {mis_datos['nombre']}. Usuario: {m}").text)
                except: st.error("Falta API Key.")

            elif s_e == "Solicitar a Prod.":
                if st.button("Levantar Ticket", key="w_sp"): ventana_pedido(pr, rol_actual)
                for ped in [p for p in pd_proy.get("pedidos_equipos", []) if p["area"] == rol_actual or rol_actual == "Super Admin"]:
                    with st.container(border=True): st.write(f"**{ped['item']}** — {ped['notas']} ({ped['estado']})")

            elif s_e == "Bandeja Prod.":
                for i, ped in enumerate(pd_proy["pedidos_equipos"]):
                    if ped['estado'] == "Pendiente":
                        with st.container(border=True):
                            st.write(f"**{ped['area']}:** {ped['item']}")
                            c1, c2 = st.columns(2)
                            if c1.button("Aprobar", key=f"w_ap_{i}"): pd_proy["equipos"].append({"area": ped['area'], "item": ped['item'], "cant": 1, "tipo": "A Confirmar", "rental": "A Definir"}); pd_proy["pedidos_equipos"][i]["estado"] = "Aprobado"; guardar_y_recargar()
                            if c2.button("Denegar", key=f"w_re_{i}", type="secondary"): pd_proy["pedidos_equipos"][i]["estado"] = "Rechazado"; guardar_y_recargar()

            elif s_e == "Rentals IA":
                c1, c2, c3 = st.columns(3)
                c1.button("Proveedor", on_click=lambda: ventana_nuevo_rental(pr), key="w_r_p")
                c2.button("Scanner IA", on_click=lambda: ventana_comparador_rental(pr), key="w_r_s")
                c3.button("Purga", on_click=lambda: ventana_vaciar_comparador(pr), type="secondary", key="w_r_pu")
                st.divider()
                if pd_proy.get("carrito_rentals"):
                    if st.button("Checkout", key="w_r_c"): ventana_checkout(pr)
                    for i, item in enumerate(pd_proy["carrito_rentals"]):
                        with st.container(border=True):
                            st.write(f"{item['nombre']} - ${item['precio']}")
                            if st.button("Quitar", key=f"w_rq_{i}", type="secondary"): pd_proy["carrito_rentals"].pop(i); guardar_y_recargar()
                st.markdown("### Base Analizada")
                for i, r in enumerate(pd_proy.get("comparador_rentals", [])):
                    with st.container(border=True):
                        st.write(f"{r['nombre']} - ${r['precio']}")
                        if st.button("Añadir", key=f"w_ra_{i}", type="secondary"): pd_proy["carrito_rentals"].append(r); guardar_y_recargar()

            elif s_e == "Archivos":
                a = st.file_uploader("Documento (.txt)", key="w_ar_f")
                if a and st.button("Subir", key="w_ar_b"): pd_proy["archivos_pendientes"].append({"autor": mis_datos['nombre'], "nombre": a.name, "texto": a.getvalue().decode('utf-8')}); guardar_y_recargar()

            elif s_e == "Tablón":
                if st.button("Publicar", key="w_ta_b"): ventana_aviso(pr, mis_datos['nombre'], pd_proy["locaciones"])
                for a in reversed(pd_proy["avisos"]): st.write(f"**{a['autor']}**: {a.get('texto', 'Citación')}")

            elif s_e == "Enlaces":
                if st.button("Cargar URL", key="w_en_b"): ventana_link(pr)
                for l in pd_proy["links"]: st.write(f"[{l['titulo']}]({l['url']})")

            elif s_e == "Presupuesto":
                if st.button("Asentar Gasto", key="w_pr_b"): ventana_presupuesto(pr)
                if pd_proy.get("presupuesto"):
                    df = pd.DataFrame(pd_proy["presupuesto"])
                    st.metric("Total", f"${df['costo'].sum():,.2f}")
                    st.plotly_chart(px.pie(df, values='costo', names='area', template="plotly_dark"))

            elif s_e == "Scouting":
                if st.button("Registrar Locación", key="w_sc_b"): ventana_locacion(pr)
                for l in pd_proy.get("locaciones", []): st.write(f"**{l['nombre']}**: {l['direccion']}")

            elif s_e == "Base Crew":
                if st.button("Contratar", key="w_bc_b"): ventana_crew(pr)
                if pd_proy.get("crew"): st.dataframe(pd.DataFrame(pd_proy["crew"]))

            elif s_e == "Casting":
                if st.button("Añadir Actor", key="w_ca_b"): ventana_casting(pr)
                for a in pd_proy["casting"]: st.write(f"**{a['actor']}** ({a['personaje']})")

            elif s_e == "Catering":
                if st.button("Añadir Dieta", key="w_cat_b"): ventana_catering(pr)
                for p in pd_proy["catering"]: st.write(f"**{p['nombre']}**: {p['dieta']}")

            elif s_e == "Desglose":
                if st.button("Extraer Escena", key="w_de_b"): ventana_desglose(pr)
                for d in pd_proy["desglose"]: st.write(f"**ESC {d['escena']}**: {d['desc']}")

            elif s_e == "Laboratorio Guion":
                if st.button("Crear Personaje", key="w_lg_b"): ventana_personaje(pr)
                for p in pd_proy.get("personajes", []): st.write(f"**{p['nombre']}**: {p['rol']}")

            elif s_e == "Inventario":
                if st.button("Agregar a Base", key="w_in_b"): ventana_equipo(pr, rol_actual)
                for e in pd_proy["equipos"]: st.write(f"**{e['cant']}x {e['item']}**")

            elif s_e == "Plan Rodaje":
                if st.button("Nuevo Bloque", key="w_pl_b"): ventana_cronograma(pr)
                for a in pd_proy["plan_rodaje"]: st.write(f"**{a['hora']}**: {a['actividad']}")

            elif s_e == "Monitor DIR":
                c1, c2 = st.columns(2)
                c1.button("Shot List", on_click=lambda: ventana_plano(pr), key="w_md_1")
                c2.button("Loguear Toma", on_click=lambda: ventana_toma_dir(pr), key="w_md_2")
                for t in pd_proy["tomas_dir"]: st.write(f"**ESC {t['escena']} T {t['toma']}**: {t['evaluacion']}")

            elif s_e == "Luces (Canvas)":
                modo = st.selectbox("Trazado", ["freedraw", "line", "rect", "circle", "transform"], key="w_lu_s")
                st_canvas(stroke_color="#FBAF3B", background_color="#0A0A0C", width=330, height=350, drawing_mode=modo, key="cv_l")

            elif s_e == "Ref. IA":
                try:
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    m = st.chat_input("Prompt visual...", key="w_ri")
                    if m: st.info(genai.GenerativeModel('gemini-1.5-flash').generate_content(f"Sos DF: {m}").text)
                except: st.error("Falta API Key.")

            elif s_e == "Arte & Vestuario":
                if st.button("Añadir Objeto", key="w_ar_v"): ventana_arte(pr)
                for i in pd_proy["arte"]: st.write(f"**{i['objeto']}** ({i['estado']})")

            elif s_e == "Log Sonido":
                if st.button("Registrar", key="w_ls"): ventana_sonido(pr)
                for s in pd_proy["sonido_log"]: st.write(f"**ESC {s['escena']} T {s['toma']}**")

            elif s_e == "Raccord":
                if st.button("Asentar", key="w_ra"): ventana_continuidad(pr)
                for n in pd_proy["continuidad"]: st.write(f"**ESC {n['escena']} T {n['toma']}**: {n['detalle']}")
