using MauEyeCare.Desktop.ViewModels;
using System.Windows;
using System.Windows.Input;

namespace MauEyeCare.Desktop.Views;

public partial class LoginWindow : Window
{
    private readonly LoginViewModel _vm;

    public LoginWindow()
    {
        InitializeComponent();
        _vm = App.Services.GetService(typeof(LoginViewModel)) as LoginViewModel
              ?? new LoginViewModel(null!, null!);
        DataContext = _vm;
        _vm.LoginSucceeded += OnLoginSucceeded;
    }

    private void OnLoginSucceeded(object? sender, EventArgs e)
    {
        var main = new MainWindow();
        main.Show();
        Close();
    }

    private void DragBar_MouseDown(object sender, MouseButtonEventArgs e)
    {
        if (e.ChangedButton == MouseButton.Left) DragMove();
    }

    private void CloseButton_Click(object sender, RoutedEventArgs e) => Close();

    private void PasswordBox_PasswordChanged(object sender, RoutedEventArgs e)
        => _vm.Password = PasswordBox.Password;

    private void RoleSelector_SelectionChanged(object sender, System.Windows.Controls.SelectionChangedEventArgs e)
    {
        if (sender is System.Windows.Controls.ComboBox cb && cb.SelectedItem is System.Windows.Controls.ComboBoxItem item)
        {
            var tag = item.Tag?.ToString() ?? "";
            if (!string.IsNullOrWhiteSpace(tag))
            {
                var parts = tag.Split('|');
                if (parts.Length == 2)
                {
                    _vm.Email = parts[0];
                    PasswordBox.Password = parts[1];
                }
            }
        }
    }
}
