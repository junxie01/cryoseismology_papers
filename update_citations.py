#!/usr/bin/env python3
"""
Fetch papers that cited the user's publications.

Strategy (in order, results merged and deduplicated):
  1. OpenCitations COCI API  — confirmed citation index (may lag ~weeks)
  2. Crossref journal scan   — scan ALL recent papers from key seismo journals,
                               check each reference list for our fingerprints
                               (catches papers immediately after deposit)
  3. scholarly (fallback)    — Google Scholar "Cited by" list
"""

import json
import os
import time
import urllib.parse
import requests
from datetime import datetime, timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ── proxy bypass ────────────────────────────────────────────────────────────
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

session = requests.Session()
session.trust_env = False
_retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=_retry))
session.mount('http://', HTTPAdapter(max_retries=_retry))

OUTPUT_FILE = 'data_citations.json'

# ── your publications ────────────────────────────────────────────────────────
# Add all your papers here.  fingerprints = distinctive text snippets that
# appear literally in citation records (journal article ID, short title, etc.)
MY_PAPERS = [
    # ── 2010 ──────────────────────────────────────────────────────────────
    {
        'title': 'The M5.0 Suining-Tongnan (China) earthquake of 31 January 2010: A destructive earthquake occurring in sedimentary cover',
        'doi': '10.1007/s11434-010-4276-2',
        'fingerprints': ['10.1007/s11434-010-4276-2', 's11434-010-4276', 'Suining-Tongnan'],
    },
    {
        'title': 'Comparison of ground truth location of earthquake from InSAR and from ambient seismic noise: A case study of the 1998 Zhangbei earthquake',
        'doi': '10.1007/s11589-010-0788-5',
        'fingerprints': ['10.1007/s11589-010-0788-5', 's11589-010-0788', 'Zhangbei earthquake'],
    },
    {
        'title': 'Effects of sedimentary layer on earthquake source modelling from geodetic inversion',
        'doi': '10.1007/s11589-010-0786-7',
        'fingerprints': ['10.1007/s11589-010-0786-7', 's11589-010-0786'],
    },
    # ── 2014 ──────────────────────────────────────────────────────────────
    {
        'title': 'Validating Accuracy of Rayleigh Wave Dispersion Extracted from Ambient Seismic Noise via Comparison with Data from a Ground-Truth Earthquake',
        'doi': '10.1785/0120130279',
        'fingerprints': ['10.1785/0120130279', '0120130279'],
    },
    {
        'title': 'Ground Truth Location of Earthquakes by Use of Ambient Seismic Noise From a Sparse Seismic Network: A Case Study in Western Australia',
        'doi': '10.1007/s00024-014-0993-6',
        'fingerprints': ['10.1007/s00024-014-0993-6', 's00024-014-0993', 'Western Australia'],
    },
    # ── 2015 ──────────────────────────────────────────────────────────────
    {
        'title': 'Synchronizing Intercontinental Seismic Networks Using the 26 s Persistent Localized Microseismic Source',
        'doi': '10.1785/0120140252',
        'fingerprints': ['10.1785/0120140252', '0120140252', '26 s persistent localized microseismic'],
    },
    {
        'title': 'Measurement of Rayleigh wave ellipticity and its application to the joint inversion of high-resolution S-wave velocity structure beneath northeast China',
        'doi': '10.1002/2015jb012459',
        'fingerprints': ['10.1002/2015jb012459', '2015jb012459'],
    },
    # ── 2016 ──────────────────────────────────────────────────────────────
    {
        'title': 'On the accuracy of long-period Rayleigh waves extracted from ambient noise',
        'doi': '10.1093/gji/ggw137',
        'fingerprints': ['10.1093/gji/ggw137', 'gji/ggw137'],
    },
    {
        'title': 'An investigation of time-frequency domain phase-weighted stacking and its application to phase-velocity extraction from ambient noise empirical Green\'s functions',
        'doi': '10.1093/gji/ggx448',
        'fingerprints': ['10.1093/gji/ggx448', 'gji/ggx448', 'phase-weighted stacking'],
    },
    # ── 2017 ──────────────────────────────────────────────────────────────
    {
        'title': 'Broad-band Rayleigh wave phase velocity maps (10-150 s) across the United States from ambient noise data',
        'doi': '10.1093/gji/ggw460',
        'fingerprints': ['10.1093/gji/ggw460', 'gji/ggw460'],
    },
    # ── 2018 ──────────────────────────────────────────────────────────────
    {
        'title': 'Assessing the short-term clock drift of early broadband stations with burst events of the 26 s persistent and localized microseism',
        'doi': '10.1093/gji/ggx401',
        'fingerprints': ['10.1093/gji/ggx401', 'gji/ggx401', 'clock drift', '26 s persistent'],
    },
    {
        'title': 'Nonlinear inversion of resistivity sounding data for 1-D earth models using the Neighbourhood Algorithm',
        'doi': '10.1016/j.jafrearsci.2017.09.003',
        'fingerprints': ['10.1016/j.jafrearsci.2017.09.003', 'jafrearsci.2017.09.003'],
    },
    {
        'title': 'Crust-mantle coupling mechanism in Cameroon, West Africa, revealed by 3D S-wave velocity and azimuthal anisotropy',
        'doi': '10.1016/j.pepi.2017.12.006',
        'fingerprints': ['10.1016/j.pepi.2017.12.006', 'pepi.2017.12.006', 'Cameroon'],
    },
    {
        'title': '3D upper-mantle shear velocity model beneath the contiguous United States based on broadband surface wave from ambient seismic noise',
        'doi': '10.1007/s00024-018-1881-2',
        'fingerprints': ['10.1007/s00024-018-1881-2', 's00024-018-1881'],
    },
    # ── 2019 ──────────────────────────────────────────────────────────────
    {
        'title': 'Imaging 3D upper-mantle structure with autocorrelation of seismic noise recorded on a transportable single station',
        'doi': '10.1785/0220180260',
        'fingerprints': ['10.1785/0220180260', '0220180260'],
    },
    {
        'title': 'Further constraints on the shear wave velocity structure of Cameroon from joint inversion of receiver function, Rayleigh wave dispersion and ellipticity measurements',
        'doi': '10.1093/gji/ggz008',
        'fingerprints': ['10.1093/gji/ggz008', 'gji/ggz008'],
    },
    {
        'title': 'Millimeter-level ultra-long period multiple Earth-circling surface waves retrieved from dense high-rate GPS network',
        'doi': '10.1016/j.epsl.2019.07.007',
        'fingerprints': ['10.1016/j.epsl.2019.07.007', 'epsl.2019.07.007', 'earth-circling surface waves'],
    },
    # ── 2020 ──────────────────────────────────────────────────────────────
    {
        'title': 'Enhancing Signal-to-Noise Ratios of High-Frequency Rayleigh Waves Extracted from Ambient Seismic Noises in Topographic Region',
        'doi': '10.1785/0120190177',
        'fingerprints': ['10.1785/0120190177', '0120190177'],
    },
    {
        'title': 'Relocation of the June 17th, 2017 Nuugaatsiaq (Greenland) landslide based on Green\'s functions from ambient seismic noise',
        'doi': '10.1029/2019jb018947',
        'fingerprints': ['10.1029/2019jb018947', '2019jb018947', 'Nuugaatsiaq'],
    },
    {
        'title': 'Validity of Resolving the 785 km Discontinuity in the Lower Mantle with P\'P\' Precursors',
        'doi': '10.1785/0220200210',
        'fingerprints': ['10.1785/0220200210', '0220200210', '785 km discontinuity'],
    },
    {
        'title': 'Coseismic Slip Distribution of the 24 January 2020 Mw 6.7 Doganyol Earthquake and in Relation to the Foreshock and Aftershock Activities',
        'doi': '10.1785/0220200152',
        'fingerprints': ['10.1785/0220200152', '0220200152', 'Doganyol'],
    },
    {
        'title': 'Crust and upper mantle structure of the South China Sea and adjacent areas from the joint inversion of ambient noise and earthquake surface wave dispersions',
        'doi': '10.1029/2020gc009356',
        'fingerprints': ['10.1029/2020gc009356', '2020gc009356'],
    },
    # ── 2021 ──────────────────────────────────────────────────────────────
    {
        'title': 'Evaluating global tomography models with antipodal ambient noise cross correlation functions',
        'doi': '10.1029/2020jb020444',
        'fingerprints': ['10.1029/2020jb020444', '2020jb020444', 'antipodal ambient noise'],
    },
    {
        'title': 'Sedimentary structure of the Sichuan Basin derived from seismic ambient noise tomography',
        'doi': '10.1093/gji/ggaa578',
        'fingerprints': ['10.1093/gji/ggaa578', 'gji/ggaa578', 'Sichuan Basin'],
    },
    {
        'title': 'Sensing shallow structure and traffic noise with fiber-optic internet cables in an urban area',
        'doi': '10.1007/s10712-021-09678-w',
        'fingerprints': ['10.1007/s10712-021-09678-w', 's10712-021-09678', 'fiber-optic internet cables'],
    },
    # ── 2022 ──────────────────────────────────────────────────────────────
    {
        'title': 'Generation mechanism of the 26 s and 28 s tremors in the Gulf of Guinea from statistical analysis of magnitudes and event intervals',
        'doi': '10.1016/j.epsl.2021.117334',
        'fingerprints': [
            '10.1016/j.epsl.2021.117334',
            'j.epsl.2021.117334',
            '26 s and 28 s tremors in the gulf',
            '26 s and 28 s tremors of the gulf',
            'epsl.2021.117334',
        ],
    },
    {
        'title': 'ADE-Net: A deep neural network for DAS earthquake detection trained with a limited number of positive samples',
        'doi': '10.1109/tgrs.2022.3143120',
        'fingerprints': ['10.1109/tgrs.2022.3143120', 'tgrs.2022.3143120', 'ADE-Net'],
    },
    {
        'title': 'Crustal structure in the Weiyuan shale gas field, China, and its tectonic implications',
        'doi': '10.1016/j.tecto.2022.229449',
        'fingerprints': ['10.1016/j.tecto.2022.229449', 'tecto.2022.229449', 'Weiyuan'],
    },
    # ── 2023 ──────────────────────────────────────────────────────────────
    {
        'title': 'Seismometer orientation correction via teleseismic receiver function measurements in West Africa and adjacent Islands',
        'doi': '10.1785/0220220316',
        'fingerprints': ['10.1785/0220220316', '0220220316'],
    },
    {
        'title': 'Topography effect on ambient noise tomography: a case study for the Longmen Shan area, eastern Tibetan Plateau',
        'doi': '10.1093/gji/ggac435',
        'fingerprints': ['10.1093/gji/ggac435', 'gji/ggac435', 'Longmen Shan'],
    },
    # ── 2024 ──────────────────────────────────────────────────────────────
    {
        'title': 'Ice plate deformation and cracking revealed by an in situ-distributed acoustic sensing array',
        'doi': '10.5194/tc-18-837-2024',
        'fingerprints': ['10.5194/tc-18-837-2024', 'tc-18-837', 'ice plate deformation'],
    },
    {
        'title': 'Near real-time in situ monitoring of nearshore ocean currents using distributed acoustic sensing on submarine fiber-optic cable',
        'doi': '10.1029/2024ea003572',
        'fingerprints': ['10.1029/2024ea003572', '2024ea003572', 'nearshore ocean currents'],
    },
    # ── 2025 ──────────────────────────────────────────────────────────────
    {
        'title': 'Seismotectonics of Ghana and adjacent regions in western Africa: a review',
        'doi': '10.1016/j.eqrea.2025.100442',
        'fingerprints': ['10.1016/j.eqrea.2025.100442', 'eqrea.2025.100442', 'Ghana'],
    },
    {
        'title': 'Complex seismogenic fault system for the 2022 Ms6.0 Maerkang (China) earthquake sequence resolved with reliable seismic source parameters',
        'doi': '10.1016/j.tecto.2025.230718',
        'fingerprints': ['10.1016/j.tecto.2025.230718', 'tecto.2025.230718', 'Maerkang'],
    },
    {
        'title': 'High resolution shallow structure of Ebao basin revealed with DAS ambient noise tomography and its relation to earthquake ground motion',
        'doi': '10.1029/2024jb029874',
        'fingerprints': ['10.1029/2024jb029874', '2024jb029874', 'Ebao basin'],
    },
    # ── 2026 ──────────────────────────────────────────────────────────────
    {
        'title': 'Fault Intersections Control the Extremely Shallow 2020 Mw 5.1 Sparta, North Carolina, Earthquake Sequence',
        'doi': '10.1785/0220250313',
        'fingerprints': ['10.1785/0220250313', '0220250313', 'Sparta', 'North Carolina'],
    },
]

