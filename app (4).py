
import os
import html

import requests
import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="Слепой.com",
    page_icon="🔮",
    layout="centered",
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #100d1c, #211332, #11101b);
    color: #ffffff;
}

.main-title {
    text-align: center;
    font-size: 44px;
    font-weight: 800;
    color: #d8a4ff;
    margin: 15px 0 30px 0;
}

h1, h2, h3, p, label {
    color: #f5edff !important;
}

.stButton > button {
    width: 100%;
    border: none;
    border-radius: 12px;
    background: linear-gradient(90deg, #8e44ad, #d63384);
    color: white;
    font-weight: bold;
    padding: 10px;
    transition: 0.2s;
}

.stButton > button:hover {
    border: none;
    color: white;
    filter: brightness(1.15);
}

.ai-answer {
    background: rgba(139, 92, 246, 0.15);
    border: 1px solid #8e44ad;
    border-radius: 14px;
    padding: 18px;
    margin-top: 15px;
    color: #ffffff;
    line-height: 1.7;
    overflow-wrap: anywhere;
}

.weather-card {
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(216, 164, 255, 0.35);
    border-radius: 16px;
    padding: 18px;
    margin: 12px 0;
    text-align: center;
}

.city-name {
    font-size: 22px;
    font-weight: bold;
    color: #d8a4ff;
}

.temp-big {
    font-size: 38px;
    font-weight: bold;
    color: #ffffff;
}

.condition {
    color: #d6cce5;
    font-size: 15px;
}

.disclaimer {
    color: #c5b6d9;
    font-size: 13px;
    text-align: center;
    margin-top: 20px;
}

div[data-testid="stTabs"] button {
    color: #e7d5ff;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">🔮 Слепой.com</div>',
    unsafe_allow_html=True,
)

tab1, tab2, tab3 = st.tabs([
    "🤖 ИИ",
    "🌤 Погода",
    "🔮 Спроси судьбу",
])


def ask_ai(question):
    if not API_KEY:
        return "⚠️ Ключ Gemini не найден. Проверь файл .env."

    try:
        client = genai.Client(api_key=API_KEY)

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=question,
        )

        if response.text:
            return response.text

        return "ИИ не вернул текстовый ответ. Попробуй задать вопрос ещё раз."

    except Exception as e:
        return f"❌ Ошибка: {type(e).__name__}: {e}"


def show_answer(answer):
    safe_answer = html.escape(str(answer)).replace("\n", "<br>")

    st.markdown(
        f'<div class="ai-answer">{safe_answer}</div>',
        unsafe_allow_html=True,
    )


with tab1:
    st.header("🤖 ИИ-помощник")
    st.write("Задай любой вопрос и получи ответ от искусственного интеллекта.")

    q1 = st.text_area(
        "Твой вопрос:",
        placeholder="Например: Как научиться лучше планировать время?",
        key="q1",
    )

    if st.button("Отправить", key="ai_btn"):
        if not q1.strip():
            st.warning("⚠️ Напиши вопрос.")
        else:
            with st.spinner("ИИ думает..."):
                answer = ask_ai(q1)
            show_answer(answer)


