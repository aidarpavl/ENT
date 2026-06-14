import statistics as stats
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

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

    /* ИСПРАВЛЕНО: Глобальное увеличение шрифтов и добавление жирности во ВСЕ таблицы сайта */
    /* Настройка обычных ячеек с данными */
    [data-testid="stTable"] td, .stDataFrame td, [data-testid="stDataFrame"] [role="gridcell"] {
        font-size: 15px !important;
        font-weight: 700 !important;
        color: #0f172a !important;
    }
    
    /* Настройка заголовков (шапки) таблиц */
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
        "file_uploader": "Выберите Excel файл (.xlsx):",
        "info_load": "👋 Пожалуйста, загрузите ваш Excel файл с результатами ЕНТ через боковую панель слева.",
        "req_title": "### 📌 Требования к колонкам в Excel файле:",
        "req_text": "Ваша таблица должна содержать обязательные столбцы с точными названиями:\n* `ФИО`, `Класс`, `Пол`\n* `Мат_Грамотность`, `Грамотность_Чтения`, `История_Казахстана`\n* `Профильный_1`, `Профильный_2`\n* **`Достижение`** (заполните значениями: *Алтын белгі* или *Үздік аттестат*)",
        "error_cols": "В вашем Excel файле не найдены обязательные столбцы: ",
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
        "sub_ach": "✨ Сводные показатели и достижения",
        "card_altyn": "🥇 Претенденты на 'Алтын белгі'",
        "card_uzdik": "🥈 Статус 'Үздік аттестат'",
        "lbl_altyn_list": "👑 Претенденты на 'Алтын белгі'",
        "lbl_uzdik_list": "💎 Обладатели статуса 'Үздік аттестат'",
        "no_altyn": "Претенденты на 'Алтын белгі' in этой выборке отсутствуют.",
        "no_uzdik": "Обладатели статуса 'Үздік аттестат' в этой выборке отсутствуют.",
        "sub_top10": "🏆 ТОП-10 результатов по дисциплине: ",
        "rank_place": "Место",
        "sub_results": "📋 Общий список результатов учеников",
        "avg_row": "⚡ ДЛЯ СРАВНЕНИЯ: СРЕДНИЙ БАЛЛ ВЫБОРКИ",
        "no_data": "Нет данных для отображения списка. Попробуйте выбрать другой диапазон баллов.",
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
        "no_ach_graph": "В выбранной выборке нет отличников для построения графиков."
    },
    "kk": {
        "title": "📊 ҰБТ нәтижелерін интерактивті талдау",
        "sidebar_load": "📂 Мәліметтерді жүктеу",
        "file_uploader": "Excel файлын таңдаңыз (.xlsx):",
        "info_load": "👋 Сол жақтағы басқару панелі арқылы ҰБТ нәтижелері бар Excel файлын жүктеңіз.",
        "req_title": "### 📌 Excel файлындағы бағандарға қойылатын талаптар:",
        "req_text": "Кестеде келесі атаулары бар міндетті бағандар болуы тиіс:\n* `ФИО`, `Класс`, `Пол`\n* `Мат_Грамотность`, `Грамотность_Чтения`, `История_Казахстана`\n* `Профильный_1`, `Профильный_2`\n* **`Достижение`** (мәндерін толтырыңыз: *Алтын белгі* немесе *Үздік аттестат*)",
        "error_cols": "Excel файлыңызда қажетті бағандар табылған жоқ: ",
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
        "sub_ach": "✨ Жиынтық көрсеткіштер мен жетістіктер",
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
        "no_data": "Тізімді көрсету үшін мәліметтер жоқ. Басқа балл ауқымын таңдап көріңіз.",
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
        "no_ach_graph": "Графиктерді құру үшін таңдалған іріктеуде үздік оқушылар жоқ."
    }
}

L = texts[st.session_state.lang]
st.title(L["title"])

# ИСПРАВЛЕНО: Ключи профильных предметов изменены под новые колонки Excel-файла
subjects_dict = {
    "Общий_Балл": "Общий балл" if st.session_state.lang == "ru" else "Жалпы балл",
    "Мат_Грамотность": "Мат. грамотность" if st.session_state.lang == "ru" else "Мат. сауаттылық",
    "Грамотность_Чтения": "Грамотность чтения" if st.session_state.lang == "ru" else "Оқу сауаттылығы",
    "История_Казахстана": "История Казахстана" if st.session_state.lang == "ru" else "Қазақстан тарихы",
    "Балл_Профиль_1": "Профильный предмет 1" if st.session_state.lang == "ru" else "Бейіндік пән 1",
    "Балл_Профиль_2": "Профильный предмет 2" if st.session_state.lang == "ru" else "Бейіндік пән 2"
}


