#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2013 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
This module for initialize project.
"""
import os
import sys
import transaction
from subprocess import PIPE, Popen

from jinja2.utils import generate_lorem_ipsum
from pyramid.paster import get_appsettings, setup_logging
from sqlalchemy import engine_from_config

from example.lib.fixture import add_fixture
from example.models import Base, DBSession
from example.models.auth import Company, User
from example.models.funny_models import (TestAllTypes, TestBOOL,
                                         TestCustomizing, TestDND, TestFile,
                                         TestHSTORE, TestTEXT, TestUNION)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def add_hstore():
    hashes = ({'foo': {'foo': 'bar', '1': '2'}},
              {'foo': {'test': 'data'}})
    add_fixture(TestHSTORE, hashes)


def add_bool():
    booles = ({'foo': True},
              {'foo': False})
    add_fixture(TestBOOL, booles)


def add_text():
    text = []
    for i in range(100):
        try:
            out = Popen(["fortune", ""], stdout=PIPE).communicate()[0]
        except OSError:
            out = generate_lorem_ipsum()
        text.append({'foo': out, 'ufoo': out, 'fooText': out, 'ufooText': out})
    add_fixture(TestTEXT, text)


def add_dnd():
    dnd = ({'name': 'foo', 'value': 1, 'position1': 1},
           {'name': 'foo1', 'value': 2, 'position1': 2},
           {'name': 'foo2', 'value': 3, 'position1': 3},
           {'name': 'foo3', 'value': 4, 'position1': 4},
           {'name': 'foo4', 'value': 5, 'position1': 5},
           {'name': 'foo5', 'value': 6, 'position1': 6})
    add_fixture(TestDND, dnd)


def add_union():
    uni = ({'name': 'foo',  'foo': True,  'cash': 100, 'double_cash': 100.13},
           {'name': 'foo1', 'foo': False, 'cash': 200, 'double_cash': 100.500},
           {'name': 'foo2', 'foo': True,  'cash': 1024, 'double_cash': 100.13},
           {'name': 'foo3', 'foo': False, 'cash': 100500, 'double_cash': 1.13},
           {'name': 'foo4', 'foo': False, 'cash': 19, 'double_cash': 6660.10},
           {'name': 'foo5', 'foo': True,  'cash': -123, 'double_cash': 130.03})
    add_fixture(TestUNION, uni)


def add_alltypes():
    objs = ({}, {}, {}, {}, {})
    add_fixture(TestAllTypes, objs)


def add_customizing():
    import random
    objs = [{'name': ('%06x' % random.randrange(16 ** 6)).upper()} for x in range(10)]
    add_fixture(TestCustomizing, objs)


def add_file():
    objs = [{'image': '/static/upload/60563666-c52a-4ec2-bc31-e21f9dcde296.gif'}]
    add_fixture(TestFile, objs)


def add_extension(engine, *args):
    """
    Add extension to PostgreSQL database.
    """
    conn = engine.connect()
    for ext in args:
        conn.execute('CREATE EXTENSION IF NOT EXISTS "%s"' % ext)
    conn.execute('COMMIT')
    conn.close()


def add_company():
    company = (
        {'name': u'ITCase'},
        {'name': u'RedHat'},
        {'name': u'Canonical'},
        {'name': u'Pylons'},
    )
    add_fixture(Company, company)


def init_user():
    new_user = User(user_name='admin', email="email@email.com")
    new_user.regenerate_security_code()
    new_user.status = 1
    new_user.set_password(u"123")
    new_user.name = 'admin'
    new_user.surname = 'admin'
    new_user.middlename = 'admin'
    new_user.type_id = 1
    new_user.company_id = 1
    DBSession.add(new_user)
    transaction.commit()


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    # drop database
    Base.metadata.drop_all(engine)
    # add postgres extension
    add_extension(engine, "plpythonu", "hstore", "uuid-ossp")

    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    add_hstore()
    add_bool()
    add_dnd()
    add_text()
    add_union()
    add_alltypes()
    add_customizing()
    add_file()

    # Auth
    add_company()
    init_user()
