from PyQt5 import QtGui, QtWidgets, QtWidgets
from linien.gui.widgets import CustomWidget


class RightPanel(QtWidgets.QWidget, CustomWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def connection_established(self):
        self.control = self.app().control
        self.parameters = self.app().parameters

        self.parameters.autolock_running.on_change(self.autolock_status_changed)
        self.parameters.relock_running.on_change(self.relock_status_changed) # New relock initialization
        self.parameters.optimization_running.on_change(self.optimization_status_changed)
        self.parameters.lock.on_change(self.enable_or_disable_panels)

    def ready(self):
        self.ids.closeButton.clicked.connect(self.close_app)
        self.ids.shutdownButton.clicked.connect(self.shutdown_server)
        self.ids.openDeviceManagerButton.clicked.connect(self.open_device_manager)

    def close_app(self):
        self.app().close()

    def shutdown_server(self):
        self.app().shutdown()

    def open_device_manager(self):
        self.app().open_device_manager()

    def autolock_status_changed(self, value):
        if value:
            self.ids.settings_toolbox.setCurrentWidget(self.ids.lockingPanel)

        self.enable_or_disable_panels()

    def optimization_status_changed(self, value):
        if value:
            self.ids.settings_toolbox.setCurrentWidget(self.ids.optimizationPanel)

        self.enable_or_disable_panels()

    def relock_status_changed(self, value):
        if value:
            # Show the same Locking Panel, since relock shares it
            self.ids.settings_toolbox.setCurrentWidget(self.ids.lockingPanel)

        self.enable_or_disable_panels()

    def enable_or_disable_panels(self, *args):
        lock = self.parameters.lock.value
        autolock = self.parameters.autolock_running.value
        relock = self.parameters.relock_running.value
        optimization = self.parameters.optimization_running.value

        def enable_panels(panel_names, condition):
            for panel_name in panel_names:
                getattr(self.ids, panel_name).setEnabled(condition)

        # Disable general panel while any task or lock is active
        enable_panels(('generalPanel',), not autolock and not relock and not optimization and not lock)

        # Disable spectroscopy/view/locking while optimization is running
        enable_panels(('modSpectroscopyPanel', 'viewPanel', 'lockingPanel'), not optimization)

        # Disable optimization panel while autolock, relock, or lock are active
        enable_panels(('optimizationPanel',), not autolock and not relock and not lock)
        