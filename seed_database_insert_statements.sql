-- ==========================================
-- MauEyeCare Complete Database Insert Scripts
-- Compatibility: PostgreSQL
-- ==========================================

-- 1. Patients Table
INSERT INTO "Patients" (
    "PatientId", "FirstName", "LastName", "DateOfBirth", "Gender", 
    "Phone", "Email", "Address", "AadhaarHash", "CreatedAt", 
    "IsDeleted", "MedicalHistory", "Allergies", "HasAiConsent"
) VALUES (
    'a1111111-1111-1111-1111-111111111111', 'Aarav', 'Sharma', '1988-04-12', 'Male',
    '9123456780', 'aarav.sharma@example.com', '101, Marine Drive, Mumbai', 
    'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', NOW(), 
    false, 'Mild Astigmatism', 'Penicillin', true
);

-- 2. Staffs Table
INSERT INTO "Staffs" (
    "StaffId", "FirstName", "LastName", "Role", "Email", 
    "IsActive", "Specialization", "LicenseNumber"
) VALUES (
    'b2222222-2222-2222-2222-222222222222', 'Maurice', 'Eyecare', 'DoctorOrAdmin', 
    'maurice@maueyecare.com', true, 'Ophthalmology', 'DOC-54321-OPH'
);

-- 3. Appointments Table
INSERT INTO "Appointments" (
    "AppointmentId", "PatientId", "DoctorUserId", "ScheduledAt", 
    "DurationMinutes", "Status", "Notes", "AppointmentType", "CreatedAt", "IsDeleted"
) VALUES (
    'c3333333-3333-3333-3333-333333333333', 'a1111111-1111-1111-1111-111111111111', 
    'b2222222-2222-2222-2222-222222222222', NOW() + INTERVAL '1 day', 
    30, 'Scheduled', 'Routine checkup and vision evaluation.', 'Consultation', NOW(), false
);

-- 4. Exams (Clinical Encounters)
INSERT INTO "Exams" (
    "ExamId", "PatientId", "AppointmentId", "DoctorUserId", "ExamDate",
    "OD_Sphere", "OD_Cylinder", "OD_Axis", "OD_VA", "OD_IOP", "OD_Add",
    "OS_Sphere", "OS_Cylinder", "OS_Axis", "OS_VA", "OS_IOP", "OS_Add",
    "OD_NV", "OS_NV", "Diagnosis", "PrescriptionPdfPath", "DoctorNotes", "CreatedAt", "IsDeleted"
) VALUES (
    'd4444444-4444-4444-4444-444444444444', 'a1111111-1111-1111-1111-111111111111', 
    'c3333333-3333-3333-3333-333333333333', 'b2222222-2222-2222-2222-222222222222', NOW(),
    -1.25, -0.50, 180, '6/6', 15.2, 'N/A',
    -1.00, -0.75, 175, '6/6', 16.0, 'N/A',
    'N6', 'N6', 'Bilateral Myopia', '/prescriptions/Rx_d4444.pdf', 
    'Wear prescribed frames continuously.', NOW(), false
);

-- 5. ClinicalImages Table
INSERT INTO "ClinicalImages" (
    "ImageId", "ExamId", "ImageType", "FilePath", "DicomUID", "UploadedAt", "AiStatus"
) VALUES (
    'e5555555-5555-5555-5555-555555555555', 'd4444444-4444-4444-4444-444444444444', 
    'Fundus', '/images/fundus_sample.png', '1.2.840.10008.1.2.3.4.5', NOW(), 'Completed'
);

-- 6. AiResults Table
INSERT INTO "AiResults" (
    "ResultId", "ImageId", "ExamId", "ConditionSuggestions", "Confidences", 
    "ImageQualityScore", "ModelVersion", "ConsentGiven", "GeneratedAt"
) VALUES (
    'f6666666-6666-6666-6666-666666666666', 'e5555555-5555-5555-5555-555555555555', 
    'd4444444-4444-4444-4444-444444444444', '["Normal", "Mild Myopia"]', '[0.95, 0.05]', 
    0.8954, 'v2.1.0', true, NOW()
);

-- 7. Invoices Table
INSERT INTO "Invoices" (
    "InvoiceId", "PatientId", "AppointmentId", "InvoiceDate", "TotalAmount", 
    "PaidAmount", "Status", "GstNumber", "PaymentMethod", "CreatedAt", "IsDeleted"
) VALUES (
    '11111111-1111-1111-1111-111111111111', 'a1111111-1111-1111-1111-111111111111', 
    'c3333333-3333-3333-3333-333333333333', '2026-04-26', 1500.00, 
    1500.00, 'Paid', '27AAECM1234F1Z5', 'UPI', NOW(), false
);

-- 8. InvoiceLineItems Table
INSERT INTO "InvoiceLineItems" (
    "LineItemId", "InvoiceId", "Description", "Quantity", "UnitPrice", "Total", "Category"
) VALUES (
    '22222222-2222-2222-2222-222222222222', '11111111-1111-1111-1111-111111111111', 
    'Optometry Consultation Fee', 1, 500.00, 500.00, 'Service'
), (
    '33333333-3333-3333-3333-333333333333', '11111111-1111-1111-1111-111111111111', 
    'Anti-Glare Corrective Spectacles', 1, 1000.00, 1000.00, 'Hardware'
);

-- 9. InventoryItems Table
INSERT INTO "InventoryItems" (
    "ItemId", "Name", "Category", "SKU", "Quantity", 
    "ReorderLevel", "UnitPrice", "ExpiryDate", "Manufacturer", "BatchNumber", "UpdatedAt"
) VALUES (
    '44444444-4444-4444-4444-444444444444', 'Tears Plus 10ml', 'Medicine', 'MED-TP-10', 45, 
    10, 150.00, '2027-12-31', 'Allergan', 'BATCH-8822', NOW()
), (
    '55555555-5555-5555-5555-555555555555', 'RayBan Aviator Frame', 'Frame', 'FRM-RB-AV', 12, 
    3, 4500.00, NULL, 'Luxottica', 'BATCH-4411', NOW()
);

-- 10. AuditEntries Table
INSERT INTO "AuditEntries" (
    "AuditId", "UserId", "Action", "EntityType", "EntityId", 
    "OldValues", "NewValues", "Timestamp", "IpAddress"
) VALUES (
    1, 'b2222222-2222-2222-2222-222222222222', 'ExamCreated', 'Exam', 'd4444444-4444-4444-4444-444444444444', 
    '{}', '{"PatientId":"a1111111"}', NOW(), '192.168.1.100'
);

-- 11. AiConsentAuditLogs Table
INSERT INTO "AiConsentAuditLogs" (
    "LogId", "PatientId", "ConsentGranted", "IdentityUserId", 
    "ActionDescription", "Timestamp", "IpAddress"
) VALUES (
    '66666666-6666-6666-6666-666666666666', 'a1111111-1111-1111-1111-111111111111', true, 
    'b2222222-2222-2222-2222-222222222222', 'Patient signed digital AI consent form.', NOW(), '127.0.0.1'
);

-- 12. TrainingFeedbacks Table
INSERT INTO "TrainingFeedbacks" (
    "FeedbackId", "ImageId", "CorrectLabel", "SubmittedBy", "SubmittedAt"
) VALUES (
    '77777777-7777-7777-7777-777777777777', 'e5555555-5555-5555-5555-555555555555', 
    'Diabetic Retinopathy - Grade 1', 'maurice@maueyecare.com', NOW()
);
