# Latest implemented upgrade

The current source includes live adaptive RSSI plots, large phase instructions,
receiver sequence-retention and corruption-burst diagnostics, and preflight
checks for board identity, channel, and estimated TX cadence. Changing selected
ports, channel, baud, or rate invalidates the previous preflight.

The standard protocol allocates 10 seconds for setup, 40 seconds for activity,
and 10 seconds for recovery. Recorded node positions are validated for minimum
3 ft link distance and 30-degree angular separation. These are protocol rules,
not experimentally optimized universal limits.

The prepared geometry uses TX (1,5) ft at 1 m height, RX01 (9,5) ft at 1 m, and
RX02 (5,1) ft at 0.45 m. Enter actual measured positions when collecting. The
sample dataset was collected in the older compact geometry recorded in its
metadata, so its plots do not validate this proposed arrangement.

Offline method `dual_link_activity_v1_empty_only` pools compatible empty
calibrations, applies robust feature scaling, skips packet gaps, and reports
quiet, receiver-dominant activity, activity on both links, or uncertainty. The
GUI's immediate RSSI disturbance display uses a simpler heuristic. Neither
output is a trained semantic action label.

A separate classic-ESP32 TX image was compiled for channel 6 at 30 Hz:

```text
TX binary SHA-256:
711704ef256c324d308be2aebdd5895e2f120b9ff1fc1d3e9519c9198b8a2b89
```

The project record documents 22 passing host tests, a GUI layout check, and
verification of the built TX image/configuration. Physical validation of this
30 Hz variant and the proposed geometry remains pending. This asset export
does not flash hardware or collect additional experiment data.

At 30 Hz only TX needs a new image if both receivers already have the matching
channel-6 firmware. New recordings need new calibration; the included 50 Hz
examples must not be treated as 30 Hz measurements. Lower cadence reduces
offered load, but its effect on data retention must be measured.
