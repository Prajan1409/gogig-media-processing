from PIL import Image
import cv2
import numpy as np
import pytesseract
import hashlib
from pathlib import Path
from datetime import datetime, timezone


# =========================================================
# TESSERACT CONFIGURATION
# =========================================================

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# =========================================================
# 1. IMAGE DIMENSION VALIDATION
# =========================================================

def validate_dimensions(image):
    """
    Checks image width, height and aspect ratio.
    """

    width, height = image.size

    if height == 0:
        aspect_ratio = None
    else:
        aspect_ratio = round(
            width / height,
            2
        )

    # Minimum acceptable dimensions
    minimum_width = 300
    minimum_height = 200

    if (
        width < minimum_width
        or height < minimum_height
    ):
        status = "too_small"

        message = (
            "Image dimensions are too small "
            "for reliable analysis"
        )

    else:
        status = "valid"

        message = (
            "Image dimensions are suitable "
            "for analysis"
        )

    return {

        "status": status,

        "width": width,

        "height": height,

        "aspect_ratio": aspect_ratio,

        "minimum_width": minimum_width,

        "minimum_height": minimum_height,

        "message": message
    }


# =========================================================
# 2. BLUR DETECTION
# =========================================================

def calculate_blur_score(image):
    """
    Uses Laplacian variance to measure image sharpness.

    Higher score = sharper image
    Lower score = blurrier image
    """

    img = np.array(image)

    if len(img.shape) == 3:

        gray = cv2.cvtColor(
            img,
            cv2.COLOR_RGB2GRAY
        )

    else:

        gray = img

    blur_score = cv2.Laplacian(
        gray,
        cv2.CV_64F
    ).var()

    return round(
        float(blur_score),
        2
    )


def analyze_blur(image):

    blur_score = calculate_blur_score(
        image
    )

    if blur_score < 100:

        status = "blurry"

    elif blur_score < 500:

        status = "moderate"

    else:

        status = "sharp"

    return {

        "score": blur_score,

        "status": status,

        "message": (

            "Image appears blurry"

            if status == "blurry"

            else

            "Image has moderate sharpness"

            if status == "moderate"

            else

            "Image appears sharp"
        )
    }


# =========================================================
# 3. BRIGHTNESS ANALYSIS
# =========================================================

def calculate_brightness(image):
    """
    Calculates average grayscale brightness.
    """

    img = np.array(image)

    if len(img.shape) == 3:

        gray = cv2.cvtColor(
            img,
            cv2.COLOR_RGB2GRAY
        )

    else:

        gray = img

    brightness = np.mean(
        gray
    )

    return round(
        float(brightness),
        2
    )


def analyze_brightness(image):

    brightness = calculate_brightness(
        image
    )

    if brightness < 60:

        status = "dark"

    elif brightness > 200:

        status = "bright"

    else:

        status = "normal"

    return {

        "score": brightness,

        "status": status,

        "message": (

            "Image is too dark"

            if status == "dark"

            else

            "Image is too bright"

            if status == "bright"

            else

            "Image brightness is normal"
        )
    }


# =========================================================
# 4. DUPLICATE DETECTION
# =========================================================

def calculate_image_hash(path):
    """
    Creates a SHA-256 hash of the image file.

    The same file will produce the same hash.
    """

    sha256 = hashlib.sha256()

    with open(
        path,
        "rb"
    ) as file:

        while True:

            data = file.read(
                8192
            )

            if not data:
                break

            sha256.update(
                data
            )

    return sha256.hexdigest()


