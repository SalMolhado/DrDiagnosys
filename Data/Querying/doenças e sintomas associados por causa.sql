-- Entradas: ID de Causa.
-- Saídas: Doenças e Sintomas associados por Causa.

-- Tabelas envolvidas: Causas, Doencas, DoencaCausa, Sintomas, DoencaSintoma.


SELECT d.nome_doenca, s.nome_sintoma
FROM Doencas d
INNER JOIN DoencaSintoma ds ON d.id_doenca = ds.id_doenca
INNER JOIN Sintomas s ON ds.id_sintoma = s.id_sintoma
INNER JOIN DoencaCausa dc ON d.id_doenca = dc.id_doenca
WHERE dc.id_causa = %s;