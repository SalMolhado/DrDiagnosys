-- Entradas: ID de Doença.
-- Saídas: Tratamentos possíveis.

-- Tabelas envolvidas: Doenças, Relação Doença-Tratamento, Tratamentos.


SELECT t.nome_tratamento FROM Tratamentos t
INNER JOIN DoencaTratamento dt ON t.id_tratamento = dt.id_tratamento
WHERE dt.id_doenca = %s