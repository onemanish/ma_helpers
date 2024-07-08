import pandas as  pd
import openpyxl, folium, os
from haversine import haversine, Unit, haversine_vector
import streamlit as st
from streamlit_folium import st_folium

# This app reads a master list of UN/LO Codes downloaded from the UNECE website
# and shows the location of the nearest UNLOC positions from own position to select suitable 
# position for reporting. (c) Manish Srivastava 04 2024 / open source

@st.cache_data
def get_unlocodes(): # split the coords col to Lat Long and convert to decimal
    df = pd.read_excel(os.path.join('ref-files','UNLOCODECodeList.xlsx')) # read the date file with UNLO Codes
    dfDNV = pd.read_excel(os.path.join('ref-files','DNVUNLOCODES.xlsx'))
    print('read the master data')
    
    def deg2dec(degVal):
        # print(degVal, end = "|")
        if degVal!='nan' or degVal != '' or degVal == 0:
            direction = degVal[-1]  # Extract the direction ('N' or 'S')
            degVal = degVal[:-1]  # Remove the direction
            degrees = int(degVal[:-2])  # Extract the degrees part
            minutes = int(degVal[-2:])  # Extract the minutes part
            decDeg = degrees + (minutes / 60)
            if direction == 'S' or direction == 'W':
                decDeg *= -1  # If direction is S or W, make decimal degrees negative
            return decDeg
        return 0
    # st.write(dfDNV)

    df['UNLOCode'] = df['Country'] + df['Location']
    df.dropna(subset=['Coordinates'], inplace=True) # throw out rows without Lat/Long info
    df.drop(columns=['Country', 'Date', 'Location','Change','IATA', 'Remarks', 'Subdivision', 'Status', 'NameWoDiacritics'], inplace=True)
    df['InDNV'] = df['UNLOCode'].isin(dfDNV['Port Code']).map({True:'Y', False:''}) # Check whether the codes exists in DNV db or not
    df['Lat'] = df['Coordinates'].str.split().str[0].apply(deg2dec)
    df['Long'] = df['Coordinates'].str.split().str[1].apply(deg2dec)
    return df, dfDNV

# Filter data based on search term
def filter_data(df, search_term):
    return df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]

# print('------ start --------')
def showCodes():
    col1, col2 = st.columns([3,4])
    # vLat = 40.0 #col1.number_input('My Latitude (use -ve decimal for S)', min_value=-90.0, max_value=90.0, value=19.0)
    # vLong = 0.0 # col1.number_input('My Longitude (use -ve decimal for W)', min_value=-180.0, max_value=180.0, value=72.5)
    
    # Initialize session state variables for latitude and longitude
    if 'vlat' not in st.session_state:
        st.session_state['vlat'] = 40.0
    if 'vlong' not in st.session_state:
        st.session_state['vlong'] = 0.0
    if 'mapZoom' not in st.session_state:
        st.session_state['mapZoom'] = 10
    
    
    vLat = st.session_state['vlat']
    vLong = st.session_state['vlong']
    mapZoom = st.session_state['mapZoom']
    st.write(f'{vLat}  {vLong}')


    vCircle = col1.number_input('Draw Circle Around Me (NM)', value=20)
    diff = col1.number_input('Show UN/LO Codes around (º)', value=1.0)
    # mapZoom = col1.number_input('Map zoom', value=5)

    df1, dfDNV1 = get_unlocodes()
    col2.markdown(f"**DNV** UNLO Code List with {len(dfDNV1)} entries")
    col2.write(dfDNV1)

    sel_df = df1[(df1['Lat'] >= vLat - diff) & (df1['Lat'] <= vLat + diff)] # remove all points diff deg far from my location
    sel_df = sel_df[(sel_df['Long'] >= vLong - diff) & (sel_df['Long'] <= vLong + diff)] # remove all points diff º far from my location

    def get_distance(row):
        return haversine((row['Lat'], row['Long']), (vLat, vLong), unit=Unit.NAUTICAL_MILES)
    
    sel_df['Distance'] = sel_df.apply(get_distance, axis=1) # Add column for distances 
    sel_df = sel_df.sort_values(by='Distance')
    sel_df.reset_index(drop=True, inplace=True) # to be able to address each point sequentially
    st.error(f'{len(sel_df)} UN/LO Code locations found within {diff}º from my position ({vLat}º, {vLong}º).\n \
        in UN database with Lat/Long Positions')
    # st.write(sel_df)
    styled_df = sel_df.style.apply(lambda x: ["background-color: pink" if val == "Y" else "" for val in x], axis=1)
    styled_df = styled_df.format("{:.2f}", subset=pd.IndexSlice[:, ["Lat", 'Long','Distance']])
    
    # st.error('Following UN/LO Codes in UN database with Lat/Long Positions')
    st.dataframe(styled_df)
    
    # set up map and add markers
    m = folium.Map(location=[vLat, vLong], tiles="OpenStreetMap", zoom_start=mapZoom)
    folium.Marker(location=[vLat, vLong], tooltip=folium.Tooltip('I am here!'), icon=folium.Icon(color='orange')).add_to(m)
    folium.Circle(location=[vLat, vLong], radius=vCircle*1852, color="black", weight=1, \
        opacity=1, fill_opacity=0.2, fill_color="green", fill=False, tooltip=f"{vCircle}NM").add_to(m)

    for i in range(0,len(sel_df)):
        Distance = haversine((vLat,vLong), (sel_df.iloc[i]['Lat'], sel_df.iloc[i]['Long']), unit=Unit.NAUTICAL_MILES)
        folium.Marker(location=[sel_df.iloc[i]['Lat'], sel_df.iloc[i]['Long']],
          tooltip=f"{sel_df.iloc[i]['Name']} - {sel_df.iloc[i]['UNLOCode']} - {sel_df.iloc[i]['Distance']:0.1f}NM away",
          icon=folium.Icon(color='red' if sel_df.iloc[i]['InDNV'] == 'Y' else 'darkgreen'),
       ).add_to(m)

    st_data = st_folium(m, use_container_width=True, height=400)
    selData = st_data['last_object_clicked_tooltip']
    st.warning(selData)
    lastClicked = st_data['last_clicked']
   
    if lastClicked:
        vLat = lastClicked['lat']
        vLong = lastClicked['lng']
    # st.info(f'{lastLat} {lastLong}')
    # st.error(f'{vLat} {vLong} \n {st_data}')
    # if selData != None:
    #     selData = "  --  ".join(st_data['last_object_clicked_tooltip'].split('-'))
    #     # st.sidebar.error(f"{selData}")

    # st_data = st_folium(m, width=700, height=500)

    if st_data and "last_clicked" in st_data:
        click_location = st_data["last_clicked"]

        st.session_state['vlat'] = click_location['lat']
        st.session_state['vlong'] = click_location['lng']
        
        # st.write("You clicked at:", click_location)


    # Display stored coordinates from session state
    # if st.session_state['vlat'] is not None and st.session_state['vlong'] is not None:
        vLat = st.session_state['vlat']
        vLong = st.session_state['vlong']
        st.write(f'{vLat}  {vLong}')

if __name__ == '__main__':
    showCodes()