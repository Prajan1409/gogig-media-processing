from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    BackgroundTasks
)

from fastapi.middleware.cors import CORSMiddleware

from pathlib import Path
from datetime import datetime, timezone
import uuid

from database import (
    images_collection,
    client
)

from processor import analyze_image


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="GoGig Intelligent Media Processing API",
    description=(
        "Backend API for asynchronous image analysis "
        "and media quality processing"
    ),
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "https://gogig-media-processing-frontend.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# UPLOAD DIRECTORY
# =========================================================

UPLOAD_DIR = Path("uploads")

UPLOAD_DIR.mkdir(
    exist_ok=True
)


# =========================================================
# UTC TIME HELPER
# =========================================================

def current_time():
    """
    Returns timezone-aware UTC datetime.
    """

    return datetime.now(
        timezone.utc
    )


# =========================================================
# BACKGROUND IMAGE PROCESSING
# =========================================================

def process_image_background(
    processing_id: str,
    file_path: str
):

    try:

        # -------------------------------------------------
        # Mark processing
        # -------------------------------------------------

        images_collection.update_one(
            {
                "processing_id": processing_id
            },
            {
                "$set": {
                    "status": "processing",
                    "updated_at": current_time()
                }
            }
        )

        # -------------------------------------------------
        # Analyze image
        # -------------------------------------------------

        analysis_result = analyze_image(
            file_path
        )

        # -------------------------------------------------
        # Save analysis
        # -------------------------------------------------

        images_collection.update_one(
            {
                "processing_id": processing_id
            },
            {
                "$set": {
                    "status": "completed",
                    "analysis": analysis_result,
                    "failure_reason": None,
                    "updated_at": current_time()
                }
            }
        )

    except Exception as e:

        # -------------------------------------------------
        # Save failure
        # -------------------------------------------------

        images_collection.update_one(
            {
                "processing_id": processing_id
            },
            {
                "$set": {
                    "status": "failed",
                    "failure_reason": str(e),
                    "updated_at": current_time()
                }
            }
        )


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "message": "GoGig Media Processing API is running",
        "version": "1.0.0"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


# =========================================================
# UPLOAD IMAGE
# =========================================================

@app.post("/images")
async def upload_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):

    # -----------------------------------------------------
    # Validate file type
    # -----------------------------------------------------

    if (
        not file.content_type
        or not file.content_type.startswith("image/")
    ):

        raise HTTPException(
            status_code=400,
            detail="Only image files are allowed"
        )

    # -----------------------------------------------------
    # Generate processing ID
    # -----------------------------------------------------

    processing_id = str(
        uuid.uuid4()
    )

    # -----------------------------------------------------
    # Get extension
    # -----------------------------------------------------

    file_extension = (
        Path(file.filename).suffix
        if file.filename
        else ".jpg"
    )

    # -----------------------------------------------------
    # Generate unique filename
    # -----------------------------------------------------

    saved_filename = (
        f"{processing_id}{file_extension}"
    )

    # -----------------------------------------------------
    # File path
    # -----------------------------------------------------

    file_path = (
        UPLOAD_DIR / saved_filename
    )

    # -----------------------------------------------------
    # Read uploaded file
    # -----------------------------------------------------

    file_content = await file.read()

    # -----------------------------------------------------
    # Validate empty file
    # -----------------------------------------------------

    if not file_content:

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    # -----------------------------------------------------
    # Save file
    # -----------------------------------------------------

    file_path.write_bytes(
        file_content
    )

    # -----------------------------------------------------
    # MongoDB document
    # -----------------------------------------------------

    image_document = {

        "processing_id": processing_id,

        "original_filename": (
            file.filename
        ),

        "file_path": str(
            file_path
        ),

        "file_size": len(
            file_content
        ),

        "content_type": file.content_type,

        "status": "pending",

        "failure_reason": None,

        "created_at": current_time(),

        "updated_at": current_time(),

        "analysis": None
    }

    # -----------------------------------------------------
    # Insert into MongoDB
    # -----------------------------------------------------

    images_collection.insert_one(
        image_document
    )

    # -----------------------------------------------------
    # Background processing
    # -----------------------------------------------------

    background_tasks.add_task(
        process_image_background,
        processing_id,
        str(file_path)
    )

    # -----------------------------------------------------
    # Immediate response
    # -----------------------------------------------------

    return {

        "processing_id": processing_id,

        "status": "pending",

        "filename": file.filename,

        "message": (
            "Image uploaded successfully "
            "and queued for processing"
        )
    }


# =========================================================
# GET PROCESSING STATUS
# =========================================================

@app.get(
    "/images/{processing_id}/status"
)
def get_image_status(
    processing_id: str
):

    document = images_collection.find_one(
        {
            "processing_id": processing_id
        },
        {
            "_id": 0,
            "processing_id": 1,
            "status": 1,
            "failure_reason": 1,
            "original_filename": 1
        }
    )

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Processing ID not found"
        )

    return {

        "processing_id": document.get(
            "processing_id"
        ),

        "status": document.get(
            "status"
        ),

        "filename": document.get(
            "original_filename"
        ),

        "failure_reason": document.get(
            "failure_reason"
        )
    }


# =========================================================
# GET PROCESSING RESULTS
# =========================================================

@app.get(
    "/images/{processing_id}/results"
)
def get_image_results(
    processing_id: str
):

    document = images_collection.find_one(
        {
            "processing_id": processing_id
        },
        {
            "_id": 0,
            "processing_id": 1,
            "status": 1,
            "original_filename": 1,
            "file_size": 1,
            "content_type": 1,
            "analysis": 1,
            "failure_reason": 1,
            "created_at": 1,
            "updated_at": 1
        }
    )

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Processing ID not found"
        )

    return document


# =========================================================
# DATABASE TEST
# =========================================================

@app.get("/db-test")
def database_test():

    try:

        client.admin.command(
            "ping"
        )

        return {
            "status": "success",
            "message": "MongoDB connection is working"
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }