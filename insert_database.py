#===================================================================================
# insert_database.py
#
# Purpose: Insert cnpj data into a database
#
# This script assumes:
#     - a file named settings.ini with database configuration      
#     - required data downloaded
#===================================================================================

from model import dict_to_Companies, dict_to_Positions, dict_to_Employees
import jsonlines
import os
import logging

logging.basicConfig(filename = 'cnpj_insert.log',level=logging.INFO)
logger = logging.getLogger()
    
def insert_data(files, table_name):
    '''
    Creates query to perform database search based on entered search parameters

    Arguments:
        files{list} -- list of files to parse and insert on database
        table_name{str} -- database table name for data insertion

    Returns:
        [str] -- search query
    '''
    for file in files:
        try:
            with jsonlines.open(file) as reader:
                for obj in reader:
                    d = reader.read()
                    if table_name == 'Companies':
                        table_data = dict_to_Companies(d)
                    elif table_name == 'Employees':
                        table_data = dict_to_Employees(d)
                    else:
                        table_data = dict_to_Positions(d)
                    table_data.save()
        except Exception as e:
            logger.info(f'{table_name} - {file} -- Error {str(e)}')
            continue


# Companies
logger.info('Processing Companies')
files = [x for x in os.listdir('json_data/companies') if '.json' in x]
insert_data(files, 'Companies')
logger.info('Companies inserted')

# Posiçoes
logger.info('Processing Positions')
insert_data('json_data/positions.json', 'Positions')
logger.info('Positions inserted')  

# Employees
logger.info('Processing Employees')
files = [x for x in os.listdir('json_data/employees') if '.json' in x]
insert_data(files, 'Employees')
logger.info('Employees inserted')