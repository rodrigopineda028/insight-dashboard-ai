"""AI service for Claude integration and analysis."""
import json
import logging
import re
from typing import List

from anthropic import Anthropic
from fastapi import HTTPException
from pydantic import ValidationError

from app.config.settings import settings
from app.models.responses import ChartSuggestion

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered data analysis using Claude."""
    
    def __init__(self):
        """Initialize AI service with API key from settings."""
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not configured")
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    def _build_column_descriptions(self, metadata: dict, detailed: bool = True) -> List[str]:
        """Build column descriptions for prompts. Extracted to avoid duplication."""
        columns_desc = []
        for col in metadata["columns"]:
            col_name = col["name"]
            col_type = col["type"]
            cardinality = col.get("cardinality", 0)
            missingness = col.get("missingness_pct", 0)
            
            desc = f"- {col_name} ({col_type}) | Únicos: {cardinality}"
            
            if detailed and missingness > 0:
                desc += f" | Nulos: {missingness}%"
            
            if detailed and "stats" in col and col["stats"] is not None:
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
            elif not detailed and "stats" in col and col["stats"] is not None:
                # Simpler stats for query prompt
                stats = col["stats"]
                if stats.get("min") is not None:
                    desc += f" | Rango: [{stats['min']:.1f}, {stats['max']:.1f}]"
            
            columns_desc.append(desc)
        
        return columns_desc
    
    def build_analysis_prompt(self, metadata: dict) -> str:
        """Build optimized prompt for Claude to analyze dataset."""
        columns_desc = self._build_column_descriptions(metadata, detailed=True)
        
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
3. Line chart: SOLO para columnas de fecha/tiempo en x_axis. Perfecto para tendencias temporales
4. Scatter chart: SOLO para 2 columnas NUMÉRICAS (NO fechas/tiempo). Para correlaciones como Sales vs Quantity
5. Pie chart: Columna categórica con <10 categorías únicas
6. Bar chart: x_axis categórica, y_axis numérica con agregación
7. NUNCA uses la misma columna para x_axis y y_axis
8. Si tienes fecha/tiempo + valor numérico → SIEMPRE usa line chart (NUNCA scatter)
9. Si hay muchas categorías (>20), NO uses pie chart

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
                
                # Log suggestions for debugging
                logger.info(f"Claude suggested {len(suggestions)} charts:")
                for i, sug in enumerate(suggestions, 1):
                    logger.info(f"  {i}. {sug.title} | Type: {sug.chart_type} | X: {sug.parameters.get('x_axis')} | Y: {sug.parameters.get('y_axis')} | Agg: {sug.parameters.get('aggregation')}")
                
                # Validate we have 3-5 suggestions
                if len(suggestions) < 3 or len(suggestions) > 5:
                    if attempt < settings.AI_MAX_RETRIES:
                        # Retry if count is wrong
                        continue
                    # On last attempt, accept what we have if >= 3
                    if len(suggestions) < 3:
                        raise ValueError(f"Claude retornó {len(suggestions)} visualizaciones, se esperaban entre 3 y 5")
                
                # Build column type map for validation
                column_types = {col["name"]: col["type"] for col in metadata["columns"]}
                
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
                    
                    # Validate scatter chart doesn't use temporal columns
                    if suggestion.chart_type == "scatter":
                        x_col = params.get("x_axis", "")
                        y_col = params.get("y_axis", "")
                        x_type = column_types.get(x_col, "")
                        y_type = column_types.get(y_col, "")
                        
                        # Detect temporal columns
                        is_x_temporal = "date" in x_type.lower() or "time" in x_type.lower()
                        is_y_temporal = "date" in y_type.lower() or "time" in y_type.lower()
                        
                        if is_x_temporal or is_y_temporal:
                            raise ValueError(f"Scatter chart no soporta columnas temporales. Usa line chart para datos con fechas ({x_col} vs {y_col})")

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
    
    async def process_natural_language_query(self, metadata: dict, query: str) -> ChartSuggestion:
        """
        Process a natural language query and generate a single chart suggestion.
        
        Args:
            metadata: Dataset metadata including columns and sample data
            query: Natural language query from user
            
        Returns:
            ChartSuggestion object
            
        Raises:
            HTTPException: If query processing fails
        """
        # Reuse column description builder
        columns_desc = self._build_column_descriptions(metadata, detailed=False)
        
        prompt = f"""Eres un analista de datos experto. Un usuario tiene este dataset y hace una pregunta.

