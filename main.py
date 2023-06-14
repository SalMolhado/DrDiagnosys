from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import mysql.connector
from json import load
from os import path, listdir, getcwd
from docker import from_env
from docker.errors import DockerException, NotFound, APIError
import atexit


# Define as informações de conexão do banco de dados como variáveis globais
DB_HOST = '127.0.0.1'
DB_USER = 'root'
DB_PASSWORD = 'botafogo'
DB_NAME = 'drdiagnosys'
CONTEINER_NAME = 'drdiagnosys_db'


def create_db_conteiner():
    try:
        client = from_env()
        client.containers.run(
            "mysql:8.0",
            detach=True,
            name=CONTEINER_NAME,
            environment={
                'MYSQL_ROOT_PASSWORD': DB_PASSWORD,
                'MYSQL_DATABASE': DB_NAME
            },
            ports={'3306/tcp': ('127.0.0.1', 3306)},
            auto_remove=True
        )
        print('mysql conteiner created')
    except DockerException:
        pass


app = Flask('__name__')
Bootstrap(app)


def execute_sql(sql: str, params=None):
    connection, cursor = None, None
    rows = ['Deu pau!']
    if params is None:
        params = ()
    try:
        # Conectar ao banco de dados
        connection = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_NAME)
        cursor = connection.cursor()

        # Executa a consulta SQL
        print(f"\n----------- ----------- -----------")
        cursor.execute(sql, params)
        rows = cursor.fetchall()

        # Exibe os resultados
        if rows:
            print(f"\nRows produced by statement '{cursor.statement}':")
            print(rows)
        else:
            print(f"\nNumber of rows affected by statement '{cursor.statement}': {cursor.rowcount}")

    except mysql.connector.Error as error:
        print(f"Something went wrong: {error}")
        if connection is not None:
            # Reverta a transação se algo deu errado
            connection.rollback()

    finally:
        # Certificar-se de que a conexão é fechada
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return rows


def format_sql_from_file(filename, params=None):  # params {'in': [(n), (n), ...], 'equal': [(1,), (2,), ...]}
    # Abre e lê o arquivo
    with open(filename, 'r') as file:
        raw_sql = file.read()

    # Se há parâmetros para inserir na consulta
    if params is not None:
        # Substitui cada %s na consulta SQL por um conjunto de placeholders para cláusulas IN
        if 'in' in params:
            for param_set in params['in']:
                placeholders = ", ".join(["%s"] * len(param_set))
                raw_sql = raw_sql.replace("IN %s", "IN (" + placeholders + ")", 1)

        # Substitui cada %s na consulta SQL para cláusulas EQUAL
        if 'equal' in params:
            for param_set in params['equal']:
                raw_sql = raw_sql.replace("= %s", "= " + str(param_set[0]), 1)

        sql = raw_sql
        # Ajusta a lista de parâmetros para passar para o cursor.execute
        final_params = [item for sublist in params.get('in', []) for item in sublist]

    else:
        sql = raw_sql
        final_params = ()

    return sql, final_params


# --------- W E B ----------
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/consulta/<int:consulta_id>', methods=['GET', 'POST'])
def consulta(consulta_id):
    if request.method == 'POST':
        handle_input = load_input_handling_function(consulta_id)
        selected_items = handle_input(request.form)
        results = get_results_from_db(selected_items, consulta_id)
        return render_template('results.html', results=results)
    elif request.method == 'GET':
        items, descriptions, input_type, title = load_items_from_db(consulta_id)
        return render_template('consulta.html', items=items, descriptions=descriptions,
                               input_type=input_type, nome_consulta=title)


def load_input_handling_function(consulta_id):
    # is meant to return another function that knows how to correctly handle the input for a given consultation ID
    consult_by_id = {1: handle_single_input, 2: handle_list_input}
    # ...
    return consult_by_id[consulta_id]


def handle_single_input(form):
    # Here we assume that the form contains a single input with the name "items"
    # We need to create a tuple for each item because the format_sql_from_file function
    # expects a list of tuples for the 'in' and 'equal' parameters
    input_data = form.get('items')
    # Ensure it's a tuple inside a list inside a dictionary
    params = {'in': [(input_data,)]}
    return params


def handle_list_input(form):
    # Here we assume that the form contains multiple inputs with the name "items"
    # We get a list of inputs and need to create a tuple for each input
    input_data = form.getlist('items')
    # Ensure it's a list of tuples inside a dictionary
    params = {'in': [(item,) for item in input_data]}
    return params


