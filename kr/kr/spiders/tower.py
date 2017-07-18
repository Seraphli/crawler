# -*- coding: utf-8 -*-
import scrapy


class TowerSpider(scrapy.Spider):
    name = 'tower'
    allowed_domains = ['kingdomrushtd.wikia.com']
    start_urls = ['http://kingdomrushtd.wikia.com/wiki/Category:Towers']
    tower_selection = [2, 3]
    upgrade_selection = 1

    def parse(self, response):
        tower_url = []
        for t in self.tower_selection:
            tower_url += response.css("h3+table")[t].css("div+a::attr(href)").extract()
        self.log("Find %d tower." % len(tower_url))
        for next_page_url in tower_url:
            yield response.follow(next_page_url, callback=self.parse_tower)

    def parse_tower(self, response):
        title = response.css(".page-header__title::text").extract_first()
        attr_key = response.css("div.center+table").css("td b::text").extract()
        if response.css("span#Upgrades::text").extract():
            attr_value = response.css("div.center+table").css("td::text").extract()[:len(attr_key) - 1]
            upgrade = [response.css("h3+p a::text").extract()[self.upgrade_selection],
                       response.css("h3+p+p a::text").extract()[self.upgrade_selection]]
            attr_value += [upgrade]
        else:
            attr_value = response.css("div.center+table").css("td::text").extract()
        yield {
            "title": title,
            "attribute": dict(zip(attr_key, attr_value))
        }
