#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2013 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
helper for SQLAlchemy fixtures in Pyramid
"""

import transaction
from random import randint
from ..models import DBSession


def add_fixture(model, fixtures):
    """
    Add fixtures to database.

    Example::

    hashes = ({'foo': {'foo': 'bar', '1': '2'}}, {'foo': {'test': 'data'}})
    add_fixture(TestHSTORE, hashes)
    """
    with transaction.manager:
        DBSession.query(model).delete()
        for fixture in fixtures:
            DBSession.add(model(**fixture))


def rand_id(model):
    qty = len(DBSession.query(model).all())
    return randint(1, qty)