def get_results_from_db(selected_items, consulta_id):
    results = []
    if consulta_id == 1:
        # Execute the SQL query for consulta 1
        # First, format the SQL query from the file using the selected_items as parameters
        sql, params = format_sql_from_file(f'sql/consulta_{consulta_id}.sql', {'in': [selected_items]})
        # Then, execute the SQL query and get the results
        results = execute_sql(sql, params)
    elif consulta_id == 2:
        sql, params = format_sql_from_file(f'Data/Querying/sum tratamentos e sintomas por doença.sql')
        results = execute_sql(sql, params)
    elif consulta_id == 3:
        sql, params = format_sql_from_file(f'Data/Querying/doenças sem tratamento.sql')
        results = execute_sql(sql, params)
    # Add code here for other consultations
    return results


def load_items_from_db(consulta_id):
    items, descriptions, input_type, title = None, None, None, None
    if consulta_id == 1:
        # Fetch all symptom options
        title = 'Assistente de Diagnóstico de Sintomas e Fatores de Riscos'
        sql, params = format_sql_from_file("Data/Querying/doenças associadas a fatores de risco por sintomas.sql")
        items = execute_sql(sql, params)
        descriptions = "Esta consulta permite que você insira uma lista de sintomas que estão sendo experimentados " \
                       "por um paciente. Com base nesses sintomas, a consulta irá gerar uma lista de possíveis " \
                       "doenças que o paciente pode ter. Além disso, a consulta também fornecerá informações sobre " \
                       "os fatores de risco associados a cada doença possível. Isso pode auxiliar os profissionais " \
                       "de saúde a determinar a melhor abordagem para o tratamento e a gestão da condição do " \
                       "paciente."
        input_type = 'multi'
    elif consulta_id == 2:
        title = 'Soma de Tratamentos e de Fatores de Risco por Doença/Categoria'
        items = None
        descriptions = "Esta consulta fornece um relatório detalhado que lista o número de tratamentos e fatores de " \
                       "risco associados a cada doença, agrupados por categoria de doença. O relatório ajuda a " \
                       "visualizar e entender a magnitude da complexidade do tratamento e os fatores de risco para " \
                       "várias doenças em suas respectivas categorias. A consulta é útil para profissionais de saúde " \
                       "e pesquisadores que desejam analisar o grau de dificuldade no tratamento de diferentes " \
                       "doenças e entender os riscos associados."
        input_type = 'no_input'
    elif consulta_id == 3:
        title = 'Doenças sem Tratamentos associados'
        items = None
        descriptions = "Esta consulta tem como objetivo identificar doenças que não possuem tratamentos associados " \
                       "registrados em nosso banco de dados. Ela fornece uma lista de doenças que não possuem nenhum " \
                       "tratamento registrado até o momento. Essas informações podem ser úteis gerenciar o banco de " \
                       "dados. Além disso, a consulta pode ajudar a identificar lacunas no conhecimento médico e " \
                       "direcionar esforços para a descoberta de novas opções de tratamento para essas doenças num " \
                       "universo paralelo."
        input_type = 'no_input'
    # Add code here for other consultations
    return items, descriptions, input_type, title


def populate_tables():
    populate_tables_nome_e_desc()

    # populate doenças
    with open(path.join(getcwd(), 'Assets\\doenças.json')) as file:
        contents = load(file)
    with open(path.join(getcwd(), 'Data\\Manipulation\\NewDoenca.sql')) as file:
        raw_sql = file.read()
    for content in contents:
        execute_sql(raw_sql, (content['Nome'], content['Descrição'], content['Categoria']))

    populate_tables_2_ids()


def populate_tables_nome_e_desc():
    assets_directory = path.join(getcwd(), "Assets\\nome e desc")
    content_files = listdir(assets_directory)

    manipulation_directory = path.join(getcwd(), 'Data\\Manipulation\\nome e desc')
    inserts = listdir(manipulation_directory)

    for insert, content_file in zip(inserts, content_files):
        # Abre e lê o INSERT INTO
        with open(path.join(manipulation_directory, insert), 'r') as file:
            raw_sql = file.read()
        # Abre e lê o JSON
        with open(path.join(assets_directory, content_file), 'r') as file:
            contents = load(file)
        for content in contents:
            execute_sql(raw_sql, (content['nome'], content['desc']))


def populate_tables_2_ids():
    pass


def define_db():
    with open('Data/Definition/criação de tabelas.sql', 'r') as file:
        sql = file.read()
    execute_sql(sql)


@atexit.register
def remove_db_conteiner():
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
