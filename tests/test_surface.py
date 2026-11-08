import unittest

from acr_evidence.normalize import classify_surface


class SurfaceTests(unittest.TestCase):
    def test_admin_path_is_authoring(self):
        result = classify_surface({
            "title": "Toolbar issue",
            "description_text": "Go to /admin/config and open the toolbar.",
            "comments": [],
        })
        self.assertEqual("authoring", result["surface"])
        self.assertEqual("admin-path", result["basis"])

    def test_login_step_is_authoring(self):
        result = classify_surface({
            "title": "Editor control disappeared",
            "description_text": "Log in as an administrator, then edit an article.",
            "comments": [],
        })
        self.assertEqual("authoring", result["surface"])
        self.assertEqual("login-step", result["basis"])

    def test_comment_login_step_is_authoring(self):
        result = classify_surface({
            "title": "Follow-up",
            "description_text": "",
            "comments": [{"body_text": "I logged in as admin and reproduced it."}],
        })
        self.assertEqual("authoring", result["surface"])

    def test_front_end_default_is_web(self):
        result = classify_surface({
            "title": "Homepage heading",
            "description_text": "The published homepage has a duplicate heading.",
            "comments": [],
        })
        self.assertEqual("web", result["surface"])
        self.assertEqual("default-web", result["basis"])

    def test_admin_theme_without_admin_or_login_is_web(self):
        result = classify_surface({
            "title": "Admin theme styling",
            "description_text": "The theme name appears in the issue title.",
            "comments": [],
        })
        self.assertEqual("web", result["surface"])


if __name__ == "__main__":
    unittest.main()
