using MauEyeCare.API.Data;
using MauEyeCare.API.Models;
using MauEyeCare.API.Services;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Moq;
using System.Security.Claims;
using Xunit;

namespace MauEyeCare.Tests;

// ── In-Memory DB factory ────────────────────────────────────────────────────
public class TestDbFactory
{
    public static AppDbContext CreateContext()
    {
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString())
            .Options;
        return new AppDbContext(options);
    }
}

public class PrescriptionPdfServiceTests
{
    [Fact]
    public async Task GeneratePrescription_ShouldCreatePdfFile()
    {
        using var db = TestDbFactory.CreateContext();
        
        var patient = new Patient {
            PatientId = Guid.NewGuid(),
            FirstName = "Jane",
            LastName = "Doe",
            DateOfBirth = new DateOnly(1985, 10, 10),
            Gender = "Female"
        };
        db.Patients.Add(patient);

        var exam = new Exam {
            ExamId = Guid.NewGuid(),
            PatientId = patient.PatientId,
            Patient = patient,
            ExamDate = DateTime.UtcNow,
            OD_Sphere = -2.50m,
            OD_Cylinder = -0.75m,
            OD_Axis = 180,
            OD_VA = "6/6",
            OS_Sphere = -2.25m,
            OS_Cylinder = -0.50m,
            OS_Axis = 165,
            OS_VA = "6/6",
            Diagnosis = "Bilateral Myopia with Astigmatism",
            DoctorNotes = "Wear corrective spectacles continuously. Follow-up in 6 months."
        };
        db.Exams.Add(exam);
        await db.SaveChangesAsync();

        var mockEnv = new Moq.Mock<Microsoft.AspNetCore.Hosting.IWebHostEnvironment>();
        mockEnv.Setup(m => m.ContentRootPath).Returns(System.IO.Path.GetTempPath());
        
        var logger = new Moq.Mock<ILogger<PrescriptionPdfService>>();
        var service = new PrescriptionPdfService(db, mockEnv.Object, logger.Object);

        var pdfPath = await service.GeneratePrescriptionAsync(exam.ExamId);

        Assert.True(System.IO.File.Exists(pdfPath));
        
        if (System.IO.File.Exists(pdfPath)) System.IO.File.Delete(pdfPath);
    }
}

// ── Patient Service Tests ───────────────────────────────────────────────────
public class PatientServiceTests
{
    [Fact]
    public async Task CreatePatient_ShouldPersistAndReturnDto()
    {
        using var db = TestDbFactory.CreateContext();
        var service = new PatientService(db);

        var req = new CreatePatientRequest(
            "Priya", "Sharma",
            new DateOnly(1990, 5, 15),
            "Female", "9876543210", "priya@example.com",
            "Mumbai, Maharashtra", null, null, null);

        var result = await service.CreatePatientAsync(req);

        Assert.NotEqual(Guid.Empty, result.PatientId);
        Assert.Equal("Priya", result.FirstName);
        Assert.Equal("Sharma", result.LastName);
        Assert.Equal("Female", result.Gender);
        Assert.Equal(1, await db.Patients.CountAsync());
    }

    [Fact]
    public async Task GetPatientById_ValidId_ReturnsPatient()
    {
        using var db = TestDbFactory.CreateContext();
        var service = new PatientService(db);
        var patient = await service.CreatePatientAsync(new("Raj", "Kumar", new DateOnly(1985, 1, 1),
            "Male", null, null, null, null, null, null));

        var result = await service.GetPatientByIdAsync(patient.PatientId);
        Assert.NotNull(result);
        Assert.Equal("Raj", result.FirstName);
    }

    [Fact]
    public async Task GetPatientById_InvalidId_ReturnsNull()
    {
        using var db = TestDbFactory.CreateContext();
        var service = new PatientService(db);

        var result = await service.GetPatientByIdAsync(Guid.NewGuid());
        Assert.Null(result);
    }

