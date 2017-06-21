# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider, CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from ..items import VacanciesItem
import re


class WorkSpider(Spider):
	name = "headhunter"
	allowed_domains = ["hh.ua"]
	start_urls = ['https://hh.ua/search/vacancy?text=&area=5']
	
	part_allow = ["/jobs-"]
	part_denied = ["/by-region/", "/by-company/", "/by-titles/"]
	
	VACANCY_RE = re.compile("\/vacancy\/(?P<vacancy_id>\d+)$")
	PAGE_TEMPLATE = "&page={p:d}"

	def parse(self, response):
		areas = response.css('a.clusters-value')
		print(len(areas))
		areas_links = [a.css("a::attr(href)").extract_first() for a in areas if 'from=cluster_industry' in  a.css("a::attr(href)").extract_first()]
		areas_titles = [a.css("span.clusters-value__name::text").extract_first() for a in areas if 'from=cluster_industry' in  a.css("a::attr(href)").extract_first()]
		areas_amount = [int(a.css("a span.clusters-value__count::text").extract_first()) for a in areas if 'from=cluster_industry' in  a.css("a::attr(href)").extract_first()]
		print(areas_titles, areas_amount)
		for i in range(len(areas_links)):
			yield scrapy.Request(response.urljoin(areas_links[i]), callback=self.parse_area, meta = {"area":areas_titles[i], "number":areas_amount[i]})
	
	def parse_area(self, response):
		pages = response.css("li a.HH-Pager-Control::text").extract()
		number_of_pages = response.request.meta['number'] // 20 + 1
		for i in range(number_of_pages):
			yield scrapy.Request(response.url + self.PAGE_TEMPLATE.format(p = i), callback = self.parse_page, meta = {"area":response.request.meta['area']})
		"""print(pages)
		pages_n = [int(p.replace(u"Страница ","")) for p in pages]
		if len(pages_n) > 0:
			max_page_number = max(pages_n)
		else:
			max_page_number = 1
		pages_hrefs = [response.url,]
		for page in range(2, max_page_number + 1):
			pages_hrefs.append(response.urljoin(self.PAGE_TEMPLATE.format(p = page)))
		for p in pages_hrefs:
			yield scrapy.Request(p, callback=self.parse_page, meta = {"area":response.request.meta['area']})"""
	
	def parse_page(self, response):
		links = [l.css("a::attr(href)").extract_first() for l in response.css("div.search-result-item__head a")]
		#job_links = [l for l in links if self.VACANCY_RE.fullmatch(l) ]
		for jl in links:
			full_url = response.urljoin(jl)
			yield scrapy.Request(full_url, callback=self.parse_vacancy, meta = {"area":response.request.meta['area']})
	
	def parse_vacancy(self, response):
		item = VacanciesItem()
		links = [l for l in response.css("a") if "company" in l.css("::attr(href)").extract_first() ]
		
		#print(links)
		link_company_name = response.css(".companyname a")
		item['company_name'] = link_company_name.css("a::text").extract_first()
		item['company_id'] = link_company_name.css("a::attr(href)").extract_first().split("/")[-1]
		item['area'] = response.request.meta['area']
		item['vacancy_title'] = response.css(".b-vacancy-title::text").extract_first()
		item['vacancy_id'] = self.VACANCY_RE.search(response.url).group("vacancy_id")
		#print(item['vacancy_title'])
		item['region'] =  response.css('.l-content-colum-2.b-v-info-content .l-paddings::text').extract_first()
		item['employment_type'] = response.css('span[itemprop="employmentType"]::text').extract_first()
		demands = response.css('div[itemprop="experienceRequirements"]::text').extract_first()
		#item['demands'] = response.xpath('//dt[contains(text(),"Требования")]/following-sibling::dd[1]/text()').extract_first()
		try:
			item['demands'] = demands.strip()
		except Exception:
			item['demands'] = demands
		item['description'] = response.css('div[itemprop="description"]').extract_first()
		item['money'] = response.css('.l-content-colum-1.b-v-info-content .l-paddings::text').extract_first()
		#item['area'] = response.css(".f-text-black.fd-craftsmen::text").extract_first()
		yield item
		
		
