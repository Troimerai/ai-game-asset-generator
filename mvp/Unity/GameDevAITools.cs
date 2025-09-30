using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;

namespace GameDevAI
{
    /// <summary>
    /// Unity Plugin for GameDev AI Tools
    /// Provides seamless integration with AI asset generation API
    /// </summary>
    public class GameDevAITools : MonoBehaviour
    {
        [Header("API Configuration")]
        public string apiBaseUrl = "http://localhost:8000/api/v1";
        public string apiKey = "";
        
        [Header("Generation Settings")]
        public AIModel preferredModel = AIModel.DALLE;
        public AssetStyle defaultStyle = AssetStyle.Realistic;
        public AssetDimensions defaultDimensions = AssetDimensions._512x512;
        
        [Header("Debug")]
        public bool enableDebugLogs = true;
        
        // Events for UI callbacks
        public static event Action<GeneratedAsset> OnAssetGenerated;
        public static event Action<string> OnGenerationFailed;
        public static event Action<float> OnGenerationProgress;
        
        private Queue<AssetRequest> requestQueue = new Queue<AssetRequest>();
        private bool isProcessing = false;
        
        public enum AIModel
        {
            DALLE,
            StableDiffusion,
            Procedural
        }
        
        public enum AssetStyle
        {
            Realistic,
            Cartoon,
            Pixel,
            Minimalist
        }
        
        public enum AssetDimensions
        {
            _256x256,
            _512x512,
            _1024x1024
        }
        
        [Serializable]
        public class AssetRequest
        {
            public string prompt;
            public AIModel model;
            public AssetStyle style;
            public AssetDimensions dimensions;
            public Action<GeneratedAsset> onSuccess;
            public Action<string> onFailure;
            
            public AssetRequest(string prompt, Action<GeneratedAsset> onSuccess = null, Action<string> onFailure = null)
            {
                this.prompt = prompt;
                this.onSuccess = onSuccess;
                this.onFailure = onFailure;
            }
        }
        
        [Serializable]
        public class GeneratedAsset
        {
            public string assetId;
            public string modelUsed;
            public float generationTime;
            public Texture2D texture;
            public string promptUsed;
        }
        
        [Serializable]
        public class APIRequest
        {
            public string prompt;
            public string style;
            public string dimensions;
            public string model_preference;
            public string quality = "standard";
        }
        
        [Serializable]
        public class APIResponse
        {
            public bool success;
            public string asset_id;
            public string model_used;
            public float generation_time;
            public string prompt_used;
            public string error;
            public string image_base64;
        }
        
        void Start()
        {
            if (enableDebugLogs)
                Debug.Log("[GameDevAI] Plugin initialized");
        }
        
        /// <summary>
        /// Generate an asset with specified parameters
        /// </summary>
        public void GenerateAsset(string prompt, Action<GeneratedAsset> onSuccess = null, Action<string> onFailure = null)
        {
            var request = new AssetRequest(prompt, onSuccess, onFailure)
            {
                model = preferredModel,
                style = defaultStyle,
                dimensions = defaultDimensions
            };
            
            QueueRequest(request);
        }
        
        /// <summary>
        /// Generate an asset with custom settings
        /// </summary>
        public void GenerateAsset(string prompt, AIModel model, AssetStyle style, AssetDimensions dimensions, 
            Action<GeneratedAsset> onSuccess = null, Action<string> onFailure = null)
        {
            var request = new AssetRequest(prompt, onSuccess, onFailure)
            {
                model = model,
                style = style,
                dimensions = dimensions
            };
            
            QueueRequest(request);
        }
        
        private void QueueRequest(AssetRequest request)
        {
            requestQueue.Enqueue(request);
            
            if (!isProcessing)
            {
                StartCoroutine(ProcessRequestQueue());
            }
        }
        
        private IEnumerator ProcessRequestQueue()
        {
            isProcessing = true;
            
            while (requestQueue.Count > 0)
            {
                var request = requestQueue.Dequeue();
                yield return StartCoroutine(ProcessSingleRequest(request));
                
                // Small delay between requests to avoid overwhelming the API
                yield return new WaitForSeconds(0.5f);
            }
            
            isProcessing = false;
        }
        
