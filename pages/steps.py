import streamlit as st
import streamlit_antd_components as sac

st.set_page_config(layout="wide") # Вся страница вместо узкой центральной колонки

titles = []
for i in range(1, 7):
    titles.append(f'Step {i}.')

subtitles = []
for i in range(1, 7):
    subtitles.append(f'Заголовок Шаг {i}.')

descriptions = []
for i in range(1, 7):
    descriptions.append(f'Выполнение набора Условий и Задач для Шага {i}.')

step_items = []
for i in range(0, 6):
    step_items.append(sac.StepsItem(title=titles[i], subtitle=subtitles[i], description=descriptions[i]))

def call_back_func():
    match st.session_state.my_steps:
        case 'Step 1.':
            action = 'Выполняется Набор Действий для Шага 1'
        case 'Step 2.':
            action = 'Выполняется Набор Действий для Шага 2'
        case 'Step 3.':
            action = 'Выполняется Набор Действий для Шага 3'
        case 'Step 4.':
            action = 'Выполняется Набор Действий для Шага 4'
        case 'Step 5.':
            action = 'Выполняется Набор Действий для Шага 5'
        case 'Step 6.':
            action = 'Выполняется Набор Действий для Шага 6'
        case _:
            action = 'Ничего ПОКА НЕ выполняется'
    return action

steps = sac.steps(items=step_items, format_func='title', type='navigation', key='my_steps', on_change=call_back_func, index=None, placement='vertical')
if steps:
    st.markdown(f"<h5>Выполнение {steps}</h5>", unsafe_allow_html=True)
    st.write(call_back_func())
