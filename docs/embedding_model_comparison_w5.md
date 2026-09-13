# M5 Official FAISS Index Comparison

All four embedding models were indexed using the same frozen M4 corpus containing 3,684 official chunks.

| Model | Dimension | Build Time (s) | Effective Content Limit | Over-limit Chunks | Reload |
|---|---:|---:|---:|---:|---|
| all-MiniLM-L6-v2 | 384 | 325.53 | 254 | 1446 | Passed |
| all-mpnet-base-v2 | 768 | 2451.13 | 382 | 1056 | Passed |
| e5-base-v2 | 768 | 2682.16 | 510 | 314 | Passed |
| bge-base-en-v1.5 | 768 | 2694.52 | 510 | 314 | Passed |

All indexes use FAISS Flat Inner Product with L2-normalised embeddings.

MiniLM was the fastest model, but it had the highest number of chunks exceeding the effective input limit. E5 and BGE had the lowest truncation risk, with only 314 over-limit chunks each.

Final model selection should not be based on build time or truncation alone. Retrieval quality metrics such as Hit@K, Recall@K and MRR should also be considered.