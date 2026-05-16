using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace MauEyeCare.API.Models;

// ────────────────────────────────────────────────────────────────────────────
// Identity User
// ────────────────────────────────────────────────────────────────────────────
using Microsoft.AspNetCore.Identity;

public class ApplicationUser : IdentityUser
{
    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;
    public string Role { get; set; } = "Receptionist";
}

// ────────────────────────────────────────────────────────────────────────────
// Patient
// ────────────────────────────────────────────────────────────────────────────
public class Patient
{
    public Guid PatientId { get; set; }
    [Required, MaxLength(100)] public string FirstName { get; set; } = string.Empty;
    [Required, MaxLength(100)] public string LastName { get; set; } = string.Empty;
    [Required] public DateOnly DateOfBirth { get; set; }
    [MaxLength(20)] public string? Gender { get; set; }
    [MaxLength(20)] public string? Phone { get; set; }
    [MaxLength(200), EmailAddress] public string? Email { get; set; }
    [MaxLength(500)] public string? Address { get; set; }
    [MaxLength(64)] public string? AadhaarHash { get; set; }  // SHA-256 only
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime? UpdatedAt { get; set; }
    public bool IsDeleted { get; set; } = false;
    [MaxLength(500)] public string? MedicalHistory { get; set; }
    [MaxLength(500)] public string? Allergies { get; set; }
    public bool HasAiConsent { get; set; } = false;
    public DateTime? ConsentSignedAt { get; set; }
    [MaxLength(2000)] public string? ReferralLetterText { get; set; }

    // Navigation
    public ICollection<Appointment> Appointments { get; set; } = [];
    public ICollection<Exam> Exams { get; set; } = [];
    public ICollection<Invoice> Invoices { get; set; } = [];
}

// ────────────────────────────────────────────────────────────────────────────
// Staff
// ────────────────────────────────────────────────────────────────────────────
public class Staff
{
    public Guid StaffId { get; set; }
    [Required, MaxLength(100)] public string FirstName { get; set; } = string.Empty;
    [Required, MaxLength(100)] public string LastName { get; set; } = string.Empty;
    [MaxLength(50)] public string Role { get; set; } = "Receptionist";
    [MaxLength(200)] public string? Email { get; set; }
    public string? IdentityUserId { get; set; }
    public bool IsActive { get; set; } = true;
    [MaxLength(50)] public string? Specialization { get; set; }
    [MaxLength(50)] public string? LicenseNumber { get; set; }
}

// ────────────────────────────────────────────────────────────────────────────
// Appointment
// ────────────────────────────────────────────────────────────────────────────
public class Appointment
{
    public Guid AppointmentId { get; set; }
    [Required] public Guid PatientId { get; set; }
    [Required] public string DoctorUserId { get; set; } = string.Empty;
    [Required] public DateTime ScheduledAt { get; set; }
    public int DurationMinutes { get; set; } = 30;
    [MaxLength(30)] public string Status { get; set; } = "Scheduled";
    [MaxLength(1000)] public string? Notes { get; set; }
    [MaxLength(50)] public string? AppointmentType { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public bool IsDeleted { get; set; } = false;

    // Navigation
    public Patient Patient { get; set; } = null!;
}

// ────────────────────────────────────────────────────────────────────────────
// Exam (Clinical Encounter)
// ────────────────────────────────────────────────────────────────────────────
public class Exam
{
    public Guid ExamId { get; set; }
    [Required] public Guid PatientId { get; set; }
    public Guid? AppointmentId { get; set; }
    [Required] public string DoctorUserId { get; set; } = string.Empty;
    [Required] public DateTime ExamDate { get; set; }

    // Without Glasses (WOG)
    [Column(TypeName = "decimal(5,2)")] public decimal? WOG_OD_Sphere { get; set; }
    [Column(TypeName = "decimal(5,2)")] public decimal? WOG_OD_Cylinder { get; set; }
    public int? WOG_OD_Axis { get; set; }
    [MaxLength(10)] public string? WOG_OD_VA { get; set; }
    [Column(TypeName = "decimal(5,1)")] public decimal? WOG_OD_IOP { get; set; }
    [MaxLength(10)] public string? WOG_OD_Add { get; set; }

