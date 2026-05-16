using MauEyeCare.API.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using MauEyeCare.API.Services;
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
