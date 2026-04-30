using MauEyeCare.API.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using MauEyeCare.API.Services;
using MauEyeCare.API.Data;
using Microsoft.EntityFrameworkCore;
using System.IO;

namespace MauEyeCare.API.Controllers;

[ApiController]
[Route("api/v1/[controller]")]
[Produces("application/json")]
public class PatientsController : ControllerBase
{
    private readonly IPatientService _patients;
    private readonly IAiService _ai;
    private readonly ILogger<PatientsController> _logger;

    public PatientsController(IPatientService patients, IAiService ai, ILogger<PatientsController> logger)
    {
        _patients = patients; _ai = ai; _logger = logger;
    }

    /// <summary>List patients with optional search and pagination</summary>
    [HttpGet]
    [Authorize(Policy = "AnyStaff")]
    public async Task<ActionResult<PagedResult<PatientDto>>> GetPatients(
        [FromQuery] string? search,
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 20)
    {
        if (pageSize > 100) pageSize = 100;
        var result = await _patients.GetPatientsAsync(search, page, pageSize);
        return Ok(result);
    }

    /// <summary>Get a single patient by ID</summary>
    [HttpGet("{id:guid}")]
    [Authorize(Policy = "AnyStaff")]
    public async Task<ActionResult<PatientDto>> GetPatient(Guid id)
    {
        var patient = await _patients.GetPatientByIdAsync(id);
        return patient is null ? NotFound() : Ok(patient);
    }

    /// <summary>Create a new patient record</summary>
    [HttpPost]
    [Authorize(Policy = "AnyStaff")]
    public async Task<ActionResult<PatientDto>> CreatePatient([FromBody] CreatePatientRequest req)
    {
        if (!ModelState.IsValid) return BadRequest(ModelState);
        var patient = await _patients.CreatePatientAsync(req);
        _logger.LogInformation("Patient created: {PatientId}", patient.PatientId);
        return CreatedAtAction(nameof(GetPatient), new { id = patient.PatientId }, patient);
    }

    /// <summary>Update patient details</summary>
    [HttpPut("{id:guid}")]
    [Authorize(Policy = "AnyStaff")]
    public async Task<ActionResult<PatientDto>> UpdatePatient(Guid id, [FromBody] UpdatePatientRequest req)
    {
        var patient = await _patients.UpdatePatientAsync(id, req);
        return patient is null ? NotFound() : Ok(patient);
    }

    /// <summary>Soft-delete a patient (Admin only)</summary>
    [HttpDelete("{id:guid}")]
    [Authorize(Policy = "AdminOnly")]
    public async Task<IActionResult> DeletePatient(Guid id)
    {
        var success = await _patients.DeletePatientAsync(id);
        return success ? NoContent() : NotFound();
    }

    /// <summary>Scan Referral Letter via AI OCR</summary>
    [HttpPost("ocr")]
    [Authorize(Policy = "AnyStaff")]
    public async Task<ActionResult<OcrResponse>> OcrReferralLetter(IFormFile file)
    {
        if (file == null || file.Length == 0) return BadRequest("No file uploaded.");

        // Save file to temp location
        var tempPath = Path.GetTempFileName() + Path.GetExtension(file.FileName);
        using (var stream = new FileStream(tempPath, FileMode.Create))
        {
            await file.CopyToAsync(stream);
        }

        try
        {
            var text = await _ai.OcrHandwritingAsync(tempPath);
            if (string.IsNullOrEmpty(text)) return StatusCode(503, "OCR service unavailable or failed.");
            return Ok(new OcrResponse(text));
        }
        finally
        {
            if (System.IO.File.Exists(tempPath)) System.IO.File.Delete(tempPath);
        }
    }
}

public record OcrResponse(string Text);

[ApiController]
[Route("api/v1/[controller]")]
[Produces("application/json")]
public class AppointmentsController : ControllerBase
{
    private readonly IAppointmentService _appointments;

    public AppointmentsController(IAppointmentService appointments) => _appointments = appointments;

