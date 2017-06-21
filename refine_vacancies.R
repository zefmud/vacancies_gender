library(textcat)
library(stringr)
library(dplyr)

word_start <- "(^|[[:punct:]|[:blank:]]|$|<])"
word_end <- "([[:punct:]|[:blank:]]|$|<])"
tag_regex <- "(<[^>]*>)"
#cyrillic_marker <- "[А-Я]"
ukrainian_marker <- "[ҐґЄєІіЇї]"
russian_marker <- "[ЫыЪъЁёЭэ]"

gm <- read.csv("gender_markers.csv", stringsAsFactors = FALSE)
gender_markers <- list()
gender_markers$male_markers <- paste0(word_start, gm$male_markers[gm$male_markers != ''], word_end)
gender_markers$female_markers <- paste0(word_start, gm$female_markers[gm$female_markers != ''], word_end)

#ua_stopwords <- read.csv("stopwords_ukrainian.csv")

mark_string <- function(s) {
  male_marker <-  sum(sapply(gender_markers$male_markers,grepl, s, ignore.case = TRUE)) > 0
  female_marker <- sum(sapply(gender_markers$female_markers,grepl, s, ignore.case = TRUE)) > 0
  if (male_marker) {
    if (!female_marker) {
      "male"
    } else {
      "both"
    }
  } else {
    if (female_marker) {
      "female"
    } else {
      "none"
    }
  }
}

mark_language <- function(s) {
  cat <- textcat(s)
  if (grepl("russian", cat)) {
    if (str_count(s, ukrainian_marker) > str_count(s, russian_marker)) {
      "ukr"
    } else {
      "ru"
    }
  } else {
    "en"
  }
}

refine_work_money <- function(s) {
  str_split(s, " грн")[[1]][1]
}

rabota_old <- read.csv("rabota_26_05.csv", stringsAsFactors = FALSE)
work_old <- read.csv("work_26_05_2017.csv", stringsAsFactors = FALSE)
hh_old <- read.csv("headhunter_25_05.csv", stringsAsFactors = FALSE)
rabota_new <- read.csv("rabota_07_06.csv", stringsAsFactors = FALSE)
work_new <- read.csv("work_07_06.csv", stringsAsFactors = FALSE)
hh_new <- read.csv("headhunter_07_06.csv", stringsAsFactors = FALSE)

rabota_new <- filter(rabota_new, !vacancy_id %in% rabota_old$vacancy_id)
work_new <- filter(work_new, !vacancy_id %in% work_old$vacancy_id)
hh_new <- filter(hh_new, !vacancy_id %in% hh_old$vacancy_id)

rabota <- rbind(rabota_old, rabota_new)
work <- rbind(work_old, work_new)
hh <- rbind(hh_old, hh_new)

rabota$description <- gsub(tag_regex, " ", rabota$description)
rabota$gender <- sapply(rabota$description, mark_string)
rabota$money <- as.numeric(gsub("[^[:digit:]]", "", rabota$money))
work$description <- gsub(tag_regex, " ", work$description)
work$gender <- sapply(work$description, mark_string)
work$money <- as.numeric(sapply(work$money, refine_work_money))
hh$description <- gsub(tag_regex, " ", hh$description)
hh$gender <- sapply(hh$description, mark_string)

hh$language <- sapply(hh$description, mark_language)
rabota$language <- sapply(rabota$description, mark_language)
work$language <- sapply(work$description, mark_language)

#write.csv(hh, "processed/hh_processed.csv", row.names = FALSE)
#write.csv(rabota, "processed/rabota_processed.csv", row.names = FALSE)
#write.csv(work, "processed/work_processed.csv", row.names = FALSE)

