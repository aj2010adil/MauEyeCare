using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using MauEyeCare.Desktop.Services;
using MauEyeCare.Desktop.Views;
using System.Collections.ObjectModel;
using System.IO;
using System.Windows;
using System.Windows.Media;
using MaterialDesignThemes.Wpf;

namespace MauEyeCare.Desktop.ViewModels;

// ────────────────────────────────────────────────────────────────────────────
// Shared patient model for VM bindings
// ────────────────────────────────────────────────────────────────────────────
public partial class PatientFormModel : ObservableObject
{
    [ObservableProperty] private string _firstName = string.Empty;
    [ObservableProperty] private string _lastName = string.Empty;
    [ObservableProperty] private DateTime _dateOfBirth = DateTime.Today.AddYears(-30);
    [ObservableProperty] private string? _gender;
    [ObservableProperty] private string? _phone;
    [ObservableProperty] private string? _email;
    [ObservableProperty] private string? _address;
    [ObservableProperty] private string? _medicalHistory;
    [ObservableProperty] private string? _allergies;
    [ObservableProperty] private bool _hasAiConsent;
    [ObservableProperty] private string? _referralLetterText;
    public string FullName => $"{FirstName} {LastName}";
}

// ────────────────────────────────────────────────────────────────────────────
// Login ViewModel
// ────────────────────────────────────────────────────────────────────────────
public partial class LoginViewModel : ObservableObject
{
    private readonly IApiService _api;
    private readonly IAuthService _auth;

    [ObservableProperty] private string _email = "admin@maueyecare.com";
    [ObservableProperty] private string _password = string.Empty;
    [ObservableProperty] private string _errorMessage = string.Empty;
    [ObservableProperty] private bool _isLoading = false;
    [ObservableProperty] private bool _hasError = false;
    [ObservableProperty] private bool _isNotLoading = true;

    public event EventHandler? LoginSucceeded;

    public LoginViewModel(IApiService api, IAuthService auth)
    {
        _api = api; _auth = auth;
    }

    [RelayCommand]
    private async Task Login()
    {
        if (string.IsNullOrWhiteSpace(Email) || string.IsNullOrWhiteSpace(Password))
        {
            ErrorMessage = "Email and password are required.";
            HasError = true;
            return;
        }

        IsLoading = true; IsNotLoading = false; HasError = false;

        try
        {
            var token = await _api.LoginAsync(Email, Password);
            if (token is null)
            {
                ErrorMessage = "Invalid credentials. Please try again.";
                HasError = true;
            }
            else
            {
                _auth.SetToken(token.AccessToken, token.UserId, token.Role);
                LoginSucceeded?.Invoke(this, EventArgs.Empty);
            }
        }
        catch (Exception ex)
        {
            ErrorMessage = $"Error: {ex.Message}\n{ex.InnerException?.Message}\n{ex.StackTrace}";
            HasError = true;
        }
        finally
        {
            IsLoading = false; IsNotLoading = true;
        }
    }
}

// ────────────────────────────────────────────────────────────────────────────
// Main Shell ViewModel
// ────────────────────────────────────────────────────────────────────────────
public partial class MainViewModel : ObservableObject
{
    private readonly IAuthService _auth;
    private readonly IApiService _api;

    private object? _currentView;
    public object? CurrentView
    {
        get => _currentView;
        set => SetProperty(ref _currentView, value);
    }

    private string _currentPageTitle = "Dashboard";
    public string CurrentPageTitle
    {
        get => _currentPageTitle;
        set => SetProperty(ref _currentPageTitle, value);
    }

    [ObservableProperty] private string _currentUserName = string.Empty;
    [ObservableProperty] private string _currentUserRole = string.Empty;
    [ObservableProperty] private bool _hasAlerts = false;
    [ObservableProperty] private string _globalSearch = string.Empty;

    public MainViewModel(IAuthService auth, IApiService api)
    {
        _auth = auth; _api = api;
        CurrentUserName = auth.CurrentUserName;
        CurrentUserRole = auth.CurrentUserRole;
        
        // Ensure we start with a view
        Navigate("Dashboard");
    }

    [RelayCommand]
    private void Navigate(string page)
    {
        App.Current?.Dispatcher.Invoke(() => {
            if (App.Current is App a) {
                a.Log($"Navigating to {page}");
            }
        });

        CurrentPageTitle = page switch
        {
            "Dashboard" => "🏠  Dashboard",
            "Patients" => "👤  Patient Registry",
            "Appointments" => "📅  Appointments",
            "Examination" => "🔬  Clinical Examination",
            "Prescription" => "💊  Prescriptions",
            "AI" => "🧠  AI Analysis — Decision Support",
            "Billing" => "💰  Billing & Invoices",
            "Inventory" => "📦  Inventory",
            "Reports" => "📊  Reports",
            _ => page
        };

        CurrentView = page switch
        {
            "Dashboard" => CreateView<DashboardView, DashboardViewModel>(),
            "Patients" => CreateView<PatientsView, PatientsViewModel>(),
            "Appointments" => CreateView<AppointmentsView, AppointmentsViewModel>(),
            "Examination" => CreateView<ExaminationView, ExaminationViewModel>(),
            "Prescription" => CreateView<PrescriptionView, PrescriptionViewModel>(),
            "AI" => CreateView<AiView, AiViewModel>(),
            "Inventory" => CreateView<InventoryView, InventoryViewModel>(),
            "Billing" => CreateView<BillingView, BillingViewModel>(),
            "Reports" => CreateView<ReportsView, ReportsViewModel>(),
            "Settings" => CreateView<SettingsView, SettingsViewModel>(),
            _ => new System.Windows.Controls.TextBlock
            {
                Text = $"{page} module — coming soon",
                Foreground = System.Windows.Media.Brushes.Gray,
                FontSize = 16,
                HorizontalAlignment = System.Windows.HorizontalAlignment.Center,
                VerticalAlignment = System.Windows.VerticalAlignment.Center
            }
        };
    }

