/*Primeira versão*/

CREATE SEQUENCE seq_recomendacao;

drop table if exists recomendacao;
create table recomendacao (
  id INT NOT NULL DEFAULT nextval('seq_recomendacao'),
  cliente VARCHAR(100) NOT NULL,
  produto VARCHAR(100) NOT NULL,
  ranking INT NOT NULL,
  data_geracao TIMESTAMP NOT NULL,
  data_oferta TIMESTAMP NULL,
  PRIMARY KEY(id)
);

/*Optional test data*/
INSERT INTO recomendacao (cliente, produto, ranking, data_geracao) VALUES ('12345', 'prod1',1,'20171210');
INSERT INTO recomendacao (cliente, produto, ranking, data_geracao) VALUES ('12345', 'prod2',2,'20171210');
INSERT INTO recomendacao (cliente, produto, ranking, data_geracao) VALUES ('12345', 'prod3',3,'20171210');

INSERT INTO recomendacao (cliente, produto, ranking, data_geracao) VALUES ('12345', 'prod4',1,'20171214');
INSERT INTO recomendacao (cliente, produto, ranking, data_geracao) VALUES ('12345', 'prod5',2,'20171214');

select * from recomendacao;
