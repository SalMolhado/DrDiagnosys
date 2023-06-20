from flask import Flask, render_template, request, jsonify
from flask_bootstrap import Bootstrap
import mysql.connector
from mysql.connector.errors import Error, IntegrityError
from json import load, dumps
from os import path, listdir, getcwd
from docker import from_env
from docker.errors import DockerException, NotFound, APIError
from time import sleep
import atexit


# Define as informações de conexão do banco de dados como variáveis globais
DB_HOST = '127.0.0.1'
DB_USER = 'root'
DB_PASSWORD = 'botafogo'
DB_NAME = 'drdiagnosys'
CONTEINER_NAME = 'drdiagnosys_db'
DB_CONFIG = {
    "user": DB_USER,
    "password": DB_PASSWORD,
    "host": DB_HOST,
    "database": DB_NAME,
}
connection = None
cursor = None


def connect_to_db():
    print('\nconnect_to_db')
    global connection
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print('Connected to MySQL database')
            global cursor
            cursor = connection.cursor()
            return True
    except Error as e:
        print(f"Error while connecting to MySQL: {str(e)}")
        return False


def close_db_connection():
    print('\nclose_db_connection')
    global connection
    if connection is not None:
        if connection.is_connected():
            connection.close()
            print('MySQL connection is closed')


def create_db_conteiner():
    print('\ncreate_db_conteiner')
    try:
        while True:
            client = from_env()
            client.containers.run(
                "mysql:8.0",
                detach=True,
                name=CONTEINER_NAME,
                environment={
                    'MYSQL_ROOT_PASSWORD': DB_PASSWORD,
                    'MYSQL_DATABASE': DB_NAME
                },
                ports={'3306/tcp': (DB_HOST, 3306)},
                auto_remove=True
            )
            print('mysql conteiner created')
            for _ in range(30):
                try:
                    container = client.containers.get(CONTEINER_NAME)
                    print(container.status)
                    if container.status == 'running':
                        print('MySQL container is running.')
                        wait_for_db()
                        break
                except NotFound:
                    print('MySQL container not found. Waiting...')
                except APIError as e:
                    print(f'API error: {e}. Waiting...')
                sleep(2.4)
            else:
                print('Timed out while waiting for MySQL container to start.')
                raise DockerException('Timed out while waiting for MySQL container to start.')
    except DockerException:
        pass


def wait_for_db():
    print('\nwait_for_db')
    tries = 0
    for _ in range(30):
        tries += 1
        if connect_to_db():
            print("MySQL is ready to accept connections.")
            break
        else:
            print(f"{tries} Failed to connect to MySQL\n\tRetrying...")
            sleep(2.3)
    else:
        print("Timed out while waiting for MySQL to connect..")
        raise Exception("Timed out while waiting for MySQL to connect..")


app = Flask('__name__')
Bootstrap(app)


def execute_sql(sql: str, params=None, headers=False):
    print('\nexecute_sql')
    rows = []
    if params is None:
        params = ()
    if connection is not None and cursor is not None:
        try:
            print(f"\n----------- ----------- -----------")
            cursor.execute(sql, params)
            if "SELECT" in sql.upper() or "SHOW TABLES" in sql.upper():
                if headers:
                    headers = [i[0] for i in cursor.description]
                rows = cursor.fetchall()
                if rows:
                    print(f"\nRows produced by statement '{cursor.statement}':")
                    print(rows)
                else:
                    print(f"\nNumber of rows affected by statement '{cursor.statement}': {cursor.rowcount}")
            elif "INSERT INTO" in sql.upper():
                print(sql)
            connection.commit()
        except mysql.connector.Error as error:
            print(f"Something went wrong: {error}")
            if connection is not None:
                connection.rollback()
    else:
        print('Connection or Cursor is None')
    if headers:
        return headers, rows
    return rows


