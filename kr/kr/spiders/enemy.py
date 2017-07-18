# -*- coding: utf-8 -*-
import scrapy


class EnemySpider(scrapy.Spider):
    name = 'enemy'
    allowed_domains = ['kingdomrushtd.wikia.com']
    start_urls = ['http://kingdomrushtd.wikia.com/wiki/Category:Enemies']
    enemy_selection = [2, 3]

    def parse(self, response):
        for t in self.enemy_selection:
            enemy_url = response.css("h3+table")[t].css("div+a::attr(href)").extract()
            enemy_type = response.css("h3 span.mw-headline::text")[t].extract()
            self.log("Find %d %s." % (len(enemy_url), enemy_type))
            for next_page_url in enemy_url:
                request = response.follow(next_page_url, callback=self.parse_enemy)
                request.meta["enemy_type"] = enemy_type
                yield request

    def parse_enemy(self, response):
        enemy_type = response.meta["enemy_type"]
        title = response.css(".page-header__title::text").extract_first()
        attr_key = response.css(".pi-data-label.pi-secondary-font b::text").extract()
        attr_value = response.css("div.pi-data-value.pi-font::text").extract()
        if not attr_key:
            attr_key = response.css("div.center+table").css("td b::text").extract()
            attr_value = response.css("div.center+table").css("td::text").extract()
        yield {
            "title": title,
            "enemy_type": enemy_type,
            "attribute": dict(zip(attr_key, attr_value))
        }
