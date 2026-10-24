"""Generate original, copyright-free devotional instrumentals (tanpura + bells + flute + soft hand-drum)."""
import numpy as np, sys
from scipy.io import wavfile
from scipy.signal import fftconvolve
sr = 44100
RAGAS = {  # just-intonation ratios
 "mohanam":   {"S":1,"R":9/8,"G":5/4,"P":3/2,"D":5/3},
 "hindolam":  {"S":1,"g":6/5,"m":4/3,"d":8/5,"n":9/5},
 "shankarabharanam": {"S":1,"R":9/8,"G":5/4,"M":4/3,"P":3/2,"D":5/3,"N":15/8},
 "madhyamavati": {"S":1,"R":9/8,"M":4/3,"P":3/2,"n":9/5},
}
def env(n, a, r):
    e = np.ones(n); a = max(1, int(a*sr)); r = max(1, int(r*sr))
    e[:a] = np.linspace(0, 1, a); e[-r:] *= np.linspace(1, 0, r); return e
def track(raga, seed, dur=20.0, Sa=146.83):
    rng = np.random.default_rng(seed); t = np.arange(int(sr*dur))/sr; out = np.zeros_like(t)
    notes = list(RAGAS[raga].items())
    fifth = Sa*1.5/2 if "P" in RAGAS[raga] else Sa*4/3/2
    for k in range(int(dur/0.55)):                       # tanpura
        f = [fifth, Sa, Sa, Sa/2][k % 4]; st = int(k*0.55*sr); n = min(int(3.2*sr), len(t)-st)
        tt = np.arange(n)/sr
        s = sum((0.62**h)*np.sin(2*np.pi*f*(h+1)*tt*(1+0.0005*h)) for h in range(12))
        out[st:st+n] += 0.10*s*np.exp(-tt*0.9)*(1+0.12*np.sin(2*np.pi*4.5*tt))
    pad = sum(np.sin(2*np.pi*Sa*m*t) for m in (1, 2, 1.5 if "P" in RAGAS[raga] else 4/3)) # shruti pad
    out += 0.025*pad*(0.7+0.3*np.sin(2*np.pi*0.1*t))
    pos = 1.2; idx = 0                                   # flute, stepwise random walk
    while pos < dur-2.2:
        idx = int(np.clip(idx + rng.choice([-2,-1,-1,0,1,1,2]), 0, len(notes)*2-1))
        name, ratio = notes[idx % len(notes)]; ratio *= 2 if idx >= len(notes) else 1
        l = rng.choice([0.4, 0.4, 0.8, 0.8, 1.2, 1.6]); n = int(l*sr*0.97); st = int(pos*sr)
        tt = np.arange(n)/sr; f = Sa*2*ratio
        vib = 1+0.005*np.sin(2*np.pi*5.3*tt)*np.clip(tt*2.5, 0, 1)
        gl = 1 + 0.01*np.exp(-tt*25)*rng.choice([-1, 1])    # gamaka-like slide
        ph = 2*np.pi*np.cumsum(f*vib*gl)/sr
        s = np.sin(ph)+0.22*np.sin(2*ph)+0.07*np.sin(3*ph)+0.02*rng.standard_normal(n)
        out[st:st+n] += 0.15*s*env(n, 0.07, 0.15); pos += l*0.85
        if rng.random() < 0.12: pos += 0.6
    for bt in [0.0, dur/2, dur-5]:                        # temple bells
        st = int(bt*sr); n = min(int(4.5*sr), len(t)-st); tt = np.arange(n)/sr
        s = sum(a*np.sin(2*np.pi*f*tt)*np.exp(-tt*d) for f, a, d in [(880,1,.8),(1333,.5,1.3),(2093,.3,2.1),(2771,.15,3)])
        out[st:st+n] += 0.11*s
    beat = 60/72                                          # soft hand drum (adi-like pulse)
    for k in range(int(dur/beat)):
        if k % 8 in (0, 3, 4, 6):
            st = int(k*beat*sr); n = min(int(0.5*sr), len(t)-st); tt = np.arange(n)/sr
            f0 = 110 if k % 8 == 0 else 160
            out[st:st+n] += (0.09 if k % 8 == 0 else 0.05)*np.sin(2*np.pi*f0*tt*(1+0.3*np.exp(-tt*30)))*np.exp(-tt*9)
    ir = rng.standard_normal(int(2.0*sr))*np.exp(-np.arange(int(2.0*sr))/sr*2.6); ir /= np.abs(ir).sum()/6
    mix = 0.72*out + 0.38*fftconvolve(out, ir)[:len(out)]
    mix *= env(len(mix), 1.2, 2.5); mix /= np.abs(mix).max()*1.12
    return (mix*32767).astype(np.int16)
if __name__ == "__main__":
    for i, (r, seed) in enumerate([("mohanam",1),("hindolam",2),("shankarabharanam",3),("madhyamavati",4),("mohanam",5),("hindolam",6)]):
        wavfile.write(f"music/track{i+1}_{r}.wav", sr, track(r, seed)); print("ok", r)
