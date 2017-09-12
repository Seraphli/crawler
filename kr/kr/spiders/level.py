# -*- coding: utf-8 -*-
import scrapy


class LevelSpider(scrapy.Spider):
    name = 'level'
    allowed_domains = ['kingdomrushtd.wikia.com']
    start_urls = ['http://kingdomrushtd.wikia.com/wiki/Category:Levels']
    level_selection = [3]

    def parse(self, response):
        for t in self.level_selection:
            level_url = response.css(".article-table.article-table-selected")[t].css("div+a::attr(href)").extract()
            level_type = response.css("h3 span.mw-headline::text")[t].extract()
            self.log("Find %d %s." % (len(level_url), level_type))
            level_index = 1
            for next_page_url in level_url:
                request = response.follow(next_page_url, callback=self.parse_tower)
                request.meta["level_type"] = level_type
                request.meta["level_index"] = level_index
                yield request
                level_index += 1

    def parse_tower(self, response):
        level_type = response.meta["level_type"]
        level_index = response.meta["level_index"]
        title = response.css(".page-header__title::text").extract_first()

        # extract scenery tower
        index = 0
        seen = False
        for ele in response.css(".WikiaArticle ul li"):
            text = "".join(ele.css("::text").extract())
            index += 1
            if "Strategic Point" in text:
                if seen:
                    index -= 1
                    break
                else:
                    seen = True
                    continue
            if "Gold" in text or "gold" in text:
                index -= 1
                break
        info = response.css(".WikiaArticle ul li")[:index]
        # put this together
        # [' ', 'Strategic Point', ' x10\n', ' ', 'Legion Archer', ' x2\n']
        scenery = []
        for i in range(index):
            scenery.append("".join(info[i].css("::text").extract()).lstrip().replace('\n', '').replace('\u00a0', ' '))

        # extract gold
        index = 0
        for ele in response.css(".WikiaArticle ul li").extract():
            index += 1
            if "Gold" in ele or "gold" in ele:
                break
        info = response.css(".WikiaArticle ul li")[index - 1].css("::text").extract()
        initial_gold = "".join(info[0:3]).lstrip().lower().replace(' gold\n', '').replace('\u00a0', ' ')

        # extract wave information
        wave_info = response.css(".wikitable")[0]
        row_len = len(response.css(".wikitable")[0].css("tr"))
        col_len = len(response.css(".wikitable")[0].css("tr")[0].css("td"))
        table = []
        for r in range(row_len):
            row = []
            # remove income
            for c in range(col_len - 1):
                num = len(wave_info.css("tr")[r].css("td")[c].css("a"))
                if num > 0:
                    info = wave_info.css("tr")[r].css("td")[c].css("::text").extract()[1:]
                    monster = []
                    for n in range(num):
                        monster.append("".join(info[n * 2:(n + 1) * 2]).replace('\n', '').replace('\u00a0', ' '))
                    row.append(",".join(monster))
                else:
                    info = wave_info.css("tr")[r].css("td")[c].css("::text").extract()
                    row.append("".join(info).replace('\n', '').lstrip().replace('\u00a0', ' '))
            table.append(row)

        yield {
            "title": title,
            "level_index": level_index,
            "level_type": level_type,
            "scenery": scenery,
            "initial_gold": initial_gold,
            "wave_info": {"row": row_len, "col": col_len, "table": table}
        }
