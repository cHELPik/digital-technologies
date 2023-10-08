import tkinter as tk
from tkinter import *
from tkinter import ttk
from db import *
import psycopg2

# Функции для работы с базой данных

def get_table_names(connection):
    try:
        cursor.execute("SELECT \"table_name\" FROM information_schema.tables WHERE table_schema = 'public'")
        table_names = cursor.fetchall()
        return [name[0] for name in table_names]
    except psycopg2.Error as e:
        print(f"Error getting table names: {e}")

def show_table(event):
    selected_table = combo.get()  # Получаем выбранную таблицу из комбобокса
    try:
        # Открываем соединение с базой данных и создаем курсор
        conn = psycopg2.connect(user="postgres", password="1234", host="localhost", port="5432", database="Philharmonic")
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM \"{selected_table}\"")
        table_data = cursor.fetchall()

        table_treeview.column("#0", width=0, stretch=NO)  # Устанавливаем ширину нулевого столбца в 0

        table_treeview.delete(*table_treeview.get_children())

        columns = [desc[0] for desc in cursor.description]

        table_treeview["columns"] = tuple(range(len(columns)))
        for i, column in enumerate(columns):
            table_treeview.heading(i, text=column)
            table_treeview.column(i, minwidth=0, width=120, stretch=NO)

        for row in table_data:
            table_treeview.insert("", "end", values=row)

        cursor.close()
        conn.close()

        create_input_fields(selected_table, columns)

    except psycopg2.Error as e:
        print(f"Error showing table: {e}")

def create_input_fields(table_name, columns):
    # Удаляем предыдущие поля ввода, если они существуют
    for child in input_frame.winfo_children():
        child.destroy()

    # Создаем метки и поля ввода для каждого столбца
    entries = []
    for i, column in enumerate(columns):
        label = Label(input_frame, text=column)
        label.grid(row=i, column=0, padx=5, pady=5)

        if i == 0:
            # Создаем комбобокс для первого столбца
            combobox = ttk.Combobox(input_frame)
            combobox.grid(row=i, column=1, padx=5, pady=5)
            entries.append(combobox)
        else:
            entry = Entry(input_frame)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries.append(entry)
        try:
            # Открываем соединение с базой данных и создаем курсор
            conn = psycopg2.connect(user="postgres", password="1234", host="localhost", port="5432", database="Philharmonic")
            cursor = conn.cursor()

            # Получаем уникальные значения из первого столбца таблицы
            cursor.execute(f"SELECT DISTINCT \"{columns[0]}\" FROM \"{table_name}\"")
            values = cursor.fetchall()
            values = [value[0] for value in values]

            # Заполняем комбобокс значениями
            entries[0]["values"] = values

            cursor.close()
            conn.close()
        except psycopg2.Error as e:
            print(f"Error getting column values: {e}")

        # Перерисовываем окно, чтобы отобразить новые поля ввода
        input_frame.update()

    # Заполняем остальные поля в зависимости от выбранного значения в первом поле
    def update_fields(event):
        selected_value = entries[0].get()
        if selected_value:
            try:
                conn = psycopg2.connect(user="postgres", password="1234", host="localhost", port="5432", database="Philharmonic")
                cursor = conn.cursor()

                cursor.execute(f"SELECT * FROM \"{table_name}\" WHERE \"{columns[0]}\" = %s", (selected_value,))
                result = cursor.fetchone()

                if result:
                    for i, value in enumerate(result[1:]):
                        entries[i+1].delete(0, END)
                        entries[i+1].insert(0, value)

                cursor.close()
                conn.close()
            except psycopg2.Error as e:
                print(f"Error updating fields: {e}")

    entries[0].bind("<<ComboboxSelected>>", update_fields)

    # Перерисовываем окно, чтобы отобразить новые поля ввода
    input_frame.update()

