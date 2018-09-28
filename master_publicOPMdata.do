/* 
Name: master_publicOPMdata.do
Author: Julia Manzella
Date created:  29 June 2018
Description: This program is a master do.file for the CES project
Federal Workforce Dynamics: A Case Study of Economist by Gender
and it reads in, prepares, and analyzes publically available data
on Economists in the Federal Government retreived from
https://www.fedsdatacenter.com/federal-pay-rates/ (Downloaded 6/11/18)
*/

**************************************************************************
/* Setup */
**************************************************************************
clear all
macro drop _all
capture log close
set more off
set linesize 100

global c_date=strtoname(c(current_date))

#delimiter ;


* create log ;
log using 
"M:\CES_New_Folder_Structure\RESEARCH\Gender_Earnings_Gap\Economists\
FedsDataCenter\MasterLog${c_date}_publicOPMdata.log", 
replace;


/* Create macros for file paths */ ;
*************************************************************************;

/* Data folder */;
global data 
"M:\CES_New_Folder_Structure\RESEARCH\Gender_Earnings_Gap\Economists\FedsDataCenter\ ;


/* Data Management */ ;
*************************************************************************;
* This program reads in publically available OPM data for FY2015 from 
* FedsDataCenter.com, then extracts first full name, and uses an API to 
* genderize this name. Genders and names are saved into 2 Stata datasets:
* "name_genders_run1_v2.dta" & "names_genders_run2_v2.dta"
* This do.file needs to be run on 2 different days, one for each run.;
     do ${data}\Prep4gender_FY2015data.do ; 


* This program merges data with names and gender to publically available 
* OPM  data for FY2015, then prepares this merged data for analysis.
    do ${data}\MergePrep_FedPay2015data_v3.do ; 


/* Data Analysis */ ;
*************************************************************************;
* This program appends the 2 runs of name with gender Stata data sets above into
* a Stata data set: "name_genders_all_v3.dta". Then it merges in gender to the
* public OPM data, saves it as "Federal-Employee-Salaries_FY2015_genders_v3.dta"
* and then analyzes salary data.;
     do ${data}\SalaryBySex_FedPay2015data_v3.do ;


* This program uses "Federal-Employee-Salaries_FY2015_genders_v3.dta" 
* and analyzes bonus data.;
    do ${data}\BonusBySex_FedPay2015data_v3.do ;


*************************************************************************;
/* The end */ ;
*************************************************************************;
#delimit cr
log close

