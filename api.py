import requests
import os

class NoCredentials(Exception):
    def __init__(self, *args: object) -> None:
        print("Please provide api_key and api_username to the DicourseAPI instance")

class DiscourseAPI:
    """
    Retrieve information from a Discourse installation
    through its API
    """

    def __init__(
        self,
        base_url,
        api_key,
        api_username,
        get_topics_query_id=None,
    ):
        """
        @param base_url: The Discourse URL (e.g. https://discourse.example.com)
        """

        self.base_url = base_url.rstrip("/")
        self.get_topics_query_id = get_topics_query_id
        self.session = requests.sessions.Session()

        if api_key and api_username:
            self.session.headers = {
                "Api-Key": api_key,
                "Api-Username": api_username,
            }
        else:
            raise NoCredentials()

    def __del__(self):
        self.session.close()

    def get_topic(self, topic_id):
        """
        Retrieve topic object by path
        """

        response = self.session.get(f"{self.base_url}/t/{topic_id}.json")
        response.raise_for_status()

        return response.json()
    
    def get_topic_by_url(self, url):
        """
        Retrieve topic object by path
        """

        response = self.session.get(f"{url}.json")
        response.raise_for_status()

        return response.json()
    
    def get_post(self, post_id):
        url = f"{self.base_url}/posts/{post_id}.json"
        response = self.session.get(url)
        response.raise_for_status()

        return response.json()
    
    def edit_post(self, post_id, raw):
        payload = {
            "post": {
                "raw": raw,
                "edit_reason": "Remove requirement to use index topic"
            }
        }
        url = f"{self.base_url}/posts/{post_id}.json"
        response = self.session.put(url, json=payload)
        response.raise_for_status()

        return response.json()

    def get_topics(self, topic_ids):
        """
        This endpoint returns multiple topics HTML cooked content.
        This is possible with the Data Explorer plugin for Discourse
        we are using it to obtain multiple Tutorials content without
        doing multiple API calls.
        """
        headers = {
            "Accept": "application/json",
            "Content-Type": "multipart/form-data;",
        }

        # Run query on Data Explorer with topic IDs
        topics = ",".join([str(i) for i in topic_ids])

        response = self.session.post(
            f"{self.base_url}/admin/plugins/explorer/"
            f"queries/{self.get_topics_query_id}/run",
            headers=headers,
            data={"params": f'{{"topics":"{topics}"}}'},
        )

        return response.json()["rows"]

    def get_topics_category(self, category_id, page=None):
        response = self.session.get(
            f"{self.base_url}/c/{category_id}.json",
            params={"page": page}
        )
        response.raise_for_status()

        return response.json()

    def create_topic(self, raw, title, category_id=0):
        payload = {
            "title": title,
            "raw": raw,
            "category": category_id
        }
        response = self.session.post(
            f"{self.base_url}/posts.json",
            json=payload
        )
        response.raise_for_status()

        return response.json()
    
    def update_topic(self, id, category_id):
        payload = {
            "topic": {
                "category_id": category_id
            }
        }
        response = self.session.put(
            f"{self.base_url}/t/{id}.json",
            json=payload
        )
        response.raise_for_status()
        return response.json()
