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

# ИСПРАВЛЕНО: Правильный URL для GitHub репозитория (RAW файлы)
github_raw_base_url = "https://raw.githubusercontent.com/aidarpavl/ENT/main/"

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
            # ИСПРАВЛЕНО: Ссылка на чистый файл в RAW формате GitHub
            cloud_url = github_raw_base_url + name
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
    st.markdown("⚠️ **Подсказка**: Проверьте, что файлы `result_ent_1.xlsx`, `result_ent_2.xlsx` и `result_ent_3.xlsx` лежат в репозитории GitHub: https://github.com/aidarpavl/ENT")
    st.stop()

# Фиксируем последний срез по хронологии дат для отображения в таблицах и карточках сверху
latest_period = unique_dates[-1]
filtered_df_base = df[df["Период"] == latest_period]

# ... (остальной код остается без изменений до конца файла)
