
# tools/gen_docs.py
import argparse
import hashlib
import json
import fnmatch
from pathlib import Path
from datetime import datetime

# 项目根目录和源代码目录、文档目录
ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "backend" / "mcpshop"
DOC_DIR = ROOT_DIR / "doc"
# 本地归档使用版本化文件，GitHub 上传使用固定文件名
default_file = DOC_DIR / "docs.md"
CACHE_FILE = DOC_DIR / "cache.json"
IGNORE_FILE = ROOT_DIR / ".gendocsignore"


def calc_hash(text: str) -> str:
    """计算文本的 SHA256 哈希"""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_cache() -> dict:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return {}


def save_cache(cache: dict):
    DOC_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2), encoding="utf-8")


def load_ignore_patterns() -> list[str]:
    """从 .gendocsignore 文件读取忽略模式，去除注释和空行"""
    patterns = []
    if IGNORE_FILE.exists():
        for line in IGNORE_FILE.read_text(encoding="utf-8").splitlines():
            raw = line.strip()
            if not raw or raw.startswith('#'):
                continue
            patterns.append(raw.rstrip('/'))
    return patterns


def should_ignore(path: Path, patterns: list[str]) -> bool:
    """判断路径是否匹配忽略模式或 __pycache__"""
    rel = str(path.relative_to(ROOT_DIR))
    # 忽略 __pycache__ 目录
    if "__pycache__" in path.parts:
        return True
    for pat in patterns:
        # 目录匹配：完全相等或前缀
        if rel == pat or rel.startswith(pat + '/'):
            return True
        # 通配符匹配相对路径或名称
        if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(path.name, pat):
            return True
    return False


def collect_files(path: Path, exts: list[str], ignore_patterns: list[str]):
    for p in sorted(path.rglob("*")):
        if not p.is_file() or p.suffix not in exts:
            continue
        if should_ignore(p, ignore_patterns):
            continue
        rel = str(p.relative_to(ROOT_DIR))
        code = p.read_text(encoding="utf-8")
        stat = p.stat()
        meta = {
            "lines": code.count("\n") + 1,
            "size_kb": round(stat.st_size / 1024, 2),
            "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        }
        yield rel, code, meta


def build_md_tree(path: Path, exts: list[str], ignore_patterns: list[str], indent: int = 0) -> list[str]:
    lines = []
    prefix = "  " * indent + f"- {path.name}"
    lines.append(prefix)
    if path.is_dir():
        for child in sorted(path.iterdir()):
            # 目录或后缀匹配
            if not (child.is_dir() or child.suffix in exts):
                continue
            if should_ignore(child, ignore_patterns):
                continue
            lines.extend(build_md_tree(child, exts, ignore_patterns, indent + 1))
    return lines


def generate_toc(files: list[str]) -> str:
    toc = ["## 目录\n"]
    for rel in files:
        anchor = rel.lower().replace("/", "-").replace(".", "")
        toc.append(f"- [{rel}](#{anchor})")
    return "\n".join(toc) + "\n\n"


def write_doc(file_path: Path, title: str, tree_lines: list[str], toc: str, sections: list[tuple]):
    DOC_DIR.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as f:
        f.write(title + "\n\n")
        f.write("## 项目结构\n\n")
        f.write("\n".join(tree_lines) + "\n\n")
        f.write(toc)
        for _, content in sections:
            f.write(content)


def generate_docs(version: str, exts: list[str], ignore_patterns: list[str]):
    # 本地版本化文件
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    versioned_file = DOC_DIR / f"docs_{version}_{timestamp}.md"

    cache = load_cache()
    new_cache = {}
    sections = []
    for rel, code, meta in collect_files(SRC_DIR, exts, ignore_patterns):
        h = calc_hash(code)
        updated = (rel not in cache) or (cache[rel] != h)
        new_cache[rel] = h
        header = f"### `{rel}`\n"
        if updated:
            header += f"> **⚡ 已更新** 生成于 `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n\n"
        header += (
            f"- 行数：{meta['lines']} 行  \n"
            f"- 大小：{meta['size_kb']} KB  \n"
            f"- 最后修改：{meta['mtime']}  \n\n"
        )
        lang = rel.split('.')[-1]
        code_block = f"```{lang}\n{code}\n```\n\n"
        sections.append((rel, header + code_block))

    tree_lines = build_md_tree(SRC_DIR.parent, exts, ignore_patterns)
    all_files = [rel for rel, _, _ in collect_files(SRC_DIR, exts, ignore_patterns)]
    toc = generate_toc(all_files)
    title = f"# 项目代码快照（版本 {version}，{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}）"

    # 写入本地存档
    write_doc(versioned_file, title, tree_lines, toc, sections)
    # 写入固定文件覆盖 GitHub 使用
    write_doc(default_file, title, tree_lines, toc, sections)

    save_cache(new_cache)
    print(f"✅ 本地存档：{versioned_file}\n✅ GitHub 上传：{default_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成项目代码快照文档")
    parser.add_argument("-v", "--version", required=True,
                        help="文档版本号，例如 v1.0.0")
    parser.add_argument(
        "-e", "--exts",
        nargs='+',
        default=[".py"],
        help="要包含的文件后缀列表，例如 .py .md .txt"
    )
    parser.add_argument(
        "-i", "--ignore",
        action='store_true',
        help="启用 .gendocsignore 过滤模式"
    )
    parser.add_argument(
        "-x", "--exclude",
        nargs='+',
        default=[],
        help="额外的忽略模式，无需写入 .gendocsignore，支持通配符"
    )
    args = parser.parse_args()
    exts = args.exts
    ignore_patterns = []
    if args.ignore:
        ignore_patterns += load_ignore_patterns()
    if args.exclude:
        ignore_patterns += args.exclude
    generate_docs(args.version, exts, ignore_patterns)
