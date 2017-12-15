CREATE DATABASE db_recommender
  DEFAULT CHARACTER SET utf8
  DEFAULT COLLATE utf8_unicode_ci;

use db_recommender;

/*Primeira versão*/
drop table if exists recomendacao;
create table recomendacao (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  cliente VARCHAR(100) NOT NULL,
  produto VARCHAR(100) NOT NULL,
  rank INT NOT NULL,
  data_geracao TIMESTAMP NOT NULL,
  data_oferta TIMESTAMP NULL
);

INSERT INTO recomendacao (cliente, produto, rank, data_geracao) VALUES ('12345', 'prod1',1,'20171210');
INSERT INTO recomendacao (cliente, produto, rank, data_geracao) VALUES ('12345', 'prod2',2,'20171210');
INSERT INTO recomendacao (cliente, produto, rank, data_geracao) VALUES ('12345', 'prod3',3,'20171210');

select * from recomendacao;
