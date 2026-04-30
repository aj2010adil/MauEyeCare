using MauEyeCare.API.Data;
using MauEyeCare.API.Models;
using Microsoft.EntityFrameworkCore;

namespace MauEyeCare.API.Services;

// ── DTOs ─────────────────────────────────────────────────────────────────────
public record AppointmentDto(
    Guid AppointmentId, Guid PatientId, string PatientName,
    string DoctorUserId, DateTime ScheduledAt, int DurationMinutes,
    string Status, string? Notes, string? AppointmentType, DateTime CreatedAt);

public record CreateAppointmentRequest(
    Guid PatientId, string DoctorUserId, DateTime ScheduledAt,
    int DurationMinutes, string? Notes, string? AppointmentType);

// ── Interface ─────────────────────────────────────────────────────────────────
public interface IAppointmentService
{
    Task<IEnumerable<AppointmentDto>> GetAppointmentsAsync(DateTime? from, DateTime? to, string? doctorUserId);
    Task<AppointmentDto?> GetByIdAsync(Guid id);
    Task<AppointmentDto> CreateAsync(CreateAppointmentRequest req);
    Task<bool> UpdateStatusAsync(Guid id, string status, string? notes);
    Task<bool> DeleteAsync(Guid id);
    Task<IEnumerable<AppointmentDto>> GetTodaysAppointmentsAsync();
}

// ── Implementation ────────────────────────────────────────────────────────────
public class AppointmentService : IAppointmentService
{
    private readonly AppDbContext _db;

    public AppointmentService(AppDbContext db) => _db = db;

    public async Task<IEnumerable<AppointmentDto>> GetAppointmentsAsync(
        DateTime? from, DateTime? to, string? doctorUserId)
    {
        var q = _db.Appointments.Include(a => a.Patient).AsQueryable();
        if (from.HasValue) q = q.Where(a => a.ScheduledAt >= from.Value);
        if (to.HasValue) q = q.Where(a => a.ScheduledAt <= to.Value);
        if (!string.IsNullOrEmpty(doctorUserId)) q = q.Where(a => a.DoctorUserId == doctorUserId);

        return await q.OrderBy(a => a.ScheduledAt).Select(a => MapToDto(a)).ToListAsync();
    }

    public async Task<AppointmentDto?> GetByIdAsync(Guid id)
    {
        var a = await _db.Appointments.Include(x => x.Patient).FirstOrDefaultAsync(x => x.AppointmentId == id);
        return a is null ? null : MapToDto(a);
    }

    public async Task<AppointmentDto> CreateAsync(CreateAppointmentRequest req)
    {
        // Check for slot conflicts
        var conflictExists = await _db.Appointments.AnyAsync(a =>
            a.DoctorUserId == req.DoctorUserId &&
            a.Status != "Cancelled" &&
            a.ScheduledAt < req.ScheduledAt.AddMinutes(req.DurationMinutes) &&
            a.ScheduledAt.AddMinutes(a.DurationMinutes) > req.ScheduledAt);

        if (conflictExists)
            throw new InvalidOperationException("Appointment slot conflicts with an existing booking.");

        var appt = new Appointment
        {
            PatientId = req.PatientId,
            DoctorUserId = req.DoctorUserId,
            ScheduledAt = req.ScheduledAt,
            DurationMinutes = req.DurationMinutes,
            Notes = req.Notes,
            AppointmentType = req.AppointmentType
        };

        _db.Appointments.Add(appt);
        await _db.SaveChangesAsync();

        await _db.Entry(appt).Reference(a => a.Patient).LoadAsync();
        return MapToDto(appt);
    }

    public async Task<bool> UpdateStatusAsync(Guid id, string status, string? notes)
    {
        var appt = await _db.Appointments.FindAsync(id);
        if (appt is null) return false;
        appt.Status = status;
        if (notes is not null) appt.Notes = notes;
        await _db.SaveChangesAsync();
        return true;
    }

    public async Task<bool> DeleteAsync(Guid id)
    {
        var appt = await _db.Appointments.FindAsync(id);
        if (appt is null) return false;
        _db.Appointments.Remove(appt);
        await _db.SaveChangesAsync();
        return true;
    }

    public async Task<IEnumerable<AppointmentDto>> GetTodaysAppointmentsAsync()
    {
        var today = DateTime.UtcNow.Date;
        return await _db.Appointments
            .Include(a => a.Patient)
            .Where(a => a.ScheduledAt.Date == today && a.Status != "Cancelled")
            .OrderBy(a => a.ScheduledAt)
            .Select(a => MapToDto(a))
            .ToListAsync();
    }

    private static AppointmentDto MapToDto(Appointment a) => new(
        a.AppointmentId, a.PatientId,
        $"{a.Patient?.FirstName} {a.Patient?.LastName}",
        a.DoctorUserId, a.ScheduledAt, a.DurationMinutes,
        a.Status, a.Notes, a.AppointmentType, a.CreatedAt);
}
