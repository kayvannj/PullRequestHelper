import os
import unittest

import prh


class PrhTests(unittest.TestCase):
    def test_config_file_migration(self):
        old_config_path = "test1.py"
        with open(old_config_path, "w") as f:
            f.write('test1_param1 = "test1 Value1 "')
        self.assertTrue(os.path.isfile(old_config_path), "old config doesn't exist")
        new_config_path = "test1.json"
        prh.migrate_config_file(from_path=old_config_path, to_path=new_config_path)
        self.assertFalse(os.path.isfile(old_config_path), "old config didn't get removed after migration")
        self.assertTrue(os.path.isfile(new_config_path), "new config doesn't exists after migration")
        config_file = prh.read_from_config_file(file_path=new_config_path)
        self.assertEqual(config_file["test1_param1"], 'test1 Value1', "the values didn't carry over to new config")

    def test_pr_template_append(self):
        pass

    def test_multiple_link_in_commit_message(self):
        cm, full_url, story_ids = prh.parse_commit_message(
            "this ishttps://www.pivotaltracker.com/story/show/140176051 https://www.pivotaltracker.com/story/show/139604723a test",
            [], [])
        self.assertEqual(cm, "this is a test")
        self.assertEqual(full_url, ["https://www.pivotaltracker.com/story/show/140176051",
                                    "https://www.pivotaltracker.com/story/show/139604723"])
        self.assertEqual(story_ids, ["140176051", "139604723"])
