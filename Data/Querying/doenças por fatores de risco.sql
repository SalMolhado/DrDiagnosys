-- Entradas: IDs de Fatores De Risco.
-- Saídas: Doenças possíveis.

-- Tabelas envolvidas: Fatores de Risco, Relação Doença-FatorRisco, Doenças.


SELECT d.nome_doenca FROM Doencas d
INNER JOIN DoencaFatorDeRisco dfr ON d.id_doenca = dfr.id_doenca
WHERE dfr.id_fatorderisco IN %s