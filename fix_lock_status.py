#!/usr/bin/env python3
import os

file_path = '/opt/anaconda3/lib/python3.12/site-packages/linien_python_client-0.3.2-py3.12.egg/linien/gui/ui/lock_status_panel.py'

try:
    # Check if we have write permissions
    if os.access(file_path, os.W_OK):
        with open(file_path, 'r') as file:
            content = file.read()
        
        # Replace write_registers with write_data
        content = content.replace('write_registers', 'write_data')
        
        # Find and modify the update_status function to reverse the TTL logic
        content = content.replace(
            '# Send TTL signal when locked and not already active\n                if locked and not self.ttl_active:',
            '# REVERSED LOGIC: Deactivate TTL when locked and TTL is active\n                if locked and self.ttl_active:'
        )
        content = content.replace(
            'self.send_ttl_signal()',
            'self.restore_gpio_output()'
        )
        content = content.replace(
            '# Turn off TTL when unlocked\n                if self.ttl_active:',
            '# REVERSED LOGIC: Activate TTL when unlocked and TTL is not active\n                if not locked and not self.ttl_active:'
        )
        content = content.replace(
            'self.restore_gpio_output()',
            'self.send_ttl_signal()'
        )
        
        # Reverse logic in stop_lock function
        content = content.replace(
            '# Make sure TTL is turned off when manually stopping the lock\n        if self.ttl_active:',
            '# REVERSED LOGIC: Activate TTL when stopping the lock (since lock will be off)\n        if not self.ttl_active:'
        )
        
        # Add shutdown functionality
        # First, add the connection to aboutToQuit in ready method
        content = content.replace(
            'self.ids.control_signal_history_length.valueChanged.connect(self.control_signal_history_length_changed)',
            'self.ids.control_signal_history_length.valueChanged.connect(self.control_signal_history_length_changed)\n\n        # Connect to the application\'s aboutToQuit signal to turn off TTL on shutdown\n        app = QtWidgets.QApplication.instance()\n        app.aboutToQuit.connect(self.turn_off_ttl_on_shutdown)'
        )
        
        # Add the turn_off_ttl_on_shutdown method
        shutdown_method = '''\n    def turn_off_ttl_on_shutdown(self):
        """Turn off all GPIO pins (set to 0) when the application shuts down"""
        try:
            # Set all GPIO pins to 0 (both P and N)
            self.parameters.gpio_p_out.value = 0
            self.parameters.gpio_n_out.value = 0
            self.control.write_data()
            print("TTL signals turned off on shutdown")
        except Exception as e:
            print(f"Error turning off TTL on shutdown: {e}")'''
        
        # Add the method to the end of the class
        content = content.replace("            self.ttl_active = False", "            self.ttl_active = False" + shutdown_method)
        
        with open(file_path, 'w') as file:
            file.write(content)
        
        print('Successfully updated the file with reversed TTL logic and shutdown functionality!')
    else:
        print(f'Cannot write to {file_path}')
        print('You need administrator privileges. Try running with sudo.')
        
except Exception as e:
    print(f'An error occurred: {e}') 