#!/usr/bin/env python3
"""
Build the three QE inputs for one self-consistent-U iteration: a smeared
spin-polarized SCF, a fixed-occupation SCF at the magnetic state you want,
and an hp.x run on top of that.

I used to have two near-identical shell scripts for iteration 1 and
iteration 2 that differed in about three lines. This replaces both - you
just pass the input U for whichever iteration you're on, and point
--prefix/--outdir at a fresh scratch directory each time (see
notes/common_problems.md for why reusing one isn't a good idea).

Usage:
    python3 make_usc_inputs.py \
        --contcar ../structures/CONTCAR \
        --species Al:26.9815385:Al.UPF Fe:55.845:Fe.UPF Mg:24.305:Mg.UPF \
                  O:15.999:O.UPF Si:28.0855:Si.UPF \
        --hubbard-species Fe --hubbard-manifold 3d --hubbard-u 4.0 \
        --prefix my_system_iter1 --outdir ../tmp --pseudo-dir /path/to/pseudos \
        --starting-magnetization Fe:0.8 \
        --tot-magnetization 5 \
        --kpoints "2 2 2 0 0 0"

Writes 01_scf_smear/scf.in, 02_scf_fixed/scf.in and 03_hp/hp.in (directory
names are configurable, see --help).
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from contcar_to_qe_structure import build_structure_block


def starting_magnetization_lines(species_order, mag_map):
    lines = []
    for i, name in enumerate(species_order, start=1):
        value = mag_map.get(name, 0.0)
        lines.append(f" starting_magnetization({i})={value}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--contcar", required=True)
    ap.add_argument("--species", nargs="+", required=True,
                     help="NAME:MASS:UPF, in the order you want QE species indices assigned")
    ap.add_argument("--hubbard-species", required=True)
    ap.add_argument("--hubbard-manifold", default="3d")
    ap.add_argument("--hubbard-u", type=float, required=True, help="U_in for this iteration")
    ap.add_argument("--prefix", required=True)
    ap.add_argument("--outdir", default="../tmp")
    ap.add_argument("--pseudo-dir", required=True)
    ap.add_argument("--ecutwfc", type=float, default=80.0)
    ap.add_argument("--ecutrho", type=float, default=640.0)
    ap.add_argument("--degauss", type=float, default=0.005)
    ap.add_argument("--starting-magnetization", nargs="*", default=[],
                     help="NAME:VALUE, repeatable - species not listed default to 0.0")
    ap.add_argument("--tot-magnetization", type=int, required=True,
                     help="total magnetization for the fixed-occupation SCF, in mu_B")
    ap.add_argument("--kpoints", default="2 2 2 0 0 0")
    ap.add_argument("--nq", default="1 1 1")
    ap.add_argument("--conv-thr-chi", default="1.0d-5")
    ap.add_argument("--find-atpert", default="1")
    ap.add_argument("--outdir-01", default="01_scf_smear")
    ap.add_argument("--outdir-02", default="02_scf_fixed")
    ap.add_argument("--outdir-03", default="03_hp")
    args = ap.parse_args()

    species_order = [e.split(":")[0] for e in args.species]
    mag_map = {}
    for e in args.starting_magnetization:
        name, value = e.split(":")
        mag_map[name] = float(value)

    struct, nat, ntyp = build_structure_block(args.contcar, args.species, args.hubbard_species)
    struct += f"\nHUBBARD atomic\nU {args.hubbard_species}-{args.hubbard_manifold} {args.hubbard_u:.6f}\n"
    struct += f"\nK_POINTS automatic\n{args.kpoints}\n"

    mag_lines = starting_magnetization_lines(species_order, mag_map)

    scf_smear = f"""&CONTROL
 calculation='scf'
 prefix='{args.prefix}'
 outdir='{args.outdir}'
 pseudo_dir='{args.pseudo_dir}'
 verbosity='low'
 disk_io='medium'
 tstress=.false.
 tprnfor=.false.
/
&SYSTEM
 ibrav=0
 nat={nat}
 ntyp={ntyp}
 ecutwfc={args.ecutwfc}
 ecutrho={args.ecutrho}
 occupations='smearing'
 smearing='gaussian'
 degauss={args.degauss}
 nspin=2
 nosym=.true.
{mag_lines}
/
&ELECTRONS
 conv_thr=1.0d-8
 mixing_beta=0.2
 electron_maxstep=250
/
{struct}"""

    scf_fixed = f"""&CONTROL
 calculation='scf'
 prefix='{args.prefix}'
 outdir='{args.outdir}'
 pseudo_dir='{args.pseudo_dir}'
 verbosity='low'
 disk_io='medium'
 tstress=.false.
 tprnfor=.false.
/
&SYSTEM
 ibrav=0
 nat={nat}
 ntyp={ntyp}
 ecutwfc={args.ecutwfc}
 ecutrho={args.ecutrho}
 occupations='fixed'
 nspin=2
 tot_magnetization={args.tot_magnetization}
 nosym=.true.
/
&ELECTRONS
 conv_thr=1.0d-8
 mixing_beta=0.2
 electron_maxstep=250
 startingpot='file'
 startingwfc='file'
/
{struct}"""

    hp_in = f"""&inputhp
 prefix='{args.prefix}'
 outdir='{args.outdir}'
 nq1={args.nq.split()[0]}
 nq2={args.nq.split()[1]}
 nq3={args.nq.split()[2]}
 conv_thr_chi={args.conv_thr_chi}
 find_atpert={args.find_atpert}
/
"""

    for d, text, name in [
        (args.outdir_01, scf_smear, "scf.in"),
        (args.outdir_02, scf_fixed, "scf.in"),
        (args.outdir_03, hp_in, "hp.in"),
    ]:
        out_dir = Path(d)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / name).write_text(text)
        print(f"wrote {out_dir / name}")


if __name__ == "__main__":
    main()