    [Fact]
    public async Task UpdatePatient_ValidData_UpdatesAndReturns()
    {
        using var db = TestDbFactory.CreateContext();
        var service = new PatientService(db);
        var patient = await service.CreatePatientAsync(new("Anita", "Singh", new DateOnly(1992, 3, 10),
            "Female", null, null, null, null, null, null));

        var updateReq = new UpdatePatientRequest("Anita Updated", "Singh", null, "111222333", null, null, null, null);
        var result = await service.UpdatePatientAsync(patient.PatientId, updateReq);

        Assert.NotNull(result);
        Assert.Equal("Anita Updated", result.FirstName);
        Assert.Equal("111222333", result.Phone);
    }

    [Fact]
    public async Task UpdatePatient_InvalidId_ReturnsNull()
    {
        using var db = TestDbFactory.CreateContext();
        var service = new PatientService(db);
        var updateReq = new UpdatePatientRequest("A", "B", null, null, null, null, null, null);
        
        var result = await service.UpdatePatientAsync(Guid.NewGuid(), updateReq);
        Assert.Null(result);
    }

    [Fact]
    public async Task GetPatients_SearchByName_ReturnsFilteredResults()
    {
        using var db = TestDbFactory.CreateContext();
        var service = new PatientService(db);

        await service.CreatePatientAsync(new("Raj", "Kumar", new DateOnly(1985, 1, 1), "Male", null, null, null, null, null, null));
        await service.CreatePatientAsync(new("Anita", "Singh", new DateOnly(1992, 3, 10), "Female", null, null, null, null, null, null));

        var result = await service.GetPatientsAsync("raj", 1, 10);

        Assert.Equal(1, result.TotalCount);
        Assert.Equal("Raj", result.Items.First().FirstName);
    }

    [Fact]
    public async Task DeletePatient_ShouldSoftDelete()
    {
        using var db = TestDbFactory.CreateContext();
        var service = new PatientService(db);

        var patient = await service.CreatePatientAsync(new("Test", "User", new DateOnly(2000, 1, 1), null, null, null, null, null, null, null));
        var deleted = await service.DeletePatientAsync(patient.PatientId);

        Assert.True(deleted);
        var allPatients = await service.GetPatientsAsync(null, 1, 10);
        Assert.Equal(0, allPatients.TotalCount);
    }
}

// ── Appointment Service Tests ───────────────────────────────────────────────
public class AppointmentServiceTests
{
    [Fact]
    public async Task CreateAppointment_WithConflict_ThrowsException()
    {
        using var db = TestDbFactory.CreateContext();
        var patient = new Patient { FirstName = "Test", LastName = "Patient", DateOfBirth = new DateOnly(1990, 1, 1) };
        db.Patients.Add(patient);
        await db.SaveChangesAsync();

        var service = new AppointmentService(db);
        var slotTime = DateTime.UtcNow.AddHours(1);
        const string doctorId = "doctor-123";

        await service.CreateAsync(new CreateAppointmentRequest(patient.PatientId, doctorId, slotTime, 30, null, null));

        await Assert.ThrowsAsync<InvalidOperationException>(() =>
            service.CreateAsync(new CreateAppointmentRequest(patient.PatientId, doctorId, slotTime.AddMinutes(10), 30, null, null)));
    }

    [Fact]
    public async Task GetAppointmentsAsync_DateRange_FiltersCorrectly()
    {
        using var db = TestDbFactory.CreateContext();
        var patient = new Patient { FirstName = "A", LastName = "B", DateOfBirth = new DateOnly(1990, 1, 1) };
        db.Patients.Add(patient);
        await db.SaveChangesAsync();

        var service = new AppointmentService(db);
        await service.CreateAsync(new CreateAppointmentRequest(patient.PatientId, "doc", DateTime.UtcNow.AddDays(1), 30, null, null));
        await service.CreateAsync(new CreateAppointmentRequest(patient.PatientId, "doc", DateTime.UtcNow.AddDays(3), 30, null, null));

        var res = await service.GetAppointmentsAsync(DateTime.UtcNow, DateTime.UtcNow.AddDays(2), "doc");
        Assert.Single(res);
    }