def delete_record():
    selected_table = combo.get()

    conn = psycopg2.connect(user="postgres", password="1234", host="localhost", port="5432", database="Philharmonic")
    cursor = conn.cursor()

    # Получаем информацию о столбцах из метаданных таблицы
    cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{selected_table}'")
    columns = [row[0] for row in cursor.fetchall()]

    # Получаем имя первого столбца таблицы
    first_column = columns[0]
    print(columns[0])
    values = [entry.get() for entry in input_frame.winfo_children() if isinstance(entry, Entry)]
    pk_value = values[0]
    print(pk_value)
    cursor.execute(f"DELETE FROM \"{selected_table}\" WHERE \"{first_column}\" = %s", (pk_value,))

    conn.commit()

    cursor.close()
    conn.close()

    # Обновляем отображение таблицы
    show_table(None)


def add_record():
    selected_table = combo.get()
    if selected_table:
        try:
            conn = psycopg2.connect(user="postgres", password="1234", host="localhost", port="5432", database="Philharmonic")
            cursor = conn.cursor()

            # Получаем информацию о столбцах из метаданных таблицы
            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{selected_table}'")
            columns = [row[0] for row in cursor.fetchall()]

            values = [entry.get() for entry in input_frame.winfo_children() if isinstance(entry, Entry)]

            # Формируем строку с именами столбцов, заключенными в двойные кавычки и разделенными запятыми
            columns_str = ', '.join([f'"{col}"' for col in columns])

            # Формируем строку с плейсхолдерами для значений, разделенными запятыми
            placeholders = ', '.join(['%s'] * len(values))

            # Формируем запрос INSERT с использованием имен столбцов и плейсхолдеров
            insert_query = f'INSERT INTO "{selected_table}" ({columns_str}) VALUES ({placeholders})'

            # Выполняем запрос с передачей значений как параметров
            cursor.execute(insert_query, values)
            conn.commit()

            cursor.close()
            conn.close()

            # Обновляем отображение таблицы
            show_table(None)
        except psycopg2.Error as e:
            print(f"Error adding record: {e}")


def edit_record():
    selected_table = combo.get()
    conn = psycopg2.connect(user="postgres", password="1234", host="localhost", port="5432", database="Philharmonic")
    cursor = conn.cursor()

    cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{selected_table}'")
    columns = [row[0] for row in cursor.fetchall()]

    values = [entry.get() for entry in input_frame.winfo_children() if isinstance(entry, Entry)]
    values = tuple(values)

    for item in range(1, len(columns)):
        cursor.execute(
            f"UPDATE \"{selected_table}\" SET \"{columns[item]}\" = %s WHERE \"{columns[0]}\" = %s",
            (values[item], values[0]))

    conn.commit()
    cursor.close()
    conn.close()

    # Обновляем отображение таблицы
    show_table(None)


def execute_query():
    query = query_text.get("1.0", tk.END).strip()  # Получаем текст запроса из поля query_text

    try:
        conn = psycopg2.connect(user="postgres", password="", host="localhost", port="5432", database="Philharmonic")
        cursor = conn.cursor()

        cursor.execute(query)  # Выполняем запрос

        # Очищаем TreeView
        query_treeview.delete(*query_treeview.get_children())

        # Получаем информацию о столбцах из метаданных запроса
        columns = [desc[0] for desc in cursor.description]

        # Добавляем заголовки столбцов
        query_treeview["columns"] = tuple(range(len(columns)))
        for i, column in enumerate(columns):
            query_treeview.heading(i, text=column)

        # Добавляем данные в TreeView
        for row in cursor.fetchall():
            query_treeview.insert("", "end", values=row)

        conn.commit()
        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"Error executing query: {e}")


def get_Groups():
    # Устанавливаем соединение с базой данных PostgreSQL
    conn = psycopg2.connect(user="postgres", password="1234", host="localhost", port="5432", database="Philharmonic")

    # Создаем курсор для выполнения запросов
    cursor = conn.cursor()

    # Выполняем запрос для получения списка групп из таблицы
    query = '''
    SELECT DISTINCT "Genre" FROM "Genre"
    '''
    cursor.execute(query)

    # Получаем результаты запроса
    dates = cursor.fetchall()

    # Закрываем курсор и соединение с базой данных
    cursor.close()
    conn.close()

    # Возвращаем список Групп
    return [date[0] for date in dates]


