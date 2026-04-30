using MauEyeCare.API.Models;
using Microsoft.AspNetCore.Identity;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;

namespace MauEyeCare.API.Services;

// ── Token DTOs ────────────────────────────────────────────────────────────────
public record LoginRequest(string Email, string Password);
public record TokenResponse(string AccessToken, string RefreshToken, DateTime ExpiresAt, string UserId, string Role);

// ── Token Service ─────────────────────────────────────────────────────────────
public interface ITokenService
{
    Task<TokenResponse?> LoginAsync(LoginRequest req);
    string GenerateAccessToken(ApplicationUser user, IList<string> roles);
    string GenerateRefreshToken();
}

public class TokenService : ITokenService
{
    private readonly IConfiguration _cfg;
    private readonly UserManager<ApplicationUser> _userMgr;
    private readonly ILogger<TokenService> _logger;

    public TokenService(IConfiguration cfg, UserManager<ApplicationUser> userMgr, ILogger<TokenService> logger)
    {
        _cfg = cfg; _userMgr = userMgr; _logger = logger;
    }

    public async Task<TokenResponse?> LoginAsync(LoginRequest req)
    {
        var user = await _userMgr.FindByEmailAsync(req.Email);
        if (user is null || !await _userMgr.CheckPasswordAsync(user, req.Password))
        {
            _logger.LogWarning("Failed login attempt for {Email}", req.Email);
            return null;
        }

        var roles = await _userMgr.GetRolesAsync(user);
        var accessToken = GenerateAccessToken(user, roles);
        var refreshToken = GenerateRefreshToken();

        // In production, persist refreshToken to DB with expiry
        var expiry = DateTime.UtcNow.AddMinutes(
            _cfg.GetValue<int>("Jwt:AccessTokenExpiryMinutes", 15));

        return new TokenResponse(accessToken, refreshToken, expiry, user.Id, roles.FirstOrDefault() ?? "User");
    }

    public string GenerateAccessToken(ApplicationUser user, IList<string> roles)
    {
        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_cfg["Jwt:Key"]!));
        var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

        var claims = new List<Claim>
        {
            new(JwtRegisteredClaimNames.Sub, user.Id),
            new(JwtRegisteredClaimNames.Email, user.Email ?? ""),
            new(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString()),
            new(ClaimTypes.Name, $"{user.FirstName} {user.LastName}"),
        };
        claims.AddRange(roles.Select(r => new Claim(ClaimTypes.Role, r)));

        var token = new JwtSecurityToken(
            issuer: _cfg["Jwt:Issuer"],
            audience: _cfg["Jwt:Audience"],
            claims: claims,
            expires: DateTime.UtcNow.AddMinutes(_cfg.GetValue<int>("Jwt:AccessTokenExpiryMinutes", 15)),
            signingCredentials: creds);

        return new JwtSecurityTokenHandler().WriteToken(token);
    }

    public string GenerateRefreshToken()
    {
        var bytes = new byte[64];
        RandomNumberGenerator.Fill(bytes);
        return Convert.ToBase64String(bytes);
    }
}

// ── Seed Data ─────────────────────────────────────────────────────────────────
public static class SeedData
{
    public static async Task InitializeAsync(
        UserManager<ApplicationUser> userMgr,
        RoleManager<IdentityRole> roleMgr)
    {
        string[] roles = ["Admin", "Doctor", "Receptionist", "Technician"];
        foreach (var role in roles)
        {
            if (!await roleMgr.RoleExistsAsync(role))
                await roleMgr.CreateAsync(new IdentityRole(role));
        }

        // Default admin
        const string adminEmail = "admin@maueyecare.com";
        if (await userMgr.FindByEmailAsync(adminEmail) is null)
        {
            var admin = new ApplicationUser
            {
                UserName = adminEmail,
                Email = adminEmail,
                FirstName = "Clinic",
                LastName = "Admin",
                Role = "Admin",
                EmailConfirmed = true
            };
            var result = await userMgr.CreateAsync(admin, "Admin@12345");
            if (result.Succeeded)
                await userMgr.AddToRoleAsync(admin, "Admin");
        }

        // Default doctor
        const string doctorEmail = "doctor@maueyecare.com";
        if (await userMgr.FindByEmailAsync(doctorEmail) is null)
        {
            var doctor = new ApplicationUser
            {
                UserName = doctorEmail,
                Email = doctorEmail,
                FirstName = "Dr. Anil",
                LastName = "Sharma",
                Role = "Doctor",
                EmailConfirmed = true
            };
            var result = await userMgr.CreateAsync(doctor, "Doctor@12345");
            if (result.Succeeded)
                await userMgr.AddToRoleAsync(doctor, "Doctor");
        }
    }
}
