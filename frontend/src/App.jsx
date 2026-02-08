import { useState } from 'react'
import './App.css'
import { generateContent } from './services/api'

// Minimal icons
const Spark = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 2L9.5 9.5 2 12l7.5 2.5L12 22l2.5-7.5L22 12l-7.5-2.5L12 2z" />
  </svg>
)

const Check = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
    <path d="M20 6 9 17l-5-5" />
  </svg>
)

const Dot = () => <span className="dot">●</span>

function App() {
  const [grade, setGrade] = useState(5)
  const [topic, setTopic] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [step, setStep] = useState(0)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!topic.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)
    setStep(1)

    const t = setTimeout(() => setStep(2), 2000)

    try {
      const data = await generateContent(grade, topic)
      setResult(data)
      setStep(3)
    } catch (err) {
      setError(err.message)
      setStep(0)
    } finally {
      setLoading(false)
      clearTimeout(t)
    }
  }

  return (
    <div className="shell">
      {/* Floating accent blobs */}
      <div className="blob blob-1" />
      <div className="blob blob-2" />

      {/* Header */}
      <header className="topbar">
        <div className="brand">
          <span className="brand-icon"><Spark /></span>
          <span className="brand-text">AI Assessment Generator</span>
        </div>
        <div className="status-pill">
          <span className={`status-dot ${loading ? 'pulse' : ''}`} />
          <code>{loading ? 'processing...' : 'ready'}</code>
        </div>
      </header>

      <div className="canvas">
        {/* LEFT: Offset input section */}
        <aside className="sidebar">
          <div className="input-box">
            <p className="eyebrow">new assessment</p>
            <h1 className="input-title">
              What should we<br />
              <span className="highlight">teach today?</span>
            </h1>

            <form onSubmit={handleSubmit} className="form">
              <div className="field">
                <label>grade</label>
                <select value={grade} onChange={(e) => setGrade(Number(e.target.value))}>
                  {Array.from({ length: 12 }, (_, i) => (
                    <option key={i + 1} value={i + 1}>Grade {i + 1} • Ages {i + 6}–{i + 7}</option>
                  ))}
                </select>
              </div>

              <div className="field">
                <label>topic</label>
                <input
                  type="text"
                  placeholder="Photosynthesis, Fractions..."
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                />
              </div>

              <button type="submit" className="btn-go" disabled={loading || !topic.trim()}>
                {loading ? (
                  <><span className="spin" /> generating...</>
                ) : (
                  <><Spark /> generate</>
                )}
              </button>
            </form>
          </div>

          {/* Pipeline with animated progress */}
          <div className="pipeline">
            <p className="pipeline-label">Pipeline Status</p>
            <div className="pipeline-track">
              <div className={`pipeline-progress step-${step}`} />
            </div>
            <div className="steps">
              <div className={`step ${step >= 1 ? 'active' : ''} ${step > 1 ? 'done' : ''}`}>
                <div className="step-indicator">
                  <div className="step-ring">
                    {step > 1 ? <Check /> : <span className="step-num">1</span>}
                  </div>
                  {step === 1 && <div className="step-pulse" />}
                </div>
                <div className="step-content">
                  <span className="step-name">Generator</span>
                  <span className="step-desc">{step === 1 ? 'Creating content...' : step > 1 ? 'Complete' : 'Waiting'}</span>
                </div>
              </div>
              <div className={`step ${step >= 2 ? 'active' : ''} ${step > 2 ? 'done' : ''}`}>
                <div className="step-indicator">
                  <div className="step-ring">
                    {step > 2 ? <Check /> : <span className="step-num">2</span>}
                  </div>
                  {step === 2 && <div className="step-pulse" />}
                </div>
                <div className="step-content">
                  <span className="step-name">Reviewer</span>
                  <span className="step-desc">{step === 2 ? 'Validating quality...' : step > 2 ? 'Complete' : 'Waiting'}</span>
                </div>
              </div>
              <div className={`step ${step >= 3 ? 'active done' : ''}`}>
                <div className="step-indicator">
                  <div className="step-ring">
                    {step >= 3 ? <Check /> : <span className="step-num">3</span>}
                  </div>
                </div>
                <div className="step-content">
                  <span className="step-name">Output</span>
                  <span className="step-desc">{step >= 3 ? 'Ready' : 'Waiting'}</span>
                </div>
              </div>
            </div>
          </div>
        </aside>

        {/* RIGHT: Results area - staggered cards */}
        <main className="main">
          {/* Loading state */}
          {loading && (
            <div className="loader-card">
              <div className="loader-ring" />
              <p>{step === 1 ? 'Generating content...' : 'Reviewing quality...'}</p>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="error-box">
              <strong>Oops!</strong>
              <p>{error}</p>
            </div>
          )}

          {/* Empty state - quirky */}
          {!loading && !result && !error && (
            <div className="empty">
              <div className="empty-icon">📚</div>
              <h2>Nothing here yet</h2>
              <p>Pick a grade and topic,<br />then hit generate.</p>
            </div>
          )}

          {/* Results - staggered layout */}
          {result && (
            <div className="results">
              {/* Explanation - wider, offset top */}
              <article className="card card-explanation">
                <header className="card-head">
                  <span className="card-tag">explanation</span>
                  {result.was_refined && <span className="badge-refined">✨ refined</span>}
                </header>
                <div className="card-body prose">
                  {result.was_refined && result.refined_output
                    ? result.refined_output.explanation
                    : result.generator_output.explanation}
                </div>
              </article>

              {/* MCQs - offset to the right */}
              <article className="card card-mcqs">
                <header className="card-head">
                  <span className="card-tag">questions</span>
                  <span className="card-count">{(result.was_refined && result.refined_output
                    ? result.refined_output.mcqs
                    : result.generator_output.mcqs).length} items</span>
                </header>
                <div className="mcq-list">
                  {(result.was_refined && result.refined_output
                    ? result.refined_output.mcqs
                    : result.generator_output.mcqs
                  ).map((mcq, i) => (
                    <div key={i} className="mcq">
                      <div className="mcq-q">
                        <span className="mcq-num">{String(i + 1).padStart(2, '0')}</span>
                        <span>{mcq.question}</span>
                      </div>
                      <div className="mcq-opts">
                        {mcq.options.map((opt, j) => (
                          <div key={j} className={`opt ${opt === mcq.answer ? 'correct' : ''}`}>
                            <span className="opt-letter">{String.fromCharCode(65 + j)}</span>
                            <span>{opt}</span>
                            {opt === mcq.answer && <Check />}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </article>

              {/* Review - full width */}
              <article className="card card-review-full">
                <header className="card-head">
                  <span className="card-tag">Quality Review</span>
                  <span className={`badge-status ${result.reviewer_output.status}`}>
                    {result.reviewer_output.status === 'pass' ? '✓ Passed' : '✗ Needs Revision'}
                  </span>
                </header>
                {result.reviewer_output.feedback?.length > 0 ? (
                  <ul className="feedback">
                    {result.reviewer_output.feedback.map((f, i) => (
                      <li key={i}>{f}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="all-good"><Check /> All checks passed</p>
                )}
              </article>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default App
