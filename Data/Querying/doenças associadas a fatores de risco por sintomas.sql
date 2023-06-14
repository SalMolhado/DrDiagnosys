-- Entradas: IDs de Sintomas relatados pelo paciente.
-- Saídas: Doenças possíveis e seus fatores de risco associados.

-- Tabelas envolvidas: Sintomas, Relação Doença-Sintoma, Doenças, FatoresDeRisco, Relação Doença-FatorDeRisco.


SELECT d.nome_doenca, fr.nome_fatorderisco 
FROM Doencas d
INNER JOIN DoencaSintoma ds ON d.id_doenca = ds.id_doenca
INNER JOIN DoencaFatorDeRisco dfr ON d.id_doenca = dfr.id_doenca
INNER JOIN FatoresDeRisco fr ON dfr.id_fatorderisco = fr.id_fatorderisco
WHERE ds.id_sintoma IN %s