def format_sql_from_file(filename, params=None):
    print(f'\nformat_sql_from_file: {params}')
    with open(filename, 'r', encoding='utf-8') as file:
        raw_sql = file.read()
    final_params = []
    if isinstance(params, tuple):
        sql = raw_sql
        final_params = params
    elif params is not None:
        if 'in' in params:
            for param_set in params['in']:
                placeholders = ", ".join(["%s"] * len(param_set))
                raw_sql = raw_sql.replace("IN %s", "IN (" + placeholders + ")", 1)
                final_params.extend(list(param_set))
        if 'equal' in params:
            for param_set in params['equal']:
                placeholder = "%s"
                raw_sql = raw_sql.replace("= %s", "= " + placeholder, 1)
                final_params.append(param_set[0])
        sql = raw_sql
        final_params = tuple([item for sublist in params.get('in', []) for item in sublist])
    else:
        sql = raw_sql
        final_params = ()
    print(sql)
    print('%', tuple(final_params))
    return sql, tuple(final_params)


# --------- W E B ----------
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/show_tables', methods=['GET'])
def show_tables():
    tables = execute_sql('SHOW TABLES;')
    tables_data = {}
    for table in [table[0] for table in tables]:
        headers, rows = execute_sql(f"SELECT * FROM {table};", headers=True)
        tables_data[table] = {"headers": headers, "rows": rows}
    return render_template('show_tables.html', tables=tables_data)


@app.route('/consulta/<int:consulta_id>', methods=['GET', 'POST'])
def consulta(consulta_id):
    if request.method == 'POST':
        handle_input = load_input_handling_function(consulta_id)
        selected_items = handle_input(request.form)
        results, headers = get_results_from_db(selected_items, consulta_id)
        return render_template('results.html', results=results, headers=headers)
    elif request.method == 'GET':
        items, descriptions, input_type, title, placeholder, sql_code = pre_render_template(consulta_id)
        return render_template('consulta.html', items=items, descriptions=descriptions, sql_code=sql_code,
                               input_type=input_type, nome_consulta=title, placeholder=placeholder)


@app.route('/update_record', methods=['GET', 'POST'])
def update_record():
    if request.method == 'GET':
        all_tables_data = get_all_tables_data()
        return render_template('update_record.html', all_tables_data=all_tables_data)

    elif request.method == 'POST':
        data = request.get_json()
        print('!@!')
        print(dumps(data, indent=4))
        for table_name, rows in data.items():
            for row in rows:
                update_row(table_name, row['original'], row['new'])

        return 'OK', 200


@app.route('/delete_record', methods=['GET', 'POST'])
def delete_record():
    if request.method == 'GET':
        all_tables_data = get_all_tables_data()
        return render_template('delete_record.html', all_tables_data=all_tables_data)
    elif request.method == 'POST':
        data = request.get_json()
        print(dumps(data, indent=4))
        for table_name, rows in data.items():
            for row in rows:
                delete_row(table_name, row)
        return jsonify({"message": "Data deleted successfully ou não"})


def delete_row(table_name, record):
    id_by_table_ent = {'Doencas': 'id_doenca', 'Sintomas': 'id_sintoma', 'Causas': 'id_causa',
                       'FatoresDeRisco': 'id_fatorderisco', 'Tratamentos': 'id_tratamento',
                       'CategoriasDeDoencas': 'id_categoriasdedoencas'}
    keys_pair_by_table_ass = {'DoencaSintoma': ('id_doenca', 'id_sintoma'),
                              'DoencaCausa': ('id_doenca', 'id_causa'),
                              'DoencaFatorDeRisco': ('id_doenca', 'id_fatorderisco'),
                              'DoencaTratamento': ('id_doenca', 'id_tratamento')}
    if table_name in id_by_table_ent:
        where = f'{id_by_table_ent[table_name]} = {int(list(record.values())[0])}'
    elif table_name in keys_pair_by_table_ass:
        where = f'{keys_pair_by_table_ass[table_name][0]} = {int(list(record.values())[0])}, ' \
                f'{keys_pair_by_table_ass[table_name][1]} = {int(list(record.values())[1])}'
    query = f'DELETE FROM {table_name} WHERE {where};'
    try:
        cursor.execute(query)
    except NotFound:
        pass
    except Error:
        pass
    except IntegrityError:
        pass


