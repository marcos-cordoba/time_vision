import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Control de Horas", page_icon="📊", layout="wide")

# ---------------------------------------------------------
# MEMORIA DE SESIÓN (SESSION STATE)
# ---------------------------------------------------------
if "base_datos" not in st.session_state:
    st.session_state.base_datos = {}  # Guarda todo por empleado y año

# ---------------------------------------------------------
# BARRA LATERAL: EMPLEADOS Y ARCHIVOS
# ---------------------------------------------------------
st.sidebar.header("⚙️ Configuración Global")
meta_horas = st.sidebar.number_input("Meta de horas mensuales:", min_value=1, value=120, step=5)

st.sidebar.divider()
st.sidebar.header("👤 Gestión de Empleados")

# Agregar un nuevo empleado
nuevo_empleado = st.sidebar.text_input("Agregar Nuevo Empleado:", placeholder="Ej: Ines")
if st.sidebar.button("➕ Crear Empleado"):
    nombre_clean = nuevo_empleado.strip().capitalize()
    if nombre_clean and nombre_clean not in st.session_state.base_datos:
        st.session_state.base_datos[nombre_clean] = {}
        st.sidebar.success(f"¡Empleado {nombre_clean} creado!")
        st.rerun()

# Selector de Empleado Actual
empleados_disponibles = list(st.session_state.base_datos.keys())
if not empleados_disponibles:
    st.session_state.base_datos["Gonzalo"] = {}
    empleados_disponibles = ["Gonzalo"]

empleado_seleccionado = st.sidebar.selectbox(
    "Selecciona un Empleado:", 
    options=empleados_disponibles
)

st.sidebar.divider()

# Carga de archivos para el empleado activo
st.sidebar.subheader(f"📁 Subir reportes para {empleado_seleccionado}")
uploaded_files = st.sidebar.file_uploader(
    "Sube los reportes anuales (CSV o Excel):", 
    type=["csv", "xlsx"],
    accept_multiple_files=True,
    key=f"uploader_{empleado_seleccionado}"
)

# ---------------------------------------------------------
# FUNCIONES DE PROCESAMIENTO DE DATOS
# ---------------------------------------------------------

# 1. Procesamiento para vista General (Resumen por Mes)
def procesar_datos_general(df_raw):
    df = df_raw.copy()
    df['Fecha_dt'] = pd.to_datetime(df['Fecha'], errors='coerce')
    df_clean = df.dropna(subset=['Fecha_dt']).copy()
    
    df_clean['Cantidad'] = pd.to_numeric(df_clean['Cantidad'], errors='coerce').fillna(0)
    df_clean['AñoMes_Key'] = df_clean['Fecha_dt'].dt.strftime('%Y-%m')
    
    resumen = df_clean.groupby('AñoMes_Key', as_index=False).agg(
        Horas=('Cantidad', 'sum'),
        Fecha_Ref=('Fecha_dt', 'min')
    ).sort_values('Fecha_Ref')
    
    meses_es = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    
    resumen['Mes'] = resumen['Fecha_Ref'].apply(lambda x: f"{meses_es[x.month]} {x.year}")
    return resumen[['Mes', 'Horas']]

# 2. Procesamiento para vista por Trabajo (Pivote por Trabajo)
def procesar_datos_trabajo(df_raw):
    df = df_raw.copy()
    
    col_trabajo = None
    for col_posible in ['Trabajo', 'Proyecto', 'Tarea', 'Project', 'Task']:
        if col_posible in df.columns:
            col_trabajo = col_posible
            break
            
    if not col_trabajo:
        df['Trabajo'] = 'General'
    else:
        df['Trabajo'] = df[col_trabajo].fillna('Sin Nombre').astype(str).str.strip()
        
    df['Fecha_dt'] = pd.to_datetime(df['Fecha'], errors='coerce')
    df_clean = df.dropna(subset=['Fecha_dt']).copy()
    
    df_clean['Cantidad'] = pd.to_numeric(df_clean['Cantidad'], errors='coerce').fillna(0)
    df_clean['AñoMes_Key'] = df_clean['Fecha_dt'].dt.strftime('%Y-%m')
    
    meses_es = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    
    df_clean['Mes'] = df_clean['Fecha_dt'].apply(lambda x: f"{meses_es[x.month]} {x.year}")
    
    agrupado = df_clean.groupby(['AñoMes_Key', 'Mes', 'Trabajo'], as_index=False)['Cantidad'].sum()
    agrupado = agrupado.sort_values('AñoMes_Key')
    
    pivoted = agrupado.pivot(index='Mes', columns='Trabajo', values='Cantidad').fillna(0)
    orden_meses = agrupado['Mes'].unique()
    pivoted = pivoted.reindex(orden_meses)
    
    return pivoted

