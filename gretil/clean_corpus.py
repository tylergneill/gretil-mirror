#!/usr/bin/env python3
"""
clean_corpus.py — Clean and rename GRETIL corpus files.

1. Deletes all CSX (_c.txt) files, after verifying each has a corresponding Unicode .htm.
2. Loops through TEI XML files, extracts the source .htm path from <notesStmt>,
   and renames both the .htm and IAST _r.txt file to match the TEI XML filename (sans .xml).
3. Updates the <ref target> in each XML to point to the new filename.

Expected directory layouts (auto-detected):

  Use case 1 — downloaded "All Sanskrit Texts" zip:
    1_sanskr/
      clean_corpus.py
      1_veda/
      2_epic/
      ...
      tei/           <- TEI XML files here
        transformations/

  Use case 2 — cloned gretil-mirror repo:
    gretil-mirror/
      gretil/
        clean_corpus.py
        1_sanskr/
        2_pali/
        corpustei/   <- TEI XML files here
          transformations/
        ...

Usage:
    python clean_corpus.py [--keep both|htm|txt] [--dry-run]
"""

import argparse
import os
import re
import shutil
import sys


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Clean and rename GRETIL corpus files.",
        epilog="Run from the directory containing the text subdirectories.",
    )
    parser.add_argument(
        "--keep",
        choices=["both", "htm", "txt"],
        default="both",
        help="Which files to keep after renaming: both (default), htm only, or txt only",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without performing them",
    )
    return parser.parse_args()


def detect_layout():
    """Auto-detect layout and return (base_dir, tei_dir).

    base_dir: the directory containing text subdirectories (1_veda/, 2_epic/, etc.)
    tei_dir:  the directory containing TEI XML files
    """
    # Case 1: zip layout — script is inside 1_sanskr/, TEI lives at 1_sanskr/tei/
    tei_in_zip = os.path.join(SCRIPT_DIR, "tei")
    if os.path.isdir(tei_in_zip):
        return SCRIPT_DIR, tei_in_zip

    # Case 2: repo layout — script is in gretil/, TEI lives at gretil/corpustei/
    corpustei = os.path.join(SCRIPT_DIR, "corpustei")
    sanskr_dir = os.path.join(SCRIPT_DIR, "1_sanskr")
    if os.path.isdir(corpustei) and os.path.isdir(sanskr_dir):
        return sanskr_dir, corpustei

    print(
        "Error: could not detect directory layout.\n"
        "Expected either:\n"
        "  - tei/ folder alongside this script (zip download), or\n"
        "  - corpustei/ and 1_sanskr/ alongside this script (repo clone)",
        file=sys.stderr,
    )
    sys.exit(1)


def find_text_subdirs(base_dir):
    """Find text subdirectories (numbered category folders)."""
    subdirs = []
    for entry in sorted(os.listdir(base_dir)):
        path = os.path.join(base_dir, entry)
        if os.path.isdir(path) and entry not in ("tei", "corpustei") and not entry.startswith("."):
            subdirs.append(entry)
    return subdirs


def find_csx_files(base_dir, subdirs):
    """Find all _c.txt files in the text subdirectories."""
    csx_files = []
    for subdir in subdirs:
        subdir_path = os.path.join(base_dir, subdir)
        for root, dirs, files in os.walk(subdir_path):
            for f in files:
                if f.endswith(".txt") and f[:-4].endswith("c"):
                    csx_files.append(os.path.join(root, f))
    return csx_files


def verify_and_delete_csx(csx_files, dry_run):
    """Delete CSX files, but only if each has a corresponding Unicode .htm."""
    deleted = 0
    skipped = []
    for c in csx_files:
        stem = os.path.basename(c)[:-4]  # strip .txt
        htm = os.path.join(os.path.dirname(c), stem[:-1] + "u.htm")
        if not os.path.exists(htm):
            skipped.append(c)
            continue
        if dry_run:
            print(f"  [dry-run] DELETE {c}")
        else:
            os.remove(c)
        deleted += 1

    if skipped:
        print(f"WARNING: {len(skipped)} CSX files skipped (no matching .htm):")
        for s in skipped:
            print(f"  {s}")
    return deleted


