# Copyright (c) 2025 @rmic
# Licensed under the terms of GNU GPL v2

def classFactory(iface):
    from .main_plugin import ConflationBridgePlugin
    return ConflationBridgePlugin(iface)