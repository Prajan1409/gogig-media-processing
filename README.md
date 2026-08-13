\# gOGig Media Processing



An intelligent media processing application for analyzing uploaded vehicle images and generating structured quality, content, and issue-analysis results.



The application provides an asynchronous image-processing workflow with a FastAPI backend, MongoDB persistence, and a React-based frontend.



\---



\## 📸 Application Screenshots



\### Upload Interface



The gOGig interface provides a clean and focused workflow for uploading media for analysis.



!\[gOGig Upload Interface](screenshots/upload.png)



\### Image Analysis Dashboard



After processing, the application presents structured image-analysis results including dimensions, blur, brightness, OCR, and other checks.



!\[gOGig Image Analysis](screenshots/analysis.png)



\### Issue Report



Detected issues are presented separately with severity, details, and recommended action.



!\[gOGig Issue Report](screenshots/issue-report.png)



\---



\## 1. Project Overview



gOGig Media Processing is designed to process uploaded images and identify common media-quality and content issues before the media is used further in a workflow.



The system analyzes an uploaded image across multiple dimensions, including:



\- Image dimensions and aspect ratio

\- Blur / sharpness

\- Brightness

\- Duplicate images

\- OCR text extraction

\- Photo-of-photo detection heuristics

\- Vehicle number-plate detection and OCR

\- Overall issue identification and reporting



The results are stored as structured analysis data and exposed through API endpoints for the frontend.



\---



\## 2. Key Features



\### Image Upload



Users can upload image files through the web interface.



The backend:



1\. Validates that the uploaded file is an image.

2\. Generates a unique processing ID.

3\. Stores the uploaded file.

4\. Creates a processing record in MongoDB.

5\. Starts background processing.

6\. Returns the processing ID to the client.



\### Image Quality Analysis



The system performs several quality checks:



\- Dimension validation

\- Aspect-ratio calculation

\- Blur / sharpness analysis

\- Brightness analysis



\### Duplicate Detection



The application checks whether the uploaded image is a duplicate of an existing image and reports the matching file when detected.



\### OCR



Optical Character Recognition is performed using Tesseract OCR to extract visible text from the image.



The extracted OCR result is stored as part of the structured analysis response.



\### Photo-of-Photo Detection



The system includes a heuristic check to determine whether an image may be a photograph of another display or photograph.



This is intentionally implemented as a heuristic rather than claiming definitive authenticity detection.



\### Vehicle Number-Plate Analysis



The processor searches for candidate number-plate regions and attempts OCR-based recognition of Indian vehicle registration numbers.



The result reports:



\- Whether a plate region was detected

\- Whether a valid registration format was recognized

\- OCR output

\- Detection method

\- Candidate regions



\### Structured Analysis Results



The processor returns a structured result containing individual analysis sections such as:



\- `image`

\- `dimension\_validation`

\- `blur\_analysis`

\- `brightness\_analysis`

\- `duplicate\_detection`

\- `ocr`

\- `photo\_of\_photo`

\- `number\_plate`

\- `overall`

\- `processed\_at`



This allows the frontend or other consumers to use individual analysis results independently.



\### Issue Identification and Reporting



The system combines detected problems into an overall issue report.



The report includes:



\- Issue count

\- Issue names

\- Issue type

\- Severity

\- Detailed message

\- Related information such as duplicate filename

\- Recommendation for manual review when appropriate



Example:



```json

{

&#x20; "status": "acceptable",

&#x20; "issue\_count": 1,

&#x20; "issues": \[

&#x20;   "Duplicate image detected"

&#x20; ],

&#x20; "issue\_details": \[

&#x20;   {

&#x20;     "type": "duplicate",

&#x20;     "severity": "warning",

&#x20;     "message": "Duplicate image detected"

&#x20;   }

&#x20; ],

&#x20; "recommendation": "Manual review recommended"

}





\## 3. System Architecture



```text

┌──────────────────────────────┐

│        React Frontend        │

│                              │

│ Upload image                 │

│ Processing status            │

│ Analysis dashboard           │

│ Issue report                 │

└──────────────┬───────────────┘

&#x20;              │ HTTP / REST API

&#x20;              ▼

┌──────────────────────────────┐

│       FastAPI Backend        │

│                              │

│ POST /images                 │

│ GET  /images/{id}/status     │

│ GET  /images/{id}/results    │

│ GET  /health                 │

│ GET  /db-test                │

└──────────────┬───────────────┘

&#x20;              │

&#x20;              ▼

┌──────────────────────────────┐

│     Background Processing    │

│                              │

│ Image validation             │

│ Blur analysis                │

│ Brightness analysis          │

│ Duplicate detection          │

│ OCR                          │

│ Photo-of-photo heuristic     │

│ Number-plate analysis        │

│ Issue generation             │