# --- 2. АВТОМАТИЧЕСКАЯ ОНЛАЙН/ЛОКАЛЬНАЯ ЗАГРУЗКА ТРЕХ ФАЙЛОВ ---
st.sidebar.header(L["sidebar_load"])

import io
import os
import ssl
import urllib.request

# Имена ваших файлов
file_names = ["result_ent_1.xlsx", "result_ent_2.xlsx", "result_ent_3.xlsx"]

# Умное определение папки, в которой находится сам запущенный файл app.py
current_folder = os.path.dirname(os.path.abspath(__file__))

# ВНИМАНИЕ: После того как создадите репозиторий на GitHub, замените 'ВАШ_НИК' и 'ИМЯ_РЕПОЗИТОРИЯ' на свои!
github_base_url = "https://github.com/zharas2000-kz/ent-analytics"

# Кнопка обновления данных
refresh_data = st.sidebar.button("🔄 Обновить данные" if st.session_state.lang == "ru" else "🔄 Мәліметтерді жаңарту")

all_dfs = []
unique_dates = []

try:
    # Обход любых блокировок SSL на домашних компьютерах
    context = ssl._create_unverified_context()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for name in file_names:
        local_path = os.path.join(current_folder, name)
        
        # ЛОГИКА: Если файл лежит рядом на компьютере — берем его. Если запустили в облаке — качаем с GitHub
        if os.path.exists(local_path):
            with open(local_path, "rb") as f:
                file_bytes = f.read()
        else:
            # Ссылка на чистый файл в облаке GitHub
            cloud_url = github_base_url + name
            req = urllib.request.Request(cloud_url, headers=headers)
            with urllib.request.urlopen(req, context=context) as response:
                file_bytes = response.read()
                
        # Читаем Excel из байтов памяти
        temp_df = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
        
        # Проверяем структуру колонок таблицы
        required_cols = [
            "ФИО", "Класс", "Пол", "Мат_Грамотность", 
            "Грамотность_Чтения", "История_Казахстана", 
            "Название_Профиля", "Балл_Профиль_1", "Балл_Профиль_2", "Достижение", "Дата"
        ]
        
        missing_cols = [col for col in required_cols if col not in temp_df.columns]
        if missing_cols:
            st.error(f"В файле '{name}' не найдены обязательные столбцы: {', '.join(missing_cols)}")
            st.stop()
            
        # Считаем общий балл для текущего ученика
        temp_df["Общий_Балл"] = (
            temp_df["Мат_Грамотность"] + temp_df["Грамотность_Чтения"] + temp_df["История_Казахстана"] + 
            temp_df["Балл_Профиль_1"] + temp_df["Балл_Профиль_2"]
        )
        
        # Извлекаем дату (берём значение первой строки)
        file_date = str(temp_df["Дата"].iloc[0]).strip().split(" ")[0]
        temp_df["Период"] = file_date
        
        if file_date not in unique_dates:
            unique_dates.append(file_date)
            
        # Очищаем текст от случайных пробелов
        temp_df["Класс"] = temp_df["Класс"].astype(str).str.strip()
        temp_df["ФИО"] = temp_df["ФИО"].astype(str).str.strip()
        temp_df["Достижение"] = temp_df["Достижение"].astype(str).str.strip()
        temp_df["Название_Профиля"] = temp_df["Название_Профиля"].astype(str).str.strip()
        
        all_dfs.append(temp_df)
        
    # Объединяем все три этапа в одну большую базу данных Pandas
    df = pd.concat(all_dfs, ignore_index=True)

except Exception as e:
    st.error(f"{L['error_read']}{e}")
    st.markdown("⚠️ **Подсказка**: Проверьте, что файлы `result_ent_1.xlsx`, `result_ent_2.xlsx` и `result_ent_3.xlsx` лежат в той же папке, что и этот скрипт app.py.")
    st.stop()

# Фиксируем последний срез по хронологии дат для отображения в таблицах и карточках сверху
latest_period = unique_dates[-1]
filtered_df_base = df[df["Период"] == latest_period]



# --- 3. КНОПКИ И УПРАВЛЕНИЕ НА САЙТЕ (БОКОВАЯ ПАНЕЛЬ) ---
st.sidebar.header(L["sidebar_filters"])
search_fio = st.sidebar.text_input(L["search_fio"], "")

