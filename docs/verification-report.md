# 数据核验报告

- 核验时间：2026-09-18 21:56:09
- 核验方式：对每篇精选论文**绕过本地缓存**重新读取官方页面，把官方摘要与仓库内 `data/papers.json` 做规范化后逐字比对；同时请求论文页与 PDF 链接确认可达。
- 结果：48 篇中，摘要逐字一致 **48** 篇，论文页可达 **48** 篇，PDF 可达 **40** 篇，异常 **0** 篇。

| 会议 | 语料规模（官方全量） | 精选 | 摘要一致 | 论文页可达 | PDF 可达 |
|---|---|---|---|---|---|
| CVPR 2026 | 4,042 | 12 | 12/12 | 12/12 | 12/12 |
| AAAI 2026 | 4,976 | 12 | 12/12 | 12/12 | 4/12（8 篇不适用） |
| ICCV 2025 | 2,701 | 12 | 12/12 | 12/12 | 12/12 |
| ACL 2026 | 4,809 | 12 | 12/12 | 12/12 | 12/12 |

## 逐篇比对

| # | 论文 | 官方记录号 | 摘要逐字一致 | 官方摘要字符数 | 论文页 | PDF |
|---|---|---|---|---|---|---|
| 1 | Seele: A Unified Acceleration Framework for Real-Time Gaus | `CVPR2026-p1164` | ✅ | 1228 | ok | ok |
| 2 | Fine-Grained Post-Training Quantization for Large Vision L | `CVPR2026-p69` | ✅ | 1642 | ok | ok |
| 3 | Visual Document Understanding and Reasoning: A Multi-Agent | `CVPR2026-p613` | ✅ | 1415 | ok | ok |
| 4 | TaskIT: Memory-Efficient Fine-Tuning of Multi-LoRA LLMs vi | `CVPR2026-p2342` | ✅ | 1377 | ok | ok |
| 5 | MAD: Modality-Adaptive Decoding for Mitigating Cross-Modal | `CVPR2026-p356` | ✅ | 1214 | ok | ok |
| 6 | HiCoGen: Hierarchical Compositional Text-to-Image Generati | `CVPR2026-p376` | ✅ | 1681 | ok | ok |
| 7 | DiffuView: Multi-View Diffusion Pretraining for 3D Aware R | `CVPR2026-p1054` | ✅ | 1422 | ok | ok |
| 8 | PGR-Net: Prior-Guided ROI Reasoning Network for Brain Tumo | `CVPR2026-p757` | ✅ | 1598 | ok | ok |
| 9 | Decoupling Defense Strategies for Robust Image Watermarkin | `CVPR2026-p2509` | ✅ | 1507 | ok | ok |
| 10 | Direct Segmentation without Logits Optimization for Traini | `CVPR2026-p224` | ✅ | 1420 | ok | ok |
| 11 | VideoChat-M1: Collaborative Policy Planning for Video Unde | `CVPR2026-p3875` | ✅ | 1531 | ok | ok |
| 12 | Global-Graph Guided and Local-Graph Weighted Contrastive L | `CVPR2026-p2534` | ✅ | 1486 | ok | ok |
| 13 | DIAA: A Decoding-Efficient Inference Acceleration Approach | `aaai-2026-w1632` | ✅ | 1523 | ok | skip |
| 14 | Efficient Multimodal Large Language Model via Dynamic KV C | `aaai-2026-w3487` | ✅ | 1364 | ok | skip |
| 15 | SPAN: Benchmarking and Improving Cross-Calendar Temporal R | `aaai-2026-w4812` | ✅ | 2028 | ok | ok |
| 16 | Mitigating Hallucinations in Large Language Models via Cau | `aaai-2026-w1223` | ✅ | 1413 | ok | skip |
| 17 | LiR3AG: A Lightweight Rerank Reasoning Strategy Framework  | `aaai-2026-w996` | ✅ | 1478 | ok | skip |
| 18 | Extracting Multimodal Learngene in CLIP: Unveiling the Mul | `aaai-2026-w3928` | ✅ | 1703 | ok | ok |
| 19 | HiTVideo: Hierarchical Tokenizers for Enhancing Text-to-Vi | `aaai-2026-w489` | ✅ | 1686 | ok | skip |
| 20 | H-RDT: Human Manipulation Enhanced Bimanual Robotic Manipu | `aaai-2026-w662` | ✅ | 1928 | ok | skip |
| 21 | PulseMind: A Multi-Modal Medical Model for Real-World Clin | `aaai-2026-w787` | ✅ | 1554 | ok | ok |
| 22 | Injection, Attack and Erasure: Revocable Backdoor Attacks  | `aaai-2026-w1569` | ✅ | 1465 | ok | ok |
| 23 | HCPO: Hierarchical Conductor-Based Policy Optimization in  | `aaai-2026-w627` | ✅ | 1241 | ok | skip |
| 24 | Dual Mamba for Node-Specific Representation Learning: Tack | `aaai-2026-w1169` | ✅ | 1376 | ok | skip |
| 25 | MobileIE: An Extremely Lightweight and Effective ConvNet f | `ICCV2025-p959` | ✅ | 1053 | ok | ok |
| 26 | METEOR: Multi-Encoder Collaborative Token Pruning for Effi | `ICCV2025-p217` | ✅ | 1572 | ok | ok |
| 27 | Corvid: Improving Multimodal Large Language Models Towards | `ICCV2025-p175` | ✅ | 1418 | ok | ok |
| 28 | Enhancing Spatial Reasoning in Multimodal Large Language M | `ICCV2025-p1834` | ✅ | 1266 | ok | ok |
| 29 | Prompt-A-Video: Prompt Your Video Diffusion Model via Pref | `ICCV2025-p275` | ✅ | 1412 | ok | ok |
| 30 | Dense2MoE: Restructuring Diffusion Transformer to MoE for  | `ICCV2025-p604` | ✅ | 1384 | ok | ok |
| 31 | SEGS-SLAM: Structure-enhanced 3D Gaussian Splatting SLAM w | `ICCV2025-p2522` | ✅ | 1294 | ok | ok |
| 32 | EmbodiedOcc: Embodied 3D Occupancy Prediction for Vision-b | `ICCV2025-p578` | ✅ | 1596 | ok | ok |
| 33 | PathFinder: A Multi-Modal Multi-Agent System for Medical D | `ICCV2025-p132` | ✅ | 1898 | ok | ok |
| 34 | TrustMark: Robust Watermarking and Watermark Removal for A | `ICCV2025-p1515` | ✅ | 673 | ok | ok |
| 35 | Feature Purification Matters: Suppressing Outlier Propagat | `ICCV2025-p102` | ✅ | 1558 | ok | ok |
| 36 | EA-Vit: Efficient Adaptation for Elastic Vision Transforme | `ICCV2025-p422` | ✅ | 1387 | ok | ok |
| 37 | VecInfer: Efficient LLM Inference with Low-Bit KV Cache vi | `acl-2026.acl-long.1454` | ✅ | 1337 | ok | ok |
| 38 | MobileLLM-Flash: Latency-Guided On-Device LLM Design for I | `acl-2026.acl-industry.51` | ✅ | 1534 | ok | ok |
| 39 | The Reasoning Trap: How Enhancing LLM Reasoning Amplifies  | `acl-2026.acl-long.376` | ✅ | 1946 | ok | ok |
| 40 | Why LLM Safety Guardrails Collapse After Fine-tuning: A Si | `acl-2026.acl-long.756` | ✅ | 1340 | ok | ok |
| 41 | SEMA-RAG: A Self-Evolving Multi-Agent Retrieval-Augmented  | `acl-2026.findings-acl.917` | ✅ | 1263 | ok | ok |
| 42 | “I See What You Did There”: Can Large Vision-Language Mode | `acl-2026.acl-long.444` | ✅ | 1028 | ok | ok |
| 43 | LADR: Locality-Aware Dynamic Rescue for Efficient Text-to- | `acl-2026.acl-long.1251` | ✅ | 1283 | ok | ok |
| 44 | Biomedical Question Answering via Multi-Level Summarizatio | `acl-2026.acl-long.743` | ✅ | 1039 | ok | ok |
| 45 | From Nodes to Narratives: Explaining Graph Neural Networks | `acl-2026.acl-long.1944` | ✅ | 1314 | ok | ok |
| 46 | An Exploration of Mamba for Speech Self-Supervised Models | `acl-2026.acl-long.470` | ✅ | 1053 | ok | ok |
| 47 | DPWriter: Reinforcement Learning with Diverse Planning Bra | `acl-2026.acl-long.647` | ✅ | 959 | ok | ok |
| 48 | SceneLM: 3D-Aware Language Models for Editable 3D Scene Sy | `acl-2026.findings-acl.2116` | ✅ | 1668 | ok | ok |

## 说明

- 「摘要一致」判定：双方文本做小写化并剔除除字母数字外的全部字符后比较，以规避连字符断行、MathJax 标签等排版差异带来的假阴性。
- 摘要比对使用抓取脚本的规范 UA；链接可达性检查改用普通浏览器 UA，因为 ojs.aaai.org 对非浏览器 UA 一律返回 403（读者点击链接时看到的是同一页面）。
- 中文摘要为人工翻译，不参与自动比对；抽查方式是在详情页展开英文原文对照。
- AAAI 走 OpenAlex（其摘要源自官方 proceedings），CVF 与 ACL 直接读会议官方开放获取站点。
