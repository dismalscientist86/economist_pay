*Bring in data from https://www.fedsdatacenter.com/federal-pay-rates/ (Downloaded 6/11/18)
clear
set more off
import excel "M:\CES_New_Folder_Structure\RESEARCH\Gender_Earnings_Gap\Economists\FedsDataCenter\Federal-Employee-Salaries_FY2015.xlsx", sheet("Sheet1") firstrow case(lower) clear
tab grade
tab payplan
tab grade if payplan=="GS"
tab agency
drop if salary==.
summ salary, d
list if salary==0
list if agency=="BUREAU OF CONSUMER FIN PRO"
list if agency=="INTERNAL REVENUE SERVICE"
save "M:\CES_New_Folder_Structure\RESEARCH\Gender_Earnings_Gap\Economists\FedsDataCenter\Federal-Employee-Salaries_FY2015.dta", replace

*******************************************************************************
* See if we can get genders based on names
* modified original code to create a merging variable using a full "first name"
*******************************************************************************

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
edit if inrange(length(firstname),1,2)
// remove periods after any first name initials
replace firstname=substr(firstname,1,1) if substr(firstname,2,1)=="."

* create a merging variable using a full "first name"
gen merge_name=firstname
replace merge_name=secondname if length(firstname)==1
replace merge_name=thirdname if (length(firstname)==1 & length(secondname)==1)
label var merge_name "first 'full' name used to assign gender"


keep merge_name
duplicates report
duplicates drop

// replace variable name2 in original code below with merge_name 
******************************************************************************
******************************************************************************

*API only does 1000 names at a time. Wait 1 day between runs
sort merge_name
drop if merge_name==""
keep if _n<1000 //Run 1
*keep if _n>=1000 //Run 2

tempfile genderized
save `genderized'
levelsof merge_name, local(names)
foreach name of local names{
    copy "https://api.genderize.io/?name=`name'" "`name'.csv", text replace
    import delimited "`name'.csv", varnames(nonames) encoding(ISO-8859-1) clear
    capture rename (v1 v2 v3 v4) (name gender probability count)
    append using `genderized'
    save `genderized', replace
}
replace name = trim(substr(name, strpos(name, ":")+2, strlen(name)-(strpos(name, ":")+2)))
replace gender = trim(subinstr(gender, `"gender":""', "",.))
replace probability = trim(substr(probability, strpos(probability, ":")+1,.))
replace count = trim(substr(count, strpos(count, ":")+1, strlen(count)-(strpos(count, ":")+1)))
compress _all

save "M:\CES_New_Folder_Structure\RESEARCH\Gender_Earnings_Gap\Economists\FedsDataCenter\name_genders_run1_v2.dta", replace //Run 1
*save "M:\CES_New_Folder_Structure\RESEARCH\Gender_Earnings_Gap\Economists\FedsDataCenter\name_genders_run2_v2.dta", replace //Run 2

