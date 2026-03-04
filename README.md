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
│   │   ├── config/
│   │   │   └── settings.py # Configuración centralizada
│   │   ├── models/
│   │   │   ├── requests.py # Pydantic request models
│   │   │   └── responses.py # Pydantic response models
│   │   ├── services/
│   │   │   ├── storage.py  # Abstracción almacenamiento
│   │   │   ├── ai_service.py # Integración Claude AI
│   │   │   └── chart_service.py # Procesamiento de gráficos
│   │   ├── routes/
│   │   │   ├── upload.py   # Endpoint upload
│   │   │   ├── analyze.py  # Endpoint análisis IA
│   │   │   └── charts.py   # Endpoint datos gráficos
│   │   └── main.py         # App principal
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                # React + TypeScript + Vite
│   ├── src/
│   │   ├── config/
│   │   │   └── api.ts      # Configuración API centralizada
│   │   ├── lib/
│   │   │   └── utils.ts    # Utilities (cn helper)
│   │   ├── types/
│   │   │   └── index.ts    # TypeScript interfaces compartidas
│   │   ├── components/
│   │   │   ├── Header.tsx           # Header con logo
│   │   │   ├── FileUpload.tsx       # Upload con integración API
│   │   │   ├── AnalysisLoader.tsx   # Loader animado
│   │   │   ├── AnalysisCard.tsx     # Cards de sugerencias
│   │   │   ├── DashboardGrid.tsx    # Grid con charts dinámicos
│   │   │   └── ui/                  # Componentes shadcn/ui
│   │   │       ├── button.tsx
│   │   │       ├── badge.tsx
│   │   │       └── card.tsx
│   │   ├── App.tsx          # App principal
│   │   └── main.tsx         # Entry point
│   └── package.json
├── examples/                # CSVs de ejemplo
│   ├── ventas_ejemplo.csv
│   ├── marketing_digital.csv
│   └── ecommerce_transacciones.csv
└── docker-compose.yml
```

## 🏗️ Arquitectura

### Backend: Service-Oriented Architecture

El backend sigue un patrón de arquitectura orientada a servicios para mejorar la mantenibilidad y escalabilidad:

**📦 Services Layer**

- `FileStorage`: Abstracción del almacenamiento (actualmente in-memory, fácil migrar a Redis/DB)
- `AIService`: Encapsula integración con Claude AI y prompt engineering
- `ChartService`: Procesa y transforma datos para visualizaciones

**📋 Models Layer**

- Pydantic models para requests (`AnalyzeRequest`, `ChartDataRequest`)
- Pydantic models para responses (`FileMetadata`, `ColumnInfo`, `ChartSuggestion`)
- Validación automática de tipos y serialización JSON

**⚙️ Config Layer**

- `Settings` class con todas las constantes (API keys, límites, configuración AI)
- Elimina valores hardcodeados del código

**🛣️ Routes Layer**

- Endpoints delgados que orquestan servicios
- Separación clara de responsabilidades

### Frontend: Component-Based Architecture

**🎯 Centralized Configuration**

**🎯 Centralized Configuration**

- `config/api.ts`: API_CONFIG con baseURL y endpoints
- Elimina duplicación de URLs en componentes

**📐 Shared Types**

- `types/index.ts`: Todas las TypeScript interfaces en un solo lugar
- Type safety across components sin 'any'
- Conversión entre formatos backend y UI

**🧩 Component Architecture**

- **Header**: Sticky header con logo
- **FileUpload**: Drag & drop con validación y upload automático
- **AnalysisLoader**: Animación de progreso durante análisis IA
- **AnalysisCard**: Cards interactivas para sugerencias de Claude
- **DashboardGrid**: Grid responsivo con charts dinámicos
- **UI Components**: Button, Badge, Card de shadcn/ui
- Path aliases configurados (`@/config`, `@/types`, `@/components`, `@/lib`)

## 🛠 Stack Técnico

**Backend:**

- **FastAPI** 0.115.0 - Web framework moderno y rápido
- **Pandas** 2.2.2 - Procesamiento y análisis de datos
- **Anthropic SDK** 0.40.0 - Integración con Claude AI
- **openpyxl** 3.1.5 - Soporte para archivos Excel
- **Pydantic** - Validación de datos y serialización

**Frontend:**

- **React** 19.2.0 + **TypeScript** 5.9.3
- **Vite** 7.3.1 - Build tool con HMR
- **Tailwind CSS** 3.4.17 - Utility-first CSS con variables CSS
- **shadcn/ui** - Componentes UI (Button, Badge, Card)
- **Recharts** - Gráficos interactivos
- **Lucide React** - Iconos modernos
- **clsx** + **tailwind-merge** - Manejo de clases dinámicas
- **class-variance-authority** - Variants de componentes

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
- El archivo se sube automáticamente al backend

### 2. Análisis Automático con IA

- El sistema procesa el archivo con pandas
- Claude AI analiza los datos y genera 3-5 sugerencias de visualización
- Animación de progreso muestra el estado del análisis
- Cada sugerencia incluye:
  - **Título** descriptivo
  - **Tipo de gráfico** (bar/line/pie/scatter)
  - **Columnas** a visualizar
  - **Insight de IA** explicando el valor del gráfico

### 3. Crear Dashboard

- Haz clic en "Agregar al Dashboard" en las sugerencias
- Los gráficos se cargan dinámicamente desde el backend
- Grid responsivo (2 columnas en desktop, 1 en mobile)
- Opciones de expansión/contracción de cada gráfico
- Elimina gráficos con el botón ✕

## 🧠 Ingeniería de Prompts para IA

### Estrategia de Análisis con Claude

El sistema utiliza **Claude Sonnet 4.5** con un enfoque de prompt engineering diseñado para obtener sugerencias de visualización estructuradas, consistentes y de alta calidad.

#### Estructura del Prompt

El prompt enviado a Claude incluye:

1. **Contexto del dataset** (generado por `AIService.build_analysis_prompt`):
   - Total de filas y columnas
   - Lista detallada de columnas con:
     - Tipo de dato (numeric, object, datetime)
     - Cardinalidad (valores únicos)
     - % de valores nulos
     - Estadísticas avanzadas para columnas numéricas:
       - Min, max, media (mean)
       - Desviación estándar (std)
       - Quartiles (Q1/Q3) y rango intercuartílico (IQR)
   - Muestra de las primeras 5-10 filas

2. **Instrucciones específicas**:
   - Generar **exactamente 3-5 visualizaciones**
   - Identificar patrones valiosos: tendencias, outliers, correlaciones, distribuciones
   - Priorizar insights accionables para el usuario

3. **Reglas estrictas de validación**:
   - **No inventar columnas**: solo usar las del dataset
   - **Tipos de gráfico permitidos**: `bar`, `line`, `pie`, `scatter`
   - **Validación por tipo**:
     - **Line**: requiere columna temporal o secuencial
     - **Pie**: solo para categóricas con <10 valores únicos
     - **Bar**: eje X categórico/temporal, eje Y numérico
     - **Scatter**: ambos ejes numéricos
   - **Agregaciones válidas**: `sum`, `count`, `avg`, `none`

4. **Formato de respuesta**:
   - JSON array **sin texto adicional** (crítico para parsing)
   - Cada objeto con: `title`, `chart_type`, `parameters` (`x_axis`, `y_axis`, `aggregation`), `insight`

#### Parámetros de Claude

```python
model="claude-sonnet-4-5"
max_tokens=2000
temperature=0.3  # Baja para JSON determinístico
```

#### Lógica de Retry

- **Hasta 3 intentos** implementados en `AIService.analyze_dataset()`
- Retry si la respuesta no es JSON válido o no cumple reglas
- **Validación post-parsing**:
  - Columnas existen en el dataset (validación en AIService)
  - Cantidad de sugerencias entre 3-5
  - Estructura JSON correcta con Pydantic models (`ChartSuggestion`)
  - Stats validation: verifica que stats no sea None antes de acceder

#### Ejemplo de Respuesta Esperada

```json
[
  {
    "title": "Top 10 Productos por Ventas Totales",
    "chart_type": "bar",
    "parameters": {
      "x_axis": "producto",
      "y_axis": "ventas",
      "aggregation": "sum"
    },
    "insight": "Este gráfico identifica los productos más rentables, permitiendo enfocar esfuerzos de marketing en los top performers."
  }
]
```

### Decisiones Técnicas Clave

- **Temperature 0.3**: Balance entre creatividad y consistencia JSON
- **Regex fallback**: Extrae JSON si Claude lo envuelve en markdown
- **Validación doble**: Schema Pydantic + verificación de columnas
- **Retry inteligente**: Refuerza instrucciones JSON en reintentos

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
