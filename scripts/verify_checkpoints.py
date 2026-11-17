"""Confere os checkpoints originais com os metadados oficiais do Hugging Face."""

from hashlib import file_digest
from pathlib import Path

from huggingface_hub import HfApi


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINTS = {
    "google/gemma-3-4b-it": (
        "093f9f388b31de276ce2de164bdc2081324b9767",
        ROOT / "models/gemma3-4b/original",
    ),
    "Qwen/Qwen3-4B": (
        "1cfa9a7208912126459214e8b04321603b3df60c",
        ROOT / "models/qwen3-4b/original",
    ),
}


def verify(repo_id: str, revision: str, directory: Path, api: HfApi) -> None:
    model = api.model_info(repo_id, revision=revision, files_metadata=True)
    if model.sha != revision:
        raise RuntimeError(f"Revisão inesperada para {repo_id}: {model.sha}")

    total_bytes = 0
    for item in model.siblings:
        path = directory / item.rfilename
        if not path.is_file():
            raise FileNotFoundError(path)
        size = path.stat().st_size
        if item.size is not None and size != item.size:
            raise RuntimeError(f"Tamanho incorreto: {path}")
        if item.lfs is not None:
            with path.open("rb") as source:
                digest = file_digest(source, "sha256").hexdigest()
            if digest != item.lfs.sha256:
                raise RuntimeError(f"SHA-256 incorreto: {path}")
        total_bytes += size

    print(f"OK {repo_id} @ {revision}: {len(model.siblings)} arquivos, {total_bytes} bytes")


if __name__ == "__main__":
    api = HfApi()
    for repo_id, (revision, directory) in CHECKPOINTS.items():
        verify(repo_id, revision, directory, api)
