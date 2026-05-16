using MauEyeCare.API.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using MauEyeCare.API.Services;

namespace MauEyeCare.API.Controllers;

[ApiController]
[Route("api/v1/[controller]")]
[Produces("application/json")]
public class InventoryController : ControllerBase
{
    private readonly IInventoryService _inventory;

    public InventoryController(IInventoryService inventory) => _inventory = inventory;

    [HttpGet]
    [Authorize(Policy = "AnyStaff")]
    public async Task<ActionResult<IEnumerable<InventoryItemDto>>> GetInventory(
        [FromQuery] string? category, [FromQuery] bool? lowStockOnly)
        => Ok(await _inventory.GetAllAsync(category, lowStockOnly));

    [HttpGet("low-stock")]
    [Authorize(Policy = "AnyStaff")]
    public async Task<ActionResult<IEnumerable<InventoryItemDto>>> GetLowStock()
        => Ok(await _inventory.GetLowStockItemsAsync());

    [HttpPost]
    [Authorize(Policy = "AdminOnly")]
    public async Task<ActionResult<InventoryItemDto>> Create([FromBody] CreateInventoryItemRequest req)
    {
        var item = await _inventory.CreateAsync(req);
        return CreatedAtAction(nameof(GetItem), new { id = item.ItemId }, item);
    }

    [HttpGet("{id:guid}")]
    [Authorize(Policy = "AnyStaff")]
    public async Task<ActionResult<InventoryItemDto>> GetItem(Guid id)
    {
        var item = await _inventory.GetByIdAsync(id);
        return item is null ? NotFound() : Ok(item);
    }

    [HttpPut("{id:guid}/adjust")]
    [Authorize(Policy = "DoctorOrAdmin")]
    public async Task<ActionResult<InventoryItemDto>> Adjust(Guid id, [FromBody] AdjustQuantityRequest req)
    {
        var item = await _inventory.AdjustQuantityAsync(id, req);
        return item is null ? NotFound() : Ok(item);
    }

    [HttpDelete("{id:guid}")]
    [Authorize(Policy = "DoctorOrAdmin")]
    public async Task<ActionResult> Delete(Guid id)
    {
        var success = await _inventory.DeleteAsync(id);
        return success ? NoContent() : NotFound();
    }
}
