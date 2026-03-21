import React from 'react';

export function StopButton({ onStop }: { onStop?: () => void }) {
  return (
    <button onClick={onStop} className="w-full bg-red-900/30 text-red-500 text-xs font-semibold py-2 rounded-md border border-red-800/50 hover:bg-red-900/50 transition-colors uppercase tracking-widest flex items-center justify-center gap-2">
      <div className="w-2 h-2 bg-red-500 rounded-sm"></div>
      HALT PIPELINE
    </button>
  );
}

export function RestartButton({ onRestart }: { onRestart?: () => void }) {
  return (
    <button onClick={onRestart} className="w-full bg-blue-900/30 text-blue-400 text-xs font-semibold py-2 rounded-md border border-blue-800/50 hover:bg-blue-900/50 transition-colors uppercase tracking-widest mt-2 flex items-center justify-center gap-2">
       REBOOT ENGINE
    </button>
  );
}
