using MauEyeCare.Desktop.ViewModels;
using Newtonsoft.Json;
using System.IO;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text;

namespace MauEyeCare.Desktop.Services;

// ────────────────────────────────────────────────────────────────────────────
// Auth State
// ────────────────────────────────────────────────────────────────────────────
public interface IAuthService
{
    string? Token { get; }
    string CurrentUserName { get; }
    string CurrentUserRole { get; }
    void SetToken(string token, string userId, string role);
    void ClearToken();
}

public class AuthService : IAuthService
{
    public string? Token { get; private set; }
    public string CurrentUserName { get; private set; } = "Clinic Staff";
    public string CurrentUserRole { get; private set; } = "User";

    public void SetToken(string token, string userId, string role)
    {
        Token = token;
        CurrentUserRole = role;
        // Decode name from JWT
        try
        {
            var parts = token.Split('.');
            if (parts.Length == 3)
            {
                var payload = parts[1];
                var padded = payload.PadRight(payload.Length + (4 - payload.Length % 4) % 4, '=');
                var json = Encoding.UTF8.GetString(Convert.FromBase64String(padded));
                dynamic? claims = JsonConvert.DeserializeObject(json);
                CurrentUserName = (string?)claims?.unique_name ?? "User";
            }
        }
        catch { }
    }

    public void ClearToken() { Token = null; CurrentUserName = ""; CurrentUserRole = ""; }
}

// ────────────────────────────────────────────────────────────────────────────
// API Service Response Models
// ────────────────────────────────────────────────────────────────────────────
public record LoginResponse(string AccessToken, string RefreshToken, DateTime ExpiresAt, string UserId, string Role);

public record PatientResponse(
    Guid PatientId, string FirstName, string LastName, DateOnly DateOfBirth,
    string? Gender, string? Phone, string? Email, string? Address,
    string? MedicalHistory, string? Allergies, DateTime CreatedAt,
    bool HasAiConsent, DateTime? ConsentSignedAt, string? ReferralLetterText);

public record PagedResponse<T>(IEnumerable<T> Items, int TotalCount, int Page, int PageSize);

public record AppointmentResponse(
    Guid AppointmentId, Guid PatientId, string PatientName,
    string DoctorUserId, DateTime ScheduledAt, int DurationMinutes,
    string Status, string? Notes, string? AppointmentType, DateTime CreatedAt);

public record InventoryResponse(
    Guid ItemId, string Name, string? Category, string? SKU, int Quantity,
    int ReorderLevel, decimal? UnitPrice, DateOnly? ExpiryDate,
    string? Manufacturer, string? BatchNumber, bool IsLowStock);

public record InvoiceResponse(
    Guid InvoiceId, Guid PatientId, string PatientName, DateOnly InvoiceDate,
    decimal TotalAmount, decimal PaidAmount, string Status, string? PaymentMethod,
    IEnumerable<object> LineItems, DateTime CreatedAt);

// ────────────────────────────────────────────────────────────────────────────
// API Service Interface
// ────────────────────────────────────────────────────────────────────────────
public interface IApiService
{
    // Auth
    Task<LoginResponse?> LoginAsync(string email, string password);

    // Patients
    Task<PagedResponse<PatientResponse>> GetPatientsAsync(string? search, int page, int pageSize);
    Task<PatientResponse> CreatePatientAsync(PatientFormModel model);
    Task<PatientResponse> UpdatePatientAsync(Guid id, PatientFormModel model);
    Task DeletePatientAsync(Guid id);

    // Appointments
    Task<IEnumerable<AppointmentResponse>> GetTodayAppointmentsAsync();
    Task<IEnumerable<AppointmentResponse>> GetAppointmentsAsync(DateTime from, DateTime to);

    // Exams
    Task CreateExamAsync(ExamFormModel model);
    Task<IEnumerable<ExamListItem>> GetExamsByPatientAsync(Guid patientId);
    Task<byte[]?> GeneratePrescriptionPdfAsync(Guid examId);

    // Inventory
    Task<IEnumerable<InventoryResponse>> GetInventoryAsync(string? category, bool? lowStockOnly);
    Task<bool> AddInventoryItemAsync(string name, string? category, int quantity, decimal? unitPrice, int reorderLevel);
    Task<bool> DeleteInventoryItemAsync(Guid itemId);
    Task<bool> AdjustInventoryAsync(Guid itemId, int delta, string reason);

