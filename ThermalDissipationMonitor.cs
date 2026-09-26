using System;

namespace CathedralEngine.Thermodynamics
{
    public sealed class ThermalDissipationMonitor
    {
        public const float AmbientTempK = 293.15f;
        public const float GlassTransitionTempK = 923.15f;
        public const float MaxPermissibleTempK = 373.15f;
        public const float SpecificHeatCp = 1050.0f;
        public const float JointMassKg = 24.0f;
        public const float PassiveBedrockDissipationW = 4200.0f;
        public const float EnergyPerEventJ = 14850.0f;

        private readonly object _thermalLock = new object();
        private float _currentMortarTempK;
        private float _lastUpdateTimestamp;

        public ThermalDissipationMonitor()
        {
            _currentMortarTempK = AmbientTempK;
            _lastUpdateTimestamp = 0.0f;
        }

        public bool CanProcessSqueezeEvent(float currentTimestamp)
        {
            lock (_thermalLock)
            {
                UpdateCooling(currentTimestamp);

                float eventDeltaT = EnergyPerEventJ / (JointMassKg * SpecificHeatCp);
                return (_currentMortarTempK + eventDeltaT) < MaxPermissibleTempK;
            }
        }

        public void RegisterSqueezeEvent(float currentTimestamp)
        {
            lock (_thermalLock)
            {
                UpdateCooling(currentTimestamp);
                float eventDeltaT = EnergyPerEventJ / (JointMassKg * SpecificHeatCp);
                _currentMortarTempK += eventDeltaT;
            }
        }

        private void UpdateCooling(float currentTimestamp)
        {
            if (_lastUpdateTimestamp <= 0.0f)
            {
                _lastUpdateTimestamp = currentTimestamp;
                return;
            }

            float dt = currentTimestamp - _lastUpdateTimestamp;
            if (dt > 0.0f)
            {
                float excessTemp = _currentMortarTempK - AmbientTempK;
                if (excessTemp > 0.0f)
                {
                    float energyRemoved = PassiveBedrockDissipationW * dt;
                    float deltaTRemoved = energyRemoved / (JointMassKg * SpecificHeatCp);
                    _currentMortarTempK = Math.Max(AmbientTempK, _currentMortarTempK - deltaTRemoved);
                }
                _lastUpdateTimestamp = currentTimestamp;
            }
        }

        public float CurrentTemperatureK => _currentMortarTempK;
    }
}
