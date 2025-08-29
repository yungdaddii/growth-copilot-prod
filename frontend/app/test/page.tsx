'use client'

export default function TestPage() {
  return (
    <div style={{ display: 'flex', height: '100vh', backgroundColor: '#212121' }}>
      {/* Sidebar */}
      <div style={{ 
        width: '260px', 
        backgroundColor: '#171717', 
        height: '100vh',
        borderRight: '1px solid rgba(255,255,255,0.1)'
      }}>
        <div style={{ padding: '12px' }}>
          <button style={{
            width: '100%',
            padding: '10px 12px',
            backgroundColor: 'transparent',
            color: 'white',
            border: '1px solid rgba(255,255,255,0.2)',
            borderRadius: '8px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            + New chat
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column',
        position: 'relative'
      }}>
        {/* Header */}
        <div style={{
          padding: '12px 16px',
          borderBottom: '1px solid rgba(255,255,255,0.1)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{ color: '#fff' }}>Growth Co-pilot</div>
          <button style={{
            padding: '6px 12px',
            backgroundColor: '#ab68ff',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer'
          }}>
            Try Pro
          </button>
        </div>

        {/* Center Content */}
        <div style={{ 
          flex: 1, 
          display: 'flex', 
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          padding: '20px'
        }}>
          <h1 style={{ 
            fontSize: '32px', 
            color: 'rgba(255,255,255,0.9)',
            fontWeight: 'normal',
            marginBottom: '40px',
            textAlign: 'center'
          }}>
            Hey there. Ready to analyze?
          </h1>
        </div>

        {/* Bottom Input */}
        <div style={{
          padding: '0 20px 20px',
          width: '100%',
          maxWidth: '768px',
          margin: '0 auto',
          boxSizing: 'border-box'
        }}>
          <div style={{
            backgroundColor: '#2f2f2f',
            borderRadius: '24px',
            padding: '12px 16px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <input 
              type="text"
              placeholder="Enter a domain to analyze (e.g., stripe.com)"
              style={{
                flex: 1,
                backgroundColor: 'transparent',
                border: 'none',
                outline: 'none',
                color: 'white',
                fontSize: '15px'
              }}
            />
            <button style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              backgroundColor: 'rgba(255,255,255,0.1)',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white'
            }}>
              ↑
            </button>
          </div>
          <p style={{
            textAlign: 'center',
            fontSize: '12px',
            color: 'rgba(255,255,255,0.5)',
            marginTop: '8px'
          }}>
            Growth Co-pilot can analyze websites and provide insights that may be inaccurate.
          </p>
        </div>
      </div>
    </div>
  )
}