available_classes = sorted(list(df["Класс"].unique()))
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
show_failed_list = st.sidebar.checkbox("🚨 Показать список не прошедших порог" if st.session_state.lang == "ru" else "🚨 Шекті балдан өтпегендер тізімін көрсету", value=False)

# ДОБАВЛЕНО: Новая галочка для поиска учеников со "двойками" по конкретным предметам
if st.session_state.lang == "ru":
    show_failed_subjects = st.sidebar.checkbox("❌ Не прошли порог по предметам", value=False)
else:
    show_failed_subjects = st.sidebar.checkbox("❌ Пәндер бойынша шекті балдан өтпегендер", value=False)

calc_stats = st.sidebar.button(L["btn_calc"])

# Найти в Части 3 блок применения фильтров и заменить на этот:
filtered_df = filtered_df_base.copy()
if selected_class != L["all_school"]:
    filtered_df = filtered_df[filtered_df["Класс"] == selected_class]
if search_fio:
    filtered_df = filtered_df[filtered_df["ФИО"].str.contains(search_fio, case=False)]
min_score, max_score = score_ranges[selected_range]
filtered_df = filtered_df[(filtered_df["Общий_Балл"] >= min_score) & (filtered_df["Общий_Балл"] <= max_score)]


# --- 4. КРАСИВЫЕ КАРТОЧКИ И СРЕДНИЙ БАЛЛ ---

if st.session_state.lang == "ru":
    if selected_class == L["all_school"]:
        dynamic_title = "✨ Сводные показатели и достижения школы"
    else:
        dynamic_title = f"✨ Сводные показатели и достижения {selected_class} класса"
else:
    if selected_class == L["all_school"]:
        dynamic_title = "✨ Мектептің жиынтық көрсеткіштері мен жетістіктерi"
    else:
        dynamic_title = f"✨ {selected_class} сыныбының жиынтық көрсеткіштері мен жетістіктерi"

st.write(f"### {dynamic_title}")

count_altyn = len(filtered_df[filtered_df["Достижение"] == "Алтын белгі"])
count_uzdik = len(filtered_df[filtered_df["Достижение"] == "Үздік аттестат"])

total_students = len(filtered_df)
school_average_score = filtered_df["Общий_Балл"].mean() if total_students > 0 else 0.0

failed_students_df = filtered_df[filtered_df["Общий_Балл"] < 50]
count_failed = len(failed_students_df)

col_ach1, col_ach2, col_ach3, col_ach4 = st.columns(4)
col_ach1.metric(L["card_altyn"], f"{count_altyn}")
col_ach2.metric(L["card_uzdik"], f"{count_uzdik}")

average_label = "🏛️ Средний балл" if st.session_state.lang == "ru" else "🏛️ Орташа балл"
col_ach3.metric(average_label, f"{school_average_score:.1f}")

failed_label = "🚨 Не прошли порог (<50 б.)" if st.session_state.lang == "ru" else "🚨 Шекті балдан өтпегендер (<50 б.)"
col_ach4.metric(failed_label, f"{count_failed} чел." if st.session_state.lang == "ru" else f"{count_failed} адам")

# Вывод списка не прошедших ОБЩИЙ пороговый балл в 50 баллов
if show_failed_list:
    st.write("")
    failed_title = "🛑 Список учащихся, не набравших пороговые 50 баллов" if st.session_state.lang == "ru" else "🛑 Шекті 50 балл жинай алмаған оқушылар тізімі"
    st.markdown(f"##### {failed_title}:")
    
    if not failed_students_df.empty:
        failed_display = failed_students_df[["ФИО", "Класс", "Общий_Балл"]].sort_values(by="Общий_Балл")
        st.dataframe(failed_display, use_container_width=True, hide_index=True)
    else:
        st.success("🎉 Отличные новости! В данной выборке нет учеников, набравших менее 50 баллов." if st.session_state.lang == "ru" else "🎉 Тамаша жаңалық! Бұл іріктеуде 50 балдан төмен жинаған оқушылар жоқ.")

