#===================================================================================
# cnpj_search.py
#
# Purpose: Build a network of relationships between members and companies.
#
# This script assumes:
#     - a file named settings.ini with database configuration      
#     - a folder structure as described on README
#===================================================================================

import pandas as pd
from sqlalchemy import create_engine
from decouple import config
import sys
import argparse

from model import conn
from cnpj_utils import make_query, create_data, get_positions, create_network

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--cnpj', help='company cnpj', type=str)
parser.add_argument('-e', '--employee', help='employee name', type=str)
parser.add_argument('-l', '--level', help='search level', type=int)

# db connection
engine = create_engine(conn)
schema = 'cnpj'


if __name__ == '__main__':
    
    args = parser.parse_args()

    cnpj = int(args.cnpj)
    employee = str(args.employee).upper()
    level = int(args.level)

    filename = str(cnpj) if cnpj else employee
    query = make_query(schema, cnpj=cnpj, employee=employee, level=level)
    data = create_data(query, engine, schema, level)
    positions = get_positions(data, engine, schema)
    positions.to_csv(f'network/companie_network_{filename}.csv', index = False)
    create_network(positions, engine, schema, filename)