"""Project Human Organism — reference implementation of the Phase 0 substrate services.

The package realizes the read-side services specified in docs/: entity
resolution, typed traversal, scale contracts, evidence retrieval, search, the
groundedness guard, and release building. It deliberately does not include the
3D viewer or content population, which remain behind the Phase 1 entry gate
(D-011).
"""

__all__ = [
    'substrate', 'graph', 'scale', 'evidence', 'search', 'groundedness',
    'release', 'api',
]
__version__ = '0.1.0'
