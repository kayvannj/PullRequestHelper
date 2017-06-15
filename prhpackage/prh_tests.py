import os
import unittest

import __main__


class PrhTests(unittest.TestCase):
    def create_local_ref(self, name):
        path_prefix = __main__.get_repo_git_dir() + "/refs/heads/"
        self.create_dirs_and_file(name, path_prefix)

    def create_remote_ref(self, name):
        path_prefix = __main__.get_repo_git_dir() + "/refs/remotes/origin/"
        self.create_dirs_and_file(name, path_prefix)

    def create_dirs_and_file(self, name, path_prefix):
        last_slash_index = name.rfind('/')
        if last_slash_index != -1:
            try:
                os.makedirs(path_prefix + name[0: last_slash_index])
                open(path_prefix + name, "w").close()
            except():
                print("error creating local ref")
        else:
            open(path_prefix + name, "w").close()

    def delete_local_ref(self, name):
        path_prefix = __main__.get_repo_git_dir() + "/refs/heads/"
        last_slash_index = name.rfind('/')
        if last_slash_index != -1:
            try:
                os.remove(path_prefix + name)
                os.removedirs(path_prefix + name[0: last_slash_index])
            except OSError as e:
                print(e.message)
        else:
            try:
                os.remove(path_prefix + name)
            except OSError as e:
                print(e.message)



    def put_ref_in_head(self, ref_name):
        with open(__main__.get_repo_git_dir() + "/HEAD", 'w') as f:
            f.write("ref: refs/heads/%s" % ref_name)

    def delete_remote_ref(self, name):
        origin_ = __main__.get_repo_git_dir() + "/refs/remotes/origin/"
        splited_name = name.split('/')
        if len(splited_name) > 1:
            path = origin_ + name
            if os.path.exists(path):
                os.removedirs(path)
        else:
            path = origin_ + name
            if os.path.exists(path):
                os.remove(path)

    def test_config_file_migration(self):
        old_config_path = "test1.py"
        with open(old_config_path, "w") as f:
            f.write('test1_param1 = "test1 Value1 "')
        self.assertTrue(os.path.isfile(old_config_path), "old config doesn't exist")
        new_config_path = "test1.json"
        __main__.migrate_config_file(from_path=old_config_path, to_path=new_config_path)
        self.assertFalse(os.path.isfile(old_config_path), "old config didn't get removed after migration")
        self.assertTrue(os.path.isfile(new_config_path), "new config doesn't exists after migration")
        config_file = __main__.read_from_config_file(file_path=new_config_path)
        self.assertEqual(config_file["test1_param1"], 'test1 Value1', "the values didn't carry over to new config")

    def test_pr_template_append(self):
        pass

    def test_multiple_link_in_commit_message(self):
        cm, full_url, story_ids = __main__.parse_commit_message(
            "this ishttps://www.pivotaltracker.com/story/show/140176051 https://www.pivotaltracker.com/story/show/139604723a test",
            [], [])
        self.assertEqual(cm, "this is a test")
        self.assertEqual(full_url, ["https://www.pivotaltracker.com/story/show/140176051",
                                    "https://www.pivotaltracker.com/story/show/139604723"])
        self.assertEqual(story_ids, ["140176051", "139604723"])

    def test_verify_parent_in_origin(self):
        ref_name = "prh_test_t1"
        self.delete_remote_ref(ref_name)
        self.create_remote_ref(ref_name)
        error = __main__.verify_parent_in_origin(ref_name)
        self.assertFalse(error, "failed with ref_name = %s" % ref_name)

        ref_name = "prh_test/t1"
        self.delete_remote_ref(ref_name)
        self.create_remote_ref(ref_name)
        error = __main__.verify_parent_in_origin(ref_name)
        self.assertFalse(error, "failed with ref_name = %s" % ref_name)

    def test_get_head(self):
        ref_name = "t1"
        self.delete_local_ref(ref_name)
        self.create_local_ref(ref_name)
        self.put_ref_in_head(ref_name)
        res = __main__.get_head()
        self.assertEqual(ref_name, res, "failed with a simple ref name")

        ref_name = "prh_test/t1"
        self.delete_local_ref(ref_name)
        self.create_local_ref(ref_name)
        self.put_ref_in_head(ref_name)
        res = __main__.get_head()
        self.assertEqual(ref_name, res, "failed when there is '/' in ref name")
