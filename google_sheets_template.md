# Google Sheets Template for MauEyeCare Hospital Management

## Sheet ID: 1Ju6luR74A_emPUWThUYO9iNDXkPMblwNFt-Ql92fyPQ

### Required Sheets and Columns:

## 1. Medicines Sheet
| Column | Description | Example |
|--------|-------------|---------|
| name | Medicine name | Refresh Tears Eye Drops |
| category | Medicine category | Lubricant |
| type | Medicine type | Eye Drops |
| price | Price in rupees | 150 |
| quantity | Stock quantity | 25 |
| prescription_required | TRUE/FALSE | TRUE |
| indication | Medical indication | Dry eyes treatment |
| dosage | Dosage instructions | 1 drop twice daily |

## 2. Spectacles Sheet
| Column | Description | Example |
|--------|-------------|---------|
| name | Spectacle name | Ray-Ban Aviator Classic |
| brand | Brand name | Ray-Ban |
| model | Model name | Aviator Classic |
| category | Category | Luxury |
| price | Frame price | 5000 |
| lens_price | Lens price | 2000 |
| material | Frame material | Metal |
| shape | Frame shape | Aviator |
| image_path | Local image path | uploaded_images/rayban_001.jpg |

## 3. Patients Sheet
| Column | Description | Example |
|--------|-------------|---------|
| patient_id | Unique ID | P0001 |
| name | Patient name | John Doe |
| age | Patient age | 35 |
| gender | Gender | Male |
| mobile | Mobile number | 9876543210 |
| issue | Chief complaint | Blurry Vision |
| advice | Doctor's advice | Spectacle Prescription |
| od_sphere | Right eye sphere | +2.00 |
| od_cylinder | Right eye cylinder | -0.50 |
| od_axis | Right eye axis | 90 |
| os_sphere | Left eye sphere | +1.75 |
| os_cylinder | Left eye cylinder | -0.25 |
| os_axis | Left eye axis | 85 |
| age_group | Age category | Adult |
| season | Visit season | December |
| visit_type | New/Return | New |
| registration_date | Registration timestamp | 2024-12-01 14:30:22 |

## 4. Prescriptions Sheet
| Column | Description | Example |
|--------|-------------|---------|
| prescription_id | Unique ID | RX0001 |
| patient_name | Patient name | John Doe |
| patient_mobile | Mobile number | 9876543210 |
| medicines | Selected medicines | Refresh Tears, Antibiotic Drops |
| spectacles | Selected spectacles | Ray-Ban Aviator |
| total_cost | Total prescription cost | 7500 |
| date_created | Creation timestamp | 2024-12-01 15:00:00 |

## 5. Analytics Sheet
| Column | Description | Example |
|--------|-------------|---------|
| record_date | Record timestamp | 2024-12-01 15:30:00 |
| metric_type | Type of metric | patient_visit |
| metric_value | Metric value | 1 |
| patient_age_group | Age group | Adult |
| visit_type | New/Return | New |
| season | Season | December |
| issue_category | Issue type | Vision |
| revenue | Revenue generated | 7500 |

## Setup Instructions:

1. **Create Google Sheet**: Copy the template with above structure
2. **Set Permissions**: Make sheet publicly viewable (Anyone with link can view)
3. **Add Sample Data**: Populate with initial inventory and test data
4. **Update Sheet ID**: Use your sheet ID in the application
5. **Test Connection**: Verify data loads correctly in the application

## Benefits:

- **Real-time Updates**: Multiple users can update inventory simultaneously
- **Cloud Backup**: Data automatically backed up to Google Drive
- **Collaborative**: Team members can access and update data
- **Analytics Ready**: Data structure optimized for business intelligence
- **Export Friendly**: Easy to export for external analysis
- **Professional**: Suitable for hospital management and marketing analysis