        private IEnumerator ProcessSingleRequest(AssetRequest request)
        {
            if (enableDebugLogs)
                Debug.Log($"[GameDevAI] Generating asset: {request.prompt}");
            
            OnGenerationProgress?.Invoke(0.1f);
            
            // Prepare API request
            var apiRequest = new APIRequest
            {
                prompt = request.prompt,
                style = request.style.ToString().ToLower(),
                dimensions = GetDimensionsString(request.dimensions),
                model_preference = GetModelString(request.model)
            };
            
            string jsonData = JsonConvert.SerializeObject(apiRequest);
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
            
            OnGenerationProgress?.Invoke(0.3f);
            
            // Make API request
            using (UnityWebRequest www = new UnityWebRequest($"{apiBaseUrl}/generate-asset", "POST"))
            {
                www.uploadHandler = new UploadHandlerRaw(bodyRaw);
                www.downloadHandler = new DownloadHandlerBuffer();
                www.SetRequestHeader("Content-Type", "application/json");
                
                if (!string.IsNullOrEmpty(apiKey))
                {
                    www.SetRequestHeader("Authorization", $"Bearer {apiKey}");
                }
                
                OnGenerationProgress?.Invoke(0.5f);
                
                yield return www.SendWebRequest();
                
                OnGenerationProgress?.Invoke(0.8f);
                
                if (www.result == UnityWebRequest.Result.Success)
                {
                    try
                    {
                        var response = JsonConvert.DeserializeObject<APIResponse>(www.downloadHandler.text);
                        
                        if (response.success)
                        {
                            // Convert base64 image to texture
                            var texture = Base64ToTexture(response.image_base64);
                            
                            var generatedAsset = new GeneratedAsset
                            {
                                assetId = response.asset_id,
                                modelUsed = response.model_used,
                                generationTime = response.generation_time,
                                texture = texture,
                                promptUsed = response.prompt_used
                            };
                            
                            OnGenerationProgress?.Invoke(1.0f);
                            
                            if (enableDebugLogs)
                                Debug.Log($"[GameDevAI] Asset generated successfully: {response.asset_id}");
                            
                            // Trigger callbacks
                            request.onSuccess?.Invoke(generatedAsset);
                            OnAssetGenerated?.Invoke(generatedAsset);
                        }
                        else
                        {
                            string error = $"API Error: {response.error}";
                            if (enableDebugLogs)
                                Debug.LogError($"[GameDevAI] {error}");
                            
                            request.onFailure?.Invoke(error);
                            OnGenerationFailed?.Invoke(error);
                        }
                    }
                    catch (Exception e)
                    {
                        string error = $"Failed to parse API response: {e.Message}";
                        if (enableDebugLogs)
                            Debug.LogError($"[GameDevAI] {error}");
                        
                        request.onFailure?.Invoke(error);
                        OnGenerationFailed?.Invoke(error);
                    }
                }
                else
                {
                    string error = $"Network Error: {www.error}";
                    if (enableDebugLogs)
                        Debug.LogError($"[GameDevAI] {error}");
                    
                    request.onFailure?.Invoke(error);
                    OnGenerationFailed?.Invoke(error);
                }
            }
        }
        
        private Texture2D Base64ToTexture(string base64String)
        {
            byte[] imageBytes = Convert.FromBase64String(base64String);
            Texture2D texture = new Texture2D(2, 2);
            texture.LoadImage(imageBytes);
            return texture;
        }
        
        private string GetDimensionsString(AssetDimensions dimensions)
        {
            switch (dimensions)
            {
                case AssetDimensions._256x256: return "256x256";
                case AssetDimensions._512x512: return "512x512";
                case AssetDimensions._1024x1024: return "1024x1024";
                default: return "512x512";
            }
        }
        
        private string GetModelString(AIModel model)
        {
            switch (model)
            {
                case AIModel.DALLE: return "dalle";
                case AIModel.StableDiffusion: return "stable_diffusion";
                case AIModel.Procedural: return "procedural";
                default: return "dalle";
            }
        }
        
        /// <summary>
        /// Check API health and available models
        /// </summary>
        public IEnumerator CheckAPIHealth(Action<bool> callback)
        {
            using (UnityWebRequest www = UnityWebRequest.Get($"{apiBaseUrl}/health"))
            {
                yield return www.SendWebRequest();
                
                bool isHealthy = www.result == UnityWebRequest.Result.Success;
                
                if (enableDebugLogs)
                {
                    if (isHealthy)
                        Debug.Log("[GameDevAI] API is healthy and ready");
                    else
                        Debug.LogWarning($"[GameDevAI] API health check failed: {www.error}");
                }
                
                callback?.Invoke(isHealthy);
            }
        }
    }
}
