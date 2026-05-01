using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using ModelContextProtocol.Server;
using ModelContextProtocol.Protocol;

var builder = Host.CreateApplicationBuilder(args);

// Configure logging to stderr to avoid interfering with stdio transport on stdout
builder.Logging.ClearProviders();
builder.Logging.AddConsole(options => {
    options.LogToStandardErrorThreshold = LogLevel.Trace;
});

// Build the MCP Server
builder.Services
    .AddMcpServer(options => {
        options.ServerInfo = new Implementation { Name = "MauEyeCare Clinical MCP", Version = "1.0.0" };
    })
    .WithStdioServerTransport() // Uses stdin/stdout for JSON-RPC
    .WithToolsFromAssembly();    // Registers [McpServerTool] methods from this project

var app = builder.Build();
await app.RunAsync();
