from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass
class RankedItem(Generic[T]):
    item: T
    score: float
    rank: int


def reciprocal_rank_fusion(
    ranked_lists: list[list[RankedItem[T]]],
    weights: list[float],
    k: int = 60,
) -> list[RankedItem[T]]:

    if len(ranked_lists) != len(weights):
        raise ValueError(
            "ranked_lists and weights must "
            "have the same length."
        )

    fused: dict[str, float] = {}
    objects: dict[str, T] = {}

    for ranked_list, weight in zip(
        ranked_lists,
        weights,
    ):

        for result in ranked_list:

            item_id = _item_id(
                result.item
            )

            objects[item_id] = (
                result.item
            )

            fused[item_id] = (
                fused.get(
                    item_id,
                    0.0,
                )
                + weight
                * (
                    1.0
                    / (
                        k
                        + result.rank
                    )
                )
            )

    ordered = sorted(
        fused.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    output: list[
        RankedItem[T]
    ] = []

    for rank, (
        item_id,
        score,
    ) in enumerate(
        ordered,
        start=1,
    ):

        output.append(
            RankedItem(
                item=objects[item_id],
                score=score,
                rank=rank,
            )
        )

    return output


def _item_id(
    item: T,
) -> str:

    # Our RetrievalResult always has chunk_id.
    return str(
        getattr(
            item,
            "chunk_id",
        )
    )