using MauEyeCare.API.Data;
using MauEyeCare.API.Models;
using Microsoft.EntityFrameworkCore;

namespace MauEyeCare.API.Services;

// ── DTOs ─────────────────────────────────────────────────────────────────────
public record PatientDto(
    Guid PatientId, string FirstName, string LastName, DateOnly DateOfBirth,
    string? Gender, string? Phone, string? Email, string? Address,
    string? MedicalHistory, string? Allergies, DateTime CreatedAt,
    bool HasAiConsent, DateTime? ConsentSignedAt, string? ReferralLetterText);

public record CreatePatientRequest(
    string FirstName, string LastName, DateOnly DateOfBirth,
    string? Gender, string? Phone, string? Email, string? Address,
    string? MedicalHistory, string? Allergies, string? AadhaarLast4,
    bool HasAiConsent = false, string? ReferralLetterText = null);

public record UpdatePatientRequest(
    string? FirstName, string? LastName, string? Gender, string? Phone,
    string? Email, string? Address, string? MedicalHistory, string? Allergies,
    bool? HasAiConsent = null, string? ReferralLetterText = null);

public record PagedResult<T>(IEnumerable<T> Items, int TotalCount, int Page, int PageSize);

// ── Interface ─────────────────────────────────────────────────────────────────
public interface IPatientService
{
    Task<PagedResult<PatientDto>> GetPatientsAsync(string? search, int page, int pageSize);
    Task<PatientDto?> GetPatientByIdAsync(Guid id);
    Task<PatientDto> CreatePatientAsync(CreatePatientRequest request);
    Task<PatientDto?> UpdatePatientAsync(Guid id, UpdatePatientRequest request);
    Task<bool> DeletePatientAsync(Guid id);
}

// ── Implementation ────────────────────────────────────────────────────────────
public class PatientService : IPatientService
{
    private readonly AppDbContext _db;

    public PatientService(AppDbContext db) => _db = db;

    public async Task<PagedResult<PatientDto>> GetPatientsAsync(string? search, int page, int pageSize)
    {
        var q = _db.Patients.Where(p => !p.IsDeleted).AsQueryable();
        if (!string.IsNullOrWhiteSpace(search))
        {
            search = search.ToLower();
            q = q.Where(p =>
                p.FirstName.ToLower().Contains(search) ||
                p.LastName.ToLower().Contains(search) ||
                (p.Phone != null && p.Phone.Contains(search)) ||
                (p.Email != null && p.Email.ToLower().Contains(search)));
        }

        var total = await q.CountAsync();
        var items = await q
            .OrderByDescending(p => p.CreatedAt)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .Select(p => MapToDto(p))
            .ToListAsync();

        return new PagedResult<PatientDto>(items, total, page, pageSize);
    }

    public async Task<PatientDto?> GetPatientByIdAsync(Guid id)
    {
        var p = await _db.Patients.FindAsync(id);
        return p is null ? null : MapToDto(p);
    }

    public async Task<PatientDto> CreatePatientAsync(CreatePatientRequest req)
    {
        var patient = new Patient
        {
            FirstName = req.FirstName,
            LastName = req.LastName,
            DateOfBirth = req.DateOfBirth,
            Gender = req.Gender,
            Phone = req.Phone,
            Email = req.Email,
            Address = req.Address,
            MedicalHistory = req.MedicalHistory,
            Allergies = req.Allergies,
            HasAiConsent = req.HasAiConsent,
            ConsentSignedAt = req.HasAiConsent ? DateTime.UtcNow : null,
            ReferralLetterText = req.ReferralLetterText,
            AadhaarHash = req.AadhaarLast4 is not null
                ? Convert.ToHexString(
                    System.Security.Cryptography.SHA256.HashData(
                        System.Text.Encoding.UTF8.GetBytes(req.AadhaarLast4)))
                : null
        };

        _db.Patients.Add(patient);
        await _db.SaveChangesAsync();

        if (patient.HasAiConsent)
        {
            _db.AiConsentAuditLogs.Add(new AiConsentAuditLog
            {
                LogId = Guid.NewGuid(),
                PatientId = patient.PatientId,
                ConsentGranted = true,
                ActionDescription = "Initial consent granted during digital intake.",
                Timestamp = DateTime.UtcNow
            });
            await _db.SaveChangesAsync();
        }

        return MapToDto(patient);
    }

    public async Task<PatientDto?> UpdatePatientAsync(Guid id, UpdatePatientRequest req)
    {
        var patient = await _db.Patients.FindAsync(id);
        if (patient is null) return null;

        if (req.FirstName is not null) patient.FirstName = req.FirstName;
        if (req.LastName is not null) patient.LastName = req.LastName;
        if (req.Gender is not null) patient.Gender = req.Gender;
        if (req.Phone is not null) patient.Phone = req.Phone;
        if (req.Email is not null) patient.Email = req.Email;
        if (req.Address is not null) patient.Address = req.Address;
        if (req.MedicalHistory is not null) patient.MedicalHistory = req.MedicalHistory;
        if (req.Allergies is not null) patient.Allergies = req.Allergies;
        if (req.HasAiConsent.HasValue && req.HasAiConsent.Value != patient.HasAiConsent)
        {
            patient.HasAiConsent = req.HasAiConsent.Value;
            patient.ConsentSignedAt = req.HasAiConsent.Value ? DateTime.UtcNow : null;

            _db.AiConsentAuditLogs.Add(new AiConsentAuditLog
            {
                LogId = Guid.NewGuid(),
                PatientId = patient.PatientId,
                ConsentGranted = req.HasAiConsent.Value,
                ActionDescription = $"Consent status updated to: {req.HasAiConsent.Value}",
                Timestamp = DateTime.UtcNow
            });
        }
        if (req.ReferralLetterText is not null) patient.ReferralLetterText = req.ReferralLetterText;
        patient.UpdatedAt = DateTime.UtcNow;

        await _db.SaveChangesAsync();
        return MapToDto(patient);
    }

    public async Task<bool> DeletePatientAsync(Guid id)
    {
        var patient = await _db.Patients.FindAsync(id);
        if (patient is null) return false;
        patient.IsDeleted = true;
        patient.UpdatedAt = DateTime.UtcNow;
        await _db.SaveChangesAsync();
        return true;
    }

    private static PatientDto MapToDto(Patient p) => new(
        p.PatientId, p.FirstName, p.LastName, p.DateOfBirth,
        p.Gender, p.Phone, p.Email, p.Address,
        p.MedicalHistory, p.Allergies, p.CreatedAt,
        p.HasAiConsent, p.ConsentSignedAt, p.ReferralLetterText);
}
