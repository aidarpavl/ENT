import statistics as stats
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
import requests  # requests модулін қосамыз
import io
import os

# Настройка страницы сайта
st.set_page_config(page_title="ЕНТ Аналитика / ҰБТ Аналитика", layout="wide", page_icon="📊")

# --- КРАСОЧНЫЙ ДИЗАЙН: Настройка CSS-стилей для интерфейса и фонов ---
st.markdown("""
<style>
    /* 1. Красивый мягкий градиентный фон для всего сайта */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
    }
    
    /* 2. Настройка боковой панели для контраста */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 2px solid #cbd5e1;
    }
    
    /* 3. Базовый стиль для карточек-метрик с тенями */
    div[data-testid="stMetric"] {
        padding: 20px !important;
        border-radius: 16px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.05) !important;
        border: none !important;
        transition: transform 0.2s ease-in-out;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
    }

    /* 4. Индивидуальные фоновые цвета для каждой карточки по порядку (от 1 до 4) */
    div[data-testid="stMetric"]:nth-of-type(1) {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%) !important;
    }
    div[data-testid="stMetric"]:nth-of-type(2) {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%) !important;
    }
    div[data-testid="stMetric"]:nth-of-type(3) {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%) !important;
    }
    div[data-testid="stMetric"]:nth-of-type(4) {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%) !important;
    }

    /* Изменение цвета текста внутри карточек для лучшей читаемости */
    div[data-testid="stMetric"] label {
        color: #1e293b !important;
        font-weight: 700 !important;
        font-size: 14px !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-weight: 800 !important;
    }

    /* Красивый стиль для кнопок */
    .stButton>button {
        background-color: #2563eb !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: bold !important;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2) !important;
    }
    .stButton>button:hover {
        background-color: #1d4ed8 !important;
        transform: scale(1.02);
    }

    /* Глобальное увеличение шрифтов и добавление жирности во ВСЕ таблицы сайта */
    [data-testid="stTable"] td, .stDataFrame td, [data-testid="stDataFrame"] [role="gridcell"] {
        font-size: 15px !important;
        font-weight: 700 !important;
        color: #0f172a !important;
    }
    
    [data-testid="stTable"] th, .stDataFrame th, [data-testid="stDataFrame"] [role="columnheader"] {
        font-size: 16px !important;
        font-weight: 900 !important;
        color: #1e293b !important;
        background-color: #f8fafc !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 1. ЛОКАЛИЗАЦИЯ И ДВУХЪЯЗЫЧНЫЙ СЛОВАРЬ ---
if "lang" not in st.session_state:
    st.session_state.lang = "ru"

st.sidebar.markdown("### 🌐 Тілді таңдау / Выбор языка")
lang_choice = st.sidebar.radio(
    "Смените язык / Тілді өзгертіңіз:",
    options=["Русский", "Қазақша"],
    index=0 if st.session_state.lang == "ru" else 1,
    label_visibility="collapsed"
)

st.session_state.lang = "ru" if lang_choice == "Русский" else "kk"

texts = {
    "ru": {
        "title": "📊 Интерактивный анализ результатов ЕНТ",
        "sidebar_load": "📂 Загрузка данных",
        "error_read": "Не удалось прочитать файл. Ошибка: ",
        "sidebar_filters": "🎛️ Фильтры и Поиск",
        "search_fio": "🔍 Поиск по ФИО:",
        "select_class": "🏫 Выберите класс:",
        "all_school": "Вся школа",
        "filter_score": "🎯 Фильтр по общему баллу:",
        "range_all": "Все баллы",
        "range_fail": "0-49 баллов (Не прошли порог)",
        "range_high": "120-140 баллов (Высокий результат)",
        "select_subject": "📚 Выберите предмет для анализа:",
        "chk_list": "Показать список учеников",
        "chk_top10": "🏆 Показать ТОП-10 результатов",
        "chk_ach": "🎖️ Показать аналитику Алтын белгі и Үздік аттестат",
        "btn_calc": "🚀 Рассчитать статистику",
        "card_altyn": "🥇 Претенденты на 'Алтын белгі'",
        "card_uzdik": "🥈 Статус 'Үздік аттестат'",
        "lbl_altyn_list": "👑 Претенденты на 'Алтын белгі'",
        "lbl_uzdik_list": "💎 Обладатели статуса 'Үздік аттестат'",
        "no_altyn": "Претенденты на 'Алтын белгі' в этой выборке отсутствуют.",
        "no_uzdik": "Обладатели статуса 'Үздік аттестат' в этой выборке отсутствуют.",
        "sub_top10": "🏆 ТОП-10 результатов по дисциплине: ",
        "rank_place": "Место",
        "sub_results": "📋 Общий список результатов учеников",
        "avg_row": "⚡ ДЛЯ СРАВНЕНИЯ: СРЕДНИЙ БАЛЛ ВЫБОРКИ",
        "no_data": "Нет данных для отображения списка.",
        "sub_stat": "📊 Статистика по дисциплине: ",
        "stat_mean": "Средний балл",
        "stat_median": "Медиана",
        "stat_mode": "Мода",
        "stat_max": "Макс. балл",
        "stat_min": "Мин. балл",
        "no_mode": "Нет уникальной моды",
        "sub_graphs": "📈 Визуальный анализ успеваемости",
        "g1_title": "Распределение баллов по предмету:\n",
        "g1_ylabel": "Количество учеников",
        "g2_title_school": "Сравнение классов по предмету:\n",
        "g2_title_class": "Средний балл парней и девушек по предмету:\n",
        "g3_title": "Сравнение средних баллов всей школы в разрезе классов",
        "sub_ach_anal": "👑 Глубокая аналитика категорий 'Алтын белгі' и 'Үздік аттестат'",
        "g_ach1_title": "Разброс общих баллов среди отличников",
        "g_ach1_xlabel": "Категория",
        "g_ach1_ylabel": "Общий балл",
        "g_ach2_title": "Сравнение средних баллов по предметам среди отличников",
    },
    "kk": {
        "title": "📊 ҰБТ нәтижелерін интерактивті талдау",
        "sidebar_load": "📂 Мәліметтерді жүктеу",
        "error_read": "Файлды оқу мүмкін болмады. Қате: ",
        "sidebar_filters": "🎛️ Сүзгілер және Іздеу",
        "search_fio": "🔍 ТАӘ бойынша іздеу:",
        "select_class": "🏫 Сыныпты таңдаңыз:",
        "all_school": "Барлық мектеп",
        "filter_score": "🎯 Жалпы балл бойынша сүзгі:",
        "range_all": "Барлық баллдар",
        "range_fail": "0-49 балл (Шекті балдан өтпегендер)",
        "range_high": "120-140 балл (Жоғары нәтиже)",
        "select_subject": "📚 Талдау үшін пәнді таңдаңыз:",
        "chk_list": "Оқушылар тізімін көрсету",
        "chk_top10": "🏆 ТОП-10 нәтижені көрсету",
        "chk_ach": "🎖️ Алтын белгі мен Үздік аттестат талдауын көрсету",
        "btn_calc": "🚀 Статистиканы есептеу",
        "card_altyn": "🥇 'Алтын белгіге' үміткерлер",
        "card_uzdik": "🥈 'Үздік аттестат' мәртебесі",
        "lbl_altyn_list": "👑 'Алтын белгі' үміткерлері",
        "lbl_uzdik_list": "💎 'Үздік аттестат' иегерлері",
        "no_altyn": "Бұл іріктеуде 'Алтын белгі' үміткерлері жоқ.",
        "no_uzdik": "Бұл іріктеуде 'Үздік аттестат' иегерлері жоқ.",
        "sub_top10": "🏆 Пән бойынша ТОП-10 нәтиже: ",
        "rank_place": "Орын",
        "sub_results": "📋 Оқушылар нәтижелерінің жалпы тізімі",
        "avg_row": "⚡ САЛЫСТЫРУ ҮШІН: ІРІКТЕУДІҢ ОРТАША БАЛЫ",
        "no_data": "Тізімді көрсету үшін мәліметтер жоқ.",
        "sub_stat": "📈 Пән бойынша статистика: ",
        "stat_mean": "Орташа балл",
        "stat_median": "Медиана",
        "stat_mode": "Мода",
        "stat_max": "Макс. балл",
        "stat_min": "Мин. балл",
        "no_mode": "Бірегей мода жоқ",
        "sub_graphs": "📈 Үлгерімді визуалды талдау",
        "g1_title": "Пән бойынша балдардың үлестірілуі:\n",
        "g1_ylabel": "Оқушылар саны",
        "g2_title_school": "Пән бойынша сыныптарды салыстыру:\n",
        "g2_title_class": "Пән бойынша ұлдар мен қыздардың орташа балы:\n",
        "g3_title": "Сыныптар бөлінісіндегі бүкіл мектептің орташа балын салыстыру",
        "sub_ach_anal": "👑 'Алтын белгі' және 'Үздік аттестат' санаттары бойынша терең талдау",
        "g_ach1_title": "Үздіктер арасындағы жалпы балдардың алшақтығы",
        "g_ach1_xlabel": "Санат",
        "g_ach1_ylabel": "Жалпы балл",
        "g_ach2_title": "Үздіктер арасындағы пәндер бойынша орташа балдарды салыстыру",
    }
}

L = texts[st.session_state.lang]
st.title(L["title"])

# Предметтердің сөздігі
subjects_dict = {
    "Общий_Балл": "Общий балл" if st.session_state.lang == "ru" else "Жалпы балл",
    "Мат_Грамотность": "Мат. грамотность" if st.session_state.lang == "ru" else "Мат. сауаттылық",
    "Грамотность_Чтения": "Грамотность чтения" if st.session_state.lang == "ru" else "Оқу сауаттылығы",
    "История_Казахстана": "История Казахстана" if st.session_state.lang == "ru" else "Қазақстан тарихы",
    "Балл_Профиль_1": "Профильный предмет 1" if st.session_state.lang == "ru" else "Бейіндік пән 1",
    "Балл_Профиль_2": "Профильный предмет 2" if st.session_state.lang == "ru" else "Бейіндік пән 2"
}

# --- 2. ФАЙЛДАРДЫ ЖҮКТЕУ ---
st.sidebar.header(L["sidebar_load"])

# GitHub RAW сілтемелері (дұрыс формат)
github_files = {
    "result_ent_1.xlsx": "https://raw.githubusercontent.com/aidarpavl/ENT/main/result_ent_1.xlsx",
    "result_ent_2.xlsx": "https://raw.githubusercontent.com/aidarpavl/ENT/main/result_ent_2.xlsx",
    "result_ent_3.xlsx": "https://raw.githubusercontent.com/aidarpavl/ENT/main/result_ent_3.xlsx"
}

@st.cache_data(ttl=3600)  # 1 сағат кэшпен сақтау
def load_data():
    """Файлдарды жүктеу функциясы"""
    all_dfs = []
    unique_dates = []
    
    for file_name, url in github_files.items():
        try:
            # Requests арқылы файлды жүктеу
            response = requests.get(url, timeout=30)
            response.raise_for_status()  # Қате болса exception шығару
            
            # Excel файлын оқу
            temp_df = pd.read_excel(io.BytesIO(response.content), engine="openpyxl")
            
            # Бағандарды тексеру
            required_cols = [
                "ФИО", "Класс", "Пол", "Мат_Грамотность", 
                "Грамотность_Чтения", "История_Казахстана", 
                "Название_Профиля", "Балл_Профиль_1", "Балл_Профиль_2", "Достижение", "Дата"
            ]
            
            missing_cols = [col for col in required_cols if col not in temp_df.columns]
            if missing_cols:
                st.warning(f"Файл '{file_name}' келесі бағандар жоқ: {', '.join(missing_cols)}")
                continue
                
            # Жалпы баллды есептеу
            temp_df["Общий_Балл"] = (
                temp_df["Мат_Грамотность"] + temp_df["Грамотность_Чтения"] + 
                temp_df["История_Казахстана"] + temp_df["Балл_Профиль_1"] + temp_df["Балл_Профиль_2"]
            )
            
            # Күнді анықтау
            file_date = str(temp_df["Дата"].iloc[0]).strip().split()[0]
            temp_df["Период"] = file_date
            
            if file_date not in unique_dates:
                unique_dates.append(file_date)
                
            # Мәтінді тазалау
            for col in ["Класс", "ФИО", "Достижение", "Название_Профиля"]:
                if col in temp_df.columns:
                    temp_df[col] = temp_df[col].astype(str).str.strip()
            
            all_dfs.append(temp_df)
            
        except Exception as e:
            st.error(f"{file_name} файлын жүктеу қатесі: {str(e)}")
            continue
    
    if not all_dfs:
        return None, None
    
    # Барлық файлдарды біріктіру
    df = pd.concat(all_dfs, ignore_index=True)
    return df, sorted(unique_dates)

# Мәліметтерді жүктеу
with st.spinner('Мәліметтер жүктелуде...'):
    df, unique_dates = load_data()

if df is None or unique_dates is None:
    st.error("⚠️ Мәліметтерді жүктеу мүмкін болмады. GitHub репозиторийін тексеріңіз.")
    st.info("📁 Файлдар келесі сілтемелерде болуы керек:\n" + 
            "\n".join([f"- {url}" for url in github_files.values()]))
    st.stop()

# Ең соңғы кезеңді анықтау
latest_period = unique_dates[-1] if unique_dates else None
filtered_df_base = df[df["Период"] == latest_period]

# --- 3. ФИЛЬТРЛЕР ---
st.sidebar.header(L["sidebar_filters"])
search_fio = st.sidebar.text_input(L["search_fio"], "")

available_classes = sorted(df["Класс"].unique())
selected_class = st.sidebar.selectbox(L["select_class"], [L["all_school"]] + available_classes)

score_ranges = {
    L["range_all"]: (0, 140),
    L["range_fail"]: (0, 49),
    "50-69": (50, 69),
    "70-99": (70, 99),
    "100-119": (100, 119),
    L["range_high"]: (120, 140)
}
selected_range = st.sidebar.selectbox(L["filter_score"], list(score_ranges.keys()))

selected_subject = st.sidebar.selectbox(
    L["select_subject"],
    options=list(subjects_dict.keys()),
    format_func=lambda x: subjects_dict[x]
)

show_list = st.sidebar.checkbox(L["chk_list"], value=True)
show_top10 = st.sidebar.checkbox(L["chk_top10"], value=False)
show_achievements = st.sidebar.checkbox(L["chk_ach"], value=True)
calc_stats = st.sidebar.button(L["btn_calc"])

# Фильтрлерді қолдану
filtered_df = filtered_df_base.copy()
if selected_class != L["all_school"]:
    filtered_df = filtered_df[filtered_df["Класс"] == selected_class]
if search_fio:
    filtered_df = filtered_df[filtered_df["ФИО"].str.contains(search_fio, case=False, na=False)]
min_score, max_score = score_ranges[selected_range]
filtered_df = filtered_df[(filtered_df["Общий_Балл"] >= min_score) & (filtered_df["Общий_Балл"] <= max_score)]

# --- 4. КАРТОЧКАЛАР ---
if selected_class == L["all_school"]:
    st.write("### ✨ Сводные показатели и достижения школы" if st.session_state.lang == "ru" else "### ✨ Мектептің жиынтық көрсеткіштері мен жетістіктерi")
else:
    st.write(f"### ✨ Сводные показатели и достижения {selected_class} класса" if st.session_state.lang == "ru" else f"### ✨ {selected_class} сыныбының жиынтық көрсеткіштері мен жетістіктерi")

count_altyn = len(filtered_df[filtered_df["Достижение"] == "Алтын белгі"])
count_uzdik = len(filtered_df[filtered_df["Достижение"] == "Үздік аттестат"])
total_students = len(filtered_df)
school_average_score = filtered_df["Общий_Балл"].mean() if total_students > 0 else 0.0

col_ach1, col_ach2, col_ach3 = st.columns(3)
col_ach1.metric(L["card_altyn"], f"{count_altyn}")
col_ach2.metric(L["card_uzdik"], f"{count_uzdik}")
col_ach3.metric("Средний балл" if st.session_state.lang == "ru" else "Орташа балл", f"{school_average_score:.1f}")

# --- 5. ТАБЛИЦАЛАР ---
if show_top10 and not filtered_df.empty:
    st.subheader(f"{L['sub_top10']}{subjects_dict[selected_subject]}")
    top10_df = filtered_df.sort_values(by=selected_subject, ascending=False).head(10).copy()
    top10_df.insert(0, L["rank_place"], range(1, len(top10_df) + 1))
    st.dataframe(top10_df[[L["rank_place"], "ФИО", "Класс", selected_subject]], use_container_width=True, hide_index=True)

if show_list:
    st.subheader(L["sub_results"])
    if not filtered_df.empty:
        display_df = filtered_df.copy()
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.warning(L["no_data"])

# --- 6. СТАТИСТИКА ---
if calc_stats and not filtered_df.empty:
    st.subheader(f"{L['sub_stat']}{subjects_dict[selected_subject]}")
    mean_val = filtered_df[selected_subject].mean()
    median_val = np.median(filtered_df[selected_subject])
    try: 
        mode_val = stats.mode(filtered_df[selected_subject])
    except: 
        mode_val = L["no_mode"]
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric(L["stat_mean"], f"{mean_val:.1f}")
    col2.metric(L["stat_median"], f"{median_val:.0f}")
    col3.metric(L["stat_mode"], str(mode_val))
    col4.metric(L["stat_max"], f"{filtered_df[selected_subject].max()}")
    col5.metric(L["stat_min"], f"{filtered_df[selected_subject].min()}")

# --- 7. ГРАФИКТЕР ---
st.write(f"### {L['sub_graphs']}")
if not filtered_df.empty:
    sns.set_theme(style="whitegrid")
    
    fig1, axes1 = plt.subplots(1, 2, figsize=(16, 5))
    
    # Балдардың таралуы
    sns.histplot(filtered_df[selected_subject], bins=8, kde=True, color="#1D4ED8", ax=axes1[0])
    axes1[0].set_title(f"{L['g1_title']}{subjects_dict[selected_subject]}", fontsize=11, fontweight="bold")
    axes1[0].set_ylabel(L["g1_ylabel"])

    if selected_class == L["all_school"]:
        sns.boxplot(x="Класс", y=selected_subject, data=filtered_df, palette="coolwarm", ax=axes1[1])
        axes1[1].set_title(f"{L['g2_title_school']}{subjects_dict[selected_subject]}", fontsize=11, fontweight="bold")
    else:
        sns.barplot(x="Пол", y=selected_subject, data=filtered_df, palette="Spectral", ax=axes1[1])
        axes1[1].set_title(f"{L['g2_title_class']}{subjects_dict[selected_subject]}", fontsize=11, fontweight="bold")
        
    st.pyplot(fig1)

# --- 8. ЖЕТІСТІКТЕР ТАЛДАУЫ ---
if show_achievements:
    st.markdown("---")
    st.markdown(f"<h2>{L['sub_ach_anal']}</h2>", unsafe_allow_html=True)
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown(f"<h4>{L['lbl_altyn_list']}</h4>", unsafe_allow_html=True)
        altyn_table = filtered_df[filtered_df["Достижение"] == "Алтын белгі"][["ФИО", "Класс", "Общий_Балл"]]
        if not altyn_table.empty:
            st.dataframe(altyn_table, use_container_width=True, hide_index=True)
        else:
            st.info(L["no_altyn"])
            
    with col_t2:
        st.markdown(f"<h4>{L['lbl_uzdik_list']}</h4>", unsafe_allow_html=True)
        uzdik_table = filtered_df[filtered_df["Достижение"] == "Үздік аттестат"][["ФИО", "Класс", "Общий_Балл"]]
        if not uzdik_table.empty:
            st.dataframe(uzdik_table, use_container_width=True, hide_index=True)
        else:
            st.info(L["no_uzdik"])

st.success("✅ Деректер сәтті жүктелді!" if st.session_state.lang == "ru" else "✅ Деректер сәтті жүктелді!")