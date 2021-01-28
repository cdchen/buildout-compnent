# -*- coding: utf-8 -*-
#
# Buildout Component
# 
# All rights reserved by Cd Chen.
#
from datetime import datetime


def collect_result(context):
    config = context.config

    config['buildout']['extends'] = ['django.cfg', 'base.cfg']
    config['buildout']['eggs'] = ['django', 'foo']
    config['versions']['django'] = '>=1.8'

    config['foo'] = {'boo': 1234}

    return datetime.utcnow()
