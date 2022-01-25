# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 16:07:29 2022

@author: manal
"""



import numpy as np
import sympy 

M=sympy.Symbol('M', positive=True)

basis_variables = [] 

basis_variable_column=[] 
def get_columns_to_add(constraint_equality_signs):
   
    columns_to_add=0 
    for equality_symbol_index in range(len(constraint_equality_signs)):
        if constraint_equality_signs[equality_symbol_index] == u"\u2264": #<=
            #ajouter une variable d'écart
            columns_to_add+=1
            
        elif constraint_equality_signs[equality_symbol_index] == u"\u2265": # >=
            #ajouter une variable d'écart et variable artificielle
            columns_to_add+=2
        
        else:#si c'est un signe égal 
            columns_to_add+=1

    return columns_to_add

def get_bigm_matrix(constraint_equality_signs,cmd="maximize"):
 
    columns_to_add=get_columns_to_add(constraint_equality_signs)
    numof_rows_bigm_matrix=len(constraint_equality_signs)+1 
    bigm_matrix = np.zeros((numof_rows_bigm_matrix,columns_to_add), dtype=sympy.Symbol)
   
    introduced_variable_index=0
    for equality_symbol_index in range(len(constraint_equality_signs)):
        if constraint_equality_signs[equality_symbol_index] == u"\u2264":
            #ajouter variable d'écart
            bigm_matrix[equality_symbol_index+1,introduced_variable_index]=1
            introduced_variable_index+=1
            basis_variable_column.append(introduced_variable_index)
            
        elif constraint_equality_signs[equality_symbol_index] == u"\u2265":
            
            bigm_matrix[equality_symbol_index+1,introduced_variable_index]=-1
            introduced_variable_index+=1
            if cmd == "maximiser":
              
                bigm_matrix[0,introduced_variable_index]=-1*M
            else:
              
                bigm_matrix[0,introduced_variable_index]=1*M
                
            bigm_matrix[equality_symbol_index+1,introduced_variable_index]=1
            introduced_variable_index+=1
            basis_variable_column.append(introduced_variable_index)
        
        else:
            #si la contrainte est une égalité, soustraire la variable artificielle si sa maximisation et
             #ajouter une variable artificielle si sa minimisation
            if cmd == "maximiser":
                bigm_matrix[0,introduced_variable_index]=-1*M
            else:
                bigm_matrix[0,introduced_variable_index]=1*M
                
            bigm_matrix[equality_symbol_index+1,introduced_variable_index]=1
            introduced_variable_index+=1
            basis_variable_column.append(introduced_variable_index)
    return bigm_matrix

def get_tableau(orig_matrix,bigm_matrix):

    tableau=np.concatenate((np.array(orig_matrix), bigm_matrix),axis=1)


    numof_tableau_rows,numof_tableau_cols = tableau.shape
    two_empty_rows = np.zeros((2,numof_tableau_cols), dtype=sympy.Symbol)
    tableau=np.concatenate((tableau,two_empty_rows),axis=0)
    
    return tableau

def get_non_basis_variables(orig_matrix):
   
    non_basis_variables=[]
    orig_matrix = np.array(orig_matrix)
    orig_matrix_rows,orig_matrix_cols = orig_matrix.shape
    for i in range(orig_matrix_cols-1):
        non_basis_variables.append(str("x"+str(i+1)))
    return non_basis_variables

def get_added_variables(bigm_matrix):
  
    first_row = bigm_matrix[0]
    ite=1
    added_variables=[]
    artificial_ite=1
    slack_ite = 1
    for i in range(len(first_row)):
        if first_row[i]== -M or first_row[i]== M:
            ite=artificial_ite
            added_variables.append(str("a"+str(ite)))
            artificial_ite+=1
        else: 
            ite=slack_ite
            added_variables.append(str("s"+str(ite)))
            slack_ite+=1
    
    return added_variables

def get_all_variables(orig_matrix,added_variables):
 
    all_variables =["bi"]
    non_basis_variables=get_non_basis_variables(orig_matrix)
    all_variables+=non_basis_variables
    all_variables+=added_variables
    return all_variables

def get_basis_variables(added_variables):
    basis_variables=[]
    for i in range(len(basis_variable_column)):
        basis_variables.append(added_variables[basis_variable_column[i]-1])
    return basis_variables

def get_bi_values(basis_variables,all_variables,tableau):
    cj_value = tableau[0]
    bi_values=[]
    for basis_variable in basis_variables:
        bi_index = all_variables.index(basis_variable)
        bi_value = cj_value[bi_index]
        bi_values.append(bi_value)
    return bi_values
        
def clear_basis_variable_column():
    global basis_variable_column
    basis_variable_column=[]