**Dataset Info:**
- Filas: {metadata['row_count']:,}
- Columnas: {metadata['column_count']}

**Columnas disponibles:**
{chr(10).join(columns_desc)}

**Muestra de datos:**
{json.dumps(metadata['sample_data'][:3], indent=2, ensure_ascii=False)}

**Pregunta del usuario:**
"{query}"

**Tu tarea:**
Interpreta la pregunta y genera UNA visualización que responda directamente.

**REGLAS:**
1. Usa SOLO las columnas listadas arriba
2. Tipos válidos: bar, line, pie, scatter
3. Line chart: Para datos temporales (fecha/tiempo en x_axis)
4. Scatter chart: SOLO para 2 columnas NUMÉRICAS (NO fechas). Para correlaciones
5. Pie chart: Columna categórica con <10 categorías
6. Bar chart: x_axis categórica, y_axis numérica
7. NUNCA uses la misma columna en x_axis y y_axis
8. Si pregunta por evolución/tendencia temporal → usa line chart (NO scatter)

**Responde SOLO con un objeto JSON (no array), SIN texto adicional:**
{{
  "title": "Título descriptivo basado en la pregunta",
  "chart_type": "bar",
  "parameters": {{
    "x_axis": "nombre_columna_exacto",
    "y_axis": "nombre_columna_exacto",
    "aggregation": "sum"
  }},
  "insight": "Explica brevemente qué responde esta visualización"
}}

Aggregation válida: sum, count, avg, none"""

        available_columns = {col["name"] for col in metadata["columns"]}
        
        try:
            message = self.client.messages.create(
                model=settings.AI_MODEL,
                max_tokens=settings.AI_MAX_TOKENS,
                temperature=settings.AI_TEMPERATURE,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response_text = message.content[0].text.strip()
            
            # Extract JSON if wrapped in markdown
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            
            # Parse and validate
            suggestion_data = json.loads(response_text)
            suggestion = ChartSuggestion(**suggestion_data)
            
            # Auto-fix: If suggested scatter with temporal column, convert to line chart
            column_types = {col["name"]: col["type"] for col in metadata["columns"]}
            if suggestion.chart_type == "scatter":
                x_col = suggestion.parameters.get("x_axis", "")
                x_type = column_types.get(x_col, "")
                
                if "date" in x_type.lower() or "time" in x_type.lower():
                    logger.warning(f"Auto-correcting: scatter → line for temporal data ({x_col})")
                    suggestion.chart_type = "line"
                    # Update title if it mentions correlation
                    if "correlación" in suggestion.title.lower():
                        suggestion.title = suggestion.title.replace("Correlación", "Evolución").replace("correlación", "evolución")
            
            # Log query result for debugging
            logger.info(f"Query '{query}' → {suggestion.title} | Type: {suggestion.chart_type} | X: {suggestion.parameters.get('x_axis')} | Y: {suggestion.parameters.get('y_axis')}")
            
            # Validate columns exist
            params = suggestion.parameters
            if "x_axis" in params and params["x_axis"] not in available_columns:
                raise ValueError(f"Columna inválida en x_axis: {params['x_axis']}")
            if "y_axis" in params and params["y_axis"] not in available_columns:
                raise ValueError(f"Columna inválida en y_axis: {params['y_axis']}")
            if "x_axis" in params and "y_axis" in params and params["x_axis"] == params["y_axis"]:
                raise ValueError(f"x_axis y y_axis no pueden ser iguales")
            
            return suggestion
            
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error procesando query: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error comunicándose con AI: {str(e)}"
            )


# Singleton instance
ai_service = AIService()
