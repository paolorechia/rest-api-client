const core = require('@actions/core');
const wait = require('./wait');
const { spawn } = require('child_process');
async function run() {
  try {
    const tox_env = core.getInput('tox_env');
    try {
	const tox = spawn('python3',  ['-m', 'tox', '-e', tox_env]);
	tox.stdout.on('data', (data) => {
	  console.log(`stdout: ${data}`);
	});

	tox.stderr.on('data', (data) => {
	  console.error(`stderr: ${data}`);
	});

	tox.on('close', (code) => {
	  console.log(`child process exited with code ${code}`);
          if (code === 0) {
             core.setOutput('success_flag', true)
          }
          if (code !== 0) {
             core.setOutput('success_flag', false)
             core.setFailed("Tox failed");
          }
	});
    } catch (error) {
        core.setfailed(error.message);
    }   
  } catch (error) {
    core.setFailed(error.message);
  }
}

run();
