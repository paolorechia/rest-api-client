const core = require('@actions/core');
const cache = require('@actions/cache');
const wait = require('./wait');
const { spawn } = require('child_process');

const pathes = [".tox"]
const key = "tox-test" 
let cacheKey = undefined

async function run_tox(code) {
    if (code === 0) {
        const tox_env = core.getInput('tox_env');
        try {
            cacheKey = await cache.restoreCache(pathes, key, [])
            if (!cacheKey) {
                core.info("Miss cache on tox")
            } else {
                core.info("Hit cache on tox")
            }
            const tox = spawn('python3',  ['-m', 'tox', '-e', tox_env]);
            tox.stdout.on('data', (data) => {
              console.log(`stdout: ${data}`);
            });

            tox.stderr.on('data', (data) => {
              console.error(`stderr: ${data}`);
            });
            tox.on('close', tox_end)
        } catch (error) {
            core.setFailed(error.message);
        }   
    } else {
        core.setFailed("Failed to install tox.");
    }
}

async function tox_end(code) {
      console.log(`child process exited with code ${code}`);
      if (code === 0) {
         core.setOutput('success_flag', true)
         if (!cacheKey) {
             core.info("Saving cache...")
             const cacheId = await cache.saveCache(pathes, key)
         }
      }
      if (code !== 0) {
         core.setOutput('success_flag', false)
         core.setFailed("Tox failed");
      }
}

async function run() {
  try {
    install = spawn('python3', ['-m', 'pip', 'install', 'tox'])
    install.stdout.on('data', (data) => {
      console.log(`stdout: ${data}`);
    });
    install.stderr.on('data', (data) => {
      console.error(`stderr: ${data}`);
    });
    install.on('close', run_tox)
  } catch (error) {
    core.setFailed(error.message);
  }
}

run();
