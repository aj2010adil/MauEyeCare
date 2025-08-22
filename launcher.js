const { spawn, exec } = require('child_process');
const { join } = require('path');
const fs = require('fs');
const http = require('http');

class MauEyeCareLauncher {
  constructor() {
    this.backendProcess = null;
    this.frontendProcess = null;
    this.backendPort = 8000;
    this.frontendPort = 5173;
    this.isBackendReady = false;
    this.isFrontendReady = false;
  }

  async checkDependencies() {
    console.log('🔍 Checking system dependencies...');
    
    const checks = [
      { name: 'Node.js', command: 'node --version' },
      { name: 'npm', command: 'npm --version' },
      { name: 'PostgreSQL', command: 'psql --version' }
    ];

    for (const check of checks) {
      try {
        await this.execCommand(check.command);
        console.log(`✅ ${check.name} is installed`);
      } catch (error) {
        console.log(`❌ ${check.name} is not installed or not in PATH`);
        console.log(`   Please install ${check.name} and try again.`);
        process.exit(1);
      }
    }
  }

  async installDependencies() {
    console.log('📦 Installing dependencies...');
    
    try {
      // Install backend dependencies
      if (!fs.existsSync('node_modules')) {
        console.log('Installing backend dependencies...');
        await this.execCommand('npm install');
      }

      // Install frontend dependencies
      if (!fs.existsSync('node_modules')) {
        console.log('Installing frontend dependencies...');
        await this.execCommand('npm install');
      }

      console.log('✅ Dependencies installed successfully');
    } catch (error) {
      console.log('❌ Failed to install dependencies:', error.message);
      process.exit(1);
    }
  }

  async startBackend() {
    console.log('🚀 Starting backend server...');
    
    return new Promise((resolve, reject) => {
      this.backendProcess = spawn('.venv/Scripts/python', ['-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000'], {
        stdio: 'pipe',
        shell: true
      });

      this.backendProcess.stdout.on('data', (data) => {
        const output = data.toString();
        console.log(`[Backend] ${output.trim()}`);
        
        if (output.includes('Uvicorn running') || output.includes('Application startup complete')) {
          this.isBackendReady = true;
          console.log('✅ Backend server is ready');
          resolve();
        }
      });

      this.backendProcess.stderr.on('data', (data) => {
        console.log(`[Backend Error] ${data.toString().trim()}`);
      });

      this.backendProcess.on('error', (error) => {
        console.log('❌ Failed to start backend:', error.message);
        reject(error);
      });

      this.backendProcess.on('exit', (code) => {
        if (code !== 0) {
          console.log(`❌ Backend process exited with code ${code}`);
        }
      });

      // Timeout after 30 seconds
      setTimeout(() => {
        if (!this.isBackendReady) {
          reject(new Error('Backend startup timeout'));
        }
      }, 30000);
    });
  }

  async startFrontend() {
    console.log('🌐 Starting frontend development server...');
    
    return new Promise((resolve, reject) => {
      this.frontendProcess = spawn('npm', ['run', 'dev'], {
        stdio: 'pipe',
        shell: true
      });

      this.frontendProcess.stdout.on('data', (data) => {
        const output = data.toString();
        console.log(`[Frontend] ${output.trim()}`);
        
        if (output.includes('Local:') && output.includes('http://localhost:5173')) {
          this.isFrontendReady = true;
          console.log('✅ Frontend server is ready');
          resolve();
        }
      });

      this.frontendProcess.stderr.on('data', (data) => {
        console.log(`[Frontend Error] ${data.toString().trim()}`);
      });

      this.frontendProcess.on('error', (error) => {
        console.log('❌ Failed to start frontend:', error.message);
        reject(error);
      });

      this.frontendProcess.on('exit', (code) => {
        if (code !== 0) {
          console.log(`❌ Frontend process exited with code ${code}`);
        }
      });

      // Timeout after 30 seconds
      setTimeout(() => {
        if (!this.isFrontendReady) {
          reject(new Error('Frontend startup timeout'));
        }
      }, 30000);
    });
  }