└──────────────┬───────────────┘

&#x20;              │

&#x20;              ▼

┌──────────────────────────────┐

│          MongoDB             │

│                              │

│ Processing metadata          │

│ Processing status            │

│ Structured analysis results  │

│ Failure information          │

└──────────────────────────────┘





\---



\## 4. Processing Flow



The image-processing lifecycle is:



```text

User uploads image

&#x20;       │

&#x20;       ▼

FastAPI validates file type

&#x20;       │

&#x20;       ▼

Generate processing ID

&#x20;       │

&#x20;       ▼

Save image

&#x20;       │

&#x20;       ▼

Create MongoDB processing record

&#x20;       │

&#x20;       ▼

Return processing ID

&#x20;       │

&#x20;       ▼

Background processing starts

&#x20;       │

&#x20;       ├── Dimension validation

&#x20;       ├── Blur analysis

&#x20;       ├── Brightness analysis

&#x20;       ├── Duplicate detection

&#x20;       ├── OCR

&#x20;       ├── Photo-of-photo analysis

&#x20;       └── Number-plate analysis

&#x20;       │

&#x20;       ▼

Generate structured analysis

&#x20;       │

&#x20;       ▼

Generate overall issue report

&#x20;       │

&#x20;       ▼

Store completed result in MongoDB

&#x20;       │



&#x20;       ▼

Frontend retrieves and displays result



\---



\## 5. API Endpoints



\### Health Check



```http

GET /health



```markdown

Returns the health status of the API.



\### Database Test



```http

GET /db-test



```markdown

Checks whether the backend can successfully connect to MongoDB.



\### Upload Image



```http

POST /images



```markdown

Accepts an image file and returns a processing ID.



Example response:



```json

{

&#x20; "processing\_id": "example-processing-id",

&#x20; "status": "pending",

&#x20; "filename": "vehicle.jpg",

&#x20; "message": "Image uploaded and queued for processing"

}



\### Processing Status



```http

GET /images/{processing\_id}/status



```markdown

Returns the current processing status.



Possible states include:



```text

pending

processing

completed

failed



GET /images/{processing\_id}/results

Returns the stored structured analysis result.



\---



\## 6. Queue / Background Processing Strategy



The current implementation uses FastAPI background processing to prevent the upload endpoint from waiting for the complete image-analysis pipeline.



The upload request creates the processing record and returns a processing ID while analysis continues in the background.



\### Why this approach?



The assignment required an asynchronous processing workflow while keeping the implementation practical and deployable within the project scope.



FastAPI background processing provides a lightweight approach without introducing additional infrastructure such as a dedicated message broker.



\### Production-scale improvement



For higher workloads, the background-processing layer could be replaced with a durable distributed queue such as Redis with Celery/RQ or another message broker.



A possible production architecture would be:



```text

FastAPI

&#x20;  │

&#x20;  ▼

Redis / Message Broker

&#x20;  │

&#x20;  ▼

Worker Pool

&#x20;  │

&#x20;  ├── Worker 1

&#x20;  ├── Worker 2

&#x20;  ├── Worker 3

&#x20;  └── ...

&#x20;  │

&#x20;  ▼

MongoDB / Object Storage

The current implementation intentionally avoids this additional infrastructure for the MVP.



\---



\## 7. Database Design



MongoDB is used to store processing metadata and analysis results.



A processing document contains information such as:



```text

processing\_id

original\_filename

file\_path

file\_size

content\_type

status

failure\_reason

created\_at

updated\_at

analysis

This approach keeps processing state and the resulting analysis associated with a single processing record.



\---



\## 8. Failure Handling



The backend maintains processing states:



```text

pending → processing → completed

&#x20;                   ↘ failed

\- Distributed tracing



\---



\## 9. Design Decisions and Trade-offs



\### FastAPI



FastAPI was selected because it provides:



\- Simple REST API development

\- Request validation

\- Background task support

\- Automatic API documentation

\- Good performance for API workloads



\### MongoDB



MongoDB was selected because the analysis output contains multiple nested and evolving fields.



A document-oriented structure makes it convenient to store the complete analysis result without requiring a large relational schema.



\### Tesseract OCR



Tesseract provides local OCR processing without requiring an external paid OCR service.



The trade-off is that OCR accuracy can vary depending on:



\- Image quality

\- Text size

\- Orientation

\- Lighting

\- Background complexity



\### Heuristic Photo Detection



The photo-of-photo check is intentionally heuristic.



It should be treated as an indicator rather than definitive proof of image authenticity.



A future version could use a trained computer-vision model or a more sophisticated image-forensics pipeline.



\---



\## 10. Scalability Considerations



The current application is designed as an MVP.



Potential production improvements include:



\### Distributed Processing



Move image processing into independently scalable workers.



\### Object Storage



