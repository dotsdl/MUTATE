from __future__ import print_function
import pandas as pd
import numpy as np
import random

class Genome(object):
    '''
    Neural Network Definition
    '''

    def __init__(self, data):
        self.data = data

    def create(self):
        '''
        Generate a Genome Definition
        '''
        X,Y = self.data

        X_count = (X.shape[-1] + 1)
        Y_count = (X_count + Y.shape[-1])

        node_genes_labels = ['node','type']                                      # Define Node Labels
        node_genes = [[i, 'sensor'] for i in xrange(1, X_count)]                 # Generate Sensor Nodes
        [node_genes.extend([[i, 'output']]) for i in xrange(X_count, Y_count)]   # Generate Output Nodes
        nodes = pd.DataFrame.from_records(node_genes, columns=node_genes_labels) # Convert Nodes to DataFrame
        connection_genes_labels = ['in','out','weight','enabled','innovation']   # Define Connection Labels
        connection_genes = [[i] for i in xrange(1, Y_count)]                     # Generate Input Connections
        [i.extend([j[0]]) for i in connection_genes for j in node_genes if ('output') in j] # Generate Output Connections
        [i.extend([np.random.uniform(-1.0,1.0)]) for i in connection_genes]                 # Generate Connection Weights
        [i.extend([True]) for i in connection_genes]                                        # Enable Initial Connection Genes
        innovation_count = len([j.extend([i+1]) for i,j in enumerate(connection_genes)])    # Generate Innovation Numbers
        connections = pd.DataFrame.from_records(connection_genes, columns=connection_genes_labels) # Convert Connections to Dataframes
        GENOME = pd.concat([nodes,connections], axis=1)                                            # GENOME = Nodes + Connections

        return GENOME

    def add_node(self,df):
        # Select a synapse to split (and disable the connection), then update innovation numbers
        ## Select a connection from the sensor nodes randomly
        potential_mutations = (df['enabled'] == True) & (df['type'] != ('output'))
        nodes_to_split = potential_mutations[potential_mutations == True].index.tolist()
        split = random.choice(nodes_to_split)
        ## Duplicate the node
        df.loc[len(df)] = df.iloc[(split)]
        dup_node_ix = df.iloc[-1].name
        dup_node_out = df.iloc[-1]['out']
        ## Discover how many nodes exist, then add a new one in sequential order
        new_node_num = list(set(df['node'].tolist()))[-1] + 1
        new_node_out = int(df.iloc[dup_node_ix]['in'])
        innov = list(set(df['innovation'].tolist()))[-1]
        ## Create the new node with weight of (1)
        df.loc[len(df)] = [new_node_num,'hidden',new_node_out,dup_node_out,1,True,(innov + 2)]
        new_node_ix = (df.iloc[-1].name)
        ## Update the duplicated node so it's output is the new node
        df.iloc[dup_node_ix] = df.iloc[dup_node_ix].set_value('out', (df.iloc[new_node_ix]['node']))
        ## Disable the original node
        df.iloc[split] = df.iloc[split].set_value('enabled', False)
        ## Update the duplicated node's innovation number
        df.iloc[dup_node_ix] = df.iloc[dup_node_ix].set_value('innovation', (innov + 1))
        return df

    def add_connection(self,df):
        # Add a new (non-duplicate) connection to the Genome
        ## Select an output or hidden node's index as the outbound connection
        potential_mutations = (df['enabled'] == True) & (df['type'] != ('sensor'))
        nodes_to_connect = potential_mutations[potential_mutations == True].index.tolist()
        node_connect_out = random.choice(nodes_to_connect)
        ## Select a sensor or hidden node as the inbound connection
        potential_mutations = (df['enabled'] == True) & (df['type'] != ('output'))
        nodes_to_connect = potential_mutations[potential_mutations == True].index.tolist()
        node_connect_in = random.choice(nodes_to_connect)
        ## Instantiate the connection gene in the Genome
        innov = (list(set(df['innovation'].tolist()))[-1])
        ## Create the New Connection
        conn = [df.iloc[node_connect_in]['node'],df.iloc[node_connect_in]['type'],df.iloc[node_connect_in]['node'],df.iloc[node_connect_out]['node'],(np.random.uniform(-1.0,1.0)),True,(innov + 1)]
        ## Check for Duplicates
        not_dup = True
        conn_check_A = list(conn[i] for i in [0,2,3])
        conn_check_B = list(conn[i] for i in [0,3])
        for ix,ser in df[['node','in','out']].iterrows():
            if ser.tolist() == conn_check_A:
                not_dup = False
        for ix,ser in df[['node', 'out']].iterrows():
            if ser.tolist() == conn_check_B:
                not_dup = False
        ## If no duplicates, then add the new connection
        if not_dup:
            df.loc[len(df)] = conn
        return df
