using MauEyeCare.API.Data;
using MauEyeCare.API.Models;
using Microsoft.EntityFrameworkCore;

namespace MauEyeCare.API.Services;

// ── DTOs ─────────────────────────────────────────────────────────────────────
public record InventoryItemDto(
    Guid ItemId, string Name, string? Category, string? SKU, int Quantity,
    int ReorderLevel, decimal? UnitPrice, DateOnly? ExpiryDate,
    string? Manufacturer, string? BatchNumber, bool IsLowStock);

public record CreateInventoryItemRequest(
    string Name, string? Category, string? SKU, int Quantity, int ReorderLevel,
    decimal? UnitPrice, DateOnly? ExpiryDate, string? Manufacturer, string? BatchNumber);

public record AdjustQuantityRequest(int Delta, string Reason);

// ── Invoice DTOs ──────────────────────────────────────────────────────────────
public record InvoiceDto(
    Guid InvoiceId, Guid PatientId, string PatientName, DateOnly InvoiceDate,
    decimal TotalAmount, decimal PaidAmount, string Status, string? PaymentMethod,
    IEnumerable<InvoiceLineItemDto> LineItems, DateTime CreatedAt);

public record InvoiceLineItemDto(
    Guid LineItemId, string? Description, int Quantity, decimal UnitPrice, decimal Total, string? Category);

public record CreateInvoiceRequest(
    Guid PatientId, Guid? AppointmentId, DateOnly InvoiceDate,
    string? GstNumber, string? PaymentMethod, IEnumerable<CreateLineItemRequest> LineItems);

public record CreateLineItemRequest(
    string? Description, int Quantity, decimal UnitPrice, string? Category);

// ── Inventory Interface ───────────────────────────────────────────────────────
public interface IInventoryService
{
    Task<IEnumerable<InventoryItemDto>> GetAllAsync(string? category, bool? lowStockOnly);
    Task<InventoryItemDto?> GetByIdAsync(Guid id);
    Task<InventoryItemDto> CreateAsync(CreateInventoryItemRequest req);
    Task<InventoryItemDto?> AdjustQuantityAsync(Guid id, AdjustQuantityRequest req);
    Task<IEnumerable<InventoryItemDto>> GetLowStockItemsAsync();
    Task<bool> DeleteAsync(Guid id);
}

// ── Invoice Interface ─────────────────────────────────────────────────────────
public interface IInvoiceService
{
    Task<IEnumerable<InvoiceDto>> GetByPatientAsync(Guid patientId);
    Task<InvoiceDto?> GetByIdAsync(Guid id);
    Task<InvoiceDto> CreateAsync(CreateInvoiceRequest req);
    Task<bool> MarkPaidAsync(Guid id, decimal amount, string paymentMethod);
}

// ── Inventory Implementation ──────────────────────────────────────────────────
public class InventoryService : IInventoryService
{
    private readonly AppDbContext _db;
    public InventoryService(AppDbContext db) => _db = db;

    public async Task<IEnumerable<InventoryItemDto>> GetAllAsync(string? category, bool? lowStockOnly)
    {
        var q = _db.InventoryItems.AsQueryable();
        if (!string.IsNullOrEmpty(category)) q = q.Where(i => i.Category == category);
        if (lowStockOnly == true) q = q.Where(i => i.Quantity <= i.ReorderLevel);
        return await q.OrderBy(i => i.Name).Select(i => MapToDto(i)).ToListAsync();
    }

    public async Task<InventoryItemDto?> GetByIdAsync(Guid id)
    {
        var item = await _db.InventoryItems.FindAsync(id);
        return item is null ? null : MapToDto(item);
    }

    public async Task<InventoryItemDto> CreateAsync(CreateInventoryItemRequest req)
    {
        var item = new InventoryItem
        {
            Name = req.Name, Category = req.Category, SKU = req.SKU,
            Quantity = req.Quantity, ReorderLevel = req.ReorderLevel,
            UnitPrice = req.UnitPrice, ExpiryDate = req.ExpiryDate,
            Manufacturer = req.Manufacturer, BatchNumber = req.BatchNumber
        };
        _db.InventoryItems.Add(item);
        await _db.SaveChangesAsync();
        return MapToDto(item);
    }

