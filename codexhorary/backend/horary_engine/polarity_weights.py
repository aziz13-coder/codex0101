"""Central repository for testimony polarity and weight tables."""

from __future__ import annotations

from enum import Enum

from .polarity import Polarity


class TestimonyKey(Enum):
    """Canonical keys for all supported testimony tokens."""

    MOON_APPLYING_TRINE_EXAMINER_SUN = "moon_applying_trine_examiner_sun"
    MOON_APPLYING_SQUARE_EXAMINER_SUN = "moon_applying_square_examiner_sun"
    PERFECTION_DIRECT = "perfection_direct"
    PERFECTION_TRANSLATION_OF_LIGHT = "perfection_translation_of_light"
    PERFECTION_COLLECTION_OF_LIGHT = "perfection_collection_of_light"


# Prevent pytest from collecting the enum as a test class
TestimonyKey.__test__ = False


POLARITY_TABLE: dict[TestimonyKey, Polarity] = {
    # Favorable Moon applying trine to the examiner (Sun in education questions)
    TestimonyKey.MOON_APPLYING_TRINE_EXAMINER_SUN: Polarity.POSITIVE,
    # Example negative testimony
    TestimonyKey.MOON_APPLYING_SQUARE_EXAMINER_SUN: Polarity.NEGATIVE,
    # Perfection testimonies are positive by default
    TestimonyKey.PERFECTION_DIRECT: Polarity.POSITIVE,
    TestimonyKey.PERFECTION_TRANSLATION_OF_LIGHT: Polarity.POSITIVE,
    TestimonyKey.PERFECTION_COLLECTION_OF_LIGHT: Polarity.POSITIVE,
}

WEIGHT_TABLE: dict[TestimonyKey, float] = {
    TestimonyKey.MOON_APPLYING_TRINE_EXAMINER_SUN: 1.0,
    TestimonyKey.MOON_APPLYING_SQUARE_EXAMINER_SUN: 1.0,
    TestimonyKey.PERFECTION_DIRECT: 1.0,
    TestimonyKey.PERFECTION_TRANSLATION_OF_LIGHT: 1.0,
    TestimonyKey.PERFECTION_COLLECTION_OF_LIGHT: 1.0,
}


# ``family``/``kind`` tagging for group-based contribution control
FAMILY_TABLE: dict[TestimonyKey, str] = {
    TestimonyKey.PERFECTION_DIRECT: "perfection",
    TestimonyKey.PERFECTION_TRANSLATION_OF_LIGHT: "perfection",
    TestimonyKey.PERFECTION_COLLECTION_OF_LIGHT: "perfection",
}

KIND_TABLE: dict[TestimonyKey, str] = {
    TestimonyKey.PERFECTION_DIRECT: "direct",
    TestimonyKey.PERFECTION_TRANSLATION_OF_LIGHT: "tol",
    TestimonyKey.PERFECTION_COLLECTION_OF_LIGHT: "col",
}