def update_row(table_name, original, new):
    id_by_table_ent = {'Doencas': 'id_doenca', 'Sintomas': 'id_sintoma', 'Causas': 'id_causa',
                       'FatoresDeRisco': 'id_fatorderisco', 'Tratamentos': 'id_tratamento',
                       'CategoriasDeDoencas': 'id_categoriasdedoencas'}
    keys_pair_by_table_ass = {'DoencaSintoma': ('id_doenca', 'id_sintoma'),
                              'DoencaCausa': ('id_doenca', 'id_causa'),
                              'DoencaFatorDeRisco': ('id_doenca', 'id_fatorderisco'),
                              'DoencaTratamento': ('id_doenca', 'id_tratamento')}
    new_record = {}
    for colunm, value in new.items():
        _, index, colunm_name = colunm.split('-')
        new_record[index] = (colunm_name, int(value)) if 'id_' in colunm_name else (colunm_name, value)
    record = {}
    for colunm, value in original.items():
        _, index, colunm_name = colunm.split('-')
        record[index] = (colunm_name, int(value)) if 'id_' in colunm_name else (colunm_name, value)
    if table_name in id_by_table_ent:
        where = f" WHERE {record['1'][0]} = %s;"
        new_params = [value[1] for value in new_record.values()]
        new_params.append(record['1'][1])
        params = tuple(new_params)
        print('params:', params)
    elif table_name in keys_pair_by_table_ass:
        where = f" WHERE {record['1'][0]} = %s AND {record['2'][0]} = %s;"
        new_params = [value[1] for value in new_record.values()]
        new_params.extend([value[1] for value in record.values()])
        params = tuple(new_params)
        print('params:', params)
    else:
        raise Error(f'????? o que diabos aconteceu. table_name: {table_name}')
    query = f'UPDATE {table_name} SET' + ','.join([f' {value[0]} = %s' for value in new_record.values()]) + where
    try:
        cursor.execute(query, params)
    except IntegrityError:
        pass


def load_input_handling_function(consulta_id):
    print('\nload_input_handling_function')
    consult_by_id = {-1: handle_single_input, 2: handle_no_input, 3: handle_no_input,
                     1: handle_list_input, 4: handle_single_input, 5: handle_single_id}
    return consult_by_id[consulta_id]


def handle_single_id(form):
    input_data = int(form.get('items'))
    params = (input_data,)
    return params


def handle_no_input(form):
    return None


def handle_single_input(form):
    print('\nhandle_single_input')
    input_data = int(form.get('items'))
    params = {'in': [(input_data,)]}
    return params


def handle_list_input(form):
    print('\nhandle_list_input')
    input_data = form.getlist('items')
    params = {'in': [(int(item),) for item in input_data]}
    return params


