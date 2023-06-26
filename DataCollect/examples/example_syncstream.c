tatic int init_sync(struct bladerf *dev)
{
 int status;
 
 /* These items configure the underlying asynch stream used by the sync
 * interface. The "buffer" here refers to those used internally by worker
 * threads, not the user's sample buffers.
 *
 * It is important to remember that TX buffers will not be submitted to
 * the hardware until `buffer_size` samples are provided via the
 * bladerf_sync_tx call. Similarly, samples will not be available to
 * RX via bladerf_sync_rx() until a block of `buffer_size` samples has been
 * received.
 */
 const unsigned int num_buffers = 16;
 const unsigned int buffer_size = 8192; /* Must be a multiple of 1024 */
 const unsigned int num_transfers = 8;
 const unsigned int timeout_ms = 3500;
 
 /* Configure both the device's x1 RX and TX channels for use with the
 * synchronous
 * interface. SC16 Q11 samples *without* metadata are used. */
 
 status = bladerf_sync_config(dev, BLADERF_RX_X1, BLADERF_FORMAT_SC16_Q11,
 num_buffers, buffer_size, num_transfers,
 timeout_ms);
 if (status != 0) {
 fprintf(stderr, "Failed to configure RX sync interface: %s\n",
 bladerf_strerror(status));
 return status;
 }
 
 status = bladerf_sync_config(dev, BLADERF_TX_X1, BLADERF_FORMAT_SC16_Q11,
 num_buffers, buffer_size, num_transfers,
 timeout_ms);
 if (status != 0) {
 fprintf(stderr, "Failed to configure TX sync interface: %s\n",
 bladerf_strerror(status));
 }
 
 return status;
}
 
int sync_rx_example(struct bladerf *dev)
{
 int status, ret;
 bool done = false;
 bool have_tx_data = false;
 
 /* "User" samples buffers and their associated sizes, in units of samples.
 * Recall that one sample = two int16_t values. */
 int16_t *rx_samples = NULL;
 int16_t *tx_samples = NULL;
 const unsigned int samples_len = 10000; /* May be any (reasonable) size */
 
 /* Allocate a buffer to store received samples in */
 rx_samples = malloc(samples_len * 2 * 1 * sizeof(int16_t));
 if (rx_samples == NULL) {
 perror("malloc");
 return BLADERF_ERR_MEM;
 }
 
 /* Allocate a buffer to prepare transmit data in */
 tx_samples = malloc(samples_len * 2 * 1 * sizeof(int16_t));
 if (tx_samples == NULL) {
 perror("malloc");
 free(rx_samples);
 return BLADERF_ERR_MEM;
 }
 
 /* Initialize synch interface on RX and TX */
 status = init_sync(dev);
 if (status != 0) {
 goto out;
 }
 
 status = bladerf_enable_module(dev, BLADERF_RX, true);
 if (status != 0) {
 fprintf(stderr, "Failed to enable RX: %s\n", bladerf_strerror(status));
 goto out;
 }
 
 status = bladerf_enable_module(dev, BLADERF_TX, true);
 if (status != 0) {
 fprintf(stderr, "Failed to enable TX: %s\n", bladerf_strerror(status));
 goto out;
 }
 
 while (status == 0 && !done) {
 /* Receive samples */
 status = bladerf_sync_rx(dev, rx_samples, samples_len, NULL, 5000);
 if (status == 0) {
 /* Process these samples, and potentially produce a response
 * to transmit */
 done = do_work(rx_samples, samples_len, &have_tx_data, tx_samples,
 samples_len);
 
 if (!done && have_tx_data) {
 /* Transmit a response */
 status =
 bladerf_sync_tx(dev, tx_samples, samples_len, NULL, 5000);
 
 if (status != 0) {
 fprintf(stderr, "Failed to TX samples: %s\n",
 bladerf_strerror(status));
 }
 }
 } else {
 fprintf(stderr, "Failed to RX samples: %s\n",
 bladerf_strerror(status));
 }
 }
 
 if (status == 0) {
 /* Wait a few seconds for any remaining TX samples to finish
 * reaching the RF front-end */
 usleep(2000000);
 }
 
out:
 ret = status;
 
 /* Disable RX, shutting down our underlying RX stream */
 status = bladerf_enable_module(dev, BLADERF_RX, false);
 if (status != 0) {
 fprintf(stderr, "Failed to disable RX: %s\n", bladerf_strerror(status));
 }
 
 /* Disable TX, shutting down our underlying TX stream */
 status = bladerf_enable_module(dev, BLADERF_TX, false);
 if (status != 0) {
 fprintf(stderr, "Failed to disable TX: %s\n", bladerf_strerror(status));
 }
 
 
 /* Free up our resources */
 free(rx_samples);
 free(tx_samples);
 
 return ret;
}