# Seismology journals for Crossref fallback scan
SEISMO_JOURNALS = [
    'Nature', 'Science', 'Nature Geoscience', 'Nature Communications',
    'Science Advances', 'Geophysical Research Letters',
    'Journal of Geophysical Research: Solid Earth',
    'Earth and Planetary Science Letters', 'Geophysical Journal International',
    'Seismological Research Letters',
    'Bulletin of the Seismological Society of America',
    'Journal of Seismology', 'Tectonophysics', 'Solid Earth',
    'Communications Earth & Environment', 'The Cryosphere',
    'Earth and Space Science', 'Earthquake Research Advances',
]

SCAN_DAYS = 7  # past week


# ── date helpers ──────────────────────────────────────────────────────────────

def _parse_date(s: str) -> datetime:
    """Parse YYYY-MM-DD or YYYY-MM or YYYY into a datetime."""
    if not s:
        return datetime.min
    for fmt in ('%Y-%m-%d', '%Y-%m', '%Y'):
        try:
            return datetime.strptime(s[:len(fmt)], fmt)
        except ValueError:
            continue
    return datetime.min


def _in_window(published: str, since: datetime) -> bool:
    """Return True if the publication date is within the scan window."""
    d = _parse_date(published)
    if d == datetime.min:
        return False  # unknown date → skip
    return d >= since


