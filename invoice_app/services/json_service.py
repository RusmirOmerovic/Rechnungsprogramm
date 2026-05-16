import json
from pathlib import Path


class JsonService:
    def __init__(self) -> None:
        self.base_dir = Path(__file__).resolve().parents[2] / "daten" / "invoices_json"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def write_invoice_json(self, payload: dict, invoice_number: str) -> str:
        path = self.base_dir / f"{invoice_number}.json"
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
        return str(path)
