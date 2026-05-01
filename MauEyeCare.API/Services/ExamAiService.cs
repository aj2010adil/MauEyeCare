using MauEyeCare.API.Data;
using MauEyeCare.API.Models;
using Microsoft.EntityFrameworkCore;
using Newtonsoft.Json;

namespace MauEyeCare.API.Services;

// ── DTOs ─────────────────────────────────────────────────────────────────────
public record ExamDto(
    Guid ExamId, Guid PatientId, string PatientName,
    Guid? AppointmentId, string DoctorUserId, DateTime ExamDate,
    decimal? WOG_OD_Sphere, decimal? WOG_OD_Cylinder, int? WOG_OD_Axis, string? WOG_OD_VA,
    decimal? WOG_OD_IOP, string? WOG_OD_Add,
    decimal? WOG_OS_Sphere, decimal? WOG_OS_Cylinder, int? WOG_OS_Axis, string? WOG_OS_VA,
    decimal? WOG_OS_IOP, string? WOG_OS_Add,
    decimal? WG_OD_Sphere, decimal? WG_OD_Cylinder, int? WG_OD_Axis, string? WG_OD_VA,
    decimal? WG_OD_IOP, string? WG_OD_Add,
    decimal? WG_OS_Sphere, decimal? WG_OS_Cylinder, int? WG_OS_Axis, string? WG_OS_VA,
    decimal? WG_OS_IOP, string? WG_OS_Add,
    string? OD_NV, string? OS_NV, string? OD_PD, string? OS_PD,
    string? Diagnosis, string? DoctorNotes, string? PrescriptionPdfPath,
    IEnumerable<ImageDto> Images, DateTime CreatedAt);

public record ImageDto(
    Guid ImageId, string? ImageType, string? FilePath, string? DicomUID, string AiStatus, DateTime UploadedAt);

public record CreateExamRequest(
    Guid PatientId, Guid? AppointmentId, string DoctorUserId, DateTime ExamDate,
    decimal? WOG_OD_Sphere, decimal? WOG_OD_Cylinder, int? WOG_OD_Axis, string? WOG_OD_VA,
    decimal? WOG_OD_IOP, string? WOG_OD_Add,
    decimal? WOG_OS_Sphere, decimal? WOG_OS_Cylinder, int? WOG_OS_Axis, string? WOG_OS_VA,
    decimal? WOG_OS_IOP, string? WOG_OS_Add,
    decimal? WG_OD_Sphere, decimal? WG_OD_Cylinder, int? WG_OD_Axis, string? WG_OD_VA,
    decimal? WG_OD_IOP, string? WG_OD_Add,
    decimal? WG_OS_Sphere, decimal? WG_OS_Cylinder, int? WG_OS_Axis, string? WG_OS_VA,
    decimal? WG_OS_IOP, string? WG_OS_Add,
    string? OD_NV, string? OS_NV, string? OD_PD, string? OS_PD,
    string? Diagnosis, string? DoctorNotes);

// ── AI Result DTO ─────────────────────────────────────────────────────────────
public record AiResultDto(
    Guid ResultId, Guid? ImageId, List<string> ConditionSuggestions,
    List<double> Confidences, double? ImageQualityScore,
    string? ModelVersion, DateTime GeneratedAt,
    string Disclaimer = "DECISION SUPPORT ONLY — Not a clinical diagnosis. Review by qualified clinician required.");

// ── Exam Interface ────────────────────────────────────────────────────────────
public interface IExamService
{
    Task<ExamDto?> GetByIdAsync(Guid id);
    Task<IEnumerable<ExamDto>> GetByPatientAsync(Guid patientId);
    Task<ExamDto> CreateAsync(CreateExamRequest req);
    Task<bool> UpdateNotesAsync(Guid id, string? notes, string? diagnosis);
    Task<bool> SetPrescriptionPdfAsync(Guid id, string pdfPath);
}

// ── AI Interface ──────────────────────────────────────────────────────────────
public interface IAiService
{
    Task<AiResultDto?> AnalyzeImageAsync(Guid imageId, bool consentGiven);
    Task<string?> OcrHandwritingAsync(string imagePath);
    Task<string?> GetRxSuggestionsAsync(string doctorNotes, string examContext);
    Task<AiResultDto?> GetResultForImageAsync(Guid imageId);
}

// ── Exam Implementation ───────────────────────────────────────────────────────
public class ExamService : IExamService
{
    private readonly AppDbContext _db;
    public ExamService(AppDbContext db) => _db = db;

