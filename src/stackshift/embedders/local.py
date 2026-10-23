"""Local sentence-transformers embedder with deterministic on-disk cache."""

from collections.abc import Sequence
from hashlib import sha256
from pathlib import Path

import numpy as np
from numpy.typing import NDArray


class LocalEmbedder:
    def __init__(
        self,
        model_id: str,
        cache_dir: Path = Path(".stackshift/cache"),
        device: str | None = None,
        batch_size: int = 64,
    ) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as error:
            raise ImportError("Install local support: pip install 'stackshift[local]'") from error
        self.model_id, self.cache_dir, self.batch_size = model_id, cache_dir, batch_size
        self._model = SentenceTransformer(model_id, device=device)

    def embed(self, texts: Sequence[str]) -> NDArray[np.float32]:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        output: list[NDArray[np.float32] | None] = [None] * len(texts)
        missing: list[tuple[int, str, Path]] = []
        for index, text in enumerate(texts):
            path = self.cache_dir / f"{sha256((self.model_id + text).encode()).hexdigest()}.npy"
            if path.exists():
                output[index] = np.load(path, allow_pickle=False).astype(np.float32)
            else:
                missing.append((index, text, path))
        if missing:
            vectors = self._model.encode(
                [item[1] for item in missing],
                batch_size=self.batch_size,
                convert_to_numpy=True,
                normalize_embeddings=False,
            )
            for (index, _, path), vector in zip(missing, vectors, strict=True):
                output[index] = np.asarray(vector, dtype=np.float32)
                np.save(path, np.asarray(output[index], dtype=np.float32), allow_pickle=False)
        return np.asarray(output, dtype=np.float32)
