'use client'

interface WelcomeProps {
  onExampleClick: (message: string) => void
}

export function ChatGPTWelcome({ onExampleClick }: WelcomeProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full px-4">
      <div className="max-w-3xl w-full">
        <h1 className="text-[32px] leading-[1.2] font-normal text-center text-white/90" style={{ fontWeight: 400 }}>
          Hey there. Ready to analyze?
        </h1>
      </div>
    </div>
  )
}