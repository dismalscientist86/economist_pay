/*
Do file to analyze salary data by sex(gender) from 
https://www.fedsdatacenter.com/federal-pay-rates/ (Downloaded 6/11/18)
that has been merged with a data set containing a gender variable 
created from using API at https://genderize.io/
*/

clear all
set more off
capture log close
set linesize 100

global c_date=strtoname(c(current_date))

* change working directory
cd "M:\CES_New_Folder_Structure\RESEARCH\Gender_Earnings_Gap\Economists\FedsDataCenter\

* create log
log using "SalaryBySex_FedPay2015data_${c_date}.log", replace

*************************************************************************
* Load Fed Pay FY2015 data with gender 
*************************************************************************
use "Federal-Employee-Salaries_FY2015_genders_v3.dta", clear
desc


*************************************************************************
* Descriptive Analysis of Salary by Sex
*************************************************************************

* check assigned gender
count if gender==""		
count if firstname=="" 
tab agency if firstname==""

* check salary info
count if salary!=.
count if salary>0
count if salary==0
tab agency if salary==0

* check both gender & salary info
count if (gender!="" & salary>0)
tab gender if (gender!="" & salary>0)  

* list of agencies 
tab agency

* list of names that could not be assigned gender
tab merge_name if gender==""

*******************************************************************************
*******************************************************************************
* Full, Unrestricted Sample
*******************************************************************************
*******************************************************************************
display "Number of Economists from Fed Pay FY2015 data:"
count

* gender composition | assigned gender
tab gender

* median earnings
summ salary, detail
summ salary if male==1, detail
summ salary if male==0, detail

* counts & median salary by GS-scale and by gender
tab grade if payplan=="GS"
count if payplan!="GS"
tab grade if payplan=="ES"
count if (payplan!="GS" & payplan!="ES")

summ salary if GSdum==1, detail
summ salary if (GSdum==1 & male==1), detail
summ salary if (GSdum==1 & male==0), detail
summ salary if ESdum==1, detail
summ salary if (ESdum==1 & male==1), detail
summ salary if (ESdum==1 & male==0), detail
summ salary if (GSdum==0 & ESdum==0), detail
summ salary if (GSdum==0 & ESdum==0 & male==1), detail
summ salary if (GSdum==0 & ESdum==0 & male==0), detail

bysort grade: summ salary if payplan=="GS", detail
bysort grade: summ salary if (payplan=="GS" & male==1), detail
bysort grade: summ salary if (payplan=="GS" & male==0), detail

************* counts & median salary by gender and by agency *************

* BLS
preserve
keep if BLSdum==1
summ salary, detail
summ salary if male==1, detail
summ salary if male==0, detail
bysort grade: summ salary if payplan=="GS", detail
bysort grade: summ salary if (payplan=="GS" & male==1), detail
bysort grade: summ salary if (payplan=="GS" & male==0), detail
summ salary if payplan=="ES", detail
summ salary if (payplan=="ES" & male==1), detail
summ salary if (payplan=="ES" & male==0), detail
restore

* BEA 
preserve
keep if BEAdum==1
summ salary, detail
summ salary if male==1, detail
summ salary if male==0, detail
bysort grade: summ salary if payplan=="ZP", detail
bysort grade: summ salary if (payplan=="ZP" & male==1), detail
bysort grade: summ salary if (payplan=="ZP" & male==0), detail
summ salary if payplan=="ES", detail
summ salary if (payplan=="ES" & male==1), detail
summ salary if (payplan=="ES" & male==0), detail
restore

* Departmental Offices
preserve
keep if agency=="DEPARTMENTAL OFFICES"
summ salary, detail
summ salary if male==1, detail
summ salary if male==0, detail
restore

* IRS
preserve
keep if agency=="INTERNAL REVENUE SERVICE"
summ salary, detail
summ salary if male==1, detail
summ salary if male==0, detail
restore

* ERS
preserve
keep if agency=="ECONOMIC RESEARCH SERVICE"
summ salary, detail
summ salary if male==1, detail
summ salary if male==0, detail
restore

* Census Bureau
preserve
keep if CBdum==1
summ salary, detail
summ salary if male==1, detail
summ salary if male==0, detail
bysort grade: summ salary if payplan=="GS", detail
bysort grade: summ salary if (payplan=="GS" & male==1), detail
bysort grade: summ salary if (payplan=="GS" & male==0), detail
summ salary if payplan=="ES", detail
summ salary if (payplan=="ES" & male==1), detail
summ salary if (payplan=="ES" & male==0), detail
restore

