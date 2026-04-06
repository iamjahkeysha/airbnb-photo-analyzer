from PIL import Image, ImageStat, ImageFilter
import numpy as np


def analyze_photo(image_path: str) -> dict:
    img_rgb = Image.open(image_path).convert("RGB")
    img_gray = img_rgb.convert("L")

    return {
        "brightness": _brightness(img_gray),
        "contrast": _contrast(img_gray),
        "sharpness": _sharpness(img_gray),
        "warmth": _warmth(img_rgb),
        "color_clutter": _color_clutter(img_rgb),
        "thirds_score": _rule_of_thirds(img_gray),
        "thumbnail": _thumbnail_scores(img_rgb),
    }


def _brightness(img_gray: Image.Image) -> dict:
    score = ImageStat.Stat(img_gray).mean[0]
    return {"score": round(score, 2), "rating": _rate(score, low=80, high=130)}


def _contrast(img_gray: Image.Image) -> dict:
    score = ImageStat.Stat(img_gray).stddev[0]
    return {"score": round(score, 2), "rating": _rate(score, low=40, high=70)}


def _sharpness(img_gray: Image.Image) -> dict:
    edges = img_gray.filter(ImageFilter.FIND_EDGES)
    score = ImageStat.Stat(edges).mean[0]
    return {"score": round(score, 2), "rating": _rate(score, low=5, high=15)}


def _warmth(img_rgb: Image.Image) -> dict:
    r, g, b = ImageStat.Stat(img_rgb).mean
    score = round(r - b, 2)
    if score > 20:
        rating = "warm"
    elif score < -20:
        rating = "cool"
    else:
        rating = "neutral"
    return {"score": score, "rating": rating}


def _color_clutter(img_rgb: Image.Image) -> dict:
    small = img_rgb.resize((100, 100))
    colors = small.getcolors(maxcolors=10000)
    num_unique = len(colors) if colors else 10000
    if num_unique < 1500:
        rating = "clean"
    elif num_unique < 3000:
        rating = "moderate"
    else:
        rating = "cluttered"
    return {"unique_colors": num_unique, "rating": rating}


def _rule_of_thirds(img_gray: Image.Image) -> dict:
    arr = np.array(img_gray)
    h, w = arr.shape
    th, tw = h // 3, w // 3

    zones = {}
    for row in range(3):
        for col in range(3):
            zone = arr[row * th:(row + 1) * th, col * tw:(col + 1) * tw]
            zones[(row, col)] = zone.mean()

    intersections = [(1, 1), (1, 2), (2, 1), (2, 2)]
    intersection_brightness = sum(zones[k] for k in intersections)
    edge_brightness = sum(v for k, v in zones.items() if k not in intersections)

    score = round(intersection_brightness / edge_brightness, 3) if edge_brightness else 1.0
    rating = "good" if score >= 1.0 else "poor"
    return {"score": score, "rating": rating}


def _thumbnail_scores(img_rgb: Image.Image) -> dict:
    thumb = img_rgb.resize((400, 300), Image.LANCZOS)
    thumb_gray = thumb.convert("L")
    return {
        "brightness": _brightness(thumb_gray),
        "contrast": _contrast(thumb_gray),
        "sharpness": _sharpness(thumb_gray),
    }


def _rate(value: float, low: float, high: float) -> str:
    if value < low:
        return "low"
    if value > high:
        return "high"
    return "good"
