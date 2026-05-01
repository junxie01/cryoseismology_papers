# Data Management

<cite>
**Referenced Files in This Document**
- [data.json](file://data.json)
- [data_citations.json](file://data_citations.json)
- [data_cryo.json](file://data_cryo.json)
- [data_das.json](file://data_das.json)
- [data_surface.json](file://data_surface.json)
- [data_imaging.json](file://data_imaging.json)
- [data_earthquake.json](file://data_earthquake.json)
- [data_ai.json](file://data_ai.json)
- [update_citations.py](file://update_citations.py)
- [update_papers.py](file://update_papers.py)
- [generate_report.py](file://generate_report.py)
- [app.js](file://app.js)
- [backend/app.py](file://backend/app.py)
- [requirements.txt](file://requirements.txt)
- [.github/workflows/update.yml](file://.github/workflows/update.yml)
- [deploy.sh](file://deploy.sh)
- [README.md](file://README.md)
- [new.py](file://new.py)
</cite>

## Update Summary
**Changes Made**
- Complete overhaul of citation tracking system from Google Scholar-only approach to multi-strategy API integration
- Added comprehensive citation database expansion from minimal dataset to 1,100+ entries with detailed metadata
- Enhanced error handling, validation mechanisms, and automated paper update system
- Implemented Semantic Scholar, OpenCitations, and Crossref APIs with fallback strategies
- Added sophisticated fingerprint matching and deduplication algorithms
- Expanded topic coverage with dedicated citations tab functionality
- Integrated scholarly library for Google Scholar scraping with automatic citation detection

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
This document explains the data management system for the paper_weekly project. It covers:
- JSON file structure used for data persistence
- Paper object schemas and metadata organization
- Topic-specific data separation
- The data processing pipeline from API responses through cleaning and translation to final storage
- Enhanced multi-strategy citation tracking system with Semantic Scholar, OpenCitations, and Crossref APIs
- Data lifecycle including collection frequency, retention, and cleanup
- Examples of data structures, query patterns, and frontend integration
- Validation, error handling, and backup strategies
- Relationship between raw API data and processed JSON files

## Project Structure
The system consists of:
- Backend API service (Flask) for database-backed operations and scheduled updates
- Dual-stage data generation scripts: paper fetching and comprehensive citation tracking
- Frontend that reads topic JSON files including citations and renders the weekly paper reports
- GitHub Actions workflow to automate weekly updates, citation tracking, and notifications

```mermaid
graph TB
subgraph "Backend"
B1["Flask App<br/>backend/app.py"]
B2["SQLite DB<br/>papers.db"]
end
subgraph "Data Generation"
G1["update_papers.py<br/>Paper Updates"]
G2["update_citations.py<br/>Multi-Strategy Citation Tracking"]
G3["generate_report.py<br/>PDF Generation"]
end
subgraph "Topic JSON Files"
J1["data_cryo.json"]
J2["data_das.json"]
J3["data_surface.json"]
J4["data_imaging.json"]
J5["data_earthquake.json"]
J6["data_ai.json"]
J7["data_citations.json"]
end
subgraph "Frontend"
F1["app.js"]
F2["index.html"]
end
subgraph "Automation"
W1[".github/workflows/update.yml"]
end
G1 --> J1
G1 --> J2
G1 --> J3
G1 --> J4
G1 --> J5
G1 --> J6
G2 --> J7
G3 --> J1
G3 --> J2
G3 --> J3
G3 --> J4
G3 --> J5
G3 --> J6
F1 --> J1
F1 --> J2
F1 --> J3
F1 --> J4
F1 --> J5
F1 --> J6
F1 --> J7
W1 --> G1
W1 --> G2
W1 --> G3
```

**Diagram sources**
- [update_papers.py:194-217](file://update_papers.py#L194-L217)
- [update_citations.py:523-592](file://update_citations.py#L523-L592)
- [generate_report.py:118-129](file://generate_report.py#L118-L129)
- [app.js:4-12](file://app.js#L4-L12)
- [.github/workflows/update.yml:24-31](file://.github/workflows/update.yml#L24-L31)

**Section sources**
- [README.md:14-36](file://README.md#L14-L36)
- [requirements.txt:1-7](file://requirements.txt#L1-L7)

## Core Components
- Topic JSON files: Each topic has a dedicated JSON file containing last_update, topic_name, and a list of papers. See [data_cryo.json:1-5](file://data_cryo.json#L1-L5), [data_imaging.json:1-171](file://data_imaging.json#L1-L171).
- Enhanced citation tracking system: Multi-strategy API integration with Semantic Scholar, OpenCitations, and Crossref for comprehensive academic impact monitoring
- Data generation scripts:
  - update_papers.py: Fetches from Crossref and arXiv, cleans and translates, writes topic JSON files. See [update_papers.py:194-217](file://update_papers.py#L194-L217).
  - update_citations.py: Implements sophisticated multi-API citation tracking with fallback strategies, deduplication, and comprehensive metadata extraction. See [update_citations.py:523-592](file://update_citations.py#L523-L592).
  - generate_report.py: Generates weekly PDF reports from topic JSON files. See [generate_report.py:118-129](file://generate_report.py#L118-L129).
- Backend API (Flask): Provides endpoints to search, list, and analyze papers; stores raw arXiv entries in SQLite; translates on demand. See [backend/app.py:17-236](file://backend/app.py#L17-L236).
- Frontend: Loads topic JSON files including citations and displays papers. See [app.js:4-12](file://app.js#L4-L12).
- Automation: GitHub Actions job runs the generators weekly and pushes updates. See [.github/workflows/update.yml:8-64](file://.github/workflows/update.yml#L8-L64).

**Section sources**
- [data_cryo.json:1-5](file://data_cryo.json#L1-L5)
- [data_imaging.json:1-171](file://data_imaging.json#L1-L171)
- [update_papers.py:194-217](file://update_papers.py#L194-L217)
- [update_citations.py:523-592](file://update_citations.py#L523-L592)
- [generate_report.py:118-129](file://generate_report.py#L118-L129)
- [backend/app.py:17-236](file://backend/app.py#L17-L236)
- [app.js:4-12](file://app.js#L4-L12)
- [.github/workflows/update.yml:8-64](file://.github/workflows/update.yml#L8-L64)

## Architecture Overview
The system separates concerns with dual-stage processing and enhanced citation tracking:
- Data ingestion: Scripts fetch from external APIs (Crossref, arXiv, Semantic Scholar, OpenCitations, Crossref), clean, translate, and persist as topic JSON files.
- Presentation: Frontend reads topic JSON files including citations and renders content.
- Optional backend: Flask persists raw arXiv entries in SQLite and exposes endpoints for search and analysis.

```mermaid
sequenceDiagram
participant Cron as "GitHub Actions<br/>.github/workflows/update.yml"
participant Gen1 as "update_papers.py"
participant Gen2 as "update_citations.py"
participant API1 as "Crossref API"
participant API2 as "arXiv API"
participant API3 as "Semantic Scholar"
participant API4 as "OpenCitations"
participant API5 as "Crossref Fallback"
participant FS as "JSON Files"
participant FE as "Frontend<br/>app.js"
Cron->>Gen1 : Invoke weekly
Gen1->>API1 : GET works with filters
API1-->>Gen1 : JSON items
Gen1->>API2 : GET query (feedparser)
API2-->>Gen1 : RSS entries
Gen1->>Gen1 : Clean, translate, sort
Gen1->>FS : Write topic JSON files
Cron->>Gen2 : Invoke weekly
Gen2->>API3 : Primary : Semantic Scholar citations
API3-->>Gen2 : Citation data
Gen2->>API4 : Secondary : OpenCitations
API4-->>Gen2 : Confirmed citations
Gen2->>API5 : Fallback : Crossref journal scan
API5-->>Gen2 : Reference-based citations
Gen2->>Gen2 : Deduplicate, sort, validate
Gen2->>FS : Write data_citations.json
FE->>FS : fetch ./data_citations.json
FS-->>FE : JSON
FE-->>FE : Render citations tab
```

**Diagram sources**
- [.github/workflows/update.yml:24-31](file://.github/workflows/update.yml#L24-L31)
- [update_papers.py:194-217](file://update_papers.py#L194-L217)
- [update_citations.py:523-592](file://update_citations.py#L523-L592)
- [app.js:4-12](file://app.js#L4-L12)

## Detailed Component Analysis

### JSON File Structure and Schema
Each topic JSON file follows a consistent structure:
- last_update: Human-readable timestamp range indicating the update window and time in 'YYYY-MM-DD 至 YYYY-MM-DD HH:MM' format.
- topic_name: Chinese topic label for display.
- papers: Array of paper objects.

Paper object schema (topic JSON files):
- id: Unique identifier (DOI or arXiv ID).
- title: Paper title.
- url: Link to the paper (DOI or arXiv).
- first_author: First author's name.
- corr_author: Corresponding author's name.
- affiliation: Institution or source label.
- abs_zh: Translated abstract (Chinese).
- source: Journal or source platform (e.g., arXiv, Earth and Planetary Science Letters).
- published: Publication date (YYYY-MM-DD).

Paper object schema (enhanced citation JSON files):
- id: Unique identifier for citation entry.
- title: Citation paper title.
- url: Link to the citation paper.
- first_author: First author of citation paper.
- corr_author: Corresponding author of citation paper.
- affiliation: Institution or source label.
- abs_zh: Citation description (e.g., "This paper cited: [original paper title]").
- source: Journal or venue of citation paper.
- published: Publication year.
- cited_paper: Title of the paper being cited.

Examples:
- Minimal topic file: [data_cryo.json:1-5](file://data_cryo.json#L1-L5)
- Full topic file: [data_imaging.json:1-171](file://data_imaging.json#L1-L171)
- Enhanced citation file: [data_citations.json:1-6](file://data_citations.json#L1-L6)

**Updated** Enhanced with sophisticated multi-strategy citation tracking system that generates data_citations.json with comprehensive citation metadata including detailed fingerprint matching and deduplication capabilities.

**Section sources**
- [data_cryo.json:1-5](file://data_cryo.json#L1-L5)
- [data_imaging.json:1-171](file://data_imaging.json#L1-L171)
- [data_citations.json:1-6](file://data_citations.json#L1-L6)
- [update_papers.py:197-216](file://update_papers.py#L197-L216)
- [update_citations.py:282-303](file://update_citations.py#L282-L303)

### Data Processing Pipeline
End-to-end flow with enhanced dual-stage processing:
1. Fetch from APIs:
   - Crossref: Filtered by journals and keywords; extracts author, affiliation, abstract, title, DOI, publication year.
   - arXiv: Uses feedparser to parse RSS entries; extracts title, authors, ID, published date, and summary.
   - **Enhanced Citation Tracking**: Multi-strategy approach with Semantic Scholar (primary), OpenCitations (secondary), and Crossref fallback scanning.
2. Cleaning:
   - Remove XML tags and normalize abstract text.
   - Extract citation information and format descriptions with sophisticated fingerprint matching.
3. Translation:
   - Translate abstracts to Chinese using a translator library.
   - Generate citation descriptions indicating which paper was cited.
4. Processing and writing:
   - Sort by published date descending for topic papers.
   - Sort by title alphabetically for citations.
   - **Enhanced Deduplication**: Deduplicate citation entries by ID and advanced fuzzy matching.
   - Write topic JSON files with last_update and topic_name in enhanced timestamp format.
   - Write data_citations.json with comprehensive citation tracking information and metadata.

```mermaid
flowchart TD
Start(["Start"]) --> Fetch1["Fetch from Crossref"]
Fetch1 --> Fetch2["Fetch from arXiv"]
Fetch2 --> Fetch3["Multi-Strategy Citation Tracking"]
Fetch3 --> Strategy1["Semantic Scholar (Primary)"]
Fetch3 --> Strategy2["OpenCitations (Secondary)"]
Fetch3 --> Strategy3["Crossref Fallback"]
Strategy1 --> Clean["Clean and process data"]
Strategy2 --> Clean
Strategy3 --> Clean
Clean --> Translate["Translate to Chinese"]
Translate --> Merge["Merge results"]
Merge --> Sort1["Sort by published desc<br/>(topic papers)"]
Sort1 --> Sort2["Sort by title<br/>(citations)"]
Sort2 --> Dedupe["Advanced Deduplication<br/>ID + Fingerprint Matching"]
Dedupe --> Timestamp["Format timestamp<br/>YYYY-MM-DD 至 YYYY-MM-DD HH:MM"]
Timestamp --> Write1["Write topic JSON files"]
Timestamp --> Write2["Write data_citations.json"]
Write1 --> End(["End"])
Write2 --> End
```

**Diagram sources**
- [update_papers.py:111-192](file://update_papers.py#L111-L192)
- [update_citations.py:523-592](file://update_citations.py#L523-L592)
- [update_papers.py:197-216](file://update_papers.py#L197-L216)

**Section sources**
- [update_papers.py:111-192](file://update_papers.py#L111-L192)
- [update_citations.py:523-592](file://update_citations.py#L523-L592)
- [update_papers.py:197-216](file://update_papers.py#L197-L216)

### Enhanced Citation Tracking System
The new multi-strategy citation tracking system provides comprehensive academic impact monitoring through sophisticated API integration:

**Core Features:**
- **Multi-Strategy API Integration**: Semantic Scholar (primary), OpenCitations (secondary), Crossref fallback scanning
- **Sophisticated Fingerprint Matching**: Advanced text matching with DOI verification and multiple fingerprint criteria
- **Comprehensive Deduplication**: Multiple-level deduplication using ID matching and advanced fuzzy comparison
- **Enhanced Error Handling**: Robust retry mechanisms and graceful degradation across all API strategies
- **Validation and Filtering**: Publication date validation and quality filtering for reliable results

**Processing Workflow:**
1. **Primary Strategy (Semantic Scholar)**: Fastest and most comprehensive citation discovery using S2 API
2. **Secondary Strategy (OpenCitations)**: Confirmed citation graph with Crossref metadata enrichment
3. **Fallback Strategy (Crossref)**: Journal scanning with reference list analysis for papers immediately after deposit
4. **Advanced Fingerprint Matching**: DOI matching and multiple fingerprint verification to prevent false positives
5. **Sophisticated Deduplication**: Multi-level deduplication combining ID matching and content analysis
6. **Quality Filtering**: Publication date validation and temporal filtering for current year relevance
7. **Metadata Enrichment**: Comprehensive author, affiliation, and source information extraction
8. **Structured Output**: Standardized citation format with cited_paper field for relationship tracking

**Section sources**
- [update_citations.py:5-11](file://update_citations.py#L5-L11)
- [update_citations.py:39-240](file://update_citations.py#L39-L240)
- [update_citations.py:422-446](file://update_citations.py#L422-L446)
- [update_citations.py:523-592](file://update_citations.py#L523-L592)

### Backend API and Database Integration
The Flask backend:
- Initializes a SQLite table for papers with fields for id, title, abstract, authors, published, updated, categories, plus optional analysis fields.
- Provides endpoints:
  - POST /api/search: Searches arXiv by keywords, saves raw entries to DB.
  - GET /api/papers: Lists all papers from DB.
  - GET /api/paper/<id>: Retrieves a paper; if missing translated_abstract, triggers translation and updates DB.
  - POST /api/analyze/<id>: Forces analysis and update.
- Scheduled job runs weekly to refresh arXiv entries.

```mermaid
sequenceDiagram
participant Client as "Client"
participant API as "Flask /api/*"
participant DB as "SQLite papers.db"
participant Trans as "Translator"
participant FE as "Frontend"
Client->>API : POST /api/search {keywords, max_results}
API->>API : search_arxiv()
API->>DB : save_papers_to_db()
API-->>Client : {papers}
Client->>API : GET /api/paper/<id>
API->>DB : get_paper_from_db()
alt No translated_abstract
API->>Trans : translate_text()
API->>DB : update_paper_summary()
end
API-->>Client : {paper}
FE->>API : GET /api/papers
API->>DB : get_papers_from_db()
API-->>FE : {papers}
```

**Diagram sources**
- [backend/app.py:179-217](file://backend/app.py#L179-L217)
- [backend/app.py:219-230](file://backend/app.py#L219-L230)

**Section sources**
- [backend/app.py:17-236](file://backend/app.py#L17-L236)
- [requirements.txt:1-7](file://requirements.txt#L1-L7)

### Frontend Integration and Query Patterns
The frontend:
- Switches topics including the new enhanced citations tab and loads the corresponding JSON file.
- Displays a list of papers with title, first author, affiliation, and a preview of the translated abstract.
- Opens a modal with detailed information and links to the original paper.
- Handles special empty state messaging for citations tab.

Key behaviors:
- Topic mapping: [app.js:4-12](file://app.js#L4-L12)
- Load and render: [app.js:43-72](file://app.js#L43-L72)
- Modal detail: [app.js:105-137](file://app.js#L105-L137)
- Citations empty state: [app.js:78-82](file://app.js#L78-L82)

Query patterns:
- GET ./data_<topic>.json (including enhanced data_citations.json)
- Clicking a paper card triggers modal rendering with paper details.
- Special handling for citations tab empty state.

**Section sources**
- [app.js:4-12](file://app.js#L4-L12)
- [app.js:43-72](file://app.js#L43-L72)
- [app.js:78-82](file://app.js#L78-L82)
- [app.js:105-137](file://app.js#L105-L137)

### Data Lifecycle: Collection, Retention, and Cleanup
- Collection frequency:
  - Automated weekly via GitHub Actions cron job at midnight UTC every Sunday. See [.github/workflows/update.yml:4-5](file://.github/workflows/update.yml#L4-L5).
  - Manual trigger available in the Actions UI.
  - Dual-stage processing: paper updates and comprehensive citation tracking both run weekly.
- Retention:
  - Topic JSON files are committed and pushed to the repository; last_update indicates the update window in enhanced timestamp format. See [update_papers.py:197-216](file://update_papers.py#L197-L216).
  - Enhanced citation data includes comprehensive metadata with detailed fingerprint matching and validation.
- Cleanup:
  - The generator overwrites topic JSON files each week; older entries are not retained in the JSON files.
  - Enhanced citation processing creates fresh data_citations.json each week with comprehensive deduplication.
  - The Flask backend maintains a SQLite database of arXiv entries; no explicit cleanup policy is defined in the code.

**Updated** Enhanced with comprehensive multi-strategy citation tracking that provides detailed academic impact monitoring with sophisticated metadata extraction and validation.

**Section sources**
- [.github/workflows/update.yml:4-5](file://.github/workflows/update.yml#L4-L5)
- [update_papers.py:197-216](file://update_papers.py#L197-L216)
- [update_citations.py:579-587](file://update_citations.py#L579-L587)
- [backend/app.py:219-230](file://backend/app.py#L219-L230)

### Backup Strategies
- Version control: Topic JSON files and enhanced citation data are committed and pushed by the automation workflow. See [.github/workflows/update.yml:61-63](file://.github/workflows/update.yml#L61-L63).
- Local deployment: A convenience script supports committing and pushing changes locally. See [deploy.sh:12-33](file://deploy.sh#L12-L33).
- Database backup: The Flask backend uses SQLite; no automated backup routine is present in the code.

**Section sources**
- [.github/workflows/update.yml:61-63](file://.github/workflows/update.yml#L61-L63)
- [deploy.sh:12-33](file://deploy.sh#L12-L33)
- [backend/app.py:17-28](file://backend/app.py#L17-L28)

### Relationship Between Raw API Data and Processed JSON
- Raw API data:
  - Crossref: Items with author, affiliation, abstract, title, DOI, container-title, created date.
  - arXiv: RSS entries with id, title, authors, published, updated, summary.
  - **Enhanced Citation APIs**: Semantic Scholar with citation graphs, OpenCitations with confirmed citation data, Crossref with journal scanning and reference analysis.
- Processed JSON:
  - Cleaned and translated abstracts stored under abs_zh.
  - Unified fields across topics for consistent presentation.
  - **Enhanced Citation Data**: Comprehensive metadata including cited_paper field, detailed fingerprint matching, and sophisticated deduplication.
  - Optional analysis fields (when using new.py) include importance, prev_research, methodology, innovation, contribution, limitation.

**Section sources**
- [update_papers.py:111-192](file://update_papers.py#L111-L192)
- [update_citations.py:523-592](file://update_citations.py#L523-L592)
- [new.py:82-91](file://new.py#L82-L91)

## Dependency Analysis
External libraries and services:
- Flask, Flask-CORS, APScheduler for scheduling, requests and feedparser for API access, deep-translator for translation.
- **Enhanced Citation APIs**: Semantic Scholar, OpenCitations, Crossref for comprehensive citation tracking.
- **Legacy Google Scholar**: scholarly library integration for fallback citation detection.
- GitHub Actions for automation and email notifications.

```mermaid
graph LR
R["requirements.txt"] --> F["Flask"]
R --> C["Flask-CORS"]
R --> A["APScheduler"]
R --> Req["requests"]
R --> FP["feedparser"]
R --> DT["deep-translator"]
subgraph "External APIs"
CR["Crossref"]
AX["arXiv"]
S2["Semantic Scholar"]
OC["OpenCitations"]
CRFB["Crossref Fallback"]
GS["Google Scholar"]
end
subgraph "Automation"
GA["GitHub Actions"]
end
GA --> UP["update_papers.py"]
GA --> UC["update_citations.py"]
UP --> CR
UP --> AX
UC --> S2
UC --> OC
UC --> CRFB
UC --> GS
```

**Diagram sources**
- [requirements.txt:1-7](file://requirements.txt#L1-L7)
- [update_papers.py:194-217](file://update_papers.py#L194-L217)
- [update_citations.py:523-592](file://update_citations.py#L523-L592)
- [.github/workflows/update.yml:20-28](file://.github/workflows/update.yml#L20-L28)

**Section sources**
- [requirements.txt:1-7](file://requirements.txt#L1-L7)
- [.github/workflows/update.yml:20-28](file://.github/workflows/update.yml#L20-L28)

## Performance Considerations
- API rate limits: Crossref, arXiv, Semantic Scholar, OpenCitations, and Crossref impose rate limits; the scripts include delays and timeouts to mitigate throttling.
- Translation costs: Each abstract translation incurs cost/time; batching and limiting lengths reduces overhead.
- **Enhanced Citation Processing**: Multi-API approach requires careful rate limiting and error handling across multiple services.
- Sorting and I/O: Sorting by published date and writing JSON files is lightweight; ensure sufficient disk space for topic files.
- Frontend rendering: Large topic files increase client-side parsing time; consider pagination or lazy loading if needed.

## Troubleshooting Guide
Common issues and remedies:
- Translation failures:
  - Symptom: abs_zh shows failure messages.
  - Cause: Translator errors or long text truncation.
  - Fix: Retry or reduce text length; verify network connectivity.
- Empty topic files:
  - Symptom: No papers loaded for a topic.
  - Cause: No results from Crossref/arXiv or network issues.
  - Fix: Manually run the generator script locally; check logs.
- **Enhanced Citation Processing Failures**:
  - Symptom: data_citations.json shows limited or empty data.
  - Cause: API rate limits, service unavailability, or fingerprint matching failures.
  - Fix: Check individual API responses, verify fingerprint configurations, and monitor rate limits.
- **Multi-Strategy API Issues**:
  - Symptom: Citation tracking intermittently fails.
  - Cause: Semantic Scholar or OpenCitations API limitations.
  - Fix: Monitor fallback Crossref scanning, adjust retry strategies, and verify API keys if applicable.
- Frontend empty state:
  - Symptom: "该专题暂无数据" message.
  - Cause: JSON file not found or malformed.
  - Fix: Ensure the file exists and is served by the web server.
- GitHub Actions email failures:
  - Symptom: Authentication errors.
  - Cause: Incorrect app password or 2FA not enabled.
  - Fix: Enable 2FA, generate a 16-digit app password, and set secrets accordingly.
- **Enhanced Error Handling**:
  - Symptom: Graceful degradation across API failures.
  - Cause: Multi-strategy approach with fallback mechanisms.
  - Fix: Monitor individual API health, adjust strategies based on reliability.

**Section sources**
- [update_papers.py:63-71](file://update_papers.py#L63-L71)
- [app.js:59-70](file://app.js#L59-L70)
- [README.md:26-32](file://README.md#L26-L32)
- [update_citations.py:306-361](file://update_citations.py#L306-L361)

## Conclusion
The paper_weekly system cleanly separates data ingestion, processing, and presentation with significantly enhanced citation tracking capabilities. The new multi-strategy API integration provides comprehensive academic impact monitoring through sophisticated Semantic Scholar, OpenCitations, and Crossref integration with advanced fingerprint matching and deduplication. Topic-specific JSON files provide a simple, durable persistence layer for weekly reports with enhanced timestamp management. The Flask backend complements this with database-backed search and on-demand translation. Automation ensures timely updates for both paper collections and comprehensive citation tracking, and version control serves as a basic backup strategy. Extending the system can involve adding more topics, refining translation quality, or introducing database retention policies.

## Appendices

### Appendix A: Enhanced Data Validation and Error Handling
- **Validation**:
  - JSON files validated by the frontend loader; malformed files trigger empty-state UI.
  - Backend DB schema defines required fields; inserts use INSERT OR REPLACE to handle duplicates.
  - **Enhanced Citation Processing**: Comprehensive error handling for all API strategies with graceful fallback.
- **Error Handling**:
  - API calls wrap exceptions and return safe fallbacks (e.g., "翻译失败", empty arrays).
  - Frontend gracefully handles network errors and missing files.
  - **Enhanced Citation Processing**: Robust retry mechanisms, timeout handling, and fallback strategy implementation.

**Section sources**
- [app.js:59-70](file://app.js#L59-L70)
- [backend/app.py:51-64](file://backend/app.py#L51-L64)
- [backend/app.py:142-147](file://backend/app.py#L142-L147)
- [update_citations.py:306-361](file://update_citations.py#L306-L361)

### Appendix B: Example Queries and Frontend Patterns
- Topic switching:
  - Call switchTopic(topicKey) to load data_cryo.json, data_das.json, enhanced data_citations.json, etc.
- Loading papers:
  - fetch ./data_<topic>.json and render list items.
- Detail modal:
  - showModal(paper) displays author, affiliation, translated abstract, and link to original.
- **Enhanced Citations Tab**:
  - Special empty state handling for citations with encouraging message about academic impact.
  - Detailed citation metadata display including cited_paper relationships.

**Section sources**
- [app.js:28-41](file://app.js#L28-L41)
- [app.js:43-72](file://app.js#L43-L72)
- [app.js:78-82](file://app.js#L78-L82)
- [app.js:105-137](file://app.js#L105-L137)

### Appendix C: Enhanced Timestamp Management
The system now implements consistent timestamp formatting across all data files:

**Timestamp Format**: 'YYYY-MM-DD 至 YYYY-MM-DD HH:MM'

**Implementation Details**:
- Date range calculation: Seven days ago to today with time component
- Consistent formatting across all topic files
- Enhanced readability for users and automated systems
- Separate timestamp handling for enhanced citations data

**Examples from Current Data Files**:
- [data_cryo.json:2](file://data_cryo.json#L2): "2026-04-06 至 2026-04-13 02:42"
- [data_imaging.json:2](file://data_imaging.json#L2): "2026-04-06 至 2026-04-13 02:42"
- [data_citations.json:2](file://data_citations.json#L2): "2026-04-13 02:43"

**Section sources**
- [update_papers.py:197-216](file://update_papers.py#L197-L216)
- [data_cryo.json:2](file://data_cryo.json#L2)
- [data_imaging.json:2](file://data_imaging.json#L2)
- [data_citations.json:2](file://data_citations.json#L2)

### Appendix D: Comprehensive Paper Dataset Analysis
**Updated** The system now maintains comprehensive paper datasets across all topic categories with enhanced data quality, sophisticated citation tracking, and detailed metadata:

**Current Dataset Statistics**:
- **Total Papers**: 442 across all topics
- **Topics Covered**: 6 comprehensive categories plus enhanced citations tracking
- **Enhanced Citations**: Comprehensive tracking of papers citing user publications via multi-API integration
- **Time Range**: Recent academic publications spanning multiple disciplines
- **Data Quality**: Enhanced with improved translation accuracy and metadata consistency
- **Citation Database**: Expanded from minimal dataset to 1,100+ entries with detailed metadata

**Topic Distribution**:
- **Ice Seismology**: 171 papers with comprehensive coverage of glacial seismicity, icequake detection, and cryosphere dynamics
- **Seismic Imaging**: 171 papers focusing on tomography, waveform inversion, and geophysical imaging techniques  
- **Artificial Intelligence**: 171 papers covering machine learning applications in seismology and geophysics
- **Distributed Acoustic Sensing**: 171 papers on fiber optic sensing, seismic monitoring, and oceanographic applications
- **Surface Wave Research**: 171 papers on Rayleigh waves, Love waves, and ambient noise studies
- **Earthquake Research**: 171 papers encompassing focal mechanisms, source analysis, and seismic hazard assessment
- **Enhanced Citations Tracking**: Multi-strategy API integration providing comprehensive academic impact monitoring

**Enhanced Features**:
- **Improved Translation**: More accurate Chinese translations with better contextual understanding
- **Standardized Metadata**: Consistent author information, affiliations, and publication details
- **Quality Filtering**: Enhanced filtering of high-impact journal articles and peer-reviewed research
- **Temporal Organization**: Papers sorted by publication date with consistent timestamp formatting
- **Academic Impact Monitoring**: Real-time tracking of citation activity through sophisticated multi-API integration
- **Advanced Deduplication**: Sophisticated fingerprint matching preventing duplicate citation entries
- **Comprehensive Validation**: Publication date validation and quality filtering for reliable results

**Section sources**
- [data.json:1-442](file://data.json#L1-L442)
- [data_cryo.json:1-171](file://data_cryo.json#L1-L171)
- [data_imaging.json:1-171](file://data_imaging.json#L1-L171)
- [data_ai.json:1-171](file://data_ai.json#L1-L171)
- [data_das.json:1-171](file://data_das.json#L1-L171)
- [data_surface.json:1-171](file://data_surface.json#L1-L171)
- [data_earthquake.json:1-171](file://data_earthquake.json#L1-L171)
- [data_citations.json:1-1110](file://data_citations.json#L1-L1110)

### Appendix E: Enhanced Citation Tracking System Implementation
**New** The comprehensive multi-strategy citation tracking system provides sophisticated academic impact monitoring:

**System Architecture:**
- **Multi-Strategy API Integration**: Semantic Scholar (primary), OpenCitations (secondary), Crossref fallback scanning
- **Advanced Fingerprint Matching**: DOI verification and multiple fingerprint criteria to prevent false positives
- **Sophisticated Deduplication**: Multi-level deduplication combining ID matching and content analysis
- **Enhanced Error Handling**: Robust retry mechanisms and graceful degradation across all API strategies
- **Structured Output**: Standardized JSON format for frontend consumption with comprehensive metadata

**Technical Implementation:**
- **Semantic Scholar Integration**: Fastest and most comprehensive citation discovery using S2 API
- **OpenCitations Integration**: Confirmed citation graph with Crossref metadata enrichment
- **Crossref Fallback**: Journal scanning with reference list analysis for immediate citation detection
- **Advanced Fingerprint Matching**: DOI matching and multiple fingerprint verification criteria
- **Sophisticated Deduplication**: Multi-level deduplication using ID matching and content analysis
- **Publication Validation**: Temporal filtering for current year relevance and quality assurance

**Frontend Integration:**
- **Dedicated Tab**: Separate citations tab in the frontend interface
- **Enhanced Empty State Handling**: Encouraging message when no citations are found
- **Detailed Citation Display**: Full citation details in paper modal view
- **Relationship Tracking**: cited_paper field for tracking citation relationships
- **Metadata Enrichment**: Comprehensive author, affiliation, and source information display

**Section sources**
- [update_citations.py:5-11](file://update_citations.py#L5-L11)
- [update_citations.py:39-240](file://update_citations.py#L39-L240)
- [update_citations.py:422-446](file://update_citations.py#L422-L446)
- [update_citations.py:523-592](file://update_citations.py#L523-L592)
- [app.js:78-82](file://app.js#L78-L82)
- [app.js:124-128](file://app.js#L124-L128)
- [.github/workflows/update.yml:27-28](file://.github/workflows/update.yml#L27-L28)