    [HttpGet]
    [Authorize(Policy = "AnyStaff")]
    public async Task<ActionResult<IEnumerable<AppointmentDto>>> GetAppointments(
        [FromQuery] DateTime? from, [FromQuery] DateTime? to, [FromQuery] string? doctorUserId)
        => Ok(await _appointments.GetAppointmentsAsync(from, to, doctorUserId));

    [HttpGet("today")]
    [Authorize(Policy = "AnyStaff")]
    public async Task<ActionResult<IEnumerable<AppointmentDto>>> GetTodays()
        => Ok(await _appointments.GetTodaysAppointmentsAsync());

    [HttpGet("{id:guid}")]
    [Authorize(Policy = "AnyStaff")]
    public async Task<ActionResult<AppointmentDto>> GetAppointment(Guid id)
    {
        var a = await _appointments.GetByIdAsync(id);
        return a is null ? NotFound() : Ok(a);
    }

    [HttpPost]
    [Authorize(Policy = "AnyStaff")]
    public async Task<ActionResult<AppointmentDto>> CreateAppointment([FromBody] CreateAppointmentRequest req)
    {
        try
        {
            var appt = await _appointments.CreateAsync(req);
            return CreatedAtAction(nameof(GetAppointment), new { id = appt.AppointmentId }, appt);
        }
        catch (InvalidOperationException ex)
        {
            return Conflict(new { error = ex.Message });
        }
    }

    [HttpPut("{id:guid}/status")]
    [Authorize(Policy = "AnyStaff")]
    public async Task<IActionResult> UpdateStatus(Guid id, [FromBody] UpdateStatusRequest req)
    {
        var success = await _appointments.UpdateStatusAsync(id, req.Status, req.Notes);
        return success ? NoContent() : NotFound();
    }

    [HttpDelete("{id:guid}")]
    [Authorize(Policy = "DoctorOrAdmin")]
    public async Task<IActionResult> Delete(Guid id)
        => await _appointments.DeleteAsync(id) ? NoContent() : NotFound();
}

public record UpdateStatusRequest(string Status, string? Notes);

[ApiController]
[Route("api/v1/[controller]")]
[Produces("application/json")]
public class ExamsController : ControllerBase
{
    private readonly IExamService _exams;

    public ExamsController(IExamService exams) => _exams = exams;

    [HttpGet("{id:guid}")]
    [Authorize(Policy = "AnyStaff")]
    public async Task<ActionResult<ExamDto>> GetExam(Guid id)
    {
        var exam = await _exams.GetByIdAsync(id);
        return exam is null ? NotFound() : Ok(exam);
    }

    [HttpGet("patient/{patientId:guid}")]
    [Authorize(Policy = "AnyStaff")]
    public async Task<ActionResult<IEnumerable<ExamDto>>> GetByPatient(Guid patientId)
        => Ok(await _exams.GetByPatientAsync(patientId));

    [HttpPost]
    [Authorize(Policy = "DoctorOrAdmin")]
    public async Task<ActionResult<ExamDto>> CreateExam([FromBody] CreateExamRequest req)
    {
        var exam = await _exams.CreateAsync(req);
        return CreatedAtAction(nameof(GetExam), new { id = exam.ExamId }, exam);
    }

    [HttpPatch("{id:guid}/notes")]
    [Authorize(Policy = "DoctorOrAdmin")]
    public async Task<IActionResult> UpdateNotes(Guid id, [FromBody] UpdateNotesRequest req)
        => await _exams.UpdateNotesAsync(id, req.Notes, req.Diagnosis) ? NoContent() : NotFound();

    [HttpGet("{id:guid}/pdf")]
    [Authorize(Policy = "AnyStaff")]
    public async Task<IActionResult> DownloadPrescriptionPdf(Guid id, [FromServices] IPrescriptionPdfService pdfService)
    {
        try
        {
            var filePath = await pdfService.GeneratePrescriptionAsync(id);
            var memory = new MemoryStream();
            using (var stream = new FileStream(filePath, FileMode.Open))
            {
                await stream.CopyToAsync(memory);
            }
            memory.Position = 0;
            return File(memory, "application/pdf", $"Prescription_{id:N}.pdf");
        }
        catch (ArgumentException)
        {
            return NotFound();
        }
    }
}

