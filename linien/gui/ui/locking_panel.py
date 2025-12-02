from PyQt5 import QtGui, QtWidgets
from linien.gui.widgets import CustomWidget
from linien.gui.utils_gui import param2ui
import time

class LockingPanel(QtWidgets.QWidget, CustomWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_ui('locking_panel.ui')

    def ready(self):
        # PID controls
        self.ids.kp.setKeyboardTracking(False)
        self.ids.kp.valueChanged.connect(self.kp_changed)
        self.ids.ki.setKeyboardTracking(False)
        self.ids.ki.valueChanged.connect(self.ki_changed)
        self.ids.kd.setKeyboardTracking(False)
        self.ids.kd.valueChanged.connect(self.kd_changed)

        # Check which tab we are in
        self.ids.lock_control_container.currentChanged.connect(self.lock_mode_changed)

        # Autolock tab checkboxes
        self.ids.checkLockCheckbox.stateChanged.connect(self.check_lock_changed)
        self.ids.watchLockCheckbox.stateChanged.connect(self.watch_lock_changed)
        self.ids.watch_lock_threshold.valueChanged.connect(self.watch_lock_threshold_changed)
        self.ids.autoOffsetCheckbox.stateChanged.connect(self.auto_offset_changed)

        # Parameters from actually clicking on the line using autolock
        self.ids.selectLineToLock.clicked.connect(self.start_autolock_selection)
        self.ids.abortLineSelection.clicked.connect(self.stop_autolock_selection)

        # Relock tab checkboxes
        self.ids.watchLockCheckbox_relock.stateChanged.connect(self.watch_relock_changed)
        self.ids.autoOffsetCheckbox_relock.stateChanged.connect(self.relock_auto_offset_changed)
        self.ids.STDthresholdbox_relock.valueChanged.connect(self.std_relock_threshold_changed)

        # Parameters from actually clicking on the line using relock
        self.ids.selectLineToRelock.clicked.connect(self.start_relock_selection)
        self.ids.abortRelockSelection.clicked.connect(self.stop_relock_selection)

        # Manual lock
        self.ids.manualLockButton.clicked.connect(self.start_manual_lock)

        self.ids.pid_on_slow_strength.setKeyboardTracking(False)
        self.ids.pid_on_slow_strength.valueChanged.connect(self.pid_on_slow_strength_changed)

        self.ids.reset_lock_failed_state.clicked.connect(self.reset_lock_failed)

    def connection_established(self):
        # Initialization
        params = self.app().parameters
        self.parameters = params
        self.control = self.app().control

        # GPIO parameters
        def gpio_update(*_):
            gpo = "GPIO P OUT: " + str(params.gpio_p_out.value)
            gno = "GPIO N OUT: " + str(params.gpio_n_out.value)
            self.ids.gpio_p_label.setText(gpo)
            self.ids.gpio_n_label.setText(gno)
        
        params.gpio_p_out.on_change(gpio_update)
        params.gpio_n_out.on_change(gpio_update)

        # error STD update
        std_update_time = 0
        def std_update(*_):
            nonlocal std_update_time
            now = time.time()
            if now - std_update_time < 0.5:  # only update every 0.5 s
                return
            std_update_time = now
            stdtext = "STD of error signal: " + str(params.gpio_p_out.value)
            self.ids.std_display.setText(stdtext)
        
        params.relock_std_val.on_change(std_update)
            
            
        # PID parameters
        param2ui(params.p, self.ids.kp)
        param2ui(params.i, self.ids.ki)
        param2ui(params.d, self.ids.kd)

        # Autolock parameters
        param2ui(params.check_lock, self.ids.checkLockCheckbox)
        param2ui(params.watch_lock, self.ids.watchLockCheckbox)
        param2ui(
            params.watch_lock_threshold,
            self.ids.watch_lock_threshold,
            lambda v: v * 100
        )
        param2ui(params.autolock_determine_offset, self.ids.autoOffsetCheckbox)

        # Relock parameters:
        param2ui(params.watch_relock, self.ids.watchLockCheckbox_relock)
        param2ui(
            params.watch_relock_threshold,
            self.ids.STDthresholdbox_relock,
            lambda v: v
        )
        param2ui(params.relock_determine_offset, self.ids.autoOffsetCheckbox_relock)

        # Handle the tab
        def _sync_tab_from_params(*_):
            # Decide the index from parameters
            if self.parameters.automatic_mode.value:
                idx = 0  # Auto
            elif self.parameters.relock_automatic_mode.value:
                idx = 1  # Relock
            else:
                idx = 2  # Manual

            # Avoid re-entrant fights by only updating when different
            if self.ids.lock_control_container.currentIndex() != idx:
                self.ids.lock_control_container.setCurrentIndex(idx)

        # Subscribe to param changes
        self.parameters.automatic_mode.on_change(_sync_tab_from_params)
        self.parameters.relock_automatic_mode.on_change(_sync_tab_from_params)

        #Slow PID
        param2ui(params.pid_on_slow_strength, self.ids.pid_on_slow_strength)
        def slow_pid_visibility(*args):
            self.ids.slow_pid_group.setVisible(self.parameters.pid_on_slow_enabled.value)
        params.pid_on_slow_enabled.on_change(slow_pid_visibility)

        def lock_status_changed(_):
            locked = params.lock.value
            task = params.task.value
            al_failed = params.autolock_failed.value
            rl_failed = params.relock_failed.value
            task_running = (task is not None) and (not al_failed) and (not rl_failed)

            if locked or task_running:
                self.ids.lock_control_container.hide()
            else:
                self.ids.lock_control_container.show()

            if al_failed:
                self.ids.lock_failed.setVisible(al_failed)
            elif rl_failed:
                self.ids.lock_failed.setVisible(rl_failed)
            else:
                self.ids.lock_failed.setVisible(False)

        for param in (params.lock, params.autolock_approaching, params.autolock_watching,
                      params.autolock_failed, params.autolock_locked, 
                      params.relock_approaching, params.relock_watching,
                      params.relock_failed, params.relock_locked):
            param.on_change(lock_status_changed)

        param2ui(params.target_slope_rising, self.ids.button_slope_rising)
        param2ui(
            params.target_slope_rising,
            self.ids.button_slope_falling,
            lambda value: not value
        )

        def autolock_selection_status_changed(value):
            self.ids.auto_mode_activated.setVisible(value)
            self.ids.auto_mode_not_activated.setVisible(not value)
        params.autolock_selection.on_change(autolock_selection_status_changed)

        def relock_selection_status_changed(value):
            self.ids.relock_activated.setVisible(value)
            self.ids.relock_not_activated.setVisible(not value)
        params.relock_selection.on_change(relock_selection_status_changed)
    
    # PID tab interactions
    def kp_changed(self):
        self.parameters.p.value = self.ids.kp.value()
        self.control.write_data()

    def ki_changed(self):
        self.parameters.i.value = self.ids.ki.value()
        self.control.write_data()

    def kd_changed(self):
        self.parameters.d.value = self.ids.kd.value()
        self.control.write_data()

    def lock_mode_changed(self, idx):
        self.parameters.automatic_mode.value = idx == 0
        self.parameters.relock_automatic_mode.value = idx == 1

    def start_manual_lock(self):
        self.control.pause_acquisition()
        self.parameters.target_slope_rising.value = self.ids.button_slope_rising.isChecked()
        self.parameters.fetch_quadratures.value = False
        self.control.write_data()
        self.control.start_lock()
        self.control.continue_acquisition()

    # Autolock tab interactions
    def check_lock_changed(self):
        self.parameters.check_lock.value = int(self.ids.checkLockCheckbox.checkState())

    def watch_lock_changed(self):
        self.parameters.watch_lock.value = int(self.ids.watchLockCheckbox.checkState())

    def auto_offset_changed(self):
        self.parameters.autolock_determine_offset.value = int(self.ids.autoOffsetCheckbox.checkState())

    def pid_on_slow_strength_changed(self):
        self.parameters.pid_on_slow_strength.value = self.ids.pid_on_slow_strength.value()
        self.control.write_data()

    def start_autolock_selection(self):
        self.parameters.autolock_selection.value = True

    def stop_autolock_selection(self):
        self.parameters.autolock_selection.value = False

    def watch_lock_threshold_changed(self):
        self.parameters.watch_lock_threshold.value = self.ids.watch_lock_threshold.value() / 100.0

    def reset_lock_failed(self):
        self.parameters.autolock_failed.value = False
        self.parameters.relock_failed.value = False

    # Relock tab interactions
    def watch_relock_changed(self):
        self.parameters.watch_relock.value = int(self.ids.watchLockCheckbox_relock.checkState())

    def relock_auto_offset_changed(self):
        self.parameters.relock_determine_offset.value = int(self.ids.autoOffsetCheckbox_relock.checkState())

    def start_relock_selection(self):
        self.parameters.relock_selection.value = True

    def stop_relock_selection(self):
        self.parameters.relock_selection.value = False

    def std_relock_threshold_changed(self):
        self.parameters.watch_relock_threshold.value = self.ids.STDthresholdbox_relock.value()