# ── Semantic Scholar ───────────────────────────────────────────────────────────

def _s2_entry(cp: dict, paper: dict) -> dict:
    authors = cp.get('authors', [])
    first = authors[0].get('name', 'N/A') if authors else 'N/A'
    corr  = authors[-1].get('name', 'N/A') if len(authors) > 1 else first
    ext   = cp.get('externalIds') or {}
    doi   = ext.get('DOI', '') or ''
    url   = f'https://doi.org/{doi}' if doi else ''
    pub   = cp.get('publicationDate', '') or str(cp.get('year', ''))
    journal = cp.get('journal') or {}
    source  = cp.get('venue') or (journal.get('name', 'Unknown') if isinstance(journal, dict) else 'Unknown')
    return {
        'id':           doi or cp.get('paperId', ''),
        'title':        cp.get('title', 'No Title'),
        'url':          url,
        'first_author': first,
        'corr_author':  corr,
        'affiliation':  'N/A',
        'abs_zh':       f'This paper cited: {paper["title"]}',
        'source':       source,
        'published':    pub,
        'cited_paper':  paper['title'],
    }


def fetch_semantic_scholar(paper: dict, since: datetime) -> list:
    """Get papers that cite `paper` and were published within the scan window."""
    results = []
    doi = paper.get('doi', '')
    if not doi:
        return results

    fields = 'title,authors,year,publicationDate,externalIds,venue,journal'
    base   = f'https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}/citations'
    offset = 0
    limit  = 500

    while True:
        url = f'{base}?fields={fields}&limit={limit}&offset={offset}'
        try:
            r = session.get(url, timeout=30, headers={'User-Agent': 'paper-weekly-bot/1.0'})
            if r.status_code == 404:
                break
            if r.status_code == 429:
                time.sleep(15)
                continue
            data = r.json()
        except Exception as e:
            print(f'  [S2] Error for {doi}: {e}')
            break

        items = data.get('data', [])
        found_in_page = 0
        for item in items:
            cp = item.get('citingPaper', {})
            if not cp:
                continue
            pub = cp.get('publicationDate', '') or str(cp.get('year', ''))
            if _in_window(pub, since):
                results.append(_s2_entry(cp, paper))
                found_in_page += 1

        # S2 returns newest first — stop early if all items are older than window
        oldest_in_page = ''
        for item in reversed(items):
            cp = item.get('citingPaper', {})
            oldest_in_page = cp.get('publicationDate', '') or str(cp.get('year', ''))
            if oldest_in_page:
                break
        if oldest_in_page and not _in_window(oldest_in_page, since):
            break  # nothing older will be in the window

        next_offset = data.get('next')
        if next_offset is None or len(items) < limit:
            break
        offset = next_offset
        time.sleep(1)

    if results:
        print(f'  [S2] {len(results)} new citation(s) in window for {doi}')
    return results


