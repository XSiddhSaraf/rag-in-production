# Example Documents

This directory contains sample technical documents for testing the EU AI Act Compliance Analyzer.

## Sample Documents

### 1. sample_technical_document.md

A realistic technical specification for "SmartBorder AI" - a fictional biometric border control system.

**Expected Analysis Results**:
- **Contains AI**: Yes (high confidence)
- **High Risks**:
  - Real-time biometric identification (Article 5 - Prohibited AI)
  - Automated decision-making for border control (Article 6 - High-Risk AI)
  - Biometric categorization (Article 5)
- **Low Risks**:
  - Transparency obligations (Article 9)
  - Data governance requirements (Article 10)
  - Technical documentation (Article 11)

**Why This Example**:
This document is designed to trigger multiple risk categories under the EU AI Act:
- Uses biometric identification in public spaces (prohibited)
- Automates critical decisions affecting fundamental rights
- Processes sensitive personal data
- Deployed in high-risk domain (border control)

### Using This Sample

#### Convert to PDF for Testing

```bash
# Option 1: Using pandoc
pandoc sample_technical_document.md -o sample_technical_document.pdf

# Option 2: Using online converter
# Visit https://www.markdowntopdf.com/
# Upload sample_technical_document.md
# Download generated PDF

# Option 3: Print to PDF from browser
# Open sample_technical_document.md in GitHub
# Click "Print" → "Save as PDF"
```

#### Test With the API

```bash
# Upload the document
curl -X POST http://localhost:8000/api/upload \
  -F "file=@examples/sample_technical_document.pdf"
```

#### Test With the Frontend

1. Navigate to http://localhost:3000
2. Click or drag the PDF file to the upload area
3. Wait for analysis to complete
4. Review the dashboard results

### Creating Your Own Test Documents

To create effective test documents:

1. **Include AI/ML Keywords**:
   - Machine learning, deep learning, neural networks
   - AI, artificial intelligence
   - Computer vision, NLP, facial recognition
   - Automated decision-making

2. **Specify Use Cases**:
   - Border control, law enforcement
   - Healthcare, education
   - Employment, credit scoring
   - Critical infrastructure

3. **Describe Functionality**:
   - What the system does
   - How it makes decisions
   - What data it processes
   - Who is affected

4. **Include Technical Details**:
   - Model architectures
   - Training data
   - Performance metrics
   - Deployment information

### Non-AI Example

For comparison, here's what a document **without** AI components might look like:

```markdown
# Simple E-Commerce Website

## Overview
A basic online store built with React and Node.js.

## Features
- Product catalog with search
- Shopping cart
- Checkout with Stripe integration
- User accounts (login/register)
- Order history

## Technical Stack
- Frontend: React, Tailwind CSS
- Backend: Node.js, Express
- Database: PostgreSQL
- Payment: Stripe API
- Hosting: Vercel + AWS

## Implementation
Standard CRUD operations with RESTful API.
No machine learning or AI components.
```

**Expected Results**: Contains AI = No, High Risks = 0, Low Risks = 0

## Tips for Testing

1. **Vary Document Complexity**:
   - Simple projects with clear AI usage
   - Complex systems with multiple AI components
   - Edge cases (ambiguous AI usage)

2. **Test Different Formats**:
   - PDF (both text-based and scanned)
   - Word documents (DOC, DOCX)
   - Different file sizes

3. **Check Evaluation Scores**:
   - High-quality documents should score >0.8
   - Poorly written docs may score <0.6
   - Use scores to improve document clarity

4. **Verify Risk Classifications**:
   - Cross-reference with EU AI Act text
   - Check if all AI components identified
   - Validate risk level assignments
