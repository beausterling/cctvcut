#!/usr/bin/env python3
"""
GENHQ Sound Design — video beat analyzer.

Produces the timing map a sound-design prompt is built from:
  - duration, resolution, fps, whether an audio track exists
  - hard cuts (scene changes)
  - motion peaks  -> candidate impact / interaction beats
  - soft peaks    -> candidate secondary beats
  - quiet windows -> candidate held-breath moments
  - brightness / saturation profile -> tells you the world (dark UI vs sunlit exterior)

Usage:
    python3 analyze.py /path/to/video.mp4
"""

import subprocess
import sys
import json


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format",
         "-of", "json", path],
        capture_output=True, text=True).stdout
    data = json.loads(out)
    v = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)
    num, den = v["r_frame_rate"].split("/")
    return {
        "duration": float(data["format"]["duration"]),
        "width": v["width"],
        "height": v["height"],
        "fps": round(float(num) / float(den), 2),
        "has_audio": a is not None,
    }


def cuts(path, threshold=0.30):
    out = subprocess.run(
        ["ffmpeg", "-i", path, "-filter:v",
         f"select='gt(scene,{threshold})',metadata=print", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    times = []
    for line in out.splitlines():
        if "pts_time:" in line:
            try:
                times.append(round(float(line.split("pts_time:")[1].split()[0]), 2))
            except (ValueError, IndexError):
                pass
    return sorted(set(times))


def motion(path, fps=15, w=48):
    import numpy as np
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-vf",
         f"fps={fps},scale={w}:-1", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        capture_output=True).stdout
    probe_h = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0", path],
        capture_output=True, text=True).stdout.strip().split(",")
    h = max(1, round(w * int(probe_h[1]) / int(probe_h[0])))
    fs = w * h
    n = len(raw) // fs
    if n < 3:
        return [], [], []
    a = np.frombuffer(raw[:n * fs], dtype=np.uint8).reshape(n, h, w).astype(float)
    d = np.abs(np.diff(a, axis=0)).mean(axis=(1, 2))
    t = np.arange(len(d)) / fps
    hard_thr = d.mean() + d.std()
    soft_lo = d.mean() * 1.3

    major, soft = [], []
    prev = -9
    for i in range(1, len(d) - 1):
        if d[i] > hard_thr and d[i] >= d[i - 1] and d[i] >= d[i + 1] and t[i] - prev > 0.30:
            major.append((round(float(t[i]), 2), round(float(d[i]), 2)))
            prev = t[i]
    prev = -9
    for i in range(1, len(d) - 1):
        if soft_lo < d[i] <= hard_thr and d[i] >= d[i - 1] and d[i] >= d[i + 1] and t[i] - prev > 0.45:
            soft.append((round(float(t[i]), 2), round(float(d[i]), 2)))
            prev = t[i]

    quiet, run = [], None
    for i in range(len(d)):
        if d[i] < 0.6:
            if run is None:
                run = t[i]
        else:
            if run is not None and t[i] - run > 0.5:
                quiet.append((round(float(run), 2), round(float(t[i]), 2)))
            run = None
    if run is not None and t[-1] - run > 0.5:
        quiet.append((round(float(run), 2), round(float(t[-1]), 2)))
    return major, soft, quiet


def look(path):
    import numpy as np
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-vf", "fps=1,scale=64:-1",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True).stdout
    probe_h = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0", path],
        capture_output=True, text=True).stdout.strip().split(",")
    h = max(1, round(64 * int(probe_h[1]) / int(probe_h[0])))
    fs = 64 * h * 3
    rows = []
    for i in range(len(raw) // fs):
        a = np.frombuffer(raw[i * fs:(i + 1) * fs], dtype=np.uint8).reshape(h, 64, 3).astype(float)
        mx, mn = a.max(2), a.min(2)
        rows.append((i, round(float(a.mean()), 1),
                     round(float(((mx - mn) / (mx + 1e-6)).mean()), 2)))
    return rows


def main():
    if len(sys.argv) < 2:
        print("usage: analyze.py <video>")
        sys.exit(1)
    p = sys.argv[1]
    info = probe(p)

    print("=" * 58)
    print("GENHQ SOUND — BEAT ANALYSIS")
    print("=" * 58)
    print(f"duration    {info['duration']:.2f}s")
    print(f"resolution  {info['width']}x{info['height']} @ {info['fps']}fps")
    print(f"audio track {'YES — preserve or replace, ask the user' if info['has_audio'] else 'NONE — build everything from scratch'}")

    c = cuts(p)
    print(f"\nHARD CUTS ({len(c)})")
    print("  " + (", ".join(f"{x:.2f}s" for x in c) if c else "none — single continuous shot"))

    major, soft, quiet = motion(p)
    print(f"\nMAJOR BEATS  -> impacts / transitions / interactions")
    for t, v in major:
        print(f"  {t:6.2f}s   strength {v}")
    if not major:
        print("  none")

    print(f"\nSOFT BEATS   -> light foley / small accents")
    for t, v in soft:
        print(f"  {t:6.2f}s   strength {v}")
    if not soft:
        print("  none")

    print(f"\nQUIET WINDOWS -> held breath, place silence before the next beat")
    for a, b in quiet:
        print(f"  {a:6.2f}s - {b:6.2f}s")
    if not quiet:
        print("  none")

    print(f"\nLOOK PROFILE (brightness 0-255 / saturation 0-1)")
    for i, br, sa in look(p):
        tag = "dark" if br < 60 else ("mid" if br < 140 else "bright")
        print(f"  {i:3d}s   bright {br:6.1f} ({tag})   sat {sa:.2f}")

    print("\n" + "=" * 58)
    print("Next: map each beat to a sound type, then write the prompt.")
    print("=" * 58)


if __name__ == "__main__":
    main()