with tab2:
    st.header("🌤 Погода")
    st.write("Посмотри текущую температуру и прогноз на сегодня.")

    cities = {
        "Одесса": (46.48, 30.73),
        "Киев": (50.45, 30.52),
        "Запорожье": (47.83, 35.17),
        "Львов": (49.84, 24.03),
        "Харьков": (49.99, 36.23),
    }

    if "extra_cities" not in st.session_state:
        st.session_state.extra_cities = {}

    city_input = st.text_input(
        "Или введи свой город:",
        placeholder="Например: Лондон",
        key="city_in",
    )

    if st.button("Найти погоду", key="weather_btn"):
        if not city_input.strip():
            st.warning("Введи название города.")
        else:
            try:
                geo_response = requests.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={
                        "q": city_input.strip(),
                        "format": "json",
                        "limit": 1,
                    },
                    headers={"User-Agent": "SlepoyApp/1.0"},
                    timeout=10,
                )
                geo_response.raise_for_status()
                geo_data = geo_response.json()

                if geo_data:
                    city_name = geo_data[0].get(
                        "display_name",
                        city_input.strip(),
                    ).split(",")[0]

                    st.session_state.extra_cities[city_name] = (
                        float(geo_data[0]["lat"]),
                        float(geo_data[0]["lon"]),
                    )
                    st.success(f"Город найден: {city_name}")
                else:
                    st.error("Город не найден 😢")

            except requests.RequestException:
                st.error("Не удалось найти город. Проверь подключение к интернету.")
            except (ValueError, KeyError, IndexError):
                st.error("Не удалось обработать данные о городе.")

    all_cities = {**cities, **st.session_state.extra_cities}

    weather_codes = {
        0: "Ясно ☀️",
        1: "Преимущественно ясно 🌤",
        2: "Переменная облачность ⛅",
        3: "Пасмурно ☁️",
        45: "Туман 🌫",
        48: "Изморозь и туман 🌫",
        51: "Лёгкая морось 🌦",
        53: "Морось 🌦",
        55: "Сильная морось 🌧",
        61: "Небольшой дождь 🌧",
        63: "Дождь 🌧",
        65: "Сильный дождь 🌧",
        71: "Небольшой снег ❄️",
        73: "Снег ❄️",
        75: "Сильный снег ❄️",
        80: "Ливневый дождь 🌦",
        81: "Ливни 🌧",
        82: "Сильные ливни ⛈",
        95: "Гроза ⛈",
        96: "Гроза с градом ⛈",
        99: "Сильная гроза с градом ⛈",
    }

    for city, (lat, lon) in all_cities.items():
        try:
            response = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,weather_code",
                    "daily": "temperature_2m_max,temperature_2m_min",
                    "timezone": "auto",
                    "forecast_days": 1,
                },
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()

            current = data["current"]
            daily = data["daily"]

            temp = current["temperature_2m"]
            code = current["weather_code"]
            tmax = daily["temperature_2m_max"][0]
            tmin = daily["temperature_2m_min"][0]
            condition = weather_codes.get(code, "Погодные данные доступны")

            st.markdown(
                f"""
                <div class="weather-card">
                    <div class="city-name">{html.escape(city)}</div>
                    <div class="temp-big">{temp}°C</div>
                    <div class="condition">{html.escape(condition)}</div>
                    <div class="condition">
                        Максимум: {tmax}°C · Минимум: {tmin}°C
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        except (requests.RequestException, KeyError, IndexError, TypeError):
            st.markdown(
                f"""
                <div class="weather-card">
                    <div class="city-name">{html.escape(city)}</div>
                    <div class="temp-big">—°C</div>
                    <div class="condition">Нет данных о погоде</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


with tab3:
    st.header("🔮 Спроси судьбу")
    st.write("Задай вопрос о будущем и получи ответ для размышления.")

    q3 = st.text_area(
        "Твой вопрос:",
        placeholder="Например: Что нового может принести мне следующий год?",
        key="q3",
    )

    length = st.radio(
        "Длина ответа:",
        ["Коротко", "Подробнее"],
        horizontal=True,
        key="len",
    )

    if st.button("Получить ответ", key="fate_btn"):
        if not q3.strip():
            st.warning("⚠️ Напиши вопрос.")
        else:
            if length == "Коротко":
                prompt = (
                    "Ответь на русском языке в 1–2 предложениях. "
                    "Будь доброжелательным. Вопрос о будущем — это "
                    "развлечение: не утверждай, что достоверно предсказываешь "
                    f"будущее. Вопрос: {q3}"
                )
            else:
                prompt = (
                    "Ответь на русском языке в 4–6 предложениях. "
                    "Будь доброжелательным и поддерживающим. "
                    "Вопрос о будущем — развлечение, а не достоверное "
                    f"предсказание. Вопрос: {q3}"
                )

            with st.spinner("Готовим ответ..."):
                answer = ask_ai(prompt)

            show_answer(answer)

    st.markdown(
        '<div class="disclaimer">'
        "Ответы о судьбе созданы для развлечения и размышления, "
        "а не являются достоверными предсказаниями."
        "</div>",
        unsafe_allow_html=True,
    )

