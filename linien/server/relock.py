import pickle
import traceback
import numpy as np
from linien.common import get_lock_point, combine_error_signal, \
    check_plot_data, ANALOG_OUT0, SpectrumUncorrelatedException, determine_shift_by_correlation
from linien.server.approach_line import Approacher


class Relock:
    """Relocking (triggering TTL) based on relock."""
    def __init__(self, control, parameters, wait_time_between_current_corrections=None):
        self.control = control
        self.parameters = parameters

        self.first_error_signal = None
        self.parameters.relock_running.value = False
        self.parameters.relock_retrying.value = False

        self.should_watch_relock = False
        self.approacher = None
        self._data_listener_added = False

        self.reset_properties()

        # Set PID lock status to false in initialization because I'm paranoid
        self.parameters.lock.value = False
        
        # Don't need to send lockbox TTL high here because the initialization in lock_status_panel already initializes that

        # Set counter for # of failed check lock and failed lock attempts to 0
        self.failed_check_attempts = 0
        self.failed_lock_attempts = 0

        self.wait_time_between_current_corrections = wait_time_between_current_corrections

    def reset_properties(self):
        # we check each parameter before setting it because otherwise
        # this may crash the client if called very often (e.g.if the
        # relock continuously fails)
        if self.parameters.relock_failed.value:
            self.parameters.relock_failed.value = False
        if self.parameters.relock_locked.value:
            self.parameters.relock_locked.value = False
        if self.parameters.relock_watching.value:
            self.parameters.relock_watching.value = False

        if self.approacher:
            self.approacher.reset_properties()

    def run(self, x0, x1, spectrum, should_watch_relock=False, auto_offset=True):
        """Starts the relock.

        If `should_watch_relock` is specified, the relock continuously monitors
        the control and error signals after the lock was successful and tries to
        relock automatically using the spectrum that was recorded in the first
        run of the lock.
        """
        print("RUNNING RELOCK!")
        self.parameters.relock_running.value = True
        self.parameters.fetch_quadratures.value = False
        self.x0, self.x1 = int(x0), int(x1)
        self.should_watch_relock = should_watch_relock
        self.auto_offset = auto_offset    

        # Send TTL to lockbox to make it go into ramp mode
        self.send_lockbox_TTL(locked=False)

        self.parameters.relock_approaching.value = True
        self.record_first_error_signal(spectrum)

        self.initial_ramp_speed = self.parameters.ramp_speed.value
        self.parameters.relock_initial_ramp_amplitude.value = self.parameters.ramp_amplitude.value
        self.initial_ramp_center = self.parameters.center.value

        self.add_data_listener()

    def add_data_listener(self):
        if not self._data_listener_added:
            self._data_listener_added = True
            self.parameters.to_plot.on_change(self.react_to_new_spectrum)

    def remove_data_listener(self):
        self._data_listener_added = False
        self.parameters.to_plot.remove_listener(self.react_to_new_spectrum)

    def react_to_new_spectrum(self, plot_data):
        """React to new spectrum data.

        If this is executed for the first time, a reference spectrum is
        recorded.

        If the relock is approaching the desired line, a correlation
        function of the spectrum with the reference spectrum is calculated
        and the laser current is adapted such that the targeted line is centered.

        After this procedure is done, the real lock is turned on and after some
        time the lock is verified.

        If automatic relocking is desired, the control and error signals are
        continuously monitored after locking.
        """
        if self.parameters.pause_acquisition.value:
            return

        if plot_data is None or not self.parameters.relock_running.value:
            return

        plot_data = pickle.loads(plot_data)
        if plot_data is None:
            return

        # No longer have access to PID status, no need for this
        # is_locked = self.parameters.lock.value

        # check that `plot_data` contains the information we need
        # otherwise skip this round
        # Manually feeding in False because the PID loop will never engage
        if not check_plot_data(False, plot_data):
            return

        # Only this case necessary because the PID loop will never engage
        combined_error_signal = combine_error_signal(
            (plot_data['error_signal_1'], plot_data['error_signal_2']),
            self.parameters.dual_channel.value,
            self.parameters.channel_mixing.value,
            self.parameters.combined_offset.value
            )

        try:
            if self.parameters.relock_approaching.value:
                # we have already recorded a spectrum and are now approaching
                # the line by decreasing the scan range and adapting the
                # center current multiple times.
                if self.approacher is None:
                    print("ZOOM TARGET: " + str(self.target_zoom))
                    self.approacher = Approacher(
                        self.control, self.parameters, self.first_error_signal,
                        self.target_zoom, self.central_y,
                        allow_ramp_speed_change=True,
                        wait_time_between_current_corrections=self.wait_time_between_current_corrections
                    )
                approaching_finished = self.approacher.approach_line(combined_error_signal)
                if approaching_finished:
                    print("Attempting lock... ")
                    self._lock()

            else:
                print("Checking lock...")
                # either just started lock or have been in lock for a while. check if still in lock with new function
                return self.check_lock(combined_error_signal)

        # This is the only way to tell if the locking failed.
        # This is called if _lock() cannot find the original error signal again using its correlation function
        except SpectrumUncorrelatedException:
            print('Spectrum uncorrelated')
            if self.parameters.watch_relock.value:
                print('retry')
                self.relock()
            else:
                self.exposed_stop()
                self.parameters.relock_failed.value = True

        except Exception:
            traceback.print_exc()
            self.exposed_stop()

    def record_first_error_signal(self, error_signal):
        mean_signal, target_slope_rising, calculated_zoom, rolled_error_signal = \
            get_lock_point(error_signal, self.x0, self.x1)
        target_zoom = min(calculated_zoom, 4) # Prevents too large target_zoom

        self.central_y = mean_signal

        self.parameters.target_slope_rising.value = target_slope_rising
        self.control.exposed_write_data()

        self.target_zoom = target_zoom
        self.first_error_signal = rolled_error_signal

    def check_lock(self, combined_error_signal):
        # --- correlation check ---
        try:
            determine_shift_by_correlation(
                self.target_zoom, self.first_error_signal, combined_error_signal
            )
        except SpectrumUncorrelatedException:
            reason = "Correlation failure! Error signal too different from reference!"
            return self._handle_failed_lock(reason)

        # --- standard deviation check ---
        std_val = np.std(combined_error_signal)
        self.parameters.relock_std_val = std_val
        if std_val < self.parameters.watch_relock_threshold.value:
            reason = "Low signal standard deviation: " + str(std_val)
            return self._handle_failed_lock(reason)

        # --- if both tests passed ---
        print("Lock Check OK!")
        self.failed_check_attempts = 0

    def _handle_failed_lock(self, reason):
        print("Lock check failed: " + reason)
        self.failed_check_attempts += 1
        print("Number of failed relock attempts: " + str(self.failed_check_attempts))

        if self.failed_check_attempts >= 5: # Check 5 times to see if it's really gone
            print("Lock dropped. Attempting to relock")
            self.relock()
            # Checking failed rip, relock
            
            
    def relock(self):
        """
        Relock the laser using the reference spectrum recorded in the first
        locking approach.
        """
        # we check each parameter before setting it because otherwise
        # this may crash the client if called very often (e.g.if the
        # relock continuously fails)
        if not self.parameters.relock_running.value:
            self.parameters.relock_running.value = True
        if not self.parameters.relock_approaching.value:
            self.parameters.relock_approaching.value = True
        if not self.parameters.relock_retrying.value:
            self.parameters.relock_retrying.value = True

        self.reset_properties()
        self._reset_scan()

        # add a listener that listens for new spectrum data and consequently
        # tries to relock.
        self.add_data_listener()

    def exposed_stop(self):
        """Abort any operation."""
        self.parameters.relock_running.value = False
        self.parameters.relock_locked.value = False
        self.parameters.relock_approaching.value = False
        self.parameters.relock_watching.value = False
        self.parameters.fetch_quadratures.value = True
        self.remove_data_listener()

        self._reset_scan()
        self.parameters.task.value = None

    def _lock(self):
        self.control.pause_acquisition()

        # acquisition in locked state doesn't care about ramp speed
        # therefore, we can reset it here
        self.parameters.ramp_speed.value = self.initial_ramp_speed
        self.parameters.relock_approaching.value = False

        if self.auto_offset:
            # note: we only set the offset directly before turning on the lock
            # and not when approaching because this would cause problems in approacher
            self.parameters.combined_offset.value = -1 * self.central_y

        # Instead of starting PID loop, send TTL through GPIO
        # self.control.exposed_start_lock()
        self.send_lockbox_TTL(locked=True)
        
        self.control.continue_acquisition()

    def _reset_scan(self):
        self.control.pause_acquisition()

        ### New line to reset GPIO TTLs
        self.send_lockbox_TTL(locked=False)

        self.parameters.center.value = self.initial_ramp_center
        self.parameters.ramp_amplitude.value = self.parameters.relock_initial_ramp_amplitude.value
        self.parameters.ramp_speed.value = self.initial_ramp_speed
        self.control.exposed_start_ramp()

        self.control.continue_acquisition()


    def send_lockbox_TTL(self, locked=False):
        """ Sends GPIO 0V if relock succeeds, GPIO 3.3V if relock fails """

        # Store original GPIO values if not already stored
        # if not hasattr(self, 'original_gpio_p'):
        #     self.original_gpio_p = self.parameters.gpio_p_out.value
        #     self.original_gpio_n = self.parameters.gpio_n_out.value
        
        if locked:
            # Restore original GPIO values when locked
            # if hasattr(self, 'original_gpio_p') and hasattr(self, 'original_gpio_n'):
            #     self.parameters.gpio_p_out.value = self.original_gpio_p
            #     self.parameters.gpio_n_out.value = self.original_gpio_n
            #     self.control.exposed_write_data()
            self.parameters.gpio_p_out.value = 0b00000000
            self.parameters.gpio_n_out.value = 0b00000000
            self.control.exposed_write_data()

        else:
            # Store original GPIO values if not already stored
            # if not hasattr(self, 'original_gpio_p'):
            #     self.original_gpio_p = self.parameters.gpio_p_out.value
            #     self.original_gpio_n = self.parameters.gpio_n_out.value
            
            # Set all GPIO pins high (both P and N) when unlocked
            self.parameters.gpio_p_out.value = 0b11111111
            self.parameters.gpio_n_out.value = 0b11111111
            self.control.exposed_write_data()