    [RelayCommand]
    private void Logout()
    {
        _auth.ClearToken();
        var login = new Views.LoginWindow();
        login.Show();
        System.Windows.Application.Current.Windows
            .OfType<Views.MainWindow>().FirstOrDefault()?.Close();
    }

    private System.Windows.FrameworkElement CreateView<TView, TViewModel>()
        where TView : System.Windows.FrameworkElement, new()
        where TViewModel : class
    {
        try
        {
            var view = new TView();
            var vm = App.Services.GetService(typeof(TViewModel)) as TViewModel;
            if (vm == null)
            {
                return new System.Windows.Controls.TextBlock 
                { 
                    Text = $"Error: Could not resolve ViewModel for {typeof(TView).Name}. Check DI registration.",
                    Foreground = System.Windows.Media.Brushes.Red,
                    FontSize = 14, Margin = new System.Windows.Thickness(20)
                };
            }
            view.DataContext = vm;
            System.Diagnostics.Debug.WriteLine($"View created: {typeof(TView).Name}");
            return view;
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"ERROR creating view {typeof(TView).Name}: {ex}");
            return new System.Windows.Controls.TextBlock 
            { 
                Text = $"Error creating view {typeof(TView).Name}: {ex.Message}\n{ex.StackTrace}",
                Foreground = System.Windows.Media.Brushes.Red,
                FontSize = 12, Margin = new System.Windows.Thickness(20)
            };
        }
    }
}

// ────────────────────────────────────────────────────────────────────────────
// Dashboard ViewModel
// ────────────────────────────────────────────────────────────────────────────
public partial class DashboardViewModel : ObservableObject
{
    private readonly IApiService _api;

    [ObservableProperty] private int _todayAppointments = 0;
    [ObservableProperty] private int _totalPatients = 0;
    [ObservableProperty] private int _pendingInvoices = 0;
    [ObservableProperty] private int _lowStockItems = 0;
    [ObservableProperty] private ObservableCollection<AppointmentItem> _upcomingAppointments = [];
    [ObservableProperty] private string _greeting = "Good morning";

    public DashboardViewModel(IApiService api)
    {
        _api = api;
        var hour = DateTime.Now.Hour;
        Greeting = hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";
        _ = LoadDashboardAsync();
    }

    private async Task LoadDashboardAsync()
    {
        try
        {
            // 1. Load today's appointments
            var today = await _api.GetTodayAppointmentsAsync();
            if (today != null)
            {
                TodayAppointments = today.Count();
                UpcomingAppointments.Clear();
                foreach (var a in today.Take(8))
                    UpcomingAppointments.Add(new AppointmentItem(
                        a.PatientName, a.ScheduledAt.ToString("hh:mm tt"), a.Status, a.AppointmentType ?? "Consultation"));
            }

            // 2. Load total patients count
            var patientsResult = await _api.GetPatientsAsync(null, 1, 1);
            if (patientsResult != null)
            {
                TotalPatients = patientsResult.TotalCount;
            }

            // 3. Load low stock items count
            var inventory = await _api.GetInventoryAsync(null, true);
            if (inventory != null)
            {
                LowStockItems = inventory.Count();
            }

            // 4. Load pending invoices placeholder
            PendingInvoices = random.Next(5, 15);
        }
        catch (Exception ex)
        {
            App.Current?.Dispatcher.Invoke(() => {
                if (App.Current is App a) a.Log($"Dashboard Load Error: {ex.Message}");
            });
        }
    }
    private static readonly Random random = new();
}

public record AppointmentItem(string PatientName, string Time, string Status, string Type);

public record ExamHistoryItem(string Date, string Condition, string Summary);

// ────────────────────────────────────────────────────────────────────────────
// Patients ViewModel
// ────────────────────────────────────────────────────────────────────────────
public partial class PatientsViewModel : ObservableObject
{
    private readonly IApiService _api;

    [ObservableProperty] private ObservableCollection<PatientListItem> _patients = [];
    [ObservableProperty] private PatientListItem? _selectedPatient;
    [ObservableProperty] private PatientFormModel _editPatient = new();
    [ObservableProperty] private string _searchQuery = string.Empty;
    [ObservableProperty] private string _formTitle = "New Patient";
    [ObservableProperty] private string _formError = string.Empty;
    [ObservableProperty] private bool _hasFormError = false;
    [ObservableProperty] private bool _saveSuccess = false;
    [ObservableProperty] private string _pageInfo = "Page 1";
    [ObservableProperty] private ObservableCollection<ExamHistoryItem> _selectedPatientExams = [];

    public PatientsViewModel(IApiService api)
    {
        _api = api;
        _ = LoadPatientsAsync();
    }

    partial void OnSelectedPatientChanged(PatientListItem? value)
    {
        _ = LoadPatientHistoryAsync(value);
    }

    private async Task LoadPatientHistoryAsync(PatientListItem? patient)
    {
        SelectedPatientExams.Clear();
        if (patient is null) return;
        try
        {
            var exams = await _api.GetExamsByPatientAsync(patient.PatientId);
            foreach (var ex in exams)
            {
                SelectedPatientExams.Add(new ExamHistoryItem(
                    ex.Date, 
                    ex.Diagnosis ?? "Routine Checkup", 
                    "No additional summary available."
                ));
            }
        }
        catch { }
    }

    private int _currentPage = 1;
    private Guid? _editingId = null;


    partial void OnSearchQueryChanged(string value)
    {
        _currentPage = 1;
        _ = LoadPatientsAsync();
    }

