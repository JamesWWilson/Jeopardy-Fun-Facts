
# I. Set Up Analysis  -----------------------------------------------------
knitr::opts_chunk$set(echo = TRUE)

#Remove Objects
rm(list = ls())

#Clear Memory
gc(reset = TRUE)

#Set Working Directory
setwd("C:/Users/jwilson2/Desktop/GitHub/Jeopardy-Fun-Facts")

#Load Packages
require(stringr)
require(tidyverse)
require(dplyr)		#Data frame functions
require(data.table)
require(dtplyr)
require(stringi)
require(ggplot2)		#Graphics
require(lubridate)
require(readxl)
require(reshape2)
require(rgdal)
require(ggthemes)
require(viridis) #devtools::install_github("sjmgarnier/viridis")
require(scales)
require(grid)
require(gridExtra)
require(ggmap)
require(openxlsx)
require(usmap)
#Set custom functions
source("//wdc1islfls02/CHI1FLS02_TSP/LosAngeles/Admin/007_RProgramming/nciCustomFunctions/R/nci_cleanDT/2.0/nci_cleanDT.r")

# II. Load Data ---------------------------------------------------------------

jep <- read.csv("Data/clean_jeopardy_data.csv", colClasses = "character")

location_cnts2 <- jep %>% group_by(Hometown, lat, lng) %>%
  summarise(plr_cnt = length(unique(Full.Name))) %>%
  ungroup %>% mutate(lat = as.numeric(lat),
                     lon = as.numeric(lng),
                     freq = as.numeric(plr_cnt)) %>% select(lon,lat,freq)