# Función global para leer cualquier archivo subido
def cargar_archivo_raw(file):
    try:
        if file.name.endswith('.csv'):
            try:
                df_raw = pd.read_csv(file, encoding='utf-8')
            except Exception:
                file.seek(0)
                df_raw = pd.read_csv(file, sep=';', encoding='utf-8')
        else:
            df_raw = pd.read_excel(file)
            
        df_raw.columns = df_raw.columns.str.strip()
        if 'Fecha' not in df_raw.columns or 'Cantidad' not in df_raw.columns:
            st.error(f"El archivo {file.name} requiere las columnas 'Fecha' y 'Cantidad'.")
            return None
        return df_raw
    except Exception as e:
        st.error(f"Error cargando {file.name}: {e}")
        return None

def obtener_color(horas, meta):
    if horas < (meta - 20):
        return '#e74c3c'  # Rojo
    elif (meta - 20) <= horas <= (meta + 20):
        return '#2ecc71'  # Verde
    else:
        return '#f39c12'  # Naranja

# Guardar archivos subidos en la memoria de sesión
if uploaded_files:
    for file in uploaded_files:
        raw_data = cargar_archivo_raw(file)
        if raw_data is not None:
            nombre_anio = file.name.rsplit('.', 1)[0]
            st.session_state.base_datos[empleado_seleccionado][nombre_anio] = raw_data

# ---------------------------------------------------------
# ESTRUCTURA PRINCIPAL DE PÁGINAS (VISTAS)
# ---------------------------------------------------------
archivos_empleado = st.session_state.base_datos.get(empleado_seleccionado, {})