def get_results_from_db(selected_items, consulta_id):
    print(f'\nget_results_from_db: {selected_items}')
    pathfile = path.join(getcwd(), 'Data\\Querying')
    pathfile_manipuation = path.join(getcwd(), 'Data\\Manipulation')
    if consulta_id == -1:
        sql, params = format_sql_from_file(
            path.join(pathfile, 'doenças associadas a fatores de risco por sintomas.sql'),
            selected_items
        )
        headers, results = execute_sql(sql, params, headers=True)
    elif consulta_id == 2:
        sql, params = format_sql_from_file(
            path.join(pathfile, 'quantidade de sintomas para cada categoria.sql'),
            selected_items
        )
        headers, results = execute_sql(sql, params, headers=True)
    elif consulta_id == 3:
        sql, params = format_sql_from_file(
            path.join(pathfile, 'somatorio tratamentos e fatores de risco por doença.sql'),
            selected_items
        )
        headers, results = execute_sql(sql, params, headers=True)
    elif consulta_id == 1:
        sql, params = format_sql_from_file(
            path.join(pathfile, 'interseção de doenças associadas a sintomas e fatores de risco.sql'),
            selected_items
        )
        headers, results = execute_sql(sql, params, headers=True)
    elif consulta_id == 4:
        sql, params = format_sql_from_file(
            path.join(pathfile, 'causas por doenças.sql'),
            selected_items
        )
        headers, results = execute_sql(sql, params, headers=True)
    elif consulta_id == 5:
        sql, params = format_sql_from_file(
            path.join(pathfile_manipuation, 'update doença.sql'),
            selected_items
        )
        headers, results = execute_sql(sql, params, headers=True)
    else:
        raise IndexError('Nenhuma consulta com esse id')
    return results, headers


def pre_render_template(consulta_id):
    print('\npre_render_template')
    filepath = path.join(getcwd(), 'Data\\Querying')
    filepath_manipulation = path.join(getcwd(), 'Data\\Manipulation')
    items, descriptions, input_type, title, placeholder, sql_code = None, None, None, None, None, None
    if consulta_id == -1:
        title = 'Assistente de Diagnóstico de Sintomas e Fatores de Riscos'
        sql = 'SELECT * FROM Sintomas;'
        items = execute_sql(sql)
        descriptions = "Esta consulta permite que você insira uma lista de sintomas que estão sendo experimentados " \
                       "por um paciente. Com base nesses sintomas, a consulta irá gerar uma lista de possíveis " \
                       "doenças que o paciente pode ter. Além disso, a consulta também fornecerá informações sobre " \
                       "os fatores de risco associados a cada doença possível. Isso pode auxiliar os profissionais " \
                       "de saúde a determinar a melhor abordagem para o tratamento e a gestão da condição do " \
                       "paciente."
        input_type = 'single'
        placeholder = 'Sintomas'
        with open(path.join(filepath, 'doenças associadas a fatores de risco por sintomas.sql'),
                  'r', encoding='utf-8') as file:
            sql_code = file.read()
    elif consulta_id == 3:
        title = 'Soma de Tratamentos e de Fatores de Risco por Doença/Categoria'
        descriptions = "Esta consulta fornece um relatório detalhado que lista o número de tratamentos e fatores de " \
                       "risco associados a cada doença, agrupados por categoria de doença. O relatório ajuda a " \
                       "visualizar e entender a magnitude da complexidade do tratamento e os fatores de risco para " \
                       "várias doenças em suas respectivas categorias. A consulta é útil para profissionais de saúde " \
                       "e pesquisadores que desejam analisar o grau de dificuldade no tratamento de diferentes " \
                       "doenças e entender os riscos associados."
        input_type = 'no_input'
        with open(
                path.join(filepath, 'somatorio tratamentos e fatores de risco por doença.sql'),
                'r', encoding='utf-8') as file:
            sql_code = file.read()
    elif consulta_id == 2:
        title = 'Quantidada de Sintomas para cada Categoria de Doença'
        descriptions = "A  consulta pode ser utilizada para entender quais categorias de doenças têm o maior número " \
                       "de sintomas associados, o que pode ser útil para fins de pesquisa médica ou análise de dados " \
                       "em saúde. Por exemplo, se você quiser entender quais categorias de doenças têm a maior " \
                       "variedade de sintomas, esta consulta fornecerá essa informação."
        input_type = 'no_input'
        with open(path.join(filepath, 'quantidade de sintomas para cada categoria.sql'),
                  'r', encoding='utf-8') as file:
            sql_code = file.read()
    elif consulta_id == 1:
        title = 'Intersecção de Doenças relacionadas a Sintomas e Fatores de Risco declarados'
        items = [execute_sql('SELECT * FROM Sintomas;'), execute_sql('SELECT * FROM FatoresDeRisco;')]
        descriptions = 'Com a resposta da consulta, o profissional de saúde tem um ponto de partida para investigar ' \
                       'mais a fundo. Ele pode, por exemplo, buscar mais informações sobre cada doença, como a ' \
                       'descrição, tratamentos possíveis, e até mesmo outras causas e sintomas não mencionados pelo ' \
                       'paciente inicialmente.'
        input_type = 'multi'
        placeholder = ['Sintomas', 'Fatores de Risco']
        with open(path.join(filepath, 'interseção de doenças associadas a sintomas e fatores de risco.sql'),
                  'r', encoding='utf-8') as file:
            sql_code = file.read()
    elif consulta_id == 4:
        title = 'Causas para um conjunto de Doenças declarado'
        items = execute_sql('SELECT * FROM Doencas')
        descriptions = 'Um médico que está tentando identificar a doença de um paciente que apresenta um conjunto de ' \
                       'sintomas que podem estar associados a várias doenças diferentes. Ao identificar as causas ' \
                       'comuns associadas a esse conjunto de doenças, o médico pode ter uma visão mais clara do que ' \
                       'poderia estar causando a condição atual do paciente.'
        input_type = 'single'
        placeholder = 'Doenças'
        with open(path.join(filepath, 'causas por doenças.sql'),
                  'r', encoding='utf-8') as file:
            sql_code = file.read()
    elif consulta_id == 5:
        title = 'Atualize uma Doença'
        items = execute_sql('SELECT * FROM Doencas')
        descriptions = 'Disclaimer: Valores memarente representativos'
        input_type = 'single'
        placeholder = 'Nome Doenças'
        with open(path.join(filepath_manipulation, 'update doença.sql'),
                  'r', encoding='utf-8') as file:
            sql_code = file.read()
    return items, descriptions, input_type, title, placeholder, sql_code


