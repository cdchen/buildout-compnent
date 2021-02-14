# -*- coding: utf-8 -*-
#
# Buildout Component
# 
# All rights reserved by Cd Chen.
#
import os
from datetime import datetime


def setup_option(context):
    config = context.config

    manifest = config.manifest

    config['buildout']['extends'] = [
        os.path.join(manifest.component_dir, 'base.cfg'),
    ]
    config['buildout']['eggs'] = ['django', 'foo']
    config['buildout']['parts'] = 'foo'
    config['buildout'].operators['parts'] = '+='
    config['versions']['django'] = '>=1.8'

    return datetime.utcnow()