def detect_duplicate(path):
    """
    Checks the uploads folder for another file
    with the same SHA-256 hash.
    """

    current_path = Path(
        path
    )

    if not current_path.exists():

        return {

            "is_duplicate": False,

            "duplicate_file": None,

            "message": "File does not exist"
        }

    current_hash = calculate_image_hash(
        current_path
    )

    uploads_directory = (
        current_path.parent
    )

    duplicate_file = None

    try:

        for file in uploads_directory.iterdir():

            if not file.is_file():
                continue

            # Don't compare the file with itself
            if (
                file.resolve()
                == current_path.resolve()
            ):
                continue

            try:

                file_hash = calculate_image_hash(
                    file
                )

                if file_hash == current_hash:

                    duplicate_file = (
                        file.name
                    )

                    break

            except Exception:

                continue

    except Exception:

        return {

            "is_duplicate": False,

            "duplicate_file": None,

            "message": (
                "Duplicate check could not "
                "be completed"
            )
        }

    if duplicate_file:

        return {

            "is_duplicate": True,

            "duplicate_file": duplicate_file,

            "message": (
                "Duplicate image detected"
            )
        }

    return {

        "is_duplicate": False,

        "duplicate_file": None,

        "message": (
            "No duplicate image detected"
        )
    }


# =========================================================
# 5. OCR EXTRACTION
# =========================================================

def extract_text(image):
    """
    Extracts visible text from the image
    using Tesseract OCR.
    """

    img = np.array(
        image
    )

    if len(img.shape) == 3:

        gray = cv2.cvtColor(
            img,
            cv2.COLOR_RGB2GRAY
        )

    else:

        gray = img

    # -----------------------------------------------------
    # Upscale for better OCR
    # -----------------------------------------------------

    height, width = gray.shape

    if width < 1200:

        scale = 1200 / width

        gray = cv2.resize(
            gray,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_CUBIC
        )

    # -----------------------------------------------------
    # Improve contrast
    # -----------------------------------------------------

    processed = cv2.GaussianBlur(
        gray,
        (3, 3),
        0
    )

    processed = cv2.threshold(
        processed,
        0,
        255,
        cv2.THRESH_BINARY
        + cv2.THRESH_OTSU
    )[1]

    try:

        text = pytesseract.image_to_string(
            processed,
            config="--psm 11"
        )

    except Exception as e:

        return {

            "detected": False,

            "text": "",

            "character_count": 0,

            "message": (
                f"OCR failed: {str(e)}"
            )
        }

    text = text.strip()

    # -----------------------------------------------------
    # Clean excessive blank lines
    # -----------------------------------------------------

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if line:

            lines.append(
                line
            )

    cleaned_text = "\n".join(
        lines
    )

    return {

        "detected": bool(
            cleaned_text
        ),

        "text": cleaned_text,

        "character_count": len(
            cleaned_text
        ),

        "message": (

            "Text successfully extracted"

            if cleaned_text

            else

            "No readable text detected"
        )
    }


# =========================================================
# 6. PHOTO-OF-PHOTO / SCREENSHOT HEURISTIC
# =========================================================

def detect_photo_of_photo(image):
    """
    Heuristic detection for images that may be:

    - photographs of screens
    - photographs of another photograph
    - screenshots or screen-like images

    This is NOT a definitive classifier.
    """

    img = np.array(
        image
    )

    if len(img.shape) == 3:

        gray = cv2.cvtColor(
            img,
            cv2.COLOR_RGB2GRAY
        )

    else:

        gray = img

    height, width = gray.shape

    # =====================================================
    # EDGE DETECTION
    # =====================================================

    edges = cv2.Canny(
        gray,
        50,
        150
    )

    edge_density = np.mean(
        edges > 0
    )

    # =====================================================
    # LARGE RECTANGLE DETECTION
    # =====================================================

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    large_rectangles = 0

    image_area = width * height

    for contour in contours:

        area = cv2.contourArea(
            contour
        )

        if area < image_area * 0.20:

            continue

        x, y, w, h = cv2.boundingRect(
            contour
        )

        if w == 0 or h == 0:

            continue

        ratio = w / float(h)

        if 1.2 <= ratio <= 2.2:

            large_rectangles += 1

    # =====================================================
    # SCREEN-LIKE ASPECT RATIO
    # =====================================================

    image_ratio = (
        width / height
        if height
        else 0
    )

    screen_like_ratio = (

        abs(
            image_ratio - (16 / 9)
        ) < 0.08

        or

        abs(
            image_ratio - (4 / 3)
        ) < 0.08
    )

    # =====================================================
    # SCORE
    # =====================================================

    score = 0

    if edge_density > 0.12:

        score += 1

    if large_rectangles >= 1:

        score += 1

    if screen_like_ratio:

        score += 1

    if score >= 2:

        status = (
            "possible_photo_of_photo"
        )

    else:

        status = (
            "likely_original"
        )

    return {

        "status": status,

        "confidence_score": score,

        "edge_density": round(
            float(edge_density),
            4
        ),

        "large_rectangles_detected": (
            large_rectangles
        ),

        "note": (
            "Heuristic result; this does not "
            "definitively prove a photo-of-photo."
        )
    }


