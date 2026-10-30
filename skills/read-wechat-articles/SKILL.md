---
name: read-wechat-articles
description: Read public WeChat Official Account articles from mp.weixin.qq.com, extract title, account, publication time, body text, links, and images, and prepare the content for summarization, verification, or critique. Use whenever the user supplies a WeChat article URL or asks to read, summarize, assess, quote-check, or archive a 微信公众号 article.
---

# Read WeChat Articles

Extract the article before analyzing it. Do not infer article content from the URL, title, or search snippets.

## Workflow

1. Run the bundled reader from a writable working directory:

   ```bash
   python <skill-dir>/scripts/read_wechat.py "<mp.weixin.qq.com URL>" --output ./wechat-output
   ```

2. Read the JSON status printed by the script.
3. If `status` is `ok`, open the Markdown file named in `markdown_path` and use it as the source for the user's requested analysis.
4. If `status` is `blocked`, report the exact blocker. Ask the user for screenshots, copied text, or a browser-saved HTML file only after both fetch methods fail.
5. If the user supplies saved HTML, run:

   ```bash
   python <skill-dir>/scripts/read_wechat.py article.html --from-file --output ./wechat-output
   ```

## Fetch Strategy

The script first sends only the public article URL to the open-source Website2Markdown endpoint at `md.genedai.me`. This moves the fetch beyond local network blocks and uses its WeChat adapter and server-side fallback pipeline. If that fails, the script tries local Camoufox and then a dependency-free mobile WeChat request.

Never send a WeChat login, Cookie, token, private-account credential, or article content supplied privately by the user to the proxy. Read only public article URLs. Treat verification pages, gateway-denial pages, deleted articles, and empty bodies as failures rather than valid articles.

## Source Handling

Preserve the original URL and distinguish the article's claims from external verification. When assessing reliability, verify consequential claims against authoritative sources rather than treating the article itself as independent evidence.
