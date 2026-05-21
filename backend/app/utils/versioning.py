import re
from dataclasses import dataclass
from pathlib import Path


SEMVER_PATTERN = re.compile(r"_v(?P<version>\d+\.\d+\.\d+)_(?P<timestamp>\d{14})$")


@dataclass(frozen=True)
class ParsedArtifactName:
    stem: str
    version: str
    version_tuple: tuple[int, int, int]
    timestamp: str


def parse_semver(version: str) -> tuple[int, int, int]:
    major, minor, patch = version.split(".")
    return int(major), int(minor), int(patch)


def bump_patch(version: str) -> str:
    major, minor, patch = parse_semver(version)
    return f"{major}.{minor}.{patch + 1}"


def parse_artifact_name(file_name: str) -> ParsedArtifactName | None:
    stem = Path(file_name).stem
    match = SEMVER_PATTERN.search(stem)
    if not match:
        return None
    version = match.group("version")
    return ParsedArtifactName(
        stem=stem,
        version=version,
        version_tuple=parse_semver(version),
        timestamp=match.group("timestamp"),
    )


def compare_artifacts(left: ParsedArtifactName, right: ParsedArtifactName) -> int:
    if left.version_tuple != right.version_tuple:
        return -1 if left.version_tuple < right.version_tuple else 1
    if left.timestamp != right.timestamp:
        return -1 if left.timestamp < right.timestamp else 1
    return 0


def get_next_version_from_names(file_names: list[str], default_version: str = "1.0.0") -> str:
    parsed_items = [item for name in file_names if (item := parse_artifact_name(name))]
    if not parsed_items:
        return default_version
    latest = sorted(parsed_items, key=lambda item: (item.version_tuple, item.timestamp))[-1]
    return bump_patch(latest.version)
