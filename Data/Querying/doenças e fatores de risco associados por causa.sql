-- Entradas: ID de Causa.
-- Saídas: Doenças e Fatores De Risco associados por Causa.

-- Tabelas envolvidas: Causas, Doencas, DoencaCausa, FatoresDeRisco, DoencaFatorDeRisco.


SELECT d.nome_doenca, fr.nome_fatorderisco
FROM Doencas d
INNER JOIN DoencaFatorDeRisco dfr ON d.id_doenca = dfr.id_doenca
INNER JOIN FatoresDeRisco fr ON dfr.id_fatorderisco = fr.id_fatorderisco
INNER JOIN DoencaCausa dc ON d.id_doenca = dc.id_doenca
WHERE dc.id_causa = %s;