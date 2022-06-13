# Standard library
import os

# Packages
from bs4 import BeautifulSoup

from base_parser import BaseParser
from markdownify import markdownify
import re
from logging import basicConfig, DEBUG

class EngageParser(BaseParser):
    """
    Parser exclusively for Engage pages
    """

    def __init__(self, api, index_topic_id, url_prefix):
        super().__init__(api, index_topic_id, url_prefix)
        

    def migrate_ep(self):
        """
        Pushes the metadata in the Engage Pages index_topic
        to the invidiual engage pages using category_id
        """
        basicConfig(filename="engage-pages", level=DEBUG)
        index_topic = self.api.get_topic(self.index_topic_id)
        raw_index_soup = BeautifulSoup(
            index_topic["post_stream"]["posts"][0]["cooked"],
            features="html.parser",
        )

        # Parse URL
        self.url_map, self.warnings = self._parse_url_map(
            raw_index_soup, self.url_prefix, self.index_topic_id, "Metadata"
        )

        self.metadata = self._parse_metadata(raw_index_soup, "Metadata")

        # Loop or no loop?
        # all_metadata = next((item for item in self.metadata if "topic_name" not in item), None)
        for metadata in self.metadata:
            topic_soup = BeautifulSoup(metadata["topic"], features="html.parser")
            topic_url = topic_soup.find_all('a', href=True)[0]["href"]
            ep = self.api.get_topic_by_url(topic_url)
            post_content_soup = BeautifulSoup(ep["post_stream"]["posts"][0]["cooked"], features="html.parser")
            post_id = ep["post_stream"]["posts"][0]["id"]
            first_table = post_content_soup.select_one("table:nth-of-type(1)")

            # Already have metadata populated
            if first_table.tbody.select_one("tr:last-child").td.string != "active":
                for item in metadata.items():
                    if item[0] not in ["topic"]:

                        new_tag = BeautifulSoup(f"<tr><td>{item[0]}</td><td>{item[1]}</td></tr>", "html.parser")
                        first_table.tbody.append(new_tag)

                payload = markdownify(str(post_content_soup), heading_style="ATX")
                payload = re.sub('^\n\n\n','', payload)
                payload = payload.replace("\\_", "_")
                try:
                    result = self.api.edit_post(post_id, payload)
                    print(result["topic_id"])
                except Exception as e:
                    print(e)
            else:
                continue
        
    def migrate_takeovers(self, category_id):
        """
        Creates new takeovers using the metadata (takeovers) in the Takeovers index_topic
        and adds the category "Takeovers"
        """
        basicConfig(filename="takeovers", level=DEBUG)
        index_topic = self.api.get_topic(self.index_topic_id)
        raw_index_soup = BeautifulSoup(
            index_topic["post_stream"]["posts"][0]["cooked"],
            features="html.parser",
        )

        # Parse URL
        self.url_map, self.warnings = self._parse_url_map(
            raw_index_soup, self.url_prefix, self.index_topic_id, "Takeovers"
        )

        self.metadata = self._parse_metadata(raw_index_soup, "Takeovers")

        for metadata in self.metadata:
            title = metadata["title"] + " takeover"
            # Check first if post exists
            all_takeovers = self.api.get_topics_category(category_id)
            match_title = any([topic for topic in all_takeovers["topic_list"]["topics"] if topic["title"] == title])

            if match_title:
                continue

            markdown_table = f"""| Key | Value |\n | ------ | ----------|\n"""
            rows = ""
            for [key, value] in metadata.items():
                single_row = f"| {key} | {value} |\n"
                rows += single_row
            markdown_table += rows
            result = self.api.create_topic(markdown_table, title, category_id)
            print("Created takeover!", result["topic_id"])
