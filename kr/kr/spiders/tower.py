# -*- coding: utf-8 -*-
import scrapy


class TowerSpider(scrapy.Spider):
    name = 'tower'
    allowed_domains = ['kingdomrushtd.wikia.com']
    start_urls = ['http://kingdomrushtd.wikia.com/wiki/Category:Towers']
    tower_selection = [2, 3]
    upgrade_selection = 1

    def parse(self, response):
        for t in self.tower_selection:
            tower_url = response.css("h3+table")[t].css("div+a::attr(href)").extract()
            tower_type = response.css("h3 span.mw-headline::text")[t].extract()
            self.log("Find %d %s." % (len(tower_url), tower_type))
            for next_page_url in tower_url:
                request = response.follow(next_page_url, callback=self.parse_tower)
                request.meta["tower_type"] = tower_type
                yield request

    def parse_tower(self, response):
        tower_type = response.meta["tower_type"]
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
            "tower_type": tower_type,
            "attribute": dict(zip(attr_key, attr_value))
        }
