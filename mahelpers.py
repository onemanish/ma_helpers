import streamlit as st

st.set_page_config(
    page_title='My Streamlit App',
    page_icon='🧊',
    layout='wide'
)

st.sidebar.header('MA Helpers')
selOpt = st.sidebar.radio('Choose Helper', ['Quote Maker', 'UN/LO Code display', 'BiVar Report'])

match selOpt:
    case 'Quote Maker':
        import maquotemaker as mq
        mq.quote_maker()
    case 'UN/LO Code display':
        import unlodisp


