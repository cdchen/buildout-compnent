# -*- coding: utf-8 -*-
#
# Buildout Component
# 
# All rights reserved by Cd Chen.
#
from collections import OrderedDict

from buildout_component.errors import ImmutableAttributeError
from buildout_component.models import Manifest

_readonly_context_names = ('manifest', 'config', 'options', 'collected')
_force_manifest_id = lambda m: m.id if isinstance(m, Manifest) else m


class Context(object):
    """

        context
            manifest
            config
            defaults
            collected
                <manifest.id>
                    config
                    options

    """

    def __init__(self):
        self.manifest = None
        self.config = OrderedDict()
        self.options = OrderedDict()
        self.defaults = OrderedDict()
        self.collected = OrderedDict()

    def __delattr__(self, key):
        if key in _readonly_context_names:
            raise ImmutableAttributeError("Can not delete `name` attribute.".format(name=key))
        super().__delattr__(key)

    def __repr__(self):
        return '{class_name}(manifest={manifest}, config={config}, options={options}, collected={collected})'.format(
            class_name=self.__class__.__name__,
            manifest=repr(self.manifest),
            config=repr(self.config),
            options=repr(self.options),
            collected=repr(self.collected),
        )

    def get_collected_option(self, manifest, name, default=None):
        manifest = _force_manifest_id(manifest)
        options = self.collected.get(manifest, {})
        return options.get(name, default=default)

    def get_collected_config(self, manifest):
        manifest = _force_manifest_id(manifest)
        return self.collected.get(manifest)
