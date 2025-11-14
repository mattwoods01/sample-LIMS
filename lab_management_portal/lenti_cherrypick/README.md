Tool used to create cherrypick csv files

<u>**REQUIRED FIELDS:**</u>

1. **ARRAY OR POOL** - Designate a sample as either Arrayed or Pooled.

2. **Species** - Species name ex. Human.

3. **CRIPSR ID OR ENTREZ ID** - Integer value that matches to corresponding CRISPR or ENTREZ/NCBI ID.

4. **Plate** - Integer value that determines which sample plate is on.

5. **Well Position** - String values in range of A01 - A12 to H01 - H12 to represent wells on 96 well plate.

6. **Project** - Integer value that determines which row from project tracker page is used to fill out Bioinformatic and COA generation sheets.

<u>**HOW TO VIEW LENTIARRAY CATALOGUE:**</u>

1. Click **Lentiarray Catalogue** to view the catalogue of all targets, both pooled and single

<u>**HOW TO CHANGE LIBRARY PREFERENCES RANKING:**</u>

1. Pre-established list will display when program is first loaded.

2. To change, simply type in library that you wish to have preference over others when running matching to database from input form.  
    1. Pop-up will display asking for confirmation of choice.

<u>**HOW TO RUN CHERRYPICK:**</u>

1. Wait for Notification saying **Cherrypick Tool ready to use** before running cherrypick

2. Click **Choose File** to upload excel formatted file with headers matching the ones in the required fields section
    1. Can also manually input information into form table.

3. Table will autopopulate with excel information or will have user-inputted information
    1. Can check and change values before running Cherrypick

4. Click **Run Cherrypick** to begin Cherrypick
    1.  Can uncheck sheet boxes if you do not want to generate bioinformatic or Coverage analysis files

    2. If generating COA files, **Generate bioinformatics sheet** must also be checked as well
        1. Do not need to check **Generate COA sheet(s)** if user only wants bioinformatic sheet option

    3.  Can change **Replicate plate** value if user wishes to pull from other plates 

5. Cherrypick program will display **Finished** once process is complete


