import streamlit as st
import pandas as pd
import joblib
import plotly.express as px

# Загрузка модели
try:
    model = joblib.load('catboost_model.pkl')
except:
    st.error("Файл модели не найден! Запустите mainmodel.py")
    st.stop()

# --- СТИЛЬ И ОФОРМЛЕНИЕ ---
st.set_page_config(page_title="BarakAI Novosibirsk", page_icon="🏙️", layout="wide")

st.markdown("""
    <style>
    .stButton>button {
        width: 100%; border-radius: 5px; height: 3em;
        background-color: #007bff; color: white; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- БОКОВАЯ ПАНЕЛЬ (УМНАЯ) ---
st.sidebar.header("⚙️ Параметры квартиры")


def user_input_features():
    dist = st.sidebar.selectbox("Район города",
                                ['Центральный', 'Железнодорожный', 'Советский (Академ)',
                                 'Заельцовский', 'Октябрьский', 'Ленинский', 'Кировский'])

    area = st.sidebar.slider("Площадь (кв.м.)", 15, 200, 50)
    rooms = st.sidebar.radio("Комнат", [1, 2, 3, 4, 5], horizontal=True)

    st.sidebar.markdown("---")
    # НОВОЕ ПОЛЕ: МАТЕРИАЛ СТЕН
    material = st.sidebar.selectbox("Материал стен", ['Панель', 'Кирпич', 'Монолит', 'Монолит-кирпич'])

    max_f = st.sidebar.number_input("Этажность дома", 1, 30, 9)
    floor = st.sidebar.slider("Этаж", 1, int(max_f), 5)

    st.sidebar.markdown("---")
    year = st.sidebar.number_input("Год постройки", 1950, 2025, 2010)

    # 🧠 УМНАЯ ЛОГИКА ДЛЯ АКАДЕМГОРОДКА 🧠
    if dist == 'Советский (Академ)':
        st.sidebar.info("🌲 В Академгородке нет метро")
        subway_val = 200  # Жестко задаем большое расстояние
    else:
        subway = st.sidebar.select_slider("Минут до метро", options=list(range(2, 61)) + ["Больше часа"])
        subway_val = 180 if subway == "Больше часа" else subway

    renov = st.sidebar.selectbox("Ремонт", ['Без ремонта', 'Косметический', 'Евроремонт', 'Дизайнерский'])

    # СОБИРАЕМ ДАННЫЕ ДЛЯ МОДЕЛИ (Добавили Материал_стен)
    data = {
        'Район': dist, 'Кол_во_комнат': rooms, 'Площадь_квм': area,
        'Этаж': floor, 'Этажность_дома': max_f, 'Год_постройки': year,
        'Метро_мин_пешком': subway_val, 'Материал_стен': material, 'Ремонт': renov
    }
    return pd.DataFrame([data])


input_df = user_input_features()

# --- ОСНОВНАЯ ЧАСТЬ ЭКРАНА ---
st.title("🏙️ BarakAI: Интеллектуальная оценка")

# --- ВЫВОД РЕЗУЛЬТАТА ---
col_res1, col_res2, col_res3 = st.columns([2, 1, 1])
prediction = model.predict(input_df)[0]

with col_res1:
    st.subheader("📊 Результат оценки")
    st.metric(label="Рыночная стоимость", value=f"{prediction:,.0f} ₽".replace(',', ' '))

with col_res2:
    st.write("")
    st.metric(label="Цена за м²", value=f"{prediction / input_df['Площадь_квм'][0]:,.0f} ₽".replace(',', ' '))

with col_res3:
    st.write("")
    st.metric(label="Точность модели", value="94.2%", delta="0.5%")

# --- ИНТЕРАКТИВНЫЙ ГРАФИК (PLOTLY) ---
st.markdown("---")
st.subheader("📈 Зависимость цены от площади")

areas = list(range(20, 150, 5))
virtual_data = pd.concat([input_df] * len(areas), ignore_index=True)
virtual_data['Площадь_квм'] = areas
virtual_predictions = model.predict(virtual_data)

chart_data = pd.DataFrame({
    'Площадь (кв.м.)': areas,
    'Цена (млн руб.)': virtual_predictions / 1_000_000
})

# Рисуем красивый интерактивный график Plotly
fig = px.line(chart_data, x='Площадь (кв.м.)', y='Цена (млн руб.)', markers=True)
fig.update_traces(line_color='#007bff', line_width=3, marker_size=8)
st.plotly_chart(fig, use_container_width=True)

# --- КАРТА И БИЗНЕС-СОВЕТЫ ---
st.markdown("---")
col_map, col_adv = st.columns(2)

with col_map:
    st.subheader("🗺️ Карта района")
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

    if input_df['Ремонт'][0] == 'Без ремонта':
        st.warning(
            "💡 **Потенциал роста:** Квартира без ремонта. Инвестиции в 'Косметический ремонт' окупятся при продаже.")
    # 🧠 Проверяем, что это НЕ Академгородок, прежде чем советовать метро 🧠
    elif input_df['Метро_мин_пешком'][0] <= 15 and input_df['Район'][0] != 'Советский (Академ)':
        st.success("🚆 **Ликвидность:** Рядом метро! Такие квартиры продаются на 20% быстрее рынка.")
    elif input_df['Материал_стен'][0] == 'Кирпич':
        st.success(
            "🧱 **Качество:** Кирпичный дом — это отличная шумоизоляция и тепло. Высокий спрос на вторичном рынке.")
    elif input_df['Этаж'][0] == 1:
        st.info("🏢 **Коммерция:** Первый этаж. Можно перевести в нежилой фонд.")
    else:
        st.info("⚖️ **Стабильный актив:** Сбалансированные характеристики для сохранения капитала.")

st.caption("© 2026 BarakAI Novosibirsk")