# -*- coding: utf-8 -*-
#
# Buildout Component
# 
# All rights reserved by Cd Chen.
#


class DuplicateVersionConfigError(ValueError):
    pass


class ImmutableValueError(ValueError):
    pass


class ImmutableAttributeError(AttributeError):
    pass
