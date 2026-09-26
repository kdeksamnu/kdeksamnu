using Godot;
using System;

namespace CathedralEngine.UI
{
    public partial class ObserverEyeDashboard : CanvasLayer
    {
        private Label _fiedlerLabel, _pyragasTorqueLabel, _thermalLabel, _paradoxCountLabel, _archiveGrowthLabel, _statusLabel;
        private Label _stressLabel, _mutationLabel; // DIMENSION 19
        private ProgressBar _thermalBar, _fiedlerBar;
        private ColorRect _statusIndicator;
        
        private float _currentFiedler = 0.0f, _currentTorque = 0.0f, _currentTemp = 20.0f;
        private int _activeParadoxes = 0, _archiveNodes = 0;
        private float _topologicalStress = 0.0f;
        private float _effectiveMutation = 0.05f;
        
        private const float T_MAX = 650.0f, FIEDLER_CRITICAL = 0.05f;
        private float _updateTimer = 0.0f;

        public override void _Ready()
        {
            var margin = new MarginContainer { AnchorsPreset = (int)Control.LayoutPreset.TopLeft, OffsetRight = 350, OffsetBottom = 550 };
            margin.AddThemeConstantOverride("margin_left", 15); margin.AddThemeConstantOverride("margin_top", 15);
            margin.AddThemeConstantOverride("margin_right", 15); margin.AddThemeConstantOverride("margin_bottom", 15);
            AddChild(margin);
            
            var vbox = new VBoxContainer(); margin.AddChild(vbox);

            var title = new Label { Text = "OBSERVER'S EYE [DIM 19]" };
            title.AddThemeFontSizeOverride("font_size", 20); title.AddThemeColorOverride("font_color", Colors.Cyan);
            vbox.AddChild(title);

            _fiedlerLabel = new Label { Text = "λ₂ (Spatial Proxy): 1.000" }; vbox.AddChild(_fiedlerLabel);
            _fiedlerBar = new ProgressBar { MaxValue = 1.0f, Value = 1.0f, CustomMinimumSize = new Vector2(300, 15) }; vbox.AddChild(_fiedlerBar);

            // DIMENSION 19: ISOMORPHIC PRINCIPLE METRICS
            _stressLabel = new Label { Text = "Topological Stress: 0.00" }; 
            _stressLabel.AddThemeColorOverride("font_color", Colors.OrangeRed);
            vbox.AddChild(_stressLabel);
            
            _mutationLabel = new Label { Text = "Effective Mutation (μ_eff): 0.05" }; 
            _mutationLabel.AddThemeColorOverride("font_color", Colors.Yellow);
            vbox.AddChild(_mutationLabel);

            _pyragasTorqueLabel = new Label { Text = "Torque: 0.0000 N·m" }; vbox.AddChild(_pyragasTorqueLabel);
            _thermalLabel = new Label { Text = "Temp: 20.0°C / 650.0°C (Tg)" }; vbox.AddChild(_thermalLabel);
            _thermalBar = new ProgressBar { MaxValue = T_MAX, Value = 20.0f, CustomMinimumSize = new Vector2(300, 15) }; vbox.AddChild(_thermalBar);

            _paradoxCountLabel = new Label { Text = "Active Paradoxes: 0" }; vbox.AddChild(_paradoxCountLabel);
            _archiveGrowthLabel = new Label { Text = "Ash Archive Nodes: 0" }; vbox.AddChild(_archiveGrowthLabel);

            var statusBox = new HBoxContainer(); vbox.AddChild(statusBox);
            _statusIndicator = new ColorRect { Color = Colors.Green, CustomMinimumSize = new Vector2(20, 20) }; statusBox.AddChild(_statusIndicator);
            _statusLabel = new Label { Text = "NOMINAL" }; statusBox.AddChild(_statusLabel);
        }

        public override void _Process(double delta)
        {
            _updateTimer += (float)delta;
            if (_updateTimer < 0.2f) return;
            _updateTimer = 0.0f;

            _fiedlerLabel.Text = $"λ₂ (Spatial Proxy): {_currentFiedler:F4}";
            _fiedlerBar.Value = _currentFiedler;
            _fiedlerBar.Modulate = _currentFiedler < FIEDLER_CRITICAL ? Colors.Red : Colors.Green;

            // DIMENSION 19: Visualizing the Isomorphic Coupling
            _stressLabel.Text = $"Topological Stress: {_topologicalStress:F2}";
            _mutationLabel.Text = $"Effective Mutation (μ_eff): {_effectiveMutation:F3}";
            
            if (_topologicalStress > 10.0f) _mutationLabel.AddThemeColorOverride("font_color", Colors.Red);
            else if (_topologicalStress > 5.0f) _mutationLabel.AddThemeColorOverride("font_color", Colors.Orange);
            else _mutationLabel.AddThemeColorOverride("font_color", Colors.Yellow);

            _pyragasTorqueLabel.Text = $"Torque: {_currentTorque:F4} N·m";
            _thermalLabel.Text = $"Temp: {_currentTemp:F1}°C / {T_MAX}°C (Tg)";
            _thermalBar.Value = _currentTemp;
            _thermalBar.Modulate = _currentTemp > T_MAX * 0.9f ? Colors.Red : (_currentTemp > T_MAX * 0.7f ? Colors.Gold : Colors.Green);

            _paradoxCountLabel.Text = $"Active Paradoxes: {_activeParadoxes}";
            _archiveGrowthLabel.Text = $"Ash Archive Nodes: {_archiveNodes}";

            bool ok = _currentTemp < T_MAX * 0.95f && _currentFiedler > FIEDLER_CRITICAL && _activeParadoxes < 20;
            _statusIndicator.Color = ok ? Colors.Green : Colors.Red;
            _statusLabel.Text = ok ? "NOMINAL" : "WARNING";
            _statusLabel.AddThemeColorOverride("font_color", ok ? Colors.Green : Colors.Red);
        }

        public void UpdateFiedler(float v) => _currentFiedler = v;
        public void UpdateTorque(float v) => _currentTorque = v;
        public void UpdateTemp(float v) => _currentTemp = v;
        public void UpdateParadoxes(int v) => _activeParadoxes = v;
        public void UpdateArchive(int v) => _archiveNodes = v;
        
        // DIMENSION 19: Isomorphic Coupling Telemetry
        public void UpdateStress(float lambda2, float stress, float mutRate) {
            _currentFiedler = lambda2;
            _topologicalStress = stress;
            _effectiveMutation = mutRate;
        }
    }
}
