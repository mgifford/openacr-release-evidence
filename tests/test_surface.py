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


    def test_drupal_user_path_is_authoring_login(self):
        result = classify_surface({
            "title": "Editor issue",
            "description_text": "Visit /user and sign in, then edit the page.",
            "comments": [],
        })
        self.assertEqual("authoring", result["surface"])
        self.assertEqual("user-path", result["basis"])

    def test_drupal_user_login_path_is_authoring(self):
        result = classify_surface({
            "title": "Editor issue",
            "description_text": "Open /user/login and authenticate.",
            "comments": [],
        })
        self.assertEqual("authoring", result["surface"])
        self.assertEqual("user-path", result["basis"])

    def test_user_profile_path_is_authoring(self):
        result = classify_surface({
            "title": "Profile heading",
            "description_text": "The account page at /user/1 has a heading issue.",
            "comments": [],
        })
        self.assertEqual("authoring", result["surface"])
        self.assertEqual("user-path", result["basis"])

    def test_user_registration_path_is_authoring(self):
        result = classify_surface({
            "title": "Registration copy",
            "description_text": "The /user/register page needs clearer instructions.",
            "comments": [],
        })
        self.assertEqual("authoring", result["surface"])
        self.assertEqual("user-path", result["basis"])

    def test_admin_theme_without_admin_or_login_is_web(self):
        result = classify_surface({
            "title": "Admin theme styling",
            "description_text": "The theme name appears in the issue title.",
            "comments": [],
        })
        self.assertEqual("web", result["surface"])


if __name__ == "__main__":
    unittest.main()