def get_all_tables_data():
    table_names = [table[0] for table in execute_sql('SHOW TABLES;')]
    all_tables_data = {table_name: {"primary_keys": [], "column_names": [], "data": [], "foreign_key_maps": {}}
                       for table_name in table_names}
    for table_name in table_names:
        table = all_tables_data[table_name]
        records = get_table_records(table_name)
        table["column_names"] = list(records[0].keys())
        if len(table["column_names"]) > 2:
            if table_name.lower() == 'fatoresderisco':
                primary_key = 'id_fatorderisco'
            elif table_name == 'CategoriasDeDoencas':
                primary_key = 'id_categoriasdedoencas'
            else:
                primary_key = 'id_' + table_name.lower()[:-1]
            table["primary_keys"].append(primary_key)
        table["data"] = get_table_records(table_name)
        table["foreign_key_maps"] = get_foreign_key_maps(table_name)
    return all_tables_data


def get_table_records(table_name):
    query = f"SELECT * FROM {table_name};"
    cursor.execute(query)
    rows = cursor.fetchall()
    column_names = [i[0] for i in cursor.description]
    records = [dict(zip(column_names, row)) for row in rows]
    return records


def get_foreign_key_maps(table_name):
    query = """
        SELECT 
            k.COLUMN_NAME, k.REFERENCED_TABLE_NAME
        FROM
            INFORMATION_SCHEMA.TABLE_CONSTRAINTS i
        LEFT JOIN
            INFORMATION_SCHEMA.KEY_COLUMN_USAGE k ON i.CONSTRAINT_NAME = k.CONSTRAINT_NAME
        WHERE
            i.TABLE_SCHEMA = DATABASE()
            AND i.CONSTRAINT_TYPE = 'FOREIGN KEY' 
            AND i.TABLE_NAME = %s;
        """
    cursor.execute(query, (table_name,))
    foreign_key_columns = cursor.fetchall()
    foreign_key_tables_dict = {}
    for column, ref_table in foreign_key_columns:
        if ref_table.lower() == 'fatoresderisco':
            query = f'SELECT id_fatorderisco, nome_fatorderisco FROM FatoresDeRisco;'
        elif ref_table == 'CategoriasDeDoencas':
            query = f'SELECT id_categoriasdedoencas, nome_categoriasdedoencas FROM CategoriasDeDoencas;'
        else:
            id_column = 'id_' + ref_table.lower()[:-1]
            name_column = 'nome_' + ref_table.lower()[:-1]
            query = f"SELECT {id_column}, {name_column} FROM {ref_table};"
        cursor.execute(query)
        id_name_pairs = cursor.fetchall()
        foreign_key_tables_dict[column] = id_name_pairs
    return foreign_key_tables_dict


