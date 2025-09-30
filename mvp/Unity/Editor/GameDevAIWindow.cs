using UnityEngine;
using UnityEditor;
using System.Collections.Generic;

namespace GameDevAI.Editor
{
    /// <summary>
    /// Unity Editor Window for GameDev AI Tools
    /// Provides a user-friendly interface for generating AI assets
    /// </summary>
    public class GameDevAIWindow : EditorWindow
    {
        private string prompt = "";
        private GameDevAITools.AIModel selectedModel = GameDevAITools.AIModel.DALLE;
        private GameDevAITools.AssetStyle selectedStyle = GameDevAITools.AssetStyle.Realistic;
        private GameDevAITools.AssetDimensions selectedDimensions = GameDevAITools.AssetDimensions._512x512;
        
        private string apiUrl = "http://localhost:8000/api/v1";
        private string apiKey = "";
        
        private Vector2 scrollPosition;
        private List<GeneratedAssetInfo> generatedAssets = new List<GeneratedAssetInfo>();
        private bool isGenerating = false;
        private float generationProgress = 0f;
        private string statusMessage = "";
        
        private GameDevAITools aiTools;
        
        [System.Serializable]
        public class GeneratedAssetInfo
        {
            public string assetId;
            public string prompt;
            public Texture2D texture;
            public string modelUsed;
            public float generationTime;
            public System.DateTime timestamp;
        }
        
        [MenuItem("GameDev AI/Asset Generator")]
        public static void ShowWindow()
        {
            GameDevAIWindow window = GetWindow<GameDevAIWindow>();
            window.titleContent = new GUIContent("GameDev AI Tools");
            window.minSize = new Vector2(400, 600);
            window.Show();
        }
        
        void OnEnable()
        {
            // Subscribe to events
            GameDevAITools.OnAssetGenerated += OnAssetGenerated;
            GameDevAITools.OnGenerationFailed += OnGenerationFailed;
            GameDevAITools.OnGenerationProgress += OnGenerationProgress;
            
            // Load saved settings
            LoadSettings();
        }
        
        void OnDisable()
        {
            // Unsubscribe from events
            GameDevAITools.OnAssetGenerated -= OnAssetGenerated;
            GameDevAITools.OnGenerationFailed -= OnGenerationFailed;
            GameDevAITools.OnGenerationProgress -= OnGenerationProgress;
            
            // Save settings
            SaveSettings();
        }
        
        void OnGUI()
        {
            scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);
            
            DrawHeader();
            DrawConfiguration();
            DrawGenerationPanel();
            DrawProgressPanel();
            DrawGeneratedAssets();
            
            EditorGUILayout.EndScrollView();
        }
        
        void DrawHeader()
        {
            EditorGUILayout.Space();
            
            GUIStyle headerStyle = new GUIStyle(EditorStyles.boldLabel);
            headerStyle.fontSize = 18;
            headerStyle.alignment = TextAnchor.MiddleCenter;
            
            EditorGUILayout.LabelField("🎮 GameDev AI Asset Generator", headerStyle);
            EditorGUILayout.LabelField("Generate game assets using AI models", EditorStyles.centeredGreyMiniLabel);
            
            EditorGUILayout.Space();
            EditorGUILayout.LabelField("", GUI.skin.horizontalSlider);
        }
        
        void DrawConfiguration()
        {
            EditorGUILayout.LabelField("⚙️ Configuration", EditorStyles.boldLabel);
            
            EditorGUI.BeginChangeCheck();
            
            apiUrl = EditorGUILayout.TextField("API URL:", apiUrl);
            apiKey = EditorGUILayout.PasswordField("API Key:", apiKey);
            
            if (EditorGUI.EndChangeCheck())
            {
                UpdateAIToolsSettings();
            }
            
            EditorGUILayout.Space();
            
            // API Health Check
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("🔍 Test Connection", GUILayout.Width(120)))
            {
                TestAPIConnection();
            }
            EditorGUILayout.LabelField(statusMessage, EditorStyles.miniLabel);
            EditorGUILayout.EndHorizontal();
            
