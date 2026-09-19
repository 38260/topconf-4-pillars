# 数据核验报告

- 核验时间：2026-09-19 12:38:22
- 核验方式：对每篇精选论文**绕过本地缓存**重新读取官方页面，把官方摘要与仓库内 `data/papers.json` 做规范化后逐字比对；同时请求论文页与 PDF 链接确认可达。
- 结果：132 篇中，摘要逐字一致 **132** 篇，论文页可达 **132** 篇，PDF 可达 **122** 篇，异常 **0** 篇。

| 届次 | 官方语料规模 | 精选 | 摘要一致 | 论文页可达 | PDF 可达 |
|---|---|---|---|---|---|
| CVPR 2026 | 4,042 | 12 | 12/12 | 12/12 | 12/12 |
| CVPR 2025 | 2,871 | 12 | 12/12 | 12/12 | 12/12 |
| CVPR 2024 | 2,716 | 12 | 12/12 | 12/12 | 12/12 |
| AAAI 2026 | 4,976 | 12 | 12/12 | 12/12 | 4/12（8 篇不适用） |
| AAAI 2025 | 3,486 | 12 | 12/12 | 12/12 | 10/12（2 篇不适用） |
| AAAI 2024 | 2,867 | 12 | 12/12 | 12/12 | 12/12 |
| ICCV 2025 | 2,701 | 12 | 12/12 | 12/12 | 12/12 |
| ICCV 2023 | 2,156 | 12 | 12/12 | 12/12 | 12/12 |
| ACL 2026 | 4,809 | 12 | 12/12 | 12/12 | 12/12 |
| ACL 2025 | 3,351 | 12 | 12/12 | 12/12 | 12/12 |
| ACL 2024 | 1,952 | 12 | 12/12 | 12/12 | 12/12 |

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
| 49 | MoPE-CLIP: Structured Pruning for Efficient Vision-Languag | `CVPR2024-p2411` | ✅ | 1285 | ok | ok |
| 50 | HMD-Poser: On-Device Real-time Human Motion Tracking from  | `CVPR2024-p567` | ✅ | 1309 | ok | ok |
| 51 | PromptCoT: Align Prompt Distribution via Adapted Chain-of- | `CVPR2024-p976` | ✅ | 2135 | ok | ok |
| 52 | Alpha-CLIP: A CLIP Model Focusing on Wherever You Want | `CVPR2024-p322` | ✅ | 1088 | ok | ok |
| 53 | AV2AV: Direct Audio-Visual Speech to Audio-Visual Speech T | `CVPR2024-p1629` | ✅ | 1675 | ok | ok |
| 54 | UFOGen: You Forward Once Large Scale Text-to-Image Generat | `CVPR2024-p2548` | ✅ | 1068 | ok | ok |
| 55 | SuGaR: Surface-Aligned Gaussian Splatting for Efficient 3D | `CVPR2024-p2222` | ✅ | 1341 | ok | ok |
| 56 | Training Like a Medical Resident: Context-Prior Learning T | `CVPR2024-p2343` | ✅ | 1601 | ok | ok |
| 57 | WateRF: Robust Watermarks in Radiance Fields for Protectio | `CVPR2024-p218` | ✅ | 1204 | ok | ok |
| 58 | FoundationPose: Unified 6D Pose Estimation and Tracking of | `CVPR2024-p235` | ✅ | 1074 | ok | ok |
| 59 | ViT-CoMer: Vision Transformer with Convolutional Multi-sca | `CVPR2024-p975` | ✅ | 1605 | ok | ok |
| 60 | DMR: Decomposed Multi-Modality Representations for Frames  | `CVPR2024-p77` | ✅ | 1137 | ok | ok |
| 61 | MobilePortrait: Real-Time One-Shot Neural Head Avatars on  | `CVPR2025-p2826` | ✅ | 962 | ok | ok |
| 62 | VL2Lite: Task-Specific Knowledge Distillation from Large V | `CVPR2025-p516` | ✅ | 1155 | ok | ok |
| 63 | Enhancing Video-LLM Reasoning via Agent-of-Thoughts Distil | `CVPR2025-p59` | ✅ | 964 | ok | ok |
| 64 | Critic-V: VLM Critics Help Catch VLM Errors in Multimodal  | `CVPR2025-p329` | ✅ | 1882 | ok | ok |
| 65 | Post-pre-training for Modality Alignment in Vision-Languag | `CVPR2025-p2046` | ✅ | 1610 | ok | ok |
| 66 | AlignMamba: Enhancing Multimodal Mamba with Local and Glob | `CVPR2025-p393` | ✅ | 1438 | ok | ok |
| 67 | Diffusion-4K: Ultra-High-Resolution Image Synthesis with L | `CVPR2025-p304` | ✅ | 1368 | ok | ok |
| 68 | Prometheus: 3D-Aware Latent Diffusion Models for Feed-Forw | `CVPR2025-p209` | ✅ | 875 | ok | ok |
| 69 | SplatAD: Real-Time Lidar and Camera Rendering with 3D Gaus | `CVPR2025-p743` | ✅ | 1401 | ok | ok |
| 70 | Multi-modal Medical Diagnosis via Large-small Model Collab | `CVPR2025-p2790` | ✅ | 1362 | ok | ok |
| 71 | T2ISafety: Benchmark for Assessing Fairness, Toxicity, and | `CVPR2025-p357` | ✅ | 1333 | ok | ok |
| 72 | SGC-Net: Stratified Granular Comparison Network for Open-V | `CVPR2025-p39` | ✅ | 1448 | ok | ok |
| 73 | SwiftFormer: Efficient Additive Attention for Transformer- | `ICCV2023-p1288` | ✅ | 1373 | ok | ok |
| 74 | SYENet: A Simple Yet Effective Network for Multiple Low-Le | `ICCV2023-p1009` | ✅ | 1645 | ok | ok |
| 75 | PromptCap: Prompt-Guided Image Captioning for VQA with GPT | `ICCV2023-p76` | ✅ | 1499 | ok | ok |
| 76 | Audio-Visual Deception Detection: DOLOS Dataset and Parame | `ICCV2023-p93` | ✅ | 1527 | ok | ok |
| 77 | Tune-A-Video: One-Shot Tuning of Image Diffusion Models fo | `ICCV2023-p874` | ✅ | 1030 | ok | ok |
| 78 | Point-SLAM: Dense Neural Point Cloud-based SLAM | `ICCV2023-p605` | ✅ | 956 | ok | ok |
| 79 | Towards Unifying Medical Vision-and-Language Pre-Training  | `ICCV2023-p1118` | ✅ | 1909 | ok | ok |
| 80 | An Adaptive Model Ensemble Adversarial Attack for Boosting | `ICCV2023-p2005` | ✅ | 1610 | ok | ok |
| 81 | A Simple Framework for Open-Vocabulary Segmentation and De | `ICCV2023-p938` | ✅ | 1826 | ok | ok |
| 82 | FLatten Transformer: Vision Transformer using Focused Line | `ICCV2023-p308` | ✅ | 1271 | ok | ok |
| 83 | Context-Aware Planning and Environment-Aware Memory for In | `ICCV2023-p148` | ✅ | 1132 | ok | ok |
| 84 | Open-vocabulary Video Question Answering: A New Benchmark  | `ICCV2023-p704` | ✅ | 1620 | ok | ok |
| 85 | MobileInst: Video Instance Segmentation on the Mobile | `aaai-2024-w1690` | ✅ | 1387 | ok | ok |
| 86 | Agile-Quant: Activation-Guided Quantization for Faster Inf | `aaai-2024-w244` | ✅ | 1762 | ok | ok |
| 87 | Benchmarking Large Language Models in Retrieval-Augmented  | `aaai-2024-w3` | ✅ | 1435 | ok | ok |
| 88 | Visual Chain-of-Thought Prompting for Knowledge-Based Visu | `aaai-2024-w160` | ✅ | 1913 | ok | ok |
| 89 | Self-Supervised Multi-Modal Knowledge Graph Contrastive Ha | `aaai-2024-w393` | ✅ | 1738 | ok | ok |
| 90 | Accelerating Text-to-Image Editing via Cache-Enabled Spars | `aaai-2024-w891` | ✅ | 1783 | ok | ok |
| 91 | Depth-Guided Robust and Fast Point Cloud Fusion NeRF for S | `aaai-2024-w1470` | ✅ | 1273 | ok | ok |
| 92 | Large Language Models Are Clinical Reasoners: Reasoning-Aw | `aaai-2024-w162` | ✅ | 1196 | ok | ok |
| 93 | LimeAttack: Local Explainable Method for Textual Hard-Labe | `aaai-2024-w1281` | ✅ | 1475 | ok | ok |
| 94 | Aspect-Based Sentiment Analysis with Explicit Sentiment Au | `aaai-2024-w367` | ✅ | 1246 | ok | ok |
| 95 | FoX: Formation-Aware Exploration in Multi-Agent Reinforcem | `aaai-2024-w883` | ✅ | 1066 | ok | ok |
| 96 | Learning to Reweight for Generalizable Graph Neural Networ | `aaai-2024-w582` | ✅ | 1677 | ok | ok |
| 97 | QJL: 1-Bit Quantized JL Transform for KV Cache Quantizatio | `aaai-2025-w1187` | ✅ | 1393 | ok | ok |
| 98 | ABQ-LLM: Arbitrary-Bit Quantized Inference Acceleration fo | `aaai-2025-w312` | ✅ | 1875 | ok | ok |
| 99 | RMath: A Logic Reasoning-Focused Datasets Toward Mathemati | `aaai-2025-w2804` | ✅ | 2018 | ok | ok |
| 100 | LightPROF: A Lightweight Reasoning Framework for Large Lan | `aaai-2025-w117` | ✅ | 1711 | ok | ok |
| 101 | Harnessing Multimodal Large Language Models for Multimodal | `aaai-2025-w38` | ✅ | 1711 | ok | ok |
| 102 | DesignEdit: Unify Spatial-Aware Image Editing via Training | `aaai-2025-w813` | ✅ | 1276 | ok | skip |
| 103 | BloomScene: Lightweight Structured 3D Gaussian Splatting f | `aaai-2025-w3451` | ✅ | 1524 | ok | skip |
| 104 | ProtCLIP: Function-Informed Protein Multi-Modal Learning | `aaai-2025-w407` | ✅ | 1894 | ok | ok |
| 105 | Adversarial-Inspired Backdoor Defense via Bridging Backdoo | `aaai-2025-w469` | ✅ | 1420 | ok | ok |
| 106 | MEDSAGE: Enhancing Robustness of Medical Dialogue Summariz | `aaai-2025-w983` | ✅ | 1377 | ok | ok |
| 107 | LNS2+RL: Combining Multi-agent Reinforcement Learning with | `aaai-2025-w593` | ✅ | 1886 | ok | ok |
| 108 | Deep Multi-modal Graph Clustering via Graph Transformer Ne | `aaai-2025-w2426` | ✅ | 1030 | ok | ok |
| 109 | Unlocking Data-free Low-bit Quantization with Matrix Decom | `acl-2024.acl-long.133` | ✅ | 1358 | ok | ok |
| 110 | LoRAPrune: Structured Pruning Meets Low-Rank Parameter-Eff | `acl-2024.findings-acl.178` | ✅ | 1650 | ok | ok |
| 111 | Active Prompting with Chain-of-Thought for Large Language  | `acl-2024.acl-long.73` | ✅ | 1496 | ok | ok |
| 112 | Self-Alignment for Factuality: Mitigating Hallucinations i | `acl-2024.acl-long.107` | ✅ | 1125 | ok | ok |
| 113 | M-RAG: Reinforcing Large Language Model Performance throug | `acl-2024.acl-long.108` | ✅ | 976 | ok | ok |
| 114 | Advancement in Graph Understanding: A Multimodal Benchmark | `acl-2024.acl-long.404` | ✅ | 1095 | ok | ok |
| 115 | UNIMO-G: Unified Image Generation through Multimodal Condi | `acl-2024.acl-long.335` | ✅ | 1370 | ok | ok |
| 116 | RAM-EHR: Retrieval Augmentation Meets Clinical Predictions | `acl-2024.acl-short.68` | ✅ | 799 | ok | ok |
| 117 | A Comprehensive Study of Jailbreak Attack versus Defense f | `acl-2024.findings-acl.443` | ✅ | 1430 | ok | ok |
| 118 | CodeScope: An Execution-based Multilingual Multitask Multi | `acl-2024.acl-long.301` | ✅ | 1666 | ok | ok |
| 119 | Planning Like Human: A Dual-process Framework for Dialogue | `acl-2024.acl-long.262` | ✅ | 1293 | ok | ok |
| 120 | Towards Better Understanding of Contrastive Sentence Repre | `acl-2024.acl-long.780` | ✅ | 1371 | ok | ok |
| 121 | MobiLoRA: Accelerating LoRA-based LLM Inference on Mobile  | `acl-2025.acl-long.1140` | ✅ | 1257 | ok | ok |
| 122 | Quaff: Quantized Parameter-Efficient Fine-Tuning under Out | `acl-2025.acl-long.325` | ✅ | 1689 | ok | ok |
| 123 | Agentic Reasoning: A Streamlined Framework for Enhancing L | `acl-2025.acl-long.1383` | ✅ | 1096 | ok | ok |
| 124 | TRACT: Regression-Aware Fine-tuning Meets Chain-of-Thought | `acl-2025.acl-long.147` | ✅ | 1132 | ok | ok |
| 125 | Jailbreak Large Vision-Language Models Through Multi-Modal | `acl-2025.acl-long.74` | ✅ | 1230 | ok | ok |
| 126 | AlignMMBench: Evaluating Chinese Multimodal Alignment in L | `acl-2025.acl-long.327` | ✅ | 1352 | ok | ok |
| 127 | Segment-Level Diffusion: A Framework for Controllable Long | `acl-2025.acl-long.210` | ✅ | 1030 | ok | ok |
| 128 | DiaLLMs: EHR-Enhanced Clinical Conversational System for C | `acl-2025.findings-acl.1313` | ✅ | 1300 | ok | ok |
| 129 | Defense Against Prompt Injection Attack by Leveraging Atta | `acl-2025.acl-long.897` | ✅ | 1404 | ok | ok |
| 130 | Ontology-Guided Reverse Thinking Makes Large Language Mode | `acl-2025.acl-long.741` | ✅ | 1079 | ok | ok |
| 131 | Advancing Collaborative Debates with Role Differentiation  | `acl-2025.acl-long.1105` | ✅ | 1640 | ok | ok |
| 132 | GNN-RAG: Graph Neural Retrieval for Efficient Large Langua | `acl-2025.findings-acl.856` | ✅ | 1440 | ok | ok |

## 说明

- 「摘要一致」判定：双方文本做小写化并剔除除字母数字外的全部字符后比较，以规避连字符断行、MathJax 标签等排版差异带来的假阴性。
- 摘要比对使用抓取脚本的规范 UA；链接可达性检查改用普通浏览器 UA，因为 ojs.aaai.org 对非浏览器 UA 一律返回 403（读者点击链接时看到的是同一页面）。
- 中文摘要为人工翻译，不参与自动比对；抽查方式是在详情页展开英文原文对照。
- AAAI 走 OpenAlex（其摘要源自官方 proceedings），CVF 与 ACL 直接读会议官方开放获取站点。
