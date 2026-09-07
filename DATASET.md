# Example dataset and processing

## Scope and selection

Three trials, two receivers, 40 seconds per receiver per trial. All trials use
the same recorded configuration: classic ESP32, channel 6, requested 50 Hz TX,
230400 baud. The source study's one qualifying empty trial and both qualifying
cross-link walks were selected by condition and capture checks, not signal
magnitude. All selected sources meet the capture criteria documented below.
This is a small illustration set, not a training corpus or evaluation benchmark.

The files contain derived measurements from raw complex CSI. They are neither
synthetic data nor the older `legacy_v0` normalized-amplitude CSV format.

`empty_01` supplies the baseline centers for `baseline_distance` and
`rssi_shift`. It therefore is not a held-out negative control. Labels are
operator-reported trial conditions; there is no measured trajectory or exact
per-packet motion ground truth. No classifier output is exported.

## Packet table

| Field | Definition |
| --- | --- |
| trial | Anonymous trial alias: empty_01, walk_01, walk_02 |
| condition | empty or walk_cross_link |
| receiver | RX01 or RX02, consistent across all three trials |
| time_s | Seconds since that receiver's first decoded modal-length packet; only [10,50) exported |
| sequence_offset | Sender sequence minus that receiver's first sequence in the original trial; gaps preserved |
| rssi_dbm | Measured packet RSSI in dBm |

Time and sequence origins are independently rebased per receiver. These fields
must not be used to assert exact cross-receiver synchronization. Use the
private original sender sequences for precise packet pairing.

## One-second feature table

| Field | Definition / units |
| --- | --- |
| trial, condition, receiver | Same identifiers as the packet table |
| window_index, window_start_s | Integer second bin and its start in seconds |
| frame_count | Decoded packets with the modal CSI vector length in this bin |
| valid_temporal_pairs | Adjacent sender-sequence pairs with valid positive time gaps |
| temporal_pair_retention | Valid pairs divided by max(1, frame_count - 1) |
| sequence_gap_count | Consecutive decoded sequence transitions whose delta is not 1 |
| largest_sequence_gap | Largest sequence delta, or 1 when all transitions are adjacent |
| usable | At least 4 valid pairs and temporal_pair_retention >= 0.90 |
| spectral_velocity_mean | Mean absolute centered log-amplitude change across valid adjacent packets |
| spectral_velocity_p95 | 95th percentile of those packet-change values |
| temporal_spread | Median across CSI entries of their within-window population standard deviation |
| baseline_distance | Mean absolute difference between window-median CSI shape and empty_01 median shape |
| rssi_mean | Mean packet RSSI in dBm |
| rssi_std | Population standard deviation of packet RSSI, in dB |
| rssi_shift | Absolute difference from the empty_01 median packet RSSI, in dB |

Despite its historical field name, `spectral_velocity` is not a time derivative
or physical velocity. It is change per adjacent packet, and varies with packet
cadence. Do not directly compare 30 Hz and 50 Hz values.

## From raw CSI to features

1. Decode COBS records and check schema, length, and CRC32.
2. Use only the expected receiver ID and the modal CSI vector length.
3. Interpret signed imaginary/real byte pairs. Discard the flagged invalid
   first word, then calculate amplitude `sqrt(real^2 + imaginary^2)`.
4. Calculate `log(1 + amplitude)` and subtract each packet's median across
   CSI entries. This reduces common gain changes while preserving shape.
5. Rebase receiver time and select every decoded packet in [10,50) seconds.
6. Group by one-second bins. Temporal comparisons require sender-sequence
   delta 1, positive elapsed time, and a gap no greater than the larger of
   0.1 seconds and 2.5 times the bin's median positive interval.
7. Compute the features defined above. No invented packets, interpolation,
   cross-trial smoothing, or motion-label-based scaling is applied.

This export mirrors the existing amplitude-processing method, including its
modal-length handling. It does not introduce a calibrated subcarrier mask or
phase correction. Null/guard entries and radio gain behavior can affect CSI
amplitude features; these are engineering measurements, not direct images or
coordinates.

## Quality and provenance

All six original receiver streams were rehashed against their retained SHA-256
manifests, decoded, and checked again without writing to the raw files. Selected
sources have at least 95% sequence retention, less than 0.1% corrupt records,
and zero reported queue drops. Full-session numerical metrics are preserved in
`metadata.json`; they refer to entire source captures, not just the excerpts.

Firmware binary/configuration hashes and current processing/decoder hashes
are retained. Firmware hashes are the artifacts recorded during capture;
they are provenance records, not a new readback of board flash. Metadata
coordinates are operator-entered approximate relative positions in feet;
heights are in meters. They describe the source setup, not the newer proposed
layout. No orientation measurements were available to add.

## De-identification

The export uses an explicit list of permitted fields. Names, participant IDs,
original timestamped session IDs, wall-clock dates, device MACs, COM ports,
computer paths, free-text notes, and external document links are omitted.
Original-to-public mappings and raw source hashes are retained separately in
private local storage. No private raw binaries are distributed.

Removing direct identifiers does not guarantee that radio fingerprints cannot
be linked to a room or device with additional information. Treat this as a
de-identified engineering sample, not a formally anonymous human dataset.

The included plotting script regenerates all scientific figures from the two
CSVs alone. The package checksum file permits checking that downloaded files
match this export. It does not grant a data license or replace repository
licensing decisions.
