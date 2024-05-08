import streamlit as st
import folium
from streamlit_folium import folium_static
import geocoder

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

# Criando um mapa com folium
m = folium.Map(location=[0, 0], zoom_start=2)  # Mapa inicial com zoom baixo

# Carregando localizações salvas do arquivo
def load_saved_locations():
    saved_locations = []
    try:
        with open(saved_locations_file, 'r') as file:
            for line in file:
                parts = line.strip().split(',')
                if len(parts) >= 3:
                    latitude, longitude = float(parts[0]), float(parts[1])
                    name = ','.join(parts[2:])
                    saved_locations.append((latitude, longitude, name))
    except FileNotFoundError:
        pass  # Arquivo ainda não existe

    return saved_locations

st.session_state.saved_locations = load_saved_locations()

# Obtendo localização atual do usuário ao iniciar o site
latitude, longitude = get_user_location()

if latitude is not None and longitude is not None:
    # Adicionando marcador da localização atual
    folium.Marker(
        location=[latitude, longitude],
        popup='Minha Localização',
        icon=folium.Icon(icon='cloud')
    ).add_to(m)

    # Definindo a localização inicial do mapa para a localização atual
    m.location = [latitude, longitude]
    m.zoom_start = 12  # Ajusta o zoom para a localização atual

    # Preenchendo o endereço com a latitude e longitude na barra lateral
    address_input = st.sidebar.text_input('Digite seu endereço (ex: "São Paulo, Brasil")', f'{latitude}, {longitude}', key='address_input')
else:
    st.warning("Localização não encontrada. Verifique se a geolocalização está ativada.")

# Botão para obter a localização atual do usuário
if st.button('Atualizar Localização', key='update_location_button'):
    latitude, longitude = get_user_location()

    if latitude is not None and longitude is not None:
        # Atualizando marcador da localização atual no mapa
        folium.Marker(
            location=[latitude, longitude],
            popup='Minha Localização',
            icon=folium.Icon(icon='cloud')
        ).add_to(m)

        # Atualizando localização do mapa para a localização atual
        m.location = [latitude, longitude]
        m.zoom_start = 12  # Ajusta o zoom para a localização atual

        # Atualizando o valor da variável associada ao text_input com a nova localização
        address_input = f'{latitude}, {longitude}'  # Atualiza a variável, não o widget

    else:
        st.warning("Localização não encontrada. Verifique se a geolocalização está ativada.")

# Campo de texto para nomear o marcador ao salvar a localização
location_name = st.sidebar.text_input('Nomeie o marcador:', key='location_name_input')

# Botão para salvar a localização atual do usuário
if st.button('Salvar Localização', key='save_location_button') and location_name.strip():
    if latitude is not None and longitude is not None:
        # Adicionando localização à lista de localizações salvas
        st.session_state.saved_locations.append((latitude, longitude, location_name.strip()))
        st.success('Localização salva com sucesso!')

        # Salvando localizações no arquivo de texto
        with open(saved_locations_file, 'a') as file:
            file.write(f'{latitude},{longitude},{location_name.strip()}\n')

# Exibindo localizações salvas no mapa
for loc in st.session_state.saved_locations:
    folium.Marker(
        location=[loc[0], loc[1]],
        popup=loc[2],  # Usando o nome como descrição do marcador
        icon=folium.Icon(icon='star', color='green')
    ).add_to(m)

# Exibindo o mapa com todas as localizações no Streamlit
folium_static(m)

# Mostrando localizações salvas no sidebar
if st.session_state.saved_locations:
    st.sidebar.header('Localizações Salvas')
    for i, loc in enumerate(st.session_state.saved_locations):
        st.sidebar.write(f"Localização {i+1}: {loc[2]} - Latitude: {loc[0]}, Longitude: {loc[1]}")
else:
    st.sidebar.info('Nenhuma localização foi salva ainda.')