    public async Task<ExamDto?> GetByIdAsync(Guid id)
    {
        var e = await _db.Exams
            .Include(x => x.Patient)
            .Include(x => x.Images)
            .FirstOrDefaultAsync(x => x.ExamId == id);
        return e is null ? null : MapToDto(e);
    }

    public async Task<IEnumerable<ExamDto>> GetByPatientAsync(Guid patientId) =>
        await _db.Exams
            .Include(x => x.Patient)
            .Include(x => x.Images)
            .Where(x => x.PatientId == patientId)
            .OrderByDescending(x => x.ExamDate)
            .Select(e => MapToDto(e))
            .ToListAsync();

    public async Task<ExamDto> CreateAsync(CreateExamRequest req)
    {
        var exam = new Exam
        {
            PatientId = req.PatientId,
            AppointmentId = req.AppointmentId,
            DoctorUserId = req.DoctorUserId,
            ExamDate = req.ExamDate,
            WOG_OD_Sphere = req.WOG_OD_Sphere, WOG_OD_Cylinder = req.WOG_OD_Cylinder,
            WOG_OD_Axis = req.WOG_OD_Axis, WOG_OD_VA = req.WOG_OD_VA, WOG_OD_IOP = req.WOG_OD_IOP,
            WOG_OD_Add = req.WOG_OD_Add,
            WOG_OS_Sphere = req.WOG_OS_Sphere, WOG_OS_Cylinder = req.WOG_OS_Cylinder,
            WOG_OS_Axis = req.WOG_OS_Axis, WOG_OS_VA = req.WOG_OS_VA, WOG_OS_IOP = req.WOG_OS_IOP,
            WOG_OS_Add = req.WOG_OS_Add,
            WG_OD_Sphere = req.WG_OD_Sphere, WG_OD_Cylinder = req.WG_OD_Cylinder,
            WG_OD_Axis = req.WG_OD_Axis, WG_OD_VA = req.WG_OD_VA, WG_OD_IOP = req.WG_OD_IOP,
            WG_OD_Add = req.WG_OD_Add,
            WG_OS_Sphere = req.WG_OS_Sphere, WG_OS_Cylinder = req.WG_OS_Cylinder,
            WG_OS_Axis = req.WG_OS_Axis, WG_OS_VA = req.WG_OS_VA, WG_OS_IOP = req.WG_OS_IOP,
            WG_OS_Add = req.WG_OS_Add,
            OD_NV = req.OD_NV, OS_NV = req.OS_NV,
            OD_PD = req.OD_PD, OS_PD = req.OS_PD,
            Diagnosis = req.Diagnosis, DoctorNotes = req.DoctorNotes
        };
        _db.Exams.Add(exam);
        await _db.SaveChangesAsync();
        await _db.Entry(exam).Reference(e => e.Patient).LoadAsync();
        return MapToDto(exam);
    }

    public async Task<bool> UpdateNotesAsync(Guid id, string? notes, string? diagnosis)
    {
        var exam = await _db.Exams.FindAsync(id);
        if (exam is null) return false;
        if (notes is not null) exam.DoctorNotes = notes;
        if (diagnosis is not null) exam.Diagnosis = diagnosis;
        await _db.SaveChangesAsync();
        return true;
    }

    public async Task<bool> SetPrescriptionPdfAsync(Guid id, string pdfPath)
    {
        var exam = await _db.Exams.FindAsync(id);
        if (exam is null) return false;
        exam.PrescriptionPdfPath = pdfPath;
        await _db.SaveChangesAsync();
        return true;
    }

    private static ExamDto MapToDto(Exam e) => new(
        e.ExamId, e.PatientId,
        $"{e.Patient?.FirstName} {e.Patient?.LastName}",
        e.AppointmentId, e.DoctorUserId, e.ExamDate,
        e.WOG_OD_Sphere, e.WOG_OD_Cylinder, e.WOG_OD_Axis, e.WOG_OD_VA, e.WOG_OD_IOP, e.WOG_OD_Add,
        e.WOG_OS_Sphere, e.WOG_OS_Cylinder, e.WOG_OS_Axis, e.WOG_OS_VA, e.WOG_OS_IOP, e.WOG_OS_Add,
        e.WG_OD_Sphere, e.WG_OD_Cylinder, e.WG_OD_Axis, e.WG_OD_VA, e.WG_OD_IOP, e.WG_OD_Add,
        e.WG_OS_Sphere, e.WG_OS_Cylinder, e.WG_OS_Axis, e.WG_OS_VA, e.WG_OS_IOP, e.WG_OS_Add,
        e.OD_NV, e.OS_NV, e.OD_PD, e.OS_PD,
        e.Diagnosis, e.DoctorNotes, e.PrescriptionPdfPath,
        e.Images.Select(img => new ImageDto(
            img.ImageId, img.ImageType, img.FilePath, img.DicomUID, img.AiStatus, img.UploadedAt)),
        e.CreatedAt);
}

