import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
import os
import base64
from streamlit_drawable_canvas import st_canvas

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="FTN AI | Workspace", page_icon="⚡", layout="wide")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

ARCHIVO_BD = "ftn_database.json"

# --- 2. MOTOR DE MEMORIA PERMANENTE Y PARCHE AUTOMÁTICO ---
def guardar_y_recargar():
    with open(ARCHIVO_BD, "w", encoding="utf-8") as f:
        json.dump(st.session_state["proyectos"], f, ensure_ascii=False, indent=4)
    st.rerun()

def inicializar_bd():
    if "proyectos" not in st.session_state:
        if os.path.exists(ARCHIVO_BD):
            with open(ARCHIVO_BD, "r", encoding="utf-8") as f:
                data_cargada = json.load(f)
                
                claves_necesarias = [
                    "archivos_pendientes", "avisos", "equipos", "pedidos_equipos", "continuidad", 
                    "arte", "planos", "plan_rodaje", "plantas_luces", "sonido_log", "tomas_dir", 
                    "personajes", "locaciones", "crew", "catering", "links", "presupuesto", 
                    "casting", "desglose"
                ]
                for nombre_proy, datos_proy in data_cargada.items():
                    if "contexto_aprobado" not in datos_proy:
                        datos_proy["contexto_aprobado"] = "Proyecto actualizado."
                    for clave in claves_necesarias:
                        if clave not in datos_proy:
                            datos_proy[clave] = []
                            
                st.session_state["proyectos"] = data_cargada
        else:
            st.session_state["proyectos"] = {
                "Piloto Serie Web": {
                    "contexto_aprobado": "Comedia negra en una oficina.",
                    "archivos_pendientes": [], "avisos": [], "equipos": [], "pedidos_equipos": [], "continuidad": [], 
                    "arte": [], "planos": [], "plan_rodaje": [], "plantas_luces": [], "sonido_log": [], "tomas_dir": [], 
                    "personajes": [], "locaciones": [], "crew": [], "catering": [],
                    "links": [], "presupuesto": [], "casting": [], "desglose": [] 
                }
            }

inicializar_bd()

# --- 3. VENTANAS EMERGENTES (MODALES) ---

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
    col1, col2, col3 = st.columns(3)
    em1_nom = col1.text_input("Nom. Em 1", key="e1n")
    em1_vin = col2.text_input("Vínculo", key="e1v")
    em1_tel = col3.text_input("Teléfono", key="e1t")
    col4, col5, col6 = st.columns(3)
    em2_nom = col4.text_input("Nom. Em 2", key="e2n")
    em2_vin = col5.text_input("Vínculo", key="e2v")
    em2_tel = col6.text_input("Teléfono", key="e2t")
    if st.button("Fichar en Proyecto", use_container_width=True):
        if nombre:
            st.session_state["proyectos"][proyecto]["crew"].append({
                "nombre": nombre, "rol": rol, "telefono": telefono, "obra_social": obra_social,
                "em1_nom": em1_nom, "em1_vin": em1_vin, "em1_tel": em1_tel, "em2_nom": em2_nom, "em2_vin": em2_vin, "em2_tel": em2_tel
            })
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

@st.dialog("🛒 Solicitar Equipo a Producción")
def ventana_pedido(proyecto, area):
    item_nombre = st.text_input("Equipo Solicitado")
    justificacion = st.text_area("Notas para Producción")
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

@st.dialog("📝 Registrar Nota de Continuidad")
def ventana_continuidad(proyecto):
    c1, c2 = st.columns(2)
    escena = c1.text_input("Escena N°")
    toma = c2.text_input("Toma N°")
    detalle = st.text_area("Detalle de raccord")
    if st.button("Guardar Registro", use_container_width=True):
        if escena and detalle:
            st.session_state["proyectos"][proyecto]["continuidad"].append({"escena": escena, "toma": toma, "detalle": detalle})
            guardar_y_recargar()

