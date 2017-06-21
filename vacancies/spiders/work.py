# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider, CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from ..items import VacanciesItem
import re


class WorkSpider(Spider):
	name = "work"
	allowed_domains = ["work.ua"]
	start_urls = ['https://www.work.ua/jobs/by-category/']
	
	part_allow = ["/jobs-"]
	part_denied = ["/by-region/", "/by-company/", "/by-titles/"]
	
	VACANCY_RE = re.compile("\/jobs\/(?P<vacancy_id>\d+)\/$")
	PAGE_TEMPLATE = "?page={p:d}"

	def parse(self, response):
		print(len(response.xpath("//a")))
		for url in response.xpath('//a'):
			#print(url.extract())
			area = url.css("::text").extract_first()
			href = url.css("::attr(href)").extract_first()
			#print(area, href)
			right_url = False
			for pa in self.part_allow:
				#print(pa)
				if pa in href:
					right_url = True
					for pd in self.part_denied:
						if pd in href:
							right_url = False
			if right_url:
				href = href.replace("-kyiv","")
				full_url = response.urljoin(href)
				yield scrapy.Request(full_url, callback=self.parse_area, meta = {"area":area})
	
	def parse_area(self, response):
		pages = response.css("ul.pagination a::attr(title)").extract()
		pages_n = [int(p.replace(u"Страница ","")) for p in pages]
		if len(pages_n) > 0:
			max_page_number = max(pages_n)
		else:
			max_page_number = 1
		pages_hrefs = [response.url,]
		for page in range(2, max_page_number + 1):
			pages_hrefs.append(response.urljoin(self.PAGE_TEMPLATE.format(p = page)))
		for p in pages_hrefs:
			yield scrapy.Request(p, callback=self.parse_page, meta = {"area":response.request.meta['area']})
	
	def parse_page(self, response):
		links = [l.css("::attr(href)").extract_first() for l in response.css("a") if l.css("::attr(href)").extract_first()]
		job_links = [l for l in links if self.VACANCY_RE.fullmatch(l) ]
		for jl in job_links:
			full_url = response.urljoin(jl)
			yield scrapy.Request(full_url, callback=self.parse_vacancy, meta = {"area":response.request.meta['area']})
	
	def parse_vacancy(self, response):
		item = VacanciesItem()
		links = [l for l in response.css("a") if "company" in l.css("::attr(href)").extract_first() ]
		item['company_id'] = links[0].css("::attr(href)").extract_first().split("/")[-2]
		#print(links)
		link_company_name = [l for l in links if l.css("b")]
		item['company_name'] = link_company_name[0].css("b::text").extract_first()
		item['area'] = response.request.meta['area']
		item['vacancy_title'] = response.css("#h1-name::text").extract_first()
		item['vacancy_id'] = self.VACANCY_RE.search(response.url).group("vacancy_id")
		#print(item['vacancy_title'])
		item['region'] =  response.xpath('//dt[contains(text(),"Город")]/following-sibling::dd[1]/text()').extract_first()
		item['employment_type'] = response.xpath('//dt[contains(text(),"Вид занятости")]/following-sibling::dd[1]/text()').extract_first()
		demands = response.xpath('//dt[contains(text(),"Требования")]/following-sibling::dd[1]/text()').extract_first()
		#item['demands'] = response.xpath('//dt[contains(text(),"Требования")]/following-sibling::dd[1]/text()').extract_first()
		try:
			item['demands'] = demands.strip()
		except Exception:
			item['demands'] = demands
		item['description'] = response.xpath('//div[@class="overflow wordwrap"]').extract_first()
		try:
			item['money'] = response.xpath('//h3[@class="wordwrap"]/b/text()').extract_first()  + response.xpath('//h3[@class="wordwrap"]/text()').extract_first()
		except Exception:
			try:
				item['money'] = response.xpath('//h3[@class="wordwrap"]/b/text()').extract_first()
			except Exception:
				item['money'] = response.xpath('//h3[@class="wordwrap"]/text()').extract_first()
		#item['area'] = response.css(".f-text-black.fd-craftsmen::text").extract_first()
		yield item
		
		
