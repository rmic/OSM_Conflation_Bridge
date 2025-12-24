def classFactory(iface):
    from .main_plugin import ConflationBridgePlugin
    return ConflationBridgePlugin(iface)