with open("mlaos_archive_audit.py", "r") as f:
    code = f.read()

# Fix the unpacking loop inside run_audit or verify_record call site
old_snippet = """    def run_audit(self):
        report = {"total": 0, "valid": 0, "invalid": 0, "errors": []}
        for filepath in self.get_archive_files():
            is_valid, data, computed_hash in self.verify_record(filepath)"""

new_snippet = """    def run_audit(self):
        report = {"total": 0, "valid": 0, "invalid": 0, "errors": []}
        for filepath in self.get_archive_files():
            result = self.verify_record(filepath)
            if not result:
                continue
            is_valid, data, computed_hash = result"""

if old_snippet in code:
    code = code.replace(old_snippet, new_snippet)
    with open("mlaos_archive_audit.py", "w") as f:
        f.write(code)
    print("[OK] mlaos_archive_audit.py successfully patched.")
else:
    print("[INFO] Snippet not found; checking alternate loop structures.")
