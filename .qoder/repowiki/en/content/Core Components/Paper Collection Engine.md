# Paper Collection Engine

<cite>
**Referenced Files in This Document**
- [update_papers.py](file://update_papers.py)
- [README.md](file://README.md)
- [requirements.txt](file://requirements.txt)
- [data.json](file://data.json)
- [data_cryo.json](file://data_cryo.json)
- [data_imaging.json](file://data_imaging.json)
- [.github/workflows/update.yml](file://.github/workflows/update.yml)
- [index.html](file://index.html)
- [app.js](file://app.js)
- [style.css](file://style.css)
</cite>

## Update Summary
**Changes Made**
- Enhanced proxy configuration management with explicit HTTP_PROXY/HTTPS_PROXY environment variable handling
- Implemented session-based requests with trust_env=False to bypass system proxy settings
- Added comprehensive retry strategy with exponential backoff for Crossref API integration
- Improved error handling and timeout management for Crossref API calls
- Added SSL verification fallback mechanism for enhanced reliability

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
This document provides comprehensive documentation for the paper collection engine implemented in update_papers.py. The engine automatically collects recent papers across six specialized topics (cryoseismology, DAS, surface wave, seismic imaging, earthquake research, and AI) from two major academic APIs: arXiv and CrossRef. It integrates translation via Google Translate API, cleans abstracts, filters journals, sorts results by publication date, and writes JSON files consumed by a frontend web interface. The system is scheduled to run weekly via GitHub Actions and can be manually triggered.

**Updated** Enhanced with robust proxy configuration management and improved error handling for reliable API integration in various network environments.

## Project Structure
The repository is organized into:
- Core automation script: update_papers.py
- Frontend web interface: index.html, app.js, style.css
- Data output files: data*.json (per topic)
- Workflow automation: .github/workflows/update.yml
- Documentation and requirements: README.md, requirements.txt

```mermaid
graph TB
subgraph "Automation"
UP["update_papers.py"]
WF[".github/workflows/update.yml"]
end
subgraph "Frontend"
HTML["index.html"]
JS["app.js"]
CSS["style.css"]
end
subgraph "Data"
DC["data_cryo.json"]
DI["data_imaging.json"]
DJ["data.json"]
end
WF --> UP
UP --> DC
UP --> DI
UP --> DJ
HTML --> JS
JS --> DC
JS --> DI
JS --> DJ
CSS --> HTML
```

**Diagram sources**
- [update_papers.py:126-149](file://update_papers.py#L126-L149)
- [.github/workflows/update.yml:24-25](file://.github/workflows/update.yml#L24-L25)
- [index.html:1-50](file://index.html#L1-L50)
- [app.js:42-71](file://app.js#L42-L71)
- [data_cryo.json:1-5](file://data_cryo.json#L1-L5)
- [data_imaging.json:1-5](file://data_imaging.json#L1-L5)

**Section sources**
- [README.md:33-40](file://README.md#L33-L40)
- [requirements.txt:1-7](file://requirements.txt#L1-L7)

## Core Components
- Topic configuration: Defines six topics, each with a Chinese name, keyword list, and output JSON filename.
- Journal filter: A curated list of high-impact journals used to constrain CrossRef results.
- Abstract cleaning: Removes XML tags and common prefixes from raw abstracts.
- Translation service: Uses Google Translate API via deep-translator to translate abstracts into Simplified Chinese.
- API integrations:
  - arXiv: Searches by keyword OR logic, sorted by submission date descending.
  - CrossRef: Filters by journal list and article type, sorted by publication date descending.
- **Enhanced Proxy Management**: Explicit HTTP_PROXY/HTTPS_PROXY environment variable handling and session-based requests with trust_env=False.
- **Improved Error Handling**: Comprehensive retry strategy with exponential backoff and SSL verification fallback for Crossref API integration.
- Date range calculation: Computes a weekly window (last 7 days) and formats a human-readable range string.
- Sorting and output: Sorts results by publication year/date, then writes JSON with metadata.

Key implementation references:
- Topic configuration and journal list: [update_papers.py:14-52](file://update_papers.py#L14-L52)
- Abstract cleaning: [update_papers.py:54-61](file://update_papers.py#L54-L61)
- Translation wrapper: [update_papers.py:63-70](file://update_papers.py#L63-L70)
- CrossRef search: [update_papers.py:72-102](file://update_papers.py#L72-L102)
- arXiv search: [update_papers.py:104-124](file://update_papers.py#L104-L124)
- Date range and JSON write: [update_papers.py:129-148](file://update_papers.py#L129-L148)

**Section sources**
- [update_papers.py:14-52](file://update_papers.py#L14-L52)
- [update_papers.py:54-70](file://update_papers.py#L54-L70)
- [update_papers.py:72-124](file://update_papers.py#L72-L124)
- [update_papers.py:129-148](file://update_papers.py#L129-L148)

## Architecture Overview
The engine follows a straightforward pipeline with enhanced reliability:
- Initialize topic list and journal filter.
- Configure robust proxy management and session-based requests.
- For each topic:
  - Query arXiv and CrossRef with improved error handling.
  - Merge results.
  - Clean and translate abstracts.
  - Sort by publication date.
  - Write JSON file with metadata.

```mermaid
sequenceDiagram
participant Scheduler as "GitHub Actions"
participant Script as "update_papers.py"
participant Proxy as "Proxy Configuration"
participant CrossRef as "CrossRef API"
participant Arxiv as "arXiv API"
participant Translator as "Google Translate API"
participant FS as "File System"
Scheduler->>Script : Invoke main()
Script->>Script : Configure proxy settings
Script->>Script : Compute date range
Script->>Proxy : Initialize session with trust_env=False
Script->>CrossRef : search_crossref(topic) with retry
CrossRef-->>Script : List of journal articles
Script->>Arxiv : search_arxiv(topic)
Arxiv-->>Script : List of preprints
Script->>Script : Merge results
Script->>Script : Clean abstracts
Script->>Translator : translate_text(abs)
Translator-->>Script : Translated abstract
Script->>Script : Sort by published date
Script->>FS : Write JSON file per topic
Script-->>Scheduler : Done
```

**Diagram sources**
- [.github/workflows/update.yml:24-25](file://.github/workflows/update.yml#L24-L25)
- [update_papers.py:18-37](file://update_papers.py#L18-L37)
- [update_papers.py:72-124](file://update_papers.py#L72-L124)
- [update_papers.py:63-70](file://update_papers.py#L63-L70)
- [update_papers.py:129-148](file://update_papers.py#L129-L148)

## Detailed Component Analysis

### Enhanced Proxy Configuration Management
The system now implements comprehensive proxy management to ensure reliable operation in various network environments:

```mermaid
flowchart TD
ProxyConfig["Proxy Configuration"] --> ClearEnv["Clear HTTP_PROXY/HTTPS_PROXY env vars"]
ClearEnv --> CreateSession["Create requests.Session()"]
CreateSession --> TrustEnvFalse["Set trust_env=False"]
TrustEnvFalse --> MountAdapters["Mount HTTPAdapter with retry strategy"]
MountAdapters --> Ready["Ready for API calls"]
```

**Diagram sources**
- [update_papers.py:18-37](file://update_papers.py#L18-L37)

**Section sources**
- [update_papers.py:18-37](file://update_papers.py#L18-L37)

### Improved Error Handling and Retry Strategy
The Crossref API integration now includes comprehensive error handling with exponential backoff:

```mermaid
flowchart TD
CrossRefCall["search_crossref()"] --> NormalRequest["Normal request attempt"]
NormalRequest --> Success{"Request successful?"}
Success --> |Yes| ProcessResults["Process JSON results"]
Success --> |No| LogError["Log error and try SSL fallback"]
LogError --> SSLFallback["Request with verify=False"]
SSLFallback --> SSLSuccess{"SSL fallback successful?"}
SSLSuccess --> |Yes| ProcessResults
SSLSuccess --> |No| ReturnEmpty["Return empty results"]
ProcessResults --> ReturnResults["Return processed papers"]
```

**Diagram sources**
- [update_papers.py:111-170](file://update_papers.py#L111-L170)

**Section sources**
- [update_papers.py:111-170](file://update_papers.py#L111-L170)

### Topic Configuration Structure
Each topic defines:
- Chinese name for display.
- Keyword list used for both arXiv and CrossRef searches.
- Output JSON filename.

```mermaid
flowchart TD
Topics["TOPICS (dict)"] --> T1["cryoseismology<br/>name_zh, keywords, file"]
Topics --> T2["das<br/>name_zh, keywords, file"]
Topics --> T3["surface_wave<br/>name_zh, keywords, file"]
Topics --> T4["imaging<br/>name_zh, keywords, file"]
Topics --> T5["earthquake<br/>name_zh, keywords, file"]
Topics --> T6["ai<br/>name_zh, keywords, file"]
```

**Diagram sources**
- [update_papers.py:14-45](file://update_papers.py#L14-L45)

**Section sources**
- [update_papers.py:14-45](file://update_papers.py#L14-L45)

### Journal Filtering Mechanism
The journal list constrains CrossRef results to high-quality venues. The search builds a filter string combining container titles and article type.

```mermaid
flowchart TD
Journals["JOURNALS list"] --> BuildFilter["Build filter string:<br/>container-title:Name1,container-title:Name2,...,type:journal-article"]
BuildFilter --> CrossRefCall["CrossRef API call with filters"]
CrossRefCall --> Items["Items with authors, abstract, title, DOI, published date"]
```

**Diagram sources**
- [update_papers.py:47-52](file://update_papers.py#L47-L52)
- [update_papers.py:75-76](file://update_papers.py#L75-L76)

**Section sources**
- [update_papers.py:47-52](file://update_papers.py#L47-L52)
- [update_papers.py:75-76](file://update_papers.py#L75-L76)

### Abstract Cleaning Algorithm
Removes XML tags and common prefixes ("Abstract", "摘要", "抽象的"。, "抽象的") to normalize raw text before translation.

```mermaid
flowchart TD
Start(["clean_abstract(text)"]) --> CheckEmpty{"Text empty?"}
CheckEmpty --> |Yes| ReturnEmpty["Return empty string"]
CheckEmpty --> |No| RemoveTags["Remove <...> tags"]
RemoveTags --> StripPrefixes["Strip leading prefixes:<br/>Abstract/摘要/抽象的。/抽象的"]
StripPrefixes --> Trim["Strip whitespace"]
Trim --> End(["Return cleaned text"])
```

**Diagram sources**
- [update_papers.py:54-61](file://update_papers.py#L54-L61)

**Section sources**
- [update_papers.py:54-61](file://update_papers.py#L54-L61)

### Translation Service Integration
Uses deep-translator GoogleTranslator to translate abstracts. Implements a safety guard for short texts and handles exceptions by returning a fallback message.

```mermaid
flowchart TD
Start(["translate_text(text)"]) --> ShortCheck{"Text empty or < 10 chars?"}
ShortCheck --> |Yes| Fallback["Return '无摘要详情'"]
ShortCheck --> |No| Init["Initialize GoogleTranslator(source='auto', target='zh-CN')"]
Init --> TryTranslate["Translate first ~2000 chars"]
TryTranslate --> Clean["Apply clean_abstract to result"]
Clean --> End(["Return translated text"])
TryTranslate -.->|Exception| Fallback2["Return '翻译失败'"]
```

**Diagram sources**
- [update_papers.py:63-70](file://update_papers.py#L63-L70)

**Section sources**
- [update_papers.py:63-70](file://update_papers.py#L63-L70)

### API Integration Details

#### Enhanced CrossRef Search
- Constructs a query from topic keywords.
- Applies journal filters and article type filter.
- Sorts by published date descending.
- **Enhanced Error Handling**: Implements retry strategy with exponential backoff and SSL verification fallback.
- Extracts author, affiliation, title, DOI, URL, and abstract; translates abstract; records source and published year.

```mermaid
sequenceDiagram
participant Script as "update_papers.py"
participant Session as "requests.Session"
participant CrossRef as "CrossRef API"
Script->>Session : Initialize with trust_env=False
Session->>CrossRef : GET works?query=...&filter=...&sort=published&order=desc&rows=N
CrossRef-->>Session : JSON items or error
Session->>Session : Retry on 429/500/502/503/504
Session->>Script : Process results
Script->>Script : Build author info, affiliation
Script->>Script : Clean abstract
Script->>Script : Translate abstract
Script-->>Script : Append to results
```

**Diagram sources**
- [update_papers.py:111-170](file://update_papers.py#L111-L170)
- [update_papers.py:24-37](file://update_papers.py#L24-L37)

**Section sources**
- [update_papers.py:111-170](file://update_papers.py#L111-L170)

#### arXiv Search
- Builds a search query using OR logic across keywords.
- Sorts by submittedDate descending.
- Extracts ID, title, URL, first author, affiliation, and abstract; translates abstract; marks source as arXiv.

```mermaid
sequenceDiagram
participant Script as "update_papers.py"
participant Arxiv as "arXiv API"
Script->>Arxiv : GET api/query?search_query=...&sortBy=submittedDate&sortOrder=descending&max_results=N
Arxiv-->>Script : Atom feed entries
Script->>Script : Iterate entries
Script->>Script : Build paper fields
Script->>Script : Translate summary
Script-->>Script : Append to results
```

**Diagram sources**
- [update_papers.py:172-192](file://update_papers.py#L172-L192)

**Section sources**
- [update_papers.py:172-192](file://update_papers.py#L172-L192)

### Data Processing Pipeline
- Merge results from both APIs.
- Sort by published date (descending).
- Write JSON with metadata: last_update, topic_name, and papers array.

```mermaid
flowchart TD
Merge["Merge CrossRef + arXiv results"] --> Sort["Sort by published date desc"]
Sort --> BuildMeta["Build metadata:<br/>last_update, topic_name"]
BuildMeta --> Write["Write JSON file per topic"]
```

**Diagram sources**
- [update_papers.py:138-148](file://update_papers.py#L138-L148)

**Section sources**
- [update_papers.py:138-148](file://update_papers.py#L138-L148)

### Date Range Calculation and Result Sorting
- Calculates a 7-day window centered on the current date.
- Formats a human-readable range string and appends current time.
- Sorts results by published year/date string in descending order.

```mermaid
flowchart TD
Now["Get current datetime"] --> SevenDaysAgo["Subtract 7 days"]
SevenDaysAgo --> FormatRange["Format 'YYYY-MM-DD to YYYY-MM-DD'"]
FormatTime["Format HH:MM"] --> Meta["Assemble last_update"]
Meta --> Sort["Sort results by published desc"]
```

**Diagram sources**
- [update_papers.py:129-139](file://update_papers.py#L129-L139)

**Section sources**
- [update_papers.py:129-139](file://update_papers.py#L129-L139)

### JSON File Generation Process
- Writes a JSON object per topic containing:
  - last_update: formatted date/time range
  - topic_name: Chinese topic name
  - papers: list of paper dictionaries with keys: id, title, url, first_author, corr_author, affiliation, abs_zh, source, published

```mermaid
flowchart TD
Open["Open file for writing"] --> Dump["Dump JSON with:<br/>{last_update, topic_name, papers}"]
Dump --> Close["Close file"]
```

**Diagram sources**
- [update_papers.py:141-146](file://update_papers.py#L141-L146)

**Section sources**
- [update_papers.py:141-146](file://update_papers.py#L141-L146)

### Frontend Consumption of JSON
- The frontend loads data_cryo.json, data_imaging.json, and others based on the selected topic.
- Displays last_update and topic_name, renders a list of papers, and opens a modal with translated abstract and links.

```mermaid
sequenceDiagram
participant Browser as "Browser"
participant Index as "index.html"
participant App as "app.js"
participant Data as "data_cryo.json / data_imaging.json"
Browser->>Index : Load page
Index->>App : Initialize
App->>App : switchTopic(topic)
App->>Data : fetch(file)
Data-->>App : JSON {last_update, topic_name, papers}
App->>App : renderPapersList()
App-->>Browser : Render cards and modal
```

**Diagram sources**
- [index.html:16-27](file://index.html#L16-L27)
- [app.js:42-71](file://app.js#L42-L71)
- [data_cryo.json:1-5](file://data_cryo.json#L1-L5)
- [data_imaging.json:1-5](file://data_imaging.json#L1-L5)

**Section sources**
- [index.html:16-27](file://index.html#L16-L27)
- [app.js:42-71](file://app.js#L42-L71)
- [data_cryo.json:1-5](file://data_cryo.json#L1-L5)
- [data_imaging.json:1-5](file://data_imaging.json#L1-L5)

## Dependency Analysis
External libraries used:
- requests: HTTP client for API calls with enhanced session management.
- feedparser: Parses arXiv Atom feeds.
- deep-translator: Google Translate integration.
- datetime, timedelta: Date/time utilities.
- re: Regular expressions for abstract cleaning.
- urllib3: Provides retry strategy and SSL handling.

```mermaid
graph TB
UP["update_papers.py"] --> Requests["requests"]
UP --> Feedparser["feedparser"]
UP --> DT["deep-translator"]
UP --> DateTime["datetime, timedelta"]
UP --> Re["re"]
UP --> URLLib3["urllib3 (Retry, HTTPAdapter)"]
```

**Diagram sources**
- [requirements.txt:1-7](file://requirements.txt#L1-L7)
- [update_papers.py:1-12](file://update_papers.py#L1-L12)

**Section sources**
- [requirements.txt:1-7](file://requirements.txt#L1-L7)
- [update_papers.py:1-12](file://update_papers.py#L1-L12)

## Performance Considerations
- **Enhanced API Reliability**: The new proxy configuration and retry strategy significantly improve API call reliability across different network environments.
- API rate limits: arXiv and CrossRef impose rate limits. The enhanced retry strategy with exponential backoff helps mitigate rate limiting issues.
- **Improved Timeout Handling**: Session-based requests with configurable timeouts provide better control over network operations.
- Translation limits: Google Translate has quotas; monitor usage and consider batching or caching translations.
- Sorting complexity: Sorting is O(n log n) per topic; acceptable for typical result sizes.
- I/O overhead: Writing JSON per topic; ensure filesystem performance is adequate for frequent updates.

## Troubleshooting Guide

Common issues and remedies:
- **Enhanced Proxy Issues**:
  - The system now explicitly clears HTTP_PROXY/HTTPS_PROXY environment variables and sets trust_env=False to bypass system proxy settings.
  - If you encounter proxy-related issues, verify that the environment variables are properly cleared before running the script.
- API rate limits or throttling:
  - The enhanced retry strategy with exponential backoff (3 retries, backoff factor 1) automatically handles temporary rate limit issues.
  - Monitor Crossref API responses for 429/500/502/503/504 status codes.
- **Network timeouts**:
  - Both Crossref and arXiv requests now use 30-second timeouts.
  - The SSL verification fallback mechanism provides an alternative when SSL certificate verification fails.
- Translation failures:
  - The translation function returns a fallback message on exceptions.
  - Consider caching translated results to reduce repeated calls.
- Empty or missing data:
  - Verify topic keywords and journal filters.
  - Ensure JSON files are written and readable by the frontend.
- **Enhanced Error Logging**:
  - Crossref API calls now include detailed error logging with exception messages.
  - The fallback mechanism attempts SSL verification without certificate validation as a last resort.
- Frontend loading errors:
  - Confirm file paths match topic mapping in the frontend.
  - Check CORS and file serving configuration if hosted externally.

**Section sources**
- [update_papers.py:18-37](file://update_papers.py#L18-L37)
- [update_papers.py:111-170](file://update_papers.py#L111-L170)
- [update_papers.py:172-192](file://update_papers.py#L172-L192)
- [app.js:42-71](file://app.js#L42-L71)

## Conclusion
The paper collection engine automates weekly discovery of relevant papers across six specialized topics by integrating arXiv and CrossRef, translating abstracts, filtering journals, and publishing JSON consumed by a lightweight frontend. The enhanced proxy configuration management and improved error handling make the system more robust and reliable across different network environments. The modular design allows easy extension of topics, keywords, and filters. With continued enhancements to error handling, translation caching, and robust error logging, the system can become even more resilient and production-ready.

## Appendices

### Execution Flow Reference
- Main entry point and loop over topics: [update_papers.py:194-217](file://update_papers.py#L194-L217)
- Weekly scheduling via GitHub Actions: [.github/workflows/update.yml:4-6](file://.github/workflows/update.yml#L4-L6)
- Manual trigger support: [.github/workflows/update.yml:6](file://.github/workflows/update.yml#L6)

**Section sources**
- [update_papers.py:194-217](file://update_papers.py#L194-L217)
- [.github/workflows/update.yml:4-6](file://.github/workflows/update.yml#L4-L6)

### Enhanced Proxy Configuration Implementation
The system now includes comprehensive proxy management:

```python
# 禁用代理设置
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

# 创建 session 并配置重试策略
session = requests.Session()
session.trust_env = False  # 忽略环境变量中的代理设置

# 配置重试策略：最多重试3次，间隔1秒
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)
```

**Section sources**
- [update_papers.py:18-37](file://update_papers.py#L18-L37)