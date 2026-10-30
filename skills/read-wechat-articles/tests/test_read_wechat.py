import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "read_wechat.py"
SPEC = importlib.util.spec_from_file_location("read_wechat", SCRIPT_PATH)
read_wechat = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(read_wechat)


class ReadWeChatTests(unittest.TestCase):
    def test_parse_html_extracts_metadata_and_body(self):
        document = """
        <html><head>
          <meta property="og:title" content="公众号文章 &amp; 标题">
          <meta name="author" content="公众号作者">
        </head><body>
          <div id="js_content"><h1>正文标题</h1><p>正文第一段。</p></div>
        </body></html>
        """
        source = "https://mp.weixin.qq.com/s/example"

        with tempfile.TemporaryDirectory() as directory:
            result = read_wechat.parse_html(document, source, Path(directory))

            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["title"], "公众号文章 & 标题")
            self.assertEqual(result["author"], "公众号作者")
            markdown = Path(result["markdown_path"]).read_text(encoding="utf-8")
            self.assertIn("正文第一段。", markdown)
            self.assertIn(source, markdown)

    def test_parse_html_blocks_verification_page(self):
        result = read_wechat.parse_html(
            "<html>环境异常，请完成验证</html>",
            "https://mp.weixin.qq.com/s/example",
            Path("unused"),
        )

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["reason"], "wechat_verification")

    def test_parse_html_blocks_missing_article_body(self):
        result = read_wechat.parse_html(
            "<html><body><p>普通页面</p></body></html>",
            "https://mp.weixin.qq.com/s/example",
            Path("unused"),
        )

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["reason"], "article_body_missing")

    def test_proxy_fetch_writes_markdown_without_network(self):
        article_url = "https://mp.weixin.qq.com/s/example"
        markdown = "# 示例标题\n\n" + ("公开文章正文。\n" * 40)

        class FakeResponse:
            headers = {"X-Markdown-Method": "mock"}

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                return False

            def read(self):
                return markdown.encode("utf-8")

        with tempfile.TemporaryDirectory() as directory:
            with patch(
                "read_wechat.urllib.request.urlopen",
                return_value=FakeResponse(),
            ) as mocked_urlopen:
                result, error = read_wechat.proxy_fetch(
                    article_url,
                    Path(directory),
                )

            self.assertEqual(error, "")
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["method"], "website2markdown:mock")
            request = mocked_urlopen.call_args.args[0]
            self.assertIn(article_url, request.full_url)
            self.assertIn("公开文章正文。", Path(result["markdown_path"]).read_text(encoding="utf-8"))

    def test_cli_from_file_writes_markdown(self):
        document = """
        <html><head><meta property="og:title" content="离线文章"></head>
        <body><div id="js_content"><p>离线正文。</p></div></body></html>
        """

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "article.html"
            output = root / "output"
            source.write_text(document, encoding="utf-8")
            captured = io.StringIO()

            with patch.object(
                sys,
                "argv",
                ["read_wechat.py", str(source), "--from-file", "--output", str(output)],
            ), contextlib.redirect_stdout(captured):
                return_code = read_wechat.main()

            result = json.loads(captured.getvalue())
            self.assertEqual(return_code, 0)
            self.assertEqual(result["status"], "ok")
            self.assertTrue(Path(result["markdown_path"]).is_file())
            self.assertIn("离线正文。", Path(result["markdown_path"]).read_text(encoding="utf-8"))

    def test_cli_rejects_non_wechat_url_before_fetching(self):
        captured = io.StringIO()

        with patch.object(sys, "argv", ["read_wechat.py", "https://example.com/article"]), contextlib.redirect_stdout(captured):
            return_code = read_wechat.main()

        result = json.loads(captured.getvalue())
        self.assertEqual(return_code, 2)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["reason"], "not_a_public_wechat_article_url")


if __name__ == "__main__":
    unittest.main()