# =========================================================
# 7. OVERALL QUALITY + ISSUE REPORT
# =========================================================

def generate_quality_summary(
    dimensions,
    blur,
    brightness,
    duplicate,
    photo_of_photo
):
    """
    Aggregates the results of all image checks
    into a structured issue report.

    The individual checks perform the analysis.

    This function identifies, classifies and reports
    the issues found across those checks.
    """

    issues = []

    issue_details = []

    # =====================================================
    # DIMENSION ISSUE
    # =====================================================

    if dimensions["status"] == "too_small":

        issue = (
            "Image dimensions are too small"
        )

        issues.append(
            issue
        )

        issue_details.append({

            "type": "dimensions",

            "severity": "error",

            "message": issue
        })

    # =====================================================
    # BLUR ISSUE
    # =====================================================

    if blur["status"] == "blurry":

        issue = (
            "Image is blurry"
        )

        issues.append(
            issue
        )

        issue_details.append({

            "type": "blur",

            "severity": "warning",

            "message": issue
        })

    # =====================================================
    # MODERATE SHARPNESS
    # =====================================================

    elif blur["status"] == "moderate":

        issue = (
            "Image has moderate sharpness"
        )

        issues.append(
            issue
        )

        issue_details.append({

            "type": "blur",

            "severity": "info",

            "message": issue
        })

    # =====================================================
    # DARK IMAGE
    # =====================================================

    if brightness["status"] == "dark":

        issue = (
            "Image is too dark"
        )

        issues.append(
            issue
        )

        issue_details.append({

            "type": "brightness",

            "severity": "warning",

            "message": issue
        })

    # =====================================================
    # BRIGHT IMAGE
    # =====================================================

    elif brightness["status"] == "bright":

        issue = (
            "Image is too bright"
        )

        issues.append(
            issue
        )

        issue_details.append({

            "type": "brightness",

            "severity": "warning",

            "message": issue
        })

    # =====================================================
    # DUPLICATE IMAGE
    # =====================================================

    if duplicate["is_duplicate"]:

        issue = (
            "Duplicate image detected"
        )

        issues.append(
            issue
        )

        duplicate_file = duplicate.get(
            "duplicate_file"
        )

        issue_details.append({

            "type": "duplicate",

            "severity": "warning",

            "message": issue,

            "duplicate_file": duplicate_file
        })

    # =====================================================
    # PHOTO-OF-PHOTO / SCREENSHOT
    # =====================================================

    if (
        photo_of_photo["status"]
        == "possible_photo_of_photo"
    ):

        issue = (
            "Possible photo-of-photo "
            "or screen image"
        )

        issues.append(
            issue
        )

        issue_details.append({

            "type": "photo_of_photo",

            "severity": "warning",

            "message": issue,

            "confidence_score": (
                photo_of_photo.get(
                    "confidence_score"
                )
            )
        })

    # =====================================================
    # FINAL STATUS
    # =====================================================

    issue_count = len(
        issues
    )

    if issue_count == 0:

        overall_status = "good"

        recommendation = (
            "No major issues detected"
        )

        message = (
            "Image passed the main "
            "quality checks"
        )

    elif issue_count == 1:

        overall_status = "acceptable"

        recommendation = (
            "Manual review recommended"
        )

        message = (
            "1 issue detected; "
            "manual review recommended"
        )

    else:

        overall_status = "needs_review"

        recommendation = (
            "Manual review recommended"
        )

        message = (
            f"{issue_count} issues detected; "
            "manual review recommended"
        )

    # =====================================================
    # STRUCTURED RESULT
    # =====================================================

    return {

        "status": overall_status,

        "issue_count": issue_count,

        # Simple issue list retained for
        # frontend compatibility
        "issues": issues,

        # Detailed structured issue information
        "issue_details": issue_details,

        "recommendation": recommendation,

        "message": message
    }