public record UpdateNotesRequest(string? Notes, string? Diagnosis);

[ApiController]
[Route("api/v1/[controller]")]
[Produces("application/json")]
public class InventoryController : ControllerBase
{
    private readonly IInventoryService _inventory;

    public InventoryController(IInventoryService inventory) => _inventory = inventory;

    [HttpGet]
    [Authorize(Policy = "AnyStaff")]
    public async Task<ActionResult<IEnumerable<InventoryItemDto>>> GetInventory(
        [FromQuery] string? category, [FromQuery] bool? lowStockOnly)
        => Ok(await _inventory.GetAllAsync(category, lowStockOnly));

    [HttpGet("low-stock")]
    [Authorize(Policy = "AnyStaff")]
    public async Task<ActionResult<IEnumerable<InventoryItemDto>>> GetLowStock()
        => Ok(await _inventory.GetLowStockItemsAsync());

    [HttpPost]
    [Authorize(Policy = "AdminOnly")]
    public async Task<ActionResult<InventoryItemDto>> Create([FromBody] CreateInventoryItemRequest req)
    {
        var item = await _inventory.CreateAsync(req);
        return CreatedAtAction(nameof(GetItem), new { id = item.ItemId }, item);
    }

    [HttpGet("{id:guid}")]
    [Authorize(Policy = "AnyStaff")]
    public async Task<ActionResult<InventoryItemDto>> GetItem(Guid id)
    {
        var item = await _inventory.GetByIdAsync(id);
        return item is null ? NotFound() : Ok(item);
    }

    [HttpPut("{id:guid}/adjust")]
    [Authorize(Policy = "DoctorOrAdmin")]
    public async Task<ActionResult<InventoryItemDto>> Adjust(Guid id, [FromBody] AdjustQuantityRequest req)
    {
        var item = await _inventory.AdjustQuantityAsync(id, req);
        return item is null ? NotFound() : Ok(item);
    }

    [HttpDelete("{id:guid}")]
    [Authorize(Policy = "DoctorOrAdmin")]
    public async Task<ActionResult> Delete(Guid id)
    {
        var success = await _inventory.DeleteAsync(id);
        return success ? NoContent() : NotFound();
    }
}

[ApiController]
[Route("api/v1/[controller]")]
[Produces("application/json")]
public class InvoicesController : ControllerBase
{
    private readonly IInvoiceService _invoices;

    public InvoicesController(IInvoiceService invoices) => _invoices = invoices;

    [HttpGet("patient/{patientId:guid}")]
    [Authorize(Policy = "AnyStaff")]
    public async Task<ActionResult<IEnumerable<InvoiceDto>>> GetByPatient(Guid patientId)
        => Ok(await _invoices.GetByPatientAsync(patientId));

    [HttpGet("{id:guid}")]
    [Authorize(Policy = "AnyStaff")]
    public async Task<ActionResult<InvoiceDto>> GetById(Guid id)
    {
        var inv = await _invoices.GetByIdAsync(id);
        return inv is null ? NotFound() : Ok(inv);
    }

    [HttpPost]
    [Authorize(Policy = "AnyStaff")]
    public async Task<ActionResult<InvoiceDto>> Create([FromBody] CreateInvoiceRequest req)
    {
        var inv = await _invoices.CreateAsync(req);
        return CreatedAtAction(nameof(GetById), new { id = inv.InvoiceId }, inv);
    }

    [HttpPut("{id:guid}/pay")]
    [Authorize(Policy = "AnyStaff")]
    public async Task<IActionResult> MarkPaid(Guid id, [FromBody] PaymentRequest req)
        => await _invoices.MarkPaidAsync(id, req.Amount, req.PaymentMethod) ? NoContent() : NotFound();
}

public record PaymentRequest(decimal Amount, string PaymentMethod);

[ApiController]
[Route("api/v1/[controller]")]
public class AuthController : ControllerBase
{
    private readonly ITokenService _tokens;

    public AuthController(ITokenService tokens) => _tokens = tokens;

