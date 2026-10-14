# Self-consistent Hubbard U with Quantum ESPRESSO hp.x

Scripts and examples for iterative Hubbard U calculations using pw.x and
hp.x.

I put this together while computing self-consistent U for Fe-bearing
bridgmanite and post-perovskite MgSiO3 under lower-mantle pressure. I kept
running into problems that weren't obvious from the standard
documentation - mostly around magnetic states, restarting hp.x cleanly,
and what to do when a structure has more than one Hubbard atom and they
turn out not to be equivalent. I'm sharing the workflow here in case it
saves someone else the same debugging.

This repo starts from an already-relaxed structure (a CONTCAR).

## What this does

The basic procedure:

1. Spin-polarized SCF with smeared occupations and an initial guess for U.
2. Fixed-occupation SCF at the magnetic state you actually want.
3. hp.x on top of that, giving you a new U.
4. Feed that back in as the input U for the next iteration.
5. Repeat until the change in U is small enough.

See `notes/workflow.md` for the longer version, and `notes/common_problems.md`
for the things that actually went wrong for me while setting this up.

For one Hubbard site (single Fe atom, Fe-Al post-perovskite (PPv) at 100 GPa):
Uin = 4.0 eV -> Uout = 3.9460 eV (iteration 1) -> Uout = 3.9486 eV
(iteration 2), converged (|dU| = 0.0026 eV). Full inputs and outputs for
this run are in `examples/single_fe_site/`.

## What's here

- `scripts/contcar_to_qe_structure.py` - turns a VASP CONTCAR into the QE
  `ATOMIC_SPECIES` / `CELL_PARAMETERS` / `ATOMIC_POSITIONS` block
- `scripts/make_usc_inputs.py` - builds the three QE inputs (smeared SCF,
  fixed SCF, hp.x) for one iteration from a structure and an input U
- `scripts/check_convergence.py` - compares U across iterations and
  tells you if you're done, site by site
- `scripts/run_iteration.sh.template` - SLURM template with the sanity
  checks I actually use (did pw.x/hp.x finish, did SCF converge)
- `examples/single_fe_site/` - the simple case, one Hubbard atom
- `examples/two_inequivalent_fe_sites/` - the case that isn't simple,
  where hp.x finds your Hubbard atoms aren't equivalent

## Pseudopotentials

Not included here. Document which family/version you used and where to
get it - don't assume redistribution is fine without checking the
license (and if you're also using VASP for the relaxation step,
POTCAR files specifically are never redistributable under VASP's
license, regardless of what you do with the QE pseudopotentials).

## Requirements

Quantum ESPRESSO built with pw.x and hp.x (standard build, nothing
unusual needed) - developed and tested against QE 7.4.1, though nothing
here relies on anything version-specific. Python 3, no extra packages -
the scripts only use the standard library.

## A caveat on the U values

The converged U values in the examples are specific to the structure,
pressure, magnetic state, XC functional, pseudopotentials, and Hubbard
projector/numerical settings they were computed with. They aren't
transferable constants for "Fe in post-perovskite" in general - if you
change any of those, recompute U, don't reuse the number.

---

Developed while working on Fe-Al-bearing bridgmanite and post-perovskite
under lower-mantle conditions.