# =========================================================
# 8. MAIN IMAGE ANALYSIS FUNCTION
# =========================================================

def analyze_image(path):

    # =====================================================
    # OPEN IMAGE
    # =====================================================

    image = Image.open(
        path
    )

    image.load()

    # =====================================================
    # IMAGE INFORMATION
    # =====================================================

    width, height = image.size

    image_format = image.format

    if image_format:

        image_format = (
            image_format.upper()
        )

    else:

        image_format = (
            Path(path)
            .suffix
            .replace(
                ".",
                ""
            )
            .upper()
        )

    # =====================================================
    # CHECK 1 - DIMENSIONS
    # =====================================================

    dimensions_result = (
        validate_dimensions(
            image
        )
    )

    # =====================================================
    # CHECK 2 - BLUR
    # =====================================================

    blur_result = (
        analyze_blur(
            image
        )
    )

    # =====================================================
    # CHECK 3 - BRIGHTNESS
    # =====================================================

    brightness_result = (
        analyze_brightness(
            image
        )
    )

    # =====================================================
    # CHECK 4 - DUPLICATE
    # =====================================================

    duplicate_result = (
        detect_duplicate(
            path
        )
    )

    # =====================================================
    # CHECK 5 - OCR
    # =====================================================

    ocr_result = (
        extract_text(
            image
        )
    )

    # =====================================================
    # CHECK 6 - PHOTO-OF-PHOTO
    # =====================================================

    photo_of_photo_result = (
        detect_photo_of_photo(
            image
        )
    )

    # =====================================================
    # OVERALL SUMMARY + ISSUE REPORT
    # =====================================================

    quality_summary = (
        generate_quality_summary(
            dimensions_result,
            blur_result,
            brightness_result,
            duplicate_result,
            photo_of_photo_result
        )
    )

    # =====================================================
    # FINAL STRUCTURED RESULT
    # =====================================================

    return {

        "image": {

            "width": width,

            "height": height,

            "format": image_format,

            "aspect_ratio": (
                dimensions_result[
                    "aspect_ratio"
                ]
            )
        },

        "dimension_validation": (
            dimensions_result
        ),

        "blur_analysis": (
            blur_result
        ),

        "brightness_analysis": (
            brightness_result
        ),

        "duplicate_detection": (
            duplicate_result
        ),

        "ocr": (
            ocr_result
        ),

        "photo_of_photo": (
            photo_of_photo_result
        ),

        "overall": (
            quality_summary
        ),

        "processed_at": (
    datetime.now(timezone.utc).isoformat()
)
    }


# =========================================================
# OPTIONAL DIRECT TEST
# =========================================================

if __name__ == "__main__":

    test_path = (
        "uploads/"
        "d2b9e64a-c2bf-44cc-ba8c-a6a345c31a33.png"
    )

    if Path(test_path).exists():

        result = analyze_image(
            test_path
        )

        print("\n")
        print("=" * 60)
        print("GOGIG IMAGE ANALYSIS")
        print("=" * 60)

        print("\nIMAGE:")
        print(
            result["image"]
        )

        print("\nDIMENSION VALIDATION:")
        print(
            result["dimension_validation"]
        )

        print("\nBLUR ANALYSIS:")
        print(
            result["blur_analysis"]
        )

        print("\nBRIGHTNESS ANALYSIS:")
        print(
            result["brightness_analysis"]
        )

        print("\nDUPLICATE DETECTION:")
        print(
            result["duplicate_detection"]
        )

        print("\nOCR:")
        print(
            result["ocr"]
        )

        print("\nPHOTO-OF-PHOTO:")
        print(
            result["photo_of_photo"]
        )

        print("\nOVERALL ISSUE REPORT:")
        print(
            result["overall"]
        )

        print("\n")
        print("=" * 60)

    else:

        print(
            f"Test image not found: {test_path}"
        )