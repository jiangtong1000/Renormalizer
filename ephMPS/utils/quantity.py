# -*- coding: utf-8 -*-
# Author: Jiajun Ren <jiajunren0522@gmail.com>
#         Weitang Li <liwt31@163.com>

from __future__ import division

import logging

from ephMPS.utils import constant

logger = logging.getLogger(__name__)

au_ratio_dict = {
    "meV": constant.au2ev * 1e3,
    "eV": constant.au2ev,
    "cm^{-1}": 1 / constant.cm2au,
    "cm-1": 1 / constant.cm2au,
    "K": constant.au2K,
    "a.u.": 1,
    "au": 1,
}

au_ratio_dict.update({k.lower(): v for k, v in au_ratio_dict.items()})

allowed_units = set(au_ratio_dict.keys())


def convert_to_au(num, unit):
    assert unit in allowed_units
    return num / au_ratio_dict[unit]


class Quantity(object):
    def __init__(self, value, unit="a.u."):
        self.value = float(value)
        if unit not in allowed_units:
            raise ValueError("Unit not in {}, got {}.".format(allowed_units, unit))
        if value < 0.1 and value != 0 and (unit == "K" or unit == "k"):
            msg = "temperature too low and might cause various numerical errors"
            # raise ValueError("temperature too low and might cause various numerical errors")
            logger.warning(msg)
            # such low temperature will lead to very large x in exact propagator
        self.unit = unit

    def as_au(self):
        return convert_to_au(self.value, self.unit)

    # kelvin to beta  au^-1
    def to_beta(self):
        return 1.0 / self.as_au()

    # a simplified and incomplete model for + - * /
    # + - only allowed between Quantities
    # * / only allowed between Quantities and non-Quantities
    # todo: retain their own unit

    def __neg__(self):
        self.value = -self.value
        return self

    def __add__(self, other):
        assert isinstance(other, Quantity)
        return Quantity(self.as_au() + other.as_au())

    def __sub__(self, other):
        assert isinstance(other, Quantity)
        return Quantity(self.as_au() - other.as_au())

    def __mul__(self, other):
        assert not isinstance(other, Quantity)
        return Quantity(self.as_au() * other)

    def __rmul__(self, other):
        assert not isinstance(other, Quantity)
        return Quantity(self.as_au() * other)

    def __truediv__(self, other):
        assert not isinstance(other, Quantity)
        return Quantity(self.as_au() / other)

    def __eq__(self, other):
        if hasattr(other, "as_au"):
            return abs (self.as_au() - other.as_au()) < 1e-10
        elif other == 0:
            return self.value == 0
        else:
            raise TypeError(
                "Quantity can only compare with Quantity or 0, not {}".format(
                    other.__class__
                )
            )

    def __ne__(self, other):
        return not self == other

    # todo: magic methods such as `__lt__` and so on

    def __str__(self):
        return "%g %s" % (self.value, self.unit)
