"""
Test Suite for GameDev AI Solutions MVP
Demonstrates testing practices and validates core functionality
"""

import pytest
import requests
import json
import time
from fastapi.testclient import TestClient
from gamedev_ai_mvp import app, AIAssetGenerator, AIDebugAssistant

# Create test client
client = TestClient(app)

class TestAPIEndpoints:
    """Test API endpoints functionality"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns correct information"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "0.1.0"
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_asset_generation_valid_request(self):
        """Test asset generation with valid parameters"""
        request_data = {
            "prompt": "medieval castle texture",
            "asset_type": "texture",
            "style": "realistic",
            "dimensions": "256x256"
        }
        
        response = client.post("/api/v1/generate-asset", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "asset_id" in data
        assert "asset_url" in data
        assert "metadata" in data
        assert "generation_time" in data
        assert isinstance(data["generation_time"], float)
    
    def test_asset_generation_invalid_type(self):
        """Test asset generation with invalid asset type"""
        request_data = {
            "prompt": "test prompt",
            "asset_type": "invalid_type",
            "style": "realistic",
            "dimensions": "256x256"
        }
        
        response = client.post("/api/v1/generate-asset", json=request_data)
        assert response.status_code == 400
        assert "Unsupported asset type" in response.json()["detail"]
    
    def test_debug_assistance(self):
        """Test debugging assistance functionality"""
        request_data = {
            "error_message": "NullReferenceException: Object reference not set",
            "engine_type": "unity"
        }
        
        response = client.post("/api/v1/debug", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "session_id" in data
        assert "error_analysis" in data
        assert "suggested_solutions" in data
        assert isinstance(data["suggested_solutions"], list)
    
    def test_asset_history(self):
        """Test asset history retrieval"""
        response = client.get("/api/v1/assets?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert "assets" in data
        assert "total" in data
        assert isinstance(data["assets"], list)

class TestAIAssetGenerator:
    """Test AI Asset Generator core functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.generator = AIAssetGenerator()
    
    def test_supported_asset_types(self):
        """Test that all expected asset types are supported"""
        expected_types = ["texture", "sprite", "icon", "background"]
        assert self.generator.supported_types == expected_types
    
    def test_color_analysis(self):
        """Test prompt color analysis"""
        colors = self.generator._analyze_prompt_colors("red dragon with blue flames")
        assert len(colors) > 0
        assert (255, 0, 0) in colors  # Red
        assert (0, 0, 255) in colors  # Blue
    
    def test_shape_analysis(self):
        """Test prompt shape analysis"""
        shapes = self.generator._analyze_prompt_shapes("circular shield with square gems")
        assert "circle" in shapes
        assert "square" in shapes
    
    def test_asset_generation_performance(self):
        """Test asset generation performance"""
        start_time = time.time()
        
        result = self.generator.generate_asset(
            prompt="test texture",
            asset_type="texture",
            style="realistic",
            dimensions="128x128"
        )
        
        generation_time = time.time() - start_time
        
        # Should generate asset in reasonable time (< 5 seconds for MVP)
        assert generation_time < 5.0
        assert "asset_id" in result
        assert "metadata" in result
    
    def test_different_asset_types(self):
        """Test generation of different asset types"""
        asset_types = ["texture", "sprite", "icon", "background"]
        
        for asset_type in asset_types:
            result = self.generator.generate_asset(
                prompt=f"test {asset_type}",
                asset_type=asset_type,
                style="realistic",
                dimensions="64x64"
            )
            
            assert result["metadata"]["asset_type"] == asset_type
            assert "asset_id" in result

class TestAIDebugAssistant:
    """Test AI Debug Assistant functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.assistant = AIDebugAssistant()
    
    def test_common_error_recognition(self):
        """Test recognition of common Unity errors"""
        error_message = "NullReferenceException: Object reference not set to an instance of an object"
        
        result = self.assistant.analyze_error(error_message, engine_type="unity")
        
        assert "session_id" in result
        assert "null object reference" in result["error_analysis"].lower()
        assert len(result["suggested_solutions"]) > 0
    
    def test_engine_specific_tips(self):
        """Test engine-specific debugging tips"""
        unity_tips = self.assistant._get_engine_specific_tips("unity")
        unreal_tips = self.assistant._get_engine_specific_tips("unreal")
        godot_tips = self.assistant._get_engine_specific_tips("godot")
        
        assert "Debug.Log" in str(unity_tips)
        assert "UE_LOG" in str(unreal_tips)
        assert "print()" in str(godot_tips)
    
    def test_unknown_error_handling(self):
        """Test handling of unknown error types"""
        result = self.assistant.analyze_error("Some unknown error occurred")
        
        assert result["error_analysis"] == "Unknown error type"
        assert len(result["suggested_solutions"]) > 0

class TestDataStructuresAndAlgorithms:
    """Test implementation of CS concepts"""
    
    def test_hash_generation_uniqueness(self):
        """Test that asset IDs are unique"""
        generator = AIAssetGenerator()
        
        ids = set()
        for i in range(100):
            result = generator.generate_asset(
                prompt=f"test prompt {i}",
                asset_type="texture",
                style="realistic",
                dimensions="32x32"
            )
            asset_id = result["asset_id"]
            assert asset_id not in ids  # Should be unique
            ids.add(asset_id)
    
    def test_color_palette_extraction(self):
        """Test color palette extraction algorithm"""
        from PIL import Image
        generator = AIAssetGenerator()
        
        # Create test image
        image = Image.new('RGBA', (100, 100), (255, 0, 0, 255))  # Red image
        
        palette = generator._extract_color_palette(image)
        assert len(palette) > 0
        assert isinstance(palette[0], str)
        assert palette[0].startswith("#")  # Hex color format

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_malformed_requests(self):
        """Test handling of malformed API requests"""
        # Missing required fields
        response = client.post("/api/v1/generate-asset", json={})
        assert response.status_code == 422  # Validation error
        
        # Invalid JSON
        response = client.post("/api/v1/generate-asset", data="invalid json")
        assert response.status_code == 422
    
    def test_extreme_dimensions(self):
        """Test handling of extreme dimension requests"""
        request_data = {
            "prompt": "test",
            "asset_type": "texture",
            "style": "realistic",
            "dimensions": "10000x10000"  # Very large
        }
        
        # Should handle gracefully (may take longer but shouldn't crash)
        response = client.post("/api/v1/generate-asset", json=request_data)
        # Accept either success or controlled failure
        assert response.status_code in [200, 400, 500]

# Performance benchmarks
class TestPerformance:
    """Test performance characteristics"""
    
    def test_concurrent_asset_generation(self):
        """Test handling of multiple concurrent requests"""
        import threading
        import time
        
        results = []
        
        def generate_asset():
            request_data = {
                "prompt": "test concurrent",
                "asset_type": "texture",
                "style": "realistic",
                "dimensions": "64x64"
            }
            response = client.post("/api/v1/generate-asset", json=request_data)
            results.append(response.status_code)
        
        # Create 5 concurrent threads
        threads = []
        start_time = time.time()
        
        for _ in range(5):
            thread = threading.Thread(target=generate_asset)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        # Should complete in reasonable time
        assert total_time < 30.0  # 30 seconds for 5 concurrent requests

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
