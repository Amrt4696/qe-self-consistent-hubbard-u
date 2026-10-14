#!/usr/bin/env python3
"""
Compare Hubbard U values across iterations and tell you if you're done.

Give it the Hubbard_parameters.dat files from hp.x in order (iteration 1
first, then 2, 3, ...). Hubbard_parameters.dat columns are:
    site n.  type  label  spin  new_type  new_label  manifold  Hubbard U (eV)

This tracks each physical atom by its site number (column 1), not by its
label. That matters because hp.x gives inequivalent atoms of the same
species the same label (e.g. both show up as 'Fe') in whichever iteration
you haven't relabeled them yet - keying on the label alone would silently
merge two different atoms' U values into one and drop the other. Keying
on site number keeps them distinct even before you've relabeled them
Fe1/Fe2 for the next iteration (see examples/two_inequivalent_fe_sites).

If a site shows up more than once with different U values, that means
hp.x found inequivalent atoms of that species (see notes/common_problems.md)
- this script keeps them separate rather than averaging them, since
averaging them is exactly the wrong thing to do.

Note: this assumes atom ordering in the structure is unchanged between
iterations - true if you only rename species labels for inequivalent
atoms and don't reorder/add/remove atoms. If atom order does change
between the files you're comparing, site numbers won't line up and this
comparison will be wrong.

Usage:
    python3 check_convergence.py Usc_iter1/Hubbard_parameters.dat Usc_iter2/Hubbard_parameters.dat --tolerance 0.01
"""

import argparse
from pathlib import Path


def parse_hubbard_file(path):
    """Returns {site_number: (label, manifold, U)} for one
    Hubbard_parameters.dat file, keyed by the integer in the first
    ('site n.') column so inequivalent atoms of the same species never
    collide under a shared label."""
    entries = {}
    for line in Path(path).read_text().splitlines():
        fields = line.split()
        if len(fields) < 8:
            continue
        try:
            site_number = int(fields[0])
            u = float(fields[-1])
        except ValueError:
            continue
        label = fields[2]
        manifold = fields[6]
        entries[site_number] = (label, manifold, u)
    return entries


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", help="Hubbard_parameters.dat, one per iteration, in order")
    ap.add_argument("--tolerance", type=float, default=0.01, help="eV, default 0.01")
    args = ap.parse_args()

    iterations = [parse_hubbard_file(f) for f in args.files]
    all_sites = sorted(set().union(*[it.keys() for it in iterations])) if iterations else []

    if not all_sites:
        raise SystemExit("ERROR: couldn't find any Hubbard U values in these files - "
                          "check the file format matches what this script expects")

    print(f"{'site':<20}" + "".join(f"U_iter{i+1:<8}" for i in range(len(iterations))) + "last |dU|")
    all_converged = True
    for site_number in all_sites:
        row = [it.get(site_number) for it in iterations]
        label, manifold = next(((r[0], r[1]) for r in reversed(row) if r is not None), ("?", "?"))
        site_tag = f"{label}-{manifold} (site {site_number})"

        u_row = [r[2] if r is not None else None for r in row]
        row_str = "".join(f"{v:<13.4f}" if v is not None else f"{'--':<13}" for v in u_row)

        present = [v for v in u_row if v is not None]
        if len(present) >= 2:
            delta = abs(present[-1] - present[-2])
            status = "CONVERGED" if delta <= args.tolerance else "not converged"
            if delta > args.tolerance:
                all_converged = False
        else:
            delta, status = None, "only one iteration so far"

        delta_str = f"{delta:.4f}" if delta is not None else "--"
        print(f"{site_tag:<20}{row_str}{delta_str:<10}{status}")

    print()
    print(f"tolerance: {args.tolerance} eV")
    if all_converged and len(iterations) >= 2:
        print("all sites converged")
    elif len(iterations) < 2:
        print("need at least two iterations to say anything about convergence")
    else:
        print("not all sites converged yet - run another iteration")


if __name__ == "__main__":
    main()
