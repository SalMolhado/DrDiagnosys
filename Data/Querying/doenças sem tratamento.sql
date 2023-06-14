-- Saídas: Doenças sem Tratamento associado.

-- Tabelas: Doenças, DoençaTratamentos.


SELECT d.nome_doenca
FROM Doencas d
LEFT JOIN DoencaTratamento dt ON d.id_doenca = dt.id_doenca
WHERE dt.id_tratamento IS NULL;
