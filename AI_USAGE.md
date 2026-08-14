# AI Usage Disclosure



## Overview



AI tools were used as development assistance during the implementation of the gOGig Intelligent Media Processing project.



AI was used primarily for development guidance, debugging assistance, code suggestions, documentation support, and improving the user interface.



All generated suggestions were reviewed, tested, and adapted before being included in the final project.



---



## 1. Where AI Was Used



AI assistance was used during several stages of development.


### Development Guidance



AI was used to:



- Break down the assignment into smaller implementation tasks.

- Suggest approaches for implementing the image-processing workflow.

- Help understand FastAPI, React, MongoDB, and deployment configuration.

- Suggest project structure and implementation strategies.



### Frontend Development



AI assistance was used for:



- Improving the React interface structure.

- Refining the analysis results dashboard.

- Improving the layout and presentation of processing results.

- Suggesting UI text and component organization.



### Backend and API Development



AI was used to assist with:



- FastAPI endpoint implementation and debugging.

- API integration between the frontend and backend.

- CORS configuration.

- MongoDB connection troubleshooting.

- Deployment configuration.



### Documentation



AI was also used to help:



- Structure the README.

- Explain project features and processing flow.

- Document API endpoints.

- Document deployment and testing procedures.

- Improve the clarity and organization of project documentation.



---



## 2. What AI Helped With



AI primarily helped with:



- Understanding implementation requirements.

- Debugging errors and configuration issues.

- Suggesting code changes.

- Improving UI presentation.

- Explaining deployment errors.

- Structuring technical documentation.

- Reviewing implementation approaches.



AI was used as an assistant rather than as an autonomous development system.



The final implementation was reviewed and tested manually.



---



## 3. Where AI Output Was Wrong or Needed Correction



AI-generated suggestions were not always correct and required verification.



### OCR Deployment



The deployed application initially reported that Tesseract OCR was not installed or available in the production environment.



The issue was identified through actual testing of the deployed application.



The OCR-related UI was then adjusted so that internal installation errors would not be exposed directly to the user.



### MongoDB Connection



During testing, MongoDB initially produced connection and authentication errors.



The errors were investigated using the actual application response and MongoDB configuration.



The connection was subsequently verified successfully.



### CORS Configuration



The deployed frontend initially encountered API communication problems because the backend CORS configuration only allowed the local development frontend.



The deployed frontend URL was added to the backend CORS configuration and the application was tested again.



### Deployment Configuration



Deployment configuration also required manual verification.



For example, the Dockerfile was initially created as:



`Dockerfile.txt`



It was corrected to:



`Dockerfile`



before being committed to the repository.



These examples demonstrate that AI suggestions were treated as recommendations and were not accepted without testing.



---



## 4. How AI-Generated Code Was Validated



AI-assisted changes were validated through actual development and deployment testing.



### Local Testing



The application was run locally using:



- Frontend: http://localhost:5173

- Backend: http://localhost:8000



The frontend was tested by uploading images and checking whether the backend returned the expected results.



### API Testing



The backend endpoints were tested to verify:



- Image upload

- Processing status

- Processing results

- MongoDB connectivity



### Functional Testing



Multiple image scenarios were tested, including:



- Unique images

- Duplicate images

- Blurry images

- Different image formats

- Different image dimensions



### Deployment Testing



The deployed frontend and backend were tested together.



The final workflow was verified as:



User → React Frontend → FastAPI Backend → Image Processing → MongoDB → Analysis Results → React Frontend



The deployed application was manually tested after deployment to confirm that uploads and analysis results were working correctly.



---



## 5. Human Verification



AI suggestions were reviewed and modified during development.



The final decisions regarding:



- Application behavior

- UI design

- API configuration

- Database configuration

- Deployment

- Testing

- Error handling

- Documentation



were made and verified by the developer.



AI-generated code was therefore treated as an aid during development rather than as automatically trusted or production-ready code.



---



## 6. AI Tools Used



The primary AI assistance used during development included:



- Claude

- ChatGPT



These tools were used for development guidance, debugging, code review, documentation, and implementation assistance.



---



## 7. Final Statement



AI significantly assisted the development process, particularly in debugging, implementation guidance, UI refinement, and documentation.



However, generated suggestions were manually reviewed, corrected when necessary, and validated through local testing and deployment testing before being considered part of the final submission.







