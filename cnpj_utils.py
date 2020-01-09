#===================================================================================
# cnpj_utils.py
#
# Purpose: Auxiliary functions to perform cnpj analysis
#===================================================================================

import pandas as pd
from sqlalchemy import create_engine
from decouple import config
import networkx as nx
import matplotlib.pyplot as plt
import sys
import argparse

def make_query(schema, cnpj=None, employee=None, level=5):
    '''
    Creates query to perform database search based on entered search parameters

    Arguments:
        schema -- database schema
        cnpj{int} -- company CNPJ
        employee{str} -- employee fullname
        level{int} -- how deep should the network be

    Returns:
        [str] -- search query
    '''

    # first two levels query
    if cnpj:
        var1 = 'name'
        var2 = 'company_cnpj'
        query = f'with \
            n1 as \
            (select company_cnpj, name from {schema}.employees \
                where company_cnpj = {cnpj}), \
            n2 as \
            (select m.company_cnpj, m.name from {schema}.employees m, n1 \
                where m.name = n1.name and m.company_cnpj != {cnpj})'
    elif employee:
        var1 = 'company_cnpj'
        var2 = 'name'
        query = f'with \
            n1 as \
            (select m.company_cnpj, m.name from {schema}.employees \
                where name = upper({employee})), \
            n2 as \
            (select distinct(m.name) from {schema}.employees m, n1 \
                where m.company_cnpj = n1.company_cnpj and m.name != upper({employee}))'
    else:
        print('No data to search')
        sys.exit()

    if level > 10:
        print('High search level. Consider decreasing to a maximum of 10.')
        sys.exit()

    # remaining levels
    for i in range(3,level+1):
        if i % 2 != 0:
            query = query + f', n{i} as \
            (select m.company_cnpj, m.name from {schema}.employees m, n{i-1} \
                where m.{var2} = n{i-1}.{var2} and m.{var1} not in (select distinct({var1}) from n{i-2}))\
            '
        else:
            query = query + f', n{i} as \
            (select m.company_cnpj, m.name from {schema}.employees m, n{i-1} \
                where m.{var1} = n{i-1}.{var1} and m.{var2} not in (select distinct({var2}) from n{i-2}))'

    return query


def create_data(query, engine, schema, level=5):
    '''
    Creates dataset with all connected companies based on search query result

    Arguments:
        query{str} -- search query obtained with make_query function
        engine -- database conection
        schema -- database schema
        level{int} -- same level used to create the search query 

    Returns:
        [DataFrame] -- dataset with network data
    '''
    data = pd.DataFrame()

    for i in range(1,level):
        q = query + f'select * from n{i};'
        data = pd.read_sql_query(sql=q,con=engine)
        data = pd.concat([data, data])

    return data

def get_positions(data, engine, schema):
    '''
    Returns the position and company name of each employee

    Arguments:
        data{DataFrame} -- dataset with companies network
        engine -- database conection
        schema -- database schema

    Returns:
        [DataFrame] -- dataset with employees informations
    '''

    positions = pd.DataFrame()
    for cnpj,name in data.itertuples(index=False):       
        query = f"select c.name as company, m.name as employee, p.name as position\
        from {schema}.positions p, {schema}.employees m, {schema}.companies c \
        where m.name = '{name}' and m.company_cnpj= {cnpj} and c.cnpj = {cnpj} and p.id = m.position_id"
        
        data = pd.read_sql_query(sql=query,con=engine)
        positions = pd.concat([positions, data])

    return positions

def create_network(data, engine, schema, filename):
    '''
    Creates the network and save the figure

    Arguments:
        data{DataFrame} -- dataset with companies network
        engine -- database conection
        schema -- database schema
        filename{str} -- name to save the figure

    Returns:
        [None]
    '''

    if data.empty:
        return None
    
    nodes = list(data['company'].unique())+ list(data['employee'].unique())
    subset = data[['company', 'employee']]
    edges = [tuple(x) for x in subset.values]

    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    nodes_colors = ['blue']*data['company'].unique().shape[0]+['red']*data['employee'].unique().shape[0]
    edge_labels = {(u, v): d for u, v, d in data.values}
    pos = nx.spring_layout(G)

    # saving the network
    fig = plt.figure(figsize=(20,20)) 
    nx.draw_networkx(G, pos, arrows=False, with_labels=True, 
                    font_weight='bold', font_size=15,
                    node_color=nodes_colors, node_size=1000)
    nx.draw_networkx_edge_labels(G, pos, 
                                edge_labels=edge_labels)
    plt.axis('off')
    
    fig.savefig(f'figure/graph_{str(filename)}.png', format="PNG")