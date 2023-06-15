from os import path, listdir, getcwd
from json import load, dump

assets_directory = path.join(getcwd(), "Assets\\nome e desc")
contents = listdir(assets_directory)


def sintoma_doenca_json():
    with open(path.join(getcwd(), 'Assets\\doenças.json'), 'r', encoding='utf-8') as file:
        json_doenca = load(file)

    with open(path.join(assets_directory, 'sintomas.json'), 'r', encoding='utf-8') as file:
        json_sintomas = load(file)

    with open(path.join(getcwd(), 'Assets\\dois ids\\sintomas rascunho.json'), 'r', encoding='utf-8') as file:
        json_relacao = load(file)

    # fazer dict com chave: nome do sintoma, valor: id com sintomas.json
    # para cada sintoma em sintomas rascunho.json, appender para lista de DoencaSintomas cada doenca id com o id do sintoma

    id_por_sintoma = {sintoma['Nome']: id for id, sintoma in enumerate(json_sintomas, start=1)}

    relacoes = []
    for sintoma in json_relacao:
        for id_doenca in sintoma['Doenças Associadas']:
            relacao = {'Sintoma': id_por_sintoma[sintoma['Nome']], 'Doenca': id_doenca}
            relacoes.append(relacao)

    dump(relacoes, open('Assets\\dois ids\\DoencaSintoma.json', 'w'))


def fator_doenca_json():
    with open(path.join(assets_directory, 'fatores de risco.json'), 'r', encoding='utf-8') as file:
        json_fatores = load(file)

    fatores = []
    relacoes = []
    for id, fator_dict in enumerate(json_fatores, start=1):
        fatores.append({'Nome': fator_dict['Nome'], 'id': id})

    id_por_fator = {fator['Nome']: id for id, fator in enumerate(json_fatores, start=1)}


    with open(path.join(getcwd(), 'Assets\\dois ids\\fatores rascunho.json'), 'r', encoding='utf-8') as file:
        relacoes_json = load(file)

    for fator in relacoes_json:
        for id_doenca in fator['Doenças Associadas']:
            relacao = {'Fator': id_por_fator[fator['Nome']], 'Doenca': id_doenca}
            relacoes.append(relacao)

    dump(relacoes, open('Assets\\dois ids\\DoencaFatorDeRisco.json', 'w'))


def causa_doenca_json():
    with open(path.join(assets_directory, 'causas.json'), 'r', encoding='utf-8') as file:
        json_causas = load(file)

    causas = []
    for id, causa_dict in enumerate(json_causas, start=1):
        causas.append(causa_dict['Nome'])

    id_por_causa = {causa['Nome']: id for id, causa in enumerate(json_causas, start=1)}

    print(', '.join(causas))

    with open(path.join(getcwd(), 'Assets\\dois ids\\causas rascunho.json'), 'r', encoding='utf-8') as file:
        relacoes_json = load(file)

    relacoes = []
    for causa in relacoes_json:
        for id_doenca in causa['Doenças Associadas']:
            relacao = {'Causa': id_por_causa[causa['Nome']], 'Doenca': id_doenca}
            relacoes.append(relacao)

    dump(relacoes, open('Assets\\dois ids\\DoencaCausa.json', 'w'))


with open(path.join(getcwd(), 'Assets\\nome e desc\\tratamentos.json'), 'r', encoding='utf-8') as file:
    json_tratamento = load(file)

tratamento = []
for id, tratamento_dict in enumerate(json_tratamento, start=1):
    tratamento.append(tratamento_dict['Nome'])

id_por_tratamento = {tratamento['Nome']: id for id, tratamento in enumerate(json_tratamento, start=1)}

with open(path.join(getcwd(), 'Assets\\dois ids\\tratamentos rascunho.json'), 'r', encoding='utf-8') as file:
    relacoes_json = load(file)

relacoes = []
for tratamento in relacoes_json:
    for id_doenca in tratamento['Doenças Associadas']:
        relacao = {'Causa': id_por_tratamento[tratamento['Nome']], 'Doenca': id_doenca}
        relacoes.append(relacao)

dump(relacoes, open('Assets\\dois ids\\DoencaTratamento.json', 'w'))
