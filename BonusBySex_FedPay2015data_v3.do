/*
Do file to prepare and analyze bonus data from 
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
log using "BonusesBySex_FedPay2015data_v3_${c_date}.log", replace

******************************************************************************
* Load Fed Pay FY2015 data with gender 
******************************************************************************

use "Federal-Employee-Salaries_FY2015_genders_v3.dta", clear
desc

*************************************************************************
*************************************************************************
* Descriptive Analysis of Bonuses by Sex
*************************************************************************
*************************************************************************


******************************************************************************
* Full, Unrestricted Sample
******************************************************************************
display "Number of Economists from Fed Pay FY2015 data:"
count

* gender composition | assigned gender
tab gender

* median bonus
summ bonus, detail
summ bonus if male==1, detail
summ bonus if male==0, detail

* counts & median bonus by GS-scale and by gender
tab grade if payplan=="GS"
count if payplan!="GS"
tab grade if payplan=="ES"
count if (payplan!="GS" & payplan!="ES")

summ bonus if GSdum==1, detail
summ bonus if (GSdum==1 & male==1), detail
summ bonus if (GSdum==1 & male==0), detail
summ bonus if ESdum==1, detail
summ bonus if (ESdum==1 & male==1), detail
summ bonus if (ESdum==1 & male==0), detail
summ bonus if (GSdum==0 & ESdum==0), detail
summ bonus if (GSdum==0 & ESdum==0 & male==1), detail
summ bonus if (GSdum==0 & ESdum==0 & male==0), detail

bysort grade: summ bonus if payplan=="GS", detail
bysort grade: summ bonus if (payplan=="GS" & male==1), detail
bysort grade: summ bonus if (payplan=="GS" & male==0), detail


************* counts & median bonus by gender and by agency *************

* BLS
preserve
keep if BLSdum==1
summ bonus, detail
summ bonus if male==1, detail
summ bonus if male==0, detail
bysort grade: summ bonus if payplan=="GS", detail
bysort grade: summ bonus if (payplan=="GS" & male==1), detail
bysort grade: summ bonus if (payplan=="GS" & male==0), detail
summ bonus if GSdum==1, detail
summ bonus if (GSdum==1 & male==1), detail
summ bonus if (GSdum==1 & male==0), detail
summ bonus if ESdum==1, detail
summ bonus if (ESdum==1 & male==1), detail
summ bonus if (ESdum==1 & male==0), detail
summ bonus if (GSdum==0 & ESdum==0), detail
summ bonus if (GSdum==0 & ESdum==0 & male==1), detail
summ bonus if (GSdum==0 & ESdum==0 & male==0), detail
restore

* BEA 
preserve
keep if BEAdum==1
summ bonus, detail
summ bonus if male==1, detail
summ bonus if male==0, detail
bysort grade: summ bonus if payplan=="ZP", detail
bysort grade: summ bonus if (payplan=="ZP" & male==1), detail
bysort grade: summ bonus if (payplan=="ZP" & male==0), detail
summ bonus if payplan=="ZP", detail
summ bonus if (payplan=="ZP" & male==1), detail
summ bonus if (payplan=="ZP" & male==0), detail
summ bonus if ESdum==1, detail
summ bonus if (ESdum==1 & male==1), detail
summ bonus if (ESdum==1 & male==0), detail
summ bonus if (payplan!="ZP" & ESdum==0), detail
summ bonus if (payplan!="ZP" & ESdum==0 & male==1), detail
summ bonus if (payplan!="ZP" & ESdum==0 & male==0), detail
restore

* Departmental Offices
preserve
keep if agency=="DEPARTMENTAL OFFICES"
summ bonus, detail
summ bonus if male==1, detail
summ bonus if male==0, detail
restore

* IRS
preserve
keep if agency=="INTERNAL REVENUE SERVICE"
summ bonus, detail
summ bonus if male==1, detail
summ bonus if male==0, detail
restore

* ERS
preserve
keep if agency=="ECONOMIC RESEARCH SERVICE"
summ bonus, detail
summ bonus if male==1, detail
summ bonus if male==0, detail
restore

* Census Bureau
preserve
keep if CBdum==1
summ bonus, detail
summ bonus if male==1, detail
summ bonus if male==0, detail
bysort grade: summ bonus if payplan=="GS", detail
bysort grade: summ bonus if (payplan=="GS" & male==1), detail
bysort grade: summ bonus if (payplan=="GS" & male==0), detail
summ bonus if GSdum==1, detail
summ bonus if (GSdum==1 & male==1), detail
summ bonus if (GSdum==1 & male==0), detail
summ bonus if ESdum==1, detail
summ bonus if (ESdum==1 & male==1), detail
summ bonus if (ESdum==1 & male==0), detail
summ bonus if (GSdum==0 & ESdum==0), detail
summ bonus if (GSdum==0 & ESdum==0 & male==1), detail
summ bonus if (GSdum==0 & ESdum==0 & male==0), detail
restore


*********** conditional on having a bonus>0 ***********************************
display "Number of Economists from Fed Pay FY2015 data with bonus>0 "
count if bonus>0

preserve
keep if bonus>0

* gender composition | assigned gender
tab gender

* median bonus
summ bonus, detail
summ bonus if male==1, detail
summ bonus if male==0, detail

* counts & median bonus by GS-scale and by gender
tab grade if payplan=="GS"
count if payplan!="GS"
tab grade if payplan=="ES"
count if (payplan!="GS" & payplan!="ES")

summ bonus if GSdum==1, detail
summ bonus if (GSdum==1 & male==1), detail
summ bonus if (GSdum==1 & male==0), detail
summ bonus if ESdum==1, detail
summ bonus if (ESdum==1 & male==1), detail
summ bonus if (ESdum==1 & male==0), detail
summ bonus if (GSdum==0 & ESdum==0), detail
summ bonus if (GSdum==0 & ESdum==0 & male==1), detail
summ bonus if (GSdum==0 & ESdum==0 & male==0), detail

bysort grade: summ bonus if payplan=="GS", detail
bysort grade: summ bonus if (payplan=="GS" & male==1), detail
bysort grade: summ bonus if (payplan=="GS" & male==0), detail

restore
************* counts & median bonus by gender and by agency *************

* BLS
preserve
keep if (bonus>0 & BLSdum==1)
summ bonus if bonus>0, detail
summ bonus if (bonus>0 & male==1), detail
summ bonus if (bonus>0 & male==0), detail
bysort grade: summ bonus if (bonus>0 & payplan=="GS"), detail
bysort grade: summ bonus if (bonus>0 & payplan=="GS" & male==1), detail
bysort grade: summ bonus if (bonus>0 & payplan=="GS" & male==0), detail
summ bonus if (bonus>0 & GSdum==1), detail
summ bonus if (bonus>0 & GSdum==1 & male==1), detail
summ bonus if (bonus>0 & GSdum==1 & male==0), detail
summ bonus if (bonus>0 & ESdum==1), detail
summ bonus if (bonus>0 & ESdum==1 & male==1), detail
summ bonus if (bonus>0 & ESdum==1 & male==0), detail
summ bonus if (GSdum==0 & ESdum==0), detail
summ bonus if (bonus>0 & GSdum==0 & ESdum==0 & male==1), detail
summ bonus if (bonus>0 & GSdum==0 & ESdum==0 & male==0), detail
restore

* BEA 
preserve
keep if (bonus>0 & BEAdum==1)
summ bonus if bonus>0, detail
summ bonus if (bonus>0 & male==1), detail
summ bonus if (bonus>0 & male==0), detail
bysort grade: summ bonus if (bonus>0 & payplan=="ZP"), detail
bysort grade: summ bonus if (bonus>0 & payplan=="ZP" & male==1), detail
bysort grade: summ bonus if (bonus>0 & payplan=="ZP" & male==0), detail
summ bonus if (bonus>0 & payplan=="ZP"), detail
summ bonus if (bonus>0 & payplan=="ZP" & male==1), detail
summ bonus if (bonus>0 & payplan=="ZP" & male==0), detail
summ bonus if (bonus>0 & ESdum==1), detail
summ bonus if (bonus>0 & ESdum==1 & male==1), detail
summ bonus if (bonus>0 & ESdum==1 & male==0), detail
summ bonus if (bonus>0 & payplan!="ZP" & ESdum==0), detail
summ bonus if (bonus>0 & payplan!="ZP" & ESdum==0 & male==1), detail
summ bonus if (bonus>0 & payplan!="ZP" & ESdum==0 & male==0), detail
restore

* Departmental Offices
preserve
keep if (bonus>0 & agency=="DEPARTMENTAL OFFICES")
summ bonus if bonus>0, detail
summ bonus if (bonus>0 & male==1), detail
summ bonus if (bonus>0 & male==0), detail
restore

* IRS
preserve
keep if (bonus>0 & gender!="" & salary>0 & agency=="INTERNAL REVENUE SERVICE")
summ bonus if bonus>0, detail
summ bonus if (bonus>0 & male==1), detail
summ bonus if (bonus>0 & male==0), detail
restore

* ERS
preserve
keep if (bonus>0 & agency=="ECONOMIC RESEARCH SERVICE")
summ bonus if bonus>0, detail
summ bonus if (bonus>0 & male==1), detail
summ bonus if (bonus>0 & male==0), detail
restore

* Census Bureau
preserve
keep if (bonus>0 & CBdum==1)
summ bonus if bonus>0, detail
summ bonus if (bonus>0 & male==1), detail
summ bonus if (bonus>0 & male==0), detail
bysort grade: summ bonus if (bonus>0 & payplan=="GS"), detail
bysort grade: summ bonus if (bonus>0 & payplan=="GS" & male==1), detail
bysort grade: summ bonus if (bonus>0 & payplan=="GS" & male==0), detail
summ bonus if (bonus>0 & GSdum==1), detail
summ bonus if (bonus>0 & GSdum==1 & male==1), detail
summ bonus if (bonus>0 & GSdum==1 & male==0), detail
summ bonus if (bonus>0 & ESdum==1), detail
summ bonus if (bonus>0 & ESdum==1 & male==1), detail
summ bonus if (bonus>0 & ESdum==1 & male==0), detail
summ bonus if (bonus>0 & GSdum==0 & ESdum==0), detail
summ bonus if (bonus>0 & GSdum==0 & ESdum==0 & male==1), detail
summ bonus if (bonus>0 & GSdum==0 & ESdum==0 & male==0), detail
restore


******************************************************************************
* Restricted Sample
******************************************************************************
count

* salary = 0 OR missing gender
summ bonus if (salary==0 & gender=="")
summ bonus if (bonus>0 & (salary==0 | gender==""))
tab agency if (bonus>0 & (salary==0 | gender==""))
tab bonus if (bonus>0 & (salary==0 | gender==""))

* salary = 0
summ bonus if salary==0
summ bonus if (bonus>0 & salary==0)
tab agency if (bonus>0 & salary==0)
tab bonus if (bonus>0 & salary==0)

* missing gender
summ bonus if gender==""
summ bonus if (bonus>0 & gender=="")
tab agency if (bonus>0 & gender=="")
tab bonus if (bonus>0 & gender=="")

display "Number of Economists from Fed Pay FY2015 data with salary & gender:"
count if (gender!="" & salary>0)

preserve 
keep if (gender!="" & salary>0)

* gender composition | assigned gender
tab gender

* median bonus
summ bonus, detail
summ bonus if male==1, detail
summ bonus if male==0, detail

* counts & median bonus by GS-scale and by gender
tab grade if payplan=="GS"
count if payplan!="GS"
tab grade if payplan=="ES"
count if (payplan!="GS" & payplan!="ES")

summ bonus if GSdum==1, detail
summ bonus if (GSdum==1 & male==1), detail
summ bonus if (GSdum==1 & male==0), detail
summ bonus if ESdum==1, detail
summ bonus if (ESdum==1 & male==1), detail
summ bonus if (ESdum==1 & male==0), detail
summ bonus if (GSdum==0 & ESdum==0), detail
summ bonus if (GSdum==0 & ESdum==0 & male==1), detail
summ bonus if (GSdum==0 & ESdum==0 & male==0), detail

bysort grade: summ bonus if payplan=="GS", detail
bysort grade: summ bonus if (payplan=="GS" & male==1), detail
bysort grade: summ bonus if (payplan=="GS" & male==0), detail

restore
************* counts & median bonus by gender and by agency *************

* BLS
preserve
keep if (gender!="" & salary>0 & BLSdum==1)
summ bonus, detail
summ bonus if male==1, detail
summ bonus if male==0, detail
bysort grade: summ bonus if payplan=="GS", detail
bysort grade: summ bonus if (payplan=="GS" & male==1), detail
bysort grade: summ bonus if (payplan=="GS" & male==0), detail
summ bonus if GSdum==1, detail
summ bonus if (GSdum==1 & male==1), detail
summ bonus if (GSdum==1 & male==0), detail
summ bonus if ESdum==1, detail
summ bonus if (ESdum==1 & male==1), detail
summ bonus if (ESdum==1 & male==0), detail
summ bonus if (GSdum==0 & ESdum==0), detail
summ bonus if (GSdum==0 & ESdum==0 & male==1), detail
summ bonus if (GSdum==0 & ESdum==0 & male==0), detail
restore

* BEA 
preserve
keep if (gender!="" & salary>0 & BEAdum==1)
summ bonus, detail
summ bonus if male==1, detail
summ bonus if male==0, detail
bysort grade: summ bonus if payplan=="ZP", detail
bysort grade: summ bonus if (payplan=="ZP" & male==1), detail
bysort grade: summ bonus if (payplan=="ZP" & male==0), detail
summ bonus if payplan=="ZP", detail
summ bonus if (payplan=="ZP" & male==1), detail
summ bonus if (payplan=="ZP" & male==0), detail
summ bonus if ESdum==1, detail
summ bonus if (ESdum==1 & male==1), detail
summ bonus if (ESdum==1 & male==0), detail
summ bonus if (payplan!="ZP" & ESdum==0), detail
summ bonus if (payplan!="ZP" & ESdum==0 & male==1), detail
summ bonus if (payplan!="ZP" & ESdum==0 & male==0), detail
restore

* Departmental Offices
preserve
keep if (gender!="" & salary>0 & agency=="DEPARTMENTAL OFFICES")
summ bonus, detail
summ bonus if male==1, detail
summ bonus if male==0, detail
restore

* IRS
preserve
keep if (gender!="" & salary>0 & agency=="INTERNAL REVENUE SERVICE")
summ bonus, detail
summ bonus if male==1, detail
summ bonus if male==0, detail
restore

* ERS
preserve
keep if (gender!="" & salary>0 & agency=="ECONOMIC RESEARCH SERVICE")
summ bonus, detail
summ bonus if male==1, detail
summ bonus if male==0, detail
restore

* Census Bureau
preserve
keep if (gender!="" & salary>0 & CBdum==1)
summ bonus, detail
summ bonus if male==1, detail
summ bonus if male==0, detail
bysort grade: summ bonus if payplan=="GS", detail
bysort grade: summ bonus if (payplan=="GS" & male==1), detail
bysort grade: summ bonus if (payplan=="GS" & male==0), detail
summ bonus if GSdum==1, detail
summ bonus if (GSdum==1 & male==1), detail
summ bonus if (GSdum==1 & male==0), detail
summ bonus if ESdum==1, detail
summ bonus if (ESdum==1 & male==1), detail
summ bonus if (ESdum==1 & male==0), detail
summ bonus if (GSdum==0 & ESdum==0), detail
summ bonus if (GSdum==0 & ESdum==0 & male==1), detail
summ bonus if (GSdum==0 & ESdum==0 & male==0), detail
restore


*********** conditional on having a bonus>0 ***********************************
display "Number of Economists from Fed Pay FY2015 data with bonus>0 "
count if (bonus>0 & gender!="" & salary>0)

preserve
keep if (bonus>0 & gender!="" & salary>0)

* gender composition | assigned gender
tab gender

* median bonus
summ bonus, detail
summ bonus if male==1, detail
summ bonus if male==0, detail

* counts & median bonus by GS-scale and by gender
tab grade if payplan=="GS"
count if payplan!="GS"
tab grade if payplan=="ES"
count if (payplan!="GS" & payplan!="ES")

summ bonus if GSdum==1, detail
summ bonus if (GSdum==1 & male==1), detail
summ bonus if (GSdum==1 & male==0), detail
summ bonus if ESdum==1, detail
summ bonus if (ESdum==1 & male==1), detail
summ bonus if (ESdum==1 & male==0), detail
summ bonus if (GSdum==0 & ESdum==0), detail
summ bonus if (GSdum==0 & ESdum==0 & male==1), detail
summ bonus if (GSdum==0 & ESdum==0 & male==0), detail

bysort grade: summ bonus if payplan=="GS", detail
bysort grade: summ bonus if (payplan=="GS" & male==1), detail
bysort grade: summ bonus if (payplan=="GS" & male==0), detail

restore
************* counts & median bonus by gender and by agency *************

* BLS
preserve
keep if (bonus>0 & gender!="" & salary>0 & BLSdum==1)
summ bonus, detail
summ bonus if male==1, detail
summ bonus if male==0, detail
bysort grade: summ bonus if payplan=="GS", detail
bysort grade: summ bonus if (payplan=="GS" & male==1), detail
bysort grade: summ bonus if (payplan=="GS" & male==0), detail
summ bonus if GSdum==1, detail
summ bonus if (GSdum==1 & male==1), detail
summ bonus if (GSdum==1 & male==0), detail
summ bonus if ESdum==1, detail
summ bonus if (ESdum==1 & male==1), detail
summ bonus if (ESdum==1 & male==0), detail
summ bonus if (GSdum==0 & ESdum==0), detail
summ bonus if (GSdum==0 & ESdum==0 & male==1), detail
summ bonus if (GSdum==0 & ESdum==0 & male==0), detail
restore

* BEA 
preserve
keep if (bonus>0 & gender!="" & salary>0 & BEAdum==1)
summ bonus, detail
summ bonus if male==1, detail
summ bonus if male==0, detail
bysort grade: summ bonus if payplan=="ZP", detail
bysort grade: summ bonus if (payplan=="ZP" & male==1), detail
bysort grade: summ bonus if (payplan=="ZP" & male==0), detail
summ bonus if payplan=="ZP", detail
summ bonus if (payplan=="ZP" & male==1), detail
summ bonus if (payplan=="ZP" & male==0), detail
summ bonus if ESdum==1, detail
summ bonus if (ESdum==1 & male==1), detail
summ bonus if (ESdum==1 & male==0), detail
summ bonus if (payplan!="ZP" & ESdum==0), detail
summ bonus if (payplan!="ZP" & ESdum==0 & male==1), detail
summ bonus if (payplan!="ZP" & ESdum==0 & male==0), detail
restore

* Departmental Offices
preserve
keep if (bonus>0 & gender!="" & salary>0 & agency=="DEPARTMENTAL OFFICES")
summ bonus, detail
summ bonus if male==1, detail
summ bonus if male==0, detail
restore

* IRS
preserve
keep if (bonus>0 & gender!="" & salary>0 & agency=="INTERNAL REVENUE SERVICE")
summ bonus, detail
summ bonus if male==1, detail
summ bonus if male==0, detail
restore

* ERS
preserve
keep if (bonus>0 & gender!="" & salary>0 & agency=="ECONOMIC RESEARCH SERVICE")
summ bonus, detail
summ bonus if male==1, detail
summ bonus if male==0, detail
restore

* Census Bureau
preserve
keep if (bonus>0 & gender!="" & salary>0 & CBdum==1)
summ bonus, detail
summ bonus if male==1, detail
summ bonus if male==0, detail
bysort grade: summ bonus if payplan=="GS", detail
bysort grade: summ bonus if (payplan=="GS" & male==1), detail
bysort grade: summ bonus if (payplan=="GS" & male==0), detail
summ bonus if GSdum==1, detail
summ bonus if (GSdum==1 & male==1), detail
summ bonus if (GSdum==1 & male==0), detail
summ bonus if ESdum==1, detail
summ bonus if (ESdum==1 & male==1), detail
summ bonus if (ESdum==1 & male==0), detail
summ bonus if (GSdum==0 & ESdum==0), detail
summ bonus if (GSdum==0 & ESdum==0 & male==1), detail
summ bonus if (GSdum==0 & ESdum==0 & male==0), detail
restore

******************************************************************************
******************************************************************************
log close
