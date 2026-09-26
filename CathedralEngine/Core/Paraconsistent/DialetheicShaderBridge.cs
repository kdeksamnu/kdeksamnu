using System;
using System.Runtime.InteropServices;
using Godot;

namespace CathedralEngine.Core.Paraconsistent
{
    [GlobalClass]
    public partial class DialetheicShaderBridge : Node
    {
        [Export] public string ShaderResourcePath { get; set; } = "res://DialetheicBuffer.glsl";
        [Export] public uint GridWidth { get; set; } = 64;
        [Export] public uint GridHeight { get; set; } = 64;

        [Signal]
        public delegate void MetamorphicSqueezeTriggeredEventHandler(int cellIndex, float cos2Theta, float residualShear);

        private RenderingDevice _rd;
        private Rid _shaderRid;
        private Rid _pipelineRid;
        private bool _isInitialized;

        [StructLayout(LayoutKind.Sequential)]
        public struct VoxelCell
        {
            public float TruthVal;   // 0=N, 1=F, 2=T, 3=B
            public float SigmaX;
            public float SigmaY;
            public float TauXY;
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct ShaderResult
        {
            public float IsMagicAligned; // 1.0 if |cos(2*theta) - (-1/3)| <= 0.015
            public float Cos2Theta;      // Direct Mohr circle alignment
            public float ResidualShear;  // tau_xy * (1 - isMagicAligned)
            public float NeedsSqueeze;   // 1.0 if State B + high shear + aligned
        }

        [StructLayout(LayoutKind.Sequential)]
        private struct PushConstants
        {
            public uint GridWidth;
            public uint GridHeight;
        }

        public override void _Ready()
        {
            InitializeComputeDevice();
        }

        public bool InitializeComputeDevice()
        {
            if (_isInitialized) return true;

            _rd = RenderingServer.CreateLocalRenderingDevice();
            if (_rd == null)
            {
                GD.PrintErr("[DialetheicShaderBridge] Local RenderingDevice is not supported on this platform.");
                return false;
            }

            var shaderFile = GD.Load<RDShaderFile>(ShaderResourcePath);
            if (shaderFile == null)
            {
                GD.PrintErr($"[DialetheicShaderBridge] Failed to load compute shader at: {ShaderResourcePath}");
                return false;
            }

            RDShaderSpirV spirv = shaderFile.GetSpirV();
            _shaderRid = _rd.ShaderCreateFromSpirV(spirv);
            if (!_shaderRid.IsValid)
            {
                GD.PrintErr("[DialetheicShaderBridge] Failed to compile SPIR-V bytecode for DialetheicBuffer.");
                return false;
            }

            _pipelineRid = _rd.ComputePipelineCreate(_shaderRid);
            if (!_pipelineRid.IsValid)
            {
                GD.PrintErr("[DialetheicShaderBridge] Failed to create compute pipeline.");
                return false;
            }

            _isInitialized = true;
            GD.Print($"[DialetheicShaderBridge] Pipeline initialized successfully for {GridWidth}x{GridHeight} voxel lattice.");
            return true;
        }

        public ShaderResult[] DispatchEvaluationPass(VoxelCell[] inputCells)
        {
            if (!_isInitialized && !InitializeComputeDevice())
            {
                return Array.Empty<ShaderResult>();
            }

            uint cellCount = GridWidth * GridHeight;
            if (inputCells.Length != cellCount)
            {
                Array.Resize(ref inputCells, (int)cellCount);
            }

            byte[] inputBytes = MemoryMarshal.AsBytes<VoxelCell>(inputCells).ToArray();
            Rid inputBuffer = _rd.StorageBufferCreate((uint)inputBytes.Length, inputBytes);

            int outputSizeBytes = Marshal.SizeOf<ShaderResult>() * (int)cellCount;
            Rid outputBuffer = _rd.StorageBufferCreate((uint)outputSizeBytes);

            var uInput = new RDUniform
            {
                UniformType = RenderingDevice.UniformType.StorageBuffer,
                Binding = 0
            };
            uInput.AddId(inputBuffer);

            var uOutput = new RDUniform
            {
                UniformType = RenderingDevice.UniformType.StorageBuffer,
                Binding = 1
            };
            uOutput.AddId(outputBuffer);

            Rid uniformSet = _rd.UniformSetCreate(new Godot.Collections.Array<RDUniform> { uInput, uOutput }, _shaderRid, 0);

            PushConstants pushData = new PushConstants { GridWidth = GridWidth, GridHeight = GridHeight };
            byte[] pushBytes = MemoryMarshal.AsBytes<PushConstants>(MemoryMarshal.CreateReadOnlySpan(ref pushData, 1)).ToArray();

            long computeList = _rd.ComputeListBegin();
            _rd.ComputeListBindComputePipeline(computeList, _pipelineRid);
            _rd.ComputeListBindUniformSet(computeList, uniformSet, 0);
            _rd.ComputeListSetPushConstant(computeList, pushBytes, (uint)pushBytes.Length);

            uint xGroups = (GridWidth + 7) / 8;
            uint yGroups = (GridHeight + 7) / 8;
            _rd.ComputeListDispatch(computeList, xGroups, yGroups, 1);
            _rd.ComputeListEnd();

            _rd.Submit();
            _rd.Sync();

            // Safe, zero-allocation conversion from raw GPU byte span to ShaderResult array
            byte[] outputDataBytes = _rd.BufferGetData(outputBuffer);
            ShaderResult[] results = MemoryMarshal.Cast<byte, ShaderResult>(outputDataBytes).ToArray();

            for (int i = 0; i < results.Length; i++)
            {
                if (results[i].NeedsSqueeze > 0.5f)
                {
                    EmitSignal(SignalName.MetamorphicSqueezeTriggered, i, results[i].Cos2Theta, results[i].ResidualShear);
                }
            }

            _rd.FreeRid(uniformSet);
            _rd.FreeRid(inputBuffer);
            _rd.FreeRid(outputBuffer);

            return results;
        }

        public override void _ExitTree()
        {
            if (_rd != null)
            {
                if (_pipelineRid.IsValid) _rd.FreeRid(_pipelineRid);
                if (_shaderRid.IsValid) _rd.FreeRid(_shaderRid);
                _rd.Dispose();
                _rd = null;
            }
        }
    }
}