            EditorGUILayout.Space();
            EditorGUILayout.LabelField("", GUI.skin.horizontalSlider);
        }
        
        void DrawGenerationPanel()
        {
            EditorGUILayout.LabelField("🎨 Asset Generation", EditorStyles.boldLabel);
            
            // Prompt input
            EditorGUILayout.LabelField("Describe your asset:");
            prompt = EditorGUILayout.TextArea(prompt, GUILayout.Height(60));
            
            EditorGUILayout.Space();
            
            // Model selection
            EditorGUILayout.BeginHorizontal();
            EditorGUILayout.LabelField("AI Model:", GUILayout.Width(80));
            selectedModel = (GameDevAITools.AIModel)EditorGUILayout.EnumPopup(selectedModel);
            EditorGUILayout.EndHorizontal();
            
            // Style selection
            EditorGUILayout.BeginHorizontal();
            EditorGUILayout.LabelField("Style:", GUILayout.Width(80));
            selectedStyle = (GameDevAITools.AssetStyle)EditorGUILayout.EnumPopup(selectedStyle);
            EditorGUILayout.EndHorizontal();
            
            // Dimensions selection
            EditorGUILayout.BeginHorizontal();
            EditorGUILayout.LabelField("Size:", GUILayout.Width(80));
            selectedDimensions = (GameDevAITools.AssetDimensions)EditorGUILayout.EnumPopup(selectedDimensions);
            EditorGUILayout.EndHorizontal();
            
            EditorGUILayout.Space();
            
            // Generate button
            EditorGUI.BeginDisabledGroup(isGenerating || string.IsNullOrEmpty(prompt.Trim()));
            
            GUIStyle buttonStyle = new GUIStyle(GUI.skin.button);
            buttonStyle.fontSize = 14;
            buttonStyle.fixedHeight = 35;
            
            if (GUILayout.Button("🚀 Generate Asset", buttonStyle))
            {
                GenerateAsset();
            }
            
            EditorGUI.EndDisabledGroup();
            
            EditorGUILayout.Space();
            EditorGUILayout.LabelField("", GUI.skin.horizontalSlider);
        }
        
        void DrawProgressPanel()
        {
            if (isGenerating)
            {
                EditorGUILayout.LabelField("⏳ Generating Asset...", EditorStyles.boldLabel);
                
                Rect progressRect = EditorGUILayout.GetControlRect();
                EditorGUI.ProgressBar(progressRect, generationProgress, $"{(generationProgress * 100):F0}%");
                
                EditorGUILayout.Space();
                EditorGUILayout.LabelField("", GUI.skin.horizontalSlider);
            }
        }
        
        void DrawGeneratedAssets()
        {
            EditorGUILayout.LabelField($"📁 Generated Assets ({generatedAssets.Count})", EditorStyles.boldLabel);
            
            if (generatedAssets.Count == 0)
            {
                EditorGUILayout.HelpBox("No assets generated yet. Create your first AI asset above!", MessageType.Info);
                return;
            }
            
            for (int i = generatedAssets.Count - 1; i >= 0; i--)
            {
                var asset = generatedAssets[i];
                DrawAssetItem(asset, i);
            }
        }
        
        void DrawAssetItem(GeneratedAssetInfo asset, int index)
        {
            EditorGUILayout.BeginVertical(GUI.skin.box);
            
            EditorGUILayout.BeginHorizontal();
            
            // Asset preview
            if (asset.texture != null)
            {
                GUILayout.Label(asset.texture, GUILayout.Width(64), GUILayout.Height(64));
            }
            else
            {
                GUILayout.Box("No Preview", GUILayout.Width(64), GUILayout.Height(64));
            }
            
            // Asset info
            EditorGUILayout.BeginVertical();
            
            EditorGUILayout.LabelField($"ID: {asset.assetId}", EditorStyles.miniLabel);
            EditorGUILayout.LabelField($"Prompt: {asset.prompt}", EditorStyles.wordWrappedMiniLabel);
            EditorGUILayout.LabelField($"Model: {asset.modelUsed} | Time: {asset.generationTime:F2}s", EditorStyles.miniLabel);
            EditorGUILayout.LabelField($"Generated: {asset.timestamp:HH:mm:ss}", EditorStyles.miniLabel);
            
            EditorGUILayout.EndVertical();
            
            // Actions
            EditorGUILayout.BeginVertical(GUILayout.Width(80));
            
            if (GUILayout.Button("💾 Save", GUILayout.Height(20)))
            {
                SaveAssetToProject(asset);
            }
            
            if (GUILayout.Button("🗑️ Remove", GUILayout.Height(20)))
            {
                generatedAssets.RemoveAt(index);
            }
            
            EditorGUILayout.EndVertical();
            
            EditorGUILayout.EndHorizontal();
            EditorGUILayout.EndVertical();
            
            EditorGUILayout.Space();
        }
        
        void GenerateAsset()
        {
            if (aiTools == null)
            {
                SetupAITools();
            }
            
            if (aiTools == null)
            {
                statusMessage = "❌ Failed to setup AI Tools";
                return;
            }
            
            isGenerating = true;
            generationProgress = 0f;
            statusMessage = "🔄 Generating asset...";
            
            aiTools.GenerateAsset(
                prompt, 
                selectedModel, 
                selectedStyle, 
                selectedDimensions,
                OnAssetGenerated,
                OnGenerationFailed
            );
        }
        
        void OnAssetGenerated(GameDevAITools.GeneratedAsset asset)
        {
            isGenerating = false;
            generationProgress = 1f;
            statusMessage = $"✅ Asset generated successfully! ({asset.generationTime:F2}s)";
            
            var assetInfo = new GeneratedAssetInfo
            {
                assetId = asset.assetId,
                prompt = asset.promptUsed,
                texture = asset.texture,
                modelUsed = asset.modelUsed,
                generationTime = asset.generationTime,
                timestamp = System.DateTime.Now
            };
            
            generatedAssets.Add(assetInfo);
            Repaint();
        }
        
        void OnGenerationFailed(string error)
        {
            isGenerating = false;
            generationProgress = 0f;
            statusMessage = $"❌ Generation failed: {error}";
            Repaint();
        }
        
        void OnGenerationProgress(float progress)
        {
            generationProgress = progress;
            Repaint();
        }
        
        void TestAPIConnection()
        {
            if (aiTools == null)
            {
                SetupAITools();
            }
            
            if (aiTools != null)
            {
                statusMessage = "🔄 Testing connection...";
                aiTools.StartCoroutine(aiTools.CheckAPIHealth((isHealthy) =>
                {
                    statusMessage = isHealthy ? "✅ API is healthy" : "❌ API connection failed";
                }));
            }
        }
        
        void SetupAITools()
        {
            GameObject toolsObject = GameObject.Find("GameDevAITools");
            if (toolsObject == null)
            {
                toolsObject = new GameObject("GameDevAITools");
                toolsObject.hideFlags = HideFlags.HideInHierarchy;
            }
            
            aiTools = toolsObject.GetComponent<GameDevAITools>();
            if (aiTools == null)
            {
                aiTools = toolsObject.AddComponent<GameDevAITools>();
            }
            
            UpdateAIToolsSettings();
        }
        
        void UpdateAIToolsSettings()
        {
            if (aiTools != null)
            {
                aiTools.apiBaseUrl = apiUrl;
                aiTools.apiKey = apiKey;
                aiTools.preferredModel = selectedModel;
                aiTools.defaultStyle = selectedStyle;
                aiTools.defaultDimensions = selectedDimensions;
            }
        }
        
        void SaveAssetToProject(GeneratedAssetInfo asset)
        {
            if (asset.texture == null) return;
            
            string path = EditorUtility.SaveFilePanel(
                "Save Generated Asset",
                "Assets",
                $"ai_asset_{asset.assetId}",
                "png"
            );
            
            if (!string.IsNullOrEmpty(path))
            {
                byte[] pngData = asset.texture.EncodeToPNG();
                System.IO.File.WriteAllBytes(path, pngData);
                
                // Refresh asset database if saved in project
                if (path.StartsWith(Application.dataPath))
                {
                    AssetDatabase.Refresh();
                    statusMessage = $"✅ Asset saved to project: {System.IO.Path.GetFileName(path)}";
                }
                else
                {
                    statusMessage = $"✅ Asset saved: {System.IO.Path.GetFileName(path)}";
                }
            }
        }
        
        void LoadSettings()
        {
            apiUrl = EditorPrefs.GetString("GameDevAI.ApiUrl", "http://localhost:8000/api/v1");
            apiKey = EditorPrefs.GetString("GameDevAI.ApiKey", "");
            selectedModel = (GameDevAITools.AIModel)EditorPrefs.GetInt("GameDevAI.Model", 0);
            selectedStyle = (GameDevAITools.AssetStyle)EditorPrefs.GetInt("GameDevAI.Style", 0);
            selectedDimensions = (GameDevAITools.AssetDimensions)EditorPrefs.GetInt("GameDevAI.Dimensions", 1);
        }
        
        void SaveSettings()
        {
            EditorPrefs.SetString("GameDevAI.ApiUrl", apiUrl);
            EditorPrefs.SetString("GameDevAI.ApiKey", apiKey);
            EditorPrefs.SetInt("GameDevAI.Model", (int)selectedModel);
            EditorPrefs.SetInt("GameDevAI.Style", (int)selectedStyle);
            EditorPrefs.SetInt("GameDevAI.Dimensions", (int)selectedDimensions);
        }
    }
}
