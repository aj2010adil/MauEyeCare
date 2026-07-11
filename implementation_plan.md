# Implementation Plan: Clinical Enhancements & Bug Fixes

This plan addresses session reset issues, missing data in prescriptions, and professional eye care vision terminology.

## User Review Required

> [!NOTE]
> I will be updating the distance vision options to include `CF 1m`, `CF 2m`, etc., and the `5/60`, `4/60` notation as requested. I will also add specific cataract surgery advice.

## Proposed Changes

### Main Application (`main_app_streamlined.py`)

#### 1. Session Reset Fix
- [ ] Add a more comprehensive clearing of `st.session_state` in the "Start New Patient" button logic.
- [ ] Explicitly clear form-related keys like `reg_name`, `reg_mobile`, etc.

#### 2. Prescription HTML Content
- [ ] Update the `prescription_html` generation logic to include `patient_complaint` and `advice`.
- [ ] Ensure the HTML structure properly reflects these sections.

#### 3. Vision Notation & Cataract Advice
- [ ] Update the `vision_options` list to include:
    - `CF 1m`, `CF 2m`, `CF 3m`, `CF 4m`, `CF 5m`, `CF 6m`.
    - `1/60`, `2/60`, `3/60`, `4/60`, `5/60`.
- [ ] Update the `advice_options` list to include:
    - `Cataract Surgery (Phaco)`, `Cataract Surgery (SICS)`, `Cataract Surgery (ECCE)`.

## Verification Plan

### Manual Verification
1.  **Reset Test**: Register a patient, go to the finalize tab, click "Start New Patient", and verify the registration form is empty.
2.  **Vision Test**: Open the vision testing dropdown and verify the new notations (`CF 1m`, `5/60`, etc.) are present.
3.  **Prescription Content Test**: Generate a prescription with a complaint and advice, download it, and verify the text is present in the HTML file.
