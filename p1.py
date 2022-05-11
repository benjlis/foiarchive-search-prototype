import streamlit as st
import plotly.express as px
import pandas as pd
import psycopg2


VERSION = 'v0.1'
TITLE = f'FOIArchive Search Prototype ({VERSION})'
st.set_page_config(page_title=TITLE, layout="wide")
st.title(TITLE)
st.markdown('Learn more about the FOIArchive \
[Collections](http://history-lab.org/analytics).')


# Initialize database connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])


conn = init_connection()


title = st.text_input(label='',
                      placeholder='Search for person, event, place, topic')


doc_dist_qry = "select extract(year from authored)::integer yr, corpus collection," + \
                       "count(*) doccnt from foiarchive.docs " + \
                       f"where full_text @@ websearch_to_tsquery('english', '{title}')" + \
                       " group by yr, corpus order by yr, doccnt"
doc_dist_df = pd.read_sql_query(doc_dist_qry, conn)
fig = px.bar(doc_dist_df, x='yr', y='doccnt', color='collection',
             labels={'yr': 'Year',
                     'doccnt': 'Number of Documents',
                     'collection': 'Collections:'})
fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))
st.plotly_chart(fig, use_container_width=True)
st.table(doc_dist_df)

# Perform query.
# Uses to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()
