# Insight Dashboard AI 📊✨

Dashboard builder impulsado por IA que analiza archivos Excel/CSV y genera visualizaciones automáticamente usando Claude Sonnet 4.5.

**Demo features:**

- 🚀 Control drag-and-drop para archivos CSV/XLSX
- 🤖 Análisis inteligente con Claude AI
- 📈 Visualizaciones automáticas (Bar, Line, Pie, Scatter)
- ⚡ Procesamiento en tiempo real con `pandas`
- 🎨 UI moderna con Tailwind CSS

## 🚀 Quick Start

### Prerequisitos

- Docker y Docker Compose instalados
- Cuenta de Anthropic con API key (https://console.anthropic.com/)

### Configuración Local

1. **Clonar el repositorio**

```bash
git clone https://github.com/rodrigopineda028/insight-dashboard-ai.git
cd insight-dashboard-ai
```

2. **Configurar API Key de Claude**

```bash
cp .env.example .env
# Edita .env y agrega tu ANTHROPIC_API_KEY
```

**Obtener API Key:**

- Regístrate en https://console.anthropic.com/
- Ve a Settings → API Keys
- Crea una nueva key
- Copia y pega en `.env`

3. **Iniciar con Docker**

```bash
docker compose up --build
```

Espera a que ambos servicios estén listos (backend: ~30s, frontend: ~40s)

4. **Abrir en el navegador**

- **Frontend**: http://localhost:5173
- **Backend API Docs**: http://localhost:8000/docs

## 📁 Estructura del Proyecto

```
insight-dashboard-ai/
├── backend/                 # FastAPI + Python
│   ├── app/
│   │   ├── routes/
│   │   │   ├── upload.py   # Upload y procesamiento pandas
│   │   │   ├── analyze.py  # Integración Claude AI
│   │   │   └── charts.py   # Endpoint de datos para gráficos
│   │   └── main.py         # App principal
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                # React + TypeScript + Vite
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.tsx
│   │   │   ├── AnalysisSuggestions.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── charts/     # Componentes Recharts
│   │   │   └── ui/         # Skeletons, tooltips, feedback
│   │   └── App.tsx
│   └── package.json
├── examples/                # CSVs de ejemplo
│   ├── ventas_ejemplo.csv
│   ├── marketing_digital.csv
│   └── ecommerce_transacciones.csv
└── docker-compose.yml
```

## 🛠 Stack Técnico

**Backend:**

- **FastAPI** 0.115.0 - Web framework moderno y rápido
- **Pandas** 2.2.2 - Procesamiento y análisis de datos
- **Anthropic SDK** 0.40.0 - Integración con Claude AI
- **openpyxl** 3.1.5 - Soporte para archivos Excel

**Frontend:**

- **React** 19.2.0 + **TypeScript** 5.9.3
- **Vite** 7.3.1 - Build tool
- **Tailwind CSS** 3.4.17 - Para estílos CSS
- **Recharts** - Gráficos interactivos
- **react-dropzone** - Drag & drop para subida de archivos

**AI:**

- **Claude Sonnet 4.5** (`claude-sonnet-4-5`)
- Temperature: 0.3 para JSON consistente
- Max tokens: 2000 por análisis
- Retry logic con 3 intentos

## 📊 Cómo Usar

### 1. Subir Archivo

- Arrastra un CSV o XLSX al área de upload (máx 5MB)
- O haz clic para seleccionar desde tu computadora
- Formatos soportados: `.csv`, `.xlsx`

### 2. Ver Metadatos

El sistema automáticamente procesa y muestra:

- **Resumen**: Cantidad de filas y columnas
- **Columnas**: Tipo de dato, valores únicos, % de nulos
- **Estadísticas**: Min, max, media para columnas numéricas
- **Vista previa**: Primeras 10 filas del dataset

### 3. Analizar con IA

- Haz clic en "Analizar con Claude"
- Claude analiza el dataset y sugiere 3-5 visualizaciones
- Cada sugerencia incluye:
  - **Título** descriptivo
  - **Tipo de gráfico** (bar/line/pie/scatter)
  - **Parámetros** (ejes, agregación)
  - **Insight** explicando el valor del gráfico

### 4. Crear Dashboard

- Haz clic en "Agregar al Dashboard" en las sugerencias
- Los gráficos se renderizan automáticamente
- Grid responsivo (2 columnas en desktop, 1 en mobile)
- Elimina gráficos con el botón ✕

## 🔑 Variables de Entorno

### Backend (`.env`)

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxx

```

### Frontend

```bash
# Optional - solo si cambias el puerto del backend
VITE_API_URL=http://localhost:8000
```

## 📦 Desarrollo Local (sin Docker)

**Backend:**

```bash
cd backend
pip install -r requirements.txt
export ANTHROPIC_API_KEY=tu_key
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```
