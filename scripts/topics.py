"""Topic taxonomy for the theme view.

Topics are *derived* by this project (rule match over the official title/abstract,
hand-checked during curation) -- they are NOT publisher classifications. The UI says so.
Order matters: earlier topics win the "primary" slot, so put narrow ones first.
"""
from __future__ import annotations

import re

TOPICS = [
    {
        "id": "edge-efficiency",
        "label": "边缘计算与高效推理",
        "label_en": "Edge Computing & Efficient Inference",
        "accent": "teal",
        "patterns": [
            r"\bedge (?:device|deployment|computing|inference|intelligence)\b",
            r"\bon-?device\b", r"\bmobile-?\w*\b", r"\breal-?time\b",
            r"\bquantiz", r"\bpruning\b", r"\bknowledge distillation\b",
            r"\bsparsity\b", r"\bmodel compression\b", r"\bFLOPs?\b",
            r"\bparameter-?efficient\b", r"\bfederated\b", r"\blatency\b",
            r"\baccelerat", r"\bNPU\b", r"\blow-?power\b",
            r"\befficient (?:LLM|transformer|inference|generation|fine-?tuning|vision|sampling)\b",
            r"\bKV cache\b", r"\bspeculative decoding\b", r"\bearly-?exit\b",
            r"\bcompact\b", r"\blightweight\b",
        ],
    },
    {
        "id": "llm",
        "label": "大模型",
        "label_en": "Large Language Models",
        "accent": "clay",
        "patterns": [
            r"\bLLMs?\b", r"\blarge language model", r"\bfoundation model",
            r"\bGPT-[\d.]+\b", r"\bLlama\b", r"\bQwen\b", r"\bMistral\b",
            r"\bpre-?training\b", r"\binstruction (?:tuning|following)\b",
            r"\bRLHF\b", r"\balignment\b", r"\bchain-of-thought\b",
            r"\bfine-?tuning\b", r"\bLoRA\b", r"\bprompt",
            r"\breasoning\b", r"\bagent(?:ic)?\b", r"\bhallucinat",
            r"\bcontext (?:window|length)\b", r"\bRAG\b",
            r"\bretrieval-?augmented\b",
        ],
    },
    {
        "id": "multimodal",
        "label": "多模态",
        "label_en": "Multimodal Learning",
        "accent": "violet",
        "patterns": [
            r"\bmulti-?modal\b", r"\bcross-?modal\b", r"\bvision-?language\b",
            r"\bVLMs?\b", r"\bMLLM\b", r"\bCLIP\b", r"\bimage-?text\b",
            r"\bvideo-?language\b", r"\baudio-?visual\b", r"\btext-?to-?(?:image|video)\b",
            r"\bvisual question\b", r"\bany-?modality\b",
        ],
    },
    {
        "id": "generative",
        "label": "生成模型与内容创作",
        "label_en": "Generative Models",
        "accent": "rose",
        "patterns": [
            r"\bdiffusion\b", r"\bGANs?\b", r"\bgenerative\b",
            r"\btext-?to-?(?:image|video|3d|speech|audio)\b",
            r"\bimage (?:synthesis|generation|editing)\b",
            r"\bvideo (?:generation|synthesis|editing)\b",
            r"\bworld model\b", r"\blatent (?:space|diffusion)\b", r"\bflow matching\b",
            r"\bautoregressive\b", r"\bstyle transfer\b", r"\binpainting\b",
        ],
    },
    {
        "id": "3d-embodied",
        "label": "三维视觉与具身智能",
        "label_en": "3D Vision & Embodied AI",
        "accent": "indigo",
        "patterns": [
            r"\b3D\b", r"\bpoint cloud", r"\bmesh\b", r"\bNeRF\b",
            r"\bGaussian splatting\b", r"\bSLAM\b", r"\bnovel view synthesis\b",
            r"\bembodied\b", r"\brobot\w*\b", r"\bmanipulation\b",
            r"\bnavigation\b", r"\bautonomous driving\b", r"\bdrone\b",
            r"\bscene (?:reconstruction|understanding|generation)\b", r"\bdepth\b",
        ],
    },
    {
        "id": "medical-science",
        "label": "医学影像与科学智能",
        "label_en": "Medical & Scientific AI",
        "accent": "green",
        "patterns": [
            r"\bmedical\b", r"\bclinical\b", r"\bradiolog", r"\btumor",
            r"\blesion\b", r"\bMRI\b", r"\bCT scan", r"\bpatholog",
            r"\belectronic health record", r"\bEHR\b", r"\bprotein\b", r"\bmolecul",
            r"\bdrug\b", r"\bgenomic", r"\bdiagnos", r"\bsurgical\b",
            r"\bweather (?:forecast|prediction)\b", r"\bclimate\b", r"\bbiolog",
        ],
    },
    {
        "id": "trustworthy",
        "label": "安全可信与评测",
        "label_en": "Trustworthiness, Safety & Evaluation",
        "accent": "amber",
        "patterns": [
            r"\badversarial\b", r"\brobust", r"\bbackdoor\b",
            r"\bjailbreak\b", r"\bprompt injection\b", r"\bwatermark", r"\bprivacy\b",
            r"\bfairness\b", r"\bbias\b", r"\btrustworth", r"\bexplainab",
            r"\binterpretab", r"\bout-of-distribution\b", r"\banomaly detection\b",
            r"\bbenchmark\b", r"\bdefense\b", r"\battack\b", r"\bmisinformation\b",
            r"\btoxicity\b", r"\bde-?tection of (?:generated|fake|ai-?generated)\b",
        ],
    },
    {
        "id": "language-nlp",
        "label": "语言理解与知识",
        "label_en": "Language Understanding & Knowledge",
        "accent": "cyan",
        "patterns": [
            r"\bNLP\b", r"\bmachine translation\b", r"\bsentiment\b",
            r"\bquestion answering\b", r"\binformation extraction\b",
            r"\bnamed entity\b", r"\bsummariz", r"\bknowledge graph\b",
            r"\bdiscourse\b", r"\bspeech (?:recognition|synthesis)\b", r"\bASR\b",
            r"\bmultilingual\b", r"\blanguage model\b", r"\bcode (?:generation|understanding|repair)\b",
            r"\btheorem proving\b", r"\bmathematical reasoning\b",
        ],
    },
    {
        "id": "perception",
        "label": "检测分割与感知",
        "label_en": "Detection, Segmentation & Perception",
        "accent": "orange",
        "patterns": [
            r"\bdetection\b", r"\bsegmentation\b", r"\btracking\b",
            r"\bpose estimation\b", r"\boptical flow\b",
            r"\bkeypoint\b", r"\baction recognition\b",
            r"\bface\b", r"\bre-?identification\b", r"\bsuper-resolution\b",
            r"\bimage restoration\b", r"\bdeblurring\b", r"\bdenoising\b",
            r"\bopen-?vocabulary\b", r"\bsalient object\b",
        ],
    },
    {
        "id": "rl-decision",
        "label": "强化学习与决策",
        "label_en": "Reinforcement Learning & Decision Making",
        "accent": "purple",
        "patterns": [
            r"\breinforcement learning\b", r"\bpolicy (?:optimization|gradient)\b",
            r"\bMARL\b", r"\bmulti-agent\b", r"\bexploration\b", r"\bbandit\b",
            r"\bdecision-?making\b", r"\bplanning\b", r"\bimitation learning\b",
            r"\bmarkov\b", r"\bQ-?learning\b",
        ],
    },
    {
        "id": "architectures",
        "label": "深度学习架构与方法",
        "label_en": "Deep Learning Architectures & Methods",
        "accent": "slate",
        "patterns": [
            r"\btransformer\b", r"\battention\b", r"\bCNNs?\b", r"\bconvolution",
            r"\bVision Transformer\b", r"\bViT\b", r"\bMamba\b", r"\bstate space model",
            r"\bgraph neural\b", r"\bGNNs?\b", r"\bself-?supervised\b", r"\bcontrastive\b",
            r"\bmasked (?:image|autoencoder)\b", r"\brepresentation learning\b",
            r"\btransfer learning\b", r"\bdomain adaptation\b", r"\bmeta-?learning\b",
            r"\bcontinual learning\b", r"\bneural architecture search\b",
            r"\bgeneraliz", r"\bdeep learning\b",
            r"\bgraph\b", r"\bembedd", r"\bclustering\b", r"\bgradient\b",
        ],
    },
]

BY_ID = {t["id"]: t for t in TOPICS}

# "深度学习" is the umbrella: every selected paper is a deep-learning paper.
# The UI surfaces it as a lens over the concrete topics, not a sibling tag.
UMBRELLA = {
    "id": "deep-learning",
    "label": "深度学习（总览）",
    "label_en": "Deep Learning (umbrella)",
    "accent": "clay",
    "note": "本看板所选论文均属深度学习方法体系；此视图是全量聚合，不与具体主题并列计数。",
}

_COMPILED = {t["id"]: [re.compile(p, re.I) for p in t["patterns"]] for t in TOPICS}


def match_topics(text: str, max_topics: int = 3) -> list[str]:
    """Rule pass over official title + abstract; returns topic ids, narrow first."""
    scored = []
    for topic in TOPICS:
        score = sum(len(pat.findall(text)) for pat in _COMPILED[topic["id"]])
        if score:
            scored.append((score, len(topic["id"]), topic["id"]))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [s[2] for s in scored[:max_topics]]
