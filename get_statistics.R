library(dplyr)

rabota <- read.csv("processed/rabota_processed.csv", stringsAsFactors = FALSE)
work <- read.csv("processed/work_processed.csv", stringsAsFactors = FALSE)
hh <- read.csv("processed/hh_processed.csv", stringsAsFactors = FALSE)

rabota_stat <- rabota %>% group_by(area) %>% mutate(vacancy_n = n()) %>%
  group_by(gender, area, vacancy_n) %>% mutate(gender_marked_n = n()) %>%
  mutate(gender_marked_part = round(gender_marked_n / vacancy_n * 100, 2)) %>%
  group_by(gender_marked_n, gender_marked_part, add = TRUE) %>%
  summarise(mean_salary = mean(money, na.rm = TRUE)) %>%
  filter(gender %in% c("male", "female"), area != "") 

work_stat <- work %>% group_by(area) %>% mutate(vacancy_n = n()) %>%
  group_by(gender, area, vacancy_n) %>% mutate(gender_marked_n = n()) %>%
  mutate(gender_marked_part = round(gender_marked_n / vacancy_n * 100, 2)) %>%
  group_by(gender_marked_n, gender_marked_part, add = TRUE) %>%
  summarise(mean_salary = mean(money, na.rm = TRUE)) %>%
  filter(gender %in% c("male", "female"), area != "")

write.csv(rabota_stat, "rabota_stat.csv", row.names = FALSE)
write.csv(work_stat, "work_stat.csv", row.names = FALSE)