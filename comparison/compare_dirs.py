#!/usr/bin/env python3
"""Compare GRETIL mirror directories against 1_sanskr to find moves, additions, and removals.

Writes both raw diff output and an analysis report to disk.
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict

BASE = Path("/Users/tyler/Git/gretil")

# --- Part 1: Compare 1_sanskr (before) vs GRETIL-mirror 1_sanskr (after) ---

BEFORE_ROOT = BASE / "1_sanskr"
AFTER_ROOT = BASE / "GRETIL-mirror-dominik/gretil.sub.uni-goettingen.de/gretil/1_sanskr"

SUBDIRS = ["1_veda", "2_epic", "3_purana", "4_rellit", "5_poetry", "6_sastra", "7_fromindonesia"]


def collect_files(root, subdirs=None):
    """Collect files under root, optionally restricted to subdirs. Returns {relative_path: absolute_path} and {filename: [relative_paths]}."""
    by_rel = {}
    by_name = defaultdict(list)
    if subdirs:
        dirs = [root / s for s in subdirs if (root / s).is_dir()]
    else:
        dirs = [root]
    for d in dirs:
        for dirpath, _, filenames in os.walk(d):
            for f in filenames:
                abs_path = Path(dirpath) / f
                rel = abs_path.relative_to(root)
                by_rel[str(rel)] = abs_path
                by_name[f].append(str(rel))
    return by_rel, by_name


def compare(before_root, after_root, before_subdirs=None, after_subdirs=None, label=""):
    """Compare two directory trees. Returns (same, moved, added, removed, case_renames) for analysis."""
    lines = []
    def p(s=""):
        lines.append(s)

    p(f"\n{'='*80}")
    p(f"  {label}")
    p(f"  Before: {before_root}")
    p(f"  After:  {after_root}")
    p(f"{'='*80}")

    before_rel, before_by_name = collect_files(before_root, before_subdirs)
    after_rel, after_by_name = collect_files(after_root, after_subdirs)

    before_keys = set(before_rel.keys())
    after_keys = set(after_rel.keys())

    same = before_keys & after_keys
    only_before = before_keys - after_keys
    only_after = after_keys - before_keys

    moved = []       # (filename, before_rel, after_rel)
    added = []       # (rel_path,)
    removed = []     # (rel_path,)
    case_renames = [] # (before_rel, after_rel)

    # Check files only in "after": moved from "before" (exact or case-insensitive match)?
    before_lower_name = defaultdict(list)  # lowercase filename -> [rel_paths in before]
    for rel in only_before:
        before_lower_name[Path(rel).name.lower()].append(rel)

    matched_before = set()
    for rel in sorted(only_after):
        fname = Path(rel).name
        # Exact filename match = moved
        if fname in before_by_name:
            for b_rel in before_by_name[fname]:
                if b_rel in only_before:
                    moved.append((fname, b_rel, rel))
                    matched_before.add(b_rel)
        else:
            # Case-insensitive match = case rename (possibly also moved)
            lname = fname.lower()
            if lname in before_lower_name:
                for b_rel in before_lower_name[lname]:
                    if b_rel not in matched_before:
                        case_renames.append((b_rel, rel))
                        matched_before.add(b_rel)
            else:
                added.append(rel)

    # Files only in "before" not accounted for = removed
    for rel in sorted(only_before):
        if rel in matched_before:
            continue
        fname = Path(rel).name
        if fname in after_by_name:
            pass  # Already captured from after side
        else:
            removed.append(rel)

    if not moved and not added and not removed and not case_renames:
        p("\nNo differences found.")
    else:
        if case_renames:
            # Separate true case-only renames from case+move
            true_case = [(b, a) for b, a in case_renames if Path(b).parent == Path(a).parent]
            case_and_move = [(b, a) for b, a in case_renames if Path(b).parent != Path(a).parent]
            if true_case:
                p(f"\n--- CASE RENAMES ({len(true_case)}) ---")
                for b, a in sorted(true_case):
                    p(f"  {b}  -->  {a}")
            if case_and_move:
                p(f"\n--- MOVED + CASE RENAMED ({len(case_and_move)}) ---")
                for b, a in sorted(case_and_move):
                    p(f"  {b}  -->  {a}")

        if moved:
            p(f"\n--- MOVED ({len(moved)}) ---")
            for fname, b, a in sorted(moved):
                p(f"  {fname}")
                p(f"    before: {b}")
                p(f"    after:  {a}")

        if added:
            p(f"\n--- ADDED (in after only, {len(added)}) ---")
            for rel in sorted(added):
                p(f"  {rel}")

        if removed:
            p(f"\n--- REMOVED (in before only, {len(removed)}) ---")
            for rel in sorted(removed):
                p(f"  {rel}")

        p(f"\nSummary: {len(same)} identical paths, {len(case_renames)} case renames, "
          f"{len(moved)} moved, {len(added)} added, {len(removed)} removed")

    output = "\n".join(lines)
    print(output)
    return output, same, moved, added, removed, case_renames, before_rel, after_rel, before_by_name, after_by_name


def analyze_tei_removed(removed, after_by_name):
    """Analyze the pattern of removed TEI files — are they partial/fragment versions?"""
    lines = []
    def p(s=""):
        lines.append(s)

    after_stems = set()
    for name_list in after_by_name.values():
        for rel in name_list:
            after_stems.add(Path(rel).stem)

    # Categorize removed files
    xml_files = [f for f in removed if f.endswith('.xml')]
    htm_files = [f for f in removed if f.endswith('.htm')]
    txt_files = [f for f in removed if f.endswith('.txt')]
    other_files = [f for f in removed if not f.endswith(('.xml', '.htm', '.txt'))]

    # Check which removed files have a base-name match in after
    # (i.e., partial version whose complete counterpart exists)
    superseded = []
    truly_gone = []
    for f in removed:
        stem = Path(f).stem
        # Try stripping trailing numeric range suffixes
        base = re.sub(r'[\d,\.\-]+$', '', stem).rstrip('-')
        # Also try stripping -comm, -subcomm, -alt, -rev suffixes
        base2 = re.sub(r'-(comm|subcomm|alt|rev)$', '', base)
        if stem in after_stems:
            superseded.append((f, stem, "exact stem"))
        elif base in after_stems:
            superseded.append((f, base, "base match (stripped range)"))
        elif base2 in after_stems:
            superseded.append((f, base2, "base match (stripped suffix)"))
        else:
            truly_gone.append(f)

    p(f"\n{'='*80}")
    p(f"  ANALYSIS: Removed TEI files breakdown")
    p(f"{'='*80}")
    p(f"\nTotal removed: {len(removed)}")
    p(f"  .xml source files: {len(xml_files)}")
    p(f"  .htm transformations: {len(htm_files)}")
    p(f"  .txt transformations: {len(txt_files)}")
    if other_files:
        p(f"  other: {len(other_files)}")
    p(f"\nSuperseded (base name matches a file in corpustei): {len(superseded)}")
    p(f"  These are likely partial/fragment versions replaced by complete texts.")
    p(f"\nTruly absent (no matching base name in corpustei): {len(truly_gone)}")

    if truly_gone:
        p(f"\n--- TRULY ABSENT from corpustei ({len(truly_gone)}) ---")
        for f in sorted(truly_gone):
            p(f"  {f}")

    # Group superseded by their base text for a cleaner view
    if superseded:
        p(f"\n--- SUPERSEDED partial versions ({len(superseded)}) ---")
        by_base = defaultdict(list)
        for f, base, match_type in superseded:
            by_base[base].append((f, match_type))
        for base in sorted(by_base):
            files = by_base[base]
            if len(files) <= 3:
                for f, mt in files:
                    p(f"  {f}  ({mt} -> {base})")
            else:
                p(f"  [{len(files)} files] matching base '{base}':")
                for f, mt in files:
                    p(f"    {f}")

    return "\n".join(lines)


# ===== Run comparisons =====
all_output = []

# Part 1
result1 = compare(
    BEFORE_ROOT, AFTER_ROOT,
    before_subdirs=SUBDIRS, after_subdirs=SUBDIRS,
    label="Part 1: 1_sanskr subdirectories"
)
all_output.append(result1[0])

# Part 1 analysis
part1_analysis = []
part1_analysis.append(f"\n{'='*80}")
part1_analysis.append(f"  ANALYSIS: Part 1 details")
part1_analysis.append(f"{'='*80}")
_, same1, moved1, added1, removed1, case1, _, _, _, _ = result1
if case1:
    part1_analysis.append(f"\nCase renames are likely intentional normalization (e.g., UPPERCASE.HTM -> lowercase.htm).")
    for b, a in case1:
        bname = Path(b).name
        aname = Path(a).name
        if bname.lower() == aname.lower():
            part1_analysis.append(f"  '{bname}' -> '{aname}': filename case normalization")
        else:
            part1_analysis.append(f"  '{b}' -> '{a}': path + case change")

if moved1:
    part1_analysis.append(f"\nMoved files represent reclassification:")
    for fname, b, a in moved1:
        b_parts = Path(b).parts
        a_parts = Path(a).parts
        # Find where paths diverge
        for i, (bp, ap) in enumerate(zip(b_parts, a_parts)):
            if bp != ap:
                part1_analysis.append(f"  {fname}: reclassified from '{'/'.join(b_parts[i:-1])}' to '{'/'.join(a_parts[i:-1])}'")
                break

if added1 and removed1:
    # Check for add/remove pairs that are really case renames not caught above
    add_lower = {Path(a).name.lower(): a for a in added1}
    rem_lower = {Path(r).name.lower(): r for r in removed1}
    overlap = set(add_lower) & set(rem_lower)
    if overlap:
        part1_analysis.append(f"\nPossible case-rename pairs (added + removed with same name, different case):")
        for lname in overlap:
            part1_analysis.append(f"  removed '{rem_lower[lname]}' -> added '{add_lower[lname]}'")

part1_analysis_str = "\n".join(part1_analysis)
print(part1_analysis_str)
all_output.append(part1_analysis_str)

# Part 2
result2 = compare(
    BASE / "1_sanskr" / "tei",
    BASE / "GRETIL-mirror-dominik/gretil.sub.uni-goettingen.de/gretil/corpustei",
    label="Part 2: TEI (1_sanskr/tei vs corpustei)"
)
all_output.append(result2[0])

# Part 2 deep analysis
_, same2, moved2, added2, removed2, case2, _, _, _, after_by_name2 = result2
if removed2:
    tei_analysis = analyze_tei_removed(removed2, after_by_name2)
    print(tei_analysis)
    all_output.append(tei_analysis)

# Write report to disk
report_path = BASE / "compare_dirs_report.txt"
with open(report_path, "w") as f:
    f.write("GRETIL Directory Comparison Report\n")
    f.write("Generated by compare_dirs.py\n")
    f.write("\n".join(all_output))
print(f"\n\nReport written to: {report_path}")
