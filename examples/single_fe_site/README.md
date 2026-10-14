# Example: one Hubbard site

The simplest case - a structure with a single Fe atom, nothing
inequivalent to worry about.

## What's actually here

`iter1/` has the QE inputs I actually ran
(`scf_smear.in`, `scf_fixed.in`, `hp.in`, with the Hubbard U input set to
4.0 eV) and the resulting `Hubbard_parameters.dat`. `iter2/` has the
second iteration's `Hubbard_parameters.dat` (U_in = 3.9460 eV, the output
of iteration 1).

`CONTCAR` is regenerated directly from `iter1/scf_fixed.in`'s structure
block (same cell, same atomic positions, just converted back to VASP's
format/species grouping) rather than kept as a separately-sourced file -
that way it's guaranteed to actually match the QE inputs sitting next to
it, instead of silently drifting from whatever VASP run originally
produced it.

`pseudo_dir` in the `.in` files is set to a placeholder path - swap it
for wherever your own pseudopotentials live.

## Reproducing or extending it

To regenerate `iter1`'s inputs from `CONTCAR` yourself (or adapt this for
your own structure), make a fresh directory for the iteration and run
`make_usc_inputs.py` from inside it, using its default output folder names
(`01_scf_smear/`, `02_scf_fixed/`, `03_hp/`) so the layout matches what
`run_iteration.sh.template` expects:

```
mkdir iter1_regenerated && cd iter1_regenerated
python3 ../../../scripts/make_usc_inputs.py \
    --contcar ../CONTCAR \
    --species Al:26.9815385:Al.UPF Fe:55.845:Fe.UPF Mg:24.305:Mg.UPF \
              O:15.999:O.UPF Si:28.0855:Si.UPF \
    --hubbard-species Fe --hubbard-manifold 3d --hubbard-u 4.0 \
    --prefix my_system_iter1 --outdir ../tmp \
    --pseudo-dir /path/to/your/pseudopotentials \
    --starting-magnetization Fe:0.8 \
    --tot-magnetization 5
```

This writes `01_scf_smear/scf.in`, `02_scf_fixed/scf.in` and `03_hp/hp.in`
inside `iter1_regenerated/`. For iteration 2, make another directory the
same way and rerun with `--hubbard-u 3.9460` (iteration 1's Uout) and a
fresh prefix.

Copy `scripts/run_iteration.sh.template` into `iter1_regenerated/` (it
expects to sit next to `01_scf_smear/`, `02_scf_fixed/`, `03_hp/`), fill in
your cluster's SBATCH header, and submit it from there.

## Checking convergence

```
python3 ../../scripts/check_convergence.py iter1/Hubbard_parameters.dat iter2/Hubbard_parameters.dat
```

## Result

```
site        U_iter1    U_iter2    |dU|
Fe-3d       3.9460     3.9486     0.0026    CONVERGED
```

Uin = 4.0 eV -> Uout(1) = 3.9460 eV -> Uout(2) = 3.9486 eV. Change between
iterations 1 and 2 is 0.0026 eV, well under the 0.01 eV tolerance, so I
call this converged after two iterations.
