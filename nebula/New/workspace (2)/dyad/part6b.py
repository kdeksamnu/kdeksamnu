import numpy as np
"""
Can a Gamma-governor actually hold 0.8 <= Gamma <= 1.2?

A pure integral law trivially pins Gamma=1 in the noiseless limit (zero steady-state
error), so that case is uninformative. The real question is what the band costs under
(i) noisy Gamma estimation, (ii) measurement/actuation delay, (iii) finite actuator
slew -- a rate limiter cannot change throughput instantaneously.

Control law (bounded-slew multiplicative, as a real token-rate governor would be):
    u(t+dt) = clip( u(t) * (1 + clip(Kp*dt*(1 - Gamma_meas), -slew, +slew)), u_lo, u_hi )
"""
dt=0.05; T=1800.0; N=int(T/dt)
H_S=H_C=2.0; nu_nom=50.0; u_lo,u_hi=0.02,2.0; LO,HI=0.8,1.2
PAD=int(60/dt)

def human(seed):
    rng=np.random.default_rng(seed); c=10.0; out=np.zeros(N+PAD)
    for k in range(N+PAD):
        c+=(-0.8*(c-10.0))*dt + 1.1*np.sqrt(dt)*rng.normal()
        c+=3.6*np.sin(2*np.pi*k*dt/240.0)*dt
        out[k]=c
    return np.clip(out,1.5,16.0)

def run(Kp,tau_d,slew,noise,seed=5,governor=True):
    rng=np.random.default_rng(seed+999); cmax=human(seed).copy()
    dly=int(round(tau_d/dt)); rd=int(round(0.30/dt))
    hist=np.full(max(dly,rd)+2,nu_nom); u=1.0; Gm=np.zeros(N)
    for k in range(N):
        nuS=u*nu_nom; hist=np.append(hist,nuS)
        g_true=(nuS*H_S)/max(min(hist[-rd-1],cmax[k])*H_C,1e-9)
        Gm[k]=g_true
        cmax[k+1]-=0.05*max(0.0,nuS-10.0)*dt
        if governor:
            g_meas=g_true*(1.0+noise*rng.normal())
            step=np.clip(Kp*dt*(1.0-g_meas),-slew,+slew)
            u=np.clip(u*(1.0+step),u_lo,u_hi)
    return Gm[int(300/dt):]

def row(lbl,**kw):
    gs=[run(**kw,seed=s) for s in (5,6,7)]
    ib=np.mean([100*np.mean((g>=LO)&(g<=HI)) for g in gs])
    mx=np.mean([g.max() for g in gs]); p95=np.mean([np.percentile(g,95) for g in gs])
    print(f"{lbl:<46}{ib:>9.1f}%{p95:>9.2f}{mx:>9.2f}")

print(f"{'configuration':<46}{'in-band':>10}{'p95 G':>9}{'max G':>9}")
print("-"*74)
row("OPEN LOOP (no governor)",Kp=0,tau_d=0,slew=1,noise=0,governor=False)
print("-- noiseless, bounded slew 0.05/step --")
for Kp in [2,10,40]: row(f"  Kp={Kp:>3}/s, tau_d=2 s, noise=0",Kp=Kp,tau_d=2.0,slew=0.05,noise=0.0)
print("-- with 10% Gamma estimation noise --")
for Kp in [2,10,40]: row(f"  Kp={Kp:>3}/s, tau_d=2 s, noise=0.10",Kp=Kp,tau_d=2.0,slew=0.05,noise=0.10)
print("-- delay sweep at Kp=10/s, noise=0.10 --")
for td in [0.5,2,5,10,20,40]: row(f"  tau_d={td:>5.1f} s",Kp=10,tau_d=td,slew=0.05,noise=0.10)
print("-- slew sweep at Kp=10/s, tau_d=5 s, noise=0.10 --")
for sl in [0.5,0.2,0.1,0.05,0.02]: row(f"  max slew={sl:.2f}/step ({sl/dt:.1f}/s)",Kp=10,tau_d=5.0,slew=sl,noise=0.10)
