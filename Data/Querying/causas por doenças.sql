-- Entradas: IDs de Doenças.
-- Saídas: Causas associadas.

-- Tabelas envolvidas: DoençaCausa, Causas.


SELECT C.nome_causa 
FROM Causas C
WHERE C.id_causa IN 
(
    SELECT DC.id_causa 
    FROM DoencaCausa DC
    WHERE DC.id_doenca IN %s
);