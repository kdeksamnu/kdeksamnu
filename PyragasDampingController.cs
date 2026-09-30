using System;
using System.Numerics;

namespace CathedralEngine.Physics.Damping
{
    public sealed class PyragasDampingController
    {
        private struct TimestampedOmega
        {
            public float Time;
            public Vector3 Omega;
        }

        private readonly object _syncLock = new object();
        private readonly float _gainK;
        private readonly float _delaySeconds;
        private readonly TimestampedOmega[] _historyBuffer;
        private int _writeIndex;
        private int _count;

        public PyragasDampingController(float gainK = 0.25f, float delayMs = 11.2f, int maxHistorySize = 128)
        {
            if (gainK < 0.10f || gainK > 0.35f)
            {
                throw new ArgumentOutOfRangeException(nameof(gainK), "Gain K must reside within stable corridor [0.10, 0.35].");
            }

            _gainK = gainK;
            _delaySeconds = delayMs / 1000.0f;
            _historyBuffer = new TimestampedOmega[maxHistorySize];
            _writeIndex = 0;
            _count = 0;
        }

        public Vector3 ComputeDampingTorque(Vector3 currentOmega, float currentTime)
        {
            lock (_syncLock)
            {
                float targetTime = currentTime - _delaySeconds;

                int lowerIdx = -1;
                int upperIdx = -1;
                float lowerTime = 0.0f;
                float upperTime = 0.0f;

                for (int i = 0; i < _count; i++)
                {
                    int idx = (_writeIndex - 1 - i + _historyBuffer.Length) % _historyBuffer.Length;
                    if (_historyBuffer[idx].Time <= targetTime)
                    {
                        lowerIdx = idx;
                        lowerTime = _historyBuffer[idx].Time;

                        if (i > 0)
                        {
                            int nextIdx = (_writeIndex - i + _historyBuffer.Length) % _historyBuffer.Length;
                            upperIdx = nextIdx;
                            upperTime = _historyBuffer[nextIdx].Time;
                        }
                        else
                        {
                            upperIdx = lowerIdx;
                            upperTime = lowerTime;
                        }
                        break;
                    }
                }

                Vector3 delayedOmega;

                if (lowerIdx != -1 && upperIdx != -1 && (upperTime - lowerTime) > 1e-6f)
                {
                    float fraction = Math.Clamp((targetTime - lowerTime) / (upperTime - lowerTime), 0.0f, 1.0f);
                    Vector3 lowerOmega = _historyBuffer[lowerIdx].Omega;
                    Vector3 upperOmega = _historyBuffer[upperIdx].Omega;
                    delayedOmega = Vector3.Lerp(lowerOmega, upperOmega, fraction);
                }
                else if (lowerIdx != -1)
                {
                    delayedOmega = _historyBuffer[lowerIdx].Omega;
                }
                else
                {
                    delayedOmega = currentOmega;
                }

                Vector3 omegaDiff = delayedOmega - currentOmega;
                Vector3 pyragasTorque = _gainK * omegaDiff;

                _historyBuffer[_writeIndex] = new TimestampedOmega
                {
                    Time = currentTime,
                    Omega = currentOmega
                };

                _writeIndex = (_writeIndex + 1) % _historyBuffer.Length;
                if (_count < _historyBuffer.Length)
                {
                    _count++;
                }

                return pyragasTorque;
            }
        }
    }
}
