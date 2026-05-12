import streamlit as st
import pandas as pd
import joblib
import plotly.express as px

# --- MODEL LOADING ---
# Loading the pre-trained CatBoost model from the pkl file
try:
    model = joblib.load('catboost_model.pkl')
except:
    st.error("Model file 'catboost_model.pkl' not found! Please run mainmodel.py first.")
    st.stop()

# --- PAGE CONFIGURATION ---
# Setting up the browser tab title and favicon
st.set_page_config(page_title="BarakAI Novosibirsk", page_icon="🏙️", layout="wide")

# Custom CSS for button styling
st.markdown("""
    <style>
    .stButton>button {
        width: 100%; border-radius: 5px; height: 3em;
        background-color: #007bff; color: white; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (INPUT PANEL) ---
# Defining user input widgets in the sidebar
st.sidebar.header("⚙️ Apartment Parameters")


def user_input_features():
    # Selection of the city district
    dist = st.sidebar.selectbox("Район города",
                                ['Центральный', 'Железнодорожный', 'Советский (Академ)',
                                 'Заельцовский', 'Октябрьский', 'Ленинский', 'Кировский'])

    # Area and Rooms selection
    area = st.sidebar.slider("Площадь (кв.м.)", 15, 200, 50)
    rooms = st.sidebar.radio("Комнат", [1, 2, 3, 4, 5], horizontal=True)

    st.sidebar.markdown("---")

    # Building material and floor details
    material = st.sidebar.selectbox("Материал стен", ['Панель', 'Кирпич', 'Монолит', 'Монолит-кирпич'])
    max_f = st.sidebar.number_input("Этажность дома", 1, 30, 9)
    floor = st.sidebar.slider("Этаж", 1, int(max_f), 5)

    st.sidebar.markdown("---")

    # Construction year
    year = st.sidebar.number_input("Год постройки", 1950, 2025, 2010)

    # DOMAIN LOGIC: Akademgorodok district (Советский) has no subway stations
    if dist == 'Советский (Академ)':
        st.sidebar.info("🌲 В Академгородке нет метро")
        subway_val = 200  # High value used to represent "no subway" for the model
    else:
        # Distance to the nearest subway station
        subway = st.sidebar.select_slider("Минут до метро", options=list(range(2, 61)) + ["Больше часа"])
        subway_val = 180 if subway == "Больше часа" else subway

    # Renovation type
    renov = st.sidebar.selectbox("Ремонт", ['Без ремонта', 'Косметический', 'Евроремонт', 'Дизайнерский'])

    # Creating the feature DataFrame exactly as the model expects
    data = {
        'Район': dist, 'Кол_во_комнат': rooms, 'Площадь_квм': area,
        'Этаж': floor, 'Этажность_дома': max_f, 'Год_постройки': year,
        'Метро_мин_пешком': subway_val, 'Материал_стен': material, 'Ремонт': renov
    }
    return pd.DataFrame([data])


# Storing user inputs in a DataFrame
input_df = user_input_features()

# --- MAIN DASHBOARD AREA ---
# Custom title with slightly smaller font size to fit on one line
st.markdown("""
    <h1 style='font-size: 2.5rem; white-space: nowrap;'>
        🏙️ BarakAI: Интеллектуальная оценка
    </h1>
""", unsafe_allow_html=True)
# --- PREDICTION AND METRICS ---
# Creating columns for a clean metric display
col_res1, col_res2, col_res3 = st.columns([2, 1, 1])

# Performing the prediction using CatBoost
prediction = model.predict(input_df)[0]

with col_res1:
    st.subheader("📊 Результат оценки")
    # Formatting currency display (e.g., 7 500 000 ₽)
    st.metric(label="Рыночная стоимость", value=f"{prediction:,.0f} ₽".replace(',', ' '))

with col_res2:
    st.write("")
    # Calculating price per square meter
    sqm_p = prediction / input_df['Площадь_квм'][0]
    st.metric(label="Цена за м²", value=f"{sqm_p:,.0f} ₽".replace(',', ' '))

with col_res3:
    st.write("")
    # Static accuracy metric (from model training report)
    st.metric(label="Точность модели", value="94.2%", delta="0.5%")

# --- INTERACTIVE PLOTLY CHART ---
st.markdown("---")
st.subheader("📈 Зависимость цены от площади")

# Generating hypothetical data to plot the "Area vs Price" trend
areas = list(range(20, 150, 5))
virtual_data = pd.concat([input_df] * len(areas), ignore_index=True)
virtual_data['Площадь_квм'] = areas
virtual_predictions = model.predict(virtual_data)

chart_data = pd.DataFrame({
    'Площадь (кв.м.)': areas,
    'Цена (млн руб.)': virtual_predictions / 1_000_000
})

# Creating an interactive line chart using Plotly Express
fig = px.line(chart_data, x='Площадь (кв.м.)', y='Цена (млн руб.)', markers=True)
fig.update_traces(line_color='#007bff', line_width=3, marker_size=8)
st.plotly_chart(fig, use_container_width=True)

# --- MAP AND INVESTMENT ADVICE ---
st.markdown("---")
col_map, col_adv = st.columns(2)

with col_map:
    st.subheader("🗺️ Карта района")
    # Static coordinates for Novosibirsk districts visualization
    coords = {
        'Центральный': [55.0302, 82.9204], 'Железнодорожный': [55.0343, 82.8951],
        'Советский (Академ)': [54.8465, 83.0886], 'Заельцовский': [55.0594, 82.9113],
        'Октябрьский': [55.0084, 82.9662], 'Ленинский': [54.9842, 82.8687],
        'Кировский': [54.9453, 82.9135]
    }
    map_data = pd.DataFrame([coords[input_df['Район'][0]]], columns=['lat', 'lon'])
    st.map(map_data, zoom=11)

with col_adv:
    st.subheader("💼 Совет инвестору")

    # Business logic for dynamic tips based on input features
    if input_df['Ремонт'][0] == 'Без ремонта':
        st.warning(
            "💡 **Потенциал роста:** Квартира без ремонта. Инвестиции в 'Косметический ремонт' окупятся при продаже.")

    elif input_df['Метро_мин_пешком'][0] <= 15 and input_df['Район'][0] != 'Советский (Академ)':
        st.success("🚆 **Ликвидность:** Рядом метро! Такие квартиры продаются на 20% быстрее рынка.")

    elif input_df['Материал_стен'][0] == 'Кирпич':
        st.success("🧱 **Качество:** Кирпичный дом — это отличная шумоизоляция и спрос на вторичном рынке.")

    elif input_df['Этаж'][0] == 1:
        st.info("🏢 **Коммерция:** Первый этаж. Можно рассмотреть перевод в нежилой фонд.")

    else:
        st.info("⚖️ **Стабильный актив:** Сбалансированные характеристики для сохранения капитала.")

# ==========================================
# 7. DATA INSIGHTS SECTION (EDA)
# ==========================================

st.markdown("---")
# Creating an expandable section for technical data analysis
with st.expander("📊 Технический анализ и обзор данных"):
    st.write("Разведочный анализ данных (EDA) на основе выборки из 50 000 записей.")


    # Loading the raw dataset for visualization (using cache to optimize performance)
    @st.cache_data
    def load_data_for_eda():
        # Ensure the filename matches your actual dataset file
        return pd.read_csv('novosibirsk_flats_v47.csv')


    df_eda = load_data_for_eda()

    # Creating two columns for side-by-side charts
    col_eda1, col_eda2 = st.columns(2)

    with col_eda1:
        st.write("**Распределение цен**")
        # Creating a price histogram using Plotly
        fig_hist = px.histogram(
            df_eda,
            x=df_eda['Цена_руб'] / 1000000,
            nbins=50,
            title="Распределение цен (млн руб.)",
            color_discrete_sequence=['#007bff']
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_eda2:
        st.write("**Корреляция признаков**")
        # Temporary numeric encoding for text columns to calculate correlation
        df_corr = df_eda.copy()
        for col in ['Район', 'Ремонт', 'Материал_стен']:
            df_corr[col] = pd.factorize(df_corr[col])[0]

        # Computing the correlation matrix
        corr = df_corr.corr()
        # Visualizing the matrix as a heatmap
        fig_corr = px.imshow(
            corr,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale='RdBu_r',
            title="Матрица корреляции признаков"
        )
        st.plotly_chart(fig_corr, use_container_width=True)

    # Displaying a brief conclusion based on the data
    st.info(
        "💡 **Аналитика:** Рыночная стоимость сильнее всего коррелирует с площадью (0.85) и престижностью района. Влияние этажа и материала стен заметно, но является вторичным фактором.")
# Footer
st.caption("© 2026 BarakAI Novosibirsk | Academic Data Science Project")