@st.dialog("🎨 Cargar Arte (Con Foto)")
def ventana_arte(proyecto):
    categoria = st.radio("Baúl:", ["🪑 Utilería", "👗 Vestuario"], horizontal=True)
    objeto = st.text_input("Objeto o Prenda")
    responsable = st.text_input("Quién lo trae")
    estado = st.selectbox("Estado", ["🔴 Pendiente", "🟢 Listo en Set"])
    foto_subida = st.file_uploader("Subir foto", type=["jpg", "png", "jpeg"])
    if st.button("Guardar Elemento", use_container_width=True):
        if objeto:
            foto_base64 = base64.b64encode(foto_subida.read()).decode('utf-8') if foto_subida else None
            st.session_state["proyectos"][proyecto]["arte"].append({
                "categoria": categoria, "objeto": objeto, "responsable": responsable, "estado": estado, "foto": foto_base64
            })
            guardar_y_recargar()

@st.dialog("🎬 Diseñar Plano (Shot List)")
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

@st.dialog("⏱️ Cargar Cronograma (AD)")
def ventana_cronograma(proyecto):
    hora = st.time_input("Hora")
    actividad = st.text_input("Actividad (Ej: Armado, Rodaje)")
    if st.button("Sumar al Cronograma", use_container_width=True):
        if actividad:
            st.session_state["proyectos"][proyecto]["plan_rodaje"].append({"hora": str(hora), "actividad": actividad})
            guardar_y_recargar()

@st.dialog("💡 Cargar Planta de Luces")
def ventana_luces(proyecto):
    set_nom = st.text_input("Set / Escena")
    key_light = st.text_input("Luz Principal (Key Light)")
    fill_light = st.text_input("Luz de Relleno (Fill)")
    back_light = st.text_input("Contraluz (Backlight)")
    filtros = st.text_input("Filtros / Gelatinas / Accesorios")
    if st.button("Guardar Esquema", use_container_width=True):
        if set_nom:
            st.session_state["proyectos"][proyecto]["plantas_luces"].append({
                "set": set_nom, "key": key_light, "fill": fill_light, "back": back_light, "filtros": filtros
            })
            guardar_y_recargar()

@st.dialog("🎧 Crear Reporte de Sonido")
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

@st.dialog("📋 Registrar Toma de Dir")
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

@st.dialog("💸 Cargar Gasto al Presupuesto")
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

# --- 4. BASE DE USUARIOS Y SESIÓN ---

if "usuario_logueado" not in st.session_state:
    st.session_state["usuario_logueado"] = None

usuarios = {
    "lau": {"nombre": "Lau", "rol": "Super Admin", "nivel": "jefe_supremo", "pass": "1234"},
    "juan": {"nombre": "Juan", "rol": "Director de Sonido", "nivel": "jefe", "pass": "1234"},
    "pedro": {"nombre": "Pedro", "rol": "Asistente de Sonido", "nivel": "asistente", "pass": "1234"},
    "dani": {"nombre": "Dani", "rol": "Dirección de Fotografía", "nivel": "jefe", "pass": "1234"},
    "mario": {"nombre": "Mario", "rol": "Guion", "nivel": "jefe", "pass": "1234"},
    "ana": {"nombre": "Ana", "rol": "Producción", "nivel": "jefe", "pass": "1234"},
    "lucia": {"nombre": "Lucía", "rol": "Dirección de Arte", "nivel": "jefe", "pass": "1234"},
    "leo": {"nombre": "Leo", "rol": "Dirección", "nivel": "jefe", "pass": "1234"},
    "clara": {"nombre": "Clara", "rol": "Continuidad", "nivel": "jefe", "pass": "1234"},
    "invitado": {"nombre": "Cliente", "rol": "Invitado", "nivel": "lectura", "pass": "0000"}
}

