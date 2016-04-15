import json

__author__ = 'kayvan'

import requests

API_TOKEN = "API TOKEN"
# PROJECT_ID = 61085 #mobile
# story_id = 115053971
PROJECT_ID = 1473026
STORY_ID = 107210010

base_endpoint = "https://www.pivotaltracker.com/services/v5"


def get(api):
    return requests.get(api, headers={"X-TrackerToken": API_TOKEN})


def post(api, data):
    return requests.post(api, data=data, headers={"X-TrackerToken": API_TOKEN})


def put(api, data):
    return requests.put(api, data=data, headers={"X-TrackerToken": API_TOKEN})


def get_story(project_id, story_id):
    resp = get("{}/projects/{}/stories/{}".format(base_endpoint, project_id, story_id))
    return resp.json()


def mark_story_finished(project_id, story_id):
    resp = put("{}/projects/{}/stories/{}".format(base_endpoint, project_id, story_id), {"current_state": "finished"})
    return resp.json()


def post_comment(project_id, story_id, text):
    resp = post("{}/projects/{}/stories/{}/comments".format(base_endpoint, project_id, story_id),
                {"text": text})
    print(resp.status_code)


if __name__ == '__main__':
    try:
        print mark_story_finished(PROJECT_ID, STORY_ID)
    except requests.exceptions.ConnectionError:
        print("Error connecting to Pivotal Tracker api")