# ДОБАВЛЕНО: Фильтрация и вывод списка не прошедших порог по КОНКРЕТНЫМ ПРЕДМЕТАМ
if show_failed_subjects:
    st.write("")
    fail_subj_title = "❌ Учащиеся, не прошедшие порог по отдельным предметам" if st.session_state.lang == "ru" else "❌ Жеке пәндер бойынша шекті балдан өтпеген оқушылар"
    st.markdown(f"##### {fail_subj_title}:")
    
    # Задаем условия «двоек» по предметам
    cond_mat_g = (filtered_df["Мат_Грамотность"] <= 3)
    cond_read_g = (filtered_df["Грамотность_Чтения"] <= 3)
    cond_hist_k = (filtered_df["История_Казахстана"] <= 5)
    cond_prof1 = (filtered_df["Балл_Профиль_1"] <= 5)
    cond_prof2 = (filtered_df["Балл_Профиль_2"] <= 5)
    
    # Объединяем все условия через ИЛИ ('|')
    failed_by_subjects = filtered_df[cond_mat_g | cond_read_g | cond_hist_k | cond_prof1 | cond_prof2].copy()
    
    if not failed_by_subjects.empty:
        cols_to_show = ["ФИО", "Класс", "Мат_Грамотность", "Грамотность_Чтения", "История_Казахстана", "Балл_Профиль_1", "Балл_Профиль_2", "Общий_Балл"]
        table_to_style = failed_by_subjects[cols_to_show].sort_values(by="Класс")

        # Функция для динамического окрашивания ячеек с баллами
        def highlight_failed_cells(row):
            # По умолчанию все ячейки в строке не имеют цвета фонового выделения
            styles = [''] * len(row)
            
            # Индексы наших колонок в таблице:
            # row.index: 0=ФИО, 1=Класс, 2=Мат_Грамотность, 3=Грамотность_Чтения, 4=История_Казахстана, 5=Балл_Профиль_1, 6=Балл_Профиль_2, 7=Общий_Балл
            
            # Проверяем Мат. грамотность (индекс 2)
            if row.iloc[2] <= 3:
                styles[2] = 'background-color: #fee2e2; color: #991b1b;' # пастельно-красный фон и темно-красный текст
                
            # Проверяем Грамотность чтения (индекс 3)
            if row.iloc[3] <= 3:
                styles[3] = 'background-color: #fee2e2; color: #991b1b;'
                
            # Проверяем Историю Казахстана (индекс 4)
            if row.iloc[4] <= 5:
                styles[4] = 'background-color: #fee2e2; color: #991b1b;'
                
            # Проверяем Профильный предмет 1 (индекс 5)
            if row.iloc[5] <= 5:
                styles[5] = 'background-color: #fee2e2; color: #991b1b;'
                
            # Проверяем Профильный предмет 2 (индекс 6)
            if row.iloc[6] <= 5:
                styles[6] = 'background-color: #fee2e2; color: #991b1b;'
                
            return styles

        # Применяем стиль построчно ко всей таблице через Styler Pandas
        styled_df = table_to_style.style.apply(highlight_failed_cells, axis=1)
        
        # Выводим стилизованную таблицу на сайт
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        no_fail_sub_text = "🎉 Замечательно! Все учащиеся успешно преодолели внутренние пороги по всем предметам." if st.session_state.lang == "ru" else "🎉 Керемет! Барлық оқушылар барлық пәндер бойынша ішкі шекті балдардан сәтті өтті."
        st.success(no_fail_sub_text)


