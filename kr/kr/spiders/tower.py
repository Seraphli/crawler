# -*- coding: utf-8 -*-
import scrapy


class TowerSpider(scrapy.Spider):
    name = 'tower'
    allowed_domains = ['kingdomrushtd.wikia.com']
    start_urls = ['http://kingdomrushtd.wikia.com/wiki/Category:Towers']
    tower_selection = [2, 3]
    upgrade_selection = 1

    def parse(self, response):
        tower_id = 0
        for t in self.tower_selection:
            tower_url = response.css("h3+table")[t].css("div+a::attr(href)").extract()
            tower_type = response.css("h3 span.mw-headline::text")[t].extract()
            self.log("Find %d %s." % (len(tower_url), tower_type))
            for next_page_url in tower_url:
                request = response.follow(next_page_url, callback=self.parse_tower)
                tower_id += 1
                request.meta["tower_id"] = tower_id
                request.meta["tower_type"] = tower_type
                yield request

    def parse_tower(self, response):
        tower_id = response.meta["tower_id"]
        tower_type = response.meta["tower_type"]
        title = response.css(".page-header__title::text").extract_first()
        attr_key = response.css("div h3 b::text").extract()
        b_introduce = False
        if "Introduced" in attr_key:
            b_introduce = True
            del attr_key[attr_key.index("Introduced")]
        b_feature = False
        if "Featured" in attr_key:
            b_feature = True
            del attr_key[attr_key.index("Featured")]
        b_upgrade = False
        if "Upgrades" in attr_key:
            b_upgrade = True
            del attr_key[attr_key.index("Upgrades")]
        attr_value = response.css("div.pi-data-value.pi-font::text").extract()
        attribute = dict(zip(attr_key, attr_value))
        sup = response.css("div div sup::text").extract()
        sup_text = response.css("div.pi-data-value.pi-font a::text").extract()
        KRF_info = []
        for i in range(len(sup)):
            if sup[i] == "KRF":
                KRF_info.append(sup_text[i])
        if not KRF_info:
            self.logger.warning('No element')
            self.logger.warning(sup)
            self.logger.warning(sup_text)
        if b_introduce:
            if len(sup) < len(sup_text):
                if KRF_info:
                    attribute.update({"Introduced": KRF_info[0]})
                else:
                    attribute.update({"Introduced": sup_text})
                if b_upgrade:
                    attribute.update({"Upgrades": sup_text[-1]})
            else:
                if KRF_info:
                    attribute.update({"Introduced": KRF_info[0]})
                else:
                    attribute.update({"Introduced": sup_text})
                if b_upgrade:
                    attribute.update({"Upgrades": KRF_info[1:]})
        if b_feature:
            attribute.update({"Featured": sup_text})
        yield {
            "title": title,
            "tower_id": tower_id,
            "tower_type": tower_type,
            "attribute": attribute
        }
