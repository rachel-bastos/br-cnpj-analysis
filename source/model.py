#===================================================================================
# model.py
#
# Purpose: Database schema
#===================================================================================

from sqlalchemy import Column, Integer, BigInteger, Text, create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from decouple import config
conn = '{program}://{user}:{password}@{ip}:{port}/{database}?application_name={app}'.format(
	program=config('program'),
	user=config('user'),
	password=config('password'),
	ip=config('ip'),
	port=config('port'),
	database=config('database'),
	app=config('app_name'))

Base = declarative_base()

def make_session(conection):
	'''
	Method for database insertion
	'''
	engine = create_engine(conection)
	Session = sessionmaker(bind=engine)
	session = Session()
	return session

db = make_session(conn)

class DBop(object):
	'''
	Method for database insert operation
	'''
	def save(self, commit=True):
		"""Save the record."""
		db.add(self)
		if commit:
			db.commit()
		return self

class Companies(DBop, Base):
	__tablename__ = 'companies'

	id = Column(Integer, primary_key=True, unique=True)
	cnpj = Column(BigInteger, unique=True,index=True)
	state = Column(Text)
	name = Column(Text)

class Employees(DBop, Base):
	__tablename__ = 'employees'

	id = Column(Integer, primary_key=True, unique=True)
	position_id = Column(Integer)
	company_cnpj = Column( BigInteger, index=True)
	cpf = Column( BigInteger)
	cpf_cnpj = Column(BigInteger)
	state = Column( Text)
	name = Column(Text, index=True)

class Positions(DBop, Base):
	__tablename__ = 'positions'

	id = Column(Integer, primary_key=True, unique=True)
	position_id = Column(Integer)
	name = Column(Text)


def dict_to_Companies(d):
	'''
	Creates object of class Companies
	'''
	obj = Companies(
	cnpj = d['cnpj'],
	state = d['uf'],
	name = d['nome_empresarial'])

	return obj

def dict_to_Positions(d):
	'''
	Creates object of class Positions
	'''
	obj = Positions(
	position_id = d['qualificacao'],
	name = d['qualificacao_nm'])

	return obj

def dict_to_Employees(d):
	'''
	Creates object of class Employees
	'''
	obj = Employees(
	position_id = d['qualificacao'],
	company_cnpj = d['cnpj'],
	cpf = d['indicador_cpf_cnpj'],
	cpf_cnpj = d['cpf_cnpj_socio'],
	state = d['uf'],
	name = d['nome'])

	return obj