using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Configuration;
using MauEyeCare.Desktop.Services;
using MauEyeCare.Desktop.ViewModels;
using System.Windows;
using System.IO;
using System.Diagnostics;
using System.Net.Http;

namespace MauEyeCare.Desktop;

public partial class App : Application
{
    public static IServiceProvider Services { get; private set; } = null!;
    private Process? _apiProcess;
    private Process? _aiProcess;

    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);
        
        // Global exception handling
        AppDomain.CurrentDomain.UnhandledException += (s, ev) => Log("FATAL: " + ev.ExceptionObject);
        DispatcherUnhandledException += (s, ev) => { Log("DISPATCHER ERROR: " + ev.Exception); ev.Handled = false; };

        Log("Application Starting...");

        var config = new ConfigurationBuilder()
            .SetBasePath(AppDomain.CurrentDomain.BaseDirectory)
            .AddJsonFile("desktopsettings.json", optional: true)
            .Build();

        var services = new ServiceCollection();

        // Configuration
        services.AddSingleton<IConfiguration>(config);

        // HTTP Client
        services.AddHttpClient<IApiService, ApiService>(c =>
        {
            var baseUrl = config["ApiBaseUrl"] ?? "https://localhost:5001";
            c.BaseAddress = new Uri(baseUrl);
            c.DefaultRequestHeaders.Add("Accept", "application/json");
            Log($"Configured API BaseUrl: {baseUrl}");
        }).ConfigurePrimaryHttpMessageHandler(() => new HttpClientHandler
        {
            ServerCertificateCustomValidationCallback = (sender, cert, chain, sslPolicyErrors) => true
        });

        // Services
        services.AddSingleton<IAuthService, AuthService>();

        // ViewModels
        services.AddTransient<LoginViewModel>();
        services.AddTransient<MainViewModel>();
        services.AddTransient<DashboardViewModel>();
        services.AddTransient<PatientsViewModel>();
        services.AddTransient<AppointmentsViewModel>();
        services.AddTransient<ExaminationViewModel>();
        services.AddTransient<PrescriptionViewModel>();
        services.AddTransient<AiViewModel>();
        services.AddTransient<InventoryViewModel>();
        services.AddTransient<BillingViewModel>();
        services.AddTransient<ReportsViewModel>();
        services.AddTransient<SettingsViewModel>();
        services.AddTransient<ReleaseNotesViewModel>();

        Services = services.BuildServiceProvider();
        Log("DI Container built.");

        StartBackgroundServices();
    }

    private void StartBackgroundServices()
    {
        var baseDir = Path.GetDirectoryName(Environment.ProcessPath) ?? AppDomain.CurrentDomain.BaseDirectory;
        var logLines = new List<string> { "BaseDir: " + baseDir };
        
        // 1. Start API
        var apiExePath = Path.Combine(baseDir, "MauEyeCare.API.exe");
        if (!File.Exists(apiExePath))
        {
            apiExePath = Path.GetFullPath(Path.Combine(baseDir, "..", "..", "..", "..", "MauEyeCare.API", "bin", "Debug", "net8.0", "MauEyeCare.API.exe"));
        }
        logLines.Add("Resolved API Path: " + apiExePath + " (Exists: " + File.Exists(apiExePath) + ")");

        if (File.Exists(apiExePath))
        {
            _apiProcess = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = apiExePath,
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    WorkingDirectory = Path.GetDirectoryName(apiExePath)
                }
            };
            try 
            {
                _apiProcess.Start(); 
                var apiLogPath = Path.Combine(baseDir, "api_log.txt");
                
                // Use real-time logging for API
                Task.Run(() => {
                    try {
                        using var reader = _apiProcess.StandardOutput;
                        while (!reader.EndOfStream) {
                            var line = reader.ReadLine();
                            if (line != null) File.AppendAllText(apiLogPath, line + Environment.NewLine);
                        }
                    } catch { }
                });
                Task.Run(() => {
                    try {
                        using var reader = _apiProcess.StandardError;
                        while (!reader.EndOfStream) {
                            var line = reader.ReadLine();
                            if (line != null) File.AppendAllText(apiLogPath, "ERR: " + line + Environment.NewLine);
                        }
                    } catch { }
                });
                logLines.Add("API Started successfully."); 
            } 
            catch (Exception ex) { logLines.Add("API Start Failed: " + ex.Message); }
        }

        // 2. Start Python AI
        var aiPath = Path.Combine(baseDir, "MauEyeCare.AI", "app.py");
        if (!File.Exists(aiPath))
        {
            // Fallback for local dev
            aiPath = Path.GetFullPath(Path.Combine(baseDir, "..", "..", "..", "..", "MauEyeCare.AI", "app.py"));
        }
        logLines.Add("Resolved AI Path: " + aiPath + " (Exists: " + File.Exists(aiPath) + ")");

        if (File.Exists(aiPath))
        {
            _aiProcess = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = "python",
                    Arguments = $"\"{aiPath}\"",
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    WorkingDirectory = Path.GetDirectoryName(aiPath)
                }
            };
            try { _aiProcess.Start(); Log("AI Service Started successfully."); } 
            catch (Exception ex) { Log("AI Service Start Failed: " + ex.Message); }
        }

        try { File.WriteAllLines(Path.Combine(baseDir, "launcher_log.txt"), logLines); } catch { }
    }

    public void Log(string message)
    {
        try
        {
            var logPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "app_debug.log");
            File.AppendAllText(logPath, $"[{DateTime.Now:HH:mm:ss}] {message}\n");
        }
        catch { }
    }

    protected override void OnExit(ExitEventArgs e)
    {
        base.OnExit(e);
        Log("Application Exiting...");
        try
        {
            if (_apiProcess != null && !_apiProcess.HasExited)
                _apiProcess.Kill();
            
            if (_aiProcess != null && !_aiProcess.HasExited)
                _aiProcess.Kill();
        }
        catch { }
    }
}
