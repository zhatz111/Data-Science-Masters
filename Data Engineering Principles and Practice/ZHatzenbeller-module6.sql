-- Question 1: Create a new schema within ‘jhu’ named ‘stackoverflow’ (Use SQL, not the GUI)

-- Approach: To create the schema I use this command
CREATE SCHEMA IF NOT EXISTS stackoverflow;

-- I use this command to drop the table so that it can be recreated with the correct schema from the SQL below rather than needing to manually delete it when
-- I want to recreate the table. This helps with initial troubleshooting to get the correct data types for each column.
DROP TABLE stackoverflow.survey;

-- Question 2: Create a new table within ‘stackoverflow’ named ‘survey’. 
-- Specify data types and any constraints you feel necessary based on the data 
-- (i.e., integer, varchar(n), text data types, and whether a field should not be null)

-- Approach: The way I thought about this was that the majority of the columns were variable-length character strings since they are mostly free text fields.
-- Even the columns that were not free text still required a variable in length data type to fit the different choices a user has. I listed everything as VARCHAR
-- with the limit length designated by the excel document provided to us. I then went through each column in the survey and adjusted there data type based on the
-- data I saw in the column and the length we were told for that data. An example would be the "YearsCode" column that initially looks as though a smallint would
-- be appropriate for it but when looking at the maximum length provided by the excel document which was 18, I knew this would require the data type to be a BIGINT
-- to fully fit the max numeric size allowed. 
-- I took this same approach for all columns adjusting some to the TEXT, BOOLEAN, INTEGER, and SMALLINT data types. I allowed NULL values to be present in all column 
-- except the "MainBranch" column which requires and answer in the survey. The TEXT data type was necessary for two columns since there max lenght is 0 and the 
-- VARCHAR OR CHAR both do not allow lengths below 1.
-- I used the "ResponseId" column as the primary key and designated the data type as a SERIAL since the max length was said to be 5 but checking the data it does go
-- over the SMALLSERIAL limit. I used this data type instead of INTEGER because this data type will automatically generate a sequence of integers
-- for the ResponseId field.
-- Some issues I faced when uploading the data based on the data types is that there are anomoulous values in some columns like "comptotal" which has a number that
-- is 10^52. This cannot be captured by any numerical data type so I was forced to just use a TEXT field.
CREATE TABLE IF NOT EXISTS stackoverflow.survey (
    ResponseId SERIAL PRIMARY KEY,
    MainBranch VARCHAR(77) NOT NULL,
    Employment VARCHAR(212),
    RemoteWork VARCHAR(36),
    CodingActivities VARCHAR(137),
    EdLevel VARCHAR(82),
    LearnCode VARCHAR(274),
    LearnCodeOnline VARCHAR(372),
    LearnCodeCoursesCert VARCHAR(65),
    YearsCode VARCHAR(18),
    YearsCodePro VARCHAR(18),
    DevType VARCHAR(659),
    OrgSize VARCHAR(50),
    PurchaseInfluence VARCHAR(32),
    BuyNewTool VARCHAR(277),
    Country VARCHAR(52),
    Currency VARCHAR(43),
    CompTotal TEXT,
    CompFreq VARCHAR(7),
    LanguageHaveWorkedWith VARCHAR(264),
    LanguageWantToWorkWith VARCHAR(264),
    DatabaseHaveWorkedWith VARCHAR(181),
    DatabaseWantToWorkWith VARCHAR(181),
    PlatformHaveWorkedWith VARCHAR(164),
    PlatformWantToWorkWith VARCHAR(164),
    WebframeHaveWorkedWith VARCHAR(210),
    WebframeWantToWorkWith VARCHAR(210),
    MiscTechHaveWorkedWith VARCHAR(219),
    MiscTechWantToWorkWith VARCHAR(219),
    ToolsTechHaveWorkedWith VARCHAR(100),
    ToolsTechWantToWorkWith VARCHAR(100),
    NEWCollabToolsHaveWorkedWith VARCHAR(267),
    NEWCollabToolsWantToWorkWith VARCHAR(267),
    OpSysProfessional VARCHAR(87),
    OpSysPersonal VARCHAR(87),
    VersionControlSystem VARCHAR(41),
    VCInteraction VARCHAR(106),
    VCHostingPersonal TEXT,
    VCHostingProfessional TEXT,
    OfficeStackAsyncHaveWorkedWith VARCHAR(260),
    OfficeStackAsyncWantToWorkWith VARCHAR(260),
    OfficeStackSyncHaveWorkedWith VARCHAR(138),
    OfficeStackSyncWantToWorkWith VARCHAR(138),
    Blockchain VARCHAR(16),
    NEWSOSites VARCHAR(151),
    SOVisitFreq VARCHAR(35),
    SOAccount VARCHAR(23),
    SOPartFreq VARCHAR(50),
    SOComm VARCHAR(15),
    Age VARCHAR(18),
    Gender VARCHAR(82),
    Trans VARCHAR(22),
    Sexuality VARCHAR(78),
    Ethnicity VARCHAR(345),
    Accessibility VARCHAR(200),
    MentalHealth VARCHAR(322),
    TBranch BOOLEAN,
    ICorPM VARCHAR(23),
    WorkExp SMALLINT,
    Knowledge_1 VARCHAR(26),
    Knowledge_2 VARCHAR(26),
    Knowledge_3 VARCHAR(26),
    Knowledge_4 VARCHAR(26),
    Knowledge_5 VARCHAR(26),
    Knowledge_6 VARCHAR(26),
    Knowledge_7 VARCHAR(26),
    Frequency_1 VARCHAR(17),
    Frequency_2 VARCHAR(17),
    Frequency_3 VARCHAR(17),
    TimeSearching VARCHAR(26),
    TimeAnswering VARCHAR(26),
    Onboarding VARCHAR(14),
    ProfessionalTech VARCHAR(233),
    TrueFalse_1 BOOLEAN,
    TrueFalse_2 BOOLEAN,
    TrueFalse_3 BOOLEAN,
    SurveyLength VARCHAR(21),
    SurveyEase VARCHAR(26),
    ConvertedCompYearly INTEGER
);