location_cnts <- jep %>% group_by(county_fips) %>% 
  summarise(freq = length(unique(Full.Name))) %>% 
  ungroup %>% mutate(county_fips = as.character(county_fips),
    freq = as.numeric(freq)) %>% select(county_fips,freq)

  
  transformed_data <- usmap_transform(location_cnts2)

  plot_usmap("states") +
    geom_point(data = transformed_data, aes(x = lon.1, y = lat.1, size = freq),
               color = "orange"
              , alpha = 0.5
               )+
    labs(title = "US Jeopardy Players",
         subtitle = "Source: Jeopardy Archive",
         size = "Frequency") +
    theme(legend.position = "right")


  library(socviz)
  data("county_map")  
  str(county_map)
  data("county_data")  
  str(county_data)

  
  
  county_full <- left_join(county_map, county_data, by = "id")
  
  p <- ggplot(data = county_full,
              mapping = aes(x = long, y = lat,
                            fill = pop_dens, 
                            group = group))
  
  p1 <- p + geom_polygon(color = "gray90", size = 0.05) + coord_equal()
  
  p2 <- p1 + scale_fill_brewer(palette="Blues",
                               labels = c("0-10", "10-50", "50-100", "100-500",
                                          "500-1,000", "1,000-5,000", ">5,000"))
  
  p2 + labs(fill = "Population per\nsquare mile") +
    theme_map() +
    guides(fill = guide_legend(nrow = 1)) + 
    theme(legend.position = "bottom")
  
  
  
  ## WORKING 
  maps::county.fips %>%
    as_tibble %>% 
    extract(polyname, c("region", "subregion"), "^([^,]+),([^,]+)$") ->
    dfips
  
  map_data("county") %>% 
    left_join(dfips) ->
    dall
  
  dall %>% 
    mutate(is_example = fips %in% jep$county_fips) %>% 
    ggplot(aes(long, lat, group = group)) +
    geom_polygon(aes(fill=is_example), color="gray70") +
    coord_map() +
    scale_fill_manual(values=c("TRUE"="red", "FALSE"="gray90"))
  
  
  
  hist(location_cnts$freq,breaks=20)
  boxplot(location_cnts$freq)
  
  location_cnts <- location_cnts %>% as.data.table()
  location_cnts[nchar(county_fips)==4,county_fips := paste0("0",county_fips),]
  
  county_full_dt <- merge(county_map, location_cnts, by.x = "id", by.y = "county_fips", all.x = TRUE) %>% as.data.table()
  #county_full_dt[is.na(freq)==TRUE, freq:=0,]
  county_full_dt[freq == 1, freq_cat:="01",]
  county_full_dt[freq > 1 & freq <= 5, freq_cat:="02-05",]
  county_full_dt[freq > 5 & freq <= 10, freq_cat:="06-10",]
  county_full_dt[freq > 10 & freq <= 20, freq_cat:="11-20",]
  county_full_dt[freq > 20 & freq <= 40, freq_cat:="20-40",]
  county_full_dt[freq > 40, freq_cat:="40+",]
  county_full_dt[is.na(freq_cat)==TRUE, freq_cat:="0",]
  county_full_dt[,freq_cat:=as.factor(freq_cat),]
  
  county_full_dt <- as.data.table(county_full_dt)[is.na(freq)==TRUE, freq:=0,]
  test <- county_full_dt %>% mutate(region = as.numeric(id), value = (freq_cat)) %>% select(region,value) %>% unique()
  county_choropleth(test, num_colors=6)

  # Changing colors, harder and works for all states
  choro1<-CountyChoropleth$new(test)
  choro1$title = "Jeopardy Player Hometowns"
  col.pal<-brewer.pal(6,"YlOrRd")
  choro1$ggplot_scale <- scale_fill_manual(name="Number of Jeopardy Players",values=c("white",col.pal), drop=FALSE)
  choro1$render()
  
  
  # test2 <- county_full_dt %>% mutate(region = as.numeric(id), value = (freq)) %>% select(region,value) %>% unique()
  # choro2<-CountyChoropleth$new(test2)
  # choro2$set_num_colors(1)
  # choro2$ggplot_scale = scale_fill_gradientn(name = "Population", colours = c(brewer.pal(6, "RdBu")))
  # choro2$render()
  
  
  
  # p <- ggplot(data = county_full_dt,
  #              mapping = aes(x = long, y = lat,
  #                           fill = freq_cat, 
  #                           group = group))
  # 
  # p1 <- p + geom_polygon(color = "gray90",size = 0.05) + coord_equal()
  # 
  # p2 <- p1 + scale_fill_brewer(palette="Blues",labels = c("0","1-10", "11-20", "21-30", "31-40",
  #                                                          "41-50", "51-60", "60+"))
  # #p2 <- p1 + scale_fill_manual(values=c("#999999", "#E69F00", "#56B4E9","#C72230","#F08A27","#1D326B","#25F7C3"))
  # 
  # p3 <- p2 + labs(fill = "Jeopardy contestants") +
  #   theme_map() +
  #   guides(fill = guide_legend(nrow = 1)) +
  #   theme(legend.position = "bottom")
  # 
  # p3
  
  
  
  
  # working 
  
  dall %>% 
    mutate(is_example = fips %in% jep$county_fips) %>% 
    ggplot(aes(long, lat, group = group)) +
    geom_polygon(aes(fill=is_example), color="gray70") +
    coord_map() +
    scale_fill_manual(values=c("TRUE"="red", "FALSE"="gray90"))
  
  
  
  
  str(county_full)
  county_full$pop_dens
  
  p <- ggplot(data = county_full,
              mapping = aes(x = long, y = lat,
                            fill = pop_dens, 
                            group = group))
  
  p1 <- p + geom_polygon(color = "gray90", size = 0.05) + coord_equal()
  
  p2 <- p1 + scale_fill_brewer(palette="Blues",
                               labels = c("0-10", "10-50", "50-100", "100-500",
                                          "500-1,000", "1,000-5,000", ">5,000"))
  
  p2 + labs(fill = "Population per\nsquare mile") +
    theme_map() +
    guides(fill = guide_legend(nrow = 1)) + 
    theme(legend.position = "bottom")
  
  

# new try -----------------------------------------------------------------


  
  
  library(choroplethr)
  library(choroplethrMaps)
  str(test)
  #test <- location_cnts %>%  mutate(region = as.numeric(county_fips), value = as.numeric(freq)) %>% select(region,value)
  county_full_dt <- as.data.table(county_full_dt)[is.na(freq)==TRUE, freq:=0,]
  test <- county_full_dt %>%  mutate(region = as.numeric(id), value = (freq_cat)) %>% select(region,value) %>% unique()
  county_choropleth(test, num_colors = 6)
  
  ?county_choropleth

