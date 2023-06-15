-- Saídas:

-- Tabelas envolvidas: CategoriasDeDoencas, Doencas, DoencaSintoma.


SELECT C.nome_categoriasdedoencas, COUNT(DS.id_sintoma) as number_of_sintomas
FROM CategoriasDeDoencas C
JOIN Doencas D on C.id_categoriasdedoencas = D.id_categoriadedoenca
JOIN DoencaSintoma DS on D.id_doenca = DS.id_doenca
GROUP BY C.nome_categoriasdedoencas;