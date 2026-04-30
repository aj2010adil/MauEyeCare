using Microsoft.AspNetCore.SignalR;
using Microsoft.EntityFrameworkCore;
using QuestPDF.Fluent;
using QuestPDF.Helpers;
using QuestPDF.Infrastructure;

namespace MauEyeCare.API.Services;

/// <summary>Pushes AI job status updates to connected WPF clients in real time.</summary>
public class AiJobHub : Hub
{
    public async Task JoinImageGroup(string imageId) =>
        await Groups.AddToGroupAsync(Context.ConnectionId, $"image-{imageId}");
}

/// <summary>Prescription PDF generation using QuestPDF.</summary>
public interface IPrescriptionPdfService
{
    Task<string> GeneratePrescriptionAsync(Guid examId);
}

public class PrescriptionPdfService : IPrescriptionPdfService
{
    private readonly Data.AppDbContext _db;
    private readonly IWebHostEnvironment _env;
    private readonly ILogger<PrescriptionPdfService> _logger;

    public PrescriptionPdfService(Data.AppDbContext db, IWebHostEnvironment env, ILogger<PrescriptionPdfService> logger)
    {
        _db = db; _env = env; _logger = logger;
    }

    public async Task<string> GeneratePrescriptionAsync(Guid examId)
    {
        var exam = await _db.Exams
            .Include(e => e.Patient)
            .FirstOrDefaultAsync(e => e.ExamId == examId);

        if (exam is null) throw new ArgumentException("Exam not found");

        var outputDir = Path.Combine(_env.ContentRootPath, "Prescriptions");
        Directory.CreateDirectory(outputDir);
        var filePath = Path.Combine(outputDir, $"Rx_{examId:N}.pdf");

        // QuestPDF 2024 — Community license
        QuestPDF.Settings.License = LicenseType.Community;
        Document.Create(container =>
        {
            container.Page(page =>
            {
                page.Size(PageSizes.A4);
                page.Margin(1.5f, Unit.Centimetre);
                page.DefaultTextStyle(x => x.FontFamily("Arial").FontSize(10));

                page.Header().Column(col =>
                {
                    col.Item().Row(row =>
                    {
                        row.RelativeItem().Column(headerCol =>
                        {
                            headerCol.Item().Text("MauEyeCare SuperSpecialty Clinic").Bold().FontSize(18).FontColor("#1A2340");
                            headerCol.Item().Text("Dr. Danish Jawed,  (Ophthalmology)").FontSize(10).Italic().FontColor("#2A3F55");
                            headerCol.Item().Text("Reg No: 54321-OPHTH | Contact: +91 9235647410").FontSize(9).FontColor("#888888");
                        });
                        row.ConstantItem(80).Text("Rx").Bold().FontSize(32).FontColor("#00BFA5").AlignRight();
                    });
                    
                    col.Item().PaddingTop(6).LineHorizontal(1.5f).LineColor("#00BFA5");
                    
                    col.Item().PaddingTop(10).Background("#F4F7F9").Padding(10).Row(row =>
                    {
                        var dob = exam.Patient.DateOfBirth;
                        var age = DateTime.Today.Year - dob.Year;
                        if (dob > DateOnly.FromDateTime(DateTime.Today.AddYears(-age))) age--;
                        
                        row.RelativeItem().Column(c =>
                        {
                            c.Item().Text($"Patient Name: {exam.Patient.FirstName} {exam.Patient.LastName}").Bold();
                            c.Item().Text($"Age / Gender: {age} Years / {exam.Patient.Gender ?? "N/A"}");
                        });
                        row.RelativeItem().AlignRight().Column(c =>
                        {
                            c.Item().Text($"Patient ID: {exam.PatientId.ToString().Substring(0, 8).ToUpper()}");
                            c.Item().Text($"Date: {exam.ExamDate:dd-MM-yyyy}");
                        });
                    });
                    col.Item().PaddingTop(8).LineHorizontal(0.5f).LineColor("#CCCCCC");
                });

                page.Content().PaddingVertical(15).Column(col =>
                {
                    col.Item().Text("Refraction Details").Bold().FontSize(12).FontColor("#1A2340");
                    col.Item().PaddingTop(6).Table(table =>
                    {
                        table.ColumnsDefinition(cols =>
                        {
                            cols.ConstantColumn(80);
                            cols.RelativeColumn(); cols.RelativeColumn();
                            cols.RelativeColumn(); cols.RelativeColumn();
                        });

                        void HeaderCell(string text) => table.Cell().Background("#1A2340")
                            .Padding(6).Text(text).FontColor("#FFFFFF").Bold().FontSize(10);
                        void DataCell(string text) => table.Cell().BorderBottom(0.5f).BorderColor("#E0E0E0")
                            .Padding(6).Text(text).FontSize(10);

                        HeaderCell("Eye"); HeaderCell("Sphere (SPH)"); HeaderCell("Cylinder (CYL)");
                        HeaderCell("Axis"); HeaderCell("VA");

                        DataCell("OD (Right)");
                        DataCell(exam.OD_Sphere?.ToString("+0.00;-0.00;0.00") ?? "Plano");
                        DataCell(exam.OD_Cylinder?.ToString("+0.00;-0.00;0.00") ?? "-");
                        DataCell(exam.OD_Axis?.ToString() ?? "-");
                        DataCell(exam.OD_VA ?? "-");

                        DataCell("OS (Left)");
                        DataCell(exam.OS_Sphere?.ToString("+0.00;-0.00;0.00") ?? "Plano");
                        DataCell(exam.OS_Cylinder?.ToString("+0.00;-0.00;0.00") ?? "-");
                        DataCell(exam.OS_Axis?.ToString() ?? "-");
                        DataCell(exam.OS_VA ?? "-");
                    });

                    if (!string.IsNullOrEmpty(exam.Diagnosis))
                    {
                        col.Item().PaddingTop(15).Text("Diagnosis").Bold().FontSize(12).FontColor("#1A2340");
                        col.Item().PaddingTop(4).Text(exam.Diagnosis).FontSize(10);
                    }

                    if (!string.IsNullOrEmpty(exam.DoctorNotes))
                    {
                        col.Item().PaddingTop(15).Text("Clinical Findings & Prescriptions").Bold().FontSize(12).FontColor("#1A2340");
                        col.Item().PaddingTop(4).Text(exam.DoctorNotes).FontSize(10).LineHeight(1.2f);
                    }

                    col.Item().PaddingTop(20).Border(1).BorderColor("#00BFA5").Padding(10).Column(notes =>
                    {
                        notes.Item().Text("Usage & Compliance Instructions:").Bold().FontSize(10).FontColor("#1A2340");
                        notes.Item().PaddingTop(4).Text("• Take prescribed medications at exactly the mentioned intervals.").FontSize(10);
                        notes.Item().Text("• Wear corrective frames continuously as advised for optical adjustment.").FontSize(10);
                        notes.Item().Text("• Report immediately if experiencing sudden pain, blurring, or irritation.").FontSize(10);
                    });

                    col.Item().PaddingTop(15).Background("#FFF3CD").Padding(8).Column(warn =>
                    {
                        warn.Item().Text("⚠ AI Decision Support Disclaimer").Bold().FontSize(8).FontColor("#856404");
                        warn.Item().Text(
                            "Any AI-assisted suggestions in this document are for decision support only " +
                            "and do not constitute a medical diagnosis. Clinician review and override capability are mandatory.")
                            .FontSize(8).FontColor("#856404");
                    });

                    col.Item().PaddingTop(40).Row(row =>
                    {
                        row.RelativeItem().Column(c =>
                        {
                            c.Item().Text("Clinic Seal Space").FontSize(9).FontColor("#888888").Italic();
                            c.Item().PaddingTop(20).Border(0.5f).BorderColor("#CCCCCC").Width(100).Height(50);
                        });
                        row.RelativeItem().AlignRight().Column(c =>
                        {
                            c.Item().PaddingBottom(20).Text("Digitally Signed by").FontSize(9).FontColor("#2A3F55");
                            c.Item().Text("Dr. Maurice Eyecare").Bold().FontSize(11).FontColor("#1A2340");
                            c.Item().LineHorizontal(0.5f).LineColor("#1A2340");
                            c.Item().AlignRight().Text("Authorized Signatory").FontSize(9).FontColor("#888888");
                        });
                    });
                });

                page.Footer().AlignCenter().Text(txt =>
                {
                    txt.Span("MauEyeCare | ").FontSize(8).FontColor("#888888");
                    txt.CurrentPageNumber().FontSize(8);
                    txt.Span(" | Page — Secure Medical Document").FontSize(8).FontColor("#888888");
                });
            });
        }).GeneratePdf(filePath);

        _logger.LogInformation("Prescription PDF generated: {Path}", filePath);
        return filePath;
    }
}
