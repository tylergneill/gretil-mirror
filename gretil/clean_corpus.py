#!/usr/bin/env python3
"""
clean_corpus.py — Clean and rename GRETIL corpus files.

1. Deletes CSX transliteration files (*c.txt) when they contain the CSX marker `‡` (ā).
2. Deletes RE transliteration files (*r.txt) when they contain the RE marker `√` (ā).
3. Deletes MBh archive artifacts: `mbh1-18*.zip` and the `mbh/sas` subtree.
4. Renames the referenced .htm file to match the TEI XML filename.
5. Updates the <ref target> in each XML to point to the new filename.

The transliteration files are legacy-encoded, typically MacRoman rather than UTF-8,
so marker detection is done against raw bytes using known encodings.

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
    python clean_corpus.py [--dry-run]
"""

import argparse
import glob
import os
import re
import shutil
import sys


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MBH_DIR = os.path.join(SCRIPT_DIR, "1_sanskr", "2_epic", "mbh")
CSX_MARKER = "\u2021"
RE_MARKER = "\u221a"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Clean and rename GRETIL corpus files.",
        epilog="Run from the directory containing the text subdirectories.",
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
    """Find all *c.txt files in the text subdirectories."""
    csx_files = []
    for subdir in subdirs:
        subdir_path = os.path.join(base_dir, subdir)
        for root, dirs, files in os.walk(subdir_path):
            for f in files:
                if f.endswith(".txt") and f[:-4].endswith("c"):
                    csx_files.append(os.path.join(root, f))
    return csx_files


def find_re_files(base_dir, subdirs):
    """Find all *r.txt files in the text subdirectories."""
    re_files = []
    for subdir in subdirs:
        subdir_path = os.path.join(base_dir, subdir)
        for root, dirs, files in os.walk(subdir_path):
            for f in files:
                if f.endswith(".txt") and f[:-4].endswith("r"):
                    re_files.append(os.path.join(root, f))
    return re_files


def file_contains(path, needle):
    """Return whether a file contains a marker in known legacy encodings."""
    with open(path, "rb") as f:
        data = f.read()

    for encoding in ("utf-8", "mac_roman", "cp1252"):
        try:
            encoded_needle = needle.encode(encoding)
        except UnicodeEncodeError:
            continue
        if encoded_needle in data:
            return True
    return False


def maybe_delete_marked_txt(path, suffix_label, marker, dry_run):
    """Delete a marked text file when its encoding-specific marker is present."""
    if not os.path.exists(path):
        return "missing"

    if not file_contains(path, marker):
        print(f"{suffix_label} file NOT deleted: {path}")
        return "kept"

    if not dry_run:
        os.remove(path)
    return "deleted"


def maybe_delete_path(path, dry_run):
    """Delete a file or directory if it exists."""
    if not os.path.exists(path):
        return "missing"

    if not dry_run:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    return "deleted"


def count_tree_entries(path):
    """Count all filesystem entries under a path, including the path itself."""
    if not os.path.exists(path):
        return 0

    total = 1
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            total += len(dirs) + len(files)
    return total


def verify_and_delete_csx(csx_files, dry_run):
    """Delete *c.txt files only when they contain the CSX marker `‡`."""
    deleted = 0
    kept = 0
    for c in csx_files:
        result = maybe_delete_marked_txt(c, "*c.txt", CSX_MARKER, dry_run)
        if result == "deleted":
            deleted += 1
        elif result == "kept":
            kept += 1
    return {"total": len(csx_files), "deleted": deleted, "kept": kept}


def verify_and_delete_re(re_files, dry_run):
    """Delete *r.txt files only when they contain the RE marker `√`."""
    deleted = 0
    kept = 0
    for path in re_files:
        result = maybe_delete_marked_txt(path, "*r.txt", RE_MARKER, dry_run)
        if result == "deleted":
            deleted += 1
        elif result == "kept":
            kept += 1
    return {"total": len(re_files), "deleted": deleted, "kept": kept}


def cleanup_mbh_artifacts(dry_run):
    """Delete `mbh1-18*.zip` files and the `mbh/sas` subtree."""
    zip_paths = sorted(glob.glob(os.path.join(MBH_DIR, "mbh1-18*.zip")))
    zip_deleted = 0
    for path in zip_paths:
        if maybe_delete_path(path, dry_run) == "deleted":
            zip_deleted += 1

    sas_path = os.path.join(MBH_DIR, "sas")
    sas_entries = count_tree_entries(sas_path)
    sas_result = maybe_delete_path(sas_path, dry_run)

    return {
        "zip_found": len(zip_paths),
        "zip_deleted": zip_deleted,
        "sas_path": sas_path,
        "sas_entries": sas_entries,
        "sas_deleted": sas_entries if sas_result == "deleted" else 0,
        "sas_missing": 1 if sas_result == "missing" else 0,
    }


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