def get_Song_list():
    selected_date = data_list.get()  # Получаем выбранную группу из Combobox

    # Устанавливаем соединение с базой данных PostgreSQL
    conn = psycopg2.connect(user="postgres", password="1234", host="localhost", port="5432", database="Philharmonic")

    # Создаем курсор для выполнения запросов
    cursor = conn.cursor()

    query = '''
        SELECT "ID_Album", "Name_album", "Publisher", "Date_of_release"
        FROM "Album"
        INNER JOIN "Musical_group" ON "Album"."ID_Musical_group" = "Musical_group"."ID_Musical_group"
        WHERE "Musical_group" = %s
        '''
    cursor.execute(query, (selected_date,))  # Передаем выбранную дату как параметр

    # Очищаем TreeView
    query_treeview.delete(*query_treeview.get_children())

    # Получаем информацию о столбцах из метаданных запроса
    columns = [desc[0] for desc in cursor.description]

    # Добавляем заголовки столбцов
    query_treeview["columns"] = tuple(range(len(columns)))
    for i, column in enumerate(columns):
        query_treeview.heading(i, text=column)

    # Добавляем данные в TreeView
    for row in cursor.fetchall():
        query_treeview.insert("", "end", values=row)

    cursor.close()
    conn.close()


# Создаем графическое окно
window = tk.Tk()
window.title("Music library")
window.geometry("500x500")

# Создание вкладок
notebook = ttk.Notebook(window)

# Создаем вкладку "Таблицы"
tabl_tab = ttk.Frame(notebook)
notebook.add(tabl_tab, text="Таблицы")

# Создаем комбобокс
combo = ttk.Combobox(tabl_tab)
combo.pack(pady=5)
combo.bind("<<ComboboxSelected>>", show_table)

combo.grid(row=0, column=0, pady=0, padx=0)



del_btn = Button(tabl_tab, text="Удалить", command=delete_record)
del_btn.grid(row=5, column=0, padx=3)


add_btn = Button(tabl_tab, text="Добавить", command=add_record)
add_btn.grid(row=5, column=1, padx=3)

edit_btn = Button(tabl_tab, text="Изменить", command=edit_record)
edit_btn.grid(row=5, column=2, padx=3)

# Создаем фрейм для размещения table_treeview
table_frame = Frame(tabl_tab, width=600, height=200)
table_frame.grid_propagate(False)
table_frame.grid(row=1, column=0, columnspan=4, pady=10)



table_treeview = ttk.Treeview(table_frame)
table_treeview.pack(expand=True, fill=BOTH)
table_treeview.column('#0', width=300)

#-------------


table_names = get_table_names(connection)
combo['values'] = table_names
connection.close()

# Размещаем table_frame по центру окна
table_frame.grid_rowconfigure(0, weight=1)
table_frame.grid_columnconfigure(0, weight=1)

# Создаем фрейм для размещения полей ввода
input_frame = Frame(tabl_tab)
input_frame.grid(row=2, column=0, columnspan=4, pady=5)



# Создаем вкладку "Запросы"
query_tab = ttk.Frame(notebook)
notebook.add(query_tab, text="Запросы")

# Создаем поле для запросов
query_text = tk.Text(query_tab, width=500, height=5)
query_text.pack(fill=tk.BOTH, expand=True)

query_btn = Button(query_tab, text="Выполнить", command=execute_query)
query_btn.pack(pady=10)

# Создаем TreeView для отображения результатов запроса
query_treeview = ttk.Treeview(query_tab)
query_treeview.pack()

# Сформировать список альбомов выбранной группы
l1 = Label(query_tab, text="Выбрать группу")
l1.pack()

data_list = ttk.Combobox(query_tab, values=get_Groups())
data_list.pack()

plane_list_btn = Button(query_tab, text="Выполнить", command=get_Song_list)
plane_list_btn.pack(pady=5)
notebook.pack()
# Запускаем главный цикл обработки событий окна
window.mainloop()