# ── OpenCitations ─────────────────────────────────────────────────────────────

def fetch_opencitations(paper: dict, since: datetime) -> list:
    """Get citations from OpenCitations that fall within the scan window."""
    results = []
    doi = paper.get('doi', '')
    if not doi:
        return results
    try:
        r = session.get(
            f'https://opencitations.net/index/coci/api/v1/citations/{doi}',
            timeout=20, headers={'Accept': 'application/json'}
        )
        if r.status_code != 200:
            return results
        for cit in r.json():
            creation = cit.get('creation', '')
            if not _in_window(creation, since):
                continue
            citing_doi = cit.get('citing', '')
            if not citing_doi:
                continue
            try:
                meta = session.get(
                    f'https://api.crossref.org/works/{citing_doi}',
                    timeout=15
                ).json().get('message', {})
                if not isinstance(meta, dict):
                    continue
                authors = meta.get('author', [])
                first = (f"{authors[0].get('given','')} {authors[0].get('family','')}".strip()
                         if authors else 'N/A')
                corr  = (f"{authors[-1].get('given','')} {authors[-1].get('family','')}".strip()
                         if len(authors) > 1 else first)
                date_parts = (meta.get('issued') or meta.get('created') or {}).get('date-parts', [['']])
                pub = '-'.join(str(x) for x in (date_parts[0] if date_parts else [])) or creation[:4]
                results.append({
                    'id':           citing_doi,
                    'title':        (meta.get('title') or ['No Title'])[0],
                    'url':          f'https://doi.org/{citing_doi}',
                    'first_author': first,
                    'corr_author':  corr,
                    'affiliation':  'N/A',
                    'abs_zh':       f'This paper cited: {paper["title"]}',
                    'source':       (meta.get('container-title') or ['Unknown'])[0],
                    'published':    pub,
                    'cited_paper':  paper['title'],
                })
                print(f'  [OC] {(meta.get("title") or [""])[0][:65]}')
            except Exception:
                pass
    except Exception as e:
        print(f'  [OC] Error for {doi}: {e}')
    return results


