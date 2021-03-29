import scrapy

from scrapy.loader import ItemLoader

from ..items import CapitaloneItem
from itemloaders.processors import TakeFirst


class CapitaloneSpider(scrapy.Spider):
	name = 'capitalone'
	start_urls = ['https://www.capitalone.com/about/newsroom/']

	def parse(self, response):
		post_links = response.xpath('//div[contains(@class,"article-tile") and contains(@class,"small-tile") and contains(@class,"show-publish-date")]')
		for post in post_links:
			url = post.xpath('.//a[@class="article-tile-card stretched-link"]/@href').get()
			title = post.xpath('.//h3/text()').get()
			date = post.xpath('.//p[@class="article-meta grv-text--small article"]/span[2]/text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date, 'title': title})

		next_page = response.xpath('/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, date, title):
		description = response.xpath('//div[@class="grv-col--sm-4 article-body-content"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=CapitaloneItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
