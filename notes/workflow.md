# The workflow

This is the self-consistent-U loop I actually run, written out in words.

1. Start from a relaxed structure (I get mine from a VASP relaxation, but
   any CONTCAR/POSCAR works - the relaxation itself isn't part of this
   repo, see the README).
2. Run a spin-polarized SCF with smeared occupations and some initial
   guess for U. This one's metallic-like and easy to converge; its job is
   just to get a reasonable starting density for step 3.
3. Run a second SCF from that density, but this time with fixed
   occupations pinned to the magnetic state you actually care about
   (`tot_magnetization` set explicitly). For the insulating Fe-bearing
   systems in these examples, this fixed-occupation step is what gets me
   to the electronic/magnetic state I actually want hp.x to compute U
   for - skipping straight to hp.x after the smeared SCF instead gives
   you U for whatever state the smeared SCF happened to land in, which
   usually isn't it. (If your system is genuinely metallic, you may not
   need this step the same way - this workflow is written for the
   insulating case.)
4. Run hp.x on top of that fixed-occupation SCF. It gives you a new U for
   each Hubbard site.
5. Feed that U back in as the input U for the next iteration, repeat from
   step 2 with a fresh scratch directory.
6. Stop once the change between iterations is small enough -
   `check_convergence.py` does this comparison for you.

As a diagram:

```
initial U
   |
   v
SCF, smeared occupations
   |
   v
SCF, fixed occupations (your target magnetic state)
   |
   v
hp.x  -->  new U
   |
   +---- not converged? use new U as input, go again
   |
   converged -> done
```

A couple of things that aren't obvious from the diagram:

**The magnetic state matters.** U depends on which electronic/magnetic
state you converged to - a high-spin Fe and a low-spin Fe at the same
structure won't give you the same self-consistent U. If you're comparing
U across pressures or compositions, make sure you're comparing the same
magnetic state each time, not whatever the SCF happened to fall into.

**Inequivalent Hubbard sites.** If your structure has more than one atom
of the Hubbard species, hp.x might find they're not actually equivalent
(different local environments, different occupations). When that
happens, don't average the two U values - treat them as separate atomic
types in the next iteration (see `examples/` and `common_problems.md`).
