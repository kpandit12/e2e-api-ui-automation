"""Contract-layer fixtures.

Contract tests hit the live API to validate response *shape*; they reuse the
shared ``client``/``settings`` fixtures defined in the root
``tests/conftest.py``.
"""

from __future__ import annotations
