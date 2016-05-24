import json
import prh_config
import requests

__author__ = 'kayvan'

API_TOKEN = prh_config.PIVOTAL_TRACKER_API_TOKEN

base_endpoint = "https://www.pivotaltracker.com/services/v5"


def get(api):
    response = requests.get(api, headers={"X-TrackerToken": API_TOKEN})
    print(api, response.status_code)
    return response


def post(api, data):
    response = requests.post(api, data=data, headers={"X-TrackerToken": API_TOKEN})
    print(api, response.status_code)
    return response


def put(api, data):
    response = requests.put(api, data=data, headers={"X-TrackerToken": API_TOKEN})
    print(api, response.status_code)
    return response


def get_story(project_id, story_id):
    resp = get("{}/projects/{}/stories/{}".format(base_endpoint, project_id, story_id))
    return resp.json()


def mark_story_finished(project_id, story_id):
    api = "{}/projects/{}/stories/{}".format(base_endpoint, project_id, story_id)
    resp = put(api, {"current_state": "finished"})
    return resp.json()


def post_comment(project_id, story_id, text):
    api = "{}/projects/{}/stories/{}/comments".format(base_endpoint, project_id, story_id)
    resp = post(api, {"text": text})
    return resp.json()


def get_project_id(story_id):
    api = "{}/stories/{}".format(base_endpoint, story_id)
    resp = get(api)
    return resp.json()["project_id"]


def finish_and_post_message(story_id, message):
    project_id = get_project_id(story_id)
    if not API_TOKEN:
        return 1
    if not mark_story_finished(project_id, story_id):
        return 1
    if not post_comment(project_id, story_id, message):
        return 1
    return 0


if __name__ == '__main__':
    pass
