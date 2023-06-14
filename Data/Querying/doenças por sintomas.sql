-- Entradas: IDs de Sintomas.
-- Saídas: Doenças possíveis.

-- Tabelas envolvidas: Sintomas, Relação Doença-Sintoma, Doenças.


SELECT d.nome_doenca FROM Doencas d
INNER JOIN DoencaSintoma ds ON d.id_doenca = ds.id_doenca
WHERE ds.id_sintoma IN %s