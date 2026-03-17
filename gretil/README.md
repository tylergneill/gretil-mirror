# GRETIL Sanskrit Corpus — Structure and Cleanup

## What is GRETIL?

[GRETIL](http://gretil.sub.uni-goettingen.de/) (Göttingen Register of Electronic Texts in Indian Languages) is a large collection of machine-readable South Asian texts. This document concerns the Sanskrit portion, which has two historical layers, detailed below.

### 1. The legacy HTM files (~1700 files)

The older layer consists of `.htm` files organized into categorical subdirectories:

```
1_sanskr/
  1_veda/
  2_epic/
  3_purana/
  4_rellit/
  5_poetry/
  6_sastra/
  7_fromindonesia/
```

These files use a cryptic 8-character naming convention (e.g. `aitupsbu.htm`) and come in up to three variants per text:

- `*u.htm` — Unicode (UTF-8) version
- `*c.txt` — CSX (legacy encoding) version
- `*r.txt` — Ronald Emmerick romanization

This layer includes everything that was ever contributed: multiple editions of the same work, versions with/without commentary, metrical markup variants, partial files, pada indexes, and so on. Many of these are duplicates or fragments that were never meant to be a curated collection.

### 2. The TEI XML files (~800 files)

The newer layer consists of TEI-conformant XML files with descriptive filenames (e.g. `sa_aitareyopaniSad-comm.xml`). Each XML file's `<notesStmt>` records which legacy `.htm` file it was converted from. These files were also back-transformed into clean `.htm` renderings (as well as plaintext `.txt` versions) stored in a `transformations/` subfolder.

This is the curated core of the collection. Not every legacy file was converted — only those selected for the main [GRETIL page](http://gretil.sub.uni-goettingen.de/gretil.htm). The curated set still includes intentional duplications (e.g. a text with and without commentary), but excludes the fragments, indexes, and miscellaneous variants from the legacy layer.

## Where the files live (two different layouts)

### "Download All Sanskrit Texts" zip (what most users have)

When you click "Download All Sanskrit Texts" on the GRETIL page, the resulting archive has this structure:

```
1_sanskr/
  1_veda/          ← legacy .htm files
  2_epic/          ← legacy .htm files
  ...
  tei/             ← ~802 TEI XML files
    transformations/
      html/        ← ~801 .htm back-transformations
      plaintext/   ← ~800 .txt back-transformations
```

Both layers are mixed together under `1_sanskr/`, which is why users encounter them side-by-side without realizing they are different things.

### This repository (gretil-mirror)

```
gretil/
  1_sanskr/        ← legacy .htm files (Sanskrit only)
  2_pali/          ← legacy .htm files (Pali)
  ...
  corpustei/       ← TEI XML files (all languages, ~785 in this mirror)
    transformations/
      html/
      plaintext/
```

The TEI files live in a sibling `corpustei/` directory rather than inside `1_sanskr/tei/`. File counts may differ slightly from the zip download.

## What `clean_corpus.py` does

The script bridges the two layers by renaming the legacy files to match their TEI XML counterparts, making it easy to identify which legacy files have curated equivalents.

Specifically, it:

1. **Deletes redundant CSX files** (`*c.txt`) after verifying each has a corresponding Unicode `.htm`.
2. **Renames legacy `.htm` and `.txt` files** to match the TEI XML filename stem. For example, if `sa_aitareyopaniSad-comm.xml` references `aitupsbu.htm`, the script renames `aitupsbu.htm` to `sa_aitareyopaniSad-comm.htm`.
3. **Updates the `<ref target>` in each XML** to point to the new filename.

After running the script, any files that were *not* renamed are legacy-only — they have no TEI equivalent and were not part of the curated collection.

### Usage

```bash
# Preview what would happen (no files changed):
python clean_corpus.py --dry-run

# Run for real, keeping both .htm and .txt:
python clean_corpus.py

# Keep only .htm files (delete .txt after renaming):
python clean_corpus.py --keep htm
```

The script auto-detects whether it's running in the zip layout (`1_sanskr/tei/`) or the repo layout (`corpustei/`).