Instead of relying on local filesystem storage, production deployment could use object storage such as S3-compatible storage.



\### Durable Queue



Introduce Redis/Celery, RQ, RabbitMQ, or another durable message queue.



\### Database Indexing



Add indexes for frequently queried fields such as:



```text

processing\_id

status

created\_at

\- Processing latency metrics



\---



\## 11. Project Structure



```text

gogig-media-processing/

│

├── README.md

├── main.py

├── processor.py

├── database.py

├── .gitignore

│

├── screenshots/

│   ├── upload.png

│   ├── analysis.png

│   └── issue-report.png

│

└── frontend/

&#x20;   │

&#x20;   ├── public/

&#x20;   │   └── gogig-logo.png

&#x20;   │

&#x20;   ├── src/

&#x20;   │   ├── App.jsx

&#x20;   │   ├── App.css

&#x20;   │   ├── index.css

&#x20;   │   └── main.jsx

&#x20;   │

&#x20;   ├── package.json

&#x20;   ├── package-lock.json

&#x20;   └── vite.config.js



\---



\## 12. Technology Stack



\### Backend



\- Python

\- FastAPI

\- Uvicorn

\- MongoDB

\- PyMongo

\- OpenCV

\- Pillow

\- Tesseract OCR



\### Frontend



\- React

\- JavaScript

\- Vite

\- CSS



\### Development



\- Git

\- GitHub

\- Python virtual environment



\---



\## 13. Local Setup



\### Backend



Create and activate a Python virtual environment:



```powershell

python -m venv .venv

.\\.venv\\Scripts\\Activate.ps1

pip install -r requirements.txt

uvicorn main:app --reload





\---



\## 14. Frontend Setup



Move into the frontend directory:



```powershell

cd frontend



npm install



npm run dev

The frontend will be available through the Vite development URL displayed in the terminal.



\---



\## 15. Testing the API



Health check:



```powershell

curl.exe http://127.0.0.1:8000/health



curl.exe http://127.0.0.1:8000/db-test

GET /images/{processing\_id}/status

GET /images/{processing\_id}/results



\---



\## 16. Validation Performed During Development



The application was manually tested using:



\- FastAPI import validation

\- Health endpoint testing

\- MongoDB connectivity testing

\- Image upload testing

\- Background processing verification

\- MongoDB result inspection

\- Direct processor execution

\- OCR verification

\- Duplicate detection verification

\- Structured issue-report verification

\- Frontend-to-backend result rendering



A sample processed image successfully produced structured results including:



```text

Image dimensions

Blur analysis

Brightness analysis

Duplicate detection

OCR

Photo-of-photo analysis

Overall issue report



\---



\## 17. AI Usage Disclosure



AI tools were used during development as development assistants and reviewers.



They were used for:



\- Code suggestions

\- Debugging assistance

\- Implementation guidance

\- Frontend UI refinement

\- Documentation support

\- Identifying potential improvements



AI-generated suggestions were not treated as automatically correct.



The implementation was validated manually by:



\- Running the backend locally

\- Testing API endpoints

\- Executing the image processor

\- Inspecting MongoDB records

\- Checking actual API responses

\- Testing the frontend against the backend



\### Example of an AI-assisted issue that required correction



During development, an initial frontend data mapping expected analysis fields that did not match the actual backend response schema.



This caused some frontend fields to display `N/A`.



The issue was identified by directly testing the API with `curl`, inspecting the MongoDB analysis document, and comparing the actual response structure with the frontend mapping.



The frontend was then corrected to use the actual backend response fields.



This demonstrated that AI-generated suggestions were treated as development assistance rather than as unquestioned implementation.





\---



\## 18. Security Considerations



Sensitive configuration values are stored locally using environment variables.



The following are intentionally excluded from Git:



```text

.env

.venv/

uploads/

\_\_pycache\_\_/



\---



\## 19. Future Improvements



Potential improvements include:



\- Durable distributed processing queues

\- Horizontal worker scaling

\- Automatic processing retries

\- Object-storage integration

\- More advanced image-forensics models

\- Improved number-plate recognition

\- Better OCR preprocessing

\- Automated test coverage

\- Authentication and authorization

\- Rate limiting

\- Monitoring and observability

\- Production logging

\- Docker-based deployment

\- CI/CD pipeline



\---



\## 20. Submission



\*\*Project:\*\* gOGig Media Processing



\*\*Repository:\*\*  

https://github.com/Prajan1409/gogig-media-processing



\*\*Live Application:\*\*  

\_To be added after deployment.\_





\---



\## 21. Conclusion



gOGig Media Processing provides an end-to-end workflow for uploading, processing, analyzing, storing, and presenting image-analysis results.



The implementation focuses on a clear separation between the frontend, API layer, processing pipeline, and persistence layer while keeping the MVP practical to deploy and extend.

