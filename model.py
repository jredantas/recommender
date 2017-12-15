#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 18:23:59 2017

@author: 09959295800
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date

Base = declarative_base()

class Recomendacao(Base):
    __tablename__ = 'recomendacao'

    id = Column(Integer, primary_key=True)
    cliente = Column(String)
    produto = Column(String)
    rank = Column(Integer)
    data_geracao = Column(Date)
    data_oferta = Column(Date)

    def __init__(self, cliente, produto, rank, data_geracao, data_oferta):
        self.cliente = cliente
        self.produto = produto
        self.rank = rank
        self.data_geracao = data_geracao
        self.data_oferta = data_oferta
