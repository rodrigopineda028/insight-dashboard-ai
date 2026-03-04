"""AI service for Claude integration and analysis."""
import json
import re
from typing import List

from anthropic import Anthropic
from fastapi import HTTPException
from pydantic import ValidationError

from app.config.settings import settings
from app.models.responses import ChartSuggestion


class AIService:
    """Service for AI-powered data analysis using Claude."""
    
    def __init__(self):
        """Initialize AI service with API key from settings."""
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not configured")
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    def build_analysis_prompt(self, metadata: dict) -> str:
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
            
            if "stats" in col and col["stats"] is not None:
                stats = col["stats"]
                if stats.get("min") is not None:
                    desc += f" | Rango: [{stats['min']:.1f}, {stats['max']:.1f}]"
                    desc += f" | Media: {stats['mean']:.1f} | Mediana: {stats['median']:.1f}"
                    if stats.get('std'):
                        desc += f" | Std: {stats['std']:.1f}"
                    # Add distribution info for outlier detection
                    if stats.get('q25') and stats.get('q75'):
                        iqr = stats['q75'] - stats['q25']
                        desc += f" | IQR: {iqr:.1f}"
            
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
Propón EXACTAMENTE entre 3 y 5 visualizaciones que revelen patrones valiosos: top categorías, tendencias temporales, outliers, correlaciones.

**REGLAS ESTRICTAS:**
1. NO inventes columnas - usa SOLO las columnas listadas arriba
2. Usa ÚNICAMENTE estos tipos: bar, line, pie, scatter
3. Si NO hay columna de fecha/tiempo, NO uses line chart
4. Si hay muchas categorías únicas (>20), NO uses pie chart
5. Para bar/line: x_axis debe ser categórica o temporal, y_axis numérica
6. Para scatter: ambos ejes deben ser numéricos Y DIFERENTES (si solo hay 1 columna numérica, usa line chart en vez de scatter)
7. Para pie: usa solo columna categórica con pocas categorías (<10)
8. NUNCA uses la misma columna para x_axis y y_axis
9. Si tienes fecha + valor numérico, prefiere line chart sobre scatter

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
    
    async def analyze_dataset(self, metadata: dict) -> List[ChartSuggestion]:
        """
        Analyze dataset and get chart suggestions from Claude.
        
        Args:
            metadata: Dataset metadata including columns and sample data
            
        Returns:
            List of ChartSuggestion objects
            
        Raises:
            HTTPException: If analysis fails or returns invalid data
        """
        prompt = self.build_analysis_prompt(metadata)
        available_columns = {col["name"] for col in metadata["columns"]}
        
        for attempt in range(settings.AI_MAX_RETRIES + 1):
            try:
                message = self.client.messages.create(
                    model=settings.AI_MODEL,
                    max_tokens=settings.AI_MAX_TOKENS,
                    temperature=settings.AI_TEMPERATURE,
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
                
                # Validate we have 3-5 suggestions
                if len(suggestions) < 3 or len(suggestions) > 5:
                    if attempt < settings.AI_MAX_RETRIES:
                        # Retry if count is wrong
                        continue
                    # On last attempt, accept what we have if >= 3
                    if len(suggestions) < 3:
                        raise ValueError(f"Claude retornó {len(suggestions)} visualizaciones, se esperaban entre 3 y 5")
                
                # Validate column names exist in metadata
                for suggestion in suggestions:
                    params = suggestion.parameters
                    if "x_axis" in params and params["x_axis"] not in available_columns:
                        raise ValueError(f"Columna inválida en x_axis: {params['x_axis']}")
                    if "y_axis" in params and params["y_axis"] not in available_columns:
                        raise ValueError(f"Columna inválida en y_axis: {params['y_axis']}")
                    # Validate x_axis != y_axis for charts that use both
                    if "x_axis" in params and "y_axis" in params and params["x_axis"] == params["y_axis"]:
                        raise ValueError(f"x_axis y y_axis no pueden ser la misma columna: {params['x_axis']}")

                return suggestions
                
            except (json.JSONDecodeError, ValidationError, ValueError) as e:
                if attempt < settings.AI_MAX_RETRIES:
                    # Retry
                    continue
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Claude retornó respuesta inválida después de {settings.AI_MAX_RETRIES + 1} intentos: {str(e)}. Respuesta: {response_text[:200]}"
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


# Singleton instance
ai_service = AIService()