def extract_htm_ref(xml_path):
    """Extract the .htm relative path from <notesStmt> in a TEI XML file.

    Returns a path like '1_sanskr/6_sastra/3_phil/saiva/bhairstu.htm',
    or for the zip layout just '6_sastra/3_phil/saiva/bhairstu.htm'
    (the '1_sanskr/' prefix is stripped since base_dir IS 1_sanskr/).
    """
    with open(xml_path, "r", errors="replace") as f:
        content = f.read()

    m = re.search(
        r"<notesStmt>.*?<ref target=\"([^\"]+)\">",
        content,
        re.DOTALL,
    )
    if not m:
        return None

    target = m.group(1)

    # The URL looks like .../gretil/1_sanskr/.../file.htm
    # Extract the part after /gretil/ to get a path relative to the gretil/ dir
    idx = target.find("/gretil/")
    if idx >= 0:
        return target[idx + 8:]  # e.g. "1_sanskr/6_sastra/3_phil/saiva/bhairstu.htm"
    return None


def resolve_htm_rel(htm_ref, base_dir):
    """Resolve the htm ref (from XML) to a path relative to base_dir.

    The ref is always like '1_sanskr/...'. If base_dir IS 1_sanskr/,
    we need to strip the '1_sanskr/' prefix.
    """
    # Direct match first
    candidate = os.path.join(base_dir, htm_ref)
    if os.path.exists(candidate):
        return htm_ref

    # If base_dir is 1_sanskr/ itself, strip the 1_sanskr/ prefix from the ref
    parts = htm_ref.split("/", 1)
    if len(parts) == 2:
        stripped = parts[1]
        candidate = os.path.join(base_dir, stripped)
        if os.path.exists(candidate):
            return stripped

    return None


def derive_txt_path(htm_rel):
    """Given a relative .htm path, derive the corresponding _r.txt path."""
    stem = htm_rel[:-4]  # strip .htm
    if stem.endswith("u"):
        return stem[:-1] + "r.txt"
    return None


