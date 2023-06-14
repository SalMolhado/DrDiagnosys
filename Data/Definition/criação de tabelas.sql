CREATE TABLE Doencas 
( 
 id_doenca INT AUTO_INCREMENT,  
 nome_doenca VARCHAR(50) NOT NULL,  
 descricao_doenca VARCHAR(300) NOT NULL,  
 id_categoriadedoenca INT NOT NULL,  
 PRIMARY KEY (id_doenca),
 UNIQUE (nome_doenca)
); 

CREATE TABLE Sintomas 
( 
 id_sintoma INT AUTO_INCREMENT,  
 descricao_sintoma VARCHAR(300) NOT NULL,  
 nome_sintoma VARCHAR(50) NOT NULL,  
 PRIMARY KEY (id_sintoma),
 UNIQUE (nome_sintoma)
); 

CREATE TABLE Causas 
( 
 id_causa INT AUTO_INCREMENT,  
 nome_causa VARCHAR(50) NOT NULL,  
 descricao_causa INT,    
 PRIMARY KEY (id_causa),
 UNIQUE (nome_causa)
); 

CREATE TABLE FatoresDeRisco 
( 
 id_fatorderisco INT AUTO_INCREMENT,  
 nome_fatorderisco VARCHAR(50) NOT NULL,  
 descricao_fatorderisco VARCHAR(300) NOT NULL,  
 PRIMARY KEY (id_fatorderisco),
 UNIQUE (nome_fatorderisco)
); 

CREATE TABLE Tratamentos 
( 
 id_tratamento INT AUTO_INCREMENT,  
 nome_tratamento VARCHAR(50) NOT NULL,  
 descricao_tratamento VARCHAR(300) NOT NULL,  
 PRIMARY KEY (id_tratamento),
 UNIQUE (nome_tratamento)
); 

CREATE TABLE CategoriasDeDoencas 
( 
 id_categoriasdedoencas INT AUTO_INCREMENT,  
 nome_categoriasdedoencas VARCHAR(50) NOT NULL,  
 descricao_categoriasdedoencas VARCHAR(300) NOT NULL,  
 PRIMARY KEY (id_categoriasdedoencas),
 UNIQUE (nome_categoriasdedoencas)
); 

CREATE TABLE DoencaSintoma 
( 
 id_doenca INT,  
 id_sintoma INT,  
 PRIMARY KEY (id_doenca, id_sintoma)
); 

CREATE TABLE DoencaCausa 
( 
 id_doenca INT,  
 id_causa INT,  
 PRIMARY KEY (id_doenca, id_causa)
); 

CREATE TABLE DoencaFatorDeRisco 
( 
 id_doenca INT,  
 id_fatorderisco INT,  
 PRIMARY KEY (id_doenca, id_fatorderisco)
); 

CREATE TABLE DoencaTratamento 
( 
 id_doenca INT,  
 id_tratamento INT,  
 PRIMARY KEY (id_doenca, id_tratamento)
); 

ALTER TABLE Doencas ADD FOREIGN KEY(id_categoriadedoenca) REFERENCES CategoriasDeDoencas (id_categoriasdedoencas);
ALTER TABLE DoencaSintoma ADD FOREIGN KEY(id_doenca) REFERENCES Doencas (id_doenca);
ALTER TABLE DoencaSintoma ADD FOREIGN KEY(id_sintoma) REFERENCES Sintomas (id_sintoma);
ALTER TABLE DoencaCausa ADD FOREIGN KEY(id_doenca) REFERENCES Doencas (id_doenca);
ALTER TABLE DoencaCausa ADD FOREIGN KEY(id_causa) REFERENCES Causas (id_causa);
ALTER TABLE DoencaFatorDeRisco ADD FOREIGN KEY(id_doenca) REFERENCES Doencas (id_doenca);
ALTER TABLE DoencaFatorDeRisco ADD FOREIGN KEY(id_fatorderisco) REFERENCES FatoresDeRisco (id_fatorderisco);
ALTER TABLE DoencaTratamento ADD FOREIGN KEY(id_doenca) REFERENCES Doencas (id_doenca);
ALTER TABLE DoencaTratamento ADD FOREIGN KEY(id_tratamento) REFERENCES Tratamentos (id_tratamento);
