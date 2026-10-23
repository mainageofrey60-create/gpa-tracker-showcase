"""Illustrative snippet written for this showcase (not copied from the private source).

Idea: marks are rounded half-up with exact decimals. Python's float round() uses
banker's rounding on binary floats, which can put a mark on the wrong side of a boundary.
"""
from decimal import Decimal, ROUND_HALF_UP


def round_half_up(value, places=2):
    """round_half_up('0.125') -> Decimal('0.13'). Pass strings or Decimals, not floats."""
    step = Decimal(1).scaleb(-places)
    return Decimal(str(value)).quantize(step, rounding=ROUND_HALF_UP)


if __name__ == "__main__":
    print(round(0.125, 2))            # 0.12  (float, banker's rounding)
    print(round_half_up("0.125"))     # 0.13  (exact, half-up)
    print(round_half_up("59.995"))    # 60.00
