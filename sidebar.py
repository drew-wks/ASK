# sidebar.py
import streamlit as st
import ui_utils

__all__ = ["build_sidebar"]          # so autoflake/ruff know what’s public

def build_sidebar():
    """Draw the ASK sidebar and return the current filter_conditions dict."""  

    st.sidebar.markdown("#### Experimental\n\n  The following features are experimental and may not work as expected.\n\n")
    
    include_d7      = st.sidebar.checkbox("Include District 7 documents in results")
    
    exclude_expired = st.sidebar.checkbox("Exclude expired documents", value=False)
    st.sidebar.caption("This excludes all Commandant Instructions issued more than 12 years ago (including AUXMAN) as well as ALCOASTs and ALAUXs issued more than one year ago, per COMDTINST 5215.6J.\n\n")

    filter_conditions = {"public_release": True}
    if exclude_expired:
        filter_conditions["exclude_expired"] = True

    if include_d7:
        filter_conditions.update({"scope": "District", "unit": "7"})
    else:
        filter_conditions["scope"] = "national"

    # st.sidebar.write("Current filter_conditions:", filter_conditions)
    return filter_conditions