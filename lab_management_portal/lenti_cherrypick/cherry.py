import numpy as np
import pandas as pd

def plate_map(input_cherry_pick):
    """
    Creates plate map based off each row exported from database
    :param input_cherry_pick: cherry pick output that plate map will be based off of
    :return: plate map
    """
    input_cherry_pick = input_cherry_pick[['gene_name',
                                           'Target',
                                           'destination well',
                                           'destination barcode']].reset_index(drop=True)
    
    convertedCoord = pd.DataFrame(input_cherry_pick['destination well'].apply(lambda x: list(x)))
    convertedCoord = pd.DataFrame(convertedCoord['destination well'].apply(lambda x: (str(x[0]), int(x[1] + x[2]))))
    destWell1, destWell2 = convertedCoord['destination well'].apply(lambda x: str(x[0])), \
                           convertedCoord['destination well'].apply(lambda x: int(x[1]))
    final_sheet = pd.concat([destWell1,
                             destWell2,
                             input_cherry_pick['destination barcode'],
                             input_cherry_pick['gene_name'],
                             input_cherry_pick['Target']], axis=1)
    final_sheet.columns = ['a', 'b', 'c', 'd', 'e']
    final_sheet['c'] = final_sheet['c'].apply(lambda x: str(x))
    final_sheet['coordinate'] = final_sheet['a'] + final_sheet['c']
    plateMapComplete = pd.DataFrame(columns=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], index=final_sheet['coordinate'])
    plateMapComplete = plateMapComplete[~plateMapComplete.index.duplicated(keep='first')]
    print('Generating Plate map')

    for i, row in final_sheet.iterrows():
        columnNumber = row['b']
        geneName = row['d']
        targetName = row['e']
        coordinateName = row['coordinate']
        fullName = geneName + '-' + targetName
        plateMapComplete.at[coordinateName, columnNumber] = fullName

    plateMapComplete.reset_index(inplace=True)
    plateMapComplete['coordinate'] = pd.DataFrame(plateMapComplete['coordinate'].apply(lambda x: (str(x[:1]),
                                                                                                  int(x[1:]))
                                                                                       )
                                                  )
    plateMapComplete['plate_row'], plateMapComplete['plate_num'] = plateMapComplete['coordinate'].apply(lambda x: x[0]), \
                                                                   plateMapComplete['coordinate'].apply(lambda x: x[1])
    plateMapComplete['plate_cnt'] = max(plateMapComplete['plate_num'])
    plateMapComplete['plate_template'] = ''
    plateMapComplete['plate_plan_id'] = ''
    plateMapComplete['plate_plan_name'] = ''
    plateMapComplete['sku'] = ''
    plateMapComplete['lot'] = ''
    plateMapComplete['plate_id'] = ''
    plateMapComplete.rename(columns={1: 'col_1',
                                     2: 'col_2',
                                     3: 'col_3',
                                     4: 'col_4',
                                     5: 'col_5',
                                     6: 'col_6',
                                     7: 'col_7',
                                     8: 'col_8',
                                     9: 'col_9',
                                     10: 'col_10',
                                     11: 'col_11',
                                     12: 'col_12'}, inplace=True
                            )
    plateMapComplete = plateMapComplete[['plate_plan_id',
                                         'plate_plan_name',
                                         'sku',
                                         'lot',
                                         'plate_id',
                                         'plate_num',
                                         'plate_cnt',
                                         'plate_template',
                                         'plate_row',
                                         'col_1',
                                         'col_2',
                                         'col_3',
                                         'col_4',
                                         'col_5',
                                         'col_6',
                                         'col_7',
                                         'col_8',
                                         'col_9',
                                         'col_10',
                                         'col_11',
                                         'col_12']]
    plateMapComplete.reset_index(inplace=True, drop=True)
    
    return plateMapComplete

