
# Project ASK Change Log
All notable changes to this project will be documented in this file.  

## [0.7.4] - 2025-04-22
### Features
- Implementing retreival filtering (experimental)

### Bug Fixes
- Moved "Checking documents..." appear below "Type your question or task here"
- cached_rag function was missing a parameter
- Fixed metadata data type issue with unit and expiration_date fields
- Fixed page nubering to start at 1 instead of 0 in results

## [0.6.4] - 2025-04-18
### Features
- Added terms of service page
- Library list now includes additional metadata fields (e.g., effective date, expriation date)
- 

- Feedback resets per query instead of once per session to enable re-use
- System now records feedback comments

## [0.6.3] - 2025-04-11
### Features
- Enriched Full Source Details container with more metadata and better formatting
- Sources document by name and issue date rather than by filename
- Filter by date or scope (i.e, national, district, etc) implemented but not turned on for user
- Vector db is now enabled for hybrid search (configured to support both sparse and dense vectors)
- 'unit' field added to metadata to support filtering
- 
### Bug Fixes
- Updated code to work with update in streamlit
- Updated OpenAI API key to track usage specific to this project
- 
## [0.6.2] - 2024-09-25
### Features
- Renamed prompt_ui.py (ui.py), inference.py (rag.py) and refactored to keep clean. 
- Rag logic is now in rag.py
- Openai status functions are now in utils.py
- Implemented caching to improve speed for various clients: truberics, qdrant, lc, retriever, and library list
- Implemented test scripts


## [0.6.1] - 2024-09-07
### Features
- Add additional metadata keys and values into library data, including effective date
- Moved vector db admin tools into separate git repo
- Updated data_flow_diagram.png
- Reorganized repo file directory

### Bug fixes
- Addressed bug in UUID approach. All docs to be re-tagged with new UUIDs in next database re-build  


## [0.5.3] - 2023-12-19
### Features
- Removal of ALAUXs that announce documents in the library to avoid competing with those docs during retrieval: ALAUXs 2023 (003, 008, 012, 013, 032, 034, 036), ALAUXs 2022 (025,034, 041,042, 043)
- Developed code to delete docs from library
- Removal of Streamlit collecting summary statistics

### Bug fixes
- Removal of superceded directives: AUX-PL-007(E)
- Added missing AUX-PL-007(E)
- Number of library documents and last update date are now dynamically generated


## [0.5.2] - 2023-12-13
### Features
-Added a Spanish language example

### Bug fixes
- Added missing 2023 ALAUXes and removed outdated ones

## [0.5.1] - 2023-11-24
### Features
- Extensive readme file added to git repo

### Bug fixes
- Error message if Open AI credits are exceeded

## [0.5.0] - 2023-11-20
### Features
- Significant increase in speed (2-3x faster) 
- Additional page in library outlining product roadmap

### Bug fixes
- User warning if OpenAI service is down 
- Modifications to the prompt and hyperparameters for improved doc retrieval
- Removed two outdated policy documents

### Breaking changes
- Moved code to new github repository and relaunched user app

## [0.4.0] - 2023-11-14
### Features
- Customized the prompt to explicitly seek all requirements and to distinguish between initial and currency maintenance
- Improved naming conventions in the github repo

## [0.3.0] - 2023-11-03
### Features
- Expanded info section to provide additional informtion about the service
- Reincorporatie Truberics feedback collector
- Include search query string with results
- Ability to test without LLM call by using "pledge" as search query
- Addition of a Roadmap to git repo

### Bug fixes
- Deployed as standard form so fully accesible via mobile 

## [0.2.1] - 2023-10-26
### Features
- Add this changelog to repo. Format based on [Keep a Changelog](http://keepachangelog.com/)

### Bug fixes
- Added ASK-chat_dummy.py and a streamlit app off of it to test streamlit mobile device issues

## [0.2.0] - 2023-10-22
Lots of changes to the user interface to better explain the service and use the screen real estate  
### Features
- Added more explanatory text
- Text explaining examples disappears after first search to make more room for results  
### Bug fixes
- Eliminated formatting errors within the detailed sources  

## [0.1.1] - 2023-10-17
### Feature adds
- Reorganized repo  
- Updated logo 

### Bug fixes
- Chat window entirely inaccessible on some mobile devices.  

### Breaking changes
- Moved logo to assets directory
- Removed Truberics feedback collector for troubleshooting streamlit code

## [0.1.0] - 2023-10-14
Pushed ASK from local to public git and streamlit cloud. ASK is public!
