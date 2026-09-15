kB=1.380649e-23; T=300.0
L_nat=kB*T                      # J per nat erased (Landauer), 2.87e-21
L_bit=kB*T*np.log(2) if False else kB*T*0.6931471805599453
import math
L_bit=kB*T*math.log(2)
print(f"Landauer @300K:  {L_bit:.3e} J/bit   {L_nat:.3e} J/nat")

def block(name, E_per_nat_J, note):
    print(f"  {name:34s} {E_per_nat_J:9.3e} J/nat   Gamma = eps/Landauer = {E_per_nat_J/L_nat:8.2e}   {note}")

print("\nSILICON (per nat of emitted token entropy):")
for tok_s, J_tok, H, lbl in [(50,4.0,2.0,"70B, H100, 50 tok/s"),
                             (50,0.4,2.0,"7B,  50 tok/s"),
                             (200,4.0,2.0,"70B, 200 tok/s (batched)")]:
    block(f"{lbl}", J_tok/H, f"nu={tok_s}/s")

print("\nCARBON (per nat of assimilated semantic content):")
for tok_s, W_marg, H, lbl in [(3,0.2,2.0,"comfortable reading ~150 wpm"),
                              (10,0.2,2.0,"max sustained ~500 wpm"),
                              (10,1.0,2.0,"max sustained, high effort"),
                              (0.5,0.2,2.0,"skimming / attention saturated")]:
    block(f"{lbl}", W_marg/(tok_s*H), f"nu={tok_s}/s")

print("\n" + "="*78)
print("DERIVED THRESHOLDS")
print("="*78)
nu_S=50.0; nu_C_max=10.0; nu_C_comfort=3.0
print(f"  Gamma_crit = nu_S / nu_C^max      = {nu_S:.0f}/{nu_C_max:.0f}  = {nu_S/nu_C_max:.1f}")
print(f"  Gamma at comfortable human pace   = {nu_S:.0f}/{nu_C_comfort:.0f}  = {nu_S/nu_C_comfort:.1f}")
print(f"  -> to hold 0.8 <= Gamma <= 1.2 at nu_C=10/s, throttle nu_S to "
      f"[{0.8*nu_C_max:.0f}, {1.2*nu_C_max:.0f}] tok/s")
print(f"  -> autonomous agent loop (no carbon in loop): nu_C -> 0, Gamma -> infinity")
print("\n  Both substrates sit at eps ~ 1e18-1e21 x Landauer, i.e. the SAME order.")
print("  Gamma ~ 1 is therefore NOT fine-tuned: it is the natural operating point.")
