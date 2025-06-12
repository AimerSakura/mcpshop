# mcpshop/core/embedding.py

import subprocess
import json
from chromadb.utils import embedding_functions

class LocalQwenEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __init__(self, model_dir: str):
        # model_dir 指向 backend/gme-Qwen2-VL-7B-Instruct 的根目录
        self.model_dir = model_dir

    def embed(self, texts: list[str]) -> list[list[float]]:
        """
        调用本地模型脚本进行推理，假设你在 model_dir 下有一个 inference.py
        接受 JSON 输入并返回 JSON 输出。
        """
        payload = json.dumps({"texts": texts})
        # 以子进程方式调用，或换成你实际的推理接口
        proc = subprocess.Popen(
            ["python", f"{self.model_dir}/inference.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        out, err = proc.communicate(payload)
        if proc.returncode != 0:
            raise RuntimeError(f"嵌入模型调用失败：{err}")
        result = json.loads(out)
        return result["embeddings"]

# 在你的 AIClient 初始化中：
from mcpshop.core.embedding import LocalQwenEmbeddingFunction
from mcpshop.core.config import settings

self.embedding_fn = LocalQwenEmbeddingFunction(
    model_dir=settings.BASE_DIR / "backend" / "gme-Qwen2-VL-7B-Instruct"
)
