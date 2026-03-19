# Tyler's GRETIL mirror

This mirror is live [on GitHub Pages](https://tylergneill.github.io/gretil-mirror/gretil.html).

For quick project context, see [GRETIL's Wikipedia page](https://en.wikipedia.org/wiki/GRETIL).

In this entire README, I'm only talking about Sanskrit.

# Official versions of GRETIL 

There are no fewer than three:

1. Cumulative Download — This `.zip` archive is a snapshot frozen in time, containing `.htm` (~1,325) and `.xml` files (~800)
2. Main Site Server File Structure — With simple tools (e.g. Dominik's `wget` script), one can discover the underlying file structure on the server behind the public GRETIL website. This appears to represent a later development 
3. Official Archive on TextGrid — The individual XML files 
4. This file/folder  
3. It's relatively easy to scrape a website to find its underlying structure.

There are actually three distinct forms of the GRETIL collection available to the public 

The final archiving of GRETIL was officially announced on 21 July 2025:
[INDOLOGY list post](https://list.indology.info/pipermail/indology/2025-July/060853.html).
As of today (March 2026), the [main website](http://gretil.sub.uni-goettingen.de/) is still up,
and people still seem to be using the collection,
often in the form of the cumulative download on their personal computers. 
This cumulative download includes not only TEI-XML files
(which the GRETIL team has been urging people to treat as authoritative for the last few years) 
but also the HTML files which preceded them.
The [official project archive on TextGrid](https://textgridrep.org/project/TGPR-2ba9cb1b-9602-202d-71ce-67e63a29de55) 
also includes an exact copy of this cumulative download, plus an improved set of the TEI XML files. 

To put a finer point on even the official situation, 

I made this working mirror to maintain continuity of this valuable resource in case the main site goes down
and people are not yet comfortable using the TextGrid archive,
and because I think the collection warrants some clarification.  

# Overview of other versions of GRETIL

Besides the [main website](http://gretil.sub.uni-goettingen.de/) which is still up, there are numerous other versions of GRETIL on the public web, many through GitHub:
- M. Mehner's official [TEI repo on GitHub](https://github.com/mmehner/gretil-corpus-tei) (+ [forks](https://github.com/mmehner/gretil-corpus-tei/forks?include=active%2Cinactive&page=1&period=)) contains an important subset of the data (see below for details), but I believe this is **out of date**
- the official project archive is on [TextGrid](https://textgridrep.org/project/TGPR-2ba9cb1b-9602-202d-71ce-67e63a29de55), and it includes quasi-official **improvements** to the TEI XML
- D. Wujastyk has a [mirror repo on GitHub](https://github.com/INDOLOGY/GRETIL-mirror) (+ [forks](https://github.com/INDOLOGY/GRETIL-mirror/forks?include=active%2Cinactive%2Cnetwork&page=1&period=&)) with a script that scrapes key files directly from the main site using `wget`
- C. Teodorescu has a [searchable version](https://claudius-teodorescu.gitlab.io/gretil-corpus-site/) which runs via [two repos on GitLab](https://gitlab.com/search?search=claudius%20teodorescu%20gretil&nav_source=navbar)
  - this includes **independent** XML improvements 
  - I'm not sure how this relates to [this additional mirror of his on GitHub](https://github.com/sanskrit-texts/gretil-corpus)
- A. Prasad (creator of Ambuda) has a [copy on GitHub with ad-hoc changes](https://github.com/ambuda-org/gretil) (+ [forks](https://github.com/ambuda-org/gretil/forks?include=active&page=1&period=))
- O. Hellwig (creator of DCS) added a copy with **systematic cleanup for NLP purposes** to [his larger sanskrit repo on GitHub](https://github.com/OliverHellwig/sanskrit/tree/master/corpus/GRETIL) (see [recent forks](https://github.com/OliverHellwig/sanskrit/forks?include=active%2Cinactive&page=1&period=1y)) 

There is **no official, public Git repo for the entire GRETIL site**.

# This repo

Like D. Wujastyk's, this mirror repo was also scraped from the main site, 
but in a slightly more comprehensive fashion, 
e.g. also including .zip archives and a few .pdf files.

It then makes the following further changes:
- some technical changes to get the site to work as expected when deployed with GitHub Pages (see commit history for details)
  - links to the full original domain were modified to stay within the mirror
  - adjusted CSS filename
  - etc.
- the large `1_sanskr.zip` file was removed and offloaded as a GitHub Release artifact to respect standard Git filesize limits (other .zip archives were small enough to retain without issue)
- this README has been added as a research document attempting to make sense of the various versions
- a `cleanup.py` script has been added to allow users to create a more useful local version for searching (thanks to Alex Watson for the idea!)

Last but not least, it's deployed [live on GitHub Pages](https://tylergneill.github.io/gretil-mirror/gretil.html). 

# Historical layers of GRETIL's Sanskrit collection

GRETIL's Sanskrit collection has **four (4)** distinct layers, with sublayers.

## 1a. The source categorical structure, primary .htm only (~1,325 files)

This layer, which can be unearthed during a direct scrape of the site,
consists of `.htm` files organized into categorical subdirectories:

```
1_sanskr/
  1_veda/
    1_sam/
      1_rv/
    2_bra/
      satapath/
    3_ara/
    ...
  2_epic/
    mbh/
    ramayana/
  3_purana/
    ...
  4_rellit/
    buddh/
    jaina/
    ...
  5_poetry/
    1_alam/
    1_chandas/
    ...
  6_sastra/
    1_gram/
    2_lex/
    3_phil/
      advaita/
      buddh/
      ...
    4_dharma/
    ...
  7_fromindonesia/
```

This structure should be familiar to anyone who has used either the navbar on the main site or the cumulative download.

The `.htm` files in these folders use a cryptic naming convention, 
most frequently 8 characters long before the file extension, e.g., `aitupsbu.htm`.

In the filename `aitupsbu.htm` above, the final `u` indicates "Unicode", i.e., IAST transliteration.
(There are also `.txt` files ending in `c` for "CSX" and `r` for "Ronald E. Emmerick", respectively,
for more on which, see section 1c below.)

There are other conventions, too, like `a` for "analytic", `i` for "index", `p` for "plaintext", etc.,
but these are used less consistently.

## 1b. The "SAS MBh" .htm (~2,060 files)

SAS is the name of a programming language, which Hans Ruelius used to create "The Mahabharata Online".
A prototype of this project is hosted by GRETIL, 
which the scrape also discovers and locates at `1_sanskr/2_epic/mbh/sas`.
This is not useful for most people.

## 1c. The CSX and RE .txt legacy transliteration files .txt (~2,640 files)

As alluded to above, GRETIL once relied more on legacy ASCII-based Romanizations instead of Unicode IAST.
The scrape reveals `.txt` files with suffixes `c` and `r` (CSX, Ronald E. Emmerick, respectively).
These are just clutter at this point.

## 2a. The TEI layer (~800 files)

This is the more highly curated portion of the collection.

Starting in 2017, M. Mehner converted select `.htm` files (about 785 out of ~1,325) to TEI-conformant XML.
The curated set still includes some intentional duplications (e.g. a text with and without commentary),
but it generally excludes the fragments, indexes, and miscellaneous other variants from the legacy layer.
See his [TEI repo on GitHub](https://github.com/mmehner/gretil-corpus-tei).
Further technical TEI improvements for this set happened for the official project archive on [TextGrid](https://textgridrep.org/project/TGPR-2ba9cb1b-9602-202d-71ce-67e63a29de55),
and C. Teodorescu also carried out his own,  (see Overview above).

A notable difference about these `.xml` files is that they have descriptive filenames,
e.g. `sa_aitareyopaniSad-comm.xml`.
With few exceptions, each XML file's `<notesStmt>` element records which legacy `.htm` file it was converted from.

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

## 3. The 1_sanskr.zip snapshot (~1,325 files + TEI)

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

1. Legacy HTM structure (~1,325 files)
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
