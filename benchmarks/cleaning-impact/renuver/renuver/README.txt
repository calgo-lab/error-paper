%%%%%%%%%%%%%%%%%%%%%% Folder organization %%%%%%%%%%%%%%%%%%%%%%

root
	Renuver.jar		%JAR file of RENUVER

	Dataset			%folder containing the missing values injected datasets	

	Logs			%folder containing logs about each execution

	Populated		%folder containing CSV files with the imputation results where 
				expected values are compared with the imputed ones
	
	ImputationResults	%folder containing TXT files reporting for each imputed value:
					- the candidate tuple selected for the imputation
					- the RFD who has been used to identify the candidate
					- the distance score (lower is better) associated with the candidate
	
	RFD			%folder containing the RFDcs used for imputation.

	InitialTuples		%folder containing CSV files with the tuples whose missing values have been randomly injected. 
				It is used by RENUVER to generate the CSVs stored in the "Populated" folder.

	Candidates		%folder containing CSV files with the candidate(s) selected for each missing value.


%%%%%%%%%%%%%%%%%%%%%%%%%%%% RENUVER %%%%%%%%%%%%%%%%%%%%%%%%%%%%%
It implements the imputation phase of the RENUVER algorithm, configured to impute missing values using RFDcs corresponding to the Differential Dependencies (DDs). 
The imputed values are stored in the "ImputationResults" folder. 
NOTE: It is necessary to have a file, within the "InitialTuples" folder, with the same name as the dataset file for the execution to be completed.

Parameters:

args0: 
A comma-separated list of values, specifying the type for each attribute value. The list should contain exactly a letter for each attribute of the dataset, letters supported in this version are:
	- D = any data type: strings, numbers, decimals, etc..
	- C = char data type, i.e., attribute values consisting of a single character
	- B = boolean attribute values, i.e., attribute values whose value distribution consists of only two possible values (e.g., "M" and "F")

args1: 
An input CSV file (containing a relation instance) stored into the Dataset folder (do not add the '.csv' extension): "<nameFile>" 

args2: 
A textual value specifying the separator used into the CSV file: "<separator>"

args3:
An input CSV file (containing a set of RFDcs) stored into the RFD folder: "<nameFile.csv>" 

args4:
A numeric value specifying the maximum distance threshold of the RFDcs set: "<maxthr>"  

Example:

java -jar Renuver.jar "D,C,D,D,D,D,D,B,B,D,D,D,D" "bridges_70_1.csv" ";" "output_false_15_bridges.csv" "15"

RENUVER tries to impute all of the 70 missing values within the Bridges dataset by using the set of RFDcs discovered having a max threshold of 15.