using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;
using MauEyeCare.API.Models;

namespace MauEyeCare.API.Data;

public class AppDbContext : IdentityDbContext<ApplicationUser>
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<Patient> Patients { get; set; } = null!;
    public DbSet<Staff> Staff { get; set; } = null!;
    public DbSet<Appointment> Appointments { get; set; } = null!;
    public DbSet<Exam> Exams { get; set; } = null!;
    public DbSet<ClinicalImage> Images { get; set; } = null!;
    public DbSet<AiResult> AiResults { get; set; } = null!;
    public DbSet<Invoice> Invoices { get; set; } = null!;
    public DbSet<InvoiceLineItem> InvoiceLineItems { get; set; } = null!;
    public DbSet<InventoryItem> InventoryItems { get; set; } = null!;
    public DbSet<AuditEntry> AuditLog { get; set; } = null!;

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Patient
        modelBuilder.Entity<Patient>(e =>
        {
            e.HasKey(x => x.PatientId);
            e.HasMany(x => x.Appointments).WithOne(x => x.Patient).HasForeignKey(x => x.PatientId);
            e.HasMany(x => x.Exams).WithOne(x => x.Patient).HasForeignKey(x => x.PatientId);
        });

        // Appointment
        modelBuilder.Entity<Appointment>(e =>
        {
            e.HasKey(x => x.AppointmentId);
            e.Property(x => x.Status).HasDefaultValue("Scheduled");
        });

        // Exam
        modelBuilder.Entity<Exam>(e =>
        {
            e.HasKey(x => x.ExamId);
            e.HasMany(x => x.Images).WithOne(x => x.Exam).HasForeignKey(x => x.ExamId);
        });

        // ClinicalImage
        modelBuilder.Entity<ClinicalImage>(e =>
        {
            e.HasKey(x => x.ImageId);
            e.Property(x => x.AiStatus).HasDefaultValue("Pending");
        });

        // AiResult
        modelBuilder.Entity<AiResult>(e =>
        {
            e.HasKey(x => x.ResultId);
        });

        // Invoice
        modelBuilder.Entity<Invoice>(e =>
        {
            e.HasKey(x => x.InvoiceId);
            e.HasMany(x => x.LineItems).WithOne(x => x.Invoice).HasForeignKey(x => x.InvoiceId);
        });

        // InvoiceLineItem
        modelBuilder.Entity<InvoiceLineItem>(e =>
        {
            e.HasKey(x => x.LineItemId);
        });

        // InventoryItem
        modelBuilder.Entity<InventoryItem>(e =>
        {
            e.HasKey(x => x.ItemId);
        });

        // AuditLog
        modelBuilder.Entity<AuditEntry>(e =>
        {
            e.HasKey(x => x.AuditId);
            e.Property(x => x.AuditId).ValueGeneratedOnAdd();
            e.ToTable("AuditLog");
        });
    }
}
