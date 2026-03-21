import React from 'react';

export default function SectionExcerpt({ content }: { content: string }) {
  return (
    <div className="ml-3 pl-2 border-l border-gray-800 text-[10px] text-gray-500 line-clamp-2 italic">
      {content}
    </div>
  );
}