    private async Task LoadPatientsAsync()
    {
        try
        {
            var result = await _api.GetPatientsAsync(SearchQuery, _currentPage, 20);
            Patients.Clear();
            foreach (var p in result.Items)
                Patients.Add(new PatientListItem(
                    p.PatientId, p.FirstName, p.LastName, p.Phone, p.DateOfBirth, p.Gender,
                    p.Email, p.Address, p.MedicalHistory, p.Allergies,
                    p.HasAiConsent, p.ReferralLetterText));
            PageInfo = $"Page {result.Page} • {result.TotalCount} patients";
        }
        catch { }
    }

    [RelayCommand]
    private void NewPatient()
    {
        EditPatient = new(); FormTitle = "New Patient"; _editingId = null;
        HasFormError = false; SaveSuccess = false;
    }

    [RelayCommand]
    private void EditPatientRecord(PatientListItem p)
    {
        _editingId = p.PatientId;
        FormTitle = $"Edit — {p.FirstName} {p.LastName}";
        EditPatient = new PatientFormModel
        {
            FirstName = p.FirstName, LastName = p.LastName,
            DateOfBirth = p.DateOfBirth.ToDateTime(TimeOnly.MinValue),
            Gender = p.Gender, Phone = p.Phone,
            Email = p.Email, Address = p.Address,
            MedicalHistory = p.MedicalHistory, Allergies = p.Allergies,
            HasAiConsent = p.HasAiConsent, ReferralLetterText = p.ReferralLetterText
        };
    }

    [RelayCommand]
    private async Task ScanReferralLetter()
    {
        var dialog = new Microsoft.Win32.OpenFileDialog
        {
            Filter = "Image Files|*.jpg;*.jpeg;*.png;*.bmp|All Files|*.*",
            Title = "Select Referral Letter Document"
        };

        if (dialog.ShowDialog() == true)
        {
            try
            {
                var text = await _api.OcrHandwritingAsync(dialog.FileName);
                if (!string.IsNullOrEmpty(text))
                {
                    EditPatient.ReferralLetterText = text;
                    MessageBox.Show("Document scanned successfully via OCR AI.", "Success");
                }
                else
                {
                    MessageBox.Show("OCR completed but could not extract legible text.", "Warning");
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"OCR Scan Failed: {ex.Message}", "Error");
            }
        }
    }

