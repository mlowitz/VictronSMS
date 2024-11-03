import pytest

from VictronProcessors.processor import (
    Item,
    TankValue,
    addWarnings,
    process,
    processTanks,
)


def test_addWarnings_low_level():
    tank_data = [
        TankValue(customName="Diesel Tank", value="20%", type="Diesel"),
        TankValue(
            customName="Fresh Water Tank", value="25%", type="Fresh water"
        ),
    ]
    warnings = addWarnings(tank_data)
    assert len(warnings) == 2
    assert "Warning  Diesel Tank Low Level" in warnings
    assert "Warning  Fresh Water Tank Low Level" in warnings


def test_addWarnings_high_level():
    tank_data = [
        TankValue(
            customName="Sewage Tank", value="80%", type="Black water (sewage)"
        ),
    ]
    warnings = addWarnings(tank_data)
    assert len(warnings) == 1
    assert "Warning  Sewage Tank High Level" in warnings


def test_processTanks():
    tank_data = [
        TankValue(customName="Diesel Tank", value="50%", type="Diesel"),
        TankValue(
            customName="Fresh Water Tank", value="75%", type="Fresh water"
        ),
    ]
    sentences = processTanks(tank_data)
    assert len(sentences) == 2
    assert "Diesel Tank = 50%" in sentences
    assert "Fresh Water Tank = 75%" in sentences


def test_process():
    item = Item(
        phoneNumber="1234567890",
        boatName="Test Boat",
        installationName="Test Installation",
        freshWater1="50%",
        freshWater2="60%",
        lpg1="70%",
        lpg2="80%",
        batterySOC="90%",
        poop="30%",
        diesel="40%",
        tanks=[
            TankValue(customName="Diesel Tank", value="40%", type="Diesel"),
            TankValue(
                customName="Fresh Water Tank", value="50%", type="Fresh water"
            ),
            TankValue(
                customName="Sewage Tank",
                value="80%",
                type="Black water (sewage)",
            ),
        ],
    )
    report = process(item)
    assert "Status Report for Test Boat" in report
    assert "Warning  Sewage Tank High Level" in report
    assert "Battery = 90%" in report
    assert "Diesel Tank = 40%" in report
    assert "Fresh Water Tank = 50%" in report
    assert "Sewage Tank = 80%" in report
