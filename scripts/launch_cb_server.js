const { spawn } = require("child_process");

let cl = console.log;

let serverProcess = spawn("python", ["-m", "examples.loop"]);

setTimeout(() => {
  serverProcess.kill();
}, 3000);

serverProcess.stdout.on("data", data => {
  console.log(`stdout: ${data}`);
});

serverProcess.stderr.on("data", data => {
  console.error(`stderr: ${data}`);
});

serverProcess.on("close", code => {
  console.log(`Server exited with code ${code}`);
});
