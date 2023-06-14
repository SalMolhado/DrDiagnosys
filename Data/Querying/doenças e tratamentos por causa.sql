-- Entradas: ID de Causa.
-- Saídas: Doenças e respectivos Tratamentos por Causa.

-- Tabelas envolvidas: Causas, Doencas, DoencaCausa, Tratamentos, DoencaTratamento.


SELECT d.nome_doenca, t.nome_tratamento
FROM Doencas d
INNER JOIN DoencaTratamento dt ON d.id_doenca = dt.id_doenca
INNER JOIN Tratamentos t ON dt.id_tratamento = t.id_tratamento
INNER JOIN DoencaCausa dc ON d.id_doenca = dc.id_doenca
WHERE dc.id_causa = %s;