    [Fact]
    public async Task GetTodaysAppointmentsAsync_ReturnsOnlyToday()
    {
        using var db = TestDbFactory.CreateContext();
        var patient = new Patient { FirstName = "A", LastName = "B", DateOfBirth = new DateOnly(1990, 1, 1) };
        db.Patients.Add(patient);
        await db.SaveChangesAsync();

        var service = new AppointmentService(db);
        await service.CreateAsync(new CreateAppointmentRequest(patient.PatientId, "doc", DateTime.UtcNow.AddHours(2), 30, null, null));
        await service.CreateAsync(new CreateAppointmentRequest(patient.PatientId, "doc", DateTime.UtcNow.AddDays(2), 30, null, null));

        var res = await service.GetTodaysAppointmentsAsync();
        Assert.Single(res);
    }

    [Fact]
    public async Task DeleteAsync_ValidId_ReturnsTrue()
    {
        using var db = TestDbFactory.CreateContext();
        var patient = new Patient { FirstName = "A", LastName = "B", DateOfBirth = new DateOnly(1990, 1, 1) };
        db.Patients.Add(patient);
        await db.SaveChangesAsync();

        var service = new AppointmentService(db);
        var appt = await service.CreateAsync(new CreateAppointmentRequest(patient.PatientId, "doc", DateTime.UtcNow.AddHours(2), 30, null, null));
        
        var deleted = await service.DeleteAsync(appt.AppointmentId);
        Assert.True(deleted);
        
        var fetched = await service.GetByIdAsync(appt.AppointmentId);
        Assert.Null(fetched);
    }
}

// ── Inventory Service Tests ─────────────────────────────────────────────────
public class InventoryServiceTests
{
    [Fact]
    public async Task GetAllAsync_CategoryFilter_ReturnsFiltered()
    {
        using var db = TestDbFactory.CreateContext();
        var service = new InventoryService(db);
        await service.CreateAsync(new("Drops", "Medication", null, 10, 5, null, null, null, null));
        await service.CreateAsync(new("Frames", "Accessory", null, 10, 5, null, null, null, null));

        var meds = await service.GetAllAsync("Medication", null);
        Assert.Single(meds);
        Assert.Equal("Drops", meds.First().Name);
    }

    [Fact]
    public async Task AdjustQuantity_BelowZero_ClampedToZero()
    {
        using var db = TestDbFactory.CreateContext();
        var service = new InventoryService(db);

        var item = await service.CreateAsync(new CreateInventoryItemRequest("Eye Drops", "Medication", "SKU001", 3, 5, 150m, null, null, null));
        var result = await service.AdjustQuantityAsync(item.ItemId, new AdjustQuantityRequest(-10, "Used in exam"));

        Assert.Equal(0, result!.Quantity);
    }

    [Fact]
    public async Task GetLowStockItems_ReturnsOnlyBelowReorder()
    {
        using var db = TestDbFactory.CreateContext();
        var service = new InventoryService(db);

        await service.CreateAsync(new("Item A", null, null, 10, 5, null, null, null, null));
        await service.CreateAsync(new("Item B", null, null, 3, 5, null, null, null, null));

        var lowStock = await service.GetLowStockItemsAsync();
        Assert.Single(lowStock);
        Assert.Equal("Item B", lowStock.First().Name);
    }

    [Fact]
    public async Task DeleteAsync_ValidId_ReturnsTrue()
    {
        using var db = TestDbFactory.CreateContext();
        var service = new InventoryService(db);
        var item = await service.CreateAsync(new("Item A", null, null, 10, 5, null, null, null, null));
        
        var deleted = await service.DeleteAsync(item.ItemId);
        Assert.True(deleted);

        var fetched = await service.GetByIdAsync(item.ItemId);
        Assert.Null(fetched);
    }
}

// ── Invoice Service Tests ───────────────────────────────────────────────────
public class InvoiceServiceTests
{
    [Fact]
    public async Task CreateAsync_CalculatesTotalCorrectly()
    {
        using var db = TestDbFactory.CreateContext();
        var patient = new Patient { FirstName = "Inv", LastName = "User", DateOfBirth = new DateOnly(1990, 1, 1) };
        db.Patients.Add(patient);
        await db.SaveChangesAsync();

        var service = new InvoiceService(db);
        var req = new CreateInvoiceRequest(patient.PatientId, null, DateOnly.FromDateTime(DateTime.UtcNow), null, null, new[]
        {
            new CreateLineItemRequest("Consultation", 1, 500m, "Service"),
            new CreateLineItemRequest("Glasses", 2, 1000m, "Product")
        });

        var invoice = await service.CreateAsync(req);
        Assert.Equal(2500m, invoice.TotalAmount); // 1*500 + 2*1000
    }