******************************************************************************
******************************************************************************
* Restricted Sample - no missing salary, no missing assigned gender
******************************************************************************
******************************************************************************
display "Number of Economists from Fed Pay FY2015 data with salary & gender:"
count if (gender!="" & salary>0)
preserve 
keep if (gender!="" & salary>0)


* gender composition | assigned gender
tab gender

* median earnings
summ salary, detail
summ salary if male==1, detail
summ salary if male==0, detail

* counts & median salary by GS-scale and by gender
tab grade if payplan=="GS"
count if payplan!="GS"
tab grade if payplan=="ES"
count if (payplan!="GS" & payplan!="ES")

summ salary if GSdum==1, detail
summ salary if (GSdum==1 & male==1), detail
summ salary if (GSdum==1 & male==0), detail
summ salary if ESdum==1, detail
summ salary if (ESdum==1 & male==1), detail
summ salary if (ESdum==1 & male==0), detail
summ salary if (GSdum==0 & ESdum==0), detail
summ salary if (GSdum==0 & ESdum==0 & male==1), detail
summ salary if (GSdum==0 & ESdum==0 & male==0), detail

bysort grade: summ salary if payplan=="GS", detail
bysort grade: summ salary if (payplan=="GS" & male==1), detail
bysort grade: summ salary if (payplan=="GS" & male==0), detail

restore
************* counts & median salary by gender and by agency *************

* BLS
preserve
keep if (gender!="" & salary>0 & BLSdum==1)
summ salary, detail
summ salary if male==1, detail
summ salary if male==0, detail
bysort grade: summ salary if payplan=="GS", detail
bysort grade: summ salary if (payplan=="GS" & male==1), detail
bysort grade: summ salary if (payplan=="GS" & male==0), detail
summ salary if GSdum==1, detail
summ salary if (GSdum==1 & male==1), detail
summ salary if (GSdum==1 & male==0), detail
summ salary if ESdum==1, detail
summ salary if (ESdum==1 & male==1), detail
summ salary if (ESdum==1 & male==0), detail
summ salary if (GSdum==0 & ESdum==0), detail
summ salary if (GSdum==0 & ESdum==0 & male==1), detail
summ salary if (GSdum==0 & ESdum==0 & male==0), detail
restore

* BEA 
preserve
keep if (gender!="" & salary>0 & BEAdum==1)
summ salary, detail
summ salary if male==1, detail
summ salary if male==0, detail
bysort grade: summ salary if payplan=="ZP", detail
bysort grade: summ salary if (payplan=="ZP" & male==1), detail
bysort grade: summ salary if (payplan=="ZP" & male==0), detail
summ salary if payplan=="ZP", detail
summ salary if (payplan=="ZP" & male==1), detail
summ salary if (payplan=="ZP" & male==0), detail
summ salary if ESdum==1, detail
summ salary if (ESdum==1 & male==1), detail
summ salary if (ESdum==1 & male==0), detail
summ salary if (payplan!="ZP" & ESdum==0), detail
summ salary if (payplan!="ZP" & ESdum==0 & male==1), detail
summ salary if (payplan!="ZP" & ESdum==0 & male==0), detail
restore

* Departmental Offices
preserve
keep if (gender!="" & salary>0 & agency=="DEPARTMENTAL OFFICES")
summ salary, detail
summ salary if male==1, detail
summ salary if male==0, detail
restore

* IRS
preserve
keep if (gender!="" & salary>0 & agency=="INTERNAL REVENUE SERVICE")
summ salary, detail
summ salary if male==1, detail
summ salary if male==0, detail
restore

* ERS
preserve
keep if (gender!="" & salary>0 & agency=="ECONOMIC RESEARCH SERVICE")
summ salary, detail
summ salary if male==1, detail
summ salary if male==0, detail
restore

* Census Bureau
preserve
keep if (gender!="" & salary>0 & CBdum==1)
summ salary, detail
summ salary if male==1, detail
summ salary if male==0, detail
bysort grade: summ salary if payplan=="GS", detail
bysort grade: summ salary if (payplan=="GS" & male==1), detail
bysort grade: summ salary if (payplan=="GS" & male==0), detail
summ salary if GSdum==1, detail
summ salary if (GSdum==1 & male==1), detail
summ salary if (GSdum==1 & male==0), detail
summ salary if ESdum==1, detail
summ salary if (ESdum==1 & male==1), detail
summ salary if (ESdum==1 & male==0), detail
summ salary if (GSdum==0 & ESdum==0), detail
summ salary if (GSdum==0 & ESdum==0 & male==1), detail
summ salary if (GSdum==0 & ESdum==0 & male==0), detail
restore

**************************************************************************
**************************************************************************
log close