def populate_tables():
    print('\npopulate_tables')
    populate_tables_nome_e_desc()
    with open(path.join(getcwd(), 'Assets\\doenças.json'), encoding='utf-8') as file:
        contents = load(file)
    with open(path.join(getcwd(), 'Data\\Manipulation\\NewDoenca.sql'), encoding='utf-8') as file:
        raw_sql = file.read()
    for content in contents:
        print('&', content)
        print(execute_sql(raw_sql, (content['Nome'], content['Descrição'], content['Categoria'])))
    populate_tables_2_ids()


def populate_tables_nome_e_desc():
    print('\npopulate_tables_nome_e_desc')
    assets_directory = path.join(getcwd(), "Assets\\nome e desc")
    content_files = [json_filepath for json_filepath in listdir(assets_directory) if json_filepath.endswith('.json')]
    print(content_files)
    manipulation_directory = path.join(getcwd(), 'Data\\Manipulation\\nome e desc')
    inserts = [sql_filepath for sql_filepath in listdir(manipulation_directory) if sql_filepath.endswith('.sql')]
    print(inserts)
    for insert, content_file in zip(inserts, content_files):
        with open(path.join(manipulation_directory, insert), 'r', encoding='utf-8') as file:
            raw_sql = file.read()
            print(raw_sql)
        with open(path.join(assets_directory, content_file), 'r', encoding='utf-8') as file:
            contents = load(file)
        for content in contents:
            print(content)
            execute_sql(raw_sql, (content['Nome'], content['Descrição']))


def populate_tables_2_ids():
    print('\npopulate_tables_2_ids')
    assets_directory = path.join(getcwd(), "Assets\\dois ids")
    content_files = [json_filepath for json_filepath in listdir(assets_directory) if json_filepath.endswith('.json')]
    print(content_files)
    manipulation_directory = path.join(getcwd(), 'Data\\Manipulation\\dois ids')
    inserts = [sql_filepath for sql_filepath in listdir(manipulation_directory) if sql_filepath.endswith('.sql')]
    print(inserts)
    for insert, content_file in zip(inserts, content_files):
        with open(path.join(manipulation_directory, insert), 'r', encoding='utf-8') as file:
            raw_sql = file.read()
            print(raw_sql)
        with open(path.join(assets_directory, content_file), 'r', encoding='utf-8') as file:
            contents = load(file)
        for content in contents:
            print(content)
            associado, doenca = content.keys()
            print(content.keys())
            execute_sql(raw_sql, (content[doenca], content[associado]))


def define_db():
    print('\ndefine_db')
    with open('Data/Definition/criação de tabelas.sql', 'r', encoding='utf-8') as file:
        sql_commands = file.read().split(';')
    for sql in sql_commands:
        sql = sql.strip()
        if sql:
            execute_sql(sql)


@atexit.register
def remove_db_conteiner():
    print('\nremove_db_conteiner')
    close_db_connection()
    client = from_env()
    try:
        container = client.containers.get(CONTEINER_NAME)
        container.stop()
        container.remove()
        print('mysql conteiner deleted')
    except NotFound:
        pass
    except APIError:
        pass


if __name__ == '__main__':
    create_db_conteiner()
    define_db()
    populate_tables()
    app.run(host="0.0.0.0", port=8080)
