using MauEyeCare.API.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using MauEyeCare.API.Services;

namespace MauEyeCare.API.Controllers;

[ApiController]
[Route("api/v1/[controller]")]
public class AuthController : ControllerBase
{
    private readonly ITokenService _tokens;

    public AuthController(ITokenService tokens) => _tokens = tokens;

    [HttpPost("login")]
    [AllowAnonymous]
    public async Task<ActionResult<TokenResponse>> Login([FromBody] LoginRequest req)
    {
        var response = await _tokens.LoginAsync(req);
        return response is null ? Unauthorized(new { error = "Invalid credentials" }) : Ok(response);
    }
}
