import streamlit as st
import geocoder
import pydeck as pdk

# Título da página
st.title('Localizador de Localização')

# Lista para armazenar localizações salvas
saved_locations_file = 'saved_locations.txt'

# Função para obter localização atual do usuário
def get_user_location():
    try:
        g = geocoder.ip('me')
        if g.ok:
            return g.latlng[0], g.latlng[1]
        else:
            return None, None
    except Exception as e:
        st.error(f"Erro ao obter localização: {e}")
        return None, None

# Obtendo localização atual do usuário ao iniciar o site
latitude, longitude = get_user_location()

# Criando dados para o marcador da localização atual
current_marker_data = [{"latitude": latitude, "longitude": longitude, "name": "Minha Localização"}] if latitude is not None and longitude is not None else []

# Carregando localizações salvas do arquivo
saved_marker_data = []
try:
    with open(saved_locations_file, 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            if len(parts) >= 3:
                lat, lon, name = float(parts[0]), float(parts[1]), ','.join(parts[2:])
                saved_marker_data.append({"latitude": lat, "longitude": lon, "name": name})
except FileNotFoundError:
    pass

# Combinando dados de marcadores atuais e salvos
marker_data = current_marker_data + saved_marker_data

if marker_data:
    # Definindo a visualização inicial do mapa
    view_state = pdk.ViewState(latitude=latitude, longitude=longitude, zoom=12, bearing=0, pitch=45)

    # Criando a camada de marcadores com tooltip
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=marker_data,
        get_position=["longitude", "latitude"],
        get_radius=200,
        get_fill_color=[255, 0, 0],
        pickable=True,
        auto_highlight=True,
        tooltip={"html": "<b>{name}</b>"}
    )

    # Criando o mapa interativo com pydeck
    map = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/light-v9"
    )

    # Exibindo o mapa no Streamlit
    st.pydeck_chart(map)

    # Preenchendo o endereço com a latitude e longitude na barra lateral
    address_input = st.sidebar.text_input('Digite seu endereço (ex: "São Paulo, Brasil")', f'{latitude}, {longitude}', key='address_input')

    # Botão para salvar a localização atual do usuário
    location_name = st.sidebar.text_input('Nomeie o marcador:', key='location_name_input')
    if st.sidebar.button('Salvar Localização') and location_name.strip():
        if latitude is not None and longitude is not None:
            # Salvando localização no arquivo de localizações salvas
            with open(saved_locations_file, 'a') as file:
                file.write(f'{latitude},{longitude},{location_name.strip()}\n')
            st.sidebar.success('Localização salva com sucesso!')

else:
    st.warning("Localização não encontrada. Verifique se a geolocalização está ativada.")

# Mostrando localizações salvas no sidebar
if marker_data:
    st.sidebar.header('Localizações Salvas')
    for i, loc in enumerate(marker_data, 1):
        st.sidebar.write(f"Localização {i}: {loc['name']} - Latitude: {loc['latitude']}, Longitude: {loc['longitude']}")
else:
    st.sidebar.info('Nenhuma localização foi salva ainda.')
