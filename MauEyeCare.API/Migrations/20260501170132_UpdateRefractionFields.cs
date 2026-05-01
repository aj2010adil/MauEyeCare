using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace MauEyeCare.API.Migrations
{
    /// <inheritdoc />
    public partial class UpdateRefractionFields : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.RenameColumn(
                name: "OS_VA",
                table: "Exams",
                newName: "WOG_OS_VA");

            migrationBuilder.RenameColumn(
                name: "OS_Sphere",
                table: "Exams",
                newName: "WOG_OS_Sphere");

            migrationBuilder.RenameColumn(
                name: "OS_IOP",
                table: "Exams",
                newName: "WOG_OS_IOP");

            migrationBuilder.RenameColumn(
                name: "OS_Cylinder",
                table: "Exams",
                newName: "WOG_OS_Cylinder");

            migrationBuilder.RenameColumn(
                name: "OS_Axis",
                table: "Exams",
                newName: "WOG_OS_Axis");

            migrationBuilder.RenameColumn(
                name: "OS_Add",
                table: "Exams",
                newName: "WOG_OS_Add");

            migrationBuilder.RenameColumn(
                name: "OD_VA",
                table: "Exams",
                newName: "WOG_OD_VA");

            migrationBuilder.RenameColumn(
                name: "OD_Sphere",
                table: "Exams",
                newName: "WOG_OD_Sphere");

            migrationBuilder.RenameColumn(
                name: "OD_IOP",
                table: "Exams",
                newName: "WOG_OD_IOP");

            migrationBuilder.RenameColumn(
                name: "OD_Cylinder",
                table: "Exams",
                newName: "WOG_OD_Cylinder");

            migrationBuilder.RenameColumn(
                name: "OD_Axis",
                table: "Exams",
                newName: "WOG_OD_Axis");

            migrationBuilder.RenameColumn(
                name: "OD_Add",
                table: "Exams",
                newName: "WOG_OD_Add");

            migrationBuilder.AddColumn<string>(
                name: "OD_PD",
                table: "Exams",
                type: "character varying(10)",
                maxLength: 10,
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "OS_PD",
                table: "Exams",
                type: "character varying(10)",
                maxLength: 10,
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "WG_OD_Add",
                table: "Exams",
                type: "character varying(10)",
                maxLength: 10,
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "WG_OD_Axis",
                table: "Exams",
                type: "integer",
                nullable: true);

            migrationBuilder.AddColumn<decimal>(
                name: "WG_OD_Cylinder",
                table: "Exams",
                type: "numeric(5,2)",
                nullable: true);

            migrationBuilder.AddColumn<decimal>(
                name: "WG_OD_IOP",
                table: "Exams",
                type: "numeric(5,1)",
                nullable: true);

            migrationBuilder.AddColumn<decimal>(
                name: "WG_OD_Sphere",
                table: "Exams",
                type: "numeric(5,2)",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "WG_OD_VA",
                table: "Exams",
                type: "character varying(10)",
                maxLength: 10,
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "WG_OS_Add",
                table: "Exams",
                type: "character varying(10)",
                maxLength: 10,
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "WG_OS_Axis",
                table: "Exams",
                type: "integer",
                nullable: true);

            migrationBuilder.AddColumn<decimal>(
                name: "WG_OS_Cylinder",
                table: "Exams",
                type: "numeric(5,2)",
                nullable: true);

            migrationBuilder.AddColumn<decimal>(
                name: "WG_OS_IOP",
                table: "Exams",
                type: "numeric(5,1)",
                nullable: true);

            migrationBuilder.AddColumn<decimal>(
                name: "WG_OS_Sphere",
                table: "Exams",
                type: "numeric(5,2)",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "WG_OS_VA",
                table: "Exams",
                type: "character varying(10)",
                maxLength: 10,
                nullable: true);

            migrationBuilder.CreateTable(
                name: "TrainingFeedbacks",
                columns: table => new
                {
                    FeedbackId = table.Column<Guid>(type: "uuid", nullable: false),
                    ImageId = table.Column<Guid>(type: "uuid", nullable: false),
                    CorrectLabel = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: false),
                    SubmittedBy = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: true),
                    SubmittedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_TrainingFeedbacks", x => x.FeedbackId);
                });
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "TrainingFeedbacks");

            migrationBuilder.DropColumn(
                name: "OD_PD",
                table: "Exams");

            migrationBuilder.DropColumn(
                name: "OS_PD",
                table: "Exams");

            migrationBuilder.DropColumn(
                name: "WG_OD_Add",
                table: "Exams");

            migrationBuilder.DropColumn(
                name: "WG_OD_Axis",
                table: "Exams");

            migrationBuilder.DropColumn(
                name: "WG_OD_Cylinder",
                table: "Exams");

            migrationBuilder.DropColumn(
                name: "WG_OD_IOP",
                table: "Exams");

            migrationBuilder.DropColumn(
                name: "WG_OD_Sphere",
                table: "Exams");

            migrationBuilder.DropColumn(
                name: "WG_OD_VA",
                table: "Exams");

            migrationBuilder.DropColumn(
                name: "WG_OS_Add",
                table: "Exams");

            migrationBuilder.DropColumn(
                name: "WG_OS_Axis",
                table: "Exams");

            migrationBuilder.DropColumn(
                name: "WG_OS_Cylinder",
                table: "Exams");

            migrationBuilder.DropColumn(
                name: "WG_OS_IOP",
                table: "Exams");

            migrationBuilder.DropColumn(
                name: "WG_OS_Sphere",
                table: "Exams");

            migrationBuilder.DropColumn(
                name: "WG_OS_VA",
                table: "Exams");

            migrationBuilder.RenameColumn(
                name: "WOG_OS_VA",
                table: "Exams",
                newName: "OS_VA");

            migrationBuilder.RenameColumn(
                name: "WOG_OS_Sphere",
                table: "Exams",
                newName: "OS_Sphere");

            migrationBuilder.RenameColumn(
                name: "WOG_OS_IOP",
                table: "Exams",
                newName: "OS_IOP");

            migrationBuilder.RenameColumn(
                name: "WOG_OS_Cylinder",
                table: "Exams",
                newName: "OS_Cylinder");

            migrationBuilder.RenameColumn(
                name: "WOG_OS_Axis",
                table: "Exams",
                newName: "OS_Axis");

            migrationBuilder.RenameColumn(
                name: "WOG_OS_Add",
                table: "Exams",
                newName: "OS_Add");

            migrationBuilder.RenameColumn(
                name: "WOG_OD_VA",
                table: "Exams",
                newName: "OD_VA");

            migrationBuilder.RenameColumn(
                name: "WOG_OD_Sphere",
                table: "Exams",
                newName: "OD_Sphere");

            migrationBuilder.RenameColumn(
                name: "WOG_OD_IOP",
                table: "Exams",
                newName: "OD_IOP");

            migrationBuilder.RenameColumn(
                name: "WOG_OD_Cylinder",
                table: "Exams",
                newName: "OD_Cylinder");

            migrationBuilder.RenameColumn(
                name: "WOG_OD_Axis",
                table: "Exams",
                newName: "OD_Axis");

            migrationBuilder.RenameColumn(
                name: "WOG_OD_Add",
                table: "Exams",
                newName: "OD_Add");
        }
    }
}
