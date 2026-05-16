using MauEyeCare.API.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using MauEyeCare.API.Services;
using MauEyeCare.API.Data;
using Microsoft.EntityFrameworkCore;

namespace MauEyeCare.API.Controllers;

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