# ── Crossref journal scan (fallback) ─────────────────────────────────────────

def _ref_matches(ref: dict, paper: dict) -> bool:
    """
    Check if a Crossref reference matches our paper.
    Requires DOI match OR multiple specific fingerprints to avoid false positives.
    """
    text = (ref.get('DOI', '') + ' ' +
            ref.get('unstructured', '') + ' ' +
            ref.get('article-title', '')).lower()
    
    doi = paper.get('doi', '').lower()
    fps = [fp.lower() for fp in paper['fingerprints']]
    
    # If DOI matches, it's a definite citation
    if doi and doi in text:
        return True
    
    # Otherwise require at least 2 fingerprint matches (or 1 if it's a long specific phrase)
    match_count = sum(1 for fp in fps if fp in text)
    if match_count >= 2:
        return True
    # Single long fingerprint (>20 chars) is also acceptable
    for fp in fps:
        if len(fp) > 20 and fp in text:
            return True
    return False


def _crossref_entry(item: dict, paper: dict) -> dict:
    authors = item.get('author', [])
    first = (f"{authors[0].get('given','')} {authors[0].get('family','')}".strip()
             if authors else 'N/A')
    corr  = (f"{authors[-1].get('given','')} {authors[-1].get('family','')}".strip()
             if len(authors) > 1 else first)
    doi = item.get('DOI', '')
    dp  = (item.get('issued') or item.get('created') or {}).get('date-parts', [['']])
    pub = '-'.join(str(x) for x in (dp[0] if dp else [])) or ''
    return {
        'id':           doi,
        'title':        (item.get('title') or ['No Title'])[0],
        'url':          f'https://doi.org/{doi}' if doi else '',
        'first_author': first,
        'corr_author':  corr,
        'affiliation':  (authors[0].get('affiliation', [{}])[0].get('name', 'N/A')
                         if authors and authors[0].get('affiliation') else 'N/A'),
        'abs_zh':       f'This paper cited: {paper["title"]}',
        'source':       (item.get('container-title') or ['Unknown'])[0],
        'published':    pub,
        'cited_paper':  paper['title'],
    }


