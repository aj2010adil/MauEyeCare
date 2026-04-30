using MauEyeCare.API.Models;
using Microsoft.AspNetCore.Identity;

namespace MauEyeCare.API.Data;

public static class DatabaseSeeder
{
    public static async Task SeedDummyDataAsync(AppDbContext context, UserManager<ApplicationUser> userManager, RoleManager<IdentityRole> roleManager)
    {
        await context.Database.EnsureCreatedAsync();

        // Ensure roles exist
        string[] roles = ["Admin", "Doctor", "Receptionist", "Technician"];
        foreach (var role in roles)
        {
            if (!await roleManager.RoleExistsAsync(role))
                await roleManager.CreateAsync(new IdentityRole(role));
        }

        // 1. Core Users
        var doctor = await userManager.FindByEmailAsync("admin@maueyecare.com");
        if (doctor == null)
        {
            doctor = new ApplicationUser { UserName = "admin@maueyecare.com", Email = "admin@maueyecare.com", FirstName = "Clinical", LastName = "Director", Role = "Admin" };
            await userManager.CreateAsync(doctor, "Admin@12345");
        }

        if (!await userManager.IsInRoleAsync(doctor, "Admin"))
            await userManager.AddToRoleAsync(doctor, "Admin");
        if (!await userManager.IsInRoleAsync(doctor, "Doctor"))
            await userManager.AddToRoleAsync(doctor, "Doctor");

        if (context.Patients.Any() && context.Appointments.Any() && context.Staff.Any()) return;

        // 2. Run Bulk Seed
        await SeedBulkDataAsync(context, doctor.Id);
    }

    public static async Task SeedBulkDataAsync(AppDbContext context, string doctorId)
    {
        var random = new Random();
        var firstNames = new[] { "Arjun", "Deepak", "Sanjay", "Vikram", "Anjali", "Priya", "Neha", "Meera", "Rohan", "Amit", "Suresh", "Kiran", "Sunita", "Rajesh", "Vijay" };
        var lastNames = new[] { "Sharma", "Verma", "Gupta", "Patel", "Reddy", "Nair", "Iyer", "Khan", "Malhotra", "Singh", "Desai", "Joshi", "Kulkarni", "Chawla" };
        var conditions = new[] { "Normal", "Myopia", "Hyperopia", "Astigmatism", "Cataract", "Glaucoma Suspect", "Dry Eye Syndrome", "Conjunctivitis" };

        // 1. Seed Staff if empty
        if (!context.Staff.Any())
        {
            context.Staff.AddRange(
                new Staff { StaffId = Guid.NewGuid(), FirstName = "Clinical", LastName = "Director", Role = "Admin", Email = "admin@maueyecare.com", Specialization = "Ophthalmology" },
                new Staff { StaffId = Guid.NewGuid(), FirstName = "Sanjay", LastName = "Gupta", Role = "Doctor", Email = "sanjay.gupta@example.com", Specialization = "Optometry" },
                new Staff { StaffId = Guid.NewGuid(), FirstName = "Neha", LastName = "Patel", Role = "Receptionist", Email = "neha.patel@example.com" }
            );
        }

        var patients = new List<Patient>();
        if (!context.Patients.Any())
        {
            for (int i = 0; i < 1000; i++)
            {
                var p = new Patient
                {
                    PatientId = Guid.NewGuid(),
                    FirstName = firstNames[random.Next(firstNames.Length)],
                    LastName = lastNames[random.Next(lastNames.Length)],
                    DateOfBirth = new DateOnly(random.Next(1950, 2015), random.Next(1, 13), random.Next(1, 28)),
                    Gender = random.Next(2) == 0 ? "Male" : "Female",
                    Phone = "98" + random.Next(10000000, 99999999).ToString(),
                    Email = $"patient{i}@example.com",
                    Address = "Mumbai, Maharashtra",
                    CreatedAt = DateTime.UtcNow.AddDays(-random.Next(0, 730))
                };
                patients.Add(p);
            }
            context.Patients.AddRange(patients);
            await context.SaveChangesAsync();
        }
        else
        {
            patients = [.. context.Patients];
        }

        var exams = new List<Exam>();
        var appointments = new List<Appointment>();
        var clinicalImages = new List<ClinicalImage>();
        var invoices = new List<Invoice>();

        if (!context.Exams.Any() || !context.Appointments.Any())
        {
            foreach (var p in patients)
            {
                if (random.NextDouble() < 0.7)
                {
                    var isToday = random.Next(0, 5) == 0; 
                    var scheduledDate = isToday ? DateTime.UtcNow : p.CreatedAt.AddDays(random.Next(1, 10));

                    var exam = new Exam
                    {
                        ExamId = Guid.NewGuid(),
                        PatientId = p.PatientId,
                        DoctorUserId = doctorId,
                        ExamDate = scheduledDate,
                        Diagnosis = conditions[random.Next(conditions.Length)],
                        OD_Sphere = (decimal)(random.Next(-600, 400) / 100.0),
                        OS_Sphere = (decimal)(random.Next(-600, 400) / 100.0),
                        DoctorNotes = "Standard clinical examination performed. No acute distress."
                    };
                    exams.Add(exam);

                    appointments.Add(new Appointment
                    {
                        AppointmentId = Guid.NewGuid(),
                        PatientId = p.PatientId,
                        DoctorUserId = doctorId,
                        ScheduledAt = scheduledDate,
                        DurationMinutes = 30,
                        Status = scheduledDate < DateTime.UtcNow ? "Completed" : "Scheduled",
                        Notes = "Routine follow-up.",
                        AppointmentType = "Consultation"
                    });

                    if (random.NextDouble() < 0.3)
                    {
                        clinicalImages.Add(new ClinicalImage
                        {
                            ImageId = Guid.NewGuid(),
                            ExamId = exam.ExamId,
                            ImageType = "Fundus",
                            FilePath = "/images/fundus_sample.jpg",
                            AiStatus = "Completed"
                        });
                    }

                    if (random.NextDouble() < 0.5)
                    {
                        var total = (decimal)random.Next(500, 5000);
                        invoices.Add(new Invoice
                        {
                            InvoiceId = Guid.NewGuid(),
                            PatientId = p.PatientId,
                            InvoiceDate = DateOnly.FromDateTime(exam.ExamDate),
                            TotalAmount = total,
                            PaidAmount = random.NextDouble() > 0.3 ? total : 0,
                            Status = random.NextDouble() > 0.3 ? "Paid" : "Pending"
                        });
                    }
                }
            }
            if (!context.Exams.Any()) context.Exams.AddRange(exams);
            if (!context.Appointments.Any()) context.Appointments.AddRange(appointments);
            if (!context.Images.Any()) context.Images.AddRange(clinicalImages);
            if (!context.Invoices.Any()) context.Invoices.AddRange(invoices);
        }

        if (!context.InventoryItems.Any())
        {
            context.InventoryItems.AddRange(
                new InventoryItem { ItemId = Guid.NewGuid(), Name = "Standard Lens Cleanser", Category = "Care", Quantity = 100, ReorderLevel = 20, UnitPrice = 250 },
                new InventoryItem { ItemId = Guid.NewGuid(), Name = "Optical Frame - Titanium", Category = "Frames", Quantity = 25, ReorderLevel = 5, UnitPrice = 3500 }
            );
        }

        await context.SaveChangesAsync();
    }
}