    [HttpPost("login")]
    [AllowAnonymous]
    public async Task<ActionResult<TokenResponse>> Login([FromBody] LoginRequest req)
    {
        var response = await _tokens.LoginAsync(req);
        return response is null ? Unauthorized(new { error = "Invalid credentials" }) : Ok(response);
    }
}

[ApiController]
[Route("api/v1/[controller]")]
public class AiController : ControllerBase
{
    private readonly IAiService _ai;

    public AiController(IAiService ai) => _ai = ai;

    [HttpPost("analyze/{imageId:guid}")]
    [Authorize(Policy = "DoctorOrAdmin")]
    public async Task<ActionResult<AiResultDto>> Analyze(Guid imageId, [FromBody] ConsentRequest req)
    {
        try
        {
            var result = await _ai.AnalyzeImageAsync(imageId, req.ConsentGiven);
            return result is null ? NotFound() : Ok(result);
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(new { error = ex.Message });
        }
    }

    [HttpGet("results/{imageId:guid}")]
    [Authorize(Policy = "AnyStaff")]
    public async Task<ActionResult<AiResultDto>> GetResult(Guid imageId)
    {
        var result = await _ai.GetResultForImageAsync(imageId);
        return result is null ? NotFound() : Ok(result);
    }

    [HttpPost("rx-assist")]
    [Authorize(Policy = "DoctorOrAdmin")]
    public async Task<ActionResult<string>> GetRxSuggestions([FromBody] RxAssistRequest req)
    {
        var suggestion = await _ai.GetRxSuggestionsAsync(req.DoctorNotes, req.ExamContext);
        return suggestion is null ? StatusCode(503, "AI service unavailable") : Ok(new { suggestion });
    }

    [HttpPost("feedback")]
    [Authorize(Policy = "DoctorOrAdmin")]
    public async Task<IActionResult> SubmitFeedback([FromBody] FeedbackRequest req, [FromServices] AppDbContext context)
    {
        if (req == null || string.IsNullOrWhiteSpace(req.CorrectLabel) || string.IsNullOrWhiteSpace(req.ImageBase64))
            return BadRequest("Invalid feedback payload.");

        // 0. Ensure Table Exists
        try
        {
            await context.Database.ExecuteSqlRawAsync(@"
                CREATE TABLE IF NOT EXISTS ""TrainingFeedbacks"" (
                    ""FeedbackId"" UUID PRIMARY KEY,
                    ""ImageId"" UUID NOT NULL,
                    ""CorrectLabel"" VARCHAR(200) NOT NULL,
                    ""SubmittedBy"" VARCHAR(200),
                    ""SubmittedAt"" TIMESTAMP WITH TIME ZONE NOT NULL
                );
            ");
        }
        catch { /* resilience fallback */ }

        // 1. Audit log the feedback
        var feedback = new TrainingFeedback
        {
            FeedbackId = Guid.NewGuid(),
            ImageId = req.ImageId,
            CorrectLabel = req.CorrectLabel,
            SubmittedBy = User.Identity?.Name ?? "Doctor",
            SubmittedAt = DateTime.UtcNow
        };
        context.TrainingFeedbacks.Add(feedback);
        await context.SaveChangesAsync();

        // 2. Forward to Python AI microservice
        using var client = new System.Net.Http.HttpClient();
        var pyPayload = new {
            image_id = req.ImageId.ToString(),
            image_base64 = req.ImageBase64,
            correct_label = req.CorrectLabel
        };
        
        try
        {
            var content = new StringContent(System.Text.Json.JsonSerializer.Serialize(pyPayload), System.Text.Encoding.UTF8, "application/json");
            var response = await client.PostAsync("http://localhost:5050/feedback", content);
            if (!response.IsSuccessStatusCode)
            {
                return StatusCode((int)response.StatusCode, "Failed to update model in AI microservice.");
            }
        }
        catch (Exception ex)
        {
            return StatusCode(500, $"AI Microservice unreachable: {ex.Message}");
        }

        return Ok(new { message = "Feedback recorded and fine-tuning initiated." });
    }
}

public record FeedbackRequest(Guid ImageId, string CorrectLabel, string ImageBase64);

public record ConsentRequest(bool ConsentGiven);
public record RxAssistRequest(string DoctorNotes, string ExamContext);