    public async Task<InventoryItemDto?> AdjustQuantityAsync(Guid id, AdjustQuantityRequest req)
    {
        var item = await _db.InventoryItems.FindAsync(id);
        if (item is null) return null;
        item.Quantity = Math.Max(0, item.Quantity + req.Delta);
        item.UpdatedAt = DateTime.UtcNow;
        await _db.SaveChangesAsync();
        return MapToDto(item);
    }

    public async Task<IEnumerable<InventoryItemDto>> GetLowStockItemsAsync() =>
        await _db.InventoryItems
            .Where(i => i.Quantity <= i.ReorderLevel)
            .Select(i => MapToDto(i))
            .ToListAsync();

    public async Task<bool> DeleteAsync(Guid id)
    {
        var item = await _db.InventoryItems.FindAsync(id);
        if (item is null) return false;
        _db.InventoryItems.Remove(item);
        await _db.SaveChangesAsync();
        return true;
    }

    private static InventoryItemDto MapToDto(InventoryItem i) => new(
        i.ItemId, i.Name, i.Category, i.SKU, i.Quantity, i.ReorderLevel,
        i.UnitPrice, i.ExpiryDate, i.Manufacturer, i.BatchNumber,
        i.Quantity <= i.ReorderLevel);
}

// ── Invoice Implementation ────────────────────────────────────────────────────
public class InvoiceService : IInvoiceService
{
    private readonly AppDbContext _db;
    public InvoiceService(AppDbContext db) => _db = db;

    public async Task<IEnumerable<InvoiceDto>> GetByPatientAsync(Guid patientId) =>
        await _db.Invoices
            .Include(i => i.Patient)
            .Include(i => i.LineItems)
            .Where(i => i.PatientId == patientId)
            .OrderByDescending(i => i.CreatedAt)
            .Select(i => MapToDto(i))
            .ToListAsync();

    public async Task<InvoiceDto?> GetByIdAsync(Guid id)
    {
        var inv = await _db.Invoices
            .Include(i => i.Patient)
            .Include(i => i.LineItems)
            .FirstOrDefaultAsync(i => i.InvoiceId == id);
        return inv is null ? null : MapToDto(inv);
    }

    public async Task<InvoiceDto> CreateAsync(CreateInvoiceRequest req)
    {
        var lineItems = req.LineItems.Select(li => new InvoiceLineItem
        {
            Description = li.Description,
            Quantity = li.Quantity,
            UnitPrice = li.UnitPrice,
            Total = li.Quantity * li.UnitPrice,
            Category = li.Category
        }).ToList();

        var invoice = new Invoice
        {
            PatientId = req.PatientId,
            AppointmentId = req.AppointmentId,
            InvoiceDate = req.InvoiceDate,
            TotalAmount = lineItems.Sum(li => li.Total),
            GstNumber = req.GstNumber,
            PaymentMethod = req.PaymentMethod,
            LineItems = lineItems
        };

        _db.Invoices.Add(invoice);
        await _db.SaveChangesAsync();
        await _db.Entry(invoice).Reference(i => i.Patient).LoadAsync();
        return MapToDto(invoice);
    }

    public async Task<bool> MarkPaidAsync(Guid id, decimal amount, string paymentMethod)
    {
        var inv = await _db.Invoices.FindAsync(id);
        if (inv is null) return false;
        inv.PaidAmount += amount;
        inv.PaymentMethod = paymentMethod;
        inv.Status = inv.PaidAmount >= inv.TotalAmount ? "Paid" : "Partial";
        await _db.SaveChangesAsync();
        return true;
    }

    private static InvoiceDto MapToDto(Invoice i) => new(
        i.InvoiceId, i.PatientId,
        $"{i.Patient?.FirstName} {i.Patient?.LastName}",
        i.InvoiceDate, i.TotalAmount, i.PaidAmount, i.Status, i.PaymentMethod,
        i.LineItems.Select(li => new InvoiceLineItemDto(
            li.LineItemId, li.Description, li.Quantity, li.UnitPrice, li.Total, li.Category)),
        i.CreatedAt);
}
