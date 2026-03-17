# Tyler's GRETIL mirror

See: https://en.wikipedia.org/wiki/GRETIL

I made this mirror because I believe people are going to continue using GRETIL by downloading files from the main website for as long as they can,
and because I think some clarification is needed regarding this data that people are using. 

# Overview of other versions of GRETIL

GRETIL officially announced that the collection was archived on 21 July 2025
[INDOLOGY list post](https://list.indology.info/pipermail/indology/2025-July/060853.html).

There are numerous versions of GRETIL on the public web at this point (March 2026):
- the [main website](http://gretil.sub.uni-goettingen.de/) is still up
- M. Mehner's official [TEI repo on GitHub](https://github.com/mmehner/gretil-corpus-tei) contains an important subset of the data (see below for details)
- the official project archive is on [TextGrid](https://textgridrep.org/project/TGPR-2ba9cb1b-9602-202d-71ce-67e63a29de55)
  - this includes XML improvements
- D. Wujastyk has a [mirror repo on GitHub](https://github.com/INDOLOGY/GRETIL-mirror) with a `GRETIL-refresh` update script that scrapes key files directly from the above using `wget` 
- C. Teodorescu has a [searchable version](https://claudius-teodorescu.gitlab.io/gretil-corpus-site/) which runs via [two repos on GitLab](https://gitlab.com/search?search=claudius%20teodorescu%20gretil&nav_source=navbar)
  - this includes **independent** XML improvements 
  - ostensibly related is [this additional mirror on GitHub](https://github.com/sanskrit-texts/gretil-corpus), but I'm not clear on details
- A. Prasad (creator of Ambuda) has a [copy on GitHub with ad-hoc changes](https://github.com/ambuda-org/gretil)  
- O. Hellwig (creator of DCS) also has a [copy on GitHub with systematic cleanup](https://github.com/OliverHellwig/sanskrit/tree/master/corpus/GRETIL) for NLP purposes 

There is **no official, public Git repo for the entire GRETIL site**.

# This repo

Like D. Wujastyk's, this mirror repo was also scraped from the main site, but in a slightly more comprehensive fashion, also including .zip archives, a few .pdf files. It then makes the following changes:
- some technical changes to get the site to work as expected (see commit history for details)
  - links to the full original domain were modified to stay within the mirror
  - adjusted CSS filename
  - etc.
- the large `1_sanskr.zip` file was removed and offloaded as a GitHub Release artifact to respect standard Git filesize limits (other .zip archives were small enough to retain without issue)
- a working version of the mirror has been [deployed with GitHub Pages](https://tylergneill.github.io/gretil-mirror/gretil.html) 
- this README has been added as a research document attempting to make sense of the various versions
- a `cleanup.py` script has been added to allow users to create a more useful local version for searching (thanks to Alex Watson for the idea!)

# Historical layers of GRETIL's Sanskrit collection

(NB: I haven't explored the non-Sanskrit parts of the collection.)

It's helpful to think in terms of **four (4)** distinct layers here:

## 1. The legacy HTM structure (~1,390 files)

This layer, which can be unearthed during a direct scrape of the site,
consists of `.htm` files organized into categorical subdirectories:

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

These files use a cryptic naming convention, 
most frequently 8 characters long before the file extension, e.g., `aitupsbu.htm`.

In my reading, THIS is the most broadly valuable layer of the project, for reasons I'll detail below.

## 2a. The TEI layer (~800 files)

This is the more highly curated portion of the collection.

Starting in 2017, M. Mehner converted select `.htm` files (about 800 out of 1,390) to TEI-conformant XML.
The curated set still includes some intentional duplications (e.g. a text with and without commentary),
but it generally excludes fragments, indexes, and miscellaneous variants from the legacy layer.
See his [TEI repo on GitHub](https://github.com/mmehner/gretil-corpus-tei).
Further technical TEI improvements for this set happened for the official project archive on [TextGrid](https://textgridrep.org/project/TGPR-2ba9cb1b-9602-202d-71ce-67e63a29de55).

A notable difference about these files is that they have descriptive filenames,
e.g. `sa_aitareyopaniSad-comm.xml`.
With few exceptions, each XML file's `<notesStmt>` records which legacy `.htm` file it was converted from.

In turn, these `.xml` files were then back-transformed into `.htm` renderings 
(as well as plaintext `.txt` versions), which are stored in the `transformations/` subfolder.
In actual substance, the resulting `.htm` files differ little from the legacy originals.

All of these TEI-tier items are displayed on the [GRETIL website main page](http://gretil.sub.uni-goettingen.de/gretil.htm). 
In the site structure discovered through scraping, they are found under `1_sanskr/corpustei`.

## 2b. The main-page non-TEI supplement (~...files)

There are also a few items which are displayed on the GRETIL website main page but which were NOT converted to TEI:
- Mahābhārata
- Śatapatha-Brāhmaṇa
- ...

This ostensibly has something to do with the size of these items and their being imported from other platforms. 

## 3. The 1_sanskr.zip snapshot (~1,390 files + TEI)

On the GRETIL website main page, under "Cumulative Download", users can download .zip archives with a single click.
Given the simplicity of this download method, this version is probably the one on most people's computers.
The .zip archive on TextGrid is identical to this one.

Surprisingly, comparison shows that this version is NOT an up-to-date representation of the legacy HTM structure.
Numerous cases of miscategorization occur in the .zip archive which are fixed in the legacy HTM subdirectory structure,
e.g., Utpaladeva's Ajaḍapramātṛsiddhi, 
classified wrongly in the .zip archive as Vaiṣṇava religious literature (4_rellit/vaisn/utajp_pu.htm) 
and more correctly in the HTM structure as Śaiva philosophical śāstra (6_sastra/3_phil/saiva/utajp_pu.htm).

(Related note: The TEI items are presented in one flat layer, with no subdirectory categorization.)

However, the frozen .zip file also contains a few things NOT found in the legacy HTM structure:
- mbh1-18u.htm (single-file Mahābhārata) 
- mrgt3miu (Mṛgendrāgama Caryapāda, "pada index" file)
- bahcar5_au and -_pu () (individual files for Ucchvāsa 5 of Bāṇa Harṣacarita)
- ...(possibly more)

AND the .zip file contains the entire TEI layer, where it is named `1_sanskr/tei` (NOT `corpustei`).

For these reasons, this mirror maintains a `legacy_1_sanskr` archive as well as an `updated_1_sanskr` achive.
The files uniquely found in the frozen zip file (e.g., mrgt3miu) have been re-inserted into the HTM structure,
and this structure has been newly zipped to produce `updated_1_sanskr`.

## 4. Legacy cruft (~3,700 files)

This layer, which is revealed by fuller scraping of the main site,
is generally not useful but is worth mentioning just in case it can cause confusion.

It contains:
- `*c.txt` (927 files) and `*r.txt` (711) variants for many (but not all!) legacy `.htm` files, containing CSX and Ronald Emmerick transliteration, respectively 
- a full prototype of H. Ruelius' "The Mahabharata Online" under 1_sanskr/2_epic/mbh/sas (2,060 files)

## Layer overview and summation

1. Legacy HTM structure (~1,390 files)
2. Main page TEI + non-TEI (~800 + 50 files)
3. TEI transformations (~1,600 files)
4. Cruft (~3,700 files)

Total
7,540 (adding above)
or
8,450 (Finder)


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