    [Column(TypeName = "decimal(5,2)")] public decimal? WOG_OS_Sphere { get; set; }
    [Column(TypeName = "decimal(5,2)")] public decimal? WOG_OS_Cylinder { get; set; }
    public int? WOG_OS_Axis { get; set; }
    [MaxLength(10)] public string? WOG_OS_VA { get; set; }
    [Column(TypeName = "decimal(5,1)")] public decimal? WOG_OS_IOP { get; set; }
    [MaxLength(10)] public string? WOG_OS_Add { get; set; }

    // With Glasses (WG)
    [Column(TypeName = "decimal(5,2)")] public decimal? WG_OD_Sphere { get; set; }
    [Column(TypeName = "decimal(5,2)")] public decimal? WG_OD_Cylinder { get; set; }
    public int? WG_OD_Axis { get; set; }
    [MaxLength(10)] public string? WG_OD_VA { get; set; }
    [Column(TypeName = "decimal(5,1)")] public decimal? WG_OD_IOP { get; set; }
    [MaxLength(10)] public string? WG_OD_Add { get; set; }

    [Column(TypeName = "decimal(5,2)")] public decimal? WG_OS_Sphere { get; set; }
    [Column(TypeName = "decimal(5,2)")] public decimal? WG_OS_Cylinder { get; set; }
    public int? WG_OS_Axis { get; set; }
    [MaxLength(10)] public string? WG_OS_VA { get; set; }
    [Column(TypeName = "decimal(5,1)")] public decimal? WG_OS_IOP { get; set; }
    [MaxLength(10)] public string? WG_OS_Add { get; set; }

    // NV (Near Vision) & PD (Pupillary Distance)
    [MaxLength(10)] public string? OD_NV { get; set; }
    [MaxLength(10)] public string? OS_NV { get; set; }
    [MaxLength(10)] public string? OD_PD { get; set; }
    [MaxLength(10)] public string? OS_PD { get; set; }

    // Diagnosis & Prescription
    [MaxLength(2000)] public string? Diagnosis { get; set; }
    [MaxLength(500)] public string? PrescriptionPdfPath { get; set; }
    public string? DoctorNotes { get; set; }
    public string? Complaints { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public bool IsDeleted { get; set; } = false;

    // Navigation
    public Patient Patient { get; set; } = null!;
    public ICollection<ClinicalImage> Images { get; set; } = [];
}

// ────────────────────────────────────────────────────────────────────────────
// Clinical Image
// ────────────────────────────────────────────────────────────────────────────
public class ClinicalImage
{
    public Guid ImageId { get; set; }
    [Required] public Guid ExamId { get; set; }
    [MaxLength(50)] public string? ImageType { get; set; }  // Fundus/OCT/SlitLamp
    [MaxLength(500)] public string? FilePath { get; set; }
    [MaxLength(200)] public string? DicomUID { get; set; }
    public DateTime UploadedAt { get; set; } = DateTime.UtcNow;
    public Guid? AiJobId { get; set; }
    [MaxLength(30)] public string AiStatus { get; set; } = "Pending";

