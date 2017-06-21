# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class VacanciesItem(scrapy.Item):
	# define the fields for your item here like:
	# name = scrapy.Field()
	date = scrapy.Field()
	company_id = scrapy.Field()
	company_name = scrapy.Field()
	area = scrapy.Field()
	vacancy_title = scrapy.Field()
	employment_type = scrapy.Field()
	description = scrapy.Field()
	money = scrapy.Field()
	region = scrapy.Field()
	demands = scrapy.Field()
	vacancy_id = scrapy.Field()