    [Fact]
    public async Task GetByPatientAsync_ReturnsPatientInvoices()
    {
        using var db = TestDbFactory.CreateContext();
        var patient = new Patient { FirstName = "Inv", LastName = "User", DateOfBirth = new DateOnly(1990, 1, 1) };
        db.Patients.Add(patient);
        await db.SaveChangesAsync();

        var service = new InvoiceService(db);
        var req = new CreateInvoiceRequest(patient.PatientId, null, DateOnly.FromDateTime(DateTime.UtcNow), null, null, new[]
        {
            new CreateLineItemRequest("Consultation", 1, 500m, "Service"),
        });

        await service.CreateAsync(req);

        var invoices = await service.GetByPatientAsync(patient.PatientId);
        Assert.Single(invoices);
    }

    [Fact]
    public async Task MarkPaidAsync_PartialPayment_SetsStatusPartial()
    {
        using var db = TestDbFactory.CreateContext();
        var patient = new Patient { FirstName = "Inv", LastName = "User", DateOfBirth = new DateOnly(1990, 1, 1) };
        db.Patients.Add(patient);
        await db.SaveChangesAsync();

        var service = new InvoiceService(db);
        var req = new CreateInvoiceRequest(patient.PatientId, null, DateOnly.FromDateTime(DateTime.UtcNow), null, null, new[]
        {
            new CreateLineItemRequest("Consultation", 1, 500m, "Service"),
        });

        var invoice = await service.CreateAsync(req);
        await service.MarkPaidAsync(invoice.InvoiceId, 200m, "Cash");

        var updated = await service.GetByIdAsync(invoice.InvoiceId);
        Assert.Equal("Partial", updated!.Status);
        Assert.Equal(200m, updated.PaidAmount);
    }

    [Fact]
    public async Task MarkPaidAsync_FullPayment_SetsStatusPaid()
    {
        using var db = TestDbFactory.CreateContext();
        var patient = new Patient { FirstName = "Inv", LastName = "User", DateOfBirth = new DateOnly(1990, 1, 1) };
        db.Patients.Add(patient);
        await db.SaveChangesAsync();

        var service = new InvoiceService(db);
        var req = new CreateInvoiceRequest(patient.PatientId, null, DateOnly.FromDateTime(DateTime.UtcNow), null, null, new[]
        {
            new CreateLineItemRequest("Consultation", 1, 500m, "Service"),
        });

        var invoice = await service.CreateAsync(req);
        await service.MarkPaidAsync(invoice.InvoiceId, 500m, "Card");

        var updated = await service.GetByIdAsync(invoice.InvoiceId);
        Assert.Equal("Paid", updated!.Status);
    }
}

// ── Exam Service Tests ──────────────────────────────────────────────────────
public class ExamServiceTests
{
    [Fact]
    public async Task CreateExam_PersistsExam()
    {
        using var db = TestDbFactory.CreateContext();
        var patient = new Patient { FirstName = "Exam", LastName = "User", DateOfBirth = new DateOnly(1990, 1, 1) };
        db.Patients.Add(patient);
        await db.SaveChangesAsync();

        var service = new ExamService(db);
        var req = new CreateExamRequest(patient.PatientId, null, "doc1", DateTime.UtcNow, null, null, null, null, null, null, null, null, null, null, null, null, null, null, "Diagnosis", "Notes");
        var exam = await service.CreateAsync(req);

        Assert.NotEqual(Guid.Empty, exam.ExamId);
        Assert.Equal("Diagnosis", exam.Diagnosis);
    }

