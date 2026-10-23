"""Build normalized stored-old/new-embedding training pairs without old-model calls."""

from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from stackshift.adapters.base import l2_normalize
from stackshift.connectors.base import VectorStoreProtocol
from stackshift.embedders.base import EmbedderProtocol
from stackshift.errors import MissingTextError, QuantizedVectorsError
from stackshift.splits import deterministic_split, enforce_evaluation_isolation


@dataclass(frozen=True)
class PairingResult:
    train_old: NDArray[np.float32]
    train_new: NDArray[np.float32]
    validation_old: NDArray[np.float32]
    validation_new: NDArray[np.float32]
    train_ids: tuple[str, ...]
    validation_ids: tuple[str, ...]
    old_dimensions: int
    new_dimensions: int
    old_model_id: str
    new_model_id: str


class PairingBuilder:
    """Use stored old vectors and only the replacement embedder."""

    def __init__(self, sample_size: int = 15_000, seed: int = 42) -> None:
        if not 10 <= sample_size <= 20_000:
            raise ValueError("sample_size must be between 10 and 20,000")
        self.sample_size, self.seed = sample_size, seed

    def build(
        self,
        store: VectorStoreProtocol,
        new_embedder: EmbedderProtocol,
        old_model_id: str,
        eval_query_ids: Iterable[str] = (),
        candidate_ids: Iterable[str] = (),
    ) -> PairingResult:
        if store.detect_quantization():
            raise QuantizedVectorsError("stored vectors are quantized or compressed")
        ids = store.sample(self.sample_size, self.seed)
        if len(ids) < 2:
            raise ValueError("store does not contain enough documents for pairing")
        try:
            texts = store.fetch_text(ids)
        except (KeyError, TypeError) as error:
            raise MissingTextError("source text unavailable for sampled documents") from error
        if len(texts) != len(ids) or any(not text for text in texts):
            raise MissingTextError("source text unavailable for sampled documents")
        old, new = l2_normalize(store.read_vectors(ids)), l2_normalize(new_embedder.embed(texts))
        if old.shape[0] != len(ids) or new.shape[0] != len(ids):
            raise ValueError("embedding and stored-vector rows must match sampled IDs")
        split = deterministic_split(ids, self.seed)
        enforce_evaluation_isolation(split.train_ids, eval_query_ids, candidate_ids)
        locations = {identifier: index for index, identifier in enumerate(ids)}
        train = [locations[identifier] for identifier in split.train_ids]
        validation = [locations[identifier] for identifier in split.validation_ids]
        return PairingResult(
            old[train],
            new[train],
            old[validation],
            new[validation],
            split.train_ids,
            split.validation_ids,
            old.shape[1],
            new.shape[1],
            old_model_id,
            new_embedder.model_id,
        )
