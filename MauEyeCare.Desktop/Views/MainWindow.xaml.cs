using MauEyeCare.Desktop.ViewModels;
using System.Windows;
using System.Windows.Input;

namespace MauEyeCare.Desktop.Views;

public partial class MainWindow : Window
{
    private readonly MainViewModel _vm;

    public MainWindow()
    {
        InitializeComponent();
        _vm = App.Services.GetService(typeof(MainViewModel)) as MainViewModel
              ?? throw new InvalidOperationException("MainViewModel not registered");
        DataContext = _vm;
    }

    private void Window_Loaded(object sender, RoutedEventArgs e)
    {
        // Trigger initial navigation after UI is fully loaded
        _vm.NavigateCommand.Execute("Dashboard");
    }

    private void TitleBar_MouseDown(object sender, MouseButtonEventArgs e)
    {
        if (e.ChangedButton == MouseButton.Left) DragMove();
    }

    private void MinimizeButton_Click(object sender, RoutedEventArgs e)
        => WindowState = WindowState.Minimized;

    private void MaximizeRestoreButton_Click(object sender, RoutedEventArgs e)
    {
        if (WindowState == WindowState.Maximized)
        {
            WindowState = WindowState.Normal;
            MaximizeButton.Content = "▢";
        }
        else
        {
            WindowState = WindowState.Maximized;
            MaximizeButton.Content = "❐";
        }
    }

    private void CloseButton_Click(object sender, RoutedEventArgs e)
        => Close();
}
