"""Regenerate the public figures from the accompanying measured CSV files."""

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle

ROOT = Path(__file__).resolve().parent
COLORS = {"RX01": "#1967b3", "RX02": "#00846b"}
TRIALS = [
    ("empty_01", "Empty room"),
    ("walk_01", "Cross-link walking 1"),
    ("walk_02", "Cross-link walking 2"),
]


def save(fig, name):
    """Write a GitHub-friendly PNG and a vector PDF with the same content."""
    for ext in ("png", "pdf"):
        metadata = {"Software": "WiFiSense"} if ext == "png" else {"CreationDate": None}
        fig.savefig(
            ROOT / "figures" / f"{name}.{ext}", dpi=180, facecolor="white", metadata=metadata
        )
    plt.close(fig)


def main():
    (ROOT / "figures").mkdir(exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )
    with (ROOT / "data" / "window_features.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    # Matching scales expose the size of changes across conditions fairly.
    fig, axes = plt.subplots(2, 3, figsize=(13.5, 7), sharex=True, sharey="row")
    fig.suptitle("Measured Wi-Fi signals: empty room and two walking repeats", fontsize=17, y=0.97)
    for column, (trial, title) in enumerate(TRIALS):
        axes[0, column].set_title(title, pad=10)
        for receiver, color in COLORS.items():
            block = [r for r in rows if r["trial"] == trial and r["receiver"] == receiver]
            t = np.array([float(r["window_start_s"]) + 0.5 for r in block])
            mean = np.array([float(r["rssi_mean"]) for r in block])
            std = np.array([float(r["rssi_std"]) for r in block])
            axes[0, column].plot(t, mean, color=color, label=receiver, lw=1.7)
            axes[0, column].fill_between(t, mean - std, mean + std, color=color, alpha=0.13)
            # CSI variation is an amplitude-change feature, not speed in meters/second.
            delta = [float(r["spectral_velocity_mean"]) for r in block]
            axes[1, column].plot(t, delta, color=color, lw=1.6)
        for row in range(2):
            axes[row, column].set_xlim(10, 50)
            axes[row, column].grid(alpha=0.18)
        axes[1, column].set_xlabel("Seconds from first received frame")
    axes[0, 0].set_ylabel("RSSI (dBm)\nmean and within-window +/-1 SD")
    axes[1, 0].set_ylabel("Mean adjacent-packet change\ncentered log-amplitude units")
    axes[1, 0].set_ylim(bottom=0)
    axes[0, 2].legend(loc="best")
    fig.text(
        0.07,
        0.035,
        "Measured 50 Hz classic-ESP32 recordings; 1 s windows, interval [10, 50). "
        "No interpolation across missing packets.\n"
        "One empty and two walking trials from one setup. Illustrative signals, "
        "not detection accuracy or the new 30 Hz configuration.",
        fontsize=9,
    )
    fig.subplots_adjust(left=0.085, right=0.985, top=0.88, bottom=0.17, wspace=0.10, hspace=0.23)
    save(fig, "empty_vs_walking")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    for ax, field, title, units in zip(
        axes,
        ("rssi_std", "spectral_velocity_mean"),
        ("RSSI variation", "CSI amplitude-pattern change"),
        ("Within-window standard deviation (dB)", "Centered log-amplitude units"),
        strict=True,
    ):
        for j, (receiver, color) in enumerate(COLORS.items()):
            for i, (trial, _) in enumerate(TRIALS):
                vals = np.array(
                    [
                        float(r[field])
                        for r in rows
                        if r["trial"] == trial and r["receiver"] == receiver
                    ]
                )
                x = i + (j - 0.5) * 0.25
                ax.scatter(
                    x + np.linspace(-0.035, 0.035, len(vals)),
                    vals,
                    color=color,
                    s=13,
                    alpha=0.55,
                    label=receiver if i == 0 else None,
                )
                ax.plot([x - 0.07, x + 0.07], [np.median(vals)] * 2, color=color, lw=3)
        ax.set_xticks(range(3), ["Empty", "Walk 1", "Walk 2"])
        ax.set_title(title)
        ax.set_ylabel(units)
        ax.set_ylim(bottom=0)
        ax.grid(axis="y", alpha=0.2)
    axes[0].legend()
    fig.suptitle("Every exported one-second window", fontsize=16)
    fig.text(
        0.06,
        0.025,
        "Dots = measured windows; short bars = medians. Windows within a trial are "
        "correlated, not independent experiments.",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.93))
    save(fig, "window_distributions")

    # This architecture schematic is conceptual; it makes no claim about room geometry.
    fig, ax = plt.subplots(figsize=(13, 6.3))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 6.3)
    ax.axis("off")
    ax.text(0.4, 5.9, "WiFiSense | one transmitter, two sensing links", fontsize=19, weight="bold")

    def box(x, y, w, h, title, detail, color):
        ax.add_patch(Rectangle((x, y), w, h, facecolor="#f7f9fa", edgecolor=color, lw=1.8))
        ax.text(x + 0.15, y + h - 0.32, title, fontsize=10, weight="bold", color=color)
        ax.text(x + 0.15, y + h - 0.64, detail, fontsize=9, va="top", linespacing=1.6)

    box(
        0.4,
        2.2,
        2.25,
        1.5,
        "ESP32 transmitter",
        "Controlled ESP-NOW\nIndependent USB power",
        "#993b2b",
    )
    box(
        4.0,
        3.5,
        2.25,
        1.4,
        "ESP32 RX01",
        "CSI, RSSI, sequence\nReceiver timestamps",
        COLORS["RX01"],
    )
    box(
        4.0,
        1.0,
        2.25,
        1.4,
        "ESP32 RX02",
        "CSI, RSSI, sequence\nReceiver timestamps",
        COLORS["RX02"],
    )
    box(
        7.6,
        2.15,
        2.5,
        1.65,
        "Python host / GUI",
        "Check COBS / CRC32\nSave raw + metadata\nLive health / RSSI",
        "#343b42",
    )
    box(
        10.65,
        2.15,
        2.0,
        1.65,
        "Offline analysis",
        "Empty calibration\nCSI/RSSI features\nActivity / link pattern",
        "#343b42",
    )

    def arrow(a, b, label, at, color="#56616b", dashed=False):
        ax.add_patch(
            FancyArrowPatch(
                a,
                b,
                arrowstyle="-|>",
                mutation_scale=15,
                lw=1.8,
                color=color,
                linestyle="--" if dashed else "-",
            )
        )
        ax.text(*at, label, fontsize=9, ha="center", color=color)

    arrow((2.65, 3.15), (4, 4.1), "RF link 1", (3.25, 3.98), COLORS["RX01"], True)
    arrow((2.65, 2.7), (4, 1.75), "RF link 2", (3.25, 1.75), COLORS["RX02"], True)
    arrow((6.25, 4.1), (7.6, 3.4), "USB serial", (6.94, 4.12))
    arrow((6.25, 1.75), (7.6, 2.6), "USB serial", (6.94, 1.6))
    arrow((10.1, 2.95), (10.65, 2.95), "", (10.4, 3.25))
    ax.text(
        0.4,
        0.45,
        "Dashed = wireless links influenced by movement and multipath. "
        "Solid = data transport. Schematic, not to scale.",
        fontsize=10,
    )
    ax.text(
        0.4,
        0.10,
        "Example recordings: channel 6, 50 Hz TX, 230400 baud. "
        "Latest prepared TX variant: 30 Hz; physical validation pending.",
        fontsize=10,
    )
    save(fig, "system_diagram")
    print("Wrote three figures, each as PNG and PDF.")


if __name__ == "__main__":
    main()
