using Godot;
using System.Text;
using System.Security.Cryptography;

public partial class MerkleValidator : Node
{
    [Export]
    public string GenesisAnchor { get; set; } = "0000000000000000000000000000000000000000000000000000000000000000";

    public string ComputeStepHash(string parentHash, string payload)
    {
        string raw = $"{parentHash}:{payload}";
        byte[] bytes = SHA256.HashData(Encoding.UTF8.GetBytes(raw));
        StringBuilder builder = new StringBuilder();
        foreach (byte b in bytes)
        {
            builder.Append(b.ToString("x2"));
        }
        return builder.ToString();
    }
}
