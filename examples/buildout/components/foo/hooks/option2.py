# -*- coding: utf-8 -*-
#
# Buildout Component
# 
# All rights reserved by Cd Chen.
#

def setup_option(context):
    config = context.config
    config['foo'] = {
        'goo': 'ABCD',
    }

    return {
        'option2_1': '21',
        'option2_2': '22',
    }
