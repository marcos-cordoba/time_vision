# 🚀 Time Vision

**Time Vision** es una aplicación desarrollada con **Streamlit** que permite analizar las horas trabajadas exportadas desde Odoo, compararlas con una meta mensual y visualizar indicadores de rendimiento mediante gráficos y métricas.

## 📋 Características

- 📂 Carga de archivos CSV y Excel exportados desde Odoo.
- 📅 Agrupación automática de horas por mes.
- 📊 Dashboard con métricas de rendimiento.
- 🎯 Comparación con una meta mensual configurable.
- 🚦 Indicadores visuales mediante colores (semáforo).
- 📈 Gráfico de barras con comparación respecto a la meta.
- 📑 Tabla resumen con cumplimiento mensual.

## 🛠️ Tecnologías utilizadas

- Python 3
- Streamlit
- Pandas
- Matplotlib

## 📦 Instalación

### 1. Clona el repositorio

```bash
git clone https://github.com/marcos-cordoba/time_vision
cd time_vision
```

### 2. Crea y activa un entorno virtual (opcional pero recomendado)

**Linux / macOS**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows**

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Instala las dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecuta la aplicación

```bash
streamlit run app.py
```

La aplicación estará disponible en:

```
http://localhost:8501
```

## 📂 Formato esperado del archivo

El archivo debe contener, como mínimo, las siguientes columnas:

| Columna | Descripción |
|---------|-------------|
| Fecha | Fecha del parte de horas |
| Cantidad | Horas registradas |

La aplicación agrupa automáticamente las horas por mes y genera el análisis correspondiente.

## 📊 Indicadores

La aplicación muestra:

- Horas totales cargadas.
- Promedio mensual.
- Porcentaje de cumplimiento.
- Balance acumulado.
- Gráfico comparativo contra la meta.
- Tabla resumen mensual.

## 🚦 Criterios de colores

| Color | Significado |
|--------|-------------|
| 🟢 Verde | Cumple la meta (±5 horas) |
| 🟠 Naranja | Supera la meta |
| 🔴 Rojo | Está por debajo de la meta |

## ☁️ Despliegue

La aplicación puede desplegarse fácilmente en **Streamlit Community Cloud**.

## 👨‍💻 Autor

Desarrollado por **Marcos Córdoba**.
