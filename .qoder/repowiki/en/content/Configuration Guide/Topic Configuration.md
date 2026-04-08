# Topic Configuration

<cite>
**Referenced Files in This Document**
- [update_papers.py](file://update_papers.py)
- [index.html](file://index.html)
- [app.js](file://app.js)
- [style.css](file://style.css)
- [.github/workflows/update.yml](file://.github/workflows/update.yml)
- [README.md](file://README.md)
- [requirements.txt](file://requirements.txt)
- [data_cryo.json](file://data_cryo.json)
- [data_imaging.json](file://data_imaging.json)
- [data_ai.json](file://data_ai.json)
- [data_das.json](file://data_das.json)
- [data_surface.json](file://data_surface.json)
- [data_earthquake.json](file://data_earthquake.json)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)
10. [Appendices](#appendices)

## Introduction
This document explains how to configure research topics and search parameters in the paper_weekly system. It focuses on the topic definition structure used in the update script, how search queries are constructed for arXiv and CrossRef APIs, and how results are processed and stored. It also provides guidance on modifying existing topic configurations for seismology areas (cryo, AI, imaging, surface wave, earthquake), customizing parameters such as date ranges, keyword filters, and result limits, and adding new topics. Finally, it covers topic-specific considerations and performance optimization strategies.

## Project Structure
The paper_weekly system consists of:
- A Python update script that defines topics, builds queries, fetches results from arXiv and CrossRef, translates abstracts, and writes JSON files per topic.
- A static web frontend that reads the topic JSON files and renders the weekly reports.
- A GitHub Actions workflow that automates weekly updates.

```mermaid
graph TB
subgraph "Core"
UP["update_papers.py"]
REQ["requirements.txt"]
end
subgraph "Frontend"
HTML["index.html"]
JS["app.js"]
CSS["style.css"]
end
subgraph "Data"
DC["data_cryo.json"]
DI["data_imaging.json"]
DA["data_ai.json"]
DD["data_das.json"]
DS["data_surface.json"]
DE["data_earthquake.json"]
end
subgraph "Automation"
WF[".github/workflows/update.yml"]
end
UP --> DC
UP --> DI
UP --> DA
UP --> DD
UP --> DS
UP --> DE
HTML --> JS
JS --> DC
JS --> DI
JS --> DA
JS --> DD
JS --> DS
JS --> DE
WF --> UP
REQ --> UP
```

**Diagram sources**
- [update_papers.py:14-45](file://update_papers.py#L14-L45)
- [index.html:16-23](file://index.html#L16-L23)
- [app.js:4-11](file://app.js#L4-L11)
- [.github/workflows/update.yml:24-25](file://.github/workflows/update.yml#L24-L25)
- [requirements.txt:1-7](file://requirements.txt#L1-L7)

**Section sources**
- [README.md:33-36](file://README.md#L33-L36)
- [update_papers.py:14-45](file://update_papers.py#L14-L45)
- [index.html:16-23](file://index.html#L16-L23)
- [app.js:4-11](file://app.js#L4-L11)
- [.github/workflows/update.yml:24-25](file://.github/workflows/update.yml#L24-L25)

## Core Components
- Topic definitions and keyword lists: Topics are defined as a dictionary keyed by topic IDs. Each topic includes a Chinese name, a list of keywords, and the output JSON filename.
- Search functions:
  - arXiv search: Builds a query combining keywords with OR logic and retrieves recent submissions.
  - CrossRef search: Builds a query with keywords and filters by selected journals and article type, sorted by publication date.
- Data processing:
  - Cleans abstracts, translates when needed, and normalizes metadata.
  - Sorts results by publication date and writes a standardized JSON structure per topic.

Key configuration points:
- Keyword lists per topic define the semantic coverage and relevance.
- Result limits for arXiv and CrossRef are configurable within the search functions.
- Date range is computed dynamically for the weekly update window.

**Section sources**
- [update_papers.py:14-45](file://update_papers.py#L14-L45)
- [update_papers.py:72-102](file://update_papers.py#L72-L102)
- [update_papers.py:104-124](file://update_papers.py#L104-L124)
- [update_papers.py:126-149](file://update_papers.py#L126-L149)

## Architecture Overview
The system follows a simple pipeline:
- Weekly trigger (GitHub Actions) runs the update script.
- The script computes a date range, iterates topics, queries arXiv and CrossRef, merges and sorts results, and writes JSON files.
- The frontend loads the appropriate JSON file based on the selected topic and displays the results.

```mermaid
sequenceDiagram
participant GH as "GitHub Actions"
participant PY as "update_papers.py"
participant ARX as "arXiv API"
participant CR as "CrossRef API"
participant FS as "Filesystem"
GH->>PY : Invoke weekly update
PY->>PY : Compute date range
loop For each topic
PY->>CR : Search with keywords + journal filter
CR-->>PY : Results (up to limit)
PY->>ARX : Search with keywords (OR)
ARX-->>PY : Results (up to limit)
PY->>PY : Merge, sort, translate
PY->>FS : Write topic JSON
end
PY-->>GH : Complete
```

**Diagram sources**
- [.github/workflows/update.yml:24-25](file://.github/workflows/update.yml#L24-L25)
- [update_papers.py:126-149](file://update_papers.py#L126-L149)
- [update_papers.py:72-102](file://update_papers.py#L72-L102)
- [update_papers.py:104-124](file://update_papers.py#L104-L124)

## Detailed Component Analysis

### Topic Definition Structure
Each topic is defined with:
- id: short identifier used in URLs and filenames.
- name_zh: human-readable Chinese name for display.
- keywords: list of semantically relevant terms used for search queries.
- file: output JSON filename for the topic.

Example structure and usage:
- Topic keys are used to iterate topics and to select the correct output file.
- The frontend maps topic IDs to JSON filenames for loading.

```mermaid
flowchart TD
Start(["Load TOPICS"]) --> Iterate["Iterate topics"]
Iterate --> BuildArXiv["Build arXiv query from keywords"]
Iterate --> BuildCrossRef["Build CrossRef query + filters"]
BuildArXiv --> FetchArXiv["Fetch arXiv entries"]
BuildCrossRef --> FetchCrossRef["Fetch CrossRef items"]
FetchArXiv --> Merge["Merge results"]
FetchCrossRef --> Merge
Merge --> Sort["Sort by published date desc"]
Sort --> Write["Write JSON with last_update, topic_name, papers"]
Write --> End(["Done"])
```

**Diagram sources**
- [update_papers.py:14-45](file://update_papers.py#L14-L45)
- [update_papers.py:104-124](file://update_papers.py#L104-L124)
- [update_papers.py:72-102](file://update_papers.py#L72-L102)
- [update_papers.py:126-149](file://update_papers.py#L126-L149)

**Section sources**
- [update_papers.py:14-45](file://update_papers.py#L14-L45)
- [app.js:4-11](file://app.js#L4-L11)

### Search Query Construction

#### arXiv Search
- Query construction: Keywords are joined with OR logic to broaden recall.
- Sorting: Results are sorted by submitted date in descending order.
- Limits: Configurable via the max_results parameter.

```mermaid
flowchart TD
AStart(["arXiv search(topic_config, max_results)"]) --> Build["Join keywords with OR"]
Build --> Call["GET http://export.arxiv.org/api/query"]
Call --> Parse["Parse entries"]
Parse --> Map["Map fields (id/title/url/authors/summary/source/date)"]
Map --> Clean["Clean and translate summary"]
Clean --> Append["Append to results"]
Append --> AEnd(["Return results"])
```

**Diagram sources**
- [update_papers.py:104-124](file://update_papers.py#L104-L124)

**Section sources**
- [update_papers.py:104-124](file://update_papers.py#L104-L124)

#### CrossRef Search
- Query construction: Keywords are passed as a free-text query.
- Filters: Selected journals and article type are combined as filters.
- Sorting: Results are sorted by published date descending.
- Limits: Configurable via the max_results parameter.

```mermaid
flowchart TD
CStart(["CrossRef search(topic_config, max_results)"]) --> Join["Join keywords into query"]
Join --> BuildFilters["Build filters: journals + type:journal-article"]
BuildFilters --> Call["GET works endpoint"]
Call --> Parse["Parse items"]
Parse --> Map["Map fields (DOI/title/author/abstract/container/published)"]
Map --> Clean["Clean and translate abstract"]
Clean --> Append["Append to results"]
Append --> CEnd(["Return results"])
```

**Diagram sources**
- [update_papers.py:72-102](file://update_papers.py#L72-L102)

**Section sources**
- [update_papers.py:72-102](file://update_papers.py#L72-L102)

### Data Processing and Storage
- Cleaning: Removes XML-like tags and standardizes abstract prefixes.
- Translation: Uses a translation service to convert abstracts to Chinese; applies cleaning again to translated text.
- Sorting: Sorts merged results by published date descending.
- JSON structure per topic:
  - last_update: Human-readable date range and time.
  - topic_name: Chinese topic name.
  - papers: List of paper objects with normalized fields.

```mermaid
erDiagram
TOPIC_JSON {
string last_update
string topic_name
array papers
}
PAPER {
string id
string title
string url
string first_author
string corr_author
string affiliation
string abs_zh
string source
string published
}
TOPIC_JSON ||--o{ PAPER : "contains"
```

**Diagram sources**
- [update_papers.py:141-146](file://update_papers.py#L141-L146)
- [update_papers.py:90-100](file://update_papers.py#L90-L100)
- [update_papers.py:112-122](file://update_papers.py#L112-L122)

**Section sources**
- [update_papers.py:54-71](file://update_papers.py#L54-L71)
- [update_papers.py:141-146](file://update_papers.py#L141-L146)

### Frontend Integration
- Topic buttons map to topic IDs and trigger loading of the corresponding JSON file.
- The app fetches the JSON, updates the last update and topic name, and renders cards with previews.
- Clicking a card opens a modal with author and translated abstract details.

```mermaid
sequenceDiagram
participant UI as "index.html"
participant APP as "app.js"
participant FS as "JSON files"
UI->>APP : User clicks topic button
APP->>FS : fetch ./data_<topic>.json
FS-->>APP : JSON payload
APP->>UI : Render list and metadata
UI->>APP : Click paper card
APP->>UI : Show modal with details
```

**Diagram sources**
- [index.html:16-23](file://index.html#L16-L23)
- [app.js:42-71](file://app.js#L42-L71)
- [app.js:94-127](file://app.js#L94-L127)

**Section sources**
- [index.html:16-23](file://index.html#L16-L23)
- [app.js:4-11](file://app.js#L4-L11)
- [app.js:42-71](file://app.js#L42-L71)

## Dependency Analysis
- update_papers.py depends on:
  - requests and feedparser for API calls and parsing.
  - deep-translator for abstract translation.
  - datetime and urllib for date range computation and URL encoding.
- Frontend depends on:
  - app.js to load and render JSON data.
  - style.css for presentation.
- Automation depends on:
  - GitHub Actions to run the update script and push changes.

```mermaid
graph LR
UP["update_papers.py"] --> REQ["requests"]
UP --> FP["feedparser"]
UP --> DT["deep-translator"]
UP --> URLLIB["urllib.parse"]
UP --> TIME["datetime"]
HTML["index.html"] --> JS["app.js"]
JS --> CSS["style.css"]
WF[".github/workflows/update.yml"] --> UP
WF --> REQ
```

**Diagram sources**
- [update_papers.py:1-10](file://update_papers.py#L1-L10)
- [requirements.txt:1-7](file://requirements.txt#L1-L7)
- [index.html:7](file://index.html#L7)
- [style.css:1-179](file://style.css#L1-L179)
- [.github/workflows/update.yml:20-25](file://.github/workflows/update.yml#L20-L25)

**Section sources**
- [requirements.txt:1-7](file://requirements.txt#L1-L7)
- [update_papers.py:1-10](file://update_papers.py#L1-L10)
- [.github/workflows/update.yml:20-25](file://.github/workflows/update.yml#L20-L25)

## Performance Considerations
- Query limits: Adjust max_results for arXiv and CrossRef to balance freshness and performance.
- Sorting and deduplication: The script merges results and sorts by date; ensure keyword lists avoid excessive overlap to reduce duplicates.
- Translation costs: Translation is applied to abstracts; consider limiting the length or number of translated items if rate limits apply.
- Network timeouts: Requests have timeout parameters; tune for reliability under network variability.
- Frontend rendering: Large JSON files increase load time; consider pagination or lazy loading if needed.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
- Translation failures: The translation wrapper catches exceptions and falls back to a placeholder; verify credentials and network connectivity if translations fail repeatedly.
- API errors: arXiv and CrossRef calls are wrapped in try-except; check logs for error messages and adjust query parameters or retry logic if needed.
- Empty results: Verify keyword lists and date range; ensure journals list is appropriate for the domain.
- Frontend empty state: If a topic JSON is missing or unreadable, the frontend shows an empty state message; run the update script to regenerate data.

**Section sources**
- [update_papers.py:63-71](file://update_papers.py#L63-L71)
- [update_papers.py:79-102](file://update_papers.py#L79-L102)
- [update_papers.py:109-124](file://update_papers.py#L109-L124)
- [app.js:46-71](file://app.js#L46-L71)

## Conclusion
The paper_weekly system provides a straightforward, extensible framework for weekly topic-based research tracking. Topic configuration centers on keyword lists and output filenames, with flexible search parameters for arXiv and CrossRef. The frontend cleanly renders topic-specific results, and automation ensures regular updates. Modifying topics, adjusting search parameters, and adding new topics are straightforward tasks that leverage the existing structure.

[No sources needed since this section summarizes without analyzing specific files]

## Appendices

### A. Topic Configuration Reference
- Location: Topic definitions and keyword lists.
- Fields:
  - id: short topic ID.
  - name_zh: display name.
  - keywords: list of terms.
  - file: output JSON filename.

**Section sources**
- [update_papers.py:14-45](file://update_papers.py#L14-L45)

### B. Search Parameter Customization
- arXiv:
  - Query: OR-joined keywords.
  - Sorting: submitted date descending.
  - Limit: max_results parameter.
- CrossRef:
  - Query: keywords.
  - Filters: journals and article type.
  - Sorting: published descending.
  - Limit: rows parameter.

**Section sources**
- [update_papers.py:104-124](file://update_papers.py#L104-L124)
- [update_papers.py:72-102](file://update_papers.py#L72-L102)

### C. JSON Data Structure for Each Topic
- Keys:
  - last_update: date range and time.
  - topic_name: Chinese topic name.
  - papers: list of paper objects.

Paper object fields:
- id, title, url, first_author, corr_author, affiliation, abs_zh, source, published.

**Section sources**
- [update_papers.py:141-146](file://update_papers.py#L141-L146)
- [update_papers.py:90-100](file://update_papers.py#L90-L100)
- [update_papers.py:112-122](file://update_papers.py#L112-L122)

### D. Modifying Existing Topic Configurations for Seismology Areas
- Cryo (glacier seismology): Broaden keywords to include calving, ice shelf, and glacial seismicity.
- DAS (Distributed Acoustic Sensing): Add terms like phase-sensitive OTDR and fiber optic seismic monitoring.
- Surface wave: Include ambient noise interferometry and surface wave detection.
- Imaging: Add full waveform inversion and body wave tomography.
- Earthquake: Extend to focal mechanism and source mechanism inversion.

Adjust the keywords list per topic and rerun the update script to reflect changes.

**Section sources**
- [update_papers.py:15-39](file://update_papers.py#L15-L39)

### E. Adding a New Topic
Steps:
- Define a new topic entry with id, name_zh, keywords, and file.
- Ensure the output JSON filename exists or is handled by the script.
- Optionally add a frontend button mapping to the new topic ID.
- Run the update script to generate the new topic’s JSON.

**Section sources**
- [update_papers.py:14-45](file://update_papers.py#L14-L45)
- [index.html:16-23](file://index.html#L16-L23)
- [app.js:4-11](file://app.js#L4-L11)

### F. Optimizing Query Performance
- Tune max_results for arXiv and CrossRef to balance freshness and speed.
- Keep keyword lists concise and domain-relevant to reduce noise.
- Consider caching or incremental updates if the system grows larger.
- Monitor translation service quotas and apply fallbacks gracefully.

[No sources needed since this section provides general guidance]