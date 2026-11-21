const fs = require('node:fs')
const path = require('node:path')
const { run } = require('node:test')

async function main() {
  const [output, selection, ...files] = process.argv.slice(2)
  const selected = JSON.parse(selection)
  const cases = []
  let collectionFailed = false
  let passed = true
  // Stop Node's isolated test subprocesses before the coordinator times out.
  const signal = AbortSignal.timeout(290_000)

  for (const file of files) {
    const absolute = path.resolve(file)
    const names = selected?.filter(id => id.startsWith(file + '::'))
      .map(id => id.slice(file.length + 2))
    if (names?.length === 0) continue
    const testNamePatterns = names?.map(name => new RegExp(
      '^(?:' + name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')(?![\\s\\S])'
    ))
    const identity = fs.realpathSync(absolute)
    if (identity !== absolute || !fs.statSync(absolute).isFile()) {
      throw new Error('Expected a regular candidate test file: ' + file)
    }
    for await (const { type, data } of run({ files: [absolute], testNamePatterns, signal })) {
      if (type === 'test:stdout' || type === 'test:stderr') {
        process.stderr.write(data.message)
      }
      if (type === 'test:summary' && data.file === undefined) {
        passed &&= data.success
      }
      if (type !== 'test:pass' && type !== 'test:fail') continue
      console.dir({ type, data }, { depth: 4 })
      const error = data.details.error
      if (data.name === absolute || data.file !== absolute || data.nesting !== 0 || data.details.type !== 'test') {
        collectionFailed = true
        continue
      }
      if (type === 'test:fail' && error?.failureType !== 'testCodeFailure') {
        collectionFailed = true
      }
      if (names && !names.includes(data.name)) continue
      const assertion = error?.failureType === 'testCodeFailure' &&
        error.cause?.code === 'ERR_ASSERTION' && !data.skip && !data.todo
      let outcome = 'error'
      if (data.skip || data.todo) outcome = 'skipped'
      else if (assertion) outcome = 'failed'
      else if (type === 'test:pass') outcome = 'passed'
      cases.push({
        case_id: file + '::' + data.name,
        outcome,
        failure_kind: assertion ? 'behavior_assertion' : error ? 'setup_or_runtime_error' : null,
      })
    }
    signal.throwIfAborted()
  }

  collectionFailed ||= cases.length === 0 ||
    new Set(cases.map(test => test.case_id)).size !== cases.length ||
    (selected !== null && selected.some(id => !cases.some(test => test.case_id === id)))
  fs.writeFileSync(output, JSON.stringify({
    cases,
    collection_status: collectionFailed ? 'error' : 'ok',
  }), { flag: 'wx', mode: 0o600 })
  process.exitCode = passed && !collectionFailed ? 0 : 1
}

main().catch(error => {
  console.error(error)
  process.exitCode = 1
})
