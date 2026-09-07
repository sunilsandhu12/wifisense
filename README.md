# WiFiSense: measured-data publication assets

A companion pack for an experimental ESP32 Wi-Fi CSI sensing project. It
contains an architecture diagram, measured empty-versus-walking figures,
installation instructions, and a small de-identified example dataset.

## System

<img width="2340" height="1134" alt="image" src="https://github.com/user-attachments/assets/73e985f2-7230-47ca-a5cb-9a56e036bf77" />


One classic ESP32 sends controlled ESP-NOW packets. Two receivers independently
measure CSI and RSSI and send checked binary records to a Python host. The GUI
records labeled experiments; offline processing derives baseline-relative
activity features. The diagram shows architecture, not the source room layout.

## Measured examples

<img width="2430" height="1260" alt="image" src="https://github.com/user-attachments/assets/e8af46ca-d23b-4356-8532-a0705a8d731f" />


These are actual measured recordings at 50 Hz on channel 6. Each column uses
the same axes and the complete 10-50 second excerpt. The shaded RSSI band is
within-window standard deviation, not a confidence interval. CSI changes are
dimensionless amplitude-pattern differences, not physical velocity.

<img width="1980" height="864" alt="image" src="https://github.com/user-attachments/assets/1f6d204d-71ce-4d44-b331-fd79aa13606e" />


Selection is explicit: this pack contains the one empty and both cross-link
walking trials satisfying capture criteria in an earlier three-round study.
Both walking repeats are shown. The sample is illustrative, not a benchmark,
held-out detection evaluation, or a representative sample of every experiment.
Windows within a session are correlated. No accuracy estimate is inferred.

The clearest visual difference here is recurring RSSI dips and increased RSSI
spread during walking. The adjacent-packet CSI feature overlaps across the
three trials, illustrating why one amplitude-change metric alone is
insufficient. The analysis pipeline also retains baseline-distance and other
features; no action classifier is implied by these plots.

## Files

| File | Contents |
| --- | --- |
| [packet_rssi.csv](data/packet_rssi.csv) | 11,792 measured packet rows from three trials and two receivers |
| [window_features.csv](data/window_features.csv) | 240 one-second CSI/RSSI feature rows |
| [metadata.json](data/metadata.json) | Capture configuration, recorded relative layout, quality metrics, firmware and processing hashes |
| [DATASET.md](DATASET.md) | Schema, processing, selection, and de-identification notes |
| [INSTALLATION.md](INSTALLATION.md) | Plot-only installation and full-project acquisition setup |
| [UPGRADE_STATUS.md](UPGRADE_STATUS.md) | Implemented upgrades and verification status |
| [reproduce_plots.py](reproduce_plots.py) | Rebuilds all figures using only the exported CSV |
| [system_diagram.mmd](system_diagram.mmd) | Editable Mermaid architecture source |
| [checksums.sha256](checksums.sha256) | Checksums for the public pack |

All figures also have vector PDF versions in `figures/`.

## Reproduce the figures

Run from this folder with Python 3.11 or newer:

```powershell
python -m pip install -r requirements-plots.txt
python reproduce_plots.py
```

This needs no ESP32, private recording, serial port, or project installation.
Raw I/Q is retained privately outside the repository; the public data is a
derived export. Exact raw-to-feature regeneration requires those original
recordings and the recorded processing source.

## Current scope

The software supports collection, visualization, and exploratory activity/link
disturbance analysis. Semantic action classification, pose, precise position,
and fall-like-event detection remain future work. This is a non-clinical
engineering prototype. See [upgrade status](UPGRADE_STATUS.md) for the prepared
30 Hz configuration, which is separate from the measured examples above.


Built with ESP-IDF and informed by [Espressif ESP-CSI](https://github.com/espressif/esp-csi).