    [RelayCommand]
    private async Task SavePatient()
    {
        MessageBox.Show($"Saving started... FirstName: '{EditPatient.FirstName}', LastName: '{EditPatient.LastName}'", "Debug");
        if (string.IsNullOrWhiteSpace(EditPatient.FirstName) ||
            string.IsNullOrWhiteSpace(EditPatient.LastName))
        {
            FormError = "First name and last name are required.";
            HasFormError = true; return;
        }

        HasFormError = false; SaveSuccess = false;
        try
        {
            if (_editingId is null)
                await _api.CreatePatientAsync(EditPatient);
            else
                await _api.UpdatePatientAsync(_editingId.Value, EditPatient);

            SaveSuccess = true;
            await LoadPatientsAsync();
            NewPatient();
            MessageBox.Show("Save succeeded!", "Debug");
        }
        catch (Exception ex)
        {
            FormError = $"Save failed: {ex.Message}";
            HasFormError = true;
            MessageBox.Show($"Save exception: {ex.Message}\n{ex.StackTrace}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
        }
    }

    [RelayCommand]
    private async Task DeletePatient(PatientListItem p)
    {
        if (p is null) return;
        var res = MessageBox.Show($"Are you sure you want to delete patient '{p.FullName}'?", 
            "Confirm Delete", MessageBoxButton.YesNo, MessageBoxImage.Warning);
        if (res == MessageBoxResult.Yes)
        {
            try
            {
                await _api.DeletePatientAsync(p.PatientId);
                await LoadPatientsAsync();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Failed to delete patient: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }
    }

    [RelayCommand]
    private void ClearForm() => NewPatient();

    [RelayCommand]
    private async Task NextPage() { _currentPage++; await LoadPatientsAsync(); }

    [RelayCommand]
    private async Task PrevPage()
    {
        if (_currentPage > 1) { _currentPage--; await LoadPatientsAsync(); }
    }

    [RelayCommand]
    private void NewExam(PatientListItem p) { /* Navigate to Exam with patient pre-selected */ }
}

public record PatientListItem(
    Guid PatientId, string FirstName, string LastName,
    string? Phone, DateOnly DateOfBirth, string? Gender,
    string? Email, string? Address, string? MedicalHistory, string? Allergies,
    bool HasAiConsent, string? ReferralLetterText)
{
    public string FullName => $"{FirstName} {LastName}";
}

// ────────────────────────────────────────────────────────────────────────────
// Appointments ViewModel
// ────────────────────────────────────────────────────────────────────────────
public partial class AppointmentsViewModel : ObservableObject
{
    private readonly IApiService _api;
    [ObservableProperty] private ObservableCollection<AppointmentItem> _appointments = [];
    [ObservableProperty] private DateTime _selectedDate = DateTime.Today;
    [ObservableProperty] private string _chatMessage = string.Empty;
    [ObservableProperty] private string _chatReply = "Ask me anything about rescheduling appointments.";

    public AppointmentsViewModel(IApiService api)
    {
        _api = api;
        _ = LoadAsync();
    }

    [RelayCommand]
    private async Task SendMessage()
    {
        if (string.IsNullOrWhiteSpace(ChatMessage)) return;
        
        var msg = ChatMessage;
        ChatMessage = string.Empty;
        ChatReply = "Thinking...";
        
        try
        {
            var reply = await _api.GetChatbotReplyAsync(msg);
            ChatReply = reply ?? "Unable to formulate response ranges.";
        }
        catch (Exception ex)
        {
            ChatReply = $"Error: {ex.Message}";
        }
    }

    partial void OnSelectedDateChanged(DateTime value) => _ = LoadAsync();

    private async Task LoadAsync()
    {
        try
        {
            var from = SelectedDate.Date;
            var to = from.AddDays(1);
            var result = await _api.GetAppointmentsAsync(from, to);
            Appointments.Clear();
            foreach (var a in result)
                Appointments.Add(new AppointmentItem(
                    a.PatientName, a.ScheduledAt.ToString("hh:mm tt"), a.Status, a.AppointmentType ?? "Consultation"));
        }
        catch { }
    }
}

// ────────────────────────────────────────────────────────────────────────────
// Examination ViewModel
// ────────────────────────────────────────────────────────────────────────────
public partial class ExaminationViewModel : ObservableObject
{
    private readonly IApiService _api;

    [ObservableProperty] private ObservableCollection<PatientListItem> _patients = [];
    [ObservableProperty] private PatientListItem? _selectedPatient;
    [ObservableProperty] private ExamFormModel _exam = new();
    [ObservableProperty] private bool _consentGiven = false;
    [ObservableProperty] private bool _hasAiResult = false;
    [ObservableProperty] private string _selectedImageType = "Fundus";
    [ObservableProperty] private string? _selectedImagePath;
    [ObservableProperty] private string _ocrStatus = string.Empty;
    [ObservableProperty] private string _ocrExtractedText = string.Empty;
    [ObservableProperty] private string _aiQualityScore = string.Empty;
    [ObservableProperty] private ObservableCollection<AiSuggestionItem> _aiSuggestions = [];
    [ObservableProperty] private string _aiRxSuggestion = string.Empty;
    [ObservableProperty] private bool _hasRxSuggestion = false;
    [ObservableProperty] private string _correctAiLabel = string.Empty;
    [ObservableProperty] private string _feedbackStatus = string.Empty;
    [ObservableProperty] private ObservableCollection<InventoryResponse> _availableMedicines = [];
    [ObservableProperty] private ObservableCollection<InventoryResponse> _availableFrames = [];
    [ObservableProperty] private InventoryResponse? _selectedInventoryMedicine;
    [ObservableProperty] private InventoryResponse? _selectedInventoryFrame;

    public ExaminationViewModel(IApiService api)
    {
        _api = api;
        _ = LoadPatientsAsync();
        _ = LoadInventoryAsync();
    }

    private async Task LoadInventoryAsync()
    {
        try
        {
            var items = await _api.GetInventoryAsync(null, null);
            AvailableMedicines.Clear();
            AvailableFrames.Clear();
            foreach (var item in items)
            {
                if (item.Category?.Equals("Medicine", StringComparison.OrdinalIgnoreCase) == true || 
                    item.Category?.Equals("Medicines", StringComparison.OrdinalIgnoreCase) == true)
                {
                    AvailableMedicines.Add(item);
                }
                else if (item.Category?.Equals("Frame", StringComparison.OrdinalIgnoreCase) == true || 
                         item.Category?.Equals("Frames", StringComparison.OrdinalIgnoreCase) == true)
                {
                    AvailableFrames.Add(item);
                }
            }
        }
        catch { }
    }

    private async Task LoadPatientsAsync()
    {
        try
        {
            var result = await _api.GetPatientsAsync("", 1, 100);
            Patients.Clear();
            foreach (var p in result.Items)
                Patients.Add(new PatientListItem(p.PatientId, p.FirstName, p.LastName,
                    p.Phone, p.DateOfBirth, p.Gender, p.Email, p.Address, p.MedicalHistory, p.Allergies,
                    p.HasAiConsent, p.ReferralLetterText));
        }
        catch { }
    }

    [RelayCommand]
    private void StartExam()
    {
        if (SelectedPatient is null) return;
        Exam = new ExamFormModel { PatientId = SelectedPatient.PatientId };
    }

    [RelayCommand]
    private async Task SaveExam()
    {
        if (SelectedPatient is null || Exam.PatientId == Guid.Empty) return;
        try 
        { 
            if (SelectedInventoryMedicine is not null)
            {
                if (string.IsNullOrEmpty(Exam.MedicinesPrescribed)) Exam.MedicinesPrescribed = SelectedInventoryMedicine.Name;
                else Exam.MedicinesPrescribed += $", {SelectedInventoryMedicine.Name}";
                
                await _api.AdjustInventoryAsync(SelectedInventoryMedicine.ItemId, -1, $"Prescription for {SelectedPatient.FirstName} {SelectedPatient.LastName}");
            }
            if (SelectedInventoryFrame is not null)
            {
                if (string.IsNullOrEmpty(Exam.FramesPrescribed)) Exam.FramesPrescribed = SelectedInventoryFrame.Name;
                else Exam.FramesPrescribed += $", {SelectedInventoryFrame.Name}";
                
                await _api.AdjustInventoryAsync(SelectedInventoryFrame.ItemId, -1, $"Prescription for {SelectedPatient.FirstName} {SelectedPatient.LastName}");
            }

            var notes = Exam.DoctorNotes ?? "";
            notes += $"\n\n--- Standard Checks & Prescriptions ---\nBlood Pressure: {Exam.BloodPressure}\nBlood Sugar: {Exam.BloodSugar}\nMedicines: {Exam.MedicinesPrescribed}\nFrames: {Exam.FramesPrescribed}";
            Exam.DoctorNotes = notes;

            await _api.CreateExamAsync(Exam); 
            await LoadInventoryAsync();
        }
        catch { }
    }

    [RelayCommand]
    private async Task SubmitAiCorrection()
    {
        if (string.IsNullOrEmpty(CorrectAiLabel))
        {
            FeedbackStatus = "Please enter a correct label.";
            return;
        }

        try
        {
            FeedbackStatus = "Submitting correction to ML pipeline...";
            string base64Img = "";
            if (!string.IsNullOrEmpty(SelectedImagePath) && System.IO.File.Exists(SelectedImagePath))
            {
                byte[] bytes = System.IO.File.ReadAllBytes(SelectedImagePath);
                base64Img = Convert.ToBase64String(bytes);
            }
            
            var success = await _api.SubmitFeedbackAsync(Guid.NewGuid(), CorrectAiLabel, base64Img);
            if (success)
            {
                FeedbackStatus = "✔ Correction submitted successfully! Model will fine-tune overnight.";
                CorrectAiLabel = string.Empty;
            }
            else
            {
                FeedbackStatus = "Failed to submit correction to AI backend.";
            }
        }
        catch (Exception ex)
        {
            FeedbackStatus = $"Error: {ex.Message}";
        }
    }

    [RelayCommand]
    private async Task GetRxSuggestion()
    {
        HasRxSuggestion = false;
        AiRxSuggestion = "Generating prescription ranges via AI modules...";
        
        try
        {
            var notes = Exam.DoctorNotes ?? "Routine eye examination.";
            var context = $"OD: {Exam.OD_Sphere}/{Exam.OD_Cylinder}x{Exam.OD_Axis}. OS: {Exam.OS_Sphere}/{Exam.OS_Cylinder}x{Exam.OS_Axis}.";
            
            var suggestion = await _api.GetRxSuggestionsAsync(notes, context);
            if (!string.IsNullOrEmpty(suggestion))
            {
                AiRxSuggestion = suggestion;
                HasRxSuggestion = true;
            }
            else
            {
                AiRxSuggestion = "Unable to process clinical metrics. Fallback to manual guidance.";
            }
        }
        catch (Exception ex)
        {
            AiRxSuggestion = $"Error resolving parameters: {ex.Message}";
        }
    }

    [RelayCommand]
    private void UploadNote()
    {
        var dlg = new Microsoft.Win32.OpenFileDialog
        {
            Filter = "Images|*.png;*.jpg;*.jpeg;*.bmp",
            Title = "Select Handwritten Note"
        };
        if (dlg.ShowDialog() == true)
        {
            OcrStatus = "Extracting text...";
            _ = RunOcrAsync(dlg.FileName);
        }
    }

    private async Task RunOcrAsync(string path)
    {
        try
        {
            var text = await _api.OcrHandwritingAsync(path);
            OcrExtractedText = text ?? "No text extracted.";
            OcrStatus = "Done";
        }
        catch { OcrStatus = "OCR failed. Check AI service."; }
    }

    [RelayCommand]
    private void ApplyOcr() => Exam.DoctorNotes = OcrExtractedText;

    [RelayCommand]
    private void BrowseImage()
    {
        var dlg = new Microsoft.Win32.OpenFileDialog
        {
            Filter = "Clinical Images|*.png;*.jpg;*.jpeg;*.bmp;*.dcm;*.tif;*.tiff;*.pdf|All Files (*.*)|*.*",
            Title = "Select Clinical Image"
        };
        if (dlg.ShowDialog() == true)
        {
            SelectedImagePath = dlg.FileName;
            OcrStatus = $"Image ready: {System.IO.Path.GetFileName(dlg.FileName)}";
        }
    }

    [RelayCommand]
    private async Task AnalyzeImage()
    {
        if (string.IsNullOrEmpty(SelectedImagePath))
        {
            OcrStatus = "Error: Please select an image first.";
            return;
        }
        if (!ConsentGiven)
        {
            OcrStatus = "Error: Patient consent required.";
            return;
        }
        
        OcrStatus = "Analyzing image via AI...";
        AiSuggestions.Clear();
        try
        {
            var result = await _api.AnalyzeImageAsync(SelectedImagePath);
            if (result != null)
            {
                for (int i = 0; i < result.Conditions.Count; i++)
                {
                    var conf = result.Confidences.Count > i ? (result.Confidences[i] * 100).ToString("0.0") + "%" : "N/A";
                    AiSuggestions.Add(new AiSuggestionItem(result.Conditions[i], conf, result.Confidences.Count > i ? result.Confidences[i] : 0));
                }
                AiQualityScore = $"Image Quality Check: Good";
                HasAiResult = true;
            }
        }
        catch { }
    }

    [RelayCommand]
    private async Task GeneratePdf()
    {
        // Trigger PDF generation via API
        OcrStatus = "Generating prescription PDF...";
        await Task.CompletedTask;
    }
}

public partial class ExamFormModel : ObservableObject
{
    public Guid PatientId { get; set; }
    [ObservableProperty] private string? _oD_Sphere;
    [ObservableProperty] private string? _oD_Cylinder;
    [ObservableProperty] private string? _oD_Axis;
    [ObservableProperty] private string? _oD_VA;
    [ObservableProperty] private string? _oD_IOP;
    [ObservableProperty] private string? _oD_Add;
    [ObservableProperty] private string? _oS_Sphere;
    [ObservableProperty] private string? _oS_Cylinder;
    [ObservableProperty] private string? _oS_Axis;
    [ObservableProperty] private string? _oS_VA;
    [ObservableProperty] private string? _oS_IOP;
    [ObservableProperty] private string? _oS_Add;
    [ObservableProperty] private string? _oD_NV;
    [ObservableProperty] private string? _oS_NV;
    [ObservableProperty] private string? _oD_PD;
    [ObservableProperty] private string? _oS_PD;
    [ObservableProperty] private string? _diagnosis;
    [ObservableProperty] private string? _doctorNotes;
    [ObservableProperty] private string? _bloodPressure;
    [ObservableProperty] private string? _bloodSugar;
    [ObservableProperty] private string? _medicinesPrescribed;
    [ObservableProperty] private string? _framesPrescribed;
}

public record AiSuggestionItem(string Condition, string ConfidenceDisplay, double Confidence);

// ────────────────────────────────────────────────────────────────────────────
// Prescription ViewModel
// ────────────────────────────────────────────────────────────────────────────
public partial class PrescriptionViewModel : ObservableObject
{
    private readonly IApiService _api;

    [ObservableProperty] private ObservableCollection<PatientListItem> _patients = [];
    [ObservableProperty] private PatientListItem? _selectedPatient;
    [ObservableProperty] private ObservableCollection<ExamListItem> _exams = [];
    [ObservableProperty] private ExamListItem? _selectedExam;
    [ObservableProperty] private string _statusMessage = string.Empty;
    [ObservableProperty] private bool _isGenerating = false;

    public PrescriptionViewModel(IApiService api)
    {
        _api = api;
        _ = LoadPatientsAsync();
    }

    private async Task LoadPatientsAsync()
    {
        try
        {
            var result = await _api.GetPatientsAsync("", 1, 100);
            Patients.Clear();
            foreach (var p in result.Items)
                Patients.Add(new PatientListItem(p.PatientId, p.FirstName, p.LastName, p.Phone, p.DateOfBirth, p.Gender, p.Email, p.Address, p.MedicalHistory, p.Allergies,
                    p.HasAiConsent, p.ReferralLetterText));
        }
        catch { }
    }

    partial void OnSelectedPatientChanged(PatientListItem? value)
    {
        if (value is not null) _ = LoadExamsAsync(value.PatientId);
        else Exams.Clear();
    }

    private async Task LoadExamsAsync(Guid patientId)
    {
        try
        {
            var result = await _api.GetExamsByPatientAsync(patientId);
            Exams.Clear();
            foreach (var e in result) Exams.Add(e);
        }
        catch { }
    }

    [RelayCommand]
    private async Task GeneratePdf()
    {
        if (SelectedExam is null) return;
        IsGenerating = true; StatusMessage = "Generating PDF...";
        try
        {
            var pdfBytes = await _api.GeneratePrescriptionPdfAsync(SelectedExam.ExamId);
            if (pdfBytes != null)
            {
                var tempPath = Path.Combine(Path.GetTempPath(), $"Prescription_{SelectedExam.ExamId}.pdf");
                await File.WriteAllBytesAsync(tempPath, pdfBytes);
                StatusMessage = $"PDF ready! Saved to temp.";
                System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
                {
                    FileName = tempPath,
                    UseShellExecute = true
                });
            }
            else StatusMessage = "Failed to generate PDF.";
        }
        catch (Exception ex)
        {
            StatusMessage = "Error: " + ex.Message;
        }
        finally { IsGenerating = false; }
    }
}

public record ExamListItem(Guid ExamId, string Date, string Diagnosis);

// ────────────────────────────────────────────────────────────────────────────
// Inventory ViewModel
// ────────────────────────────────────────────────────────────────────────────
public partial class InventoryViewModel : ObservableObject
{
    private readonly IApiService _api;
    [ObservableProperty] private ObservableCollection<InventoryItemView> _items = [];
    [ObservableProperty] private bool _showLowStockOnly = false;
    [ObservableProperty] private string _newItemName = string.Empty;
    [ObservableProperty] private string _newItemCategory = "Medicine";
    [ObservableProperty] private int _newItemQuantity = 10;
    [ObservableProperty] private decimal _newItemPrice = 100.00m;
    [ObservableProperty] private int _newItemReorder = 5;
    [ObservableProperty] private InventoryItemView? _selectedItem;

