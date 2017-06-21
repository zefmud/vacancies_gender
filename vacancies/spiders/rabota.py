# -*- coding: utf-8 -*-

import scrapy
import re
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from ..items import VacanciesItem


class RabotaSpider(CrawlSpider):
	name = "rabota"
	allowed_domains = ["rabota.ua"]
	start_urls = ['https://rabota.ua/jobsearch/vacancy_list']

	VACANCY_RE = re.compile("\/vacancy(?P<vacancy_id>\d+)$")


	rules = (
		Rule(LxmlLinkExtractor(allow = ('vacancy_list', 'pg'), deny = ["company", "service"]), follow = True),
		Rule(LxmlLinkExtractor(allow = ("vacancy"), deny = ("employer", "vacancy_list", "service")), callback = 'parse_vacancy')
		)

	def parse_vacancy(self, response):
		item = VacanciesItem()
		item['date'] = response.css(".f-date-holder::text").extract_first()
		try:
			item['vacancy_id'] = self.VACANCY_RE.search(response.url).group("vacancy_id")
			item['company_id'] = response.css(".fd-soldier::attr(href)").extract_first().split("#")[1]
			item['company_name'] = response.xpath('//span[@itemprop="name"]/text()').extract_first()
			item['region'] = response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first()
			item['area'] = response.css(".f-text-black.fd-craftsmen::text").extract_first()
			item['vacancy_title'] = response.css(".f-vacname-holder.fd-beefy-ronin.f-text-black::text").extract_first()
			item['employment_type'] = response.xpath('//span[@itemprop="employmentType"]/text()').extract_first()
			item['description'] = response.xpath('//div[@itemprop="description"]').extract_first()
			item['money'] = response.xpath('//span[@class="money"]/text()').extract_first()
		except Exception:
			item['company_id'] = ""
			item['description'] = response.css('div.d_des').extract_first()

		yield item
		#zayniatist | itemprop="employmentType"
		#description | itemprop="description"
		#area | class="f-text-black fd-craftsmen"
