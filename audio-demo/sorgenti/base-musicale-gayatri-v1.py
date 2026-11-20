import numpy as np, wave, sys
sr=44100; dur=43.0; N=int(sr*dur); rng=np.random.default_rng(11)
L=np.zeros(N); R=np.zeros(N)
Sa=118.7                     # tonic of the 2nd repetition of the chant
def add(sig,start,pan,g=1.0):
    i=int(start*sr); n=min(len(sig),N-i)
    if n>0: L[i:i+n]+=sig[:n]*g*np.cos(pan*np.pi/2); R[i:i+n]+=sig[:n]*g*np.sin(pan*np.pi/2)
# --- one sustained drone note (shruti-box like), Sa + sub-octave ---
t=np.arange(N)/sr
breath=1+0.08*np.sin(2*np.pi*t/7.3)+0.04*np.sin(2*np.pi*t/3.1+1)
dr=np.zeros(N)
for f0,g in [(Sa,1.0),(Sa/2,0.45)]:
    for k in range(1,16):
        a=g*k**-1.1
        for det in (-0.25,0.25):
            dr+=a*np.sin(2*np.pi*(f0*k+det*k)*t+rng.uniform(0,6.28))
env=np.ones(N); fi=int(3*sr); env[:fi]=np.linspace(0,1,fi)**2
fo=int(6*sr); env[-fo:]=np.linspace(1,0,fo)**2
dr*=breath*env; dr/=np.abs(dr).max()
DRONE=dr.copy()
# --- melody (one octave higher than v6), only the rising runs x3 ---
ratios=[1,9/8,5/4,3/2,5/3]
def note(deg): o,d=divmod(deg,5); return Sa*4*ratios[d]*2**o
def struck(f, length=3.5):
    n=int(length*sr); tt=np.arange(n)/sr; s=np.zeros(n)
    for k,a in [(1,1),(2,0.7),(3,0.55),(4,0.42),(5,0.32),(6,0.25),(7,0.19),(8,0.14),(9,0.1),(10,0.07),(12,0.05)]:
        fk0=f*k*(1+0.0006*k*k)
        if fk0>12000: continue
        for det in (-0.6,0.6):
            s+=a*np.exp(-tt/(1.6/k**0.4))*np.sin(2*np.pi*(fk0+det)*tt+rng.uniform(0,6.28))
    m=int(0.012*sr); nz=rng.normal(0,1,m); nz=np.diff(nz,prepend=0)*np.exp(-np.arange(m)/(0.003*sr)); s[:m]+=0.35*nz
    return s*np.minimum(1,tt/0.002)
e=60/92/2; tcur=float(sys.argv[2])   # start of the runs (after the chant)
for rep,gr in enumerate([0.8,0.9,1.0]):
    for d in range(5,10):
        add(struck(note(d)), tcur+rng.normal(0,0.004), 0.4+0.05*(d-5), gr); tcur+=e/2
    if rep<2: tcur+=e*1.5
for d,g in [(10,1.15),(8,0.6),(5,0.5)]:
    add(struck(note(d),5.0), tcur, 0.5, g)
def bowl(f0,length):
    n=int(length*sr); tt=np.arange(n)/sr; s=np.zeros(n)
    for r,a,dc in [(1,1,9),(2.71,0.5,6),(5.15,0.25,4),(8.17,0.12,2.5)]:
        for dt in (-0.35,0.35): s+=a*np.exp(-tt/dc)*np.sin(2*np.pi*(f0*r+dt)*tt)
    return s*np.minimum(1,tt/0.004)
add(bowl(Sa*2, dur-tcur-0.4), tcur+0.4, 0.5, 0.5)
print("final Sa at %.2fs"%tcur)
# reverb on melody only
irn=int(2.4*sr); ti=np.arange(irn)/sr
def rev(x,seed):
    ir=np.random.default_rng(seed).normal(0,1,irn)*np.exp(-ti/0.75); ir[0]=0
    F=1<<int(np.ceil(np.log2(len(x)+irn))); y=np.fft.irfft(np.fft.rfft(x,F)*np.fft.rfft(ir,F),F)[:len(x)]
    return y/(np.abs(y).max()+1e-9)
m=max(np.abs(L).max(),np.abs(R).max()); Lm=L/m; Rm=R/m
Lm=0.8*Lm+0.3*rev(Lm,1); Rm=0.8*Rm+0.3*rev(Rm,2)
gd=float(sys.argv[3])        # drone gain relative to melody
st=np.stack([Lm+gd*DRONE, Rm+gd*DRONE],1)
st*=env[:,None]**0 ; fo2=int(4*sr); st[-fo2:]*=np.linspace(1,0,fo2)[:,None]**2
st/=np.abs(st).max()*1.12
with wave.open(sys.argv[1],'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((st*32767).astype('<i2').tobytes())