if archivos_empleado:
    st.title(f"👤 Panel de Control: {empleado_seleccionado}")
    
    # PESTAÑAS PRINCIPALES DE NAVEGACIÓN (PÁGINAS)
    pagina_general, pagina_trabajo = st.tabs([
        "📊 Cumplimiento General (Metas)", 
        "🧩 Análisis Desglosado por Trabajo"
    ])

    # =========================================================
    # PÁGINA 1: CUMPLIMIENTO GENERAL (SEMÁFORO)
    # =========================================================
    with pagina_general:
        st.markdown("Análisis mensual respecto a la meta de horas fijada.")
        nombres_anios = list(archivos_empleado.keys())
        tabs_anios = st.tabs([f"📅 {nombre}" for nombre in nombres_anios])

        for i, nombre_anio in enumerate(nombres_anios):
            with tabs_anios[i]:
                df_raw = archivos_empleado[nombre_anio]
                df = procesar_datos_general(df_raw)

                if df is not None and not df.empty:
                    df['Diferencia'] = df['Horas'] - meta_horas
                    df['Cumplimiento_%'] = (df['Horas'] / meta_horas) * 100

                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Horas Totales Cargadas", f"{df['Horas'].sum():.2f} h")
                    col2.metric("Promedio Mensual", f"{df['Horas'].mean():.2f} h")
                    col3.metric("Cumplimiento Promedio", f"{df['Cumplimiento_%'].mean():.1f}%")
                    col4.metric("Balance Total Acumulado", f"{df['Diferencia'].sum():+.2f} h")

                    st.divider()

                    colores = [obtener_color(h, meta_horas) for h in df['Horas']]
                    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=100)
                    barras = ax.bar(df['Mes'], df['Horas'], color=colores, width=0.5)
                    ax.axhline(y=meta_horas, color='#2c3e50', linestyle='--', linewidth=2, label=f'Meta ({meta_horas}h)')

                    for bar in barras:
                        yval = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 2, f'{yval:.1f}h', 
                                ha='center', va='bottom', fontsize=9, fontweight='bold')

                    ax.set_title(f'Resumen de Horas Mensuales - {nombre_anio} ({empleado_seleccionado})', fontsize=12, fontweight='bold', pad=15)
                    ax.set_ylabel('Horas Cargadas')
                    ax.set_ylim(0, max(df['Horas']) + 25)
                    plt.xticks(rotation=45)
                    ax.grid(axis='y', linestyle=':', alpha=0.6)
                    ax.legend(loc='upper right')

                    col_graf, col_tabla = st.columns([2, 1])
                    with col_graf:
                        st.pyplot(fig)
                    with col_tabla:
                        st.subheader("Detalle Mensual")
                        df_display = df.copy()
                        df_display['Horas'] = df_display['Horas'].map('{:.2f}'.format)
                        df_display['Diferencia'] = df_display['Diferencia'].map('{:+.2f}'.format)
                        df_display['Cumplimiento_%'] = df_display['Cumplimiento_%'].map('{:.1f}%'.format)
                        st.dataframe(df_display[['Mes', 'Horas', 'Diferencia', 'Cumplimiento_%']], hide_index=True)

    # =========================================================
    # PÁGINA 2: ANÁLISIS DESGLOSADO POR TRABAJO (APILADO)
    # =========================================================
    with pagina_trabajo:
        st.markdown("Distribución de horas trabajadas desglosadas por cada Proyecto o Tarea.")
        nombres_anios = list(archivos_empleado.keys())
        tabs_anios_tr = st.tabs([f"📅 {nombre}" for nombre in nombres_anios])

        for i, nombre_anio in enumerate(nombres_anios):
            with tabs_anios_tr[i]:
                df_raw = archivos_empleado[nombre_anio]
                pivoted_df = procesar_datos_trabajo(df_raw)

                if pivoted_df is not None and not pivoted_df.empty:
                    totales_mes = pivoted_df.sum(axis=1)
                    df_resumen = pd.DataFrame({'Horas': totales_mes})
                    df_resumen['Diferencia'] = df_resumen['Horas'] - meta_horas
                    df_resumen['Cumplimiento_%'] = (df_resumen['Horas'] / meta_horas) * 100

                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Horas Totales Cargadas", f"{df_resumen['Horas'].sum():.2f} h")
                    col2.metric("Promedio Mensual", f"{df_resumen['Horas'].mean():.2f} h")
                    col3.metric("Cumplimiento Promedio", f"{df_resumen['Cumplimiento_%'].mean():.1f}%")
                    col4.metric("Balance Total Acumulado", f"{df_resumen['Diferencia'].sum():+.2f} h")

                    st.divider()

                    # Gráfico Apilado
                    fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
                    cmap = plt.get_cmap('tab10')
                    bottom = pd.Series(0.0, index=pivoted_df.index)

                    for idx, col in enumerate(pivoted_df.columns):
                        values = pivoted_df[col]
                        ax.bar(
                            pivoted_df.index, 
                            values, 
                            bottom=bottom, 
                            label=col, 
                            color=cmap(idx % 10), 
                            width=0.5
                        )
                        bottom += values

                    ax.axhline(y=meta_horas, color='#2c3e50', linestyle='--', linewidth=2, label=f'Meta ({meta_horas}h)')

                    for mes, total in zip(pivoted_df.index, totales_mes):
                        if total > 0:
                            ax.text(mes, total + 2, f'{total:.1f}h', 
                                    ha='center', va='bottom', fontsize=9, fontweight='bold')

                    ax.set_title(f'Distribución por Trabajo - {nombre_anio} ({empleado_seleccionado})', fontsize=12, fontweight='bold', pad=15)
                    ax.set_ylabel('Horas Cargadas')
                    ax.set_ylim(0, max(totales_mes) + 25)
                    plt.xticks(rotation=45)
                    ax.grid(axis='y', linestyle=':', alpha=0.6)
                    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', frameon=True)

                    col_graf, col_tabla = st.columns([2, 1])
                    with col_graf:
                        st.pyplot(fig)
                    with col_tabla:
                        st.subheader("Desglose por Trabajo")
                        st.dataframe(pivoted_df.style.format("{:.1f}"), hide_index=False)

else:
    st.info(f"👈 El empleado **{empleado_seleccionado}** no tiene reportes cargados. Sube sus archivos CSV/Excel en la barra lateral.")