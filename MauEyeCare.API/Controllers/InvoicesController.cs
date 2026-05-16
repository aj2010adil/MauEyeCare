using MauEyeCare.API.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using MauEyeCare.API.Services;

namespace MauEyeCare.API.Controllers;

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
