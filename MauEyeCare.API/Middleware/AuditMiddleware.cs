using MauEyeCare.API.Models;
using Microsoft.AspNetCore.Http;
using System.Security.Claims;
using System.Text.Json;

namespace MauEyeCare.API.Middleware;

/// <summary>
/// Captures create/update/delete operations and writes to AuditLog.
/// </summary>
public class AuditMiddleware
{
    private readonly RequestDelegate _next;

    public AuditMiddleware(RequestDelegate next) => _next = next;

    public async Task InvokeAsync(HttpContext context, Data.AppDbContext db)
    {
        await _next(context);

        // Only audit state-changing requests
        if (context.Request.Method is "POST" or "PUT" or "PATCH" or "DELETE"
            && context.Response.StatusCode is >= 200 and < 300)
        {
            var userId = context.User?.FindFirstValue(ClaimTypes.NameIdentifier);
            var action = context.Request.Method;
            var path = context.Request.Path.Value ?? "";

            db.AuditLog.Add(new AuditEntry
            {
                UserId = userId,
                Action = action,
                EntityType = ExtractEntityType(path),
                EntityId = ExtractEntityId(path),
                IpAddress = context.Connection.RemoteIpAddress?.ToString(),
                Timestamp = DateTime.UtcNow
            });

            await db.SaveChangesAsync();
        }
    }

    private static string ExtractEntityType(string path)
    {
        var segments = path.Split('/', StringSplitOptions.RemoveEmptyEntries);
        return segments.Length >= 3 ? segments[2] : path;
    }

    private static string? ExtractEntityId(string path)
    {
        var segments = path.Split('/', StringSplitOptions.RemoveEmptyEntries);
        return segments.Length >= 4 ? segments[3] : null;
    }
}