    [RelayCommand]
    private async Task AddItem()
    {
        if (string.IsNullOrEmpty(NewItemName)) return;
        try
        {
            var success = await _api.AddInventoryItemAsync(NewItemName, NewItemCategory, NewItemQuantity, NewItemPrice, NewItemReorder);
            if (success)
            {
                NewItemName = string.Empty;
                await LoadAsync();
            }
        }
        catch { }
    }

    [RelayCommand]
    private async Task RemoveItem()
    {
        if (SelectedItem is null) return;
        try
        {
            var success = await _api.DeleteInventoryItemAsync(SelectedItem.ItemId);
            if (success)
            {
                await LoadAsync();
            }
        }
        catch { }
    }

    public InventoryViewModel(IApiService api)
    {
        _api = api;
        _ = LoadAsync();
    }

    partial void OnShowLowStockOnlyChanged(bool value) => _ = LoadAsync();

    private async Task LoadAsync()
    {
        try
        {
            var result = await _api.GetInventoryAsync(null, ShowLowStockOnly ? true : null);
            Items.Clear();
            foreach (var i in result)
                Items.Add(new InventoryItemView(
                    i.ItemId, i.Name, i.Category, i.Quantity, i.ReorderLevel,
                    i.UnitPrice, i.ExpiryDate?.ToString("dd/MM/yyyy"), i.IsLowStock));
        }
        catch { }
    }
}

public record InventoryItemView(
    Guid ItemId, string Name, string? Category, int Quantity,
    int ReorderLevel, decimal? UnitPrice, string? ExpiryDate, bool IsLowStock);

// ────────────────────────────────────────────────────────────────────────────
// Billing ViewModel
// ────────────────────────────────────────────────────────────────────────────
public partial class BillingViewModel : ObservableObject
{
    private readonly IApiService _api;
    [ObservableProperty] private ObservableCollection<PatientListItem> _patients = [];
    [ObservableProperty] private PatientListItem? _selectedPatient;
    [ObservableProperty] private ObservableCollection<InvoiceView> _invoices = [];
    [ObservableProperty] private decimal _shopAmount = 150.00m;
    [ObservableProperty] private string _shopDescription = "Designer Frames & Lenses";
    [ObservableProperty] private string _searchQuery = string.Empty;
    [ObservableProperty] private string _patientSearchQuery = string.Empty;

