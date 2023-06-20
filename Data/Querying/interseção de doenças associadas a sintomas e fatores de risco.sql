-- Entradas: IDs Fatores de Risco e IDs Sintomas.
-- Saídas: Interseção de Doenças associadas aos Fatores de Risco e aos Sintomas.

-- Tabelas envolvidas: Doenças, DoençaSintoma, DoencaFatorDeRisco.


SELECT D1.nome_doenca
FROM Doencas D1
WHERE D1.id_doenca IN 
(
    SELECT DS.id_doenca 
    FROM DoencaSintoma DS
    WHERE DS.id_sintoma IN %s
) 
AND D1.id_doenca IN 
(
    SELECT DFR.id_doenca 
    FROM DoencaFatorDeRisco DFR
    WHERE DFR.id_fatorderisco IN %s
);
