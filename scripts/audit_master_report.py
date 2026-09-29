#!/usr/bin/env python3
import pathlib
import re
import sys

ROMAN = [
    "I","II","III","IV","V","VI","VII","VIII","IX","X",
    "XI","XII","XIII","XIV","XV","XVI","XVII","XVIII",
    "XIX","XX","XXI","XXII","XXIII","XXIV","XXV","XXVI","XXVII","XXVIII",
    "XXIX","XXX","XXXI","XXXII","XXXIII","XXXIV","XXXV","XXXVI","XXXVII","XXXVIII","XXXIX",
    "XL","XLI","XLII","XLIII","XLIV","XLV","XLVI","XLVII","XLVIII",
]
EXPECTED_STRESS = dict(zip(range(1, 11), ROMAN[18:28]))
ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "MASTER_REPORT_CANONICAL_48.md"
text = REPORT.read_text(encoding="utf-8")
heads = re.findall(r"(?m)^### Chapter ([IVXLCDM]+) — (.+)$", text)
nums = [n for n, _ in heads]
errors = []

if nums != ROMAN:
    errors.append(f"chapter sequence != I–XLVIII: {nums}")
if len(nums) != len(set(nums)):
    errors.append("duplicate chapter number")

for i, chapter in EXPECTED_STRESS.items():
    pattern = rf"(?m)^### Chapter {chapter} — .*\(Stress Test [IVXLCDM]+\)$"
    if not re.search(pattern, text):
        errors.append(f"missing Stress Test {i} at {chapter}")

if not re.search(r"(?m)^### Chapter XL — .*", text) or "XL = Codex Closure" not in text:
    errors.append("XL Codex Closure marker missing")
if not re.search(r"(?m)^### Chapter XLVIII — .*", text) or "XLVIII = Master Report Closure" not in text:
    errors.append("XLVIII Master Report Closure marker missing")

for label in ["PART I","PART II","PART III","PART IV","PART V","PART VI","PART VII","PART VIII"]:
    if len(re.findall(rf"(?m)^## {re.escape(label)}(?: —|:)", text)) != 1:
        errors.append(f"Part label {label} duplicate/missing")

apps = re.findall(r"(?m)^### Appendix ([A-J]) —", text)
if apps != list("ABCDEFGHIJ"):
    errors.append(f"appendix sequence != A–J: {apps}")
if re.search(r"(?m)^### Appendix [K-Z]", text):
    errors.append("appendix beyond J")

for target in ["Chapter XXI", "Chapter XXII"]:
    if not re.search(rf"(?m)^### {re.escape(target)} —", text):
        errors.append(f"{target} missing")

if errors:
    print("AUDIT: FAIL")
    print("\n".join("- " + e for e in errors))
    sys.exit(1)

print("AUDIT: PASS")
print("chapters: I–XLVIII unique and contiguous")
print("stress tests: I–X -> XIX–XXVIII")
print("XL: Codex Closure")
print("XLVIII: Master Report Closure")
print("appendices: A–J")
print("parts: I–VIII unique")