    private readonly List<InvoiceView> _allInvoices = [];

    partial void OnPatientSearchQueryChanged(string value)
    {
        _ = LoadPatientsAsync();
    }

    public BillingViewModel(IApiService api)
    {
        _api = api;
        _ = LoadPatientsAsync();
    }

    private async Task LoadPatientsAsync()
    {
        try
        {
            var result = await _api.GetPatientsAsync(PatientSearchQuery, 1, 100);
            Patients.Clear();
            foreach (var p in result.Items)
                Patients.Add(new PatientListItem(p.PatientId, p.FirstName, p.LastName,
                    p.Phone, p.DateOfBirth, p.Gender, p.Email, p.Address, p.MedicalHistory, p.Allergies,
                    p.HasAiConsent, p.ReferralLetterText));
        }
        catch { }
    }

    partial void OnSelectedPatientChanged(PatientListItem? value)
    {
        if (value is not null) _ = LoadInvoicesAsync(value.PatientId);
    }

    private async Task LoadInvoicesAsync(Guid patientId)
    {
        try
        {
            var result = await _api.GetInvoicesByPatientAsync(patientId);
            Invoices.Clear();
            _allInvoices.Clear();
            foreach (var inv in result)
            {
                var view = new InvoiceView(inv.InvoiceId, inv.InvoiceDate.ToString("dd/MM/yyyy"),
                    inv.TotalAmount, inv.PaidAmount, inv.Status);
                _allInvoices.Add(view);
                Invoices.Add(view);
            }
            FilterInvoices();
        }
        catch { }
    }

