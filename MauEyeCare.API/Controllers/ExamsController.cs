using MauEyeCare.API.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using MauEyeCare.API.Services;
using System.IO;

namespace MauEyeCare.API.Controllers;

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
