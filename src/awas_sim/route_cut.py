from __future__ import annotations

from functools import lru_cache
from itertools import combinations, product
from typing import Iterable, Sequence


def minimum_disabling_coalition(routes: Iterable[set[str]]) -> tuple[int, tuple[str, ...]]:
    routes = [set(r) for r in routes if r]
    if not routes:
        return 0, tuple()
    centres = sorted(set().union(*routes))
    for size in range(1, len(centres) + 1):
        for coalition in combinations(centres, size):
            cset = set(coalition)
            if all(cset & route for route in routes):
                return size, coalition
    return 0, tuple()


def complete_routes(
    evidence_controllers: Sequence[str],
    advocate_controllers: Sequence[str],
    reviewer_controllers: Sequence[str],
    reviewer_threshold: int,
    enforcer_controllers: Sequence[str],
) -> list[set[str]]:
    if not evidence_controllers or not advocate_controllers or not enforcer_controllers:
        return []
    if reviewer_threshold <= 0 or len(reviewer_controllers) < reviewer_threshold:
        return []

    reviewer_sets = list(combinations(reviewer_controllers, reviewer_threshold))
    routes: list[set[str]] = []
    for evidence, advocate, reviewers, enforcer in product(
        evidence_controllers,
        advocate_controllers,
        reviewer_sets,
        enforcer_controllers,
    ):
        routes.append({evidence, advocate, *reviewers, enforcer})
    return routes


@lru_cache(maxsize=512)
def _route_cut_size_cached(
    evidence_controllers: tuple[str, ...],
    advocate_controllers: tuple[str, ...],
    reviewer_controllers: tuple[str, ...],
    reviewer_threshold: int,
    enforcer_controllers: tuple[str, ...],
) -> int:
    routes = complete_routes(
        evidence_controllers,
        advocate_controllers,
        reviewer_controllers,
        reviewer_threshold,
        enforcer_controllers,
    )
    return minimum_disabling_coalition(routes)[0]


def route_cut_size(
    evidence_controllers: Sequence[str],
    advocate_controllers: Sequence[str],
    reviewer_controllers: Sequence[str],
    reviewer_threshold: int,
    enforcer_controllers: Sequence[str],
) -> int:
    # The number of possible controller topologies is tiny relative to episode count.
    # Cache exact topology results without changing any experimental semantics.
    return _route_cut_size_cached(
        tuple(evidence_controllers),
        tuple(advocate_controllers),
        tuple(reviewer_controllers),
        reviewer_threshold,
        tuple(enforcer_controllers),
    )
