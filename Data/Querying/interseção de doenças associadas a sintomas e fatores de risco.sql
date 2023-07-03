-- Entradas: IDs Fatores de Risco e IDs Sintomas.
-- Saídas: Interseção de Doenças associadas aos Fatores de Risco e aos Sintomas.

-- Tabelas envolvidas: Doenças, DoençaSintoma, DoencaFatorDeRisco.


SELECT D.nome_doenca
FROM Doencas D
WHERE D.id_doenca IN 
(
    SELECT DS.id_doenca 
    FROM DoencaSintoma DS
    WHERE DS.id_sintoma IN %s
) 
AND D.id_doenca IN 
(
    SELECT DFR.id_doenca 
    FROM DoencaFatorDeRisco DFR
    WHERE DFR.id_fatorderisco IN %s
);

-- 3/7 ~ também poderia ser:
--SELECT D.nome_doenca
--FROM Doencas D
--JOIN DoencaSintoma DS ON D.id_doenca = DS.id_doenca
--JOIN DoencaFatorDeRisco DFR ON D.id_doenca = DFR.id_doenca
--WHERE DS.id_sintoma IN %s
--AND DFR.id_fatorderisco IN %s
--GROUP BY D.nome_doenca;