    // Invoices
    Task<IEnumerable<InvoiceResponse>> GetInvoicesByPatientAsync(Guid patientId);
    Task<bool> CreateInvoiceAsync(Guid patientId, decimal amount, string description);

    // AI
    Task<string?> OcrHandwritingAsync(string imagePath);
    Task<string?> GetRxSuggestionsAsync(string doctorNotes, string examContext);
    Task<AiAnalysisResponse?> AnalyzeImageAsync(string imagePath);
    Task<bool> CheckAiServiceHealthAsync();
    Task<string?> GetChatbotReplyAsync(string message);
    Task<bool> SubmitFeedbackAsync(Guid imageId, string correctLabel, string imageBase64);
}

public record AiAnalysisResponse(List<string> Conditions, List<double> Confidences, double QualityScore, string Disclaimer);

// ────────────────────────────────────────────────────────────────────────────
// API Service Implementation
// ────────────────────────────────────────────────────────────────────────────
public class ApiService : IApiService
{
    private readonly HttpClient _http;
    private readonly IAuthService _auth;

    public ApiService(HttpClient http, IAuthService auth)
    {
        _http = http; _auth = auth;
    }

    private void AddAuthHeader()
    {
        _http.DefaultRequestHeaders.Authorization = _auth.Token is not null
            ? new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", _auth.Token)
            : null;
    }

    public async Task<LoginResponse?> LoginAsync(string email, string password)
    {
        for (int i = 0; i < 3; i++)
        {
            try
            {
                var response = await _http.PostAsJsonAsync("/api/v1/auth/login", new { email, password });
                if (response.IsSuccessStatusCode)
                    return await response.Content.ReadFromJsonAsync<LoginResponse>();
                
                if (response.StatusCode == System.Net.HttpStatusCode.Unauthorized)
                    return null;
            }
            catch (Exception ex)
            {
                if (i == 2) throw; // Final attempt failed
                await Task.Delay(2000); // Wait for API to warm up
            }
        }
        return null;
    }

    public async Task<PagedResponse<PatientResponse>> GetPatientsAsync(
        string? search, int page, int pageSize)
    {
        AddAuthHeader();
        var url = $"/api/v1/patients?page={page}&pageSize={pageSize}";
        if (!string.IsNullOrEmpty(search)) url += $"&search={Uri.EscapeDataString(search)}";
        return await _http.GetFromJsonAsync<PagedResponse<PatientResponse>>(url)
               ?? new PagedResponse<PatientResponse>([], 0, 1, pageSize);
    }

