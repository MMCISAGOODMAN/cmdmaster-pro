import json
import os
import tempfile
import unittest
from unittest.mock import patch

from cmdmaster.cache import clear_cache, get_cached, set_cached
from cmdmaster.config import _load_config_from_file, get_config_dir, load_ai_config
from cmdmaster.engines import local_ai_engine, local_engine
from cmdmaster.explain import explain_command
from cmdmaster.favorites import add_favorite, list_favorites, remove_favorite
from cmdmaster.history import export_history, get_smart_suggestions, import_history, search_history
from cmdmaster.output import format_json_result
from cmdmaster.safety import classify_command, parse_ai_safety_label
from cmdmaster.templates import match_user_template, remove_user_template, save_user_template
from cmdmaster.utils import extract_shell_commands, get_platform, platform_command, primary_command


class TestSafety(unittest.TestCase):
    def test_dangerous_rm_rf_root(self):
        self.assertEqual(classify_command("rm -rf /"), "dangerous")

    def test_cautious_rm_rf(self):
        self.assertEqual(classify_command("rm -rf ./build"), "cautious")

    def test_safe_ls(self):
        self.assertEqual(classify_command("ls -la"), "safe")

    def test_parse_ai_label(self):
        text = "git status\ngit log --oneline\nsafe"
        label, body = parse_ai_safety_label(text)
        self.assertEqual(label, "safe")
        self.assertIn("git status", body)


class TestExplain(unittest.TestCase):
    def test_git_status(self):
        self.assertIn("status", explain_command("git status").lower())

    def test_rm_rf(self):
        self.assertIn("delete", explain_command("rm -rf /tmp").lower())


class TestCache(unittest.TestCase):
    def test_set_and_get(self):
        with patch("cmdmaster.cache.CACHE_FILE", tempfile.mktemp(suffix=".json")):
            set_cached("test query", "ls -la", "local")
            entry = get_cached("test query")
            self.assertIsNotNone(entry)
            self.assertEqual(entry["result"], "ls -la")
            clear_cache()


class TestTemplates(unittest.TestCase):
    def test_save_and_match(self):
        with patch("cmdmaster.templates.TEMPLATES_FILE", tempfile.mktemp(suffix=".json")):
            self.assertTrue(save_user_template("deploy", "kubectl rollout restart app"))
            self.assertEqual(match_user_template("deploy"), "kubectl rollout restart app")
            self.assertTrue(remove_user_template("deploy"))


class TestUtils(unittest.TestCase):
    def test_extract_shell_commands(self):
        text = "git status\n# comment\ndangerous\nls -la"
        cmds = extract_shell_commands(text)
        self.assertEqual(cmds, ["git status", "ls -la"])

    def test_primary_command(self):
        text = "Run this:\ngit pull origin main\nsafe"
        self.assertEqual(primary_command(text), "git pull origin main")

    def test_platform_command_cpu(self):
        cmd = platform_command("cpu")
        self.assertTrue("top" in cmd or "CPU" in cmd)

    def test_get_platform(self):
        self.assertIn(get_platform(), ("macos", "linux", "other"))

    def test_json_output(self):
        payload = format_json_result("check disk", "df -h", "local", "safe")
        data = json.loads(payload)
        self.assertEqual(data["command"], "df -h")
        self.assertEqual(data["source"], "local")


class TestLocalEngine(unittest.TestCase):
    def test_english_cpu(self):
        result = local_engine("check CPU usage")
        self.assertIn("top", result.lower())

    def test_chinese_cpu(self):
        result = local_engine("查看CPU使用率")
        self.assertIn("top", result.lower())

    def test_chinese_disk(self):
        result = local_engine("查看磁盘空间")
        self.assertIn("df", result)

    def test_chinese_port(self):
        result = local_engine("查看端口占用")
        self.assertTrue("lsof" in result or "ss" in result)

    def test_blocks_dangerous(self):
        result = local_engine("rm -rf /")
        self.assertIn("blocked", result)

    def test_docker_logs_compound(self):
        result = local_engine("docker container logs")
        self.assertIn("docker logs", result)

    def test_docker_ps(self):
        result = local_engine("docker ps status")
        self.assertIn("docker ps", result)

    def test_large_files(self):
        result = local_engine("find large files")
        self.assertIn("find", result)


class TestLocalAIEngine(unittest.TestCase):
    def test_git_commit_english(self):
        result = local_ai_engine("commit code")
        self.assertIn("git commit", result)

    def test_git_commit_chinese(self):
        result = local_ai_engine("commit提交代码")
        self.assertIn("git commit", result)

    def test_git_push_chinese(self):
        result = local_ai_engine("push代码到远程")
        self.assertIn("git push", result)


class TestConfig(unittest.TestCase):
    def test_env_vars_override(self):
        with patch.dict(os.environ, {
            "CMDMASTER_AI_URL": "https://test.example.com",
            "CMDMASTER_AI_TOKEN": "test-token",
            "CMDMASTER_AI_MODEL": "test-model",
        }):
            url, token, model = load_ai_config()
            self.assertEqual(url, "https://test.example.com")
            self.assertEqual(token, "test-token")
            self.assertEqual(model, "test-model")

    def test_load_config_from_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('AI_URL = "https://file.example.com"\n')
            f.write('AI_TOKEN = "file-token"\n')
            f.write('AI_MODEL = "file-model"\n')
            path = f.name
        try:
            config = _load_config_from_file(path)
            self.assertEqual(config["AI_URL"], "https://file.example.com")
            self.assertEqual(config["AI_TOKEN"], "file-token")
        finally:
            os.unlink(path)

    def test_config_dir(self):
        self.assertIn("cmdmaster-pro", get_config_dir())


class TestHistory(unittest.TestCase):
    def test_suggestions_include_chinese(self):
        suggestions = get_smart_suggestions("cpu")
        self.assertTrue(any("CPU" in s or "cpu" in s.lower() for s in suggestions))

    def test_search_history_empty_query(self):
        results = search_history("")
        self.assertIsInstance(results, list)

    def test_export_import(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name
        with patch("cmdmaster.history.HIST_FILE", tempfile.mktemp()):
            from cmdmaster.history import save_history
            save_history("export test query")
            self.assertTrue(export_history(path))
            self.assertTrue(import_history(path))
        os.unlink(path)


class TestFavorites(unittest.TestCase):
    def test_add_and_remove_favorite(self):
        with patch("cmdmaster.favorites.FAV_FILE", tempfile.mktemp()):
            self.assertTrue(add_favorite("test favorite query"))
            self.assertIn("test favorite query", list_favorites())
            self.assertTrue(remove_favorite("test favorite query"))
            self.assertNotIn("test favorite query", list_favorites())


if __name__ == "__main__":
    unittest.main()