  async waitForService(port, serviceName) {
    console.log(`⏳ Waiting for ${serviceName} to be ready...`);
    
    return new Promise((resolve, reject) => {
      const maxAttempts = 30;
      let attempts = 0;

      const checkService = () => {
        attempts++;
        
        const req = http.get(`http://localhost:${port}`, (res) => {
          if (res.statusCode === 200) {
            console.log(`✅ ${serviceName} is responding`);
            resolve();
          } else {
            if (attempts < maxAttempts) {
              setTimeout(checkService, 1000);
            } else {
              reject(new Error(`${serviceName} startup timeout`));
            }
          }
        });

        req.on('error', () => {
          if (attempts < maxAttempts) {
            setTimeout(checkService, 1000);
          } else {
            reject(new Error(`${serviceName} startup timeout`));
          }
        });

        req.setTimeout(1000, () => {
          req.destroy();
          if (attempts < maxAttempts) {
            setTimeout(checkService, 1000);
          } else {
            reject(new Error(`${serviceName} startup timeout`));
          }
        });
      };

      checkService();
    });
  }

  async openBrowser() {
    console.log('🌐 Opening MauEyeCare in browser...');
    
    const url = `http://localhost:${this.frontendPort}`;
    
    try {
      // Try to open browser based on OS
      const platform = process.platform;
      let command;

      if (platform === 'win32') {
        command = `start ${url}`;
      } else if (platform === 'darwin') {
        command = `open ${url}`;
      } else {
        command = `xdg-open ${url}`;
      }

      await this.execCommand(command);
      console.log('✅ Browser opened successfully');
    } catch (error) {
      console.log('⚠️ Could not open browser automatically');
      console.log(`   Please open: ${url}`);
    }
  }

  async execCommand(command) {
    return new Promise((resolve, reject) => {
      exec(command, (error, stdout, stderr) => {
        if (error) {
          reject(error);
        } else {
          resolve(stdout);
        }
      });
    });
  }

  setupGracefulShutdown() {
    const shutdown = () => {
      console.log('\n🛑 Shutting down MauEyeCare...');
      
      if (this.backendProcess) {
        this.backendProcess.kill();
        console.log('✅ Backend stopped');
      }
      
      if (this.frontendProcess) {
        this.frontendProcess.kill();
        console.log('✅ Frontend stopped');
      }
      
      console.log('👋 MauEyeCare has been shut down');
      process.exit(0);
    };

    process.on('SIGINT', shutdown);
    process.on('SIGTERM', shutdown);
    process.on('exit', shutdown);
  }

  async launch() {
    try {
      console.log('🏥 MauEyeCare Launcher Starting...\n');
      
      // Check dependencies
      await this.checkDependencies();
      
      // Install dependencies if needed
      await this.installDependencies();
      
      // Start services
      await Promise.all([
        this.startBackend(),
        this.startFrontend()
      ]);
      
      // Wait for services to be ready
      // Wait for backend first, then frontend
      await this.waitForService(this.backendPort, 'Backend');
      await this.waitForService(this.frontendPort, 'Frontend');
      
      // Open browser
      await this.openBrowser();
      
      // Setup graceful shutdown
      this.setupGracefulShutdown();
      
      console.log('\n🎉 MauEyeCare is ready!');
      console.log('📱 Frontend: http://localhost:5173');
      console.log('🔧 Backend: http://localhost:8000');
      console.log('\n💡 Press Ctrl+C to stop the application');
      
    } catch (error) {
      console.log('❌ Failed to launch MauEyeCare:', error.message);
      
      // Cleanup on error
      if (this.backendProcess) this.backendProcess.kill();
      if (this.frontendProcess) this.frontendProcess.kill();
      
      process.exit(1);
    }
  }
}

// Start the launcher
const launcher = new MauEyeCareLauncher();
launcher.launch();