    public async Task<PatientResponse> CreatePatientAsync(PatientFormModel model)
    {
        AddAuthHeader();
        var response = await _http.PostAsJsonAsync("/api/v1/patients", new
        {
            model.FirstName, model.LastName,
            DateOfBirth = DateOnly.FromDateTime(model.DateOfBirth),
            model.Gender, model.Phone, model.Email, model.Address,
            model.MedicalHistory, model.Allergies,
            HasAiConsent = model.HasAiConsent, model.ReferralLetterText
        });
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<PatientResponse>())!;
    }

    public async Task<PatientResponse> UpdatePatientAsync(Guid id, PatientFormModel model)
    {
        AddAuthHeader();
        var response = await _http.PutAsJsonAsync($"/api/v1/patients/{id}", new
        {
            model.FirstName, model.LastName, model.Gender,
            model.Phone, model.Email, model.Address, model.MedicalHistory, model.Allergies,
            HasAiConsent = (bool?)model.HasAiConsent, model.ReferralLetterText
        });
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<PatientResponse>())!;
    }

    public async Task DeletePatientAsync(Guid id)
    {
        AddAuthHeader();
        var response = await _http.DeleteAsync($"/api/v1/patients/{id}");
        response.EnsureSuccessStatusCode();
    }



    public async Task<IEnumerable<AppointmentResponse>> GetTodayAppointmentsAsync()
    {
        AddAuthHeader();
        return await _http.GetFromJsonAsync<IEnumerable<AppointmentResponse>>("/api/v1/appointments/today")
               ?? [];
    }

    public async Task<IEnumerable<AppointmentResponse>> GetAppointmentsAsync(DateTime from, DateTime to)
    {
        AddAuthHeader();
        var url = $"/api/v1/appointments?from={from:O}&to={to:O}";
        return await _http.GetFromJsonAsync<IEnumerable<AppointmentResponse>>(url) ?? [];
    }

    public async Task CreateExamAsync(ExamFormModel model)
    {
        AddAuthHeader();
        var response = await _http.PostAsJsonAsync("/api/v1/exams", new
        {
            model.PatientId,
            DoctorUserId = _auth.CurrentUserName,
            ExamDate = DateTime.UtcNow,
            OD_Sphere = ParseDecimal(model.OD_Sphere),
            OD_Cylinder = ParseDecimal(model.OD_Cylinder),
            OD_Axis = ParseInt(model.OD_Axis),
            OD_VA = model.OD_VA, OD_IOP = ParseDecimal(model.OD_IOP), OD_Add = model.OD_Add,
            OS_Sphere = ParseDecimal(model.OS_Sphere),
            OS_Cylinder = ParseDecimal(model.OS_Cylinder),
            OS_Axis = ParseInt(model.OS_Axis),
            OS_VA = model.OS_VA, OS_IOP = ParseDecimal(model.OS_IOP), OS_Add = model.OS_Add,
            model.Diagnosis, model.DoctorNotes
        });
        response.EnsureSuccessStatusCode();
    }

    public async Task<byte[]?> GeneratePrescriptionPdfAsync(Guid examId)
    {
        AddAuthHeader();
        var response = await _http.GetAsync($"/api/v1/exams/{examId}/pdf");
        if (!response.IsSuccessStatusCode) return null;
        return await response.Content.ReadAsByteArrayAsync();
    }

    public async Task<IEnumerable<ExamListItem>> GetExamsByPatientAsync(Guid patientId)
    {
        AddAuthHeader();
        var response = await _http.GetAsync($"/api/v1/exams/patient/{patientId}");
        if (!response.IsSuccessStatusCode) return [];
        var json = await response.Content.ReadAsStringAsync();
        dynamic? exams = JsonConvert.DeserializeObject(json);
        var list = new List<ExamListItem>();
        if (exams != null)
        {
            foreach (var e in exams)
                list.Add(new ExamListItem((Guid)e.examId, ((DateTime)e.examDate).ToString("dd/MM/yyyy"), (string)e.diagnosis ?? "No diagnosis"));
        }
        return list;
    }

    public async Task<IEnumerable<InventoryResponse>> GetInventoryAsync(string? category, bool? lowStockOnly)
    {
        AddAuthHeader();
        var url = "/api/v1/inventory";
        if (lowStockOnly == true) url += "?lowStockOnly=true";
        return await _http.GetFromJsonAsync<IEnumerable<InventoryResponse>>(url) ?? [];
    }

    public async Task<bool> AddInventoryItemAsync(string name, string? category, int quantity, decimal? unitPrice, int reorderLevel)
    {
        AddAuthHeader();
        var res = await _http.PostAsJsonAsync("/api/v1/inventory", new {
            Name = name, Category = category, Quantity = quantity,
            UnitPrice = unitPrice, ReorderLevel = reorderLevel
        });
        return res.IsSuccessStatusCode;
    }

    public async Task<bool> DeleteInventoryItemAsync(Guid itemId)
    {
        AddAuthHeader();
        var res = await _http.DeleteAsync($"/api/v1/inventory/{itemId}");
        return res.IsSuccessStatusCode;
    }

    public async Task<bool> AdjustInventoryAsync(Guid itemId, int delta, string reason)
    {
        AddAuthHeader();
        var res = await _http.PutAsJsonAsync($"/api/v1/inventory/{itemId}/adjust", new {
            Delta = delta, Reason = reason
        });
        return res.IsSuccessStatusCode;
    }

    public async Task<IEnumerable<InvoiceResponse>> GetInvoicesByPatientAsync(Guid patientId)
    {
        AddAuthHeader();
        return await _http.GetFromJsonAsync<IEnumerable<InvoiceResponse>>(
            $"/api/v1/invoices/patient/{patientId}") ?? [];
    }

    public async Task<bool> CreateInvoiceAsync(Guid patientId, decimal amount, string description)
    {
        AddAuthHeader();
        var req = new
        {
            PatientId = patientId,
            InvoiceDate = DateOnly.FromDateTime(DateTime.Today),
            LineItems = new[] { new { Description = description, Quantity = 1, UnitPrice = amount, Category = "Optical Shop" } }
        };
        var response = await _http.PostAsJsonAsync("/api/v1/invoices", req);
        return response.IsSuccessStatusCode;
    }

    public async Task<string?> OcrHandwritingAsync(string imagePath)
    {
        // Call Python AI service directly for OCR (bypasses main API)
        using var form = new MultipartFormDataContent();
        var fileBytes = await File.ReadAllBytesAsync(imagePath);
        form.Add(new ByteArrayContent(fileBytes), "image", Path.GetFileName(imagePath));

        // Use AI service base URL
        var aiHttp = new HttpClient { BaseAddress = new Uri("http://localhost:5050") };
        var response = await aiHttp.PostAsync("/ocr", form);
        if (!response.IsSuccessStatusCode) return null;

        var json = await response.Content.ReadAsStringAsync();
        dynamic? result = JsonConvert.DeserializeObject(json);
        return result?.text;
    }

    public async Task<string?> GetRxSuggestionsAsync(string doctorNotes, string examContext)
    {
        AddAuthHeader();
        var response = await _http.PostAsJsonAsync("/api/v1/ai/rx-assist", new
        {
            DoctorNotes = doctorNotes, ExamContext = examContext
        });
        if (!response.IsSuccessStatusCode) return null;
        var json = await response.Content.ReadAsStringAsync();
        dynamic? result = JsonConvert.DeserializeObject(json);
        return result?.suggestion;
    }

    public async Task<AiAnalysisResponse?> AnalyzeImageAsync(string imagePath)
    {
        try
        {
            using var form = new MultipartFormDataContent();
            var fileBytes = await File.ReadAllBytesAsync(imagePath);
            form.Add(new ByteArrayContent(fileBytes), "image", Path.GetFileName(imagePath));

            var aiHttp = new HttpClient { BaseAddress = new Uri("http://localhost:5050") };
            var response = await aiHttp.PostAsync("/analyze", form);
            if (!response.IsSuccessStatusCode) return null;

            var json = await response.Content.ReadAsStringAsync();
            dynamic? res = JsonConvert.DeserializeObject(json);
            if (res == null) return null;

            return new AiAnalysisResponse(
                ((Newtonsoft.Json.Linq.JArray)res.condition_suggestions).ToObject<List<string>>()!,
                ((Newtonsoft.Json.Linq.JArray)res.confidence).ToObject<List<double>>()!,
                (double)res.image_quality_score,
                (string)res.disclaimer
            );
        }
        catch { return null; }
    }

    public async Task<bool> CheckAiServiceHealthAsync()
    {
        try
        {
            var aiHttp = new HttpClient { BaseAddress = new Uri("http://localhost:5050"), Timeout = TimeSpan.FromSeconds(2) };
            var response = await aiHttp.GetAsync("/health");
            return response.IsSuccessStatusCode;
        }
        catch { return false; }
    }

    public async Task<string?> GetChatbotReplyAsync(string message)
    {
        try
        {
            var aiHttp = new HttpClient { BaseAddress = new Uri("http://localhost:5050") };
            var response = await aiHttp.PostAsJsonAsync("/chatbot", new { message });
            if (!response.IsSuccessStatusCode) return null;

            var json = await response.Content.ReadAsStringAsync();
            dynamic? res = JsonConvert.DeserializeObject(json);
            return res?.reply;
        }
        catch { return "Failed to reach booking assistant."; }
    }

    public async Task<bool> SubmitFeedbackAsync(Guid imageId, string correctLabel, string imageBase64)
    {
        try
        {
            AddAuthHeader();
            var payload = new { ImageId = imageId, CorrectLabel = correctLabel, ImageBase64 = imageBase64 };
            var response = await _http.PostAsJsonAsync("/api/v1/ai/feedback", payload);
            return response.IsSuccessStatusCode;
        }
        catch { return false; }
    }

    private static decimal? ParseDecimal(string? s) =>
        decimal.TryParse(s, out var d) ? d : null;
    private static int? ParseInt(string? s) =>
        int.TryParse(s, out var i) ? i : null;
}
