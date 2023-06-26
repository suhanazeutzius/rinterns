nt status;
bladerf_channel channel = BLADERF_CHANNEL_RX(0);
bladerf_trigger_signal signal = BLADERF_TRIGGER_J71_4;
 
// Allocate and initialize a bladerf_trigger structure for each
// trigger in the system.
struct bladerf_trigger trig_master, trig_slave;
 
status = bladerf_trigger_init(dev_master, channel, signal, &trig_master);
if (status == 0) {
 trig_master.role = BLADERF_TRIGGER_ROLE_MASTER;
} else {
 goto handle_error;
}
 
status = bladerf_trigger_init(dev_slave1, channel, signal, &trig_slave);
if (status == 0) {
 master_rx.role = BLADERF_TRIGGER_ROLE_SLAVE;
} else {
 goto handle_error;
}
 
// Arm the triggering functionality on each device
status = bladerf_trigger_arm(dev_master, &trig_master, true, 0, 0);
if (status != 0) {
 goto handle_error;
}
 
status = bladerf_trigger_arm(dev_slave, &trig_slave, true, 0, 0);
if (status != 0) {
 goto handle_error;
}
 
// Call bladerf_sync_config() and bladerf_sync_rx() on each device.
// Ensure the timeout parameters used are long enough to accommodate
// the expected time until the trigger will be fired.
status = start_rx_streams(dev_master, dev_slave);
if (status != 0) {
 goto handle_error;
}
 
// Fire the trigger signal
status = bladerf_trigger_fire(dev_master, &trig_master);
if (status != 0) {
 goto handle_error;
}
 
// Handle RX signals and then shut down streams.
// Synchronized samples should now be reaching the host following the
// reception of the external trigger signal.
status = handle_rx_operations(dev_master, dev_slave);
if (status != 0) {
 goto handle_error;
}
 
// Disable triggering on all devices to restore normal RX operation
trig_master.role = BLADERF_TRIGGER_ROLE_DISABLED;
status = bladerf_trigger_arm(dev_master, &trig_master, false, 0, 0);
if (status != 0) {
 goto handle_error;
}
 
trig_slave.role = BLADERF_TRIGGER_ROLE_DISABLED;
status = bladerf_trigger_arm(dev_master, &trig_slave, false, 0, 0);
if (status != 0) {
 goto handle_error;
}
