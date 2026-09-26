using Godot;
using System;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;

public partial class LedgerSyncClient : Node
{
    private readonly HttpClient _httpClient = new HttpClient { BaseAddress = new Uri("http://localhost:8000/") };
    
    [Export]
    public string TerminalHash { get; set; } = string.Empty;

    [Export]
    public bool IsSynchronized { get; set; } = false;

    public override async void _Ready()
    {
        await FetchLedgerStateAsync();
    }

    public async Task FetchLedgerStateAsync()
    {
        try
        {
            HttpResponseMessage response = await _httpClient.GetAsync("/");
            if (response.IsSuccessStatusCode)
            {
                string jsonResponse = await response.Content.ReadAsStringAsync();
                using JsonDocument doc = JsonDocument.Parse(jsonResponse);
                JsonElement root = doc.RootElement;
                
                if (root.TryGetProperty("status", out JsonElement statusElem) && statusElem.GetString() == "resonant")
                {
                    IsSynchronized = true;
                    GD.Print("[*] Godot Client successfully synchronized with FastAPI backend.");
                }
            }
        }
        catch (Exception ex)
        {
            IsSynchronized = false;
            GD.PrintErr($"[!] Failed to connect to FastAPI backend: {ex.Message}");
        }
    }
}
