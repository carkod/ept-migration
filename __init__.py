from api import DiscourseAPI
from engage_parser import EngageParser
import os

api=DiscourseAPI(
        base_url="https://discourse.ubuntu.com/",
        api_key=os.environ["DISCOURSE_API_KEY"],
        api_username=os.environ["DISCOURSE_API_USER"]
    )

# EngageParser(api, 18033, "/engage").migrate_ep()
EngageParser(api, 17229, "/takeovers").migrate_takeovers(106)
# Takeovers category id = 28426