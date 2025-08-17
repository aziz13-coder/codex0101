import datetime

from horary_engine.engine import EnhancedTraditionalHoraryJudgmentEngine
from models import HoraryChart, Planet, Sign, PlanetPosition


def test_benefic_in_quesited_house_provides_support():
    engine = EnhancedTraditionalHoraryJudgmentEngine()
    now = datetime.datetime.utcnow()

    planets = {
        Planet.JUPITER: PlanetPosition(
            planet=Planet.JUPITER,
            longitude=0.0,
            latitude=0.0,
            house=7,
            sign=Sign.SAGITTARIUS,
            dignity_score=5,
        ),
        Planet.MARS: PlanetPosition(
            planet=Planet.MARS,
            longitude=0.0,
            latitude=0.0,
            house=1,
            sign=Sign.ARIES,
            dignity_score=0,
        ),
        Planet.MERCURY: PlanetPosition(
            planet=Planet.MERCURY,
            longitude=0.0,
            latitude=0.0,
            house=1,
            sign=Sign.GEMINI,
            dignity_score=0,
        ),
        Planet.VENUS: PlanetPosition(
            planet=Planet.VENUS,
            longitude=0.0,
            latitude=0.0,
            house=3,
            sign=Sign.TAURUS,
            dignity_score=0,
        ),
    }

    chart = HoraryChart(
        date_time=now,
        date_time_utc=now,
        timezone_info="UTC",
        location=(0.0, 0.0),
        location_name="Test",
        planets=planets,
        aspects=[],
        houses=[i * 30 for i in range(12)],
        house_rulers={7: Planet.MARS},
        ascendant=0.0,
        midheaven=0.0,
    )

    result = engine._check_benefic_aspects_to_significators(
        chart, Planet.MERCURY, Planet.MARS
    )

    assert result["neutral"] is True
    assert result["total_score"] == 7
    assert any(entry["aspect"] is None for entry in result["aspects"])
    assert "Jupiter" in result["reason"]
