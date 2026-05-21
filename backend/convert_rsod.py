#!/usr/bin/env python3
"""
Convert the RSOD dataset from Pascal VOC XML annotations to YOLO labels.
"""

from __future__ import annotations

import argparse
import random
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

from app.config import settings
from app.utils.file_utils import ensure_directories


CLASSES = ["aircraft", "oiltank", "overpass", "playground"]
CLASS_MAP = {class_name: index for index, class_name in enumerate(CLASSES)}


def create_yaml_config(output_dir: Path):
    yaml_content = "\n".join(
        [
            "# RSOD dataset configuration",
            f"path: {output_dir.as_posix()}",
            "",
            "train: images/train",
            "val: images/val",
            "",
            f"nc: {len(CLASSES)}",
            "names:",
            "  0: aircraft",
            "  1: oiltank",
            "  2: overpass",
            "  3: playground",
            "",
        ]
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "rsod.yaml").write_text(yaml_content, encoding="utf-8")


def convert_xml_to_yolo(xml_path: Path, image_width: int, image_height: int) -> str:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    lines: list[str] = []

    for obj in root.findall("object"):
        name_node = obj.find("name")
        bbox_node = obj.find("bndbox")
        if name_node is None or bbox_node is None:
            continue

        class_name = name_node.text.strip()
        if class_name not in CLASS_MAP:
            continue

        xmin = float(bbox_node.findtext("xmin", "0"))
        ymin = float(bbox_node.findtext("ymin", "0"))
        xmax = float(bbox_node.findtext("xmax", "0"))
        ymax = float(bbox_node.findtext("ymax", "0"))

        # Clamp boxes to the image boundary because some RSOD XML files
        # contain slightly out-of-range coordinates.
        xmin = max(0.0, min(xmin, float(image_width)))
        ymin = max(0.0, min(ymin, float(image_height)))
        xmax = max(0.0, min(xmax, float(image_width)))
        ymax = max(0.0, min(ymax, float(image_height)))

        if xmax <= xmin or ymax <= ymin:
            continue

        x_center = ((xmin + xmax) / 2.0) / image_width
        y_center = ((ymin + ymax) / 2.0) / image_height
        bbox_width = (xmax - xmin) / image_width
        bbox_height = (ymax - ymin) / image_height

        lines.append(
            f"{CLASS_MAP[class_name]} "
            f"{x_center:.6f} {y_center:.6f} {bbox_width:.6f} {bbox_height:.6f}"
        )

    return "\n".join(lines)


def _prepare_output_dirs(output_dir: Path):
    for path in (output_dir / "images", output_dir / "labels"):
        if path.exists():
            shutil.rmtree(path)

    for path in (
        output_dir / "images" / "train",
        output_dir / "images" / "val",
        output_dir / "labels" / "train",
        output_dir / "labels" / "val",
    ):
        path.mkdir(parents=True, exist_ok=True)


def convert_dataset(base_dir: Path, split_ratio: float = 0.8, seed: int = 42):
    rsod_dir = base_dir / "data" / "rsod"
    images_dir = rsod_dir / "images"
    annotations_dir = rsod_dir / "annotations"
    output_dir = rsod_dir / "yolo_dataset"

    ensure_directories()
    _prepare_output_dirs(output_dir)

    image_files = sorted(
        [path for path in images_dir.iterdir() if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}]
    )
    if not image_files:
        raise FileNotFoundError(f"No image files found in {images_dir}")

    random.seed(seed)
    random.shuffle(image_files)
    split_index = int(len(image_files) * split_ratio)
    train_files = image_files[:split_index]
    val_files = image_files[split_index:]

    for split_name, files in (("train", train_files), ("val", val_files)):
        for image_path in files:
            basename = image_path.stem
            target_image_path = output_dir / "images" / split_name / image_path.name
            shutil.copy2(image_path, target_image_path)

            xml_path = annotations_dir / f"{basename}.xml"
            label_path = output_dir / "labels" / split_name / f"{basename}.txt"
            if not xml_path.exists():
                label_path.write_text("", encoding="utf-8")
                continue

            with Image.open(image_path) as image:
                width, height = image.size
            label_content = convert_xml_to_yolo(xml_path, width, height)
            label_path.write_text(label_content, encoding="utf-8")

    create_yaml_config(output_dir)
    print(
        f"Conversion completed. train={len(train_files)} val={len(val_files)} "
        f"output={output_dir}"
    )


def build_parser():
    parser = argparse.ArgumentParser(description="Convert RSOD Pascal VOC annotations to YOLO format.")
    parser.add_argument("--base-dir", default=str(settings.BACKEND_DIR), help="Backend directory path.")
    parser.add_argument("--split-ratio", type=float, default=0.8, help="Training split ratio.")
    parser.add_argument("--seed", type=int, default=42, help="Shuffle seed.")
    return parser


def main():
    args = build_parser().parse_args()
    convert_dataset(Path(args.base_dir), split_ratio=args.split_ratio, seed=args.seed)


if __name__ == "__main__":
    main()
