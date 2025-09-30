"""
Enhanced FastAPI Backend with Real AI Integration
Supports OpenAI DALL-E and Stable Diffusion APIs
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import base64
import io
from PIL import Image
import time
import os
from ai_integration import RealAIAssetGenerator, AIGenerationRequest

# Initialize FastAPI app
app = FastAPI(
    title="GameDev AI Tools API",
    description="AI-powered game development tools with real AI model integration",
    version="2.0.0"
)

# Add CORS middleware for Unity integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI generator
ai_generator = RealAIAssetGenerator()

# Pydantic models for API
class EnhancedAssetRequest(BaseModel):
    prompt: str
    style: str = "realistic"
    dimensions: str = "512x512"
    model_preference: str = "dalle"  # "dalle", "stable_diffusion", or "procedural"
    quality: str = "standard"  # "standard" or "hd" for DALL-E

class EnhancedAssetResponse(BaseModel):
    success: bool
    asset_id: Optional[str] = None
    model_used: Optional[str] = None
    generation_time: Optional[float] = None
    prompt_used: Optional[str] = None
    image_base64: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    status: str
    available_models: Dict[str, bool]
    api_version: str
    timestamp: float

class ModelCapabilities(BaseModel):
    model_name: str
    available: bool
    supported_styles: list
    supported_dimensions: list
    max_prompt_length: int
    estimated_generation_time: str

def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string"""
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "GameDev AI Tools API",
        "version": "2.0.0",
        "documentation": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Enhanced health check with model availability"""
    available_models = ai_generator.get_available_models()
    
    return HealthResponse(
        status="healthy",
        available_models=available_models,
        api_version="2.0.0",
        timestamp=time.time()
    )

@app.get("/models", response_model=Dict[str, ModelCapabilities])
async def get_model_capabilities():
    """Get detailed information about available AI models"""
    available_models = ai_generator.get_available_models()
    
    capabilities = {}
    
    # DALL-E capabilities
    capabilities["dall-e-3"] = ModelCapabilities(
        model_name="DALL-E 3",
        available=available_models["dall-e-3"],
        supported_styles=["realistic", "cartoon", "minimalist"],
        supported_dimensions=["1024x1024", "1792x1024", "1024x1792"],
        max_prompt_length=4000,
        estimated_generation_time="10-30 seconds"
    )
    
    # Stable Diffusion capabilities
    capabilities["stable-diffusion-xl"] = ModelCapabilities(
        model_name="Stable Diffusion XL",
        available=available_models["stable-diffusion-xl"],
        supported_styles=["realistic", "cartoon", "pixel", "minimalist"],
        supported_dimensions=["512x512", "768x768", "1024x1024"],
        max_prompt_length=2000,
        estimated_generation_time="5-15 seconds"
    )
    
    # Procedural fallback
    capabilities["procedural"] = ModelCapabilities(
        model_name="Procedural Generator",
        available=available_models["procedural_fallback"],
        supported_styles=["realistic", "cartoon", "pixel", "minimalist"],
        supported_dimensions=["256x256", "512x512", "1024x1024"],
        max_prompt_length=500,
        estimated_generation_time="1-3 seconds"
    )
    
    return capabilities

@app.post("/api/v1/generate-asset", response_model=EnhancedAssetResponse)
async def generate_enhanced_asset(request: EnhancedAssetRequest):
    """
    Generate game asset using real AI models
    Supports DALL-E, Stable Diffusion, and procedural fallback
    """
    try:
        # Validate request
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        if len(request.prompt) > 4000:
            raise HTTPException(status_code=400, detail="Prompt too long (max 4000 characters)")
        
        # Create AI generation request
        ai_request = AIGenerationRequest(
            prompt=request.prompt,
            style=request.style,
            dimensions=request.dimensions,
            model_preference=request.model_preference,
            quality=request.quality
        )
        
        # Generate asset using AI
        result = ai_generator.generate_asset(ai_request)
        
        if result["success"]:
            # Convert image to base64 for API response
            image_base64 = image_to_base64(result["image"])
            
            # Prepare metadata
            metadata = {
                "dimensions": request.dimensions,
                "style": request.style,
                "quality": request.quality,
                "model_preference": request.model_preference
            }
            
            # Add model-specific metadata if available
            if "note" in result:
                metadata["note"] = result["note"]
            
            return EnhancedAssetResponse(
                success=True,
                asset_id=result["asset_id"],
                model_used=result["model_used"],
                generation_time=result["total_generation_time"],
                prompt_used=result["prompt_used"],
                image_base64=image_base64,
                metadata=metadata
            )
        else:
            return EnhancedAssetResponse(
                success=False,
                error=result["error"],
                metadata={"model_attempted": result.get("model_used", "unknown")}
            )
    
    except HTTPException:
        raise
    except Exception as e:
        return EnhancedAssetResponse(
            success=False,
            error=f"Internal server error: {str(e)}"
        )

@app.post("/api/v1/generate-batch")
async def generate_batch_assets(requests: list[EnhancedAssetRequest]):
    """
    Generate multiple assets in batch
    Useful for generating variations or multiple assets at once
    """
    if len(requests) > 5:  # Limit batch size
        raise HTTPException(status_code=400, detail="Batch size limited to 5 requests")
    
    results = []
    
    for i, request in enumerate(requests):
        try:
            # Add batch identifier to prompt
            batch_prompt = f"{request.prompt} (batch {i+1}/{len(requests)})"
            
            ai_request = AIGenerationRequest(
                prompt=batch_prompt,
                style=request.style,
                dimensions=request.dimensions,
                model_preference=request.model_preference,
                quality=request.quality
            )
            
            result = ai_generator.generate_asset(ai_request)
            
            if result["success"]:
                image_base64 = image_to_base64(result["image"])
                
                results.append(EnhancedAssetResponse(
                    success=True,
                    asset_id=result["asset_id"],
                    model_used=result["model_used"],
                    generation_time=result["total_generation_time"],
                    prompt_used=result["prompt_used"],
                    image_base64=image_base64,
                    metadata={"batch_index": i}
                ))
            else:
                results.append(EnhancedAssetResponse(
                    success=False,
                    error=result["error"],
                    metadata={"batch_index": i}
                ))
                
        except Exception as e:
            results.append(EnhancedAssetResponse(
                success=False,
                error=f"Batch item {i+1} failed: {str(e)}",
                metadata={"batch_index": i}
            ))
    
    return {"batch_results": results, "total_processed": len(results)}

@app.get("/api/v1/usage-stats")
async def get_usage_stats():
    """
    Get API usage statistics
    Useful for monitoring and analytics
    """
    # In a real implementation, this would query a database
    # For now, return mock data
    return {
        "total_generations": 0,
        "models_used": {
            "dall-e-3": 0,
            "stable-diffusion-xl": 0,
            "procedural": 0
        },
        "average_generation_time": 0.0,
        "popular_styles": {
            "realistic": 0,
            "cartoon": 0,
            "pixel": 0,
            "minimalist": 0
        }
    }

# Include original endpoints for backward compatibility
from gamedev_ai_mvp import app as original_app

# Mount original endpoints
@app.get("/api/v1/assets")
async def get_asset_history(limit: int = 10):
    """Get history of generated assets (backward compatibility)"""
    return {"message": "Asset history feature - implement database integration"}

if __name__ == "__main__":
    import uvicorn
    
    # Check for API keys
    print("🚀 Starting GameDev AI Tools API v2.0.0")
    print("=" * 50)
    
    available_models = ai_generator.get_available_models()
    print("Available AI Models:")
    for model, available in available_models.items():
        status = "✅" if available else "❌"
        print(f"  {status} {model}")
    
    if not any(available_models.values()):
        print("\n⚠️  Warning: No AI models configured!")
        print("Set environment variables:")
        print("  - OPENAI_API_KEY for DALL-E")
        print("  - STABILITY_API_KEY for Stable Diffusion")
        print("  - Procedural generation will be used as fallback")
    
    print("\n🌐 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
