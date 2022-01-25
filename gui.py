# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 16:07:29 2022

@author: manal
"""

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout,QLabel,QComboBox,QPushButton,QHBoxLayout,QSizePolicy
import sympy
import numpy as np
import bigm as bigm
import simplex as sp

M = sympy.Symbol('M', positive=True)
HEADER_SPACE=11

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.setWindowTitle("Solveur simplex")
        self.setStyleSheet("background-color: rgb(183, 240, 255);")
        self.CONSTRAINT_EQUALITY_SIGNS = [u"\u2264", u"\u2265", "="]#vous pouvez choisir soit <=,>=,= pour la contrainte
        self.new_widgets = []
        self.create_ui()
        self.set_ui_layout()
        self.setFixedWidth(self.sizeHint().width()+100)
        self.setWindowFlags(Qt.WindowCloseButtonHint|Qt.WindowMinimizeButtonHint)

    def create_ui(self):
        self.objective_function_label = QLabel("Fontion objective", self)
        self.objective_function_label.setFixedHeight(self.objective_function_label.sizeHint().height())
       
        self.objective_fxn_table = self.create_table(1, 4, ["="], self.create_header_labels(2))
        
        
        z_item = QTableWidgetItem("Z")
        self.objective_fxn_table.setItem(0, 3, z_item)
        z_item.setFlags(Qt.ItemIsEnabled)

        
        self.objective_fxn_table.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.objective_fxn_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.objective_fxn_table.resizeColumnsToContents()
        self.objective_fxn_table.setFixedHeight(self.objective_fxn_table.verticalHeader().length()+self.objective_fxn_table.horizontalHeader().height())

        self.constraints_label = QLabel("Sous Contraintes", self)
        self.constraints_label.setFixedHeight(self.constraints_label.sizeHint().height())
       
        self.constraint_table = self.create_table(2, 4, self.CONSTRAINT_EQUALITY_SIGNS, self.create_header_labels(2))
        self.constraint_table.setFixedHeight(self.constraint_table.sizeHint().height())

        self.answers_label = QLabel()

        self.add_row_btn = QPushButton('Ajout Ligne', self)
        self.add_row_btn.clicked.connect(self.add_row_event)
        self.add_row_btn.setStyleSheet("background-color:rgb(255, 170, 255);\n")
        self.add_col_btn = QPushButton('Ajout Colonne', self)
        self.add_col_btn.clicked.connect(self.add_column_event)
        self.add_col_btn.setStyleSheet("background-color:rgb(255, 170, 255);\n")
        self.del_row_btn = QPushButton("Supprimer ligne", self)
        self.del_row_btn.clicked.connect(self.del_row_event)
        self.del_row_btn.setStyleSheet("background-color:rgb(255, 170, 255);\n")
        self.del_col_btn = QPushButton("Supprimer colonne", self)
        self.del_col_btn.clicked.connect(self.del_col_event)
        self.del_col_btn.setStyleSheet("background-color:rgb(255, 170, 255);\n")
        self.solve_btn = QPushButton('Résoudre', self)
        self.solve_btn.clicked.connect(self.solve_event)
        self.solve_btn.setStyleSheet("background-color:rgb(255, 170, 255);\n")

        self.operation_combo = QComboBox()
        for item in ["Maximiser", "Minimiser"]:
            self.operation_combo.addItem(item)
            self.operation_combo.setStyleSheet("background-color:rgb(255, 170, 255);\n")
        
        self.question_combo = QComboBox()
        for item in ["Question 1", "Question 2", "Question 3"]:
            self.question_combo.addItem(item)
            self.question_combo.setStyleSheet("background-color:rgb(255, 170, 255);\n")

    def set_ui_layout(self):
        vbox_layout1 = QHBoxLayout(self)
        self.vbox_layout2 = QVBoxLayout(self)
        
        vbox_layout1.addWidget(self.question_combo)
        vbox_layout1.addWidget(self.operation_combo)
        vbox_layout1.addWidget(self.add_row_btn)
        vbox_layout1.addWidget(self.add_col_btn)
        vbox_layout1.addWidget(self.del_row_btn)
        vbox_layout1.addWidget(self.del_col_btn)
        vbox_layout1.addWidget(self.solve_btn)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_v_layout = QVBoxLayout(self)
        central_widget.setLayout(main_v_layout)

        self.vbox_layout2.addWidget(self.objective_function_label)
        self.vbox_layout2.addWidget(self.objective_fxn_table)
        self.vbox_layout2.addWidget(self.constraints_label)
        self.vbox_layout2.addWidget(self.constraint_table)
        self.vbox_layout2.addWidget(self.answers_label)

        main_v_layout.addLayout(vbox_layout1)
        main_v_layout.addLayout(self.vbox_layout2)

    def create_table(self, rows, cols,equality_signs=None, horizontal_headers=None,vertical_headers=None):
        table = QTableWidget(self)
        table.setColumnCount(cols)
        table.setRowCount(rows)

        # Set the table headers
        if horizontal_headers:
            table.setHorizontalHeaderLabels(horizontal_headers)
        

        if vertical_headers:
            table.setVerticalHeaderLabels(vertical_headers)

        #ajouter des signes <=,>=,= pour que la personne puisse sélectionner si cette contrainte est <=,>= ou =
         #c'est aussi utilisé pour la fonction objectif mais dans la fonction objectif nous utilisons juste = Z donc un signe [=] est passé
        
        if equality_signs:
            numofrows = table.rowCount()
            numofcols = table.columnCount()
            # add combo items to self.constraint_table
            for index in range(numofrows):
                equality_signs_combo = QComboBox()
                for item in equality_signs:
                    equality_signs_combo.addItem(item)
                table.setCellWidget(index, numofcols - 2, equality_signs_combo)

        table.resizeColumnsToContents()
        table.resizeRowsToContents()

        return table

    def create_header_labels(self,num_of_variables):
        """Name the columns for the tables x1,x2,.... give a space and then add bi"""
        header_labels = [" "*HEADER_SPACE +"x" + str(i + 1) + " " * HEADER_SPACE for i in range(num_of_variables)]
        header_labels.extend([" " * HEADER_SPACE, " " * HEADER_SPACE + "bi" + " " * HEADER_SPACE])
        return header_labels

    def del_row_event(self):
    
        if self.constraint_table.rowCount()>1:
            self.constraint_table.removeRow(self.constraint_table.rowCount()-1)

    def del_col_event(self):
        
        if self.constraint_table.columnCount()>4:
            self.constraint_table.removeColumn(self.constraint_table.columnCount()-3)
            self.objective_fxn_table.removeColumn(self.objective_fxn_table.columnCount()-3)

    def add_column_event(self):
        self.constraint_table.insertColumn(self.constraint_table.columnCount()-2)
        self.objective_fxn_table.insertColumn(self.objective_fxn_table.columnCount()-2)
        self.constraint_table.setHorizontalHeaderLabels(self.create_header_labels(self.constraint_table.columnCount()-2))
        self.objective_fxn_table.setHorizontalHeaderLabels(self.create_header_labels(self.constraint_table.columnCount()-2))
        

        # faire en sorte que la taille de la table de la fonction objective s'adapte parfaitement aux lignes et aux colonnes
        self.objective_fxn_table.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.objective_fxn_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.objective_fxn_table.setFixedHeight(self.objective_fxn_table.verticalHeader().length() + self.objective_fxn_table.horizontalHeader().height())

    def add_row_event(self):
        self.constraint_table.insertRow(self.constraint_table.rowCount())
        equality_signs_combo = QComboBox()
        for item in self.CONSTRAINT_EQUALITY_SIGNS:
            equality_signs_combo.addItem(item)
        self.constraint_table.setCellWidget(self.constraint_table.rowCount()-1,self.constraint_table.columnCount() - 2, equality_signs_combo)
        self.constraint_table.resizeRowsToContents()


    def solve_event(self):
        #supprimer tous les nouveaux widgets créés lors de la résolution d'un problème, comme la table de l'itération
        for item in self.new_widgets:
            item.setParent(None)
            item.deleteLater()

        self.new_widgets=[]
        bigm.clear_basis_variable_column()
        vertical_header=[]


        constraint_equality_signs=self.read_equality_signs(self.constraint_table.columnCount()-2, self.constraint_table)
        #obtenir la commande si c'est maximiser ou minimiser
        command=self.operation_combo.currentText().lower()

        unaugmented_matrix=self.form_unaugmented_matrix()
        bigm_matrix = bigm.get_bigm_matrix(constraint_equality_signs, command)

        tableau = bigm.get_tableau(unaugmented_matrix, bigm_matrix)

        added_variables = bigm.get_added_variables(bigm_matrix)

        all_variables = bigm.get_all_variables(unaugmented_matrix, added_variables)

        basis_variables = bigm.get_basis_variables(added_variables)
        basis = bigm.get_bi_values(basis_variables, all_variables, tableau)

        sp.calculate_zj(tableau, basis)
        sp.calculate_cj_zj(tableau, basis, command)

      
        vertical_header.append("cj       ")
        vertical_header.extend(basis_variables)
        vertical_header.append("zj")
        if command.lower()=="minimiser":
            vertical_header.append("zj-cj")
        else:
            vertical_header.append("cj-zj")

        spaced_all_variables = [" " * HEADER_SPACE + item + " " * HEADER_SPACE for item in all_variables]
        gui_tableau = self.create_gui_for_tableau(tableau,spaced_all_variables,basis_variables)
        current_row,current_col=tableau.shape
        self.vbox_layout2.addWidget(gui_tableau)

        #ajouter le tableau gui aux nouveaux widgets afin qu'il puisse être supprimé lorsque nous résolvons un nouveau problème
        self.new_widgets.append(gui_tableau)

        hir = sp.get_greatest_increase_in_cj_zj_function(tableau)
        hir = sp.get_expression_comparable(hir)

        while hir > 0:  
            pivot_col_index = sp.get_pivot_col_index(tableau)
            pivot_row_index = sp.get_pivot_row_index(tableau, pivot_col_index)
            if pivot_row_index:
                sp.get_new_rows(tableau, basis, all_variables, basis_variables, pivot_row_index, pivot_col_index)
                sp.calculate_zj(tableau, basis)
                sp.calculate_cj_zj(tableau, basis, command)

                hir = sp.get_greatest_increase_in_cj_zj_function(tableau)

                hir = sp.get_expression_comparable(hir)

                vertical_header.append("cj")
                vertical_header.extend(basis_variables)
                vertical_header.append("zj")
                if command.lower() == "minimiser":
                    vertical_header.append("zj-cj")
                else:
                    vertical_header.append("cj-zj")
                self.update_gui_tableau(tableau, gui_tableau,current_row,vertical_header)
                current_row, current_col = tableau.shape
                current_row+= current_row

                self.answers_label.setText(sp.display_answer_variables_and_values(tableau, basis_variables))
            else:
                w = QWidget()
                QMessageBox.warning(w, "Avertissement "," Le problème est illimité. Vérifiez la formulation du problème. Afficher uniquement les itérations.")
                self.answers_label.setText(" ")
                break

    def form_unaugmented_matrix(self):
        obj_fxn = self.get_obj_fxn()
        split1_of_constraints = self.read_table_items(self.constraint_table, 0, self.constraint_table.rowCount(), 0,
                                                      self.constraint_table.columnCount() - 2)
        split2_of_constraints = self.read_table_items(self.constraint_table, 0, self.constraint_table.rowCount(),
                                                      self.constraint_table.columnCount() - 1,
                                                      self.constraint_table.columnCount())
        unaugmented_matrix_without_obj_fxn = np.concatenate((np.array(split2_of_constraints), split1_of_constraints),
                                                            axis=1)
        unaugmented_matrix = np.vstack((obj_fxn, unaugmented_matrix_without_obj_fxn))
        return unaugmented_matrix

    def read_table_items(self,table,start_row,end_row,start_col, end_col):
        read_table = np.zeros((end_row-start_row, end_col-start_col),dtype=sympy.Symbol)
        for i in range(start_row,end_row):
            for j in range(start_col,end_col):
                read_table[i-end_row][j-end_col] = float(table.item(i, j).text())

        return read_table

    def read_equality_signs(self,equality_signs_column,table):
        equality_signs=[]
        for i in range(table.rowCount()):
            equality_signs.append(table.cellWidget(i, equality_signs_column).currentText())
        return equality_signs

    def populatetable(self,table, mylist, start_row, end_row, start_col, end_col):
        for i in range(start_row, end_row):
            for j in range(start_col, end_col):
                table.setItem(i, j, QTableWidgetItem(str(mylist[i - end_row][j - end_col])))
        table.resizeColumnsToContents()

    def get_obj_fxn(self):
        obj_fxn_coeff=self.read_table_items(self.objective_fxn_table, 0,self.objective_fxn_table.rowCount(), 0, self.objective_fxn_table.columnCount()-2)
        obj_fxn = np.insert(obj_fxn_coeff,0,0)
        return obj_fxn

    def create_gui_for_tableau(self,tableau,all_variables,vertical_headers):
        rows,cols=tableau.shape
        gui_tableau=self.create_table(rows, cols, equality_signs=None,horizontal_headers=all_variables,vertical_headers=vertical_headers)
        self.populatetable(gui_tableau, tableau, 0,rows, 0, cols)
        return gui_tableau

    def update_gui_tableau(self,tableau,gui_tableau,current_row,vertical_headers):
        
        rows, cols = tableau.shape
        for i in range(rows):
            gui_tableau.insertRow(gui_tableau.rowCount())
        self.populatetable(gui_tableau, tableau, current_row, current_row+rows, 0,cols)
        gui_tableau.setVerticalHeaderLabels(vertical_headers)



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())