class InputIter:
    def __init__(self, database_input, replicate_choice, preferred_library):
        self.database_input = database_input
        self.replicate_choice = replicate_choice
        self.preferred_library = preferred_library
        self.match_threshold = 1

    def find_exact_match(self, matching_row, id_label, exclude_type):
        """
        Find exact match within database.  contains conditional checks for if no match, bypassed match are found
        For loop section enumerates throughl library preference list picks library that is matched first.
        """
        non_existant_target = pd.DataFrame()
        bypassed_target = pd.DataFrame()
        prefered_match = pd.DataFrame()
        bypassed_label, excluded_label = exclude_type

        cherry_match = self.database_input.loc[:,id_label] == int(matching_row['CRISPR ID OR ENTREZ ID'])  # returns boolean array
        cherry_match = pd.DataFrame(cherry_match).T
        cherry_match = cherry_match.rename(index={id_label:'match_results'}).T
        final_output = pd.concat([cherry_match, self.database_input], axis=1)
        final_output = final_output[final_output['match_results'] != False]

        database_export = final_output.drop('match_results', axis=1)
        multiple_dataframe = pd.concat([matching_row, database_export], axis=1)
        database_export = database_export[~database_export['status1'].str.contains(excluded_label)]

        if database_export.empty:
            non_existant_target = pd.concat([non_existant_target, matching_row], axis=1)

        elif database_export.status1.str.contains("B").any():
            database_export_bypass = database_export[database_export['status1'].str.contains(bypassed_label)].reset_index()
            database_export = database_export[~database_export['status1'].str.contains(bypassed_label)]
            bypassed_target = pd.concat([matching_row, database_export_bypass], axis=1)

        match_found = False
        for i, library_item in enumerate(self.preferred_library['Library'].tolist()):
            for j, export_item in enumerate(database_export['Library'].tolist()):
                if export_item == library_item:
                    prefered_match = pd.DataFrame(database_export.iloc[j]).T
                    match_found = True

            if match_found:
                break

        prefered_match.reset_index(inplace=True, drop=True)

        return prefered_match, multiple_dataframe, bypassed_target, non_existant_target

    def find_plate_by_replicate(self, scan_input):
        """
        find plate by user replicate choice
        :param scan_input: dataframe that contains all matched items
        :return: dataframe that contains cherry_pick
        """
        Output = []  # create empty list
        rt = 0
        print('Finding Plate(s)')
        for k, row2 in scan_input.iterrows():
            row2 = pd.DataFrame(row2).T
            pool_selection = pd.DataFrame(row2)
            if row2['Target'].str.contains('C0').any():  # if column 'Pool' contains True then pick pool
                if self.replicate_choice == 1:  # pick replicate plate based off user input
                    pool_check = pool_selection.loc[:, pool_selection.columns.intersection(['destination well',
                                                                                            'destination barcode',
                                                                                            'Pooled R1',
                                                                                            'position'])]
                elif self.replicate_choice == 2:
                    pool_check = pool_selection.loc[:, pool_selection.columns.intersection(['destination well',
                                                                                            'destination barcode',
                                                                                            'Pooled R2',
                                                                                            'position'])]
                elif self.replicate_choice == 3:
                    pool_check = pool_selection.loc[:, pool_selection.columns.intersection(['destination well',
                                                                                            'destination barcode',
                                                                                            'Pooled R3',
                                                                                            'position'])]
                Output.append([pool_check])
                rt += 1
                
            else:  # if column  'Pool' contains False then pick array
                if self.replicate_choice == 1:  # pick replicate plate based off user input
                    pool_check = pool_selection.loc[:, pool_selection.columns.intersection(['destination well',
                                                                                            'destination barcode',
                                                                                            'Arrayed R1',
                                                                                            'position'])]
                elif self.replicate_choice == 2:
                    pool_check = pool_selection.loc[:, pool_selection.columns.intersection(['destination well',
                                                                                            'destination barcode',
                                                                                            'Arrayed R2',
                                                                                            'position'])]
                elif self.replicate_choice == 3:
                    pool_check = pool_selection.loc[:, pool_selection.columns.intersection(['destination well',
                                                                                            'destination barcode',
                                                                                            'Arrayed R3',
                                                                                            'position'])]
                Output.append([pool_check])
                rt += 1

        print('%s for Cherrypick Output' % rt)
        replicateExport = pd.DataFrame(np.array(Output).reshape(len(Output), 4))
        replicateExport['tube barcode'] = ''
        cherrypickBiomek = replicateExport[[0, 1, 'tube barcode', 2, 3]]
        cherrypickBiomek = cherrypickBiomek.rename(columns={0: 'source barcode',
                                                            1: 'source well',
                                                            2: 'destination barcode',
                                                            3: 'destination well'})
        

        cherrypickBiomek = pd.DataFrame(cherrypickBiomek)
        cherrypickBiomek['source barcode'] = cherrypickBiomek['source barcode'].astype(np.int64)

        return cherrypickBiomek
