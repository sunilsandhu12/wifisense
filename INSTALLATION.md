# Installation and reproduction

## View and regenerate this companion pack

No boards are required. Use Python 3.11 or newer. From the folder containing
this file, open PowerShell and create a local environment:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-plots.txt
.\.venv\Scripts\python.exe reproduce_plots.py
```

This regenerates three PNG figures and matching vector PDFs in `figures/`.
The script reads the supplied CSVs. It does not connect to serial ports.

## Install the complete acquisition project

These instructions require the full source checkout containing `pyproject.toml`,
`src/`, `tools/`, and `firmware/`. This companion pack by itself is insufficient
to run the collection GUI. No repository URL is assumed before publication.

From the full project root in PowerShell:

```powershell
py -3.11 -m venv "$env:LOCALAPPDATA\WiFiSensing\venv"
$python = "$env:LOCALAPPDATA\WiFiSensing\venv\Scripts\python.exe"
& $python -m pip install -e ".[dev]"
& $python -m wifisense.cli --help
& $python -m pytest -q
```

Keep raw data outside synchronized source folders. The collector defaults to
`%LOCALAPPDATA%\WiFiSensing\data`. Its dependencies include NumPy, Matplotlib,
PySerial, Tkinter (supplied by the standard Windows Python installer), and the
other packages declared in `pyproject.toml`.

## Firmware prerequisites

Install ESP-IDF **v6.0.1** and the ESP32 target tools using the official
[Windows installation guide](https://docs.espressif.com/projects/esp-idf/en/v6.0.1/esp32/get-started/windows-setup.html).
Select that version explicitly using the installer's custom installation.
Classic boards use target `esp32`, not `esp32s3`.

The current project helpers were written for a specific ESP-IDF installation:

```text
C:\Espressif\tools\Microsoft.v6.0.1.PowerShell_profile.ps1
C:\Espressif\tools\esp-rom-elfs\20241011
```

Before building on another computer, check these paths. If your installer uses
different paths, adapt `$idfProfile` and `ESP_ROM_ELF_DIR` in both
`tools/build_three_node_firmware.ps1` and
`tools/flash_three_node_firmware.ps1` to the actual installed tools. The helpers
are not yet installation-path-independent. Do not create an empty substitute
directory for a missing tool.

## Build and flash classic boards

From the full project root, build all three roles at the prepared 30 Hz setting:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\build_three_node_firmware.ps1 -HardwareProfile classic_esp32 -Role all -Channel 6 -SampleRateHz 30
```

The helpers keep build products and generated configuration outside the source
tree and write a manifest for the selected rate/channel. For the historical
50 Hz setting use `-SampleRateHz 50` and set the GUI to 50 as well.

Connect one board at a time. Identify its actual port in Device Manager and
enter it into `$port` before each flash. These commands write firmware:

```powershell
$port = Read-Host "TX COM port"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\flash_three_node_firmware.ps1 -HardwareProfile classic_esp32 -Role tx -Port $port -Channel 6 -SampleRateHz 30
```

Disconnect TX, connect the first receiver, and run:

```powershell
$port = Read-Host "RX01 COM port"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\flash_three_node_firmware.ps1 -HardwareProfile classic_esp32 -Role rx01 -Port $port -Channel 6 -SampleRateHz 30
```

Disconnect RX01, connect the second receiver, and run:

```powershell
$port = Read-Host "RX02 COM port"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\flash_three_node_firmware.ps1 -HardwareProfile classic_esp32 -Role rx02 -Port $port -Channel 6 -SampleRateHz 30
```

Label the boards by role. Existing channel-6 receivers do not need reflashing
solely to change the transmitter cadence. Close serial monitors before capture.

## Start an experiment

Power TX independently and connect both receivers to the laptop with data-capable
USB cables. Secure the boards and enter their actual positions and heights.

```powershell
.\tools\start_dual_link_gui.cmd
```

Select `classic_esp32`, channel `6`, baud `230400`, and TX rate matching the
flashed image. Run Preflight, then collect three compatible empty-room trials
before labeled movement trials. The normal timing is 0-10 s setup, 10-50 s
declared activity, and 50-60 s recovery. Keep away from the laptop until the
capture has completed. Use ordinary walking for initial tests.

The 30 Hz configuration is a prepared upgrade awaiting physical verification;
the included sample data was recorded at 50 Hz. The full repository's optimized
classic activity protocol gives the proposed next experiment block.

## Troubleshooting

- `idf.py` unavailable: load the ESP-IDF environment; plain PowerShell alone
  does not provide the toolchain.
- No receiver port: check the USB data cable, adapter driver, and Device Manager.
- Port busy: close any serial monitor or other collector using that receiver.
- Preflight rate mismatch: confirm both the TX firmware variant and GUI rate.
- No compatible calibration: collect new empty trials after changing rate,
  firmware, layout, or other recorded configuration.

Fresh-machine installation and hardware acquisition were not rerun while
preparing this pack. Commands were checked against the saved source; plot
reproduction was executed on the existing project environment.
