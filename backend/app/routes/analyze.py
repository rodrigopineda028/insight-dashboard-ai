"""AI analysis routes using Claude."""
import json
import re
from typing import Any, Dict, List

from anthropic import Anthropic
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ValidationError

from app.routes.upload import file_storage

router = APIRouter()


class AnalyzeRequest(BaseModel):
    file_id: str


class ChartSuggestion(BaseModel):
    title: str
    chart_type: str
    parameters: Dict[str, Any]
    insight: str


def build_analysis_prompt(metadata: dict) -> str:
    """Build optimized prompt for Claude to analyze dataset."""
    # Build detailed column descriptions with missingness and cardinality
    columns_desc = []
    for col in metadata["columns"]:
        col_name = col["name"]
        col_type = col["type"]
        cardinality = col.get("cardinality", 0)
        missingness = col.get("missingness_pct", 0)
        
        desc = f"- {col_name} ({col_type})"
        desc += f" | Únicos: {cardinality}"
        
        if missingness > 0:
            desc += f" | Nulos: {missingness}%"
        
        if "stats" in col:
            stats = col["stats"]
            if stats["min"] is not None:
                desc += f" | Rango: [{stats['min']:.1f}, {stats['max']:.1f}] | Media: {stats['mean']:.1f}"
        
        columns_desc.append(desc)
    
    prompt = f"""Eres un analista de datos experto. Analiza este dataset y sugiere visualizaciones impactantes.

**Dataset Info:**
- Filas totales: {metadata['row_count']:,}
- Columnas: {metadata['column_count']}

**Columnas disponibles:**
{chr(10).join(columns_desc)}

**Muestra de datos (primeras 10 filas):**
{json.dumps(metadata['sample_data'][:5], indent=2, ensure_ascii=False)}

**Tu tarea:**
Propón 3 a 5 visualizaciones que revelen patrones valiosos: top categorías, tendencias temporales, outliers, correlaciones.

**REGLAS ESTRICTAS:**
1. NO inventes columnas - usa SOLO las columnas listadas arriba
2. Usa ÚNICAMENTE estos tipos: bar, line, pie, scatter
3. Si NO hay columna de fecha/tiempo, NO uses line chart
4. Si hay muchas categorías únicas (>20), NO uses pie chart
5. Para bar/line: x_axis debe ser categórica o temporal, y_axis numérica
6. Para scatter: ambos ejes deben ser numéricos
7. Para pie: usa solo columna categórica con pocas categorías (<10)

**Responde ÚNICAMENTE con un array JSON válido, SIN texto adicional antes o después:**
[
  {{
    "title": "Título descriptivo del gráfico",
    "chart_type": "bar",
    "parameters": {{
      "x_axis": "nombre_columna_exacto",
      "y_axis": "nombre_columna_exacto",
      "aggregation": "sum"
    }},
    "insight": "Explica qué patrón revela este gráfico y por qué es valioso"
  }}
]

VALORES VÁLIDOS para aggregation: sum, count, avg, none

Recuerda: Devuelve SOLO el JSON, sin explicaciones adicionales."""
    
    return prompt


async def analyze_with_claude(metadata: dict, api_key: str, max_retries: int = 2) -> List[ChartSuggestion]:
    """Send metadata to Claude and get chart suggestions with retry logic."""
    client = Anthropic(api_key=api_key)
    
    prompt = build_analysis_prompt(metadata)
    available_columns = {col["name"] for col in metadata["columns"]}
    
    for attempt in range(max_retries + 1):
        try:
            message = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=2000,
                temperature=0.3,  # Lower for more deterministic JSON
                messages=[
                    {
                        "role": "user",
                        "content": prompt if attempt == 0 else f"{prompt}\n\nATENCIÓN: Tu respuesta anterior falló al parsear. Devuelve SOLO el array JSON, sin explicaciones."
                    }
                ]
            )
            
            response_text = message.content[0].text.strip()
            
            # Try to extract JSON if wrapped in markdown or text
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            
            # Parse JSON response
            suggestions_data = json.loads(response_text)
            
            # Validate with Pydantic
            suggestions = [ChartSuggestion(**item) for item in suggestions_data]
            
            # Validate column names exist in metadata
            for suggestion in suggestions:
                params = suggestion.parameters
                if "x_axis" in params and params["x_axis"] not in available_columns:
                    raise ValueError(f"Columna inválida en x_axis: {params['x_axis']}")
                if "y_axis" in params and params["y_axis"] not in available_columns:
                    raise ValueError(f"Columna inválida en y_axis: {params['y_axis']}")
            
            return suggestions
            
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            if attempt < max_retries:
                # Retry
                continue
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Claude retornó respuesta inválida después de {max_retries + 1} intentos: {str(e)}. Respuesta: {response_text[:200]}"
                )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al comunicarse con Claude: {str(e)}"
            )
    
    # This should never be reached due to max_retries logic, but satisfies type checker
    raise HTTPException(
        status_code=500,
        detail="No se pudo obtener respuesta válida del AI"
    )


@router.post("/analyze")
async def analyze_file(request: AnalyzeRequest):
    """
    Analyze uploaded file with Claude AI and get chart suggestions.
    """
    import os
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="ANTHROPIC_API_KEY no configurada en el servidor"
        )
    
    # Get file metadata
    if request.file_id not in file_storage:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    file_data = file_storage[request.file_id]
    metadata = file_data["metadata"]
    
    # Analyze with Claude
    suggestions = await analyze_with_claude(metadata, api_key)
    
    return {
        "file_id": request.file_id,
        "suggestions": [s.model_dump() for s in suggestions],
        "total_suggestions": len(suggestions),
    }
