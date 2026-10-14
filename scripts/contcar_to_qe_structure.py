#!/usr/bin/env python3
"""
Turn a VASP CONTCAR/POSCAR into the ATOMIC_SPECIES / CELL_PARAMETERS /
ATOMIC_POSITIONS block that goes into a QE input file.

I split this out of the setup script because it's the part that has nothing
to do with Hubbard U specifically - anyone moving a relaxed structure from
VASP into QE needs the same conversion. make_usc_inputs.py imports
build_structure_block() directly; running this file does the same thing
from the command line.

Usage:
    python3 contcar_to_qe_structure.py CONTCAR \
        --species Al:26.9815385:Al.UPF Fe:55.845:Fe.UPF Mg:24.305:Mg.UPF \
                  O:15.999:O.UPF Si:28.0855:Si.UPF \
        --hubbard-first Fe
"""

import argparse
from pathlib import Path


def parse_species_arg(entries):
    species = {}
    for e in entries:
        parts = e.split(":")
        if len(parts) != 3:
            raise SystemExit(f"--species entries must be NAME:MASS:UPF, got '{e}'")
        name, mass, upf = parts
        species[name] = (float(mass), upf)
    return species


def read_contcar(path):
    lines = Path(path).read_text().splitlines()

    scale = float(lines[1].split()[0])
    if scale <= 0:
        raise SystemExit("ERROR: expected a positive scale factor on line 2")

    cell = [[scale * float(x) for x in row.split()[:3]] for row in lines[2:5]]

    names = lines[5].split()
    counts = [int(x) for x in lines[6].split()]
    composition = dict(zip(names, counts))
    nat = sum(counts)

    i = 7
    if lines[i].strip().lower().startswith("s"):
        i += 1  # selective dynamics line
    if not lines[i].strip().lower().startswith("d"):
        raise SystemExit("ERROR: this script only handles 'Direct' coordinates")
    i += 1

    labels = []
    for name, count in zip(names, counts):
        labels += [name] * count

    atoms = []
    for label, row in zip(labels, lines[i:i + nat]):
        xyz = [float(x) for x in row.split()[:3]]
        atoms.append((label, xyz))

    return cell, composition, atoms


def build_structure_block(contcar_path, species_entries, hubbard_first=None):
    """Returns (block_text, nat, ntyp). species_entries is the raw
    NAME:MASS:UPF list, same format as the --species CLI argument."""
    species = parse_species_arg(species_entries)
    cell, composition, atoms = read_contcar(contcar_path)

    missing = [name for name in composition if name not in species]
    if missing:
        raise SystemExit(f"ERROR: CONTCAR has species {missing} with no --species entry")

    if hubbard_first and hubbard_first in composition:
        atoms = ([a for a in atoms if a[0] == hubbard_first] +
                  [a for a in atoms if a[0] != hubbard_first])

    species_block = "\n".join(
        f"{name}  {mass:<10}  {upf}" for name, (mass, upf) in species.items()
    )
    cell_block = "\n".join(
        "  " + "  ".join(f"{x:.12f}" for x in row) for row in cell
    )
    pos_block = "\n".join(
        f"{label:<2}  {x:.12f}  {y:.12f}  {z:.12f}" for label, (x, y, z) in atoms
    )

    text = (f"ATOMIC_SPECIES\n{species_block}\n\n"
            f"CELL_PARAMETERS angstrom\n{cell_block}\n\n"
            f"ATOMIC_POSITIONS crystal\n{pos_block}\n")

    nat = sum(composition.values())
    ntyp = len(species)
    return text, nat, ntyp


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("contcar")
    ap.add_argument("--species", nargs="+", required=True,
                     help="NAME:MASS:UPF_FILENAME, one per element")
    ap.add_argument("--hubbard-first", default=None,
                     help="put atoms of this species first in ATOMIC_POSITIONS "
                          "(convenient, not required by QE)")
    args = ap.parse_args()

    text, nat, ntyp = build_structure_block(args.contcar, args.species, args.hubbard_first)
    print(text, end="")
    print(f"\n! nat={nat} ntyp={ntyp}")


if __name__ == "__main__":
    main()