# --- 5. LOGIN ---
if st.session_state["usuario_logueado"] is None:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; letter-spacing: 2px;'>⚡ FTN AI</h1>", unsafe_allow_html=True)
        with st.form("login", border=True):
            user = st.text_input("ID de Usuario").lower()
            password = st.text_input("Clave de Acceso", type="password")
            if st.form_submit_button("INICIAR SESIÓN", use_container_width=True):
                if user in usuarios and usuarios[user]["pass"] == password:
                    st.session_state["usuario_logueado"] = user
                    st.rerun()
                else:
                    st.error("Credenciales inválidas.")

# --- 6. PLATAFORMA CENTRAL ---
else:
    usuario = st.session_state["usuario_logueado"]
    mis_datos = usuarios[usuario]
    rol_actual = mis_datos["rol"]
    nivel_actual = mis_datos["nivel"]
    
    with st.sidebar:
        st.markdown("### ⚡ FTN AI")
        if nivel_actual == "jefe_supremo": st.error(f"👑 **{mis_datos['nombre']}** | {rol_actual}")
        elif nivel_actual == "jefe": st.success(f"🎬 **{mis_datos['nombre']}** | {rol_actual}")
        elif nivel_actual == "asistente": st.warning(f"🛠️ **{mis_datos['nombre']}** | {rol_actual}")
        else: st.info(f"👀 **{mis_datos['nombre']}** | {rol_actual}")
        st.divider()
        
        if nivel_actual in ["jefe", "jefe_supremo"]:
            with st.expander("✦ Nuevo Proyecto"):
                nuevo_proyecto = st.text_input("Nombre del proyecto:")
                if st.button("Inicializar"):
                    if nuevo_proyecto and nuevo_proyecto not in st.session_state["proyectos"]:
                        st.session_state["proyectos"][nuevo_proyecto] = {
                            "contexto_aprobado": "Proyecto nuevo.",
                            "archivos_pendientes": [], "avisos": [], "equipos": [], "pedidos_equipos": [], "continuidad": [], 
                            "arte": [], "planos": [], "plan_rodaje": [], "plantas_luces": [], "sonido_log": [], "tomas_dir": [], 
                            "personajes": [], "locaciones": [], "crew": [], "catering": [], "links": [], "presupuesto": [], "casting": [], "desglose": []
                        }
                        guardar_y_recargar()
                        
        if len(st.session_state["proyectos"]) > 0:
            proyecto_elegido = st.selectbox("❖ PROYECTO", list(st.session_state["proyectos"].keys()))
        else:
            proyecto_elegido = None
        st.divider()
        
        # MENÚ INTELIGENTE POR ROLES
        opciones_nav = ["⟡ Panel de Control", "⟡ Chat Central IA", "⟡ Baúl y Archivos", "⟡ Tablón de Avisos", "⟡ Portfolio y Links"]
        
        if rol_actual == "Super Admin":
            opciones_nav.extend([
                "⟡ Control de Presupuesto", "⟡ Bandeja de Pedidos (Prod)", "⟡ Locaciones y Scouting", "⟡ Registro de Crew", "⟡ Casting y Actores", "⟡ Planilla de Catering",
                "⟡ Desglose de Guion", "⟡ Laboratorio de Guion", 
                "⟡ Inventario General", "⟡ Plan de Rodaje (AD)", "⟡ Planos y Dirección", 
                "⟡ DF: Plantas de Luces y Lentes", "⟡ DF: Referencias Visuales IA",
                "⟡ Departamento de Arte", "⟡ Reportes de Sonido", "⟡ Notas de Continuidad"
            ])
        else:
            if rol_actual == "Producción": 
                opciones_nav.extend(["⟡ Control de Presupuesto", "⟡ Bandeja de Pedidos (Prod)", "⟡ Locaciones y Scouting", "⟡ Registro de Crew", "⟡ Casting y Actores", "⟡ Planilla de Catering"])
            else:
                if nivel_actual != "lectura":
                    opciones_nav.extend(["⟡ Solicitar Equipos", "⟡ Inventario General"])
            
            if rol_actual == "Guion": opciones_nav.extend(["⟡ Desglose de Guion", "⟡ Laboratorio de Guion"])
            if "Dirección" in rol_actual and rol_actual not in ["Dirección de Arte", "Dirección de Fotografía"]: 
                opciones_nav.extend(["⟡ Casting y Actores", "⟡ Plan de Rodaje (AD)", "⟡ Planos y Dirección"])
            if rol_actual == "Dirección de Fotografía": opciones_nav.extend(["⟡ DF: Plantas de Luces y Lentes", "⟡ DF: Referencias Visuales IA"])
            if rol_actual == "Dirección de Arte": opciones_nav.append("⟡ Departamento de Arte")
            if "Sonido" in rol_actual: opciones_nav.extend(["⟡ Reportes de Sonido"])
            if rol_actual == "Continuidad": opciones_nav.append("⟡ Notas de Continuidad")
            
        st.markdown("❖ **MÓDULOS DE ÁREA**")
        seccion_elegida = st.radio("Navegación:", opciones_nav, label_visibility="collapsed")
        st.divider()
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state["usuario_logueado"] = None
            st.rerun()

    if proyecto_elegido:
        p_data = st.session_state["proyectos"][proyecto_elegido]
        
        # --- PORTFOLIO Y LINKS ---
        if seccion_elegida == "⟡ Portfolio y Links":
            colA, colB = st.columns([3, 1])
            with colA: st.markdown("## Archivo de Enlaces")
            with colB:
                if nivel_actual != "lectura":
                    if st.button("➕ Añadir Link", use_container_width=True): ventana_link(proyecto_elegido)
            st.divider()
            for lk in p_data["links"]:
                with st.container(border=True):
                    st.markdown(f"### 🔗 [{lk['titulo']}]({lk['url']})")
                    st.write(lk['desc'])

        # --- CONTROL DE PRESUPUESTO ---
        elif seccion_elegida == "⟡ Control de Presupuesto":
            colA, colB, colC = st.columns([2, 1, 1])
            with colA: st.markdown("## Presupuesto de Producción")
            with colB:
                if st.button("➕ Cargar Gasto", use_container_width=True): ventana_presupuesto(proyecto_elegido)
            with colC:
                if p_data["presupuesto"]:
                    df_presup = pd.DataFrame(p_data["presupuesto"])
                    st.download_button("⬇️ Descargar", data=df_presup.to_csv(index=False).encode('utf-8'), file_name="presupuesto.csv", mime="text/csv", use_container_width=True)
            st.divider()
            total = sum(item['costo'] for item in p_data["presupuesto"])
            st.success(f"**Gasto Total: ${total:,.2f}**")
            for item in p_data["presupuesto"]:
                with st.container(border=True):
                    st.markdown(f"**{item['estado']}** | ${item['costo']:,.2f} - {item['item']} ({item['area']})")

        # --- CASTING ---
        elif seccion_elegida == "⟡ Casting y Actores":
            colA, colB = st.columns([3, 1])
            with colA: st.markdown("## Planilla de Casting")
            with colB:
                if nivel_actual in ["jefe", "jefe_supremo"]:
                    if st.button("➕ Cargar Actor/Actriz", use_container_width=True): ventana_casting(proyecto_elegido)
            st.divider()
            for actor in p_data["casting"]:
                with st.container(border=True):
                    st.markdown(f"### {actor['actor']} 🎭 Personaje: {actor['personaje']}")
                    st.write(f"🔗 [Ver Reel / Videobook]({actor['reel']})")
                    if actor.get("foto"):
                        st.image(base64.b64decode(actor["foto"]), width=200)

        # --- DESGLOSE DE GUION ---
        elif seccion_elegida == "⟡ Desglose de Guion":
            colA, colB, colC = st.columns([2, 1, 1])
            with colA: st.markdown("## Desglose (Script Breakdown)")
            with colB:
                if st.button("➕ Desglosar Escena", use_container_width=True): ventana_desglose(proyecto_elegido)
            with colC:
                if p_data["desglose"]:
                    df_desg = pd.DataFrame(p_data["desglose"])
                    st.download_button("⬇️ Descargar", data=df_desg.to_csv(index=False).encode('utf-8'), file_name="desglose.csv", mime="text/csv", use_container_width=True)
            st.divider()
            for d in p_data["desglose"]:
                with st.container(border=True):
                    st.markdown(f"**Escena {d['escena']} | {d['intext']} | {d['dianoche']}**")
                    st.write(d['desc'])

        # --- PANEL DE CONTROL ---
        elif seccion_elegida == "⟡ Panel de Control":
            st.markdown(f"## {proyecto_elegido.upper()}")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Miembros", len(p_data["crew"]))
            col2.metric("Locaciones", len(p_data["locaciones"]))
            col3.metric("Equipos", len(p_data["equipos"]))
            col4.metric("Pedidos Ptes.", len(p_data["pedidos_equipos"]))
            st.divider()
            
            st.markdown("### ⚡ Inteligencia Artificial Central")
            if st.button("Generar Call Sheet Automático con IA", use_container_width=True):
                CLAVE_API = st.secrets["GEMINI_API_KEY"]
                genai.configure(api_key=CLAVE_API)
                modelo = genai.GenerativeModel('gemini-3.5-flash')
                datos = f"Avisos: {p_data['avisos']} | Equipo: {p_data['crew']} | Catering: {p_data['catering']} | Locaciones: {p_data['locaciones']}"
                prompt = f"Sos FTN AI. Proyecto: {proyecto_elegido}. Datos actuales: {datos}. Redactá una hoja de llamado (Call Sheet) profesional resumiendo citaciones, locaciones y dietas."
                with st.spinner("Procesando datos del rodaje..."):
                    respuesta = modelo.generate_content(prompt)
                    st.success("Call Sheet generado:")
                    st.write(respuesta.text)
            
        # --- SOLICITAR EQUIPOS ---
        elif seccion_elegida == "⟡ Solicitar Equipos":
            colA, colB = st.columns([3, 1])
            with colA: st.markdown("## Solicitar Equipos a Producción")
            with colB:
                if st.button("➕ Enviar Pedido", use_container_width=True): ventana_pedido(proyecto_elegido, rol_actual)
            st.divider()
            mis_pedidos = [p for p in p_data["pedidos_equipos"] if p["area"] == rol_actual or rol_actual == "Super Admin"]
            for ped in mis_pedidos:
                with st.container(border=True):
                    st.write(f"**Ítem:** {ped['item']} | **Notas:** {ped['notas']} | 🕒 Estado: {ped['estado']}")

        # --- BANDEJA DE PEDIDOS PROD ---
        elif seccion_elegida == "⟡ Bandeja de Pedidos (Prod)":
            st.markdown("## Bandeja de Solicitudes")
            for i, ped in enumerate(p_data["pedidos_equipos"]):
                with st.container(border=True):
                    st.write(f"**De:** {ped['area']} | **Ítem:** {ped['item']} | **Notas:** {ped['notas']}")
                    c1, c2 = st.columns(2)
                    if c1.button("✅ Aprobar", key=f"p_ap_{i}"):
                        p_data["equipos"].append({"area": ped['area'], "item": ped['item'], "cant": 1, "tipo": "A Confirmar", "rental": "A Definir"})
                        p_data["pedidos_equipos"].pop(i)
                        guardar_y_recargar()
                    if c2.button("❌ Rechazar", key=f"p_re_{i}"):
                        p_data["pedidos_equipos"].pop(i)
                        guardar_y_recargar()

        # --- PLAN DE RODAJE ---
        elif seccion_elegida == "⟡ Plan de Rodaje (AD)":
            colA, colB = st.columns([3, 1])
            with colA: st.markdown("## Cronograma del Día")
            with colB: 
                if st.button("➕ Cargar Actividad", use_container_width=True): ventana_cronograma(proyecto_elegido)
            st.divider()
            cronograma = sorted(p_data["plan_rodaje"], key=lambda x: x.get('hora', '00:00'))
            for act in cronograma:
                with st.container(border=True):
                    st.markdown(f"**{act.get('hora', '')}** | {act['actividad']}")

        # --- FOTO Y LUCES ---
        elif seccion_elegida == "⟡ DF: Plantas de Luces y Lentes":
            st.markdown("## Departamento de Fotografía")
            tab1, tab2 = st.tabs(["💡 Planta de Luces", "🧮 Calculadora DOF"])
            with tab1:
                c1, c2 = st.columns([1, 4])
                with c1:
                    modo_dibujo = st.selectbox("Herramienta", ["freedraw", "line", "rect", "circle"])
                    color = st.color_picker("Color", "#FFFFFF")
                with c2:
                    st_canvas(fill_color="rgba(255, 165, 0, 0.3)", stroke_width=3, stroke_color=color, background_color="#1E1E1E", width=700, height=450, drawing_mode=modo_dibujo, key="canvas_luces")
            with tab2:
                c1, c2, c3 = st.columns(3)
                focal = c1.number_input("Distancia Focal (mm)", 10, 200, 50)
                apertura = c2.number_input("Apertura (f/)", 1.0, 22.0, 2.8)
                distancia = c3.number_input("Distancia (m)", 0.5, 100.0, 3.0)
                hiperfocal = (focal ** 2) / (apertura * 0.03) / 1000 
                cerca = (distancia * hiperfocal) / (hiperfocal + distancia)
                st.info(f"**Foco nítido empieza a:** {cerca:.2f}m")

        # --- IA VISUAL ---
        elif seccion_elegida == "⟡ DF: Referencias Visuales IA":
            st.markdown("## 🧠 Laboratorio Visual IA")
            CLAVE_API = st.secrets["GEMINI_API_KEY"]
            genai.configure(api_key=CLAVE_API)
            mod_foto = genai.GenerativeModel('gemini-3.5-flash')
            instruccion_foto = "Sos un DF experto. Cuando recomiendes algo visual, poné este link exacto en Markdown: [🖼️ Ver referencias de ESTO](https://www.google.com/search?tbm=isch&q=TERMINOS)"
            msg_foto = st.chat_input("Ej: Iluminación de Roger Deakins...")
            if msg_foto:
                st.markdown(f"**Vos:** {msg_foto}")
                resp_foto = mod_foto.generate_content(f"{instruccion_foto} \n\nConsulta: {msg_foto}")
                st.markdown(f"**🧠 IA Visual:** {resp_foto.text}")

        # --- LOCACIONES ---
        elif seccion_elegida == "⟡ Locaciones y Scouting":
            colA, colB = st.columns([3, 1])
            with colA: st.markdown("## Gestión de Locaciones")
            with colB:
                if nivel_actual in ["jefe", "jefe_supremo"]:
                    if st.button("➕ Agregar Locación", use_container_width=True): ventana_locacion(proyecto_elegido)
            st.divider()
            for loc in p_data["locaciones"]:
                with st.container(border=True):
                    st.markdown(f"### 📍 {loc['nombre']}")
                    st.write(f"**Dirección:** {loc['direccion']} | **Permiso:** {loc['permisos']}")
                    if loc['lat'] != 0.0 and loc['lon'] != 0.0:
                        st.map(pd.DataFrame({'lat': [loc['lat']], 'lon': [loc['lon']]}), zoom=15, use_container_width=True)

        # --- REGISTRO DE CREW ---
        elif seccion_elegida == "⟡ Registro de Crew":
            colA, colB, colC = st.columns([2, 1, 1])
            with colA: st.markdown("## Base de Datos (Crew/Elenco)")
            with colB:
                if st.button("➕ Fichar Miembro", use_container_width=True): ventana_crew(proyecto_elegido)
            with colC:
                if p_data["crew"]:
                    df_crew = pd.DataFrame(p_data["crew"])
                    st.download_button("⬇️ Descargar", data=df_crew.to_csv(index=False).encode('utf-8'), file_name="crew.csv", mime="text/csv", use_container_width=True)
            st.divider()
            for persona in p_data["crew"]:
                with st.container(border=True):
                    st.markdown(f"### {persona['nombre']} ({persona['rol']})")

        # --- CATERING ---
        elif seccion_elegida == "⟡ Planilla de Catering":
            colA, colB, colC = st.columns([2, 1, 1])
            with colA: st.markdown("## Registro de Dietas")
            with colB:
                if st.button("➕ Cargar Preferencias", use_container_width=True): ventana_catering(proyecto_elegido)
            with colC:
                if p_data["catering"]:
                    df_cat = pd.DataFrame(p_data["catering"])
                    st.download_button("⬇️ Descargar", data=df_cat.to_csv(index=False).encode('utf-8'), file_name="catering.csv", mime="text/csv", use_container_width=True)
            st.divider()
            for persona in p_data["catering"]:
                with st.container(border=True):
                    st.markdown(f"**{persona['nombre']}** | 🍽️ {persona['dieta']}")

        # --- TABLÓN DE AVISOS ---
        elif seccion_elegida == "⟡ Tablón de Avisos":
            colA, colB = st.columns([3, 1])
            with colA: st.markdown("## Tablón de Anuncios")
            with colB:
                if nivel_actual in ["jefe", "jefe_supremo"]:
                    if st.button("➕ Crear Publicación", use_container_width=True): ventana_aviso(proyecto_elegido, mis_datos['nombre'], p_data["locaciones"])
            st.divider()
            for aviso in reversed(p_data["avisos"]):
                with st.container(border=True):
                    st.markdown(f"**{aviso['autor']} publicó:** {aviso.get('texto', 'Citación cargada.')}")

        # --- BAÚL DE ARCHIVOS ---
        elif seccion_elegida == "⟡ Baúl y Archivos":
            st.markdown("## Repositorio de Documentos")
            if nivel_actual != "lectura":
                archivo_subido = st.file_uploader("Cargar documento (.txt)", type=["txt"])
                if archivo_subido:
                    if st.button("Subir a FTN AI"):
                        if nivel_actual in ["jefe", "jefe_supremo"]:
                            p_data["contexto_aprobado"] += f"\n\n[Doc: {archivo_subido.name}]:\n{archivo_subido.getvalue().decode('utf-8')}"
                            guardar_y_recargar()
                        else:
                            p_data["archivos_pendientes"].append({"autor": mis_datos['nombre'], "nombre": archivo_subido.name, "texto": archivo_subido.getvalue().decode('utf-8')})
                            guardar_y_recargar()
            if nivel_actual in ["jefe", "jefe_supremo"] and len(p_data["archivos_pendientes"]) > 0:
                st.divider()
                st.markdown("### ↳ Requieren Aprobación")
                for i, doc in enumerate(p_data["archivos_pendientes"]):
                    with st.container(border=True):
                        st.write(f"**{doc['nombre']}** ({doc['autor']})")
                        c1, c2 = st.columns(2)
                        if c1.button("Aprobar", key=f"ap_{i}"):
                            p_data["contexto_aprobado"] += f"\n\n[Doc de {doc['autor']} - {doc['nombre']}]:\n{doc['texto']}"
                            p_data["archivos_pendientes"].pop(i)
                            guardar_y_recargar()
                        if c2.button("Rechazar", key=f"re_{i}"):
                            p_data["archivos_pendientes"].pop(i)
                            guardar_y_recargar()

        # --- INVENTARIO GENERAL ---
        elif seccion_elegida == "⟡ Inventario General":
            colA, colB = st.columns([3, 1])
            with colA: st.markdown("## Inventario Técnico Aprobado")
            with colB:
                if nivel_actual in ["jefe", "jefe_supremo"]:
                    if st.button("➕ Cargar Directo", use_container_width=True): ventana_equipo(proyecto_elegido, rol_actual)
            st.divider()
            for eq in p_data["equipos"]:
                with st.container(border=True):
                    st.markdown(f"**{eq['cant']}x {eq['item']}** | {eq['area']} | {eq['tipo']}")

        # --- LABORATORIO DE GUION ---
        elif seccion_elegida == "⟡ Laboratorio de Guion":
            colA, colB = st.columns([3, 1])
            with colA: st.markdown("## Laboratorio Narrativo")
            with colB:
                if st.button("➕ Nuevo Personaje", use_container_width=True): ventana_personaje(proyecto_elegido)
            st.divider()
            for p in p_data["personajes"]:
                with st.container(border=True):
                    st.markdown(f"### {p['nombre']} ({p['rol']})")

        # --- DEPARTAMENTO DE ARTE ---
        elif seccion_elegida == "⟡ Departamento de Arte":
            colA, colB = st.columns([3, 1])
            with colA: st.markdown("## Departamento de Arte")
            with colB:
                if st.button("➕ Agregar Elemento", use_container_width=True): ventana_arte(proyecto_elegido)
            st.divider()
            for item in p_data["arte"]:
                with st.container(border=True):
                    st.markdown(f"**{item['estado']}** | {item['objeto']} ({item['categoria']})")
                    if item.get("foto"):
                        st.image(base64.b64decode(item["foto"]), width=150)

        # --- PLANOS Y DIRECCIÓN ---
        elif seccion_elegida == "⟡ Planos y Dirección":
            colA, colB, colC = st.columns([2, 1, 1])
            with colA: st.markdown("## Dirección")
            with colB:
                if st.button("➕ Diseño de Plano", use_container_width=True): ventana_plano(proyecto_elegido)
            with colC:
                if st.button("➕ Monitor de Toma", use_container_width=True): ventana_toma_dir(proyecto_elegido)
            st.divider()
            for t in p_data["tomas_dir"]:
                with st.container(border=True):
                    st.markdown(f"{t['evaluacion']} | **Escena {t['escena']} - Toma {t['toma']}**")

        # --- REPORTES DE SONIDO ---
        elif seccion_elegida == "⟡ Reportes de Sonido":
            colA, colB = st.columns([3, 1])
            with colA: st.markdown("## Reportes de Sonido")
            with colB:
                if st.button("➕ Nuevo Reporte", use_container_width=True): ventana_sonido(proyecto_elegido)
            st.divider()
            for s in reversed(p_data["sonido_log"]):
                with st.container(border=True):
                    st.markdown(f"🎧 **Escena {s['escena']} | Toma {s['toma']}**")

        # --- NOTAS DE CONTINUIDAD ---
        elif seccion_elegida == "⟡ Notas de Continuidad":
            colA, colB = st.columns([3, 1])
            with colA: st.markdown("## Raccord")
            with colB:
                if st.button("➕ Nueva Nota", use_container_width=True): ventana_continuidad(proyecto_elegido)
            st.divider()
            for nota in reversed(p_data["continuidad"]):
                with st.container(border=True):
                    st.markdown(f"🎬 **Escena {nota['escena']} - Toma {nota['toma']}** ↳ {nota['detalle']}")

        # --- CHAT CENTRAL IA ---
        elif seccion_elegida == "⟡ Chat Central IA":
            st.markdown("## ⚡ Asistente FTN AI Central")
            CLAVE_API = st.secrets["GEMINI_API_KEY"]
            genai.configure(api_key=CLAVE_API)
            modelo = genai.GenerativeModel('gemini-3.5-flash')
            instruccion = f"Sos FTN AI. Hablás con: {mis_datos['nombre']} ({rol_actual}). Contexto: {p_data['contexto_aprobado']}"
            mensaje = st.chat_input("Escribí tu consulta técnica...")
            if mensaje:
                st.markdown(f"**{mis_datos['nombre']}:** {mensaje}")
                respuesta = modelo.generate_content(f"{instruccion} \n\nUsuario: {mensaje}")
                st.markdown(f"**⚡ FTN AI:** {respuesta.text}")
