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

    [HttpGet("options/{category}")]
    [Authorize(Policy = "AnyStaff")]
    public async Task<ActionResult<IEnumerable<string>>> GetOptions(string category, [FromServices] MauEyeCare.API.Data.AppDbContext context)
    {
        await EnsureOptionsTableExistsAsync(context);

        var options = await Microsoft.EntityFrameworkCore.EntityFrameworkQueryableExtensions.ToListAsync(
            System.Linq.Queryable.Select(
                System.Linq.Queryable.Where(context.ClinicalOptions, o => o.Category == category), 
                o => o.Value)
        );

        if (!options.Any())
        {
            // Seed defaults if empty
            if (category.Equals("Complaint", StringComparison.OrdinalIgnoreCase))
                options = new List<string> { "Redness", "Itching", "Foreign body sensation", "Dimness of vision", "Pain", "Headache", "Eye ache" };
            else if (category.Equals("MedicalHistory", StringComparison.OrdinalIgnoreCase))
                options = new List<string> { "Sugar", "BP", "Cardiac", "Major vital diseases" };
            else if (category.Equals("VA", StringComparison.OrdinalIgnoreCase))
                options = new List<string> { "Hand Movement", "Counting Fingers", "PL", "PR", "3/60", "6/60", "6/36", "6/24", "6/18", "6/12", "6/9", "6/6" };

            if (options.Any())
            {
                foreach (var opt in options)
                {
                    context.ClinicalOptions.Add(new ClinicalOption { OptionId = Guid.NewGuid(), Category = category, Value = opt });
                }
                await context.SaveChangesAsync();
            }
        }

        return Ok(options);
    }

    [HttpPost("options")]
    [Authorize(Policy = "DoctorOrAdmin")]
    public async Task<IActionResult> AddOption([FromBody] AddOptionRequest req, [FromServices] MauEyeCare.API.Data.AppDbContext context)
    {
        if (string.IsNullOrWhiteSpace(req.Category) || string.IsNullOrWhiteSpace(req.Value))
            return BadRequest("Category and Value are required.");

        await EnsureOptionsTableExistsAsync(context);

        var exists = await Microsoft.EntityFrameworkCore.EntityFrameworkQueryableExtensions.AnyAsync(
            System.Linq.Queryable.Where(context.ClinicalOptions, o => o.Category == req.Category && o.Value == req.Value)
        );

        if (!exists)
        {
            context.ClinicalOptions.Add(new ClinicalOption { OptionId = Guid.NewGuid(), Category = req.Category, Value = req.Value });
            await context.SaveChangesAsync();
        }

        return Ok();
    }

    private async Task EnsureOptionsTableExistsAsync(MauEyeCare.API.Data.AppDbContext context)
    {
        try
        {
            await Microsoft.EntityFrameworkCore.RelationalDatabaseFacadeExtensions.ExecuteSqlRawAsync(context.Database, @"
                CREATE TABLE IF NOT EXISTS ""ClinicalOptions"" (
                    ""OptionId"" TEXT PRIMARY KEY,
                    ""Category"" TEXT NOT NULL,
                    ""Value"" TEXT NOT NULL,
                    ""CreatedAt"" TEXT NOT NULL
                );
            ");

            // Seed default options if table is empty or just created
            if (!context.ClinicalOptions.Any())
            {
                var defaults = new List<ClinicalOption>();
                
                // 1. Complaints
                string[] complaints = { "Redness", "Itching", "Foreign body sensation", "Dimness of vision", "Pain", "Headache", "Eye ache" };
                foreach (var c in complaints) defaults.Add(new ClinicalOption { OptionId = Guid.NewGuid(), Category = "Complaint", Value = c });

                // 2. Medical History
                string[] medHist = { "Sugar", "BP", "Cardiac", "Major vital diseases" };
                foreach (var m in medHist) defaults.Add(new ClinicalOption { OptionId = Guid.NewGuid(), Category = "MedicalHistory", Value = m });

                // 3. Visual Acuity (VA)
                string[] vaOptions = { "6/6", "6/9", "6/12", "6/18", "6/24", "6/36", "6/60", "5/60", "4/60", "3/60", "2/60", "1/60", "CF", "HM", "PL+", "PR+" };
                foreach (var v in vaOptions) defaults.Add(new ClinicalOption { OptionId = Guid.NewGuid(), Category = "VA", Value = v });

                context.ClinicalOptions.AddRange(defaults);
                await context.SaveChangesAsync();
            }

            // Safely add Complaints column to Exams table if it doesn't exist
            try {
                await Microsoft.EntityFrameworkCore.RelationalDatabaseFacadeExtensions.ExecuteSqlRawAsync(context.Database, 
                    @"ALTER TABLE ""Exams"" ADD COLUMN ""Complaints"" TEXT;");
            } catch { /* Column likely already exists */ }
        }
        catch { /* Fallback if already handled by migrations */ }
    }
}

public record AddOptionRequest(string Category, string Value);

public record UpdateNotesRequest(string? Notes, string? Diagnosis);
