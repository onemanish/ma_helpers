import streamlit as st
import pandas as pd
import pydeck as pdk

# Load UNLOCODE data
@st.cache_data
def load_data():
    # Replace this with the actual path to your UNLOCODE CSV file
    df = pd.read_csv('unlocodes.csv')
    return df

# Filter data based on search term
def filter_data(df, search_term):
    return df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]

# Main function
def main():
    st.title('UNLOCODE Explorer')

    # Load data
    df = load_data()

    # Sidebar for search
    st.sidebar.header('Search UNLOCODEs')
    search_term = st.sidebar.text_input('Enter a search term:')

    # Create a placeholder for the grid
    grid_placeholder = st.empty()

    # Create a placeholder for the map
    map_placeholder = st.empty()

    # Filter data based on search term
    filtered_df = filter_data(df, search_term)

    # Display searchable grid
    grid_placeholder.subheader('UNLOCODE Grid')
    grid_placeholder.dataframe(filtered_df)

    # Display map
    map_placeholder.subheader('UNLOCODE Map')
    
    # Create a PyDeck map
    view_state = pdk.ViewState(
        latitude=filtered_df['Latitude'].mean(),
        longitude=filtered_df['Longitude'].mean(),
        zoom=2,
        pitch=0
    )

    layer = pdk.Layer(
        'ScatterplotLayer',
        data=filtered_df,
        get_position='[Longitude, Latitude]',
        get_color=[255, 0, 0, 160],
        get_radius=100000,
        pickable=True
    )

    tooltip = {
        "html": "<b>UNLOCODE:</b> {UNLOCODE}<br><b>Name:</b> {Name}<br><b>Country:</b> {Country}",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }

    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip
    )

    map_placeholder.pydeck_chart(r)

if __name__ == '__main__':
    main()
```

The key changes in this updated version are:

1. We've moved the filtering logic into a separate function `filter_data()`.

2. We've created placeholder elements for both the grid and the map using `st.empty()`. This allows us to update these elements dynamically as the user types.

3. The filtering and updating of the grid and map now happen immediately after the search term is entered, providing a search-as-you-type experience.

To use this code:

1. Make sure you have the required libraries installed:
   ```
   pip install streamlit pandas pydeck
   ```

2. Prepare your UNLOCODE data as before, with a CSV file containing at least these columns: 'UNLOCODE', 'Name', 'Country', 'Latitude', and 'Longitude'.

3. Save the code in a file named `unlocode_explorer.py`.

4. Run the Streamlit app:
   ```
   streamlit run unlocode_explorer.py
   ```

This updated version will provide a more responsive search experience. As the user types in the search box, the grid and map will update in real-time to show only the matching results.

Would you like me to explain any part of this code in more detail or make any further modifications?​​​​​​​​​​​​​​​​