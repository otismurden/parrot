from shop.pricing import late_fee


def test_late_fee_small():
    days = 2
    result = late_fee(days)
    assert result == 5.0
    assert result >= 0


def test_late_fee_capped():
    days = 100
    result = late_fee(days)
    assert result == 50
    assert result >= 0
