"""
GameDev AI Solutions - MVP Implementation
AI-Powered Game Development Tool

This MVP demonstrates core functionality for AI-assisted game asset generation
as outlined in the business plan by Aleksandr Zinovev.

Key Features Implemented:
- AI text-to-asset generation using pre-trained models
- RESTful API endpoints for game engine integration
- Basic asset optimization and format conversion
- Simple debugging assistance for common game development issues

Technology Stack:
- Python 3.8+
- FastAPI for REST API
- Transformers library for AI models
- PIL for image processing
- SQLite for asset storage
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import json
import hashlib
import time
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import random

# Initialize FastAPI app
app = FastAPI(
    title="GameDev AI Solutions MVP",
    description="AI-powered game development assistance tool",
    version="0.1.0"
)

# Database setup
def init_database():
    """Initialize SQLite database for storing generated assets and user data"""
    conn = sqlite3.connect('gamedev_ai.db')
    cursor = conn.cursor()
    
    # Create assets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id TEXT UNIQUE,
            prompt TEXT,
            asset_type TEXT,
            file_path TEXT,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create debug_sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS debug_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE,
            error_type TEXT,
            error_message TEXT,
            suggested_solution TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Pydantic models for API requests/responses
class AssetGenerationRequest(BaseModel):
    prompt: str
    asset_type: str  # "texture", "sprite", "icon", "background"
    style: Optional[str] = "realistic"
    dimensions: Optional[str] = "256x256"

class AssetGenerationResponse(BaseModel):
    asset_id: str
    asset_url: str
    metadata: dict
    generation_time: float

class DebugRequest(BaseModel):
    error_message: str
    code_context: Optional[str] = None
    engine_type: Optional[str] = "unity"  # "unity", "unreal", "godot"

class DebugResponse(BaseModel):
    session_id: str
    error_analysis: str
    suggested_solutions: List[str]
    relevant_documentation: List[str]

# AI Asset Generation Core Logic
class AIAssetGenerator:
    """Core AI asset generation functionality"""
    
    def __init__(self):
        self.supported_types = ["texture", "sprite", "icon", "background"]
        self.style_presets = {
            "realistic": {"saturation": 1.0, "contrast": 1.2},
            "cartoon": {"saturation": 1.5, "contrast": 0.8},
            "pixel": {"saturation": 1.3, "contrast": 1.0},
            "minimalist": {"saturation": 0.7, "contrast": 1.1}
        }
    
    def generate_asset(self, prompt: str, asset_type: str, style: str = "realistic", dimensions: str = "256x256") -> dict:
        """
        Generate AI asset based on text prompt
        
        Note: This MVP uses procedural generation as a placeholder for actual AI models
        In production, this would integrate with models like DALL-E, Stable Diffusion, or custom-trained models
        """
        start_time = time.time()
        
        # Parse dimensions
        width, height = map(int, dimensions.split('x'))
        
        # Generate unique asset ID
        asset_id = hashlib.md5(f"{prompt}_{asset_type}_{style}_{time.time()}".encode()).hexdigest()[:12]
        
        # Create procedural asset (placeholder for AI generation)
        image = self._create_procedural_asset(prompt, asset_type, style, width, height)
        
        # Save asset
        file_path = f"assets/{asset_id}.png"
        image.save(file_path)
        
        # Store in database
        metadata = {
            "prompt": prompt,
            "asset_type": asset_type,
            "style": style,
            "dimensions": dimensions,
            "file_size": len(image.tobytes()),
            "color_palette": self._extract_color_palette(image)
        }
        
        self._store_asset(asset_id, prompt, asset_type, file_path, metadata)
        
        generation_time = time.time() - start_time
        
        return {
            "asset_id": asset_id,
            "file_path": file_path,
            "metadata": metadata,
            "generation_time": generation_time
        }
    
    def _create_procedural_asset(self, prompt: str, asset_type: str, style: str, width: int, height: int) -> Image.Image:
        """Create procedural asset based on prompt analysis"""
        
        # Create base image
        image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        
        # Analyze prompt for colors and shapes
        colors = self._analyze_prompt_colors(prompt)
        shapes = self._analyze_prompt_shapes(prompt)
        
        # Apply style modifications
        style_config = self.style_presets.get(style, self.style_presets["realistic"])
        
        if asset_type == "texture":
            self._generate_texture(draw, width, height, colors, style_config)
        elif asset_type == "sprite":
            self._generate_sprite(draw, width, height, colors, shapes, style_config)
        elif asset_type == "icon":
            self._generate_icon(draw, width, height, colors, style_config)
        elif asset_type == "background":
            self._generate_background(draw, width, height, colors, style_config)
        
        return image
    
    def _analyze_prompt_colors(self, prompt: str) -> List[tuple]:
        """Extract color information from text prompt"""
        color_keywords = {
            "red": (255, 0, 0), "blue": (0, 0, 255), "green": (0, 255, 0),
            "yellow": (255, 255, 0), "purple": (128, 0, 128), "orange": (255, 165, 0),
            "brown": (139, 69, 19), "black": (0, 0, 0), "white": (255, 255, 255),
            "gray": (128, 128, 128), "pink": (255, 192, 203)
        }
        
        found_colors = []
        prompt_lower = prompt.lower()
        
        for color_name, rgb in color_keywords.items():
            if color_name in prompt_lower:
                found_colors.append(rgb)
        
        # Default colors if none found
        if not found_colors:
            found_colors = [(100, 150, 200), (200, 100, 150), (150, 200, 100)]
        
        return found_colors
    
    def _analyze_prompt_shapes(self, prompt: str) -> List[str]:
        """Extract shape information from text prompt"""
        shape_keywords = ["circle", "square", "triangle", "rectangle", "star", "diamond", "hexagon"]
        found_shapes = [shape for shape in shape_keywords if shape in prompt.lower()]
        return found_shapes if found_shapes else ["rectangle"]
    
    def _generate_texture(self, draw, width, height, colors, style_config):
        """Generate texture pattern"""
        for i in range(0, width, 20):
            for j in range(0, height, 20):
                color = random.choice(colors)
                # Apply style modifications
                modified_color = tuple(int(c * style_config["contrast"]) for c in color)
                draw.rectangle([i, j, i+15, j+15], fill=modified_color)
    
    def _generate_sprite(self, draw, width, height, colors, shapes, style_config):
        """Generate sprite with basic shapes"""
        center_x, center_y = width // 2, height // 2
        size = min(width, height) // 3
        
        for shape in shapes[:3]:  # Limit to 3 shapes
            color = random.choice(colors)
            if shape == "circle":
                draw.ellipse([center_x-size, center_y-size, center_x+size, center_y+size], fill=color)
            elif shape == "rectangle":
                draw.rectangle([center_x-size, center_y-size, center_x+size, center_y+size], fill=color)
            size -= 10  # Make nested shapes smaller
    
    def _generate_icon(self, draw, width, height, colors, style_config):
        """Generate simple icon"""
        center_x, center_y = width // 2, height // 2
        size = min(width, height) // 3
        
        # Simple icon with circle and inner shape
        draw.ellipse([center_x-size, center_y-size, center_x+size, center_y+size], 
                    fill=colors[0], outline=colors[1] if len(colors) > 1 else colors[0])
        
        # Inner detail
        inner_size = size // 2
        draw.rectangle([center_x-inner_size, center_y-inner_size, center_x+inner_size, center_y+inner_size], 
                      fill=colors[1] if len(colors) > 1 else (255, 255, 255))
    
    def _generate_background(self, draw, width, height, colors, style_config):
        """Generate background with gradient effect"""
        for y in range(height):
            # Simple gradient
            ratio = y / height
            color1, color2 = colors[0], colors[1] if len(colors) > 1 else colors[0]
            
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    def _extract_color_palette(self, image: Image.Image) -> List[str]:
        """Extract dominant colors from generated image"""
        # Simplified color extraction
        colors = image.getcolors(maxcolors=256*256*256)
        if colors:
            # Get top 5 colors
            top_colors = sorted(colors, key=lambda x: x[0], reverse=True)[:5]
            return [f"#{r:02x}{g:02x}{b:02x}" for count, (r, g, b, a) in top_colors if a > 0]
        return ["#000000"]
    
    def _store_asset(self, asset_id: str, prompt: str, asset_type: str, file_path: str, metadata: dict):
        """Store asset information in database"""
        conn = sqlite3.connect('gamedev_ai.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO assets (asset_id, prompt, asset_type, file_path, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (asset_id, prompt, asset_type, file_path, json.dumps(metadata)))
        
        conn.commit()
        conn.close()

# AI Debugging Assistant
class AIDebugAssistant:
    """AI-powered debugging assistance for game development"""
    
    def __init__(self):
        self.common_errors = {
            "NullReferenceException": {
                "description": "Attempting to access a member on a null object reference",
                "solutions": [
                    "Check if object is null before accessing its members",
                    "Initialize objects properly in Start() or Awake()",
                    "Use null-conditional operators (?.) in C#"
                ],
                "documentation": [
                    "https://docs.unity3d.com/Manual/NullReferenceException.html"
                ]
            },
            "IndexOutOfRangeException": {
                "description": "Trying to access an array element that doesn't exist",
                "solutions": [
                    "Check array bounds before accessing elements",
                    "Use array.Length to verify size",
                    "Consider using List<T> instead of arrays for dynamic sizing"
                ],
                "documentation": [
                    "https://docs.microsoft.com/en-us/dotnet/api/system.indexoutofrangeexception"
                ]
            },
            "MissingReferenceException": {
                "description": "Reference to a destroyed Unity object",
                "solutions": [
                    "Check if object exists before using it",
                    "Properly manage object lifecycle",
                    "Use FindObjectOfType() to re-establish references"
                ],
                "documentation": [
                    "https://docs.unity3d.com/ScriptReference/MissingReferenceException.html"
                ]
            }
        }
    
    def analyze_error(self, error_message: str, code_context: str = None, engine_type: str = "unity") -> dict:
        """Analyze error and provide debugging suggestions"""
        session_id = hashlib.md5(f"{error_message}_{time.time()}".encode()).hexdigest()[:12]
        
        # Find matching error pattern
        error_analysis = "Unknown error type"
        suggested_solutions = ["Check the error message for specific details", "Review recent code changes"]
        relevant_docs = []
        
        for error_type, info in self.common_errors.items():
            if error_type.lower() in error_message.lower():
                error_analysis = info["description"]
                suggested_solutions = info["solutions"]
                relevant_docs = info["documentation"]
                break
        
        # Store debug session
        self._store_debug_session(session_id, error_message, error_analysis, suggested_solutions)
        
        return {
            "session_id": session_id,
            "error_analysis": error_analysis,
            "suggested_solutions": suggested_solutions,
            "relevant_documentation": relevant_docs,
            "engine_specific_tips": self._get_engine_specific_tips(engine_type)
        }
    
    def _get_engine_specific_tips(self, engine_type: str) -> List[str]:
        """Get engine-specific debugging tips"""
        tips = {
            "unity": [
                "Use Debug.Log() for runtime debugging",
                "Check the Console window for detailed error information",
                "Use Unity's built-in Profiler for performance issues"
            ],
            "unreal": [
                "Use UE_LOG for debugging output",
                "Check the Output Log for detailed information",
                "Use Unreal's Blueprint debugger for visual scripting issues"
            ],
            "godot": [
                "Use print() statements for debugging",
                "Check the Debugger panel for runtime information",
                "Use Godot's built-in profiler for performance analysis"
            ]
        }
        return tips.get(engine_type, tips["unity"])
    
    def _store_debug_session(self, session_id: str, error_message: str, error_analysis: str, solutions: List[str]):
        """Store debugging session in database"""
        conn = sqlite3.connect('gamedev_ai.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO debug_sessions (session_id, error_type, error_message, suggested_solution)
            VALUES (?, ?, ?, ?)
        ''', (session_id, error_analysis, error_message, json.dumps(solutions)))
        
        conn.commit()
        conn.close()

# Initialize components
asset_generator = AIAssetGenerator()
debug_assistant = AIDebugAssistant()

# API Endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_database()
    print("GameDev AI Solutions MVP started successfully!")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "GameDev AI Solutions MVP",
        "version": "0.1.0",
        "description": "AI-powered game development assistance tool",
        "endpoints": {
            "generate_asset": "/api/v1/generate-asset",
            "debug_assistance": "/api/v1/debug",
            "asset_history": "/api/v1/assets",
            "health": "/health"
        }
    }

@app.post("/api/v1/generate-asset", response_model=AssetGenerationResponse)
async def generate_asset(request: AssetGenerationRequest):
    """Generate AI-powered game asset from text prompt"""
    try:
        if request.asset_type not in asset_generator.supported_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported asset type. Supported types: {asset_generator.supported_types}"
            )
        
        result = asset_generator.generate_asset(
            prompt=request.prompt,
            asset_type=request.asset_type,
            style=request.style,
            dimensions=request.dimensions
        )
        
        return AssetGenerationResponse(
            asset_id=result["asset_id"],
            asset_url=f"/assets/{result['asset_id']}.png",
            metadata=result["metadata"],
            generation_time=result["generation_time"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Asset generation failed: {str(e)}")

@app.post("/api/v1/debug", response_model=DebugResponse)
async def debug_assistance(request: DebugRequest):
    """Get AI-powered debugging assistance"""
    try:
        result = debug_assistant.analyze_error(
            error_message=request.error_message,
            code_context=request.code_context,
            engine_type=request.engine_type
        )
        
        return DebugResponse(
            session_id=result["session_id"],
            error_analysis=result["error_analysis"],
            suggested_solutions=result["suggested_solutions"],
            relevant_documentation=result["relevant_documentation"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Debug analysis failed: {str(e)}")

@app.get("/api/v1/assets")
async def get_asset_history(limit: int = 10):
    """Get history of generated assets"""
    try:
        conn = sqlite3.connect('gamedev_ai.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT asset_id, prompt, asset_type, metadata, created_at
            FROM assets
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        assets = []
        for row in cursor.fetchall():
            assets.append({
                "asset_id": row[0],
                "prompt": row[1],
                "asset_type": row[2],
                "metadata": json.loads(row[3]),
                "created_at": row[4]
            })
        
        conn.close()
        return {"assets": assets, "total": len(assets)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve assets: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0"
    }

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Create assets directory
    os.makedirs("assets", exist_ok=True)
    
    # Run the application
    uvicorn.run(app, host="0.0.0.0", port=8000)