def fetch_crossref_scan(paper: dict, since_dt: datetime) -> list:
    """
    Scan recently indexed papers in key journals and check reference lists.
    Only used as fallback when S2 and OC return nothing.
    Filters results by actual publication date (not index date).
    """
    results = []
    own_doi = paper.get('doi', '').lower()
    since_str = since_dt.strftime('%Y-%m-%d')

    for journal in SEISMO_JOURNALS:
        j_enc  = urllib.parse.quote(journal)
        cursor = '*'
        pages  = 0
        while pages < 2:  # max 200 papers per journal
            url = (f'https://api.crossref.org/works'
                   f'?filter=container-title:{j_enc},type:journal-article,from-index-date:{since_str}'
                   f'&select=DOI,title,author,container-title,issued,created,reference'
                   f'&rows=100&cursor={urllib.parse.quote(cursor)}')
            try:
                resp = session.get(url, timeout=30)
                msg  = resp.json().get('message', {})
                items = msg.get('items', [])
                for item in items:
                    if item.get('DOI', '').lower() == own_doi:
                        continue
                    # Check publication date is within window
                    dp = (item.get('issued') or item.get('created') or {}).get('date-parts', [[]])
                    pub_str = '-'.join(str(x) for x in (dp[0] if dp and dp[0] else []))
                    if not _in_window(pub_str, since_dt):
                        continue
                    refs = item.get('reference', [])
                    if refs and any(_ref_matches(ref, paper) for ref in refs):
                        e = _crossref_entry(item, paper)
                        results.append(e)
                        print(f'  [Crossref] {e["title"][:65]}')
                next_cursor = msg.get('next-cursor', '')
                if not items or not next_cursor or next_cursor == cursor:
                    break
                cursor = next_cursor
                pages += 1
                time.sleep(0.5)
            except Exception as e:
                print(f'  [Crossref] Error scanning {journal}: {e}')
                break
    return results


# ── main ─────────────────────────────────────────────────────────────────────

def fetch_citing_papers():
    now       = datetime.now()
    since_dt  = now - timedelta(days=SCAN_DAYS)
    since_str = since_dt.strftime('%Y-%m-%d')
    all_results = []

    print(f'Scanning for citations published since {since_str}\n')

    for paper in MY_PAPERS:
        print(f'--- {paper["title"][:70]}')

        # 1. Semantic Scholar — primary (fastest, most comprehensive)
        r1 = fetch_semantic_scholar(paper, since_dt)
        all_results.extend(r1)
        time.sleep(1)

        # 2. OpenCitations — supplement (confirmed citation graph)
        r2 = fetch_opencitations(paper, since_dt)
        # Add only if not already found by S2
        s2_ids = {x['id'].lower() for x in r1}
        for x in r2:
            if x['id'].lower() not in s2_ids:
                all_results.append(x)
        time.sleep(0.5)

        # 3. Crossref scan — fallback only when both S2 and OC are empty
        if not r1 and not r2:
            r3 = fetch_crossref_scan(paper, since_dt)
            all_results.extend(r3)
            time.sleep(0.5)

    # Final filter: ensure all results are within the date window
    # (protects against any API returning out-of-window results)
    filtered = []
    for r in all_results:
        pub = r.get('published', '')
        if _in_window(pub, since_dt):
            filtered.append(r)
        else:
            print(f'  [FILTERED] Out of window: {pub} {r.get("title", "")[:50]}')

    # Deduplicate by id
    seen, unique = set(), []
    for r in filtered:
        key = (r.get('id') or r.get('title', '')[:60]).lower()
        if key and key not in seen:
            seen.add(key)
            unique.append(r)

    # Sort newest first
    unique.sort(key=lambda x: x.get('published', ''), reverse=True)

    print(f'\nDone. {len(unique)} unique citing paper(s) in the past {SCAN_DAYS} days.')
    save_results(unique, now)


def save_results(papers, now):
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            'last_update': now.strftime('%Y-%m-%d %H:%M'),
            'topic_name': '文章引用',
            'papers': papers,
        }, f, ensure_ascii=False, indent=2)
    print(f'Saved to {OUTPUT_FILE}')


if __name__ == '__main__':
    fetch_citing_papers()

