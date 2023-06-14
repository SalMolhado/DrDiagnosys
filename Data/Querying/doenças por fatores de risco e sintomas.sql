-- Entradas: IDs de Sintomas e IDs de Fatores de Risco.
-- Saídas: Doenças possíveis associadas aos Fatores de Risco.

-- Tabelas envolvidas: Sintomas, Relação Doença-Sintoma, Doenças, FatoresDeRisco, Relação Doença-FatorDeRisco.


SELECT DISTINCT d.nome_doenca
FROM Doencas d
INNER JOIN DoencaSintoma ds ON d.id_doenca = ds.id_doenca
INNER JOIN DoencaFatorDeRisco dfr ON d.id_doenca = dfr.id_doenca
WHERE ds.id_sintoma IN %s AND dfr.id_fatorderisco IN %s