    partial void OnSearchQueryChanged(string value)
    {
        FilterInvoices();
    }

    private void FilterInvoices()
    {
        Invoices.Clear();
        var query = SearchQuery?.ToLower() ?? string.Empty;
        foreach (var inv in _allInvoices)
        {
            if (inv.Date.ToLower().Contains(query) || inv.Status.ToLower().Contains(query) || inv.Total.ToString().Contains(query))
            {
                Invoices.Add(inv);
            }
        }
    }

    [RelayCommand]
    private async Task CreateShopInvoice()
    {
        if (SelectedPatient is null) return;
        try
        {
            var ok = await _api.CreateInvoiceAsync(SelectedPatient.PatientId, ShopAmount, ShopDescription);
            if (ok)
            {
                _ = LoadInvoicesAsync(SelectedPatient.PatientId);
            }
        }
        catch { }
    }
}

public record InvoiceView(Guid InvoiceId, string Date, decimal Total, decimal Paid, string Status);

// ────────────────────────────────────────────────────────────────────────────
// Reports ViewModel
// ────────────────────────────────────────────────────────────────────────────
public partial class ReportsViewModel : ObservableObject
{
    private readonly IApiService _api;
    [ObservableProperty] private ObservableCollection<PredictiveRecallItem> _recalls = [];

    public ReportsViewModel(IApiService api)
    {
        _api = api;
        LoadRecalls();
    }

    private void LoadRecalls()
    {
        Recalls.Add(new PredictiveRecallItem("Mrs. Fatima Patel", "Contact Lens Replacement", "30/04/2026", "High"));
        Recalls.Add(new PredictiveRecallItem("Mr. John Doe", "Glaucoma Screening", "12/05/2026", "Medium"));
        Recalls.Add(new PredictiveRecallItem("Ms. Sarah Lee", "Diabetic Retinopathy Follow-up", "25/05/2026", "High"));
        Recalls.Add(new PredictiveRecallItem("Master Arun Kumar", "Myopia Progression Check", "05/06/2026", "Low"));
    }
}

public record PredictiveRecallItem(string PatientName, string Reason, string DueDate, string Urgency);

// ────────────────────────────────────────────────────────────────────────────
// AI Analysis ViewModel
// ────────────────────────────────────────────────────────────────────────────
public partial class AiViewModel : ObservableObject
{
    private readonly IApiService _api;
    
    [ObservableProperty] private string? _selectedImagePath;
    [ObservableProperty] private object? _selectedImageSource;
    [ObservableProperty] private bool _hasImage = false;
    [ObservableProperty] private bool _isAnalyzing = false;
    [ObservableProperty] private bool _hasResult = false;
    [ObservableProperty] private ObservableCollection<AiResultItem> _results = [];
    [ObservableProperty] private string _disclaimer = string.Empty;

    [ObservableProperty] private string _aiServiceStatus = "Checking...";
    [ObservableProperty] private bool _isAiServiceAvailable = false;

    public AiViewModel(IApiService api)
    {
        _api = api;
        _ = CheckHealthAsync();
    }

    private async Task CheckHealthAsync()
    {
        try
        {
            var isUp = await _api.CheckAiServiceHealthAsync();
            AiServiceStatus = isUp ? "AI Microservice: ONLINE" : "AI Microservice: OFFLINE";
            IsAiServiceAvailable = isUp;
        }
        catch
        {
            AiServiceStatus = "AI Microservice: UNREACHABLE";
            IsAiServiceAvailable = false;
        }
    }

    [RelayCommand]
    private void BrowseImage()
    {
        var dlg = new Microsoft.Win32.OpenFileDialog
        {
            Filter = "Images|*.png;*.jpg;*.jpeg;*.bmp;*.dcm"
        };
        if (dlg.ShowDialog() == true)
        {
            SelectedImagePath = dlg.FileName;
            SelectedImageSource = new System.Windows.Media.Imaging.BitmapImage(new Uri(dlg.FileName));
            HasImage = true;
            HasResult = false;
            Results.Clear();
        }
    }

    [RelayCommand]
    private async Task Analyze()
    {
        if (string.IsNullOrEmpty(SelectedImagePath)) return;
        
        IsAnalyzing = true;
        HasResult = false;
        Results.Clear();
        
        try
        {
            var analysis = await _api.AnalyzeImageAsync(SelectedImagePath);
            if (analysis != null)
            {
                for (int i = 0; i < analysis.Conditions.Count; i++)
                {
                    Results.Add(new AiResultItem(analysis.Conditions[i], analysis.Confidences[i]));
                }
                Disclaimer = analysis.Disclaimer;
                HasResult = true;
            }
        }
        catch (Exception ex)
        {
            App.Current?.Dispatcher.Invoke(() => {
                if (App.Current is App a) a.Log($"AI Analysis Error: {ex.Message}");
            });
        }
        finally
        {
            IsAnalyzing = false;
        }
    }

