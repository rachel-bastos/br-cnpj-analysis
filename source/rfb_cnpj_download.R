#===================================================================================
# rfb_cnpj_download.R
#
# Purpose: Download, parse and export RFB data in json lines format.
#
# This script assumes:
#     - a folder structure as described on README
#===================================================================================

# packages -------------------------------------------------------------------------

if (!require("install.load")) {
  install.packages("install.load")
  library(install.load)
}
install_load("dplyr","tidyr","jsonlite","tibble","magrittr","devtools")
devtools::install_github("jtrecenti/rfbCNPJ")

# inputs --------------------------------------------------------------------------

statesList <- c('AC','AL','AM','AP','BA','CE','DF','ES','GO','MA','MG','MS','MT','PA',
         'PB','PE','PI','PR','RJ','RN','RO','RR','RS','SC','SE','SP','TO')

# working directory ---------------------------------------------------------------

args = R.utils::commandArgs(trailingOnly=TRUE, asValues=TRUE)
wd = args['path']
dir.create(paste0(wd,'json_data'))
dir.create(paste0(wd,'json_data/companies'))
dir.create(paste0(wd,'json_data/employees'))

# download data
rfb_download(ufs = statesList, path = wd)

data(qualificacao)
jsonlite::stream_out(qualificacao, file(paste0(wd,'json_data/positions.json')))

files <- list.files(wd, "*.txt", full.names = T)

lapply(files, function(f){
  
  state <- substr(f, nchar(f)-5, nchar(f)-4)
  
  # import and parse data
  rfb_data <- rfb_read(f)
  
  companies <- rfb_data %>% 
    select(file, company) %>%
    unnest(company) %>%
    mutate(uf = state)
  
  employees <- rfb_data %>% 
    select(file, employee) %>%
    unnest(employee)%>%
    mutate(uf = state)
  
  # export data to json
  jsonlite::stream_out(companies, file(paste0(wd,'json_data/companies/',state,'.json')))
  jsonlite::stream_out(employees, file(paste0(wd,'json_data/employees/',state,'.json')))
})