// ── AI Service Implementation (calls Python microservice) ─────────────────────
public class AiService : IAiService
{
    private readonly HttpClient _http;
    private readonly AppDbContext _db;
    private readonly ILogger<AiService> _logger;

    public AiService(HttpClient http, AppDbContext db, ILogger<AiService> logger)
    {
        _http = http; _db = db; _logger = logger;
    }

    public async Task<AiResultDto?> AnalyzeImageAsync(Guid imageId, bool consentGiven)
    {
        if (!consentGiven)
            throw new InvalidOperationException("Patient consent is required before AI analysis.");

        var image = await _db.Images.FindAsync(imageId);
        if (image is null) return null;

        image.AiStatus = "Processing";
        await _db.SaveChangesAsync();

        try
        {
            using var form = new MultipartFormDataContent();
            if (image.FilePath is not null && File.Exists(image.FilePath))
            {
                var fileBytes = await File.ReadAllBytesAsync(image.FilePath);
                form.Add(new ByteArrayContent(fileBytes), "image", Path.GetFileName(image.FilePath));
            }
            form.Add(new StringContent(image.ImageType ?? "unknown"), "image_type");

            var response = await _http.PostAsync("/analyze", form);
            response.EnsureSuccessStatusCode();

            var json = await response.Content.ReadAsStringAsync();
            var raw = JsonConvert.DeserializeObject<dynamic>(json);

            var result = new AiResult
            {
                ImageId = imageId,
                ExamId = image.Exam?.ExamId,
                ConditionSuggestions = JsonConvert.SerializeObject(raw!.condition_suggestions),
                Confidences = JsonConvert.SerializeObject(raw!.confidence),
                ImageQualityScore = (decimal?)raw!.image_quality_score,
                ModelVersion = (string?)raw!.model_version ?? "1.0.0",
                ConsentGiven = consentGiven
            };

            _db.AiResults.Add(result);
            image.AiStatus = "Completed";
            await _db.SaveChangesAsync();

            return MapToDto(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "AI analysis failed for image {ImageId}", imageId);
            image.AiStatus = "Failed";
            await _db.SaveChangesAsync();
            return null;
        }
    }

    public async Task<string?> OcrHandwritingAsync(string imagePath)
    {
        try
        {
            var fileBytes = await File.ReadAllBytesAsync(imagePath);
            using var form = new MultipartFormDataContent();
            form.Add(new ByteArrayContent(fileBytes), "image", Path.GetFileName(imagePath));

            var response = await _http.PostAsync("/ocr", form);
            if (!response.IsSuccessStatusCode) return null;

            var json = await response.Content.ReadAsStringAsync();
            dynamic? result = JsonConvert.DeserializeObject(json);
            return result?.text;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "OCR failed for {Path}", imagePath);
            return null;
        }
    }

    public async Task<string?> GetRxSuggestionsAsync(string doctorNotes, string examContext)
    {
        try
        {
            var payload = new { doctor_notes = doctorNotes, exam_context = examContext };
            var response = await _http.PostAsJsonAsync("/rx-assist", payload);
            if (!response.IsSuccessStatusCode) return null;

            var json = await response.Content.ReadAsStringAsync();
            dynamic? result = JsonConvert.DeserializeObject(json);
            return result?.suggestion;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Rx assist failed");
            return null;
        }
    }

    public async Task<AiResultDto?> GetResultForImageAsync(Guid imageId)
    {
        var result = await _db.AiResults.FirstOrDefaultAsync(r => r.ImageId == imageId);
        return result is null ? null : MapToDto(result);
    }

    private static AiResultDto MapToDto(AiResult r) => new(
        r.ResultId, r.ImageId,
        JsonConvert.DeserializeObject<List<string>>(r.ConditionSuggestions ?? "[]") ?? [],
        JsonConvert.DeserializeObject<List<double>>(r.Confidences ?? "[]") ?? [],
        r.ImageQualityScore is null ? null : (double)r.ImageQualityScore,
        r.ModelVersion, r.GeneratedAt);
}
