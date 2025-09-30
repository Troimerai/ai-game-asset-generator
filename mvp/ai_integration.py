"""
AI Integration Module - Real AI Model Integration
Supports OpenAI DALL-E and Stable Diffusion APIs
"""

import os
import requests
import base64
import io
from PIL import Image
from typing import Optional, Dict, Any
import openai
from dataclasses import dataclass
import time
import hashlib

@dataclass
class AIGenerationRequest:
    prompt: str
    style: str = "realistic"
    dimensions: str = "512x512"
    model_preference: str = "dalle"  # "dalle" or "stable_diffusion"
    quality: str = "standard"  # "standard" or "hd" for DALL-E

class RealAIAssetGenerator:
    """
    Real AI Asset Generator using actual AI models
    Integrates with OpenAI DALL-E and Stable Diffusion APIs
    """
    
    def __init__(self):
        # API Keys (should be set as environment variables)
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.stability_api_key = os.getenv('STABILITY_API_KEY')
        
        # Initialize OpenAI client
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        # Stable Diffusion API endpoint
        self.stability_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        
        # Style mappings for different AI models
        self.dalle_style_prompts = {
            "realistic": "photorealistic, high quality, detailed",
            "cartoon": "cartoon style, animated, colorful",
            "pixel": "pixel art style, 8-bit, retro gaming",
            "minimalist": "minimalist design, clean, simple"
        }
        
        self.sd_style_prompts = {
            "realistic": "photorealistic, ultra detailed, 8k resolution",
            "cartoon": "cartoon illustration, vibrant colors, stylized",
            "pixel": "pixel art, 16-bit style, game sprite",
            "minimalist": "minimalist art, clean design, geometric"
        }

    def generate_with_dalle(self, request: AIGenerationRequest) -> Dict[str, Any]:
        """Generate asset using OpenAI DALL-E"""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        # Enhance prompt with style
        style_enhancement = self.dalle_style_prompts.get(request.style, "")
        enhanced_prompt = f"{request.prompt}, {style_enhancement}, game asset"
        
        try:
            # Parse dimensions
            width, height = map(int, request.dimensions.split('x'))
            size = f"{width}x{height}" if width == height else "1024x1024"
            
            # Generate image using DALL-E 3
            response = openai.Image.create(
                model="dall-e-3",
                prompt=enhanced_prompt,
                size=size,
                quality=request.quality,
                n=1
            )
            
            # Download the generated image
            image_url = response.data[0].url
            image_response = requests.get(image_url)
            image = Image.open(io.BytesIO(image_response.content))
            
            # Generate unique ID
            asset_id = hashlib.md5(f"dalle_{enhanced_prompt}_{time.time()}".encode()).hexdigest()[:12]
            
            return {
                "success": True,
                "asset_id": asset_id,
                "image": image,
                "model_used": "dall-e-3",
                "prompt_used": enhanced_prompt,
                "original_url": image_url,
                "generation_time": time.time()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model_used": "dall-e-3"
            }

    def generate_with_stable_diffusion(self, request: AIGenerationRequest) -> Dict[str, Any]:
        """Generate asset using Stability AI Stable Diffusion"""
        if not self.stability_api_key:
            raise ValueError("Stability AI API key not configured")
        
        # Enhance prompt with style
        style_enhancement = self.sd_style_prompts.get(request.style, "")
        enhanced_prompt = f"{request.prompt}, {style_enhancement}, game asset, high quality"
        
        try:
            # Parse dimensions
            width, height = map(int, request.dimensions.split('x'))
            
            # Prepare request data
            data = {
                "text_prompts": [
                    {
                        "text": enhanced_prompt,
                        "weight": 1.0
                    }
                ],
                "cfg_scale": 7,
                "height": height,
                "width": width,
                "samples": 1,
                "steps": 30,
            }
            
            # Make API request
            response = requests.post(
                self.stability_url,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {self.stability_api_key}"
                },
                json=data
            )
            
            if response.status_code != 200:
                raise Exception(f"Stability AI API error: {response.status_code}")
            
            # Process response
            response_data = response.json()
            image_data = base64.b64decode(response_data["artifacts"][0]["base64"])
            image = Image.open(io.BytesIO(image_data))
            
            # Generate unique ID
            asset_id = hashlib.md5(f"sd_{enhanced_prompt}_{time.time()}".encode()).hexdigest()[:12]
            
            return {
                "success": True,
                "asset_id": asset_id,
                "image": image,
                "model_used": "stable-diffusion-xl",
                "prompt_used": enhanced_prompt,
                "generation_time": time.time()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model_used": "stable-diffusion-xl"
            }

    def generate_asset(self, request: AIGenerationRequest) -> Dict[str, Any]:
        """
        Main generation method that routes to appropriate AI model
        """
        start_time = time.time()
        
        try:
            if request.model_preference == "dalle" and self.openai_api_key:
                result = self.generate_with_dalle(request)
            elif request.model_preference == "stable_diffusion" and self.stability_api_key:
                result = self.generate_with_stable_diffusion(request)
            else:
                # Fallback to available model or procedural generation
                if self.openai_api_key:
                    result = self.generate_with_dalle(request)
                elif self.stability_api_key:
                    result = self.generate_with_stable_diffusion(request)
                else:
                    # Fallback to procedural generation from original MVP
                    from gamedev_ai_mvp import AIAssetGenerator
                    fallback_generator = AIAssetGenerator()
                    fallback_result = fallback_generator.generate_asset(
                        request.prompt, "texture", request.style, request.dimensions
                    )
                    return {
                        "success": True,
                        "asset_id": fallback_result["asset_id"],
                        "image": Image.open(fallback_result["file_path"]),
                        "model_used": "procedural_fallback",
                        "prompt_used": request.prompt,
                        "generation_time": time.time() - start_time,
                        "note": "Used procedural generation as AI APIs not configured"
                    }
            
            if result["success"]:
                result["total_generation_time"] = time.time() - start_time
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Generation failed: {str(e)}",
                "total_generation_time": time.time() - start_time
            }

    def get_available_models(self) -> Dict[str, bool]:
        """Check which AI models are available based on API keys"""
        return {
            "dall-e-3": bool(self.openai_api_key),
            "stable-diffusion-xl": bool(self.stability_api_key),
            "procedural_fallback": True
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize the real AI generator
    ai_generator = RealAIAssetGenerator()
    
    # Check available models
    available_models = ai_generator.get_available_models()
    print("Available AI Models:", available_models)
    
    # Example generation request
    request = AIGenerationRequest(
        prompt="fantasy sword with glowing blue runes",
        style="realistic",
        dimensions="512x512",
        model_preference="dalle"
    )
    
    # Generate asset
    result = ai_generator.generate_asset(request)
    
    if result["success"]:
        print(f"✅ Asset generated successfully!")
        print(f"Model used: {result['model_used']}")
        print(f"Asset ID: {result['asset_id']}")
        print(f"Generation time: {result['total_generation_time']:.2f}s")
        
        # Save the generated image
        if "image" in result:
            result["image"].save(f"generated_{result['asset_id']}.png")
            print(f"Image saved as: generated_{result['asset_id']}.png")
    else:
        print(f"❌ Generation failed: {result['error']}")
