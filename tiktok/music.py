#!/usr/bin/env python3
"""A soft, original lo-fi background track (no samples, no copyright) for under the voice."""
import numpy as np
import soundfile as sf

SR = 44100


def _env(n, attack, release):
    e = np.ones(n, dtype=np.float32)
    a, r = min(int(attack * SR), n), min(int(release * SR), n)
    if a: e[:a] = np.linspace(0, 1, a)
    if r: e[-r:] *= np.linspace(1, 0, r)
    return e


def _note(freq, dur, vol):
    t = np.arange(int(dur * SR)) / SR
    # warm electric-piano-like tone: a few soft harmonics with gentle vibrato
    vib = 1 + 0.002 * np.sin(2 * np.pi * 5 * t)
    s = (np.sin(2 * np.pi * freq * vib * t) + 0.35 * np.sin(4 * np.pi * freq * t) * np.exp(-t * 3)
         + 0.12 * np.sin(6 * np.pi * freq * t) * np.exp(-t * 5))
    return (s * _env(len(t), 0.02, dur * 0.6) * np.exp(-t * 0.9) * vol).astype(np.float32)


def _lowpass(x, a):
    y = np.empty_like(x); acc = 0.0
    for i in range(0, len(x), 4096):  # simple one-pole filter, in blocks for speed
        blk = x[i:i + 4096]
        out = np.empty_like(blk)
        for j, v in enumerate(blk):
            acc += a * (v - acc); out[j] = acc
        y[i:i + 4096] = out
    return y


def make(seconds, path, bpm=82, seed=7):
    rng = np.random.default_rng(seed)
    beat = 60 / bpm
    bar = beat * 4
    n = int((seconds + bar) * SR)
    mix = np.zeros(n, dtype=np.float32)
    # Cmaj7 - Am7 - Fmaj7 - G6, voiced low and soft
    chords = [[130.81, 164.81, 196.0, 246.94], [110.0, 130.81, 164.81, 196.0],
              [87.31, 130.81, 174.61, 220.0], [98.0, 146.83, 196.0, 246.94]]
    bars = int(seconds / bar) + 1
    for b in range(bars):
        ch = chords[b % 4]
        start = int(b * bar * SR)
        for k, f in enumerate(ch):  # gently rolled chord
            s = start + int(k * 0.03 * SR)
            note = _note(f, bar * 1.1, 0.12)
            e = min(len(note), n - s)
            if e > 0: mix[s:s + e] += note[:e]
        # soft bass on beat 1 and 3
        for off in (0, 2):
            s = start + int(off * beat * SR)
            bnote = _note(ch[0] / 2, beat * 1.6, 0.22)
            e = min(len(bnote), n - s)
            if e > 0: mix[s:s + e] += bnote[:e]
        # light melody notes from the chord, every other beat
        for off in (1, 3):
            s = start + int((off + 0.5) * beat * SR)
            m = _note(ch[rng.integers(1, 4)] * 2, beat * 1.2, 0.05)
            e = min(len(m), n - s)
            if e > 0: mix[s:s + e] += m[:e]
    # drums: soft kick (1, 3) and brushed hat (off-beats)
    kt = np.arange(int(0.25 * SR)) / SR
    kick = (np.sin(2 * np.pi * (45 + 60 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 14) * 0.35).astype(np.float32)
    hat = (rng.standard_normal(int(0.06 * SR)) * np.exp(-np.arange(int(0.06 * SR)) / SR * 70) * 0.03).astype(np.float32)
    hat = hat - _lowpass(hat, 0.3)  # keep it airy, not harsh
    for i in range(int(seconds / beat) + 1):
        s = int(i * beat * SR)
        if i % 2 == 0 and s + len(kick) < n: mix[s:s + len(kick)] += kick
        h = s + int(beat / 2 * SR)
        if h + len(hat) < n: mix[h:h + len(hat)] += hat * (0.8 + 0.4 * rng.random())
    # a little warmth: soft vinyl-style noise and a gentle low-pass over everything
    noise = _lowpass(rng.standard_normal(n).astype(np.float32), 0.05) * 0.02
    mix = _lowpass(mix + noise, 0.35)
    # simple room echo
    d = int(0.23 * SR); mix[d:] += mix[:-d] * 0.25
    mix = mix[:int(seconds * SR)]
    fade = int(1.5 * SR)
    mix[:fade] *= np.linspace(0, 1, fade); mix[-fade:] *= np.linspace(1, 0, fade)
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.6
    sf.write(path, np.stack([mix, mix], axis=1), SR)
    return path


if __name__ == "__main__":
    import sys
    make(float(sys.argv[1]), sys.argv[2])
