const fs = require('node:fs')
const path = require('node:path')
const { spawnSync } = require('node:child_process')

function testName(test) {
  const names = []
  for (let item = test; item.parent; item = item.parent) names.unshift(item.name)
  return names.join(' ')
}

if (require.main !== module) {
  const environment = require(process.env.ASK_JEST_ENVIRONMENT)
  const BaseEnvironment = environment.TestEnvironment || environment.default || environment
  module.exports = class extends BaseEnvironment {
    constructor(config, context) {
      super(config, context)
      this.file = path.relative(process.cwd(), context.testPath)
      this.cases = []
      this.assertions = new WeakMap()
      this.collectionFailed = false
    }

    async handleTestEvent(event, state) {
      await super.handleTestEvent?.(event, state)
      const { name, test, error } = event
      if (name === 'test_fn_failure' && !test.failing &&
          (typeof error?.matcherResult?.pass === 'boolean' || error?.code === 'ERR_ASSERTION')) {
        this.assertions.set(test, error)
      }
      if (name === 'hook_failure' || name === 'error') this.collectionFailed = true
      if (name === 'test_done' || name === 'test_skip' || name === 'test_todo') {
        const errors = test.errors
        const assertion = errors.length === 1 && errors[0][0] === this.assertions.get(test)
        let outcome = 'skipped'
        if (name === 'test_done') {
          if (test.failing || (errors.length && !assertion)) outcome = 'error'
          else if (assertion) outcome = 'failed'
          else outcome = 'passed'
        }
        this.cases.push({
          case_id: this.file + '::' + testName(test),
          outcome,
          failure_kind: assertion ? 'behavior_assertion' :
            outcome === 'error' ? 'setup_or_runtime_error' : null,
        })
      }
      if (name === 'run_finish') {
        const evidence = JSON.stringify({
          file: this.file, cases: this.cases, collectionFailed: this.collectionFailed,
        })
        fs.appendFileSync(process.env.ASK_JEST_EVENTS, evidence + '\n', { mode: 0o600 })
      }
    }
  }
} else {
  try {
    main()
  } catch (error) {
    console.error(error.message)
    process.exitCode = 1
  }
}

function main() {
  const [output, selection, npm, script, ...files] = process.argv.slice(2)
  const selected = JSON.parse(selection)
  const cases = []
  let collectionFailed = false
  let passed = true
  const args = ['--silent', 'run', script, '--']
  const config = spawnSync(npm, ['--ignore-scripts', ...args, '--showConfig'], { encoding: 'utf8' })
  if (config.status !== 0) throw new Error(config.stderr || 'Could not read the Jest configuration')
  const { configs } = JSON.parse(config.stdout)
  if (configs.length !== 1 || !path.isAbsolute(configs[0].testEnvironment) ||
      !configs[0].testRunner.replaceAll(path.sep, '/').includes('/jest-circus/')) {
    throw new Error('Jest traceability requires one Jest project using jest-circus')
  }

  const eventsPath = output + '.jest-events'
  const env = { ...process.env, ASK_JEST_ENVIRONMENT: configs[0].testEnvironment, ASK_JEST_EVENTS: eventsPath }
  const flags = ['--runInBand', '--ci', '--watch=false', '--watchAll=false', '--coverage=false',
    '--no-cache', '--env', __filename, '--runTestsByPath']
  const batches = selected === null ? [files] : files.map(file => [file])
  for (const batch of batches) {
    const chosen = selected?.filter(id => id.startsWith(batch[0] + '::'))
    if (chosen?.length === 0) continue
    for (const file of batch) {
      const absolute = path.resolve(file)
      if (fs.realpathSync(absolute) !== absolute || !fs.statSync(absolute).isFile()) {
        throw new Error('Expected a regular candidate test file: ' + file)
      }
    }
    fs.writeFileSync(eventsPath, '', { flag: 'wx', mode: 0o600 })
    const options = chosen ? ['--testNamePattern', '^(?:' + chosen.map(id =>
      id.slice(batch[0].length + 2).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|') + ')(?![\\s\\S])'] : []
    const run = spawnSync(npm, [...args, ...flags, ...batch, ...options], { env, stdio: 'inherit' })
    const rows = fs.readFileSync(eventsPath, 'utf8').trim().split('\n').filter(Boolean).map(line => JSON.parse(line))
    fs.unlinkSync(eventsPath)
    const seenFiles = new Set(rows.map(row => row.file))
    const collected = rows.flatMap(row => row.cases).filter(test => !chosen || chosen.includes(test.case_id))
    const failed = collected.some(test => test.outcome === 'failed' || test.outcome === 'error')
    collectionFailed ||= rows.length !== batch.length || batch.some(file => !seenFiles.has(file)) ||
      rows.some(row => row.collectionFailed) || (run.status !== 0 && run.status !== 1) ||
      (run.status === 1 && !failed) || (run.status === 0 && failed)
    passed &&= run.status === 0
    cases.push(...collected)
  }

  const ids = new Set(cases.map(test => test.case_id))
  collectionFailed ||= cases.length === 0 || ids.size !== cases.length ||
    (selected !== null && selected.some(id => !ids.has(id)))
  fs.writeFileSync(output, JSON.stringify({
    cases, collection_status: collectionFailed ? 'error' : 'ok',
  }), { flag: 'wx', mode: 0o600 })
  process.exitCode = passed && !collectionFailed ? 0 : 1
}
