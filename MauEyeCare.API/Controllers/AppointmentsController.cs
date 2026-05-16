using MauEyeCare.API.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using MauEyeCare.API.Services;

namespace MauEyeCare.API.Controllers;

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
