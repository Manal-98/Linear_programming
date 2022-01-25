# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 16:07:29 2022

@author: manal
"""
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
import numpy as np
import sympy
M = sympy.Symbol('M', positive=True)
LARGE_VALUE=99999999

def get_expression_comparable(value):
    
    if type(value) == np.float64 or type(value)==int or type(value)==float:
            comparable_value=value
    else:
        comparable_value=value.subs({M:LARGE_VALUE})  
        
    return comparable_value

def get_maximum_positive_number(row):
    #Assurez-vous que la première ligne du tableau ne contient que des variables non basiques et basiques
    #en supprimant la valeur (dernier élément) et le coefficient de Z (premier élément)
    #row = row[1:]
    coeffs_of_basic_and_non_basic_variables= row[1:]#supprimer le premier élément de la ligne 
    
    #parcourir la première ligne et trouver le nombre négatif maximum
    current_max_pos_num=0 #définir le nombre négatif maximum initial à zéro afin qu'il puisse être remplacé 
    for coeff in coeffs_of_basic_and_non_basic_variables:
        original_value_of_coeff=coeff
        original_value_of_current_max_pos_num=current_max_pos_num
        
        #vérifier si le coeff est un entier ou un flottant. Si c'est le cas, laissez-le comme
        #c'est ou bien c'est une expression de M alors substituez-lui une grande valeur 
        coeff=get_expression_comparable(coeff)
        
        #vérifier si le nombre négatif maximum actuel est un entier ou un flottant. Si c'est le cas,
        #laissez-le tel quel ou bien c'est une expression de M alors remplacez-le par une grande valeur 
        current_max_pos_num =get_expression_comparable(current_max_pos_num)
        
        if coeff > current_max_pos_num:
            current_max_pos_num = original_value_of_coeff
        else:
            current_max_pos_num=original_value_of_current_max_pos_num
            
    return current_max_pos_num

def calculate_zj(tableau,basis):
    #supprimer la fonction objectif
    constraint_tableau = np.delete(tableau,0,0)
    #supprimer cj-zj et zj
    constraint_tableau = np.delete(constraint_tableau,-1,0)
    constraint_tableau = np.delete(constraint_tableau,-1,0)
    
    numof_constraint_tableau_rows,numof_constraint_tableau_columns = constraint_tableau.shape
    zj_row = np.zeros((1,numof_constraint_tableau_columns), dtype=sympy.Symbol)
    
    for i in range(numof_constraint_tableau_rows):
        zj_row = zj_row + basis[i]*constraint_tableau[i]
    
    tableau[-2]=zj_row
    
    return zj_row

def calculate_cj_zj(tableau,basis,cmd="maximiser"):
    #supprimer la fonction objectif
    zj=calculate_zj(tableau,basis)
    objective_function = tableau[0]
    if cmd=="maximiser":
        cj_zj = objective_function - zj
    else:
        cj_zj = zj-objective_function
    tableau[-1]=cj_zj 
    
    return cj_zj

def get_greatest_increase_in_cj_zj_function(tableau):
    cj_zj_row = tableau[-1]
    
    hir= get_maximum_positive_number(cj_zj_row )
    return hir


def get_pivot_col_index(tableau):
    cj_zj_row =tableau[-1] #converti en liste car numpy n'a pas de propriété d'index
    hir= get_maximum_positive_number(cj_zj_row )
    pivot_col_index = list(cj_zj_row).index(hir)
    return pivot_col_index

def get_pivot_row_index(tableau,pivot_col):
    """Now that we have the pivot column, how do we determine the pivot row?
    Divide each row's Right Hand Side column by corresponding pivot value in column
    Find out which row has the minimum non negative number and return that row
    """
    nonneg_nums_after_RHS_division=[]
    
  
    constraint_tableau = np.delete(tableau,0,0)
    
    constraint_tableau = np.delete(constraint_tableau,-1,0)
    constraint_tableau = np.delete(constraint_tableau,-1,0)
    
    
    last_row_on_constraint_tableau_index,last_col_on_constraint_tableau_index=constraint_tableau.shape
    first_col_on_constraint_tableau_index=0
    
  
    for i in range(last_row_on_constraint_tableau_index):
        num_in_bi_on_row_i=constraint_tableau[i,first_col_on_constraint_tableau_index]
        orig_num_in_bi_on_row_i = num_in_bi_on_row_i
        num_in_bi_on_row_i=get_expression_comparable(num_in_bi_on_row_i)
        
        numinpivotcol_on_row_i = constraint_tableau[i,pivot_col]
        orig_numinpivotcol_on_row_i = numinpivotcol_on_row_i 
        numinpivotcol_on_row_i = get_expression_comparable(numinpivotcol_on_row_i )
        try:
            num_after_pivot_div = num_in_bi_on_row_i/numinpivotcol_on_row_i
        except ZeroDivisionError:
            continue
        if num_after_pivot_div > 0:
            num_in_bi_on_row_i = orig_num_in_bi_on_row_i  
            numinpivotcol_on_row_i = orig_numinpivotcol_on_row_i 
            num_after_pivot_div = num_in_bi_on_row_i/numinpivotcol_on_row_i
            
            nonneg_nums_after_RHS_division.append(num_after_pivot_div)
    

    try:
        min_non_neg_num=min(nonneg_nums_after_RHS_division)
    except ValueError:
        return None

   #itérer à nouveau pour trouver la ligne du nombre minimum non négatif en effectuant
     #num_in_bi_on_row_i/numinpivotcol_on_row_i pour voir quelle ligne nous donnera le minimum
     #nombre non négatif que nous venons de déterminer. Quand vous le trouvez, retournez-le
    for i in range(last_row_on_constraint_tableau_index):
        num_in_bi_on_row_i=constraint_tableau[i,first_col_on_constraint_tableau_index]
        numinpivotcol_on_row_i = constraint_tableau[i,pivot_col]
        try:
            num_after_pivot_div = num_in_bi_on_row_i/numinpivotcol_on_row_i
        except ZeroDivisionError:
            continue
        #si num est positif, ajouter aux nombres non négatifs après la division pivot
        if num_after_pivot_div == min_non_neg_num :
            min_non_neg_num_row_index = i+1#1 est ajouté car nous avons supprimé l'objectif fxn
             #qui a fait diminuer son indice dans le tableau d'origine
            break
        
    return min_non_neg_num_row_index

def get_new_pivot_row(tableau,pivot_row_index,pivot_col_index):
    pivot_row = tableau[pivot_row_index]
    pivot_num = tableau[pivot_row_index, pivot_col_index]
    new_pivot_row = pivot_row/pivot_num 
    
    return new_pivot_row

def get_new_rows(tableau,basis,all_variables, basic_variables,pivot_row_index,pivot_col_index):
    new_pivot_row = get_new_pivot_row(tableau,pivot_row_index,pivot_col_index)
    obj_fxn=tableau[0]
#supprimer la fonction objectif
    constraint_tableau = np.delete(tableau,0,0)
    constraint_tableau = np.delete(constraint_tableau,-1,0)
    constraint_tableau = np.delete(constraint_tableau,-1,0)
    last_row_on_tableau_index,last_col_on_tableau_index=constraint_tableau.shape
    last_col_on_tableau_index-=1 # soustraire 1 puisque la numérotation des tableaux commence à partir de zéro
     #saisir une variable de base entrante et supprimer une variable de base sortante
     #basic_variables[pivot_row_index] = all_variables[pivot_col_index ]
     
    
    basic_variables[pivot_row_index-1] = all_variables[pivot_col_index ]
    basis[pivot_row_index-1]=obj_fxn[pivot_col_index]
    
    for i in range(1,last_row_on_tableau_index+1):
        row_to_be_changed = tableau[i]
        num_in_pivot_col_for_row_i = tableau[i,pivot_col_index]
        
        gauss_pivot_row = num_in_pivot_col_for_row_i*-1*new_pivot_row
        new_row = gauss_pivot_row + row_to_be_changed
        tableau[i]=new_row
    
    tableau[pivot_row_index]=new_pivot_row 
    return tableau

def display_answer_variables_and_values(final_tableau, basic_variables):
    answer_variable_and_values=" "
    for i in range(len(basic_variables)):

        print(basic_variables[i],"=",final_tableau[i+1][0])
        answer_variable_and_values += basic_variables[i]+"= "+str(final_tableau[i+1][0]) + "    "
    
    answer_variable_and_values+="Z= "+str(final_tableau[-2][0])
    return answer_variable_and_values

