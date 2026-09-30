using System;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace CathedralEngine.Storage.AshArchive
{
    public sealed class AshArchiveLedger
    {
        private readonly object _ledgerLock = new object();
        private readonly string _ledgerFilePath;
        private string _lastBlockHash;
        private long _blockIndex;

        public AshArchiveLedger(string ledgerFilePath = "ash_archive_ledger.ndjson", string genesisHash = "e4d29f81a7b5c036")
        {
            _ledgerFilePath = ledgerFilePath;
            _lastBlockHash = genesisHash;
            _blockIndex = 1702;
        }

        public string CommitBlock(object payload)
        {
            lock (_ledgerLock)
            {
                _blockIndex++;
                string timestampUtc = DateTime.UtcNow.ToString("o");

                var options = new JsonSerializerOptions { WriteIndented = false };
                string canonicalPayload = JsonSerializer.Serialize(payload, options);

                string rawBlockData = $"{_blockIndex}:{timestampUtc}:{_lastBlockHash}:{canonicalPayload}";
                string currentBlockHash = ComputeSha512Hex(rawBlockData);

                var ledgerRecord = new
                {
                    BlockIndex = _blockIndex,
                    TimestampUtc = timestampUtc,
                    PrevHash = _lastBlockHash,
                    BlockHash = currentBlockHash,
                    Payload = payload
                };

                string ndjsonLine = JsonSerializer.Serialize(ledgerRecord, options);
                File.AppendAllText(_ledgerFilePath, ndjsonLine + Environment.NewLine);

                _lastBlockHash = currentBlockHash;
                return currentBlockHash;
            }
        }

        private static string ComputeSha512Hex(string input)
        {
            using var sha512 = SHA512.Create();
            byte[] bytes = Encoding.UTF8.GetBytes(input);
            byte[] hash = sha512.ComputeHash(bytes);
            return Convert.ToHexString(hash).ToLowerInvariant();
        }

        public string LatestHash => _lastBlockHash;
        public long CurrentBlockIndex => _blockIndex;
    }
}