def rename_files(base_dir, tei_dir, subdirs, keep, dry_run):
    """Rename .htm and .txt files to match their TEI XML filename."""
    subdir_set = set(subdirs)
    renamed = 0
    skipped = []
    absent_subdirs = {}  # subdir -> count of skipped entries

    for xml_name in sorted(os.listdir(tei_dir)):
        if not xml_name.endswith(".xml"):
            continue

        xml_path = os.path.join(tei_dir, xml_name)
        new_stem = xml_name[:-4]  # strip .xml

        htm_ref = extract_htm_ref(xml_path)
        if htm_ref is None:
            skipped.append((xml_name, "no valid <ref> in notesStmt"))
            continue

        htm_rel = resolve_htm_rel(htm_ref, base_dir)
        if htm_rel is None:
            # Check if it's in an absent subdirectory
            top_dir = htm_ref.split("/")[0]
            # For zip layout, the first component might be 1_sanskr
            if top_dir == os.path.basename(base_dir):
                parts = htm_ref.split("/")
                top_dir = parts[1] if len(parts) > 1 else top_dir
            if top_dir not in subdir_set:
                absent_subdirs[top_dir] = absent_subdirs.get(top_dir, 0) + 1
                continue
            skipped.append((xml_name, f"referenced .htm not found: {htm_ref}"))
            continue

        # Check the top-level subdir is present
        top_dir = htm_rel.split("/")[0]
        if top_dir not in subdir_set:
            absent_subdirs[top_dir] = absent_subdirs.get(top_dir, 0) + 1
            continue

        htm_path = os.path.join(base_dir, htm_rel)
        htm_dir = os.path.dirname(htm_path)
        txt_rel = derive_txt_path(htm_rel)
        txt_path = os.path.join(base_dir, txt_rel) if txt_rel else None
        txt_exists = txt_path and os.path.exists(txt_path)

        new_htm = os.path.join(htm_dir, new_stem + ".htm")
        new_txt = os.path.join(htm_dir, new_stem + ".txt") if txt_rel else None

        # Rename .htm
        if keep in ("both", "htm"):
            if dry_run:
                print(f"  [dry-run] RENAME {htm_path} -> {new_htm}")
            else:
                shutil.move(htm_path, new_htm)
        else:
            if dry_run:
                print(f"  [dry-run] DELETE {htm_path}")
            else:
                os.remove(htm_path)

        # Rename .txt
        if txt_exists:
            if keep in ("both", "txt"):
                if dry_run:
                    print(f"  [dry-run] RENAME {txt_path} -> {new_txt}")
                else:
                    shutil.move(txt_path, new_txt)
            else:
                if dry_run:
                    print(f"  [dry-run] DELETE {txt_path}")
                else:
                    os.remove(txt_path)
        elif keep in ("both", "txt"):
            skipped.append((xml_name, f"no _r.txt found for {htm_rel}"))

        # Update the <ref target> in the XML
        update_xml_ref(xml_path, htm_ref, new_stem, keep, dry_run)

        renamed += 1

    if absent_subdirs:
        total = sum(absent_subdirs.values())
        breakdown = ", ".join(f"{k}: {v}" for k, v in sorted(absent_subdirs.items()))
        print(f"Skipped {total} entries for absent subdirectories ({breakdown})")

    if skipped:
        print(f"\nWARNINGS ({len(skipped)}):")
        for name, reason in skipped:
            print(f"  {name}: {reason}")

    return renamed


def update_xml_ref(xml_path, old_htm_ref, new_stem, keep, dry_run):
    """Update the <ref target> URL in the XML to use the new filename."""
    with open(xml_path, "r", errors="replace") as f:
        content = f.read()

    old_basename = os.path.basename(old_htm_ref)
    if keep == "txt":
        new_ref_basename = new_stem + ".txt"
    else:
        new_ref_basename = new_stem + ".htm"

    def replace_ref(m):
        url = m.group(1)
        new_url = url.rsplit("/", 1)[0] + "/" + new_ref_basename
        return f'<ref target="{new_url}">{new_ref_basename}</ref>'

    new_content = re.sub(
        r'<ref target="([^"]*/' + re.escape(old_basename) + r')">([^<]+)</ref>',
        replace_ref,
        content,
    )

    if new_content != content:
        if dry_run:
            print(f"  [dry-run] UPDATE XML ref in {os.path.basename(xml_path)}")
        else:
            with open(xml_path, "w") as f:
                f.write(new_content)


def main():
    args = parse_args()
    base_dir, tei_dir = detect_layout()
    subdirs = find_text_subdirs(base_dir)

    print(f"Text directory: {base_dir}")
    print(f"TEI directory:  {tei_dir}")
    print(f"Text subdirectories found: {', '.join(subdirs)}\n")

    print("=== Step 1: Delete redundant CSX (_c.txt) files ===")
    csx_files = find_csx_files(base_dir, subdirs)
    deleted = verify_and_delete_csx(csx_files, args.dry_run)
    print(f"{'Would delete' if args.dry_run else 'Deleted'} {deleted} CSX files.\n")

    print("=== Step 2: Rename .htm/.txt to match TEI XML filenames ===")
    renamed = rename_files(base_dir, tei_dir, subdirs, args.keep, args.dry_run)
    print(f"\n{'Would rename' if args.dry_run else 'Renamed'} files for {renamed} TEI entries.")
    print(f"Mode: --keep {args.keep}")


if __name__ == "__main__":
    main()
