# -*- coding: utf-8 -*-
#
# Buildout Component
# 
# All rights reserved by Cd Chen.
#
def setup_option(context):
    config = context.config
    config['foo'] = {
        'coo': 5678,
    }

    return 1234