    // Navigation
    public Exam Exam { get; set; } = null!;
    public AiResult? AiResult { get; set; }
}

// ────────────────────────────────────────────────────────────────────────────
// AI Result
// ────────────────────────────────────────────────────────────────────────────
public class AiResult
{
    public Guid ResultId { get; set; }
    public Guid? ImageId { get; set; }
    public Guid? ExamId { get; set; }
    public string? ConditionSuggestions { get; set; }  // JSON array
    public string? Confidences { get; set; }           // JSON array
    [Column(TypeName = "decimal(5,4)")] public decimal? ImageQualityScore { get; set; }
    [MaxLength(50)] public string? ModelVersion { get; set; }
    public bool ConsentGiven { get; set; } = false;
    public string? RawResponse { get; set; }
    public DateTime GeneratedAt { get; set; } = DateTime.UtcNow;
}

// ────────────────────────────────────────────────────────────────────────────
// Invoice & Line Items
// ────────────────────────────────────────────────────────────────────────────
public class Invoice
{
    public Guid InvoiceId { get; set; }
    [Required] public Guid PatientId { get; set; }
    public Guid? AppointmentId { get; set; }
    [Required] public DateOnly InvoiceDate { get; set; }
    [Column(TypeName = "decimal(10,2)")] public decimal TotalAmount { get; set; }
    [Column(TypeName = "decimal(10,2)")] public decimal PaidAmount { get; set; } = 0;
    [MaxLength(20)] public string Status { get; set; } = "Unpaid";
    [MaxLength(20)] public string? GstNumber { get; set; }
    [MaxLength(50)] public string? PaymentMethod { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public bool IsDeleted { get; set; } = false;

    // Navigation
    public Patient Patient { get; set; } = null!;
    public ICollection<InvoiceLineItem> LineItems { get; set; } = [];
}

public class InvoiceLineItem
{
    public Guid LineItemId { get; set; }
    [Required] public Guid InvoiceId { get; set; }
    [MaxLength(300)] public string? Description { get; set; }
    public int Quantity { get; set; } = 1;
    [Column(TypeName = "decimal(10,2)")] public decimal UnitPrice { get; set; }
    [Column(TypeName = "decimal(10,2)")] public decimal Total { get; set; }
    [MaxLength(50)] public string? Category { get; set; }

    // Navigation
    public Invoice Invoice { get; set; } = null!;
}

// ────────────────────────────────────────────────────────────────────────────
// Inventory
// ────────────────────────────────────────────────────────────────────────────
public class InventoryItem
{
    public Guid ItemId { get; set; }
    [Required, MaxLength(200)] public string Name { get; set; } = string.Empty;
    [MaxLength(100)] public string? Category { get; set; }
    [MaxLength(50)] public string? SKU { get; set; }
    public int Quantity { get; set; } = 0;
    public int ReorderLevel { get; set; } = 5;
    [Column(TypeName = "decimal(10,2)")] public decimal? UnitPrice { get; set; }
    public DateOnly? ExpiryDate { get; set; }
    [MaxLength(100)] public string? Manufacturer { get; set; }
    [MaxLength(50)] public string? BatchNumber { get; set; }
    public DateTime? UpdatedAt { get; set; }
}

// ────────────────────────────────────────────────────────────────────────────
// Audit Log
// ────────────────────────────────────────────────────────────────────────────
public class AuditEntry
{
    public long AuditId { get; set; }
    public string? UserId { get; set; }
    [MaxLength(100)] public string? Action { get; set; }
    [MaxLength(100)] public string? EntityType { get; set; }
    [MaxLength(100)] public string? EntityId { get; set; }
    public string? OldValues { get; set; }
    public string? NewValues { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    [MaxLength(50)] public string? IpAddress { get; set; }
}

public class AiConsentAuditLog
{
    [Key]
    public Guid LogId { get; set; }
    public Guid PatientId { get; set; }
    public bool ConsentGranted { get; set; }
    public string? IdentityUserId { get; set; }
    public string? ActionDescription { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    [MaxLength(50)] public string? IpAddress { get; set; }
}

// ────────────────────────────────────────────────────────────────────────────
// AI Training Feedback
// ────────────────────────────────────────────────────────────────────────────
public class TrainingFeedback
{
    [Key]
    public Guid FeedbackId { get; set; }
    [Required] public Guid ImageId { get; set; }
    [Required, MaxLength(200)] public string CorrectLabel { get; set; } = string.Empty;
    [MaxLength(200)] public string? SubmittedBy { get; set; }
    public DateTime SubmittedAt { get; set; } = DateTime.UtcNow;
}

// ────────────────────────────────────────────────────────────────────────────
// Clinical Options (Dropdowns)
// ────────────────────────────────────────────────────────────────────────────
public class ClinicalOption
{
    [Key]
    public Guid OptionId { get; set; }
    [Required, MaxLength(100)] public string Category { get; set; } = string.Empty;
    [Required, MaxLength(200)] public string Value { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