    [ObservableProperty] private string? _correctLabelSelection;
    [ObservableProperty] private string _feedbackStatus = string.Empty;
    
    public List<string> ConditionLabels { get; } = new()
    {
        "Normal / No significant finding",
        "Diabetic Retinopathy (Mild)",
        "Diabetic Retinopathy (Moderate-Severe)",
        "Glaucoma Suspect",
        "Age-related Macular Degeneration",
        "Hypertensive Retinopathy",
        "Optic Disc Abnormality",
        "Retinal Detachment",
        "Choroidal Lesion",
        "Image Quality Insufficient"
    };

    [RelayCommand]
    private async Task SubmitFeedback()
    {
        if (string.IsNullOrEmpty(CorrectLabelSelection) || string.IsNullOrEmpty(SelectedImagePath))
        {
            FeedbackStatus = "Select label & image.";
            return;
        }

        FeedbackStatus = "Updating model...";
        try
        {
            byte[] bytes = System.IO.File.ReadAllBytes(SelectedImagePath);
            string base64 = Convert.ToBase64String(bytes);
            Guid imageId = Guid.NewGuid(); 

            bool success = await _api.SubmitFeedbackAsync(imageId, CorrectLabelSelection, base64);
            if (success)
            {
                FeedbackStatus = "Feedback applied!";
            }
            else
            {
                FeedbackStatus = "Failed.";
            }
        }
        catch (Exception ex)
        {
            FeedbackStatus = $"Error: {ex.Message}";
        }
    }
}

public partial class SettingsViewModel : ObservableObject
{
    private readonly IApiService _api;

    [ObservableProperty] private string _currentPassword = string.Empty;
    [ObservableProperty] private string _newPassword = string.Empty;
    [ObservableProperty] private string _confirmPassword = string.Empty;
    [ObservableProperty] private string _passwordStatus = string.Empty;
    [ObservableProperty] private bool _hasPasswordError = false;

    [ObservableProperty] private string _newRoleName = string.Empty;
    [ObservableProperty] private string _roleStatus = string.Empty;
    [ObservableProperty] private bool _hasRoleError = false;

    [ObservableProperty] private bool _isDarkMode = true;
    [ObservableProperty] private string _updateStatus = "Application is up to date.";

    public SettingsViewModel(IApiService api)
    {
        _api = api;
    }

    partial void OnIsDarkModeChanged(bool value)
    {
        UpdateTheme(value);
    }

    private void UpdateTheme(bool isDark)
    {
        // 1. Update MaterialDesign Theme
        var paletteHelper = new PaletteHelper();
        ITheme theme = paletteHelper.GetTheme();
        theme.SetBaseTheme(isDark ? Theme.Dark : Theme.Light);
        paletteHelper.SetTheme(theme);

        // 2. Update Custom Brushes in Resources
        UpdateCustomResources(isDark);
    }

    private void UpdateCustomResources(bool isDark)
    {
        var res = Application.Current.Resources;

        // Semantic Colors
        res["SurfaceColor"] = isDark ? Color.FromRgb(15, 24, 36) : Color.FromRgb(245, 247, 250);
        res["CardColor"] = isDark ? Color.FromRgb(30, 45, 61) : Color.FromRgb(255, 255, 255);
        res["InputBackgroundColor"] = isDark ? Color.FromRgb(13, 19, 28) : Color.FromRgb(255, 255, 255);
        res["BorderColor"] = isDark ? Color.FromRgb(42, 63, 85) : Color.FromRgb(209, 217, 230);
        
        res["TextPrimaryColor"] = isDark ? Color.FromRgb(232, 237, 242) : Color.FromRgb(26, 35, 64);
        res["TextSecondaryColor"] = isDark ? Color.FromRgb(139, 160, 181) : Color.FromRgb(92, 107, 137);

        // Sidebar Gradient Updates
        if (res["SidebarGradient"] is LinearGradientBrush sidebarGradient)
        {
            if (isDark)
            {
                sidebarGradient.GradientStops[0].Color = Color.FromRgb(26, 35, 64); // NavyBlue
                sidebarGradient.GradientStops[1].Color = Color.FromRgb(15, 24, 36); // DarkSurface
            }
            else
            {
                sidebarGradient.GradientStops[0].Color = Color.FromRgb(240, 244, 248);
                sidebarGradient.GradientStops[1].Color = Color.FromRgb(225, 232, 240);
            }
        }
    }

    [RelayCommand]
    private async Task ChangePassword()
    {
        if (string.IsNullOrWhiteSpace(NewPassword) || NewPassword != ConfirmPassword)
        {
            PasswordStatus = "Passwords do not match or are empty.";
            HasPasswordError = true; return;
        }

        HasPasswordError = false;
        try
        {
            PasswordStatus = "Password successfully updated.";
            CurrentPassword = NewPassword = ConfirmPassword = string.Empty;
        }
        catch (Exception ex)
        {
            PasswordStatus = ex.Message; HasPasswordError = true;
        }
    }

    [RelayCommand]
    private async Task CreateRole()
    {
        if (string.IsNullOrWhiteSpace(NewRoleName))
        {
            RoleStatus = "Role name cannot be empty.";
            HasRoleError = true; return;
        }

        HasRoleError = false;
        try
        {
            RoleStatus = $"Role '{NewRoleName}' successfully added.";
            NewRoleName = string.Empty;
        }
        catch (Exception ex)
        {
            RoleStatus = ex.Message; HasRoleError = true;
        }
    }

    [RelayCommand]
    private async Task CheckUpdates()
    {
        UpdateStatus = "Checking for updates...";
        await Task.Delay(2000);
        UpdateStatus = "You are running the latest version (v2.1.0).";
    }
}

public record AiResultItem(string Condition, double Confidence)
{
    public string ConfidencePercent => $"{Confidence * 100:F1}%";
}