def count_htm_files(base_dir, excluded_paths=None):
    """Count remaining .htm files under the text tree, excluding removed subtrees."""
    excluded_paths = {
        os.path.normpath(path)
        for path in (excluded_paths or [])
    }
    total = 0
    for root, dirs, files in os.walk(base_dir):
        root_norm = os.path.normpath(root)
        dirs[:] = [
            d for d in dirs
            if os.path.normpath(os.path.join(root, d)) not in excluded_paths
        ]
        if root_norm in excluded_paths:
            dirs[:] = []
            continue
        for name in files:
            if name.endswith(".htm"):
                total += 1
    return total


def print_grouped_xml_skips(skipped_details):
    """Print skipped XML files grouped under shared reason headers."""
    grouped = {}
    for xml_name, category, detail in skipped_details:
        grouped.setdefault(category, []).append((xml_name, detail))

    print("XML skipped detail:")
    for category in sorted(grouped):
        print(category)
        for xml_name, detail in grouped[category]:
            if detail:
                print(f"  {xml_name}: {detail}")
            else:
                print(f"  {xml_name}")


def rename_files(base_dir, tei_dir, subdirs, dry_run):
    """Rename .htm files to match their TEI XML filename."""
    subdir_set = set(subdirs)
    renamed = 0
    xml_skipped = []

    for xml_name in sorted(os.listdir(tei_dir)):
        if not xml_name.endswith(".xml"):
            continue

        xml_path = os.path.join(tei_dir, xml_name)
        new_stem = xml_name[:-4]  # strip .xml

        htm_ref = extract_htm_ref(xml_path)
        if htm_ref is None:
            xml_skipped.append((xml_name, "no valid <ref> in notesStmt", None))
            continue

        htm_rel = resolve_htm_rel(htm_ref, base_dir)
        if htm_rel is None:
            xml_skipped.append((xml_name, "stated source in <notesStmt> not found", htm_ref))
            continue

        # Check the top-level subdir is present
        top_dir = htm_rel.split("/")[0]
        if top_dir not in subdir_set:
            xml_skipped.append((xml_name, "top-level subdir absent", top_dir))
            continue

        htm_path = os.path.join(base_dir, htm_rel)
        htm_dir = os.path.dirname(htm_path)
        new_htm = os.path.join(htm_dir, new_stem + ".htm")

        # Rename .htm
        if not dry_run:
            shutil.move(htm_path, new_htm)

        # Update the <ref target> in the XML
        update_xml_ref(xml_path, htm_ref, new_stem, dry_run)

        renamed += 1

    return {
        "xml_renamed": renamed,
        "xml_skipped": len(xml_skipped),
        "xml_skipped_details": xml_skipped,
    }


def update_xml_ref(xml_path, old_htm_ref, new_stem, dry_run):
    """Update the <ref target> URL in the XML to use the new filename."""
    with open(xml_path, "r", errors="replace") as f:
        content = f.read()

    old_basename = os.path.basename(old_htm_ref)
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
        if not dry_run:
            with open(xml_path, "w") as f:
                f.write(new_content)


def main():
    args = parse_args()
    base_dir, tei_dir = detect_layout()
    subdirs = find_text_subdirs(base_dir)

    csx_files = find_csx_files(base_dir, subdirs)
    c_stats = verify_and_delete_csx(csx_files, args.dry_run)
    re_files = find_re_files(base_dir, subdirs)
    r_stats = verify_and_delete_re(re_files, args.dry_run)
    mbh_stats = cleanup_mbh_artifacts(args.dry_run)

    run_stats = rename_files(base_dir, tei_dir, subdirs, args.dry_run)
    excluded_paths = []
    if mbh_stats["sas_deleted"]:
        excluded_paths.append(mbh_stats["sas_path"])
    htm_remaining = count_htm_files(base_dir, excluded_paths=excluded_paths)

    print(
        "Summary:\n"
        f".htm remaining: {htm_remaining}\n"
        f"*c.txt total {c_stats['total']}, deleted {c_stats['deleted']} (found ‡=ā), not deleted {c_stats['kept']}\n"
        f"*r.txt total {r_stats['total']}, deleted {r_stats['deleted']} (found √=ā), not deleted {r_stats['kept']}\n"
        f"MBH cleanup: mbh1-18*.zip found {mbh_stats['zip_found']}, deleted {mbh_stats['zip_deleted']}; sas entries deleted {mbh_stats['sas_deleted']}, missing {mbh_stats['sas_missing']}\n"
        f"XML processed {run_stats['xml_renamed']}, skipped {run_stats['xml_skipped']}"
    )

    if run_stats["xml_skipped_details"]:
        print_grouped_xml_skips(run_stats["xml_skipped_details"])


if __name__ == "__main__":
    main()
