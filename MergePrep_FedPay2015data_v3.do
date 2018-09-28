/*
Do file to merge data on eFederal employee salary and bonus from
https://www.fedsdatacenter.com/federal-pay-rates/ (Downloaded 6/11/18)
with a data set containing a gender variable 
created from using API at https://genderize.io/
then prepare this merged data for analysis
*/

clear all
set more off
capture log close
set linesize 100

global c_date=strtoname(c(current_date))

* change working directory
cd "M:\CES_New_Folder_Structure\RESEARCH\Gender_Earnings_Gap\Economists\FedsDataCenter\

* create log
log using "MergePrep_FedPay2015data_v3_${c_date}.log", replace

************************************************************************
* Load & Append data sets containing gender variable
* data (ending in run1_v2 or run2_v2) created from "Prep4gender_FY2015.do"  
************************************************************************

*use "name_genders_run1_v2.dta", clear
*append using "name_genders_run1_v2.dta"

*use "name_genders_run1_v2.dta", clear
*append using "name_genders_run2_v2.dta"

*************************************************************************
* Examine, Prep, & Save the Gender Data to be used for merging
*************************************************************************
desc
display "Number of unique first names from Fed Pay 2015 Data"

drop count v1 v2 merge_name
rename name merge_name  // name is all uppercase letters
count if merge_name!="" // # of unique names that could not be assigned gender

rename probability Pr_gender // Probability of gender based on first name
drop if gender==""  
display "Number of unique first names with gender assigned"
count				

sort merge_name
save "name_genders_all_v3.dta", replace

*************************************************************************
* Load & Prep Fed Pay 2015 data for merging by firstname
*************************************************************************

use "Federal-Employee-Salaries_FY2015.dta", clear
desc

* name variable format is: LAST,FIRST MIDDLE/M.I. for most agencies
split name, p(,)
rename name1 lastname
label var lastname "last name"

split name2, p(" ") 
rename name21 firstname
label var firstname "first name"
rename name22 secondname
label var secondname "second name"
rename name23 thirdname
label var thirdname "third name"

// name variable format is" LAST,,FIRST MIDDLE/M.I. for a few agencies
split name3, p(" ")
replace firstname=name31 if length(name3)>0
replace secondname=name32 if length(name3)>0
replace thirdname=name33 if length(name3)>0

// look for initial first names
tab firstname if inrange(length(firstname),1,2) 
*edit if inrange(length(firstname),1,2)
// remove periods after any first name initials
replace firstname=substr(firstname,1,1) if substr(firstname,2,1)=="."

* create a merging variable using a full "first name"
gen merge_name=firstname
replace merge_name=secondname if length(firstname)==1
replace merge_name=thirdname if (length(firstname)==1 & length(secondname)==1)

sort merge_name

* merge with prepped gender data
merge m:1 merge_name using "name_genders_all_v3.dta"
tab _merge
drop if _merge==2  // in name_genders_all data but not in Fed Pay data

label var gender "assigned gender"
label var Pr_gender "Prob. of gender based on first name"
drop name2 name3 name31 name32 name33 _merge

*************************************************************************
* Prep & Save data set for analysis
*************************************************************************
desc

* create male dummy variable
gen male=1 if gender=="male"
replace male=0 if gender=="female"
label var male "assigned male"
tab gender
tab male

*create GS payplan dummy variable
gen GSdum=0
replace GSdum=1 if payplan=="GS"
label var GSdum "=1 if GS pay scale"

* create ES payplan dummy variable
gen ESdum=0
replace ESdum=1 if payplan=="ES"
label var ESdum "=1 if Executive Service pay scale"

* create dummies for sister agencies
gen CBdum=0
replace CBdum=1 if agency=="BUREAU OF THE CENSUS"
label var CBdum "=1 if Census Bureau"

gen BLSdum=0
replace BLSdum=1 if agency=="BUREAU OF LABOR STATISTICS"
label var BLSdum "=1 if Bureau of Labor Statistics"

gen BEAdum=0
replace BEAdum=1 if agency=="BUREAU OF ECONOMIC ANALYSIS"
label var BEAdum "=1 if Bureau of Economic Analysis"


* save prepped data
save "Federal-Employee-Salaries_FY2015_genders_v3.dta", replace


**************************************************************************
**************************************************************************
log close