-- Question 3: Copy the Stack Overflow Survey 2022 data (survey_results_public.csv) into the ‘survey’ table. HINT: You will need to give execute & read access to the 
-- survey_results_public.csv file via terminal with the command chmod +xr survey_results_public.csv

-- Approach: To upload the data from the CSV file I used the \copy command rather than the COPY command because the former searches locally for the file on my computer.
-- I then set the file path to the csv, specified the delimter, that there is a header in the csv so it skips the top row and also to treat any values that are "NA" as NULL values
\copy stackoverflow.survey FROM 'C:\Users\zhatz\Documents\GitHub\Data-Science-Masters\Data Engineering Principles and Practice\Module 2\survey_results_public.csv' DELIMITER ',' CSV HEADER NULL 'NA';


-- Question 4: Hypothetically, we decide to follow up with a handful of survey participants who submitted anomalous 'CompTotal' answers (>= 1000000000000). After our follow-up, 
-- we determine these respondents’ actual CompTotal is the median of all respondents excluding the anomalous responses. 


-- Question 5: Use UPDATE to change the values in 'CompTotal' column to the median value excluding the anomalous responses. HINT: Do some research online on the syntax to calculate the median in PostgreSQL. 
-- A: The initial median 'CompTotal' excluding the anomalous responses before the UPDATE, round your answer up to the nearest whole number. 
-- B: The mean 'CompTotal' after the UPDATE, round your answer up to the nearest whole number.

-- Approach: I start by updating all anomlous values that take on characters other than just numbers. I used a regular expression to find these anomlous values. After finding them I set them to a very large number
-- that would be easily searchable in the database but does not correspond to an actual value already in the column. I then changed the table's column's data type to a BIGINT so I can perform computation such
-- as median and mean in the next parts.
UPDATE stackoverflow.survey SET comptotal = '10000000000000' WHERE comptotal !~ '^[0-9]+$';
ALTER TABLE stackoverflow.survey ALTER COLUMN comptotal TYPE BIGINT USING comptotal::BIGINT;

-- A: The median value before the update. To do this I used a select statement with the PERCENTILE_CONT to get the value at 50% the way through the data. I first needed to sort the data to do this and also
-- exclude and of the anomolous values which I deemed to be '10000000000000' in the previous query. I also stored this median value so that I could change the anomoulous values in Part B.

SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY comptotal) AS median
FROM stackoverflow.survey
WHERE comptotal < 10000000000000;

WITH median_value AS (
    SELECT 
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY comptotal) AS median
    FROM 
        stackoverflow.survey
    WHERE 
        comptotal < 10000000000000
)

-- B: The mean value after the update. I first updated the anomoulous values in the table with the UPDATE command. I then selected the average value from the data column using the AVG command.

UPDATE stackoverflow.survey
SET comptotal = (SELECT median FROM median_value)
WHERE comptotal = 10000000000000;

SELECT CEIL(AVG(comptotal)) AS mean_value_rounded
FROM stackoverflow.survey;