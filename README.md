![Logo](https://raw.githubusercontent.com/dvvilkins/ASK/main/images/ASK_logotype_color.png?raw=true)

**Auxiliary Source of Knowledge (ASK)** was developed by U.S. Coast Guard Auxiliarist Drew Wilkins as a proof of concept to make it easier for Auxiliarists and prospective members to find Auxiliary-related information. ASK utilizes Retrieval Augmented Generation to search over 300 Coast Guard Auxiliary references to find answers directly from authoritative sources.

## Background
ASK stems from the need for easier ways to find official information. Being a member of the U.S. Coast Guard, Auxiliarists are surrounded by vast amounts of policy and procedure information that guides their actions.

However, that bulk of that information is stowed away in PDFs scattered across various platforms, making it cumbersome to located and search. Furthermore, outdated and regionally-specific documents can be misconstrued as applicable. Web searches yield thousands of documents, but it is difficult to know which one applies. Tools like Chat GPT might provide inaccurate data or even fabricate responses.

ASK is different. It examines the documents themselves, and then uses AI to answer them in natural language. ASK works by analyzing documents that are the most current official policy that exists at a national level. Its library contains over 238 policy documents (over 8000 pages)— from Commandant Instructions to ALAUXs to national workshops—managed in a central location. Scope is limited to publicly-available, national documents, so it doesn’t include information behind firewall or specific to individual districts, sectors, divisions, etc. That way, even applicants can use it without authentication.

## Mission 
ASK's mission is to provide members efficient, accurate, and easy access  to the authoritative source of knowledge on any topic in the Auxiliary.

## Access
ASK is available to try [here](https://uscg-auxiliary-ask.streamlit.app/) <br>
<a href="https://uscg-auxiliary-ask.streamlit.app/"><img align="center" src="https://raw.githubusercontent.com/dvvilkins/ASK/main/images/what_is_the_aux_screenshot.png" alt="library ui" width="80%" align="center"/></a>

## Uses

  - **Policy Compliance:** ASK can assist members fulfill their responsibilities to understand and adhere to policy, and help the organization transition to new policies. For example, a member can find the policy changes affecting their competency.

 - **New Member Onboarding:** ASK can help new members integrate into the Auxiliary. For example, a new member can ask questions that might make them “feel stupid” to ask in person. A supportive and informative “first ninety days” sets the foundation for a productive and engaged member.

 - **Training Support:** ASK provides personalized learning for trainees. It can compare and contrast terms or create custom quizzes, with ASK grading the results

 - **In-the-Field Mission Support:** ASK facilitates instant, on-the-go access to crucial documents during mission execution, enhancing Auxiliarist performance efficiency and decision-making. It can create checklists and provide Quick information retrieval. For example, an AUX Culinary Assistant could immediately determine all the currency requirements for the competency.

 - **Language Access:** ASK can assist the US Coast Guard in fulfilling its requirements under Executive Order 13166, _“Improving Access to Services for Persons with Limited English Proficiency”_ by detecting language automatically and translate both question and responses in real time


## How it Works
### Generative AI Document Search
Generative AI Document Search brings together two capabilities of Artificial Intelligence (AI): the powerful information **retrieval** of a search engine with **text generation** ability of a Generative AI operating within a controlled organizational environment. Generative AI Document Search overcomes limitations of both by utilizing retrieved information from existing data, ensuring that the answers provided are not only contextually appropriate but also substantiated by credible sources. It works by taking a user’s question from a search bar, retrieving related information from a pre-defined library of USCG reference documents, and then generating a detailed response back to the user that includes the source citations.
<br><br>
<a href="https://uscg-auxiliary-ask.streamlit.app/"><img align="center" src="https://raw.githubusercontent.com/dvvilkins/ASK/main/images/rag_flow_detail.png" alt="low" width="90%" align="center"/></a>

## Document Library
ASK is loaded with over 250 national documents (over 8000 pages). The app includes a searchable list of documents in its information section. Click image to visit.<br><br>
<a href="https://uscg-auxiliary-ask.streamlit.app/Library#library-overview"><img align="center" src="https://raw.githubusercontent.com/dvvilkins/ASK/main/images/library_ui.png" alt="library ui" width="60%"/></a>


## Document Library
ASK is loaded with over 250 national documents (over 8000 pages). The app includes a searchable list of documents in its information section.![library search](https://raw.githubusercontent.com/dvvilkins/ASK/main/images/library_ui.png?raw=true)


## Data Flow
The data flow model is below. <br><br>
<img align="center" src="https://raw.githubusercontent.com/dvvilkins/ASK/main/images/data_flow_diagram.png" alt="low" width="80%" align="center"/></a>  


## Technology Components

ASK relies on five core components: a python codebase, a Gen AI model, vector database, a runtime environment, and a Web app server. It has been designed to take advantage of open-source to allow continued innovation and to keep costs low.

The main components of the solution are:

  - **Codebase**: written by me in Python 3.8.10 using open source licenses. Version control is via a public git repository located at _https://github.com/dvvilkins/Webapp1_

- **Embedding model**: Embeddings are generated using OpenAI Ada v.2 which is providing state of the art (SOTA) embeddings at the time of this writing. The model is accessed from the code via API. Alternatives exist and may provide superior results or same for less cost. More on this embedding can be found here: https://platform.openai.com/docs/guides/embeddings/what-are-embeddings

- **Storage**: Qdrant open-source vector database cluster hosted on AWS. The proof of concept utilizes 300 MB of file storage (186 MB payload of pdfs plus 100 MB for the vectors, metadata, index and swap files). The recommended configuration is for 600 MB to hold all policy documents in the Auxiliary.

- **Inference model**: OpenAI ChatGPT 3.5 series via API. Chat history is currently turned off as it doesn’t seem to be needed and minimizes per-request costs. More information on this API is located at https://platform.openai.com/docs/guides/gpt/chat-completions-api

- **Runtime environment, Web app server, front end:** All provided by Streamlit framework and cloud turns the Python script by rendering it as a web app.

Two additional components simplify system development and management:

- **LangChain**: An open-source integration framework for Gen AI models which integrates the components in the Gen AI pipeline and makes it easy to change the ingestion approach, model or vector database as requirement change or opportunities arise. This is essential since generative AI technology is advancing quickly.

- **AI Ops:** Trubrics monitoring and optimization for machine learning models. It collects the queries and responses, parameters and token usage , and direct user feedback and provides an administrative dashboard for monitoring performance.

## Configuration
The following configuration was specified for the proof of concept. This proposal recommends using it for the first-year launch of ASK. 
<br> <br>
 <img src="https://raw.githubusercontent.com/dvvilkins/ASK/main/images/configuration_table.png" alt="configuration table" width="60%"/>

## Administration
Process details for the first several stages are located [here.](https://cdn-0.plantuml.com/plantuml/png/ZLF1Qjj04BtxAuRaPcXA3xtKbpHnGmEXf2JGenZlZkL5gnrbPcH7rFttHbgbLOrTSX9evhsPUU_jfHgAjNMSQHLIWu8rhD1LfN2R_3L75Z31f2ybIZRfKdfgAJdwBCAxnqrmLI9L-73nSTBaQOrjj1jEzWrhWgyKjsJ1uMosF_-n2KOFDLUq1u3hLj1O060_6vQQDIWMB722yxjGRkoXwgvYIt1slxo1Uw5tZR0ZrP3AC_Wv0m3u53mb2-iE-XxbLXn1P8SzZIx-7VhGgL6zpq1rWWs1HqDO2zSZM24aOqYqAtB7nNFKvqN6t2xxGZzAOTM1uxf12QayR8TTi0rmz4Sui6ae-SDYHepamr9Zk-TTYep-x-39ils1NvwD964SpvhFNvgAa885ZCMBOoszdyypsMant8PSDTAp08cmw6Ai2Q4H6AuY0Q-71HFMf839Gqs6atKpKL-8N2hujed1eT70FL5WWeIAkYE7D7wjXLyNv8CLzLJ2m_1aKZzXt69iIS4OCkf_tEIdr5DL3XSTpbBS4g0ETlGqfnnu1HLzI29PTk7N9EFPZ1pksrIIzdzVStrW3pTTTiTu-1PX09mQdgjlyhrDrTGRgbVaOKlEM7Jq4Nr-4qzUC1aihuvf5RcSmlwav8X0tpDFLbU11OHoo1GSnqYkLsBn1XsAkx0IbEwK3Z6Nto34yEg230Tqu29XQXjul5hsdgbnCxkavDiw_WO0) Process details for database auditing and deleting are [here.](https://cdn-0.plantuml.com/plantuml/png/ZP5FRzD04CNl_XIZzW3aq8e3b-JIAg5mg12ebH12A9hiJkoLrpjcTZP_HFZkxCOkAYL5v13BC-_dVVlULLGKJPslOkj2Zu8ThD2qjN0ATiwU1LGmnBoYe8zKaRud2eQkHNXxtpZJ1eeHNb-yUIIojCRazOQ3Vi2Eu3tv3QapM5NLuVnpuvJkEcxf003p9AWi072eZgwggi__JXq7EBzrTQDVo7lUmjbridaSQj26O86AAunq1ZygoB-dtogpwRsukYQ9W0MT3SAxVLJgHiKxqhpr7dfsGIEiXJluP0L3bX_UxfGae1_5mno4D4auOiiHUzdZtZFQ2Bo6ZXGjAhuwTQ1foBIP3HOyrn5eusm9j80szTuPL8AFYviu6m6XF8cGWilHBoCdCPINqwsuh5I6jVCqY9yQzcubAFkbPPCw2hhqBkfNYqgNwZhwTj6tVlQVqfsFkrdrCrSObVlgkRBcBEZXR46UIbVb9cEgjyC9_ooiPA5klH-nl1BgU8F-L9IZs54iyXSHDcIKvI4uMopGE1myZ2zWLy-MEr3nJyomzsJABK_vA3qEt6_1D9iUMWJbyboYcCPjwEzpCtri47HbHtWokIpe0pEPbDolADZK-Ly0)

## Administration
Process details for the first several stages are located [here.](https://cdn-0.plantuml.com/plantuml/png/ZLF1Qjj04BtxAuRaPcXA3xtKbpHnGmEXf2JGenZlZkL5gnrbPcH7rFttHbgbLOrTSX9evhsPUU_jfHgAjNMSQHLIWu8rhD1LfN2R_3L75Z31f2ybIZRfKdfgAJdwBCAxnqrmLI9L-73nSTBaQOrjj1jEzWrhWgyKjsJ1uMosF_-n2KOFDLUq1u3hLj1O060_6vQQDIWMB722yxjGRkoXwgvYIt1slxo1Uw5tZR0ZrP3AC_Wv0m3u53mb2-iE-XxbLXn1P8SzZIx-7VhGgL6zpq1rWWs1HqDO2zSZM24aOqYqAtB7nNFKvqN6t2xxGZzAOTM1uxf12QayR8TTi0rmz4Sui6ae-SDYHepamr9Zk-TTYep-x-39ils1NvwD964SpvhFNvgAa885ZCMBOoszdyypsMant8PSDTAp08cmw6Ai2Q4H6AuY0Q-71HFMf839Gqs6atKpKL-8N2hujed1eT70FL5WWeIAkYE7D7wjXLyNv8CLzLJ2m_1aKZzXt69iIS4OCkf_tEIdr5DL3XSTpbBS4g0ETlGqfnnu1HLzI29PTk7N9EFPZ1pksrIIzdzVStrW3pTTTiTu-1PX09mQdgjlyhrDrTGRgbVaOKlEM7Jq4Nr-4qzUC1aihuvf5RcSmlwav8X0tpDFLbU11OHoo1GSnqYkLsBn1XsAkx0IbEwK3Z6Nto34yEg230Tqu29XQXjul5hsdgbnCxkavDiw_WO0) Process details for database auditing and deleting are [here.](https://cdn-0.plantuml.com/plantuml/png/ZP5FRzD04CNl_XIZzW3aq8e3b-JIAg5mg12ebH12A9hiJkoLrpjcTZP_HFZkxCOkAYL5v13BC-_dVVlULLGKJPslOkj2Zu8ThD2qjN0ATiwU1LGmnBoYe8zKaRud2eQkHNXxtpZJ1eeHNb-yUIIojCRazOQ3Vi2Eu3tv3QapM5NLuVnpuvJkEcxf003p9AWi072eZgwggi__JXq7EBzrTQDVo7lUmjbridaSQj26O86AAunq1ZygoB-dtogpwRsukYQ9W0MT3SAxVLJgHiKxqhpr7dfsGIEiXJluP0L3bX_UxfGae1_5mno4D4auOiiHUzdZtZFQ2Bo6ZXGjAhuwTQ1foBIP3HOyrn5eusm9j80szTuPL8AFYviu6m6XF8cGWilHBoCdCPINqwsuh5I6jVCqY9yQzcubAFkbPPCw2hhqBkfNYqgNwZhwTj6tVlQVqfsFkrdrCrSObVlgkRBcBEZXR46UIbVb9cEgjyC9_ooiPA5klH-nl1BgU8F-L9IZs54iyXSHDcIKvI4uMopGE1myZ2zWLy-MEr3nJyomzsJABK_vA3qEt6_1D9iUMWJbyboYcCPjwEzpCtri47HbHtWokIpe0pEPbDolADZK-Ly0)

## Costs
Estimated year one costs are given below based on the recommended configuration. Primary cost drivers are usage and storage. All costs are monthly subscriptions. There is no deployment cost since the prototype has already been built and can be moved to production using volunteers.
 <br> <br> 
 <img align="center" src="https://raw.githubusercontent.com/dvvilkins/ASK/main/images/costs.png" alt="costs" width="50%"/>

## Github Repo Contents
The streamlit app is a multi-page app with the TOC hidden. Streamlit runs off of prompt_ui.py. ASK_inference.py contains most of the retrieval and inference code.  
Efforts were taken to free up as much screen real estate as possible for small mobile screens. This includes:
  - Creating a rich info area located on a separate page of a multipage app and hiding the TOC
  - Linking to other pages with a hyperlink rather than a button that takes up vertical space
  - Adjustments to page header and footer
  - Replacing Streamlit header with st.status
  - Removing instructional text after query is submitted to make room for response (using st.empty)
    
Other features  
  - OpenAI down triggers a user warning
  - Warning is displayed if OpenAI quota is exceeded and I need to pay for more credits

Testing  
  - Primarily conducted through a separate streamlit app that accesses github.com/drew-wks/ASK/tree/test.  
  - Additional testing is conducted using /test, test.py, just_streamlit_text.py
