# -*- coding: utf-8 -*-
#
# Buildout Component
# 
# All rights reserved by Cd Chen.
#
from datetime import datetime


def setup_option(context):
    config = context.config

    manifest = config.manifest

    config['buildout']['extends'] = [
        manifest.join('base.cfg'),
    ]
    config['buildout']['eggs'] = ['django', 'foo']
    config['buildout']['parts'] = 'foo'
    config['buildout'].operators['parts'] = '+='
    config['versions']['django'] = '>=1.8'

    return datetime.utcnow()
