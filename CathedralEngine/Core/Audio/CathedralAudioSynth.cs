using Godot;
using System;

namespace CathedralEngine.Core.Audio
{
    /// <summary>
    /// Procedural Audio Synthesizer for the Cathedral Engine.
    /// Generates real-time PCM audio via AudioStreamGenerator.
    /// </summary>
    public partial class CathedralAudioSynth : AudioStreamPlayer
    {
        private AudioStreamGeneratorPlayback _playback;
        private float _mixRate;
        
        // Phase accumulators
        private float _phaseBass = 0f;
        private float _phaseChime = 0f;
        private float _phaseHum = 0f;
        private float _phaseFracture = 0f;
        
        // Envelopes (0.0 to 1.0)
        private float _bassEnv = 0f;
        private float _chimeEnv = 0f;
        private float _humEnv = 0f;
        private float _fractureEnv = 0f;

        public override void _Ready()
        {
            var generator = new AudioStreamGenerator();
            generator.MixRate = 44100;
            generator.BufferLength = 0.5f;
            Stream = generator;
            Play();
            _playback = GetStreamPlayback() as AudioStreamGeneratorPlayback;
            _mixRate = generator.MixRate;
        }

        public override void _Process(double delta)
        {
            if (_playback == null) return;
            
            int framesAvailable = _playback.GetFramesAvailable();
            float dt = 1.0f / _mixRate;

            for (int i = 0; i < framesAvailable; i++)
            {
                float sample = 0f;

                // 1. Sub-bass Drone (Metamorphic Squeeze) - 40Hz Sine
                _phaseBass += 40.0f * dt;
                if (_phaseBass > 1.0f) _phaseBass -= 1.0f;
                sample += (float)Math.Sin(_phaseBass * Math.PI * 2.0) * 0.5f * _bassEnv;
                _bassEnv = Mathf.MoveToward(_bassEnv, 0f, dt * 0.5f);

                // 2. Crystalline Chime (Monolith Fragment) - 2500Hz Sine
                _phaseChime += 2500.0f * dt;
                if (_phaseChime > 1.0f) _phaseChime -= 1.0f;
                sample += (float)Math.Sin(_phaseChime * Math.PI * 2.0) * 0.3f * _chimeEnv;
                _chimeEnv = Mathf.MoveToward(_chimeEnv, 0f, dt * 2.0f);

                // 3. Pyragas Hum (Motor Actuation) - 60Hz Sine modulated by 1000Hz pulse
                _phaseHum += 60.0f * dt;
                if (_phaseHum > 1.0f) _phaseHum -= 1.0f;
                float pulse = (float)(Math.Sin(_phaseHum * 1000.0 * Math.PI * 2.0) * 0.5 + 0.5);
                sample += (float)Math.Sin(_phaseHum * Math.PI * 2.0) * 0.2f * _humEnv * (0.5f + 0.5f * pulse);
                _humEnv = Mathf.MoveToward(_humEnv, 0f, dt * 0.2f);

                // 4. Fracture Noise (Observer Paradox) - 150Hz Sawtooth
                _phaseFracture += 150.0f * dt;
                if (_phaseFracture > 1.0f) _phaseFracture -= 1.0f;
                float saw = (_phaseFracture * 2.0f) - 1.0f;
                sample += saw * 0.6f * _fractureEnv;
                _fractureEnv = Mathf.MoveToward(_fractureEnv, 0f, dt * 1.5f);

                // Push stereo frame
                _playback.PushFrame(new Vector2(sample, sample));
            }
        }

        public void TriggerSqueezeDrone() { _bassEnv = 1.0f; }
        public void TriggerChime() { _chimeEnv = 1.0f; }
        public void TriggerPyragasHum() { _humEnv = 1.0f; }
        public void TriggerFracture() { _fractureEnv = 1.0f; }
    }
}
