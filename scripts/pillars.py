"""The four pillars: one conference each, with its official data source.

Single source of truth for the fetch pipeline and (via build_data.py) the UI.
"""
from __future__ import annotations

PILLARS = [
    {
        "key": "CVPR",
        "label": "CVPR",
        "year": 2026,
        "full_name": "IEEE/CVF Conference on Computer Vision and Pattern Recognition",
        "full_name_zh": "IEEE/CVF 计算机视觉与模式识别会议",
        "field": "视觉",
        "source": "CVF Open Access",
        "source_url": "https://openaccess.thecvf.com/CVPR2026",
        "accent": "clay",
    },
    {
        "key": "AAAI",
        "label": "AAAI",
        "year": 2026,
        "full_name": "Proceedings of the AAAI Conference on Artificial Intelligence",
        "full_name_zh": "AAAI 人工智能会议",
        "field": "通用 AI",
        "source": "OpenAlex (Proceedings of AAAI, S4210191458)",
        "source_url": "https://api.openalex.org/sources/S4210191458",
        "accent": "indigo",
    },
    {
        "key": "ICCV",
        "label": "ICCV",
        "year": 2025,
        "full_name": "IEEE/CVF International Conference on Computer Vision",
        "full_name_zh": "IEEE/CVF 国际计算机视觉会议",
        "field": "视觉",
        "source": "CVF Open Access",
        "source_url": "https://openaccess.thecvf.com/ICCV2025",
        "accent": "teal",
    },
    {
        "key": "ACL",
        "label": "ACL",
        "year": 2026,
        "full_name": "Annual Meeting of the Association for Computational Linguistics",
        "full_name_zh": "国际计算语言学协会年会",
        "field": "语言 / NLP",
        "source": "ACL Anthology",
        "source_url": "https://aclanthology.org/events/acl-2026/",
        "accent": "amber",
    },
]

BY_KEY = {p["key"]: p for p in PILLARS}
