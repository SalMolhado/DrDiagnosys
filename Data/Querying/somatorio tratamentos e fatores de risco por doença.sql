-- Saídas: Total de Tratamentos e de Fatores de Risco por Doença e de grátis a Categoria da Doença.

-- Tabelas envolvidas: Doencas, CategoriasDeDoencas, DoencaTratamento, DoencaFatorDeRisco.


SELECT
    cat.nome_categoriasdedoencas,
    d.nome_doenca,
    COUNT(DISTINCT dt.id_tratamento) AS num_tratamentos,
    COUNT(DISTINCT dfr.id_fatorderisco) AS num_fatores_risco
FROM Doencas d
INNER JOIN CategoriasDeDoencas cat ON d.id_categoriadedoenca = cat.id_categoriasdedoencas
LEFT JOIN DoencaTratamento dt ON d.id_doenca = dt.id_doenca
LEFT JOIN DoencaFatorDeRisco dfr ON d.id_doenca = dfr.id_doenca
GROUP BY cat.nome_categoriasdedoencas, d.nome_doenca;