# Подготовка сводного отчета по классам (отображается при режиме "Вся школа")
if selected_class == L["all_school"] and not df.empty:
    st.write("")
    class_report_title = "📊 Сводный отчет по классам" if st.session_state.lang == "ru" else "📊 Сыныптар бойынша жиынтық есеп"
    st.markdown(f"##### {class_report_title}")
    
    class_report_data = []
    # ИСПРАВЛЕНО: берем уникальные классы и расчеты строго из filtered_df_base (последний этап ЕНТ)
    for cls in sorted(filtered_df_base["Класс"].unique()):
        class_df = filtered_df_base[filtered_df_base["Класс"] == cls]
        cls_total = len(class_df)
        cls_high = len(class_df[class_df["Общий_Балл"] >= 100])
        cls_quality = (cls_high / cls_total * 100) if cls_total > 0 else 0.0
        cls_avg = class_df["Общий_Балл"].mean()
        
        class_report_data.append({
            "Класс" if st.session_state.lang == "ru" else "Сынып": cls,
            "Всего учеников" if st.session_state.lang == "ru" else "Оқушы саны": cls_total,
            "Средний общий балл" if st.session_state.lang == "ru" else "Орташа жалпы балл": round(cls_avg, 1),
            "Качество знаний" if st.session_state.lang == "ru" else "Білім сапасы": f"{cls_quality:.1f}%"
        })
    summary_classes_df = pd.DataFrame(class_report_data)
    st.dataframe(summary_classes_df, use_container_width=True, hide_index=True)
    
    # Кнопка скачивания сводного отчета по классам
    import io
    buffer_summary = io.BytesIO()
    with pd.ExcelWriter(buffer_summary, engine="openpyxl") as writer:
        summary_classes_df.to_excel(writer, index=False, sheet_name="Summary")
    
    btn_label_sum = "📥 Скачать сводный отчет классов" if st.session_state.lang == "ru" else "📥 Сыныптардың жиынтық есебін жүктеу"
    st.download_button(
        label=btn_label_sum,
        data=buffer_summary.getvalue(),
        file_name="summary_classes.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.markdown("---")


# --- 5. ТАБЛИЦЫ СПИСКОВ И ИХ ВЫГРУЗКА ---
if show_top10:
    st.subheader(f"{L['sub_top10']}{subjects_dict[selected_subject]}")
    top10_df = filtered_df.sort_values(by=selected_subject, ascending=False).head(10).copy()
    top10_df.insert(0, L["rank_place"], range(1, len(top10_df) + 1))
    st.dataframe(top10_df[[L["rank_place"], "ФИО", "Класс", selected_subject]], use_container_width=True, hide_index=True)

if show_list:
    st.subheader(L["sub_results"])
    if not filtered_df.empty:
        display_df = filtered_df.copy()
        num_cols = list(display_df.select_dtypes(include=[np.number]).columns)
        display_df[num_cols] = display_df[num_cols].astype(float)
        
        means = display_df[num_cols].mean().round(1)
        summary_data = {
            "ФИО": L["avg_row"], 
            "Класс": "-", 
            "Пол": "-",
            "Достижение": "-"
        }
        for col in num_cols:
            summary_data[col] = means[col]
            
        summary_row = pd.DataFrame([summary_data])
        final_table = pd.concat([display_df, summary_row], ignore_index=True)
        st.dataframe(final_table, use_container_width=True, hide_index=True)
        
        import io
        buffer_list = io.BytesIO()
        with pd.ExcelWriter(buffer_list, engine="openpyxl") as writer:
            final_table.to_excel(writer, index=False, sheet_name="Filtered_Students")
            
        btn_label_list = "📥 Скачать отфильтрованный список (с расчетом среднего)" if st.session_state.lang == "ru" else "📥 Сүзілген тізімді жүктеу (орташа баллмен)"
        st.download_button(
            label=btn_label_list,
            data=buffer_list.getvalue(),
            file_name="filtered_students.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning(L["no_data"])

# --- 6. СТАТИСТИКА ПО ПРЕДМЕТУ ---
if calc_stats and not filtered_df.empty:
    st.subheader(f"{L['sub_stat']}{subjects_dict[selected_subject]}")
    mean_val = filtered_df[selected_subject].mean()
    median_val = np.median(filtered_df[selected_subject])
    try: mode_val = stats.mode(filtered_df[selected_subject])
    except stats.StatisticsError: mode_val = L["no_mode"]
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric(L["stat_mean"], f"{mean_val:.1f}")
    col2.metric(L["stat_median"], f"{median_val:.0f}")
    col3.metric(L["stat_mode"], str(mode_val))
    col4.metric(L["stat_max"], f"{filtered_df[selected_subject].max()}")
    col5.metric(L["stat_min"], f"{filtered_df[selected_subject].min()}")

# --- 7. ОСНОВНЫЕ ГРАФИКИ ПОСЕРЕДИНЕ (ТЕКУЩИЙ ЭТАП) ---
st.write(f"### {L['sub_graphs']}")
if not filtered_df.empty:
    sns.set_theme(style="whitegrid")
    
    fig1, axes1 = plt.subplots(1, 2, figsize=(16, 5))
    
    # Распределение баллов по выбранному в меню предмету
    sns.histplot(filtered_df[selected_subject], bins=8, kde=True, color="#1D4ED8", ax=axes1[0])
    axes1[0].set_title(f"{L['g1_title']}{subjects_dict[selected_subject]} ({latest_period})", fontsize=11, fontweight="bold")
    axes1[0].set_ylabel(L["g1_ylabel"])

    if selected_class == L["all_school"]:
        sns.boxplot(x="Класс", y=selected_subject, data=filtered_df, palette="coolwarm", ax=axes1[1], hue="Класс", legend=False)
        axes1[1].set_title(f"{L['g2_title_school']}{subjects_dict[selected_subject]}", fontsize=11, fontweight="bold")
        
        for i, cls in enumerate(sorted(filtered_df["Класс"].unique())):
            class_scores = filtered_df[filtered_df["Класс"] == cls][selected_subject].dropna()
            if not class_scores.empty:
                axes1[1].text(i, class_scores.min() - 0.8, f"Min: {class_scores.min()}", ha="center", va="top", color="#b91c1c", fontweight="bold", fontsize=10)
                axes1[1].text(i, class_scores.max() + 0.8, f"Max: {class_scores.max()}", ha="center", va="bottom", color="#15803d", fontweight="bold", fontsize=10)
    else:
        sns.barplot(x="Пол", y=selected_subject, data=filtered_df, palette="Spectral", ax=axes1[1], errorbar=None, hue="Пол", legend=False)
        axes1[1].set_title(f"{L['g2_title_class']}{subjects_dict[selected_subject]}", fontsize=11, fontweight="bold")
        for container in axes1[1].containers:
            axes1[1].bar_label(container, fmt="%.1f", padding=3, size=10, weight="bold")
            
    st.pyplot(fig1)
    
    st.write("")
    fig2, ax2 = plt.subplots(figsize=(16, 7))
    
    # Сводный анализ предметов школы за текущий этап
    school_rows = []
    lang_m = "Мат. грамотность" if st.session_state.lang == "ru" else "Мат. сауаттылық"
    lang_r = "Грамотность чтения" if st.session_state.lang == "ru" else "Оқу сауаттылығы"
    lang_h = "История Казахстана" if st.session_state.lang == "ru" else "Қазақстан тарихы"
    
    for _, row in filtered_df.iterrows():
        school_rows.append({"Класс": row["Класс"], "Предмет": lang_m, "Балл": row["Мат_Грамотность"]})
        school_rows.append({"Класс": row["Класс"], "Предмет": lang_r, "Балл": row["Грамотность_Чтения"]})
        school_rows.append({"Класс": row["Класс"], "Предмет": lang_h, "Балл": row["История_Казахстана"]})
        
        prof_text = str(row["Название_Профиля"])
        prof_split = prof_text.split('-') if '-' in prof_text else [prof_text, prof_text]
        prof1_name = prof_split[0].strip()
        prof2_name = prof_split[1].strip() if len(prof_split) > 1 else (prof_text + " 2")
        
        school_rows.append({"Класс": row["Класс"], "Предмет": prof1_name, "Балл": row["Балл_Профиль_1"]})
        school_rows.append({"Класс": row["Класс"], "Предмет": prof2_name, "Балл": row["Балл_Профиль_2"]})
        
    melted_school_means = pd.DataFrame(school_rows)
    melted_school_means = melted_school_means.groupby(["Класс", "Предмет"], observed=False)["Балл"].mean().reset_index()
    
    unique_profs = sorted([p for p in melted_school_means["Предмет"].unique() if p not in [lang_m, lang_r, lang_h]])
    subject_order = [lang_m, lang_r, lang_h] + unique_profs
    melted_school_means["Предмет"] = pd.Categorical(melted_school_means["Предмет"], categories=subject_order, ordered=True)
    melted_school_means = melted_school_means.sort_values("Предмет")
    
    sns.barplot(x="Балл", y="Предмет", hue="Класс", data=melted_school_means, palette="mako", ax=ax2)
    ax2.set_title(L["g3_title"], fontsize=13, fontweight="bold")
    ax2.set_xlabel(L["stat_mean"])
    ax2.set_ylabel("")
    ax2.legend(title="Классы" if st.session_state.lang == "ru" else "Сыныптар", loc="upper right")
    
    for container in ax2.containers:
        ax2.bar_label(container, fmt="%.1f", padding=5, size=10, weight="bold")
    st.pyplot(fig2)
else:
    st.info("Данные для построения графиков отсутствуют.")


# --- 8. БЛОК АНАЛИТИКИ ОТЛИЧНИКОВ ---
if show_achievements:
    st.markdown("---")
    st.markdown(f"<h2>{L['sub_ach_anal']}</h2>", unsafe_allow_html=True)
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown(f"<h4>{L['lbl_altyn_list']}</h4>", unsafe_allow_html=True)
        altyn_table = filtered_df[filtered_df["Достижение"] == "Алтый белгі" if "Алтый белгі" in filtered_df["Достижение"].values else filtered_df["Достижение"] == "Алтын белгі"][["ФИО", "Класс", "Общий_Балл"]]
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

    st.write("")
    ach_df = filtered_df[filtered_df["Достижение"].isin(["Алтын белгі", "Үздік аттестат"])]
    
    if not ach_df.empty:
        fig3, axes3 = plt.subplots(1, 2, figsize=(16, 5))
        fig3.subplots_adjust(wspace=0.4)
        
        sns.boxplot(x="Достижение", y="Общий_Балл", data=ach_df, palette="magma", ax=axes3[0], hue="Достижение", legend=False)
        axes3[0].set_title(L["g_ach1_title"], fontsize=11, fontweight="bold")
        axes3[0].set_xlabel(L["g_ach1_xlabel"])
        axes3[0].set_ylabel(L["g_ach1_ylabel"])
        
        ach_rows = []
        lang_m = "Мат. грамотность" if st.session_state.lang == "ru" else "Мат. сауаттылық"
        lang_r = "Грамотность чтения" if st.session_state.lang == "ru" else "Оқу сауаттылығы"
        lang_h = "История Казахстана" if st.session_state.lang == "ru" else "Қазақстан тарихы"
        
        for _, row in ach_df.iterrows():
            ach_rows.append({"Достижение": row["Достижение"], "Предмет": lang_m, "Балл": row["Мат_Грамотность"]})
            ach_rows.append({"Достижение": row["Достижение"], "Предмет": lang_r, "Балл": row["Грамотность_Чтения"]})
            ach_rows.append({"Достижение": row["Достижение"], "Предмет": lang_h, "Балл": row["История_Казахстана"]})
            
            prof_text = str(row["Название_Профиля"])
            prof_split = prof_text.split('-') if '-' in prof_text else [prof_text, prof_text]
            prof1_name = prof_split[0].strip()
            prof2_name = prof_split[1].strip() if len(prof_split) > 1 else (prof_text + " 2")
            
            ach_rows.append({"Достижение": row["Достижение"], "Предмет": prof1_name, "Балл": row["Балл_Профиль_1"]})
            ach_rows.append({"Достижение": row["Достижение"], "Предмет": prof2_name, "Балл": row["Балл_Профиль_2"]})
            
        melted_ach = pd.DataFrame(ach_rows)
        melted_ach = melted_ach.groupby(["Достижение", "Предмет"], observed=False)["Балл"].mean().reset_index()
        
        unique_ach_profs = sorted([p for p in melted_ach["Предмет"].unique() if p not in [lang_m, lang_r, lang_h]])
        ach_subject_order = [lang_m, lang_r, lang_h] + unique_ach_profs
        melted_ach["Предмет"] = pd.Categorical(melted_ach["Предмет"], categories=ach_subject_order, ordered=True)
        melted_ach = melted_ach.sort_values("Предмет")
        
        sns.barplot(x="Балл", y="Предмет", hue="Достижение", data=melted_ach, palette="rocket", ax=axes3[1])
        axes3[1].set_title(L["g_ach2_title"], fontsize=11, fontweight="bold")
        axes3[1].set_xlabel(L["stat_mean"])
        axes3[1].set_ylabel("")
        axes3[1].legend(title="Достижения" if st.session_state.lang == "ru" else "Жетістіктер", loc="upper right")
        
        for container in axes3[1].containers:
            axes3[1].bar_label(container, fmt="%.1f", padding=3, size=9, weight="bold")
            
        plt.tight_layout()
        st.pyplot(fig3)

# --- 9. ФИНАЛЬНЫЙ БЛОК: ГРАФИКИ ДИНАМИКИ ПО ДАТАМ ПРОВЕДЕНИЯ (В САМОМ НИЗУ) ---
if not df.empty:
    st.markdown("---")
    trend_title = "📈 Динамика изменения результатов по датам проведения ЕНТ" if st.session_state.lang == "ru" else "📈 ҰБТ өткізілу күндері бойынша нәтижелердің динамикасы"
    st.markdown(f"<h2>{trend_title}</h2>", unsafe_allow_html=True)
    
    fig_dyn, axes_dyn = plt.subplots(1, 2, figsize=(16, 5))
    fig_dyn.subplots_adjust(wspace=0.4)
    
    # Фильтруем общую историческую базу под выбранный класс или ФИО для честного тренда
    trend_df = df.copy()
    if selected_class != L["all_school"]:
        trend_df = trend_df[trend_df["Класс"] == selected_class]
    if search_fio:
        trend_df = trend_df[trend_df["ФИО"].str.contains(search_fio, case=False)]
        
    # ИСПРАВЛЕНО: Временной порядок оси теперь строится по реальным датам, вытащенным из файлов
    period_order = unique_dates
    
    if not trend_df.empty:
        # 1. Левый линейный график: Динамика среднего общего балла
        avg_total_trend = trend_df.groupby("Период", observed=False)["Общий_Балл"].mean().reindex(period_order).reset_index()
        
        sns.lineplot(x="Период", y="Общий_Балл", data=avg_total_trend, marker="o", markersize=10, linewidth=3, color="#059669", ax=axes_dyn[0])
        axes_dyn[0].set_title("Динамика СРЕДНЕГО ОБЩЕГО балла ЕНТ" if st.session_state.lang == "ru" else "ҰБТ ОРТАША ЖАЛПЫ балының динамикасы", fontsize=11, fontweight="bold")
        axes_dyn[0].set_ylabel("Баллы" if st.session_state.lang == "ru" else "Баллдар")
        axes_dyn[0].set_xlabel("")
        
        # Проставляем точные цифры над маркерами общего балла
        for x, y in zip(avg_total_trend["Период"], avg_total_trend["Общий_Балл"]):
            if pd.notna(y):
                axes_dyn[0].text(x, y + 1.5, f"{y:.1f}", ha="center", fontweight="bold", color="#065f46", fontsize=10)
                
        # 2. Правый линейный график: Динамика всех предметов (Обязательные + Профильные)
        all_trend_rows = []
        lang_m = "Мат. грамотность" if st.session_state.lang == "ru" else "Мат. сауаттылық"
        lang_r = "Грамотность чтения" if st.session_state.lang == "ru" else "Оқу сауаттылығы"
        lang_h = "История Казахстана" if st.session_state.lang == "ru" else "Қазақстан тарихы"
        
        for _, row in trend_df.iterrows():
            # Заносим обязательные предметы
            all_trend_rows.append({"Период": row["Период"], "Предмет": lang_m, "Балл": row["Мат_Грамотность"]})
            all_trend_rows.append({"Период": row["Период"], "Предмет": lang_r, "Балл": row["Грамотность_Чтения"]})
            all_trend_rows.append({"Период": row["Период"], "Предмет": lang_h, "Балл": row["История_Казахстана"]})
            
            # Разделяем строку профиля по дефису
            prof_text = str(row["Название_Профиля"])
            prof_split = prof_text.split('-') if '-' in prof_text else [prof_text, prof_text]
            
            prof1_name = prof_split[0].strip()
            prof2_name = prof_split[1].strip() if len(prof_split) > 1 else (prof_text + " 2")
            
            # Заносим профильные предметы
            all_trend_rows.append({"Период": row["Период"], "Предмет": prof1_name, "Балл": row["Балл_Профиль_1"]})
            all_trend_rows.append({"Период": row["Период"], "Предмет": prof2_name, "Балл": row["Балл_Профиль_2"]})
            
        # Создаем DataFrame трендов
        melted_full_trend = pd.DataFrame(all_trend_rows)
        
        # Считаем средние значения для каждой точки (Период + Предмет)
        melted_full_trend = melted_full_trend.groupby(["Период", "Предмет"], observed=False)["Балл"].mean().reset_index()
        
        # Фиксируем сортировку дат на горизонтальной оси, чтобы они шли по хронологии файлов
        melted_full_trend["Период"] = pd.Categorical(melted_full_trend["Период"], categories=period_order, ordered=True)
        melted_full_trend = melted_full_trend.sort_values("Период")
        
        # Строим правый график (индекс 1)
        sns.lineplot(x="Период", y="Ballo_Profile_1" if "Ballo_Profile_1" in melted_full_trend.columns else "Балл", hue="Предмет", data=melted_full_trend, marker="s", markersize=8, linewidth=2.5, palette="tab10", ax=axes_dyn[1])
        axes_dyn[1].set_title("Динамика средних баллов по всем предметам" if st.session_state.lang == "ru" else "Барлық пәндер бойынша орташа балдар динамикасы", fontsize=11, fontweight="bold")
        axes_dyn[1].set_ylabel("Баллы" if st.session_state.lang == "ru" else "Баллдар")
        axes_dyn[1].set_xlabel("")
        
        # Выносим легенду вправо, чтобы не мешала
        axes_dyn[1].legend(title="Пәндер" if st.session_state.lang == "kk" else "Предметы", loc="upper left", bbox_to_anchor=(1, 1), fontsize=9)
        
        plt.tight_layout()
        st.pyplot(fig_dyn)