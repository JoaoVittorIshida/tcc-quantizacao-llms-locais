"""Save the untouched WikiText-2 raw test texts as newline-separated UTF-8."""

import hashlib
import json
from pathlib import Path

from datasets import load_dataset


root = Path(__file__).resolve().parents[1]
revision = "b08601e04326c79dfdd32d625aee71d232d685c3"
dataset = load_dataset(
    "Salesforce/wikitext", "wikitext-2-raw-v1", split="test", revision=revision
)
path = root / "datasets" / "wiki.test.raw"
path.parent.mkdir(exist_ok=True)
path.write_text("\n".join(dataset["text"]) + "\n", encoding="utf-8", newline="\n")
metadata = {
    "source": "Salesforce/wikitext",
    "config": "wikitext-2-raw-v1",
    "split": "test",
    "revision": revision,
    "rows": len(dataset),
    "path": str(path.relative_to(root)).replace("\\", "/"),
    "size_bytes": path.stat().st_size,
    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    "processing": "Join unmodified row text with LF and add final LF; UTF-8",
}
(root / "datasets" / "wiki.test.metadata.json").write_text(
    json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(metadata, indent=2))
