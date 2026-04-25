using MauEyeCare.API.Data;
using MauEyeCare.API.Middleware;
using MauEyeCare.API.Models;
using MauEyeCare.API.Services;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi.Models;
using Serilog;
using System.Text;

// ──────────────────────────────────────────────────────────────────────────────
// Bootstrap Serilog early so startup exceptions are captured
// ──────────────────────────────────────────────────────────────────────────────
Log.Logger = new LoggerConfiguration()
    .WriteTo.Console()
    .CreateBootstrapLogger();

try
{
    var builder = WebApplication.CreateBuilder(args);

    // ── Serilog ───────────────────────────────────────────────────────────────
    builder.Host.UseSerilog((ctx, lc) => lc
        .ReadFrom.Configuration(ctx.Configuration)
        .WriteTo.Console()
        .Enrich.FromLogContext()
        .Enrich.WithProperty("Application", "MauEyeCare.API"));

    // ── EF Core + SQLite ──────────────────────────────────────────────────────
    builder.Services.AddDbContext<AppDbContext>(options =>
        options.UseSqlite(
            builder.Configuration.GetConnectionString("DefaultConnection")));

    // ── ASP.NET Identity ─────────────────────────────────────────────────────
    builder.Services.AddIdentity<ApplicationUser, IdentityRole>(opts =>
    {
        opts.Password.RequireDigit = true;
        opts.Password.RequiredLength = 8;
        opts.Lockout.MaxFailedAccessAttempts = 5;
    })
    .AddEntityFrameworkStores<AppDbContext>()
    .AddDefaultTokenProviders();

    // ── JWT Authentication ────────────────────────────────────────────────────
    var jwtKey = builder.Configuration["Jwt:Key"]
        ?? throw new InvalidOperationException("Jwt:Key is not configured.");
    
    builder.Services.AddAuthentication(opts =>
    {
        opts.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
        opts.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
    })
    .AddJwtBearer(opts =>
    {
        opts.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtKey)),
            ClockSkew = TimeSpan.Zero
        };
    });

    builder.Services.ConfigureApplicationCookie(options =>
    {
        options.Events.OnRedirectToLogin = context =>
        {
            context.Response.StatusCode = Microsoft.AspNetCore.Http.StatusCodes.Status401Unauthorized;
            return Task.CompletedTask;
        };
    });

    builder.Services.AddAuthorization(opts =>
    {
        opts.AddPolicy("DoctorOrAdmin", p => p.RequireRole("Doctor", "Admin"));
        opts.AddPolicy("AdminOnly", p => p.RequireRole("Admin"));
        opts.AddPolicy("AnyStaff", p => p.RequireRole("Doctor", "Receptionist", "Technician", "Admin"));
    });

    // ── Application Services ──────────────────────────────────────────────────
    builder.Services.AddScoped<ITokenService, TokenService>();
    builder.Services.AddScoped<IPatientService, PatientService>();
    builder.Services.AddScoped<IAppointmentService, AppointmentService>();
    builder.Services.AddScoped<IExamService, ExamService>();
    builder.Services.AddScoped<IInventoryService, InventoryService>();
    builder.Services.AddScoped<IInvoiceService, InvoiceService>();
    builder.Services.AddScoped<IAiService, AiService>();
    builder.Services.AddScoped<IPrescriptionPdfService, PrescriptionPdfService>();
    builder.Services.AddHttpClient<IAiService, AiService>(c =>
        c.BaseAddress = new Uri(builder.Configuration["AiService:BaseUrl"] ?? "http://localhost:5050"));

    // ── CORS (for WPF client on same machine) ─────────────────────────────────
    builder.Services.AddCors(opts =>
        opts.AddPolicy("DesktopClient", p =>
            p.WithOrigins("https://localhost", "http://localhost")
             .AllowAnyMethod()
             .AllowAnyHeader()
             .AllowCredentials()));

    // ── SignalR ────────────────────────────────────────────────────────────────
    builder.Services.AddSignalR();

    // ── Controllers + Swagger ─────────────────────────────────────────────────
    builder.Services.AddControllers();
    builder.Services.AddEndpointsApiExplorer();
    builder.Services.AddSwaggerGen(c =>
    {
        c.SwaggerDoc("v1", new OpenApiInfo
        {
            Title = "MauEyeCare API",
            Version = "v1",
            Description = "Optometry Clinic Management System API"
        });
        c.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
        {
            In = ParameterLocation.Header,
            Description = "Enter JWT token",
            Name = "Authorization",
            Type = SecuritySchemeType.Http,
            BearerFormat = "JWT",
            Scheme = "bearer"
        });
        c.AddSecurityRequirement(new OpenApiSecurityRequirement
        {
            {
                new OpenApiSecurityScheme { Reference = new OpenApiReference
                    { Type = ReferenceType.SecurityScheme, Id = "Bearer" } },
                Array.Empty<string>()
            }
        });
    });

    // ── Build ─────────────────────────────────────────────────────────────────
    var app = builder.Build();

    // ── Auto-migrate on startup (dev convenience) ─────────────────────────────
    using (var scope = app.Services.CreateScope())
    {
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        db.Database.EnsureCreated();

        // Seed default admin user
        var userMgr = scope.ServiceProvider.GetRequiredService<UserManager<ApplicationUser>>();
        var roleMgr = scope.ServiceProvider.GetRequiredService<RoleManager<IdentityRole>>();
        // await SeedData.InitializeAsync(userMgr, roleMgr);
    }

    if (app.Environment.IsDevelopment())
    {
        app.UseSwagger();
        app.UseSwaggerUI(c => c.SwaggerEndpoint("/swagger/v1/swagger.json", "MauEyeCare API v1"));
    }

    // if (!app.Environment.IsDevelopment())
    // {
    //     app.UseHttpsRedirection();
    // }
    app.UseSerilogRequestLogging();
    app.UseCors("DesktopClient");
    app.UseAuthentication();
    app.UseAuthorization();
    app.UseMiddleware<AuditMiddleware>();

    app.MapControllers();
    app.MapHub<AiJobHub>("/hubs/aijob");

    // ────────────────────────────────────────────────────────────────────────────
    // Database Seeding
    // ────────────────────────────────────────────────────────────────────────────
    using (var scope = app.Services.CreateScope())
    {
        var context = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        var userManager = scope.ServiceProvider.GetRequiredService<UserManager<ApplicationUser>>();
        var roleManager = scope.ServiceProvider.GetRequiredService<RoleManager<IdentityRole>>();
        try
        {
            await MauEyeCare.API.Data.DatabaseSeeder.SeedDummyDataAsync(context, userManager, roleManager);
        }
        catch (Exception ex)
        {
            Log.Error(ex, "An error occurred seeding the DB.");
        }
    }

    app.Run();
}
catch (Exception ex)
{
    Log.Fatal(ex, "MauEyeCare API terminated unexpectedly");
}
finally
{
    Log.CloseAndFlush();
}