    [Fact]
    public async Task GetByPatientAsync_ReturnsExams()
    {
        using var db = TestDbFactory.CreateContext();
        var patient = new Patient { FirstName = "Exam", LastName = "User", DateOfBirth = new DateOnly(1990, 1, 1) };
        db.Patients.Add(patient);
        await db.SaveChangesAsync();

        var service = new ExamService(db);
        var req = new CreateExamRequest(patient.PatientId, null, "doc1", DateTime.UtcNow, null, null, null, null, null, null, null, null, null, null, null, null, null, null, "Diagnosis", "Notes");
        await service.CreateAsync(req);

        var exams = await service.GetByPatientAsync(patient.PatientId);
        Assert.Single(exams);
    }

    [Fact]
    public async Task UpdateNotesAsync_ValidId_UpdatesNotes()
    {
        using var db = TestDbFactory.CreateContext();
        var patient = new Patient { FirstName = "Exam", LastName = "User", DateOfBirth = new DateOnly(1990, 1, 1) };
        db.Patients.Add(patient);
        await db.SaveChangesAsync();

        var service = new ExamService(db);
        var req = new CreateExamRequest(patient.PatientId, null, "doc1", DateTime.UtcNow, null, null, null, null, null, null, null, null, null, null, null, null, null, null, "Old", "Old");
        var exam = await service.CreateAsync(req);

        var success = await service.UpdateNotesAsync(exam.ExamId, "NewNotes", "NewDiag");
        Assert.True(success);

        var fetched = await service.GetByIdAsync(exam.ExamId);
        Assert.Equal("NewNotes", fetched!.DoctorNotes);
        Assert.Equal("NewDiag", fetched.Diagnosis);
    }
}

// ── Token Service Tests ─────────────────────────────────────────────────────
public class TokenServiceTests
{
    private IConfiguration GetInMemoryConfig()
    {
        var inMemorySettings = new Dictionary<string, string?> {
            {"Jwt:Key", "SuperSecretKeyThatIsAtLeast32BytesLongForHS256"},
            {"Jwt:Issuer", "TestIssuer"},
            {"Jwt:Audience", "TestAudience"},
            {"Jwt:AccessTokenExpiryMinutes", "15"}
        };
        return new ConfigurationBuilder()
            .AddInMemoryCollection(inMemorySettings)
            .Build();
    }

    [Fact]
    public async Task LoginAsync_InvalidCredentials_ReturnsNull()
    {
        var config = GetInMemoryConfig();

        var store = new Mock<IUserStore<ApplicationUser>>();
        var userMgrMock = new Mock<UserManager<ApplicationUser>>(store.Object, null!, null!, null!, null!, null!, null!, null!, null!);
        userMgrMock.Setup(x => x.FindByEmailAsync(It.IsAny<string>())).ReturnsAsync((ApplicationUser?)null);

        var loggerMock = new Mock<ILogger<TokenService>>();

        var service = new TokenService(config, userMgrMock.Object, loggerMock.Object);

        var response = await service.LoginAsync(new LoginRequest("fake@example.com", "wrong"));
        Assert.Null(response);
    }

    [Fact]
    public async Task LoginAsync_ValidCredentials_ReturnsToken()
    {
        var config = GetInMemoryConfig();

        var store = new Mock<IUserStore<ApplicationUser>>();
        var userMgrMock = new Mock<UserManager<ApplicationUser>>(store.Object, null!, null!, null!, null!, null!, null!, null!, null!);

        var fakeUser = new ApplicationUser { Id = "test-123", Email = "doc@example.com", FirstName = "Doc", LastName = "Tor" };

        userMgrMock.Setup(x => x.FindByEmailAsync("doc@example.com")).ReturnsAsync(fakeUser);
        userMgrMock.Setup(x => x.CheckPasswordAsync(fakeUser, "correct")).ReturnsAsync(true);
        userMgrMock.Setup(x => x.GetRolesAsync(fakeUser)).ReturnsAsync(new List<string> { "Doctor" });

        var loggerMock = new Mock<ILogger<TokenService>>();

        var service = new TokenService(config, userMgrMock.Object, loggerMock.Object);

        var response = await service.LoginAsync(new LoginRequest("doc@example.com", "correct"));
        
        Assert.NotNull(response);
        Assert.NotNull(response!.AccessToken);
        Assert.NotNull(response.RefreshToken);
        Assert.Equal("Doctor", response.Role);
    }
}
