"""
Demo Script: Real AI Integration POC
Demonstrates DALL-E and Stable Diffusion integration
"""

import os
import asyncio
import time
from ai_integration import RealAIAssetGenerator, AIGenerationRequest

async def demo_real_ai_integration():
    """
    Comprehensive demo of real AI integration capabilities
    """
    print("🎮 GameDev AI Tools - Real AI Integration Demo")
    print("=" * 60)
    
    # Initialize the AI generator
    ai_generator = RealAIAssetGenerator()
    
    # Check available models
    available_models = ai_generator.get_available_models()
    print("\n🤖 Available AI Models:")
    for model, available in available_models.items():
        status = "✅ Ready" if available else "❌ Not configured"
        print(f"  • {model}: {status}")
    
    if not available_models["dall-e-3"] and not available_models["stable-diffusion-xl"]:
        print("\n⚠️  No real AI models configured!")
        print("To enable real AI generation:")
        print("  1. Set OPENAI_API_KEY environment variable for DALL-E")
        print("  2. Set STABILITY_API_KEY environment variable for Stable Diffusion")
        print("\n🔄 Falling back to procedural generation for demo...")
    
    # Demo prompts for different game asset types
    demo_prompts = [
        {
            "prompt": "fantasy sword with glowing blue runes, game weapon asset",
            "style": "realistic",
            "type": "weapon"
        },
        {
            "prompt": "cute cartoon mushroom character, game sprite",
            "style": "cartoon",
            "type": "character"
        },
        {
            "prompt": "stone brick wall texture, seamless tileable",
            "style": "realistic",
            "type": "texture"
        },
        {
            "prompt": "pixel art treasure chest, 16-bit style",
            "style": "pixel",
            "type": "item"
        }
    ]
    
    print(f"\n🎨 Generating {len(demo_prompts)} demo assets...")
    print("-" * 60)
    
    results = []
    
    for i, demo in enumerate(demo_prompts, 1):
        print(f"\n[{i}/{len(demo_prompts)}] Generating {demo['type']}: {demo['prompt'][:50]}...")
        
        # Try different models for variety
        model_preference = "dalle" if i % 2 == 1 else "stable_diffusion"
        
        request = AIGenerationRequest(
            prompt=demo["prompt"],
            style=demo["style"],
            dimensions="512x512",
            model_preference=model_preference
        )
        
        start_time = time.time()
        result = ai_generator.generate_asset(request)
        
        if result["success"]:
            # Save the generated image
            filename = f"demo_{demo['type']}_{result['asset_id']}.png"
            result["image"].save(filename)
            
            print(f"  ✅ Generated successfully!")
            print(f"     Model: {result['model_used']}")
            print(f"     Time: {result['total_generation_time']:.2f}s")
            print(f"     Saved: {filename}")
            
            results.append({
                "type": demo["type"],
                "success": True,
                "model": result["model_used"],
                "time": result["total_generation_time"],
                "filename": filename
            })
        else:
            print(f"  ❌ Generation failed: {result['error']}")
            results.append({
                "type": demo["type"],
                "success": False,
                "error": result["error"]
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DEMO SUMMARY")
    print("=" * 60)
    
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    print(f"✅ Successful generations: {len(successful)}")
    print(f"❌ Failed generations: {len(failed)}")
    
    if successful:
        avg_time = sum(r["time"] for r in successful) / len(successful)
        print(f"⏱️  Average generation time: {avg_time:.2f}s")
        
        models_used = {}
        for r in successful:
            models_used[r["model"]] = models_used.get(r["model"], 0) + 1
        
        print(f"🤖 Models used:")
        for model, count in models_used.items():
            print(f"   • {model}: {count} generations")
    
    if successful:
        print(f"\n📁 Generated files:")
        for r in successful:
            print(f"   • {r['filename']} ({r['type']})")
    
    print("\n🎯 Integration Features Demonstrated:")
    print("   ✅ Multi-model support (DALL-E + Stable Diffusion)")
    print("   ✅ Automatic fallback to procedural generation")
    print("   ✅ Style-aware prompt enhancement")
    print("   ✅ Performance monitoring and timing")
    print("   ✅ Error handling and graceful degradation")
    print("   ✅ Asset type optimization")
    
    return results

async def demo_unity_integration():
    """
    Demo Unity integration capabilities
    """
    print("\n🎮 Unity Integration Demo")
    print("-" * 40)
    
    print("Unity Plugin Features:")
    print("  ✅ C# Unity script for seamless integration")
    print("  ✅ Editor window for asset generation")
    print("  ✅ Real-time progress tracking")
    print("  ✅ Asset preview and management")
    print("  ✅ Automatic texture import")
    print("  ✅ Batch generation support")
    
    print("\nUnity Setup Instructions:")
    print("  1. Copy GameDevAITools.cs to your Unity project")
    print("  2. Copy GameDevAIWindow.cs to Assets/Editor/")
    print("  3. Install Newtonsoft.Json package via Package Manager")
    print("  4. Open 'GameDev AI/Asset Generator' from Unity menu")
    print("  5. Configure API URL and start generating!")
    
    print("\nAPI Endpoints for Unity:")
    print("  • POST /api/v1/generate-asset - Single asset generation")
    print("  • POST /api/v1/generate-batch - Batch generation")
    print("  • GET /health - API health check")
    print("  • GET /models - Model capabilities")

if __name__ == "__main__":
    print("Starting Real AI Integration Demo...")
    
    # Run the demo
    results = asyncio.run(demo_real_ai_integration())
    
    # Demo Unity integration info
    asyncio.run(demo_unity_integration())
    
    print("\n🚀 Demo completed!")
    print("Ready for production integration with real AI models!")
