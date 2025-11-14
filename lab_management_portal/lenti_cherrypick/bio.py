import numpy as np
import pandas as pd

def boolConversion(dataFrameinput, trueAs, falseAs):  # converts boolean values to user designation
    """
    converts dataframe values from boolean values to chosen values. 
    """

    mask = dataFrameinput.applymap(type) != bool
    d = {True: trueAs, False: falseAs}
    Output = dataFrameinput.where(mask, dataFrameinput.replace(d)).T

    return Output

def matchesTwo(sourceInput1, sourceInput2, dataframeSlice, lenti_database):

    """
    Matches two dataframes based off 2 criteria
    converts from bool to 1/0 and takes sum
    """
    matchingResults = pd.concat([sourceInput1, sourceInput2], axis=1)
    matchingResults = boolConversion(matchingResults, 1, 0)
    matchingSum = pd.DataFrame(np.sum(matchingResults, axis=0)).T
    matchingResults = pd.concat([matchingResults, matchingSum]).T
    finalOutput = pd.concat([matchingResults, lenti_database], axis=1)
    databaseExport = finalOutput[(finalOutput[0] == 2)]
    databaseExport = databaseExport.iloc[:, dataframeSlice:]  # removes TRUE/FALSE dataframes and SUM column

    return databaseExport

class BioGenerator:
    def __init__(self, lenti_database):
        self.lenti_database = lenti_database
        self.bio_df = pd.DataFrame()

    def create_bio(self, row):

        """
        Creates bioinformatics sheet in dataframe form.  Checks for pooled or arrayed version
        """
        barcode_source = str(row['source barcode'])
        well_source = str(row['source well'])
        well_destination = str(row['destination well'][0])
        barcode_destination = str(row['destination barcode'][0])
        well_project = str(row['Project'])
        project_type = str(row['ARRAY OR POOL'])
        barcode_match = self.lenti_database.iloc[:, 2:10] == barcode_source
        well_match = self.lenti_database.iloc[:, 13] == well_source
        databse_export = matchesTwo(barcode_match, well_match, 20, self.lenti_database)

        if databse_export['Target'].str.contains('C0').any():
            databasePool = databse_export.squeeze()
            matchingLibrary = str(databasePool['Full Plate name'])
            matchingGene = str(databasePool['gene_name'])
            libraryMatch = self.lenti_database.loc[:, 'Full Plate name'] == matchingLibrary
            geneMatch = self.lenti_database.loc[:, 'gene_name'] == matchingGene
            poolCheck = matchesTwo(libraryMatch, geneMatch, 13, self.lenti_database)
            poolCheck['destination well'] = well_destination
            poolCheck['destination barcode'] = barcode_destination
            poolCheck['Library Name'] = well_project
            poolCheck['Library Type'] = project_type
            self.bio_df = pd.concat([self.bio_df, poolCheck], ignore_index=True)

        else:
            databse_export['destination well'] = well_destination
            databse_export['destination barcode'] = barcode_destination
            databse_export['Library Name'] = well_project
            databse_export['Library Type'] = project_type
            self.bio_df = pd.concat([self.bio_df, databse_export])

        return self.bio_df

    def format_bio(self):
        """
        Formats bioinformatics dataframe to match format used by thermofisher.
        """

        self.bio_df = self.bio_df[~self.bio_df.sequence1.str.contains("pool", na=False)]  # removes all rows with pool in sequence
        self.bio_df = self.bio_df[~self.bio_df.status1.str.contains("B", na=False)]  # removes all rows with pool in sequence
        self.bio_df["Total Plates Per Library"] = self.bio_df['destination barcode'].nunique() #retrieves integer value of number of unique values found in column
        self.bio_df['Target'] = self.bio_df['Target'].apply(lambda x: int(x.replace('C', '')))
        preformatted_df = self.bio_df

        self.bio_df = self.bio_df[['Library Name', 'destination well', 'destination barcode', 'Total Plates Per Library', 'crispr_id', 'ncbi_gene', 'gene_name', 'sequence1', 'Target', 'crispr_pam', 'crispr_gc',
                       'chromosome', 'chr_direction', 'chr_start', 'chr_stop', 'exon', 'transcript_id', 'direction',
                       'crispr_start', 'crispr_stop']]
        self.bio_df.sort_values(['destination barcode', 'destination well'], ascending=True, inplace=True)
        self.bio_df = self.bio_df.rename(columns={
                                     'destination barcode': 'Plate Number',
                                     'destination well': 'Well Position',
                                     'crispr_id': "CRISPR ID",
                                     'ncbi_gene': "NCBI Gene",
                                     'gene_name': "Gene Symbol",
                                     'sequence1': "Target Sequence",
                                     'Target': "Target Number",
                                     'crispr_pam': "PAM",
                                     'crispr_gc': f"%GC",
                                     'chromosome': "Chromosome"
                                    })

        self.bio_df['Well Position'] = self.bio_df['Well Position'].apply(lambda x: (str(x[:1]), int(x[1:])))
        self.bio_df['Well Position'] = self.bio_df['Well Position'].apply(lambda x: f'({x[0]},{x[1]})')

        return self